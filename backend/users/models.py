"""Plain data for the users module."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
    name: str
