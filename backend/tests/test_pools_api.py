from datetime import datetime, timedelta, timezone

import pytest

from app import format_pool
from pool_api.domain import GUEST_USER_ID


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_pools_starts_empty(client):
    response = client.get("/api/pools")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_pool_returns_contract_shape(client, valid_payload):
    response = client.post("/api/pools", json=valid_payload)

    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == valid_payload["name"]
    assert body["statement"] == valid_payload["statement"]
    assert body["status"] == "OPEN"
    assert body["winning_outcome_id"] is None
    assert body["creator"] == {"id": GUEST_USER_ID, "name": "Guest User"}
    assert body["decider"] == body["creator"]
    assert [o["label"] for o in body["options"]] == valid_payload["options"]
    assert body["deadline"].endswith("Z")


def test_created_pool_is_listed_newest_first(client, valid_payload):
    client.post("/api/pools", json={**valid_payload, "name": "First"})
    client.post("/api/pools", json={**valid_payload, "name": "Second"})

    names = [p["name"] for p in client.get("/api/pools").get_json()]
    assert names == ["Second", "First"]


def test_create_pool_validation_error_is_400(client, repo, valid_payload):
    response = client.post("/api/pools", json={**valid_payload, "options": ["Only one"]})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "A pool must have exactly 2 unique, non-empty outcomes."
    }
    assert repo.pools == []


def test_create_pool_without_json_body_is_400(client):
    response = client.post("/api/pools", data="not json")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/nope")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_repository_failure_returns_json_500(client, repo, valid_payload):
    def boom(_):
        raise RuntimeError("db down")

    repo.create_pool = boom
    response = client.post("/api/pools", json=valid_payload)

    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error."}


@pytest.mark.parametrize(
    "overrides",
    [
        {"options": ["a" * 101, "No"]},
        {"deadline": "2099-01-01"},
        {"deadline": "2099-01-01T12:00:00"},
        {"options": ["Straße", " STRASSE "]},
    ],
)
def test_invalid_contract_data_is_rejected_before_storage(client, repo, valid_payload, overrides):
    response = client.post("/api/pools", json={**valid_payload, **overrides})
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert repo.pools == []


def test_create_pool_normalises_input_and_uses_guest(client, valid_payload):
    response = client.post(
        "/api/pools",
        json={
            **valid_payload,
            "name": "  Final  ",
            "options": [" Yes ", "No"],
            "deadline": "2099-01-01T15:00:00-05:00",
            "creator_id": "another-user",
            "decider_id": "another-decider",
        },
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Final"
    assert body["deadline"] == "2099-01-01T20:00:00Z"
    assert [option["label"] for option in body["options"]] == ["Yes", "No"]
    assert body["creator"]["id"] == body["decider"]["id"] == GUEST_USER_ID


def test_list_recomputes_status_when_deadline_has_passed(client, repo, valid_payload):
    client.post("/api/pools", json=valid_payload)
    repo.pools[0]["deadline"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()

    response = client.get("/api/pools")
    assert response.get_json()[0]["status"] == "LOCKED"


def test_database_pool_with_negative_offset_is_formatted_as_utc():
    now = datetime(2026, 10, 21, 20, tzinfo=timezone.utc)
    pool = format_pool(
        {
            "id": "p1",
            "name": "Final",
            "statement": "Home team wins.",
            "deadline": "2026-10-21T15:00:00-05:00",
        },
        now=now,
    )
    assert pool["deadline"] == "2026-10-21T20:00:00Z"
    assert pool["status"] == "LOCKED"
