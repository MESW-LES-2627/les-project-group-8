from datetime import datetime, timedelta, timezone

import pytest

from pools.models import Pool, PoolStatus, UserSummary
from pools.service import parse_new_pool
from shared.errors import ValidationError

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
GUEST = UserSummary(id="00000000-0000-0000-0000-000000000001", name="Guest User")


def make_payload(**overrides):
    payload = {
        "name": "Final",
        "statement": "Home team wins.",
        "deadline": "2026-11-01T20:00:00Z",
        "options": ["Yes", "No"],
    }
    payload.update(overrides)
    return payload


def make_pool(deadline, winning_outcome_id=None):
    return Pool(
        id="p1",
        name="n",
        statement="s",
        deadline=deadline,
        creator=GUEST,
        decider=GUEST,
        options=(),
        winning_outcome_id=winning_outcome_id,
        created_at=NOW,
    )


class TestNewPoolValidation:
    def test_valid_payload_is_normalised(self):
        pool = parse_new_pool(
            make_payload(name="  Final  ", options=[" Yes ", "No"]),
            creator=GUEST,
            now=NOW,
        )
        assert pool.name == "Final"
        assert pool.options == ("Yes", "No")
        assert pool.deadline == datetime(2026, 11, 1, 20, 0, tzinfo=timezone.utc)

    def test_decider_defaults_to_creator(self):
        creator = UserSummary(id="abc", name="Ana")
        pool = parse_new_pool(make_payload(), creator=creator, now=NOW)
        assert pool.decider == creator

    @pytest.mark.parametrize("payload", [None, [], "x"])
    def test_rejects_non_object_body(self, payload):
        with pytest.raises(ValidationError, match="JSON object"):
            parse_new_pool(payload, creator=GUEST, now=NOW)

    @pytest.mark.parametrize("field", ["name", "statement"])
    @pytest.mark.parametrize("value", [None, "", "   ", 42])
    def test_rejects_empty_text_fields(self, field, value):
        with pytest.raises(ValidationError, match="cannot be empty"):
            parse_new_pool(make_payload(**{field: value}), creator=GUEST, now=NOW)

    def test_rejects_overlong_name(self):
        with pytest.raises(ValidationError, match="at most 120"):
            parse_new_pool(make_payload(name="x" * 121), creator=GUEST, now=NOW)

    @pytest.mark.parametrize(
        "options",
        [None, [], ["Yes"], ["Yes", "No", "Maybe"], ["Yes", ""], ["Yes", "yes "]],
    )
    def test_rejects_bad_options(self, options):
        with pytest.raises(ValidationError, match="exactly 2 unique"):
            parse_new_pool(make_payload(options=options), creator=GUEST, now=NOW)

    @pytest.mark.parametrize("deadline", ["2026-10-19T12:00:00Z", "2020-01-01T00:00:00Z"])
    def test_rejects_past_or_present_deadline(self, deadline):
        with pytest.raises(ValidationError, match="in the future"):
            parse_new_pool(make_payload(deadline=deadline), creator=GUEST, now=NOW)

    @pytest.mark.parametrize("deadline", ["tomorrow", "2026-13-01T00:00:00Z"])
    def test_rejects_malformed_deadline(self, deadline):
        with pytest.raises(ValidationError, match="ISO-8601"):
            parse_new_pool(make_payload(deadline=deadline), creator=GUEST, now=NOW)


class TestPoolStatus:
    def test_open_before_deadline(self):
        assert make_pool(NOW + timedelta(seconds=1)).status(NOW) is PoolStatus.OPEN

    def test_locked_at_or_after_deadline(self):
        assert make_pool(NOW).status(NOW) is PoolStatus.LOCKED

    def test_resolved_when_winner_set(self):
        pool = make_pool(NOW + timedelta(days=1), winning_outcome_id="o1")
        assert pool.status(NOW) is PoolStatus.RESOLVED
