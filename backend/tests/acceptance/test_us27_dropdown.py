"""US27: Display multiple choice as a dropdown."""

import pytest

from tests.acceptance.steps import create_pool, pick_payload, pool_payload, sign_in


@pytest.mark.parametrize("presentation", ["radio", "dropdown"])
def test_presentation_is_preserved_after_reload(client, user_repo, presentation):
    # Given a multiple-choice question
    _, headers = sign_in(user_repo)

    # When I choose radio or dropdown presentation and save
    pool = create_pool(client, headers, presentation=presentation)

    # Then that presentation is preserved after reload
    assert pool["presentation"] == presentation
    reloaded = client.get(f"/api/pools/{pool['id']}").get_json()
    assert reloaded["presentation"] == presentation


def test_presentation_defaults_to_radio(client, user_repo):
    # Given a question saved without a presentation choice
    _, headers = sign_in(user_repo)

    # When I save it
    pool = create_pool(client, headers)

    # Then radio buttons are used
    assert pool["presentation"] == "radio"


def test_unknown_presentation_is_rejected(client, user_repo, pool_repo):
    # Given an unsupported presentation
    _, headers = sign_in(user_repo)

    # When I save the question
    response = client.post(
        "/api/pools", json=pool_payload(presentation="checkboxes"), headers=headers
    )

    # Then I get a 400 error and no question is created
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'presentation' must be 'radio' or 'dropdown'."
    }
    assert pool_repo.pools == []


def test_dropdown_question_shows_ordered_options_and_no_answer_by_default(client, user_repo):
    # Given a question configured as a dropdown
    _, headers = sign_in(user_repo)
    options = ["First", "Second", "Third"]

    # When a participant opens it
    pool = create_pool(client, headers, presentation="dropdown", options=options)

    # Then the same ordered options appear and no answer is assumed
    assert pool["presentation"] == "dropdown"
    assert [option["label"] for option in pool["options"]] == options
    response = client.get(f"/api/pools/{pool['id']}/picks", headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"pick": None}


@pytest.mark.parametrize("presentation", ["radio", "dropdown"])
@pytest.mark.parametrize(
    "options", [["A", "B"], ["A", "B", "C", "D", "E"]], ids=["binary", "five-options"]
)
def test_single_choice_rules_apply_to_both_presentations(
    client, user_repo, pick_repo, presentation, options
):
    # Given either presentation, with two or more than two options
    ana, headers = sign_in(user_repo)
    pool = create_pool(client, headers, presentation=presentation, options=options)
    first_option = pool["options"][0]
    last_option = pool["options"][-1]

    # When a participant submits an answer
    response = client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(first_option["id"]),
        headers=headers,
    )

    # Then the same single-choice, identity and deadline rules apply
    assert response.status_code == 201
    replaced = client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(last_option["id"]),
        headers=headers,
    )
    assert replaced.status_code == 201
    assert len(pick_repo.picks) == 1

    other_pool = create_pool(client, headers, name="Another question", options=["X", "Y"])
    unrelated = client.post(
        f"/api/pools/{pool['id']}/picks",
        json=pick_payload(other_pool["options"][0]["id"]),
        headers=headers,
    )
    assert unrelated.status_code == 400
    assert pick_repo.get(pool["id"], ana.id).outcome_id == last_option["id"]
