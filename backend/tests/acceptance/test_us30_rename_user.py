"""US30: Rename my User. See docs/iterations/3/i03.d003-user-stories.md."""

import pytest

from tests.acceptance.steps import create_pool, leaderboard, seed_pick, sign_in


@pytest.mark.parametrize(
    ("submitted", "saved"),
    [("A", "A"), (" Ana ", "Ana"), ("  " + "n" * 80 + "  ", "n" * 80)],
    ids=["one-character", "saved-name", "eighty-characters"],
)
def test_names_of_1_to_80_characters_after_trimming_are_accepted(
    client, user_repo, submitted, saved
):
    # Given I am logged in with a saved name
    _, headers = sign_in(user_repo, name="Old name")

    # When I submit a name of 1 or 80 characters after trimming
    response = client.patch("/api/me", json={"name": submitted}, headers=headers)

    # Then the name is accepted and read back on the next request
    assert response.status_code == 200
    assert response.get_json()["name"] == saved
    assert client.get("/api/me", headers=headers).get_json()["name"] == saved


@pytest.mark.parametrize(
    ("name", "error"),
    [
        ("   ", "Field 'name' cannot be empty."),
        ("  " + "n" * 81 + "  ", "Field 'name' must be at most 80 characters."),
    ],
    ids=["whitespace", "eighty-one-characters"],
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


def test_rename_updates_every_display_and_keeps_my_participation(
    client, user_repo, pool_repo, pick_repo
):
    # Given I have a Pool, a Pick and a Record
    ana, headers = sign_in(user_repo, name="Ana")
    _, visitor_headers = sign_in(user_repo, name="Visitor")
    pool = create_pool(client, headers)
    bet = seed_pick(client, pool_repo, pick_repo, ana, pool, headers, winner=0)
    before = leaderboard(client, pool_repo, pool)

    # When I rename myself
    response = client.patch("/api/me", json={"name": "Ana Maria"}, headers=headers)

    # Then the same token and User remain, under the new name
    assert response.status_code == 200
    assert response.get_json() == {"id": ana.id, "name": "Ana Maria"}
    assert client.get("/api/me", headers=headers).get_json() == {
        "id": ana.id,
        "name": "Ana Maria",
    }

    # And the Pool list and page show the new name
    listed = client.get("/api/pools").get_json()[0]
    assert listed["creator"] == {"id": ana.id, "name": "Ana Maria"}
    detail = client.get(f"/api/pools/{pool['id']}").get_json()
    assert detail["creator"] == {"id": ana.id, "name": "Ana Maria"}
    assert detail["decider"]["name"] == "Ana Maria"

    # And another visitor sees my Pick and Record under the new name
    rows = leaderboard(client, pool_repo, pool)
    picks = client.get(
        f"/api/pools/{pool['id']}/picks", headers=visitor_headers
    ).get_json()["picks"]
    assert picks[0]["user"] == {"id": ana.id, "name": "Ana Maria"}
    assert rows[0]["user"] == {"id": ana.id, "name": "Ana Maria"}

    # And my ownership, Pick and win/loss totals are unchanged
    assert detail["bets"][0]["id"] == bet["id"]
    assert pick_repo.get(bet["id"], ana.id).outcome_id == bet["options"][0]["id"]
    after = leaderboard(client, pool_repo, pool)
    assert [(row["wins"], row["losses"]) for row in after] == [
        (row["wins"], row["losses"]) for row in before
    ] == [(1, 0)]


def test_only_the_logged_in_user_can_rename_themselves(client, user_repo):
    # Given Ana has a saved name and Bruno is a different signed-in User
    ana, _ = sign_in(user_repo, name="Ana")
    bruno, bruno_headers = sign_in(user_repo, name="Bruno")

    # When I try to rename without a token, or name Ana's id as Bruno
    signed_out = client.patch("/api/me", json={"name": "Mallory"})
    another_user = client.patch(
        "/api/me", json={"id": ana.id, "name": "Mallory"}, headers=bruno_headers
    )

    # Then both attempts are refused and both names are unchanged
    assert signed_out.status_code == 401
    assert signed_out.get_json() == {"error": "Authentication required."}
    assert another_user.status_code == 400
    assert another_user.get_json() == {
        "error": "Field 'id' is not accepted: you can only rename yourself."
    }
    assert user_repo.get(ana.id).name == "Ana"
    assert user_repo.get(bruno.id).name == "Bruno"
