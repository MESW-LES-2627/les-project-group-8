"""SupabasePoolRepository.resolve_bet: a Bet is updated only while it has no winner (US20)."""

from pools.repository import SupabasePoolRepository

ROW = {
    "id": "b1",
    "pool_id": "p1",
    "statement": "Real Madrid wins in 90 minutes.",
    "winning_outcome_id": "o1",
    "created_at": "2026-11-17T12:00:00+00:00",
    "presentation": "radio",
    "outcomes": [
        {"id": "o1", "label": "Yes", "position": 0},
        {"id": "o2", "label": "No", "position": 1},
    ],
}


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, calls, rows):
        self.calls = calls
        self.rows = rows

    def update(self, values):
        self.calls.append(("update", values))
        return self

    def eq(self, column, value):
        self.calls.append(("eq", column, value))
        return self

    def is_(self, column, value):
        self.calls.append(("is_", column, value))
        return self

    def select(self, columns):
        self.calls.append(("select", columns))
        return self

    def execute(self):
        return FakeResponse(self.rows)


class FakeClient:
    """Records the query the repository builds; returns `rows` from execute()."""

    def __init__(self, rows):
        self.calls = []
        self.rows = rows

    def table(self, name):
        self.calls.append(("table", name))
        return FakeQuery(self.calls, self.rows)


def test_resolve_updates_only_a_bet_without_a_winner():
    client = FakeClient([ROW])

    bet = SupabasePoolRepository(client).resolve_bet("p1", "b1", "o1")

    assert bet is not None
    assert bet.winning_outcome_id == "o1"
    # Without this filter, two concurrent resolutions can overwrite each other.
    assert ("is_", "winning_outcome_id", None) in client.calls
    assert ("eq", "id", "b1") in client.calls


def test_resolve_returns_none_when_no_bet_matches():
    client = FakeClient([])

    assert SupabasePoolRepository(client).resolve_bet("p1", "b1", "o1") is None
