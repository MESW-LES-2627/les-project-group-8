"""US20: A Bet is resolved at most once; the winner is final."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tests.acceptance.steps import create_bet, create_pool, sign_in


@pytest.fixture
def resolved_bet(client, user_repo, pool_repo):
    """A resolved Bet in a locked Pool: the Pool's decider picked one Outcome."""
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = create_bet(client, pool["id"], headers)
    pool_repo.pools[0] = replace(
        pool_repo.pools[0],
        deadline=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    winner = bet["options"][0]["id"]
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": winner},
        headers=headers,
    )
    assert response.status_code == 200
    return pool, bet, headers, winner


def resolve_again(client, pool, bet, headers):
    """Try to replace the existing winner with the Bet's other Outcome."""
    return client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": bet["options"][1]["id"]},
        headers=headers,
    )


def test_resolving_a_resolved_bet_conflicts(client, resolved_bet):
    # Given a Bet that already has a winner
    pool, bet, headers, _ = resolved_bet

    # When the decider resolves it again
    response = resolve_again(client, pool, bet, headers)

    # Then it is refused and the winner is unchanged
    assert response.status_code == 409
    assert response.get_json() == {"error": "This bet is already resolved."}


def test_a_second_resolution_keeps_the_first_winner(client, pool_repo, resolved_bet):
    # Given a Bet that already has a winner
    pool, bet, headers, winner = resolved_bet

    # When a second resolution is attempted
    resolve_again(client, pool, bet, headers)

    # Then the first winner is still stored
    assert pool_repo.get_pool(pool["id"]).find_bet(bet["id"]).winning_outcome_id == winner


def test_a_resolved_bet_stays_resolved(client, resolved_bet):
    # Given a Bet that already has a winner
    pool, bet, headers, winner = resolved_bet

    # When I open its Pool
    response = client.get(f"/api/pools/{pool['id']}")

    # Then the Bet is still resolved with the same winning Outcome
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "LOCKED"
    assert body["bets"][0]["winning_outcome_id"] == winner
