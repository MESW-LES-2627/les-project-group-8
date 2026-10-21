"""US3: See the pools. See docs/iterations/0/i00.d003-user-stories.md."""

import uuid
from datetime import datetime, timedelta, timezone

from pools.models import Pool, UserSummary
from tests.acceptance.steps import create_user, pool_payload


def test_ac3_1_list_is_empty_when_there_are_no_pools(client):
    # Given no pools exist
    # When I list the pools
    response = client.get("/api/pools")

    # Then I get an empty list
    assert response.status_code == 200
    assert response.get_json() == []


def test_ac3_2_newest_pool_comes_first(client):
    # Given two pools created one after the other
    ana = create_user(client)
    client.post("/api/pools", json=pool_payload(ana["id"], name="First"))
    client.post("/api/pools", json=pool_payload(ana["id"], name="Second"))

    # When I list the pools
    response = client.get("/api/pools")

    # Then the newest one comes first
    assert [pool["name"] for pool in response.get_json()] == ["Second", "First"]


def test_ac3_3_pool_past_its_deadline_is_locked(client, pool_repo):
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
