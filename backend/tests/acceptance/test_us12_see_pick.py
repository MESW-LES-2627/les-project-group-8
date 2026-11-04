"""US12: See my own pick."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from tests.acceptance.steps import create_pool, pick_payload, sign_in


def test_my_saved_pick_is_highlighted_when_i_open_the_pool(client, user_repo):
    # Given I have picked an outcome
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers, options=["A", "B", "C"])
    outcome = pool["options"][1]
    client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(outcome["id"]), headers=headers
    )

    # When I open the pool
    response = client.get(f"/api/pools/{pool['id']}/picks", headers=headers)

    # Then my outcome is available to be highlighted
    assert response.status_code == 200
    assert response.get_json()["pick"]["outcome_id"] == outcome["id"]


def test_open_pool_without_a_pick_offers_the_pick_action(client, user_repo):
    # Given the pool is open and I have not picked
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)

    # When I open the pool
    response = client.get(f"/api/pools/{pool['id']}/picks", headers=headers)

    # Then the pick action is offered
    assert pool["status"] == "OPEN"
    assert response.get_json() == {"pick": None}


def test_my_pick_is_still_visible_after_the_pool_is_locked(client, user_repo, pool_repo):
    # Given the pool is locked and I have picked
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers, options=["A", "B"])
    outcome = pool["options"][0]
    client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(outcome["id"]), headers=headers
    )
    pool_repo.pools[0] = replace(
        pool_repo.pools[0], deadline=datetime.now(timezone.utc) - timedelta(minutes=1)
    )

    # When I open the pool
    response = client.get(f"/api/pools/{pool['id']}/picks", headers=headers)

    # Then my pick is still visible
    assert response.status_code == 200
    assert response.get_json()["pick"]["outcome_id"] == outcome["id"]
    assert client.get(f"/api/pools/{pool['id']}").get_json()["status"] == "LOCKED"


def test_answers_to_different_pools_are_independent(client, user_repo, pick_repo):
    # Given a participant answering more than one question
    # (until #29 a pool holds a single question, so two pools stand in for two questions)
    ana, headers = sign_in(user_repo)
    first = create_pool(client, headers, name="First", options=["A", "B"])
    second = create_pool(client, headers, name="Second", options=["C", "D"])
    first_outcome = first["options"][0]
    second_outcome = second["options"][1]

    # When I answer both questions
    client.post(
        f"/api/pools/{first['id']}/picks",
        json=pick_payload(first_outcome["id"]),
        headers=headers,
    )
    client.post(
        f"/api/pools/{second['id']}/picks",
        json=pick_payload(second_outcome["id"]),
        headers=headers,
    )

    # Then each question keeps its own answer
    assert len(pick_repo.picks) == 2
    first_pick = client.get(f"/api/pools/{first['id']}/picks", headers=headers).get_json()
    second_pick = client.get(f"/api/pools/{second['id']}/picks", headers=headers).get_json()
    assert first_pick["pick"]["outcome_id"] == first_outcome["id"]
    assert second_pick["pick"]["outcome_id"] == second_outcome["id"]
    assert ana.id in {user_id for _, user_id in pick_repo.picks}


def test_my_pick_without_login_is_rejected(client, user_repo):
    # Given I am not logged in
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)

    # When I ask for my pick without a token
    response = client.get(f"/api/pools/{pool['id']}/picks")

    # Then I am told to log in
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}
