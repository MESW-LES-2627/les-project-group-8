"""Plain data for the scores module."""

from dataclasses import dataclass


@dataclass
class LeaderboardEntry:
    user_id: str
    user_name: str
    wins: int = 0
    losses: int = 0
    rank: int = 0
