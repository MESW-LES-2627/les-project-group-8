"""US22: A participant's wins and losses, independent of the resolution API."""

import uuid

import pytest

from tests.acceptance.steps import create_bet, create_pool, sign_in


@pytest.fixture
def participant_pool(client, user_repo):
    user, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    return user, headers, pool


def seed_pick(client, pool_repo, pick_repo, user, pool, headers, *, winner=None, choice=0):
    bet = create_bet(client, pool["id"], headers)
    pick_repo.create_or_replace(bet["id"], user.id, bet["options"][choice]["id"])
    if winner is not None:
        pool_repo.resolve_bet(pool["id"], bet["id"], bet["options"][winner]["id"])
    return bet


def leaderboard(client, pool):
    # Public: deliberately no Authorization header.
    response = client.get(f"/api/pools/{pool['id']}/leaderboard")
    assert response.status_code == 200
    return response.get_json()


def record(user, wins, losses, rank=1):
    return {"user": {"id": user.id, "name": user.name}, "wins": wins, "losses": losses, "rank": rank}


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


def test_orders_by_wins_then_losses_and_shares_competition_ranks(client, pool_repo, pick_repo, user_repo, participant_pool):
    _, headers, pool = participant_pool
    # Insert in a different order; equal display names still represent distinct Users.
    expected = []
    for wins, losses, rank in ((1, 1, 4), (2, 0, 1), (1, 0, 2), (1, 0, 2)):
        user, _ = sign_in(user_repo, "Same name")
        for winner in [0] * wins + [1] * losses:
            seed_pick(client, pool_repo, pick_repo, user, pool, headers, winner=winner)
        expected.append(record(user, wins, losses, rank))
    expected.sort(key=lambda entry: (-entry["wins"], entry["losses"], entry["user"]["id"]))
    assert leaderboard(client, pool) == expected


def test_pool_without_picks_has_empty_leaderboard(client, participant_pool):
    assert leaderboard(client, participant_pool[2]) == []


@pytest.mark.parametrize("pool_id", [str(uuid.uuid4()), "invalid"])
def test_unknown_pool_returns_404(client, pool_id):
    response = client.get(f"/api/pools/{pool_id}/leaderboard")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Pool not found."}
