"""US27: Display multiple choice as a dropdown."""

import pytest

from tests.acceptance.steps import bet_payload, create_bet, create_pool, sign_in


@pytest.mark.parametrize("presentation", ["radio", "dropdown"])
def test_presentation_is_preserved_after_reload(
    client,
    user_repo,
    presentation,
):
    # Given a multiple-choice bet
    _, headers = sign_in(user_repo)
    options = ["Third", "First", "Second"]

    # When I choose radio or dropdown presentation and save
    pool = create_pool(
        client,
        headers,
    )
    bet = create_bet(
        client,
        pool["id"],
        headers,
        presentation=presentation,
        options=options,
    )

    # Then that presentation is preserved after reload
    assert bet["presentation"] == presentation
    reloaded = client.get(f"/api/pools/{pool['id']}").get_json()
    assert reloaded["bets"][0]["presentation"] == presentation
    assert [option["label"] for option in reloaded["bets"][0]["options"]] == options
    response = client.get(
        f"/api/pools/{pool['id']}/picks",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json() == {"picks": []}


def test_presentation_defaults_to_radio(
    client,
    user_repo,
):
    # Given a bet saved without a presentation choice
    _, headers = sign_in(user_repo)

    # When I save it
    pool = create_pool(
        client,
        headers,
    )
    bet = create_bet(
        client,
        pool["id"],
        headers,
    )

    # Then radio buttons are used
    assert bet["presentation"] == "radio"


def test_unknown_presentation_is_rejected(
    client,
    user_repo,
    pool_repo,
):
    # Given an unsupported presentation
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )

    # When I save the bet
    response = client.post(
        f"/api/pools/{pool['id']}/bets",
        json=bet_payload(presentation="checkboxes"),
        headers=headers,
    )

    # Then I get a 400 error and no bet is created
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'presentation' must be 'radio' or 'dropdown'."
    }
    assert pool_repo.get_pool(pool["id"]).bets == ()
