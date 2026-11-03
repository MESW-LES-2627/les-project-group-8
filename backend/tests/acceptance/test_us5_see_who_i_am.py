"""US5: See who I am. See docs/iterations/1/i01.d003-user-stories.md."""

import uuid

import pytest

from tests.acceptance.steps import (
    bearer,
    expired_token,
    forged_token,
    sign_in,
    token_for,
    wrong_audience_token,
)


def test_logged_in_user_gets_their_id_and_name(client, user_repo):
    # Given I am logged in as Ana
    ana, headers = sign_in(user_repo, name="Ana")

    # When I ask who I am
    response = client.get("/api/me", headers=headers)

    # Then I get my own id and name
    assert response.status_code == 200
    assert response.get_json() == {"id": ana.id, "name": "Ana"}


def test_request_without_token_is_rejected(client):
    # Given I am not logged in
    # When I ask who I am without a token
    response = client.get("/api/me")

    # Then I am told to log in
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}


@pytest.mark.parametrize("authorization", ["Bearer", "Bearer   ", "Basic YW5hOnB3", "Bearer not-a-jwt", "token"])
def test_malformed_authorization_header_is_rejected(client, authorization):
    # Given an Authorization header that does not carry a usable bearer token
    # When I ask who I am
    response = client.get("/api/me", headers={"Authorization": authorization})

    # Then I am told to log in
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}


@pytest.mark.parametrize("make_token", [expired_token, wrong_audience_token, forged_token])
def test_invalid_token_is_rejected(client, user_repo, make_token):
    # Given Ana exists but my token is expired, meant for another audience, or signed by another key
    ana, _ = sign_in(user_repo, name="Ana")

    # When I ask who I am with that token
    response = client.get("/api/me", headers=bearer(make_token(ana.id)))

    # Then I am told to log in
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}


def test_valid_token_without_a_user_is_forbidden(client):
    # Given a valid token for an Account that has no User
    headers = bearer(token_for(str(uuid.uuid4())))

    # When I ask who I am
    response = client.get("/api/me", headers=headers)

    # Then I am refused
    assert response.status_code == 403
