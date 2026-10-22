"""US1: Create a user. See docs/iterations/0/i00.d003-user-stories.md."""

import pytest


def test_user_is_created_with_id_and_trimmed_name(client, user_repo):
    # Given a name with surrounding spaces
    payload = {"name": "  Ana  "}

    # When I create a user
    response = client.post("/api/users", json=payload)

    # Then the user is created with a new id and the trimmed name
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Ana"
    assert body["id"] in user_repo.users


@pytest.mark.parametrize("payload", [{}, {"name": ""}, {"name": "   "}, {"name": 42}])
def test_empty_name_is_rejected(client, user_repo, payload):
    # Given an empty or blank name
    # When I create a user
    response = client.post("/api/users", json=payload)

    # Then I get a 400 error and no user is created
    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'name' cannot be empty."}
    assert user_repo.users == {}


def test_name_longer_than_80_characters_is_rejected(client, user_repo):
    # Given a name longer than 80 characters
    payload = {"name": "x" * 81}

    # When I create a user
    response = client.post("/api/users", json=payload)

    # Then I get a 400 error and no user is created
    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'name' must be at most 80 characters."}
    assert user_repo.users == {}
