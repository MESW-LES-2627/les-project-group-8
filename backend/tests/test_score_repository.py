"""Check the real read projection and pagination without a database."""

from types import SimpleNamespace
from unittest.mock import MagicMock, call

from scores.models import ScoringPick
from scores.repository import SupabaseScoreRepository


def test_reads_all_pick_pages_and_filters_by_bets_pool():
    db = MagicMock()
    query = db.table.return_value
    query.select.return_value = query
    query.eq.return_value = query
    query.order.return_value = query
    query.range.return_value = query
    row = {
        "id": "pick", "outcome_id": "winner",
        "user": {"id": "user", "name": "Ana"},
        "bet": {"pool_id": "pool", "winning_outcome_id": "winner"},
    }
    query.execute.side_effect = [
        SimpleNamespace(data=[row] * 1000),
        SimpleNamespace(data=[{**row, "bet": {"pool_id": "pool", "winning_outcome_id": None}}]),
    ]

    picks = SupabaseScoreRepository(db).list_scoring_picks("pool")

    assert len(picks) == 1001
    assert picks[0] == ScoringPick("user", "Ana", "winner", "winner")
    assert picks[-1] == ScoringPick("user", "Ana", "winner", None)
    assert db.table.call_args_list == [call("picks"), call("picks")]
    assert query.eq.call_args_list == [call("bet.pool_id", "pool")] * 2
    assert query.range.call_args_list == [call(0, 999), call(1000, 1999)]
