"""US26: Create a multiple-choice bet with n options."""

import pytest

from tests.acceptance.steps import bet_payload, create_bet, create_pool, sign_in


@pytest.mark.parametrize("count", [2, 10])
def test_options_keep_the_authored_order(
    client,
    user_repo,
    count,
):
    # Given a Bet at either supported option-count boundary
    _, headers = sign_in(user_repo)
    options = [f"Option {index}" for index in reversed(range(count))]

    # When I save it
    pool = create_pool(
        client,
        headers,
    )
    bet = create_bet(
        client,
        pool["id"],
        headers,
        options=options,
    )

    # Then all its options are stored and displayed in the authored order
    assert [option["label"] for option in bet["options"]] == options
    listed = client.get("/api/pools").get_json()[0]
    assert [option["label"] for option in listed["bets"][0]["options"]] == options
    reloaded = client.get(f"/api/pools/{pool['id']}").get_json()
    assert [option["label"] for option in reloaded["bets"][0]["options"]] == options


@pytest.mark.parametrize(
    "options",
    [
        None,
        [],
        ["Only one"],
        ["Yes", ""],
        ["Yes", "   "],
        ["Yes", "yes"],
        [" Yes ", "yes"],
        [123, "No"],
        "Yes, No",
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
        "duplicate-after-trimming",
        "non-string-label",
        "not-a-list",
        "label-too-long",
        "more-than-ten",
    ],
)
def test_invalid_option_lists_are_rejected_without_partial_data(
    client,
    user_repo,
    pool_repo,
    options,
):
    # Given fewer than two options, blank labels, duplicate labels, or too many options
    _, headers = sign_in(user_repo)
    pool = create_pool(
        client,
        headers,
    )

    # When I save the bet
    response = client.post(
        f"/api/pools/{pool['id']}/bets",
        json=bet_payload(options=options),
        headers=headers,
    )

    # Then validation rejects it without partial data
    assert response.status_code == 400
    assert len(pool_repo.pools) == 1
    assert pool_repo.get_pool(pool["id"]).bets == ()
