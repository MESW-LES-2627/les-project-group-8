"""US18: Only the Pool's decider can resolve its Bets."""

import uuid
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from pools.models import UserSummary
from tests.acceptance.steps import bearer, create_bet, create_pool, expired_token, sign_in


@pytest.fixture
def pool_with_decider(client, user_repo, pool_repo):
    _, creator_headers = sign_in(user_repo, "Creator")
    decider, decider_headers = sign_in(user_repo, "Decider")
    _, participant_headers = sign_in(user_repo, "Participant")
    pool = create_pool(client, creator_headers)
    bet = create_bet(client, pool["id"], creator_headers)
    # Creation currently assigns the creator as decider; seed distinct roles to
    # prove that resolution checks the decider, independently of the creator.
    pool_repo.pools[0] = replace(
        pool_repo.pools[0],
        decider=UserSummary.of(decider),
        deadline=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    return pool, bet, {
        "creator": creator_headers,
        "decider": decider_headers,
        "participant": participant_headers,
    }


@pytest.mark.parametrize("role", ["creator", "participant"])
@pytest.mark.parametrize("valid_payload", [True, False], ids=["valid-payload", "non-object"])
def test_non_decider_is_forbidden_and_bet_unchanged(
    client, pool_repo, pool_with_decider, role, valid_payload,
):
    pool, bet, headers = pool_with_decider
    before = tuple(pool_repo.pools)
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": bet["options"][0]["id"]} if valid_payload else [],
        headers=headers[role],
    )
    assert response.status_code == 403
    assert response.get_json() == {"error": "Only the pool's decider can resolve bets."}
    assert tuple(pool_repo.pools) == before


def test_decider_who_is_not_creator_can_resolve(client, pool_repo, pool_with_decider):
    pool, bet, headers = pool_with_decider
    winner = bet["options"][1]["id"]
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": winner}, headers=headers["decider"],
    )
    assert response.status_code == 200
    assert response.get_json() == {**bet, "winning_outcome_id": winner}
    assert pool_repo.get_pool(pool["id"]).find_bet(bet["id"]).winning_outcome_id == winner


@pytest.mark.parametrize("role", ["decider", "participant"])
@pytest.mark.parametrize("target", [
    "unknown-pool", "unknown-bet", "malformed-pool", "malformed-bet", "other-pool-bet",
])
def test_missing_or_mismatched_bet_returns_404(
    client, pool_repo, pool_with_decider, role, target,
):
    pool, bet, headers = pool_with_decider
    pool_id, bet_id = pool["id"], bet["id"]
    if target == "unknown-pool":
        pool_id = str(uuid.uuid4())
    elif target == "unknown-bet":
        bet_id = str(uuid.uuid4())
    elif target == "malformed-pool":
        pool_id = "invalid"
    elif target == "malformed-bet":
        bet_id = "invalid"
    else:
        other_pool = create_pool(client, headers["creator"])
        other_bet = create_bet(client, other_pool["id"], headers["creator"])
        bet_id = other_bet["id"]
    before = tuple(pool_repo.pools)
    response = client.post(
        f"/api/pools/{pool_id}/bets/{bet_id}/resolve",
        json={"winning_outcome_id": bet["options"][0]["id"]}, headers=headers[role],
    )
    assert response.status_code == 404
    assert tuple(pool_repo.pools) == before


@pytest.mark.parametrize("auth", ["missing", "invalid", "expired"])
def test_resolve_requires_login(client, pool_repo, pool_with_decider, auth):
    pool, bet, _ = pool_with_decider
    decider_id = pool_repo.get_pool(pool["id"]).decider.id
    headers = {} if auth == "missing" else bearer(
        expired_token(decider_id) if auth == "expired" else "invalid",
    )
    before = tuple(pool_repo.pools)
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": bet["options"][0]["id"]}, headers=headers,
    )
    assert response.status_code == 401
    assert tuple(pool_repo.pools) == before
