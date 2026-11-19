"""Plain data for the picks module."""

from dataclasses import dataclass
from datetime import datetime

from users.models import User


@dataclass(frozen=True)
class Pick:
    """One participant's answer to one Bet."""

    id: str
    bet_id: str
    user_id: str
    outcome_id: str
    created_at: datetime
    user: User
