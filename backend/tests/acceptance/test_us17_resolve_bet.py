"""US17: Store a valid winning outcome and expose it when reading pools."""

import uuid
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tests.acceptance.steps import create_bet, create_pool, sign_in


@pytest.fixture
def unresolved_bet(client, user_repo, pool_repo):
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = create_bet(client, pool["id"], headers)
    pool_repo.pools[0] = replace(
        pool_repo.pools[0], deadline=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    return pool, bet, headers


def test_resolve_stores_the_winner(client, pool_repo, unresolved_bet):
    pool, bet, headers = unresolved_bet
    winner = bet["options"][1]["id"]
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": winner}, headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json() == {**bet, "winning_outcome_id": winner}
    assert pool_repo.get_pool(pool["id"]).find_bet(bet["id"]).winning_outcome_id == winner


@pytest.mark.parametrize("listing", [False, True], ids=["open-pool", "list-pools"])
def test_reading_pools_includes_the_result(client, unresolved_bet, listing):
    pool, bet, headers = unresolved_bet
    winner = bet["options"][0]["id"]
    assert client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": winner}, headers=headers,
    ).status_code == 200
    response = client.get("/api/pools" if listing else f"/api/pools/{pool['id']}")
    assert response.status_code == 200
    result = response.get_json()[0] if listing else response.get_json()
    assert result["bets"][0]["winning_outcome_id"] == winner
    assert result["status"] == "LOCKED"


@pytest.mark.parametrize("same_pool", [True, False], ids=["same-pool", "other-pool"])
def test_outcome_from_another_bet_is_rejected(client, user_repo, pool_repo, same_pool):
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = create_bet(client, pool["id"], headers)
    other_pool = pool if same_pool else create_pool(client, headers)
    other_bet = create_bet(client, other_pool["id"], headers)
    pool_repo.pools[0] = replace(
        pool_repo.pools[0], deadline=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    before = tuple(pool_repo.pools)
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": other_bet["options"][0]["id"]}, headers=headers,
    )
    assert response.status_code == 400
    assert tuple(pool_repo.pools) == before


@pytest.mark.parametrize("payload", [
    {}, {"winning_outcome_id": str(uuid.uuid4())}, {"winning_outcome_id": "invalid"},
    {"winning_outcome_id": None}, {"winning_outcome_id": []}, [],
], ids=["missing", "unknown", "malformed", "null", "wrong-type", "non-object"])
def test_invalid_winner_leaves_the_bet_unchanged(client, pool_repo, unresolved_bet, payload):
    pool, bet, headers = unresolved_bet
    before = pool_repo.get_pool(pool["id"])
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve", json=payload, headers=headers,
    )
    assert response.status_code == 400
    assert pool_repo.get_pool(pool["id"]) == before
