"""US3: See the pools. See docs/iterations/1/i01.d003-user-stories.md."""

import uuid
from datetime import datetime, timedelta, timezone

from pools.models import Pool, UserSummary
from tests.acceptance.steps import pool_payload, sign_in


def test_list_is_empty_when_there_are_no_pools(client):
    # Given no pools exist
    # When I list the pools
    response = client.get("/api/pools")

    # Then I get an empty list
    assert response.status_code == 200
    assert response.get_json() == []


def test_newest_pool_comes_first(client, user_repo):
    # Given two pools created one after the other
    _, headers = sign_in(user_repo)
    client.post("/api/pools", json=pool_payload(name="First"), headers=headers)
    client.post("/api/pools", json=pool_payload(name="Second"), headers=headers)

    # When I list the pools, without logging in
    response = client.get("/api/pools")

    # Then the newest one comes first
    assert [pool["name"] for pool in response.get_json()] == ["Second", "First"]


def test_pool_past_its_deadline_is_locked(client, pool_repo):
    # Given a pool whose deadline has passed and has no winner
    # (the API refuses past deadlines, so it is placed straight into the repository)
    now = datetime.now(timezone.utc)
    ana = UserSummary(id=str(uuid.uuid4()), name="Ana")
    pool_repo.pools.append(Pool(
        id=str(uuid.uuid4()), name="Yesterday's match", statement="Home team wins.",
        deadline=now - timedelta(hours=1), creator=ana, decider=ana,
        options=(), winning_outcome_id=None, created_at=now - timedelta(days=1),
    ))

    # When I list the pools
    response = client.get("/api/pools")

    # Then its status is LOCKED
    assert [pool["status"] for pool in response.get_json()] == ["LOCKED"]
