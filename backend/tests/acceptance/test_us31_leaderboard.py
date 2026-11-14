"""US31: A pool's leaderboard ranks everyone's records."""

import uuid

import pytest

from tests.acceptance.steps import create_pool, leaderboard, record, seed_pick, sign_in


@pytest.fixture
def given_records(client, pool_repo, pick_repo, user_repo):
    """Seed a Pool with one participant per (wins, losses); return the Pool and its participants."""
    def seed(*records):
        _, headers = sign_in(user_repo, "Creator")
        pool = create_pool(client, headers)
        participants = []
        for wins, losses in records:
            # Equal display names still represent distinct Users.
            participant, _ = sign_in(user_repo, "Same name")
            for winner in [0] * wins + [1] * losses:
                seed_pick(client, pool_repo, pick_repo, participant, pool, headers, winner=winner)
            participants.append(participant)
        return pool, participants
    return seed


def test_most_wins_come_first(client, given_records):
    # AC 31.1
    pool, (fewer, most) = given_records((1, 0), (2, 0))
    assert leaderboard(client, pool) == [record(most, 2, 0, rank=1), record(fewer, 1, 0, rank=2)]


def test_equal_wins_put_fewer_losses_first(client, given_records):
    # AC 31.2
    pool, (more, fewer) = given_records((1, 1), (1, 0))
    assert leaderboard(client, pool) == [record(fewer, 1, 0, rank=1), record(more, 1, 1, rank=2)]


def test_equal_records_share_a_competition_rank(client, given_records):
    # AC 31.3: ranks 1, 2, 2, 4; ties are listed by user id.
    pool, (last, first, *tied) = given_records((1, 1), (2, 0), (1, 0), (1, 0))
    tied.sort(key=lambda user: user.id)
    assert leaderboard(client, pool) == [
        record(first, 2, 0, rank=1),
        record(tied[0], 1, 0, rank=2),
        record(tied[1], 1, 0, rank=2),
        record(last, 1, 1, rank=4),
    ]


def test_pool_without_picks_has_empty_leaderboard(client, given_records):
    # AC 31.4
    pool, _ = given_records()
    assert leaderboard(client, pool) == []


@pytest.mark.parametrize("pool_id", [str(uuid.uuid4()), "invalid"])
def test_unknown_pool_returns_404(client, pool_id):
    # AC 31.5
    response = client.get(f"/api/pools/{pool_id}/leaderboard")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Pool not found."}
