"""Plain data for the picks module."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Pick:
    """One participant's answer to one question (a pool in the current model)."""

    id: str
    pool_id: str
    user_id: str
    outcome_id: str
    created_at: datetime
