"""Reusable "Given" steps, so each test reads like its acceptance criterion."""

from datetime import datetime, timedelta, timezone


def create_user(client, name="Ana") -> dict:
    response = client.post("/api/users", json={"name": name})
    assert response.status_code == 201
    return response.get_json()


def pool_payload(creator_id: str, **overrides) -> dict:
    payload = {
        "creator_id": creator_id,
        "name": "Champions League Final",
        "statement": "Real Madrid wins in 90 minutes.",
        "deadline": iso(datetime.now(timezone.utc) + timedelta(days=7)),
        "options": ["Yes, they win", "No, draw or loss"],
    }
    payload.update(overrides)
    return payload


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
