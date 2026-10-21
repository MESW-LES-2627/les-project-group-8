"""Friendly Pools Flask API.

A simple, direct Flask backend:
- Direct Supabase table queries (no ORM, no stored procedures).
- Simple, straightforward endpoints: GET /api/health, GET /api/pools, POST /api/pools.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from supabase import create_client, Client

load_dotenv()

app: Flask = Flask(__name__)

def require_value[T](val: T | None, value_name: str="Value") -> T:
    if val is None:
        raise ValueError(f"{value_name} cannot be None")
    return val

def get_supabase_client() -> Client:
    url: str = require_value(os.environ.get("SUPABASE_URL"), "SUPABASE_URL")
    key: str = require_value(os.environ.get("SUPABASE_KEY"), "SUPABASE_KEY")
    return create_client(url, key)

sb: Client = get_supabase_client()

GUEST_USER_ID: str = "00000000-0000-0000-0000-000000000001"
GUEST_USER: dict = {"id": GUEST_USER_ID, "name": "Guest User"}

@app.get("/api/health")
def health() -> Response:
    return jsonify(status="ok")

@app.post("/api/pools")
def create_pool():
    payload: dict = require_value(request.get_json(silent=True), "Request body")
    try:
        validated: dict = validate_pool_payload(payload)
    except ValueError as err:
        return jsonify(error=str(err)), 400

    res = sb.rpc("create_pool", {
        "p_name": validated["name"],
        "p_statement": validated["statement"],
        "p_deadline": validated["deadline"],
        "p_creator_id": GUEST_USER_ID,
        "p_decider_id": GUEST_USER_ID,
        "p_options": validated["options"],
    }).execute()

    pool_id = res.data

    return jsonify({"pool_id": pool_id}), 201

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
    AT_LEAST_TWO_OUTCOMES_MESSAGE = "A pool must have at least two non-empty outcomes."
    if not isinstance(options, list) or len(options) <= 1:
        raise ValueError(AT_LEAST_TWO_OUTCOMES_MESSAGE)
    cleaned_options = []
    seen = set()
    for opt in options:
        if not isinstance(opt, str) or not opt.strip():
            raise ValueError(AT_LEAST_TWO_OUTCOMES_MESSAGE)
        opt_stripped = opt.strip()
        folded = opt_stripped.casefold()
        if folded in seen:
            raise ValueError(AT_LEAST_TWO_OUTCOMES_MESSAGE)
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


if __name__ == '__main__':
    app.run(debug=True)
