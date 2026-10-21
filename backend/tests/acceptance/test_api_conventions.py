"""Rules every endpoint follows: health check for deployments, and errors always as JSON."""

from tests.acceptance.steps import create_user, pool_payload


def test_health_check_reports_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/nope")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}


def test_database_failure_returns_json_500_without_details(client, pool_repo):
    # Given the database fails while saving
    ana = create_user(client)

    def database_down(_new_pool):
        raise RuntimeError("connection refused")

    pool_repo.create_pool = database_down

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(ana["id"]))

    # Then I get a generic 500 error that does not leak internal details
    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error."}
