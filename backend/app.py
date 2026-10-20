"""Friendly Pools Flask API.

A simple, direct Flask backend:
- Direct Supabase table queries (no ORM, no stored procedures).
- Automatic in-memory fallback for local testing without database.
- Simple, straightforward endpoints: GET /api/health, GET /api/pools, POST /api/pools.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from supabase import create_client

load_dotenv()

GUEST_USER_ID = "00000000-0000-0000-0000-000000000001"
GUEST_USER = {"id": GUEST_USER_ID, "name": "Guest User"}

_POOL_SELECT = (
    "id, name, statement, deadline, winning_outcome_id, created_at,"
    " creator:users!creator_id(id, name),"
    " decider:users!decider_id(id, name),"
    " outcomes(id, label)"
)


def compute_status(deadline_str: str, winning_outcome_id: str | None = None, now: datetime | None = None) -> str:
    if winning_outcome_id:
        return "RESOLVED"
    now_dt = now or datetime.now(timezone.utc)
    try:
        dl = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)
        return "OPEN" if dl > now_dt else "LOCKED"
    except Exception:
        return "LOCKED"


def format_pool(row: dict, now: datetime | None = None) -> dict:
    deadline = str(row["deadline"])
    if not deadline.endswith("Z") and "+" not in deadline:
        deadline = f"{deadline}Z"
    outcomes = row.get("outcomes") or []
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "statement": row["statement"],
        "deadline": deadline,
        "status": compute_status(deadline, row.get("winning_outcome_id"), now=now),
        "winning_outcome_id": row.get("winning_outcome_id"),
        "creator": row.get("creator") or GUEST_USER,
        "decider": row.get("decider") or GUEST_USER,
        "options": [{"id": str(o["id"]), "label": o["label"]} for o in outcomes],
        "created_at": row.get("created_at") or datetime.now(timezone.utc).isoformat(),
    }


def validate_pool_payload(payload: dict, now: datetime | None = None) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Field 'name' cannot be empty.")
    name = name.strip()
    if len(name) > 120:
        raise ValueError("Field 'name' must be at most 120 characters.")

    statement = payload.get("statement")
    if not isinstance(statement, str) or not statement.strip():
        raise ValueError("Field 'statement' cannot be empty.")
    statement = statement.strip()
    if len(statement) > 500:
        raise ValueError("Field 'statement' must be at most 500 characters.")

    options = payload.get("options")
    if not isinstance(options, list) or len(options) != 2:
        raise ValueError("A pool must have exactly 2 unique, non-empty outcomes.")
    cleaned_options = []
    seen = set()
    for opt in options:
        if not isinstance(opt, str) or not opt.strip():
            raise ValueError("A pool must have exactly 2 unique, non-empty outcomes.")
        opt_stripped = opt.strip()
        folded = opt_stripped.casefold()
        if folded in seen:
            raise ValueError("A pool must have exactly 2 unique, non-empty outcomes.")
        seen.add(folded)
        cleaned_options.append(opt_stripped)

    raw_deadline = payload.get("deadline")
    if not isinstance(raw_deadline, str):
        raise ValueError("Field 'deadline' must be an ISO-8601 string.")
    try:
        dl_dt = datetime.fromisoformat(raw_deadline.replace("Z", "+00:00"))
        if dl_dt.tzinfo is None:
            dl_dt = dl_dt.replace(tzinfo=timezone.utc)
    except Exception:
        raise ValueError("Field 'deadline' is not a valid ISO-8601 timestamp.")

    now_dt = now or datetime.now(timezone.utc)
    if dl_dt <= now_dt:
        raise ValueError("Field 'deadline' must be in the future.")

    normalized_deadline = dl_dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "name": name,
        "statement": statement,
        "deadline": normalized_deadline,
        "options": cleaned_options,
    }


def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


class InMemoryStore:
    def __init__(self):
        self.pools: list[dict] = []

    def list_pools(self) -> list[dict]:
        return list(reversed(self.pools))

    def create_pool(self, data: dict) -> dict:
        pool = {
            "id": str(uuid.uuid4()),
            "name": data["name"],
            "statement": data["statement"],
            "deadline": data["deadline"],
            "status": "OPEN",
            "winning_outcome_id": None,
            "creator": GUEST_USER,
            "decider": GUEST_USER,
            "options": [{"id": str(uuid.uuid4()), "label": o} for o in data["options"]],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.pools.append(pool)
        return pool


in_memory_store = InMemoryStore()


def create_app(store=None) -> Flask:
    app = Flask(__name__)
    app.store = store

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/pools")
    def list_pools():
        if app.store is not None:
            return jsonify(app.store.list_pools())

        sb = get_supabase_client()
        if sb:
            try:
                res = sb.table("pools").select(_POOL_SELECT).order("created_at", desc=True).execute()
                return jsonify([format_pool(row) for row in res.data])
            except Exception:
                app.logger.exception("Failed to query Supabase")
                return jsonify(error="Internal server error."), 500

        return jsonify(in_memory_store.list_pools())

    @app.post("/api/pools")
    def create_pool():
        payload = request.get_json(silent=True)
        try:
            validated = validate_pool_payload(payload)
        except ValueError as err:
            return jsonify(error=str(err)), 400

        if app.store is not None:
            try:
                return jsonify(app.store.create_pool(validated)), 201
            except Exception:
                return jsonify(error="Internal server error."), 500

        sb = get_supabase_client()
        if sb:
            try:
                # 1. Insert pool
                pool_insert = sb.table("pools").insert({
                    "name": validated["name"],
                    "statement": validated["statement"],
                    "deadline": validated["deadline"],
                    "creator_id": GUEST_USER_ID,
                    "decider_id": GUEST_USER_ID,
                }).execute()
                pool_id = pool_insert.data[0]["id"]

                # 2. Insert outcomes
                sb.table("outcomes").insert([
                    {"pool_id": pool_id, "label": opt} for opt in validated["options"]
                ]).execute()

                # 3. Fetch full created pool
                row = sb.table("pools").select(_POOL_SELECT).eq("id", pool_id).single().execute().data
                return jsonify(format_pool(row)), 201
            except Exception as err:
                app.logger.exception("Failed to create pool in Supabase: %s", err)
                err_msg = str(err)
                if "row-level security" in err_msg.lower():
                    return jsonify(error="Supabase RLS error: Use the service_role key in backend/.env or disable RLS."), 500
                return jsonify(error="Internal server error."), 500

        return jsonify(in_memory_store.create_pool(validated)), 201

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not found."), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(error="Internal server error."), 500

    return app


app = create_app()
