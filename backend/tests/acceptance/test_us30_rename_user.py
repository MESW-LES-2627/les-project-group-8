"""US30: Rename my User. See docs/iterations/3/i03.d003-user-stories.md."""

import pytest

from tests.acceptance.steps import (
    create_bet,
    create_pool,
    leaderboard,
    pick_payload,
    seed_pick,
    sign_in,
)


def test_a_logged_in_user_saves_their_name(client, user_repo):
    # Given I am logged in
    ana, headers = sign_in(user_repo, name="Old name")

    # When I save "Ana" as my name
    response = client.patch("/api/me", json={"name": "Ana"}, headers=headers)

    # Then the saved name is Ana
    assert response.status_code == 200
    assert response.get_json() == {"id": ana.id, "name": "Ana"}

    # And the next request (the page reload) reads it back
    assert client.get("/api/me", headers=headers).get_json() == {"id": ana.id, "name": "Ana"}


@pytest.mark.parametrize(
    ("submitted", "saved"),
    [
        ("A", "A"),
        ("  Ana  ", "Ana"),
        ("  " + "n" * 80 + "  ", "n" * 80),
    ],
    ids=["one-character", "trimmed", "eighty-characters"],
)
def test_names_of_1_to_80_characters_after_trimming_are_accepted(
    client, user_repo, submitted, saved
):
    # Given I am logged in with a saved name
    _, headers = sign_in(user_repo, name="Ana")

    # When I submit a name of 1 or 80 characters after trimming
    response = client.patch("/api/me", json={"name": submitted}, headers=headers)

    # Then the name is accepted
    assert response.status_code == 200
    assert response.get_json()["name"] == saved


@pytest.mark.parametrize(
    ("name", "error"),
    [
        ("   ", "Field 'name' cannot be empty."),
        (" \t\r\n ", "Field 'name' cannot be empty."),
        ("  " + "n" * 81 + "  ", "Field 'name' must be at most 80 characters."),
    ],
    ids=["spaces", "other-whitespace", "eighty-one-characters"],
)
def test_invalid_names_are_rejected_and_the_previous_name_remains(
    client, user_repo, name, error
):
    # Given I am logged in with a saved name
    ana, headers = sign_in(user_repo, name="Ana")

    # When I submit whitespace only or 81 characters after trimming
    response = client.patch("/api/me", json={"name": name}, headers=headers)

    # Then I see a validation error
    assert response.status_code == 400
    assert response.get_json() == {"error": error}

    # And my previous name remains unchanged after a reload
    assert client.get("/api/me", headers=headers).get_json()["name"] == "Ana"
    assert user_repo.get(ana.id).name == "Ana"


def test_every_existing_display_shows_the_new_name(client, user_repo, pool_repo, pick_repo):
    # Given I have created a Pool and have a visible Pick and Record
    ana, headers = sign_in(user_repo, name="Ana")
    _, visitor_headers = sign_in(user_repo, name="Visitor")
    pool = create_pool(client, headers)
    seed_pick(client, pool_repo, pick_repo, ana, pool, headers, winner=0)

    # When I rename myself
    response = client.patch("/api/me", json={"name": "Ana Maria"}, headers=headers)
    assert response.status_code == 200

    # Then the Pool list and the Pool page name me by my new name
    listed = client.get("/api/pools").get_json()[0]
    assert listed["creator"] == {"id": ana.id, "name": "Ana Maria"}
    assert listed["decider"] == {"id": ana.id, "name": "Ana Maria"}
    detail = client.get(f"/api/pools/{pool['id']}").get_json()
    assert detail["creator"] == {"id": ana.id, "name": "Ana Maria"}
    assert detail["decider"] == {"id": ana.id, "name": "Ana Maria"}

    # And another visitor reloading the Pool sees my Pick and Record under my new name
    rows = leaderboard(client, pool_repo, pool)
    picks = client.get(
        f"/api/pools/{pool['id']}/picks", headers=visitor_headers
    ).get_json()["picks"]
    assert picks[0]["user"] == {"id": ana.id, "name": "Ana Maria"}
    assert rows[0]["user"] == {"id": ana.id, "name": "Ana Maria"}


def test_rename_keeps_identity_ownership_picks_and_record(
    client, user_repo, pool_repo, pick_repo
):
    # Given I have a Pool, a Pick and a Record
    ana, headers = sign_in(user_repo, name="Ana")
    pool = create_pool(client, headers)
    bet = create_bet(client, pool["id"], headers)
    outcome = bet["options"][0]
    client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/picks",
        json=pick_payload(outcome["id"]),
        headers=headers,
    )
    pool_repo.resolve_bet(pool["id"], bet["id"], outcome["id"])
    before = leaderboard(client, pool_repo, pool)

    # When I rename myself
    response = client.patch("/api/me", json={"name": "Ana Maria"}, headers=headers)

    # Then my User identity and credentials still work
    assert response.status_code == 200
    assert response.get_json() == {"id": ana.id, "name": "Ana Maria"}
    assert client.get("/api/me", headers=headers).get_json() == {
        "id": ana.id,
        "name": "Ana Maria",
    }

    # And my ownership and Pick are unchanged
    pool_after = client.get(f"/api/pools/{pool['id']}").get_json()
    assert pool_after["creator"]["id"] == ana.id
    assert pool_after["decider"]["id"] == ana.id
    assert pool_after["bets"][0]["id"] == bet["id"]
    assert pick_repo.get(bet["id"], ana.id).outcome_id == outcome["id"]

    # And my win/loss totals are unchanged
    after = leaderboard(client, pool_repo, pool)
    assert [(row["wins"], row["losses"]) for row in after] == [
        (row["wins"], row["losses"]) for row in before
    ] == [(1, 0)]


def test_a_signed_out_visitor_cannot_rename_a_user(client, user_repo):
    # Given I am signed out and Ana has a saved name
    ana, _ = sign_in(user_repo, name="Ana")

    # When I attempt to change Ana's name without a token
    response = client.patch("/api/me", json={"name": "Mallory"})

    # Then I am told to log in and Ana's name is unchanged
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}
    assert user_repo.get(ana.id).name == "Ana"


def test_a_different_user_cannot_rename_another_user(client, user_repo):
    # Given I am signed in as Bruno and Ana has a saved name
    ana, _ = sign_in(user_repo, name="Ana")
    bruno, bruno_headers = sign_in(user_repo, name="Bruno")

    # When I try to change Ana's name, naming her id
    response = client.patch(
        "/api/me",
        json={"id": ana.id, "name": "Mallory"},
        headers=bruno_headers,
    )

    # Then the change is refused and Ana's name is unchanged
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'id' is not accepted: you can only rename yourself."
    }
    assert user_repo.get(ana.id).name == "Ana"
    assert user_repo.get(bruno.id).name == "Bruno"
