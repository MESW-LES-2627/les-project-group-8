"""Read projections for a participant's record in a pool."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringPick:
    user_id: str
    user_name: str
    outcome_id: str
    winning_outcome_id: str | None


@dataclass
class LeaderboardEntry:
    user_id: str
    user_name: str
    wins: int = 0
    losses: int = 0
    rank: int = 0
