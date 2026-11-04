"""US26: Create a multiple-choice question with n options."""

import pytest

from tests.acceptance.steps import create_pool, pick_payload, pool_payload, sign_in


def test_binary_question_is_stored_and_displayed_in_authored_order(client, user_repo):
    # Given a question with two distinct non-empty options
    _, headers = sign_in(user_repo)

    # When I save it
    pool = create_pool(client, headers, options=["Yes", "No"])

    # Then the binary question is stored and displayed correctly
    assert [option["label"] for option in pool["options"]] == ["Yes", "No"]
    reloaded = client.get(f"/api/pools/{pool['id']}").get_json()
    assert [option["label"] for option in reloaded["options"]] == ["Yes", "No"]


def test_more_than_two_options_keep_the_authored_order(client, user_repo):
    # Given a question with more than two distinct non-empty options
    _, headers = sign_in(user_repo)
    options = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]

    # When I save it
    pool = create_pool(client, headers, options=options)

    # Then all its options are stored and displayed in the authored order
    assert [option["label"] for option in pool["options"]] == options
    listed = client.get("/api/pools").get_json()[0]
    assert [option["label"] for option in listed["options"]] == options


@pytest.mark.parametrize(
    "options",
    [
        None,
        [],
        ["Only one"],
        ["Yes", ""],
        ["Yes", "   "],
        ["Yes", "yes"],
        ["x" * 101, "No"],
        [f"Option {index}" for index in range(11)],
    ],
    ids=[
        "missing",
        "empty-list",
        "one-option",
        "blank-label",
        "whitespace-label",
        "duplicate-label",
        "label-too-long",
        "more-than-ten",
    ],
)
def test_invalid_option_lists_are_rejected_without_partial_data(
    client, user_repo, pool_repo, options
):
    # Given fewer than two options, blank labels, duplicate labels, or too many options
    _, headers = sign_in(user_repo)

    # When I save the question
    response = client.post("/api/pools", json=pool_payload(options=options), headers=headers)

    # Then validation rejects it without partial data
    assert response.status_code == 400
    assert pool_repo.pools == []


def test_a_pick_saves_exactly_one_option_of_the_question(client, user_repo, pick_repo):
    # Given an open multiple-choice question
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers, options=["A", "B", "C"])
    option_id = pool["options"][2]["id"]

    # When I submit a prediction
    response = client.post(
        f"/api/pools/{pool['id']}/picks", json=pick_payload(option_id), headers=headers
    )

    # Then exactly one option belonging to that question is saved as my answer
    assert response.status_code == 201
    assert response.get_json()["outcome_id"] == option_id
    assert len(pick_repo.picks) == 1
