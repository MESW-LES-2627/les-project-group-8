"""Pool.status(): the single clock rule for Picks and resolutions."""

from datetime import datetime, timedelta, timezone

from pools.models import Pool, PoolStatus, UserSummary

NOW = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
DECIDER = UserSummary(id="u1", name="Ana")


def make_pool(deadline):
    return Pool(
        id="p1",
        name="Final",
        description="",
        deadline=deadline,
        creator=DECIDER,
        decider=DECIDER,
        created_at=deadline - timedelta(days=1),
    )


def test_a_pool_is_open_before_its_deadline():
    assert make_pool(NOW).status(now=NOW - timedelta(microseconds=1)) == PoolStatus.OPEN


def test_the_deadline_itself_is_late_enough():
    # US19.3: exactly at the deadline is already late, not still open.
    assert make_pool(NOW).status(now=NOW) == PoolStatus.LOCKED


def test_a_pool_is_locked_after_its_deadline():
    assert make_pool(NOW).status(now=NOW + timedelta(microseconds=1)) == PoolStatus.LOCKED
