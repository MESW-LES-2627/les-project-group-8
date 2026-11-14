"""US22: A participant's wins and losses, independent of the resolution API."""

import pytest

from tests.acceptance.steps import create_bet, create_pool, leaderboard, record, seed_pick, sign_in


@pytest.fixture
def participant_pool(client, user_repo):
    user, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    return user, headers, pool


def test_winning_picks_count_as_wins(client, pool_repo, pick_repo, participant_pool):
    # AC 22.1: each winning Pick counts once, including non-first outcomes.
    user, headers, pool = participant_pool
    for choice in (0, 1):
        seed_pick(client, pool_repo, pick_repo, user, pool, headers, winner=choice, choice=choice)
    assert leaderboard(client, pool) == [record(user, 2, 0)]


def test_losing_picks_count_as_losses(client, pool_repo, pick_repo, participant_pool):
    # AC 22.2
    user, headers, pool = participant_pool
    for choice in (0, 1):
        seed_pick(client, pool_repo, pick_repo, user, pool, headers, winner=1-choice, choice=choice)
    assert leaderboard(client, pool) == [record(user, 0, 2)]


def test_unresolved_and_unpicked_bets_do_not_change_record(client, pool_repo, pick_repo, participant_pool):
    # AC 22.3: a winner, a loser, an unresolved Pick and an unpicked resolved Bet.
    user, headers, pool = participant_pool
    for winner in (0, 1, None):
        seed_pick(client, pool_repo, pick_repo, user, pool, headers, winner=winner)
    unpicked = create_bet(client, pool["id"], headers)
    pool_repo.resolve_bet(pool["id"], unpicked["id"], unpicked["options"][0]["id"])
    assert leaderboard(client, pool) == [record(user, 1, 1)]


def test_only_unresolved_picks_give_zero_record(client, pool_repo, pick_repo, participant_pool):
    # AC 22.4
    user, headers, pool = participant_pool
    seed_pick(client, pool_repo, pick_repo, user, pool, headers)
    assert leaderboard(client, pool) == [record(user, 0, 0)]


def test_users_without_picks_in_this_pool_are_absent(client, pool_repo, pick_repo, user_repo, participant_pool):
    # AC 22.5: being a creator, or picking in another Pool, is insufficient.
    user, headers, pool = participant_pool
    other_pool = create_pool(client, headers)
    seed_pick(client, pool_repo, pick_repo, user, other_pool, headers, winner=0)
    participant, _ = sign_in(user_repo, "Participant")
    seed_pick(client, pool_repo, pick_repo, participant, pool, headers, winner=1)
    assert leaderboard(client, pool) == [record(participant, 0, 1)]
