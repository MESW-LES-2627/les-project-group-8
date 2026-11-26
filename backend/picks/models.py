"""Plain data for the picks module."""

from dataclasses import dataclass
from datetime import datetime

from users.models import User


@dataclass(frozen=True)
class ChoiceAnswer:
    """An answer to a multiple-choice Bet: one of its Outcomes."""

    outcome_id: str


@dataclass(frozen=True)
class TextAnswer:
    """An answer to an open-ended Bet: trimmed, non-empty free text."""

    text: str


Answer = ChoiceAnswer | TextAnswer


@dataclass(frozen=True)
class Pick:
    """One participant's answer to one Bet."""

    id: str
    bet_id: str
    user_id: str
    answer: Answer
    created_at: datetime
    user: User
