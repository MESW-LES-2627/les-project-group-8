"""US19: A Bet resolves only at or after the Pool deadline."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tests.acceptance.steps import create_bet, create_pool, iso, sign_in


@pytest.fixture
def open_bet(client, user_repo):
    """A Bet in a Pool whose deadline is still in the future."""
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client, headers,
        deadline=iso(datetime.now(timezone.utc) + timedelta(minutes=5)),
    )
    bet = create_bet(client, pool["id"], headers)
    return pool, bet, headers


def resolve(client, pool, bet, headers):
    return client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": bet["options"][0]["id"]},
        headers=headers,
    )


def test_resolving_before_the_deadline_is_rejected(client, pool_repo, open_bet):
    # Given a Pool whose deadline is in the future
    pool, bet, headers = open_bet
    before = tuple(pool_repo.pools)

    # When its decider resolves a Bet
    response = resolve(client, pool, bet, headers)

    # Then it is refused and the Bet is unchanged
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "This bet cannot be resolved before the pool deadline.",
    }
    assert tuple(pool_repo.pools) == before


def test_resolving_after_the_deadline_is_accepted(client, pool_repo, open_bet):
    # Given a Pool whose deadline has passed
    pool, bet, headers = open_bet
    pool_repo.pools[0] = replace(
        pool_repo.pools[0],
        deadline=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    # When its decider resolves a Bet
    response = resolve(client, pool, bet, headers)

    # Then the resolution is accepted
    assert response.status_code == 200
    assert response.get_json()["winning_outcome_id"] == bet["options"][0]["id"]


def test_resolving_at_the_deadline_is_accepted(client, pool_repo, open_bet):
    # Given a Pool whose deadline is exactly now
    pool, bet, headers = open_bet
    pool_repo.pools[0] = replace(
        pool_repo.pools[0], deadline=datetime.now(timezone.utc),
    )

    # When its decider resolves a Bet
    response = resolve(client, pool, bet, headers)

    # Then the resolution is accepted: only the time before the deadline is too early
    assert response.status_code == 200
