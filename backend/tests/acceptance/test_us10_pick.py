"""US10: Pick an outcome. Also covers the deadline and identity rules the pick flow relies on."""

import uuid
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tests.acceptance.steps import (
    bearer,
    create_pool,
    expired_token,
    forged_token,
    pick_payload,
    sign_in,
    token_for,
    wrong_audience_token,
)


def test_pick_is_saved_with_pool_user_outcome_and_time(client, user_repo, pick_repo):
    # Given an open pool, an existing user and one of its outcomes
    ana, headers = sign_in(user_repo, name="Ana")
    pool = create_pool(client, headers, options=["A", "B", "C"])
    outcome = pool["options"][1]
    before = datetime.now(timezone.utc)

    # When I pick that outcome
    response = client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(outcome["id"]), headers=headers
    )
    after = datetime.now(timezone.utc)

    # Then the pick is saved with the pool, user, outcome and time
    assert response.status_code == 201
    pick = response.get_json()
    assert pick["pool_id"] == pool["id"]
    assert pick["user_id"] == ana.id
    assert pick["outcome_id"] == outcome["id"]
    created = datetime.fromisoformat(pick["created_at"].replace("Z", "+00:00"))
    assert before <= created <= after
    assert pick_repo.get(pool["id"], ana.id).outcome_id == outcome["id"]


def test_pick_is_restored_after_reload(client, user_repo):
    # Given I have just picked
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers, options=["A", "B"])
    outcome = pool["options"][0]
    client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(outcome["id"]), headers=headers
    )

    # When the pool reloads
    response = client.get(f"/api/pools/{pool['id']}/picks", headers=headers)

    # Then my pick is shown
    assert response.status_code == 200
    assert response.get_json()["pick"]["outcome_id"] == outcome["id"]


def test_pick_without_login_is_rejected(client, user_repo, pick_repo):
    # Given I am not logged in
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)

    # When I try to pick an outcome without a token
    response = client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(pool["options"][0]["id"])
    )

    # Then I am told to log in and no pick is created
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}
    assert pick_repo.picks == {}


def test_pick_for_an_account_without_a_user_is_forbidden(client, pick_repo):
    # Given a valid token for an Account that has no User
    headers = bearer(token_for(str(uuid.uuid4())))

    # When I try to pick an outcome
    response = client.post(
        f"/api/pools/{uuid.uuid4()}/picks",
        json=pick_payload(str(uuid.uuid4())),
        headers=headers,
    )

    # Then I am refused and no pick is created
    assert response.status_code == 403
    assert response.get_json() == {"error": "No user exists for this account."}
    assert pick_repo.picks == {}


def test_pick_naming_its_user_is_rejected(client, user_repo, pick_repo):
    # Given I am logged in as Ana and my request still says who the participant is
    ana, headers = sign_in(user_repo, name="Ana")
    pool = create_pool(client, headers)

    # When I send my own id in the body
    response = client.post(
        f"/api/pools/{pool['id']}/picks",
        json={**pick_payload(pool["options"][0]["id"]), "user_id": ana.id},
        headers=headers,
    )

    # Then I get a 400 error and no pick is created
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'user_id' is not accepted: the participant is the logged-in user."
    }
    assert pick_repo.picks == {}


def test_unknown_pool_is_rejected(client, user_repo, pick_repo):
    # Given an unknown pool
    _, headers = sign_in(user_repo)

    # When I pick an outcome
    response = client.post(
        f"/api/pools/{uuid.uuid4()}/picks",
        json=pick_payload(str(uuid.uuid4())),
        headers=headers,
    )

    # Then I get a 400 error and no pick is created
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'pool_id' must be the id of an existing pool."
    }
    assert pick_repo.picks == {}


def test_unknown_outcome_is_rejected(client, user_repo, pick_repo):
    # Given an unknown outcome id
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)

    # When I pick it
    response = client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(str(uuid.uuid4())),
        headers=headers,
    )

    # Then I get a 400 error and no pick is created
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'outcome_id' must be one of the pool's options."
    }
    assert pick_repo.picks == {}


def test_outcome_from_another_pool_is_rejected(client, user_repo, pick_repo):
    # Given an outcome id that belongs to a different pool
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers, name="First")
    other_pool = create_pool(client, headers, name="Second")

    # When I pick it in this pool
    response = client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(other_pool["options"][0]["id"]),
        headers=headers,
    )

    # Then I get a 400 error and no pick is created
    assert response.status_code == 400
    assert pick_repo.picks == {}


def test_pick_is_replaced_not_duplicated(client, user_repo, pick_repo):
    # Given I have already picked one outcome
    ana, headers = sign_in(user_repo)
    pool = create_pool(client, headers, options=["A", "B", "C"])
    first, second, _ = pool["options"]
    client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(first["id"]), headers=headers
    )

    # When I pick another outcome before the deadline
    response = client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(second["id"]), headers=headers
    )

    # Then my pick is replaced, not duplicated
    assert response.status_code == 201
    assert len(pick_repo.picks) == 1
    assert pick_repo.get(pool["id"], ana.id).outcome_id == second["id"]


def test_pick_after_the_deadline_is_rejected(client, user_repo, pool_repo, pick_repo):
    # Given the deadline has passed
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    pool_repo.pools[0] = replace(
        pool_repo.pools[0], deadline=datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    # When I try to pick an outcome
    response = client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(pool["options"][0]["id"]),
        headers=headers,
    )

    # Then I get a 400 error and no pick is created
    assert response.status_code == 400
    assert response.get_json() == {"error": "Picks are closed for this pool."}
    assert pick_repo.picks == {}


def test_existing_pick_is_unchanged_after_the_deadline(client, user_repo, pool_repo, pick_repo):
    # Given the deadline has passed and I already picked
    ana, headers = sign_in(user_repo)
    pool = create_pool(client, headers, options=["A", "B"])
    first, second = pool["options"]
    client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(first["id"]), headers=headers
    )
    pool_repo.pools[0] = replace(
        pool_repo.pools[0], deadline=datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    # When I try to change my pick
    response = client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(second["id"]), headers=headers
    )

    # Then I get a 400 error and my pick is unchanged
    assert response.status_code == 400
    assert pick_repo.get(pool["id"], ana.id).outcome_id == first["id"]


def test_pick_at_the_exact_deadline_is_refused(client, user_repo, pool_repo, pick_repo):
    # Given the deadline is exactly now
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    pool_repo.pools[0] = replace(pool_repo.pools[0], deadline=datetime.now(timezone.utc))

    # When I try to pick an outcome
    response = client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(pool["options"][0]["id"]),
        headers=headers,
    )

    # Then the pick is refused
    assert response.status_code == 400
    assert pick_repo.picks == {}


def test_two_participants_keep_their_own_picks(client, user_repo, pick_repo):
    # Given Ana and Bruno are both logged in and the same pool is open
    ana, ana_headers = sign_in(user_repo, name="Ana")
    bruno, bruno_headers = sign_in(user_repo, name="Bruno")
    pool = create_pool(client, ana_headers, options=["A", "B"])
    first, second = pool["options"]

    # When each picks a different outcome
    client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(first["id"]),
        headers=ana_headers,
    )
    client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(second["id"]),
        headers=bruno_headers,
    )

    # Then each sees their own pick
    ana_pick = client.get(f"/api/pools/{pool['id']}/picks", headers=ana_headers).get_json()
    bruno_pick = client.get(f"/api/pools/{pool['id']}/picks", headers=bruno_headers).get_json()
    assert ana_pick["pick"]["outcome_id"] == first["id"]
    assert bruno_pick["pick"]["outcome_id"] == second["id"]
    assert len(pick_repo.picks) == 2


@pytest.mark.parametrize("make_token", ["expired", "wrong-audience", "forged"])
def test_pick_with_invalid_token_is_rejected(client, user_repo, pick_repo, make_token):
    # Given Ana exists but my token is expired, meant for another audience, or signed by another key
    ana, headers = sign_in(user_repo, name="Ana")
    pool = create_pool(client, headers)
    make = {
        "expired": expired_token,
        "wrong-audience": wrong_audience_token,
        "forged": forged_token,
    }[make_token]

    # When I try to pick with that token
    response = client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(pool["options"][0]["id"]),
        headers=bearer(make(ana.id)),
    )

    # Then I am told to log in and no pick is created
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}
    assert pick_repo.picks == {}
