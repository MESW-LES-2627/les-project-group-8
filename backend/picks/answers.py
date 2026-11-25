"""Answer validation strategies: one per Bet answer type (Strategy pattern).

`PickService` owns the rules every Pick shares (who answers, deadline, resolution,
one Pick per User and Bet). What a valid answer looks like depends on the Bet's
answer type, so that part is delegated to the strategy selected for `bet.answer_type`.
A new answer type adds a strategy here and an entry in `default_answer_validators`.
"""

from typing import Mapping, Protocol

from pools.models import AnswerType, Bet
from shared.errors import ValidationError

from .models import Answer, ChoiceAnswer, TextAnswer

MAX_TEXT_ANSWER_LENGTH = 500

_ANSWER_FIELDS = ("outcome_id", "answer_text")


class AnswerValidationStrategy(Protocol):
    def validate(self, payload: dict, bet: Bet) -> Answer:
        """Return the validated answer in `payload` for `bet`, or raise ValidationError."""
        ...


class ChoiceAnswerValidator:
    """A choice answer is the id of one of the Bet's own Outcomes."""

    def validate(self, payload: dict, bet: Bet) -> ChoiceAnswer:
        _refuse_other_fields(payload, "outcome_id", "a multiple-choice bet")
        outcome_id = payload.get("outcome_id")
        if not isinstance(outcome_id, str) or outcome_id not in {
            option.id for option in bet.options
        }:
            raise ValidationError("Field 'outcome_id' must be one of the bet's options.")
        return ChoiceAnswer(outcome_id)


class TextAnswerValidator:
    """A text answer is plain text of 1 to `max_length` code points after trimming."""

    def __init__(self, max_length: int = MAX_TEXT_ANSWER_LENGTH):
        self._max_length = max_length

    def validate(self, payload: dict, bet: Bet) -> TextAnswer:
        _refuse_other_fields(payload, "answer_text", "a text bet")
        raw = payload.get("answer_text")
        if not isinstance(raw, str) or not raw.strip():
            raise ValidationError("Field 'answer_text' cannot be empty.")
        text = raw.strip()
        # Python's len counts code points, which is the unit US28 specifies.
        if len(text) > self._max_length:
            raise ValidationError(
                f"Field 'answer_text' must be at most {self._max_length} characters."
            )
        return TextAnswer(text)


def default_answer_validators() -> Mapping[AnswerType, AnswerValidationStrategy]:
    return {
        AnswerType.CHOICE: ChoiceAnswerValidator(),
        AnswerType.TEXT: TextAnswerValidator(),
    }


def _refuse_other_fields(payload: dict, expected: str, bet_kind: str) -> None:
    for field in _ANSWER_FIELDS:
        if field != expected and field in payload:
            raise ValidationError(f"Field '{field}' is not accepted for {bet_kind}.")
