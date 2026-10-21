from pools.service import GUEST_USER

GUEST_USER_ID = GUEST_USER.id


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
