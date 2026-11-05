"""US12: See my own pick."""

from tests.acceptance.steps import create_bet, create_pool, pick_payload, sign_in


def test_my_saved_pick_is_highlighted_when_i_open_the_pool(
    client,
    user_repo,
):
    # Given I have picked an outcome
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )
    bet = create_bet(
        client,
        pool["id"],
        headers,
        options=["A", "B", "C"],
    )
    outcome = bet["options"][1]
    client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/picks",
        json=pick_payload(outcome["id"]),
        headers=headers,
    )

    # When I open the pool
    response = client.get(
        f"/api/pools/{pool['id']}/picks",
        headers=headers,
    )

    # Then my outcome is available to be highlighted
    assert response.status_code == 200
    assert response.get_json()["picks"][0]["outcome_id"] == outcome["id"]


def test_open_pool_without_a_pick_offers_the_pick_action(
    client,
    user_repo,
):
    # Given the pool is open and I have not picked
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )
    bet = create_bet(
        client,
        pool["id"],
        headers,
    )

    # When I open the pool
    response = client.get(
        f"/api/pools/{pool['id']}/picks",
        headers=headers,
    )

    # Then the pick action is offered
    assert pool["status"] == "OPEN"
    assert response.get_json() == {"picks": []}


def test_bets_keep_independent_picks_and_pool_reads_exclude_other_pools(
    client,
    user_repo,
    pick_repo,
):
    # Given two Bets in one Pool and another Bet in a different Pool
    ana, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )
    other_pool = create_pool(
        client,
        headers,
        name="Other pool",
    )
    first = create_bet(
        client,
        pool["id"],
        headers,
        options=["A", "B"],
    )
    second = create_bet(
        client,
        pool["id"],
        headers,
        options=["C", "D"],
        presentation="dropdown",
    )
    other = create_bet(
        client,
        other_pool["id"],
        headers,
    )
    first_outcome = first["options"][0]
    second_outcome = second["options"][1]

    # When I pick on all three Bets, then change only the first Pick
    client.post(
        f"/api/pools/{pool['id']}/bets/{first['id']}/picks",
        json=pick_payload(first_outcome["id"]),
        headers=headers,
    )
    client.post(
        f"/api/pools/{pool['id']}/bets/{second['id']}/picks",
        json=pick_payload(second_outcome["id"]),
        headers=headers,
    )

    client.post(
        f"/api/pools/{other_pool['id']}/bets/{other['id']}/picks",
        json=pick_payload(other["options"][0]["id"]),
        headers=headers,
    )
    changed = client.post(
        f"/api/pools/{pool['id']}/bets/{first['id']}/picks",
        json=pick_payload(first["options"][1]["id"]),
        headers=headers,
    )

    # Then the Pool returns just its two independent Picks for this User
    assert changed.status_code == 201
    assert len(pick_repo.picks) == 3
    response = client.get(
        f"/api/pools/{pool['id']}/picks",
        headers=headers,
    )
    assert response.status_code == 200
    picks = response.get_json()["picks"]
    assert {pick["bet_id"]: pick["outcome_id"] for pick in picks} == {
        first["id"]: first["options"][1]["id"],
        second["id"]: second_outcome["id"],
    }
    assert {pick["user_id"] for pick in picks} == {ana.id}


def test_my_pick_without_login_is_rejected(
    client,
    user_repo,
):
    # Given I am not logged in
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )
    bet = create_bet(
        client,
        pool["id"],
        headers,
    )

    # When I ask for my pick without a token
    response = client.get(f"/api/pools/{pool['id']}/picks")

    # Then I am told to log in
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required."}
