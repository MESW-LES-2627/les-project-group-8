"""US2: Create a two-option pool. See docs/iterations/1/i01.d003-user-stories.md."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from tests.acceptance.steps import (
    bearer,
    expired_token,
    forged_token,
    iso,
    pool_payload,
    sign_in,
    token_for,
    wrong_audience_token,
)


def test_pool_is_created_open_with_creator_as_decider(client, user_repo, pool_repo):
    # Given I am logged in as Ana and have valid pool data
    ana, headers = sign_in(user_repo, name="Ana")
    payload = pool_payload()

    # When I create a pool
    response = client.post("/api/pools", json=payload, headers=headers)

    # Then the pool is saved as OPEN, with me as creator and decider, no winner, and my two outcomes
    assert response.status_code == 201
    pool = response.get_json()
    assert pool["name"] == payload["name"]
    assert pool["statement"] == payload["statement"]
    assert pool["status"] == "OPEN"
    assert pool["creator"] == {"id": ana.id, "name": "Ana"}
    assert pool["decider"] == {"id": ana.id, "name": "Ana"}
    assert pool["winning_outcome_id"] is None
    assert sorted(o["label"] for o in pool["options"]) == sorted(payload["options"])
    assert [p.id for p in pool_repo.pools] == [pool["id"]]


def test_each_user_owns_only_the_pool_they_created(client, user_repo):
    # Given Ana and Bruno are both logged in
    ana, ana_headers = sign_in(user_repo, name="Ana")
    bruno, bruno_headers = sign_in(user_repo, name="Bruno")

    # When each creates a pool
    client.post("/api/pools", json=pool_payload(name="Ana's pool"), headers=ana_headers)
    client.post("/api/pools", json=pool_payload(name="Bruno's pool"), headers=bruno_headers)

    # Then each pool has its own creator as creator and decider
    owners = {
        pool["name"]: (pool["creator"]["id"], pool["decider"]["id"])
        for pool in client.get("/api/pools").get_json()
    }
    assert owners == {"Ana's pool": (ana.id, ana.id), "Bruno's pool": (bruno.id, bruno.id)}


def test_pool_without_login_is_rejected(client, pool_repo):
    # Given I am not logged in
    # When I create a pool without a token
    response = client.post("/api/pools", json=pool_payload())

    # Then I am told to log in and no pool is created
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}
    assert pool_repo.pools == []


@pytest.mark.parametrize("make_token", [expired_token, wrong_audience_token, forged_token])
def test_pool_with_invalid_token_is_rejected(client, user_repo, pool_repo, make_token):
    # Given Ana exists but my token is expired, meant for another audience, or signed by another key
    ana, _ = sign_in(user_repo, name="Ana")

    # When I create a pool with that token
    response = client.post("/api/pools", json=pool_payload(), headers=bearer(make_token(ana.id)))

    # Then I am told to log in and no pool is created
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}
    assert pool_repo.pools == []


def test_pool_for_an_account_without_a_user_is_forbidden(client, pool_repo):
    # Given a valid token for an Account that has no User
    headers = bearer(token_for(str(uuid.uuid4())))

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(), headers=headers)

    # Then I am refused and no pool is created
    assert response.status_code == 403
    assert response.get_json() == {"error": "No user exists for this account."}
    assert pool_repo.pools == []


@pytest.mark.parametrize("creator_id", ["mine", "someone-else", None])
def test_pool_naming_its_creator_is_rejected(client, user_repo, pool_repo, creator_id):
    # Given I am logged in as Ana and my request still says who the creator is
    # (my own id, another User's id, or null)
    ana, headers = sign_in(user_repo, name="Ana")
    bruno, _ = sign_in(user_repo, name="Bruno")
    creator_id = {"mine": ana.id, "someone-else": bruno.id}.get(creator_id)

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(creator_id=creator_id), headers=headers)

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'creator_id' is not accepted: the creator is the logged-in user."
    }
    assert pool_repo.pools == []


def test_deadline_is_returned_in_utc(client, user_repo):
    # Given a deadline with a timezone offset
    _, headers = sign_in(user_repo)
    payload = pool_payload(deadline="2030-06-01T20:00:00+01:00")

    # When I create a pool
    response = client.post("/api/pools", json=payload, headers=headers)

    # Then the deadline is stored and returned in UTC
    assert response.status_code == 201
    assert response.get_json()["deadline"] == "2030-06-01T19:00:00Z"


@pytest.mark.parametrize(
    "options",
    [None, [], ["Yes"], ["Yes", "No", "Maybe"], ["Yes", ""], ["Yes", "yes "]],
)
def test_pool_without_exactly_two_unique_outcomes_is_rejected(client, user_repo, pool_repo, options):
    # Given fewer or more than two outcomes, an empty one, or two equal ones
    _, headers = sign_in(user_repo)

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(options=options), headers=headers)

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert response.get_json() == {"error": "A pool must have exactly 2 unique, non-empty outcomes."}
    assert pool_repo.pools == []


@pytest.mark.parametrize("days_from_now", [0, -1, -365])
def test_deadline_not_in_the_future_is_rejected(client, user_repo, pool_repo, days_from_now):
    # Given a deadline that is not in the future
    _, headers = sign_in(user_repo)
    deadline = iso(datetime.now(timezone.utc) + timedelta(days=days_from_now))

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(deadline=deadline), headers=headers)

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'deadline' must be in the future."}
    assert pool_repo.pools == []


@pytest.mark.parametrize("deadline", ["tomorrow", "2030-13-01T00:00:00Z", 1234])
def test_malformed_deadline_is_rejected(client, user_repo, pool_repo, deadline):
    # Given a deadline that is not a valid ISO-8601 timestamp
    _, headers = sign_in(user_repo)

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(deadline=deadline), headers=headers)

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert "ISO-8601" in response.get_json()["error"]
    assert pool_repo.pools == []


@pytest.mark.parametrize(
    "field, value, error",
    [
        ("name", "", "Field 'name' cannot be empty."),
        ("name", "   ", "Field 'name' cannot be empty."),
        ("name", "x" * 121, "Field 'name' must be at most 120 characters."),
        ("statement", None, "Field 'statement' cannot be empty."),
        ("statement", "x" * 501, "Field 'statement' must be at most 500 characters."),
    ],
    ids=["empty-name", "blank-name", "long-name", "missing-statement", "long-statement"],
)
def test_empty_or_too_long_text_is_rejected(client, user_repo, pool_repo, field, value, error):
    # Given an empty name or statement, or one that is too long
    _, headers = sign_in(user_repo)

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(**{field: value}), headers=headers)

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert response.get_json() == {"error": error}
    assert pool_repo.pools == []


def test_body_that_is_not_json_is_rejected(client, user_repo):
    # Given I am logged in and send a request body that is not JSON
    _, headers = sign_in(user_repo)

    # When I create a pool
    response = client.post("/api/pools", data="not json", headers=headers)

    # Then I get a 400 error
    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must be a JSON object."}
