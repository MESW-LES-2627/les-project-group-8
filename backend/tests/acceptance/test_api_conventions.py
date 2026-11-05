"""Rules every endpoint follows: health check for deployments, and errors always as JSON."""

import uuid

from tests.acceptance.steps import pool_payload, sign_in


def test_health_check_reports_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/nope")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}


def test_unknown_pool_returns_json_404(client):
    response = client.get(f"/api/pools/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Pool not found."}


def test_users_cannot_be_created_through_the_api(client, user_repo):
    # Given Users only come from Accounts (a database trigger creates them at sign-up)
    # When I try to create a User directly
    response = client.post("/api/users", json={"name": "Ana"})

    # Then the endpoint does not exist and no User is created
    assert response.status_code == 404
    assert user_repo.users == {}


def test_database_failure_returns_json_500_without_details(client, user_repo, pool_repo):
    # Given I am logged in and the database fails while saving
    _, headers = sign_in(user_repo)

    def database_down(_new_pool):
        raise RuntimeError("connection refused")

    pool_repo.create_pool = database_down

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(), headers=headers)

    # Then I get a generic 500 error that does not leak internal details
    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error."}
