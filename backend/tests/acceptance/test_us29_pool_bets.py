"""US29: A Pool contains Bets and owns their shared deadline."""

import uuid
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from tests.acceptance.steps import (
    bearer,
    bet_payload,
    create_bet,
    create_pool,
    pick_payload,
    pool_payload,
    sign_in,
    token_for,
)


def test_creator_adds_multiple_bets_without_changing_the_pool(
    client,
    user_repo,
):
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )
    first = create_bet(
        client,
        pool["id"],
        headers,
        statement="Home team wins.",
    )
    second = create_bet(
        client,
        pool["id"],
        headers,
        statement="Total goals?",
        options=["0", "1–2", "3+"],
        presentation="dropdown",
    )

    # Public reads include the authored Bets, while Pool metadata stays on the Pool.
    detail = client.get(f"/api/pools/{pool['id']}")
    assert detail.status_code == 200
    saved = detail.get_json()
    assert saved == {**pool, "bets": [first, second]}
    assert client.get("/api/pools").get_json() == [saved]
    assert first["id"] != second["id"]
    for bet in saved["bets"]:
        assert bet["pool_id"] == pool["id"]
        assert bet["winning_outcome_id"] is None
        assert {"deadline", "creator", "decider", "picks"}.isdisjoint(bet)


@pytest.mark.parametrize("description", ["", "   "])
def test_description_is_optional_and_blank_text_is_normalized(
    client,
    user_repo,
    description,
):
    _, headers = sign_in(user_repo)
    payload = pool_payload(description=description)
    if description == "":
        payload.pop("description")

    response = client.post(
        "/api/pools",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["description"] == ""
    assert response.get_json()["bets"] == []


@pytest.mark.parametrize("field", ["statement", "options", "presentation", "bets"])
def test_pool_creation_refuses_embedded_bet_fields(
    client,
    user_repo,
    pool_repo,
    field,
):
    _, headers = sign_in(user_repo)

    response = client.post(
        "/api/pools",
        json=pool_payload(**{field: None}),
        headers=headers,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Pools are created empty. Add bets separately."}
    assert pool_repo.pools == []


def test_decider_cannot_be_chosen_in_the_request(
    client,
    user_repo,
    pool_repo,
):
    _, headers = sign_in(user_repo)

    response = client.post(
        "/api/pools",
        json=pool_payload(decider_id=str(uuid.uuid4())),
        headers=headers,
    )

    assert response.status_code == 400
    assert pool_repo.pools == []


@pytest.mark.parametrize(
    "actor, status",
    [("anonymous", 401), ("other-user", 403), ("account-without-user", 403)],
)
def test_only_the_authenticated_creator_can_add_bets(
    client,
    user_repo,
    pool_repo,
    actor,
    status,
):
    _, owner_headers = sign_in(user_repo)
    pool = create_pool(
        client,
        owner_headers,
    )
    if actor == "other-user":
        _, headers = sign_in(user_repo, name="Bruno")
    elif actor == "account-without-user":
        headers = bearer(token_for(str(uuid.uuid4())))
    else:
        headers = {}

    response = client.post(
        f"/api/pools/{pool['id']}/bets",
        json=bet_payload(),
        headers=headers,
    )

    assert response.status_code == status
    assert pool_repo.get_pool(pool["id"]).bets == ()


@pytest.mark.parametrize("pool_id", ["not-a-uuid", str(uuid.uuid4())])
def test_cannot_add_a_bet_to_an_unknown_pool(
    client,
    user_repo,
    pool_repo,
    pool_id,
):
    _, headers = sign_in(user_repo)

    response = client.post(
        f"/api/pools/{pool_id}/bets",
        json=bet_payload(),
        headers=headers,
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Pool not found."}
    assert pool_repo.pools == []


@pytest.mark.parametrize(
    "field",
    ["pool_id", "deadline", "creator_id", "decider_id", "winning_outcome_id"],
)
def test_bets_cannot_override_pool_metadata_or_set_a_winner(
    client,
    user_repo,
    pool_repo,
    field,
):
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )

    response = client.post(
        f"/api/pools/{pool['id']}/bets",
        json=bet_payload(**{field: None}),
        headers=headers,
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": f"Field '{field}' is not accepted when adding a bet."
    }
    assert pool_repo.get_pool(pool["id"]).bets == ()


@pytest.mark.parametrize("statement", [None, "", "   ", "x" * 501])
def test_invalid_statement_does_not_create_a_bet(
    client,
    user_repo,
    pool_repo,
    statement,
):
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )

    response = client.post(
        f"/api/pools/{pool['id']}/bets",
        json=bet_payload(statement=statement),
        headers=headers,
    )

    assert response.status_code == 400
    assert pool_repo.get_pool(pool["id"]).bets == ()


@pytest.mark.parametrize(
    "seconds_after_deadline",
    [0, 1],
    ids=["at-deadline", "after-deadline"],
)
def test_the_shared_deadline_closes_authoring_and_picks_for_all_bets(
    client,
    user_repo,
    pool_repo,
    pick_repo,
    seconds_after_deadline,
):
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )
    bets = [
        create_bet(
            client,
            pool["id"],
            headers,
        )
        for _ in range(2)
    ]
    first = bets[0]
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{first['id']}/picks",
        json=pick_payload(first["options"][0]["id"]),
        headers=headers,
    )
    assert response.status_code == 201
    saved = response.get_json()
    deadline = datetime(2030, 1, 1, tzinfo=timezone.utc)
    pool_repo.pools[0] = replace(pool_repo.pools[0], deadline=deadline)

    # Cover the boundary and a passed deadline with a fixed clock.
    with patch("pools.models.datetime") as clock:
        clock.now.return_value = deadline + timedelta(seconds=seconds_after_deadline)
        added = client.post(
            f"/api/pools/{pool['id']}/bets",
            json=bet_payload(),
            headers=headers,
        )
        assert added.status_code == 400
        assert added.get_json() == {"error": "Bets cannot be added after the pool's deadline."}
        for bet in bets:
            picked = client.post(
                f"/api/pools/{pool['id']}/bets/{bet['id']}/picks",
                json=pick_payload(bet["options"][1]["id"]),
                headers=headers,
            )
            assert picked.status_code == 400
            assert picked.get_json() == {"error": "Picks are closed for this pool."}
        assert client.get(f"/api/pools/{pool['id']}").get_json()["status"] == "LOCKED"

    assert len(pool_repo.get_pool(pool["id"]).bets) == 2
    assert len(pick_repo.picks) == 1
    assert client.get(
        f"/api/pools/{pool['id']}/picks",
        headers=headers,
    ).get_json() == {"picks": [saved]}


@pytest.mark.parametrize(
    "target",
    ["unknown-bet", "bet-from-other-pool", "option-from-sibling-bet"],
)
def test_pick_rejects_references_outside_the_selected_bet(
    client,
    user_repo,
    pick_repo,
    target,
):
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )
    other_pool = create_pool(
        client,
        headers,
        name="Another pool",
    )
    bet = create_bet(
        client,
        pool["id"],
        headers,
    )
    sibling = create_bet(
        client,
        pool["id"],
        headers,
    )
    unrelated = create_bet(
        client,
        other_pool["id"],
        headers,
    )
    bet_id = unrelated["id"] if target == "bet-from-other-pool" else bet["id"]
    if target == "unknown-bet":
        bet_id = str(uuid.uuid4())
    outcome_id = (
        unrelated["options"][0]["id"]
        if target == "bet-from-other-pool"
        else sibling["options"][0]["id"]
    )

    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet_id}/picks",
        json=pick_payload(outcome_id),
        headers=headers,
    )

    assert response.status_code == 400
    assert pick_repo.picks == {}


def test_a_bet_with_a_winner_does_not_close_its_open_sibling(
    client,
    user_repo,
    pool_repo,
):
    # A migrated Bet may already have a winner, even while its Pool's deadline is future.
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )
    resolved = create_bet(
        client,
        pool["id"],
        headers,
    )
    sibling = create_bet(
        client,
        pool["id"],
        headers,
    )
    stored = pool_repo.get_pool(pool["id"])
    pool_repo.pools[0] = replace(
        stored,
        bets=(
            replace(stored.bets[0], winning_outcome_id=resolved["options"][0]["id"]),
            stored.bets[1],
        ),
    )

    refused = client.post(
        f"/api/pools/{pool['id']}/bets/{resolved['id']}/picks",
        json=pick_payload(resolved["options"][0]["id"]),
        headers=headers,
    )
    accepted = client.post(
        f"/api/pools/{pool['id']}/bets/{sibling['id']}/picks",
        json=pick_payload(sibling["options"][0]["id"]),
        headers=headers,
    )

    assert refused.status_code == 400
    assert refused.get_json() == {"error": "Picks are closed for this bet."}
    assert accepted.status_code == 201
    assert client.get(f"/api/pools/{pool['id']}").get_json()["status"] == "OPEN"


def test_empty_pool_has_no_user_picks(
    client,
    user_repo,
):
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )

    response = client.get(
        f"/api/pools/{pool['id']}/picks",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == {"picks": []}
