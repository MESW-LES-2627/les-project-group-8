"""Database access for picks, using supabase-py. Rows are mapped to dataclasses by hand."""

from datetime import datetime

from users.models import User

from .models import Answer, ChoiceAnswer, Pick, TextAnswer

_PICK_COLUMNS = "id, bet_id, user_id, outcome_id, answer_text, created_at, user:users!user_id(id, name)"


class SupabasePickRepository:
    def __init__(self, client):
        self._db = client

    def list_user_picks(self, bet_ids: tuple[str, ...], user_id: str) -> list[Pick]:
        return _execute(self._picks_for(bet_ids).eq("user_id", user_id))

    def list_all_picks(self, bet_ids: tuple[str, ...]) -> list[Pick]:
        return _execute(self._picks_for(bet_ids))

    def _picks_for(self, bet_ids: tuple[str, ...]):
        return self._db.table("picks").select(_PICK_COLUMNS).in_("bet_id", list(bet_ids))

    def create_or_replace(self, bet_id: str, user_id: str, answer: Answer) -> Pick:
        row = (
            self._db.table("picks")
            .upsert(
                {"bet_id": bet_id, "user_id": user_id, **_answer_columns(answer)},
                on_conflict="bet_id,user_id",
            )
            .select(_PICK_COLUMNS)
            .execute()
            .data[0]
        )
        return _to_pick(row)


def _execute(query) -> list[Pick]:
    return [_to_pick(row) for row in query.order("created_at").order("id").execute().data]


def _to_pick(row: dict) -> Pick:
    return Pick(
        id=str(row["id"]),
        bet_id=str(row["bet_id"]),
        user_id=str(row["user_id"]),
        answer=_to_answer(row),
        created_at=datetime.fromisoformat(row["created_at"]),
        user=User(id=str(row["user"]["id"]), name=row["user"]["name"]),
    )


def _answer_columns(answer: Answer) -> dict:
    """Both columns are always written, so replacing a Pick clears the other one."""
    match answer:
        case ChoiceAnswer(outcome_id):
            return {"outcome_id": outcome_id, "answer_text": None}
        case TextAnswer(text):
            return {"outcome_id": None, "answer_text": text}
    raise TypeError(f"Unknown answer: {answer!r}")


def _to_answer(row: dict) -> Answer:
    if row.get("answer_text") is not None:
        return TextAnswer(row["answer_text"])
    return ChoiceAnswer(str(row["outcome_id"]))
