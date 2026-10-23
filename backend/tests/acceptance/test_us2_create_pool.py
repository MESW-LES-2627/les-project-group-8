"""US2: Create a two-option pool. See docs/iterations/0/i00.d003-user-stories.md."""

from datetime import datetime, timedelta, timezone

import pytest

from tests.acceptance.steps import create_user, iso, pool_payload


def test_pool_is_created_open_with_creator_as_decider(client, pool_repo):
    # Given an existing user and valid pool data
    ana = create_user(client, "Ana")
    payload = pool_payload(ana["id"])

    # When I create a pool
    response = client.post("/api/pools", json=payload)

    # Then the pool is saved as OPEN, with me as creator and decider, no winner, and my two outcomes
    assert response.status_code == 201
    pool = response.get_json()
    assert pool["name"] == payload["name"]
    assert pool["statement"] == payload["statement"]
    assert pool["status"] == "OPEN"
    assert pool["creator"] == ana
    assert pool["decider"] == ana
    assert pool["winning_outcome_id"] is None
    assert sorted(o["label"] for o in pool["options"]) == sorted(payload["options"])
    assert [p.id for p in pool_repo.pools] == [pool["id"]]


def test_deadline_is_returned_in_utc(client):
    # Given a deadline with a timezone offset
    ana = create_user(client)
    payload = pool_payload(ana["id"], deadline="2030-06-01T20:00:00+01:00")

    # When I create a pool
    response = client.post("/api/pools", json=payload)

    # Then the deadline is stored and returned in UTC
    assert response.status_code == 201
    assert response.get_json()["deadline"] == "2030-06-01T19:00:00Z"


@pytest.mark.parametrize("creator_id", [None, "", "not-a-uuid", "00000000-0000-0000-0000-000000000999"])
def test_unknown_creator_is_rejected(client, pool_repo, creator_id):
    # Given a creator_id that is not an existing user
    payload = pool_payload(creator_id)

    # When I create a pool
    response = client.post("/api/pools", json=payload)

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'creator_id' must be the id of an existing user."}
    assert pool_repo.pools == []


@pytest.mark.parametrize(
    "options",
    [None, [], ["Yes"], ["Yes", "No", "Maybe"], ["Yes", ""], ["Yes", "yes "]],
)
def test_pool_without_exactly_two_unique_outcomes_is_rejected(client, pool_repo, options):
    # Given fewer or more than two outcomes, an empty one, or two equal ones
    ana = create_user(client)

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(ana["id"], options=options))

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert response.get_json() == {"error": "A pool must have exactly 2 unique, non-empty outcomes."}
    assert pool_repo.pools == []


@pytest.mark.parametrize("days_from_now", [0, -1, -365])
def test_deadline_not_in_the_future_is_rejected(client, pool_repo, days_from_now):
    # Given a deadline that is not in the future
    ana = create_user(client)
    deadline = iso(datetime.now(timezone.utc) + timedelta(days=days_from_now))

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(ana["id"], deadline=deadline))

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'deadline' must be in the future."}
    assert pool_repo.pools == []


@pytest.mark.parametrize("deadline", ["tomorrow", "2030-13-01T00:00:00Z", 1234])
def test_malformed_deadline_is_rejected(client, pool_repo, deadline):
    # Given a deadline that is not a valid ISO-8601 timestamp
    ana = create_user(client)

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(ana["id"], deadline=deadline))

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
def test_empty_or_too_long_text_is_rejected(client, pool_repo, field, value, error):
    # Given an empty name or statement, or one that is too long
    ana = create_user(client)

    # When I create a pool
    response = client.post("/api/pools", json=pool_payload(ana["id"], **{field: value}))

    # Then I get a 400 error and no pool is created
    assert response.status_code == 400
    assert response.get_json() == {"error": error}
    assert pool_repo.pools == []


def test_body_that_is_not_json_is_rejected(client):
    # Given a request body that is not JSON
    # When I create a pool
    response = client.post("/api/pools", data="not json")

    # Then I get a 400 error
    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must be a JSON object."}
