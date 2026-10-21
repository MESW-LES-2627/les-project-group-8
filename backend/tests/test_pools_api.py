import pytest


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_pools_starts_empty(client):
    response = client.get("/api/pools")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_pool_returns_contract_shape(client, creator, valid_payload):
    response = client.post("/api/pools", json=valid_payload)

    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == valid_payload["name"]
    assert body["statement"] == valid_payload["statement"]
    assert body["status"] == "OPEN"
    assert body["winning_outcome_id"] is None
    assert body["creator"] == creator
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


@pytest.mark.parametrize("creator_id", [None, "", "not-a-uuid", "00000000-0000-0000-0000-000000000999"])
def test_create_pool_with_unknown_creator_is_400(client, repo, valid_payload, creator_id):
    response = client.post("/api/pools", json={**valid_payload, "creator_id": creator_id})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'creator_id' must be the id of an existing user."
    }
    assert repo.pools == []


def test_create_user_returns_id_and_trimmed_name(client, user_repo):
    response = client.post("/api/users", json={"name": "  Ana  "})

    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Ana"
    assert body["id"] in user_repo.users


@pytest.mark.parametrize(
    "payload, error",
    [
        ({}, "Field 'name' cannot be empty."),
        ({"name": "   "}, "Field 'name' cannot be empty."),
        ({"name": "x" * 81}, "Field 'name' must be at most 80 characters."),
    ],
)
def test_create_user_validation_error_is_400(client, user_repo, payload, error):
    response = client.post("/api/users", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": error}
    assert user_repo.users == {}


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
