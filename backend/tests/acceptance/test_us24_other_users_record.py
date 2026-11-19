"""US24: A participant sees another User's record next to their own."""

import pytest

from tests.acceptance.steps import create_pool, leaderboard, record, seed_pick, seed_record, sign_in


@pytest.fixture
def viewer_and_other(client, user_repo):
    """A viewer who created a Pool, and another User with no tie to them."""
    viewer, headers = sign_in(user_repo, "Viewer")
    other, _ = sign_in(user_repo, "Other")
    return viewer, other, headers, create_pool(client, headers)


@pytest.mark.parametrize(
    ("viewer_record", "other_record", "expected"),
    [
        pytest.param((1, 0), (2, 0), [("other", 1), ("viewer", 2)], id="other-above"),
        pytest.param((2, 0), (1, 0), [("viewer", 1), ("other", 2)], id="other-below"),
        # Ranks by losses on equal wins; update with #93 if ranking moves to wins only.
        pytest.param((1, 1), (1, 0), [("other", 1), ("viewer", 2)], id="fewer-losses-above"),
        pytest.param((1, 0), (1, 0), [("viewer", 1), ("other", 1)], id="identical-share-rank"),
    ],
)
def test_other_users_wins_and_losses_are_shown(
    client, pool_repo, pick_repo, viewer_and_other, viewer_record, other_record, expected
):
    # AC 24.1
    viewer, other, headers, pool = viewer_and_other
    seed_record(client, pool_repo, pick_repo, viewer, pool, headers, *viewer_record)
    seed_record(client, pool_repo, pick_repo, other, pool, headers, *other_record)
    rows = {"viewer": (viewer, viewer_record), "other": (other, other_record)}
    expected_rows = [record(rows[who][0], *rows[who][1], rank=rank) for who, rank in expected]
    # Equal ranks are listed by user id.
    expected_rows.sort(key=lambda row: (row["rank"], row["user"]["id"]))
    assert leaderboard(client, pool) == expected_rows


def test_other_user_without_resolved_picks_has_zero_record(client, pool_repo, pick_repo, viewer_and_other):
    # AC 24.2
    viewer, other, headers, pool = viewer_and_other
    seed_record(client, pool_repo, pick_repo, viewer, pool, headers, 1, 0)
    for _ in range(2):
        seed_pick(client, pool_repo, pick_repo, other, pool, headers)
    assert leaderboard(client, pool) == [record(viewer, 1, 0, rank=1), record(other, 0, 0, rank=2)]


def test_other_user_without_picks_in_this_pool_is_absent(client, pool_repo, pick_repo, viewer_and_other):
    # AC 24.3: their Picks in another Pool do not count here.
    viewer, other, headers, pool = viewer_and_other
    seed_record(client, pool_repo, pick_repo, viewer, pool, headers, 1, 0)
    other_pool = create_pool(client, headers)
    seed_pick(client, pool_repo, pick_repo, other, other_pool, headers, winner=0)
    assert leaderboard(client, pool) == [record(viewer, 1, 0)]
