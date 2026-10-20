"""Compatibility helpers for persistence."""

from __future__ import annotations

from app import InMemoryStore, get_supabase_client


class PoolRepository:
    pass


class SupabasePoolRepository(PoolRepository):
    @classmethod
    def from_env(cls):
        return get_supabase_client()
