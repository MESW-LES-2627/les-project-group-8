from datetime import datetime, timedelta, timezone

import pytest

from pool_api.domain import (
    GUEST_USER_ID,
    NewPool,
    Outcome,
    Pool,
    PoolStatus,
    UserSummary,
    ValidationError,
)

NOW = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
GUEST = UserSummary(id=GUEST_USER_ID, name="Guest User")


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
    )


class TestNewPoolValidation:
    def test_valid_payload_is_normalised(self):
        pool = NewPool.from_payload(
            make_payload(name="  Final  ", options=[" Yes ", "No"]),
            creator_id=GUEST_USER_ID,
            now=NOW,
        )
        assert pool.name == "Final"
        assert pool.options == ("Yes", "No")
        assert pool.deadline == datetime(2026, 11, 1, 20, 0, tzinfo=timezone.utc)

    def test_decider_defaults_to_creator(self):
        pool = NewPool.from_payload(make_payload(), creator_id="abc", now=NOW)
        assert pool.decider_id == "abc"

    @pytest.mark.parametrize("payload", [None, [], "x"])
    def test_rejects_non_object_body(self, payload):
        with pytest.raises(ValidationError, match="JSON object"):
            NewPool.from_payload(payload, creator_id=GUEST_USER_ID, now=NOW)

    @pytest.mark.parametrize("field", ["name", "statement"])
    @pytest.mark.parametrize("value", [None, "", "   ", 42])
    def test_rejects_empty_text_fields(self, field, value):
        with pytest.raises(ValidationError, match="cannot be empty"):
            NewPool.from_payload(
                make_payload(**{field: value}), creator_id=GUEST_USER_ID, now=NOW
            )

    def test_rejects_overlong_name(self):
        with pytest.raises(ValidationError, match="at most 120"):
            NewPool.from_payload(
                make_payload(name="x" * 121), creator_id=GUEST_USER_ID, now=NOW
            )

    def test_rejects_overlong_statement(self):
        with pytest.raises(ValidationError, match="at most 500"):
            NewPool.from_payload(make_payload(statement="x" * 501), now=NOW)

    def test_accepts_text_at_contract_limits(self):
        pool = NewPool.from_payload(
            make_payload(name="n" * 120, statement="s" * 500, options=["a" * 100, "b" * 100]),
            now=NOW,
        )
        assert len(pool.name) == 120
        assert len(pool.statement) == 500
        assert tuple(map(len, pool.options)) == (100, 100)

    def test_rejects_overlong_outcome(self):
        with pytest.raises(ValidationError, match="at most 100"):
            NewPool.from_payload(make_payload(options=["a" * 101, "No"]), now=NOW)

    @pytest.mark.parametrize(
        "overrides",
        [
            {"name": " " + "n" * 120},
            {"statement": "s" * 500 + " "},
            {"options": [" " + "a" * 100, "No"]},
        ],
    )
    def test_length_limits_apply_to_submitted_strings(self, overrides):
        with pytest.raises(ValidationError, match="at most"):
            NewPool.from_payload(make_payload(**overrides), now=NOW)

    def test_rejects_unicode_equivalent_outcomes(self):
        with pytest.raises(ValidationError, match="exactly 2 unique"):
            NewPool.from_payload(make_payload(options=["Straße", " STRASSE "]), now=NOW)

    @pytest.mark.parametrize(
        "options",
        [None, [], ["Yes"], ["Yes", "No", "Maybe"], ["Yes", ""], ["Yes", "yes "]],
    )
    def test_rejects_bad_options(self, options):
        with pytest.raises(ValidationError, match="exactly 2 unique"):
            NewPool.from_payload(
                make_payload(options=options), creator_id=GUEST_USER_ID, now=NOW
            )

    @pytest.mark.parametrize("deadline", ["2026-10-19T12:00:00Z", "2020-01-01T00:00:00Z"])
    def test_rejects_past_or_present_deadline(self, deadline):
        with pytest.raises(ValidationError, match="in the future"):
            NewPool.from_payload(
                make_payload(deadline=deadline), creator_id=GUEST_USER_ID, now=NOW
            )

    @pytest.mark.parametrize(
        "deadline",
        ["tomorrow", "2026-13-01T00:00:00Z", "2026-11-01T20:00:00+00:99", "2026-11-01T20:00:00+24:00"],
    )
    def test_rejects_malformed_deadline(self, deadline):
        with pytest.raises(ValidationError, match="ISO-8601"):
            NewPool.from_payload(
                make_payload(deadline=deadline), creator_id=GUEST_USER_ID, now=NOW
            )

    @pytest.mark.parametrize(
        "deadline",
        [None, 42, "2026-11-01", "2026-11-01T20:00:00", "20261101T200000Z", "2026-11-01 20:00:00Z"],
    )
    def test_rejects_deadline_without_explicit_date_time_and_timezone(self, deadline):
        with pytest.raises(ValidationError, match="ISO-8601"):
            NewPool.from_payload(make_payload(deadline=deadline), now=NOW)

    @pytest.mark.parametrize(
        "deadline", ["2026-11-01T22:00:00+02:00", "2026-11-01T15:00:00-05:00"]
    )
    def test_normalises_timezone_offsets(self, deadline):
        pool = NewPool.from_payload(make_payload(deadline=deadline), now=NOW)
        assert pool.deadline == datetime(2026, 11, 1, 20, tzinfo=timezone.utc)

    def test_accepts_fractional_seconds_and_lowercase_utc_marker(self):
        pool = NewPool.from_payload(
            make_payload(deadline="2026-11-01t20:00:00.123456z"), now=NOW
        )
        assert pool.deadline == datetime(2026, 11, 1, 20, 0, 0, 123456, tzinfo=timezone.utc)

    def test_compares_deadline_as_an_instant(self):
        with pytest.raises(ValidationError, match="in the future"):
            NewPool.from_payload(make_payload(deadline="2026-10-19T13:00:00+01:00"), now=NOW)

    def test_does_not_allow_request_to_override_guest_identity(self):
        pool = NewPool.from_payload(
            make_payload(creator_id="another-user", decider_id="another-decider"), now=NOW
        )
        assert pool.creator_id == GUEST_USER_ID
        assert pool.decider_id == GUEST_USER_ID

    def test_does_not_modify_request_data(self):
        payload = make_payload(name="  Final  ", options=[" Yes ", "No"])
        NewPool.from_payload(payload, now=NOW)
        assert payload["name"] == "  Final  "
        assert payload["options"] == [" Yes ", "No"]


class TestPoolStatus:
    def test_open_before_deadline(self):
        assert make_pool(NOW + timedelta(seconds=1)).status(NOW) is PoolStatus.OPEN

    def test_locked_at_or_after_deadline(self):
        assert make_pool(NOW).status(NOW) is PoolStatus.LOCKED

    def test_resolved_when_winner_set(self):
        pool = make_pool(NOW + timedelta(days=1), winning_outcome_id="o1")
        assert pool.status(NOW) is PoolStatus.RESOLVED

    def test_resolved_after_deadline(self):
        assert make_pool(NOW - timedelta(days=1), "o1").status(NOW) is PoolStatus.RESOLVED

    def test_timezone_offset_does_not_change_status(self):
        deadline = NOW.astimezone(timezone(timedelta(hours=-5)))
        assert make_pool(deadline).status(NOW) is PoolStatus.LOCKED

    def test_pool_serializes_nested_values_and_utc_deadline(self):
        pool = Pool(
            id="p1",
            name="Final",
            statement="Home team wins.",
            deadline=datetime(2099, 1, 1, 15, tzinfo=timezone(timedelta(hours=-5))),
            creator=GUEST,
            decider=GUEST,
            options=(Outcome("o1", "Yes"), Outcome("o2", "No")),
        )
        body = pool.to_dict()
        assert body["deadline"] == "2099-01-01T20:00:00Z"
        assert body["status"] == "OPEN"
        assert body["creator"] == body["decider"] == {"id": GUEST_USER_ID, "name": "Guest User"}
        assert body["options"] == [{"id": "o1", "label": "Yes"}, {"id": "o2", "label": "No"}]
        assert body["winning_outcome_id"] is None
