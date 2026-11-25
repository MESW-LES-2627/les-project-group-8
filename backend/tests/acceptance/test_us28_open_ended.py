"""US28: Create and answer an open-ended Bet."""

from datetime import datetime, timedelta

import pytest

from picks.models import TextAnswer
from tests.acceptance.steps import bearer, create_pool, sign_in, token_for


def text_bet(client, pool_id, headers, statement="Who scores first?"):
    response = client.post(
        f"/api/pools/{pool_id}/bets",
        json={"statement": statement, "answer_type": "text"},
        headers=headers,
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def answer(client, pool, bet, headers, text):
    return client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/picks",
        json={"answer_text": text},
        headers=headers,
    )


def picks(client, pool, headers):
    response = client.get(f"/api/pools/{pool['id']}/picks", headers=headers)
    assert response.status_code == 200
    return response.get_json()["picks"]


def freeze_clock(monkeypatch, pool_repo, offset):
    """Move the clock to the Pool's deadline plus `offset` microseconds."""
    deadline = pool_repo.pools[0].deadline

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return deadline + timedelta(microseconds=offset)

    monkeypatch.setattr("pools.models.datetime", Clock)


def test_creator_adds_a_text_bet_without_options(client, user_repo):
    # 28.1 Given I am the creator of an open Pool
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)

    # When I add a valid open-ended prompt without options
    bet = text_bet(client, pool["id"], headers)

    # Then it is saved, remains after reload and offers a text answer, not an option list
    assert bet["answer_type"] == "text"
    assert bet["options"] == []
    reloaded = client.get(f"/api/pools/{pool['id']}").get_json()["bets"]
    assert [(item["id"], item["answer_type"], item["options"]) for item in reloaded] == [
        (bet["id"], "text", [])
    ]


@pytest.mark.parametrize(
    "extra",
    [{"options": ["A", "B"]}, {"options": []}, {"presentation": "radio"}],
    ids=["options", "empty-options", "presentation"],
)
def test_text_bet_with_choice_fields_is_rejected(client, user_repo, pool_repo, extra):
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)

    response = client.post(
        f"/api/pools/{pool['id']}/bets",
        json={"statement": "Who scores first?", "answer_type": "text", **extra},
        headers=headers,
    )

    assert response.status_code == 400
    assert pool_repo.pools[0].bets == ()


def test_unknown_answer_type_is_rejected(client, user_repo, pool_repo):
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)

    response = client.post(
        f"/api/pools/{pool['id']}/bets",
        json={"statement": "How many goals?", "answer_type": "number"},
        headers=headers,
    )

    assert response.status_code == 400
    assert pool_repo.pools[0].bets == ()


def test_non_creator_cannot_add_a_text_bet(client, user_repo, pool_repo):
    # 28.2 Given an open Pool exists
    _, ana_headers = sign_in(user_repo, name="Ana")
    _, bruno_headers = sign_in(user_repo, name="Bruno")
    pool = create_pool(client, ana_headers)

    # When a non-creator attempts to add an open-ended prompt
    response = client.post(
        f"/api/pools/{pool['id']}/bets",
        json={"statement": "Who scores first?", "answer_type": "text"},
        headers=bruno_headers,
    )

    # Then creation is refused and no Bet is added
    assert response.status_code == 403
    assert pool_repo.pools[0].bets == ()


def test_text_answer_is_saved_and_shown_after_reload(client, user_repo, pick_repo):
    # 28.3 Given I am signed in and an open-ended Bet is open
    ana, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = text_bet(client, pool["id"], headers)

    # When I submit `Ana`
    response = answer(client, pool, bet, headers, "Ana")

    # Then my saved answer is `Ana` and I can see it after reload
    assert response.status_code == 201
    assert response.get_json()["answer_text"] == "Ana"
    assert response.get_json()["outcome_id"] is None
    assert pick_repo.get(bet["id"], ana.id).answer == TextAnswer("Ana")
    assert [(pick["bet_id"], pick["answer_text"]) for pick in picks(client, pool, headers)] == [
        (bet["id"], "Ana")
    ]


@pytest.mark.parametrize(
    "submitted, stored",
    [
        ("A", "A"),
        ("  A  ", "A"),
        ("é" * 500, "é" * 500),
        ("😀" * 500, "😀" * 500),
        (" " + "x" * 500 + "\n", "x" * 500),
        ("<b>Ana</b> & co", "<b>Ana</b> & co"),
    ],
    ids=["one", "one-trimmed", "500-accented", "500-emoji", "500-after-trimming", "markup"],
)
def test_answers_of_1_and_500_code_points_are_kept_as_plain_text(
    client, user_repo, pick_repo, submitted, stored,
):
    # 28.4 Given an open-ended Bet is open
    ana, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = text_bet(client, pool["id"], headers)

    # When I submit an answer of 1 or 500 code points after trimming
    response = answer(client, pool, bet, headers, submitted)

    # Then it is accepted and preserved as plain text
    assert response.status_code == 201
    assert response.get_json()["answer_text"] == stored
    assert pick_repo.get(bet["id"], ana.id).answer == TextAnswer(stored)


@pytest.mark.parametrize(
    "payload",
    [
        {"answer_text": ""},
        {"answer_text": "   \t\n "},
        {"answer_text": "x" * 501},
        {"answer_text": "😀" * 501},
        {"answer_text": 42},
        {"answer_text": None},
        {},
        {"outcome_id": "anything"},
        {"answer_text": "Bruno", "outcome_id": "anything"},
    ],
    ids=[
        "empty", "whitespace", "501", "501-emoji", "number", "null",
        "missing", "choice-field", "both-fields",
    ],
)
def test_invalid_answer_keeps_the_saved_one(client, user_repo, pick_repo, payload):
    # 28.5 Given I have a saved answer on an open Bet
    ana, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = text_bet(client, pool["id"], headers)
    assert answer(client, pool, bet, headers, "Ana").status_code == 201

    # When I submit an invalid answer
    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/picks", json=payload, headers=headers,
    )

    # Then I see a validation error and my saved answer remains unchanged
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert pick_repo.get(bet["id"], ana.id).answer == TextAnswer("Ana")


def test_replacing_an_answer_changes_only_mine(client, user_repo, pick_repo):
    # 28.6 Given I have a saved answer and the deadline is in the future
    ana, ana_headers = sign_in(user_repo, name="Ana")
    bruno, bruno_headers = sign_in(user_repo, name="Bruno")
    pool = create_pool(client, ana_headers)
    bet = text_bet(client, pool["id"], ana_headers)
    answer(client, pool, bet, ana_headers, "Ronaldo")
    answer(client, pool, bet, bruno_headers, "Messi")

    # When I submit another valid answer
    response = answer(client, pool, bet, ana_headers, "Mbappé")

    # Then only my current answer is replaced; other Users' answers are unchanged
    assert response.status_code == 201
    assert len(pick_repo.picks) == 2
    assert pick_repo.get(bet["id"], ana.id).answer == TextAnswer("Mbappé")
    assert pick_repo.get(bet["id"], bruno.id).answer == TextAnswer("Messi")


@pytest.mark.parametrize("offset", [0, 1], ids=["at", "after"])
def test_nothing_changes_at_or_after_the_deadline(
    client, user_repo, pool_repo, pick_repo, monkeypatch, offset,
):
    # 28.7 Given an existing text Bet with my answer, and the clock at or after the deadline
    ana, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = text_bet(client, pool["id"], headers)
    answer(client, pool, bet, headers, "Ana")
    freeze_clock(monkeypatch, pool_repo, offset)

    # When I add an open-ended Bet or replace my answer
    added = client.post(
        f"/api/pools/{pool['id']}/bets",
        json={"statement": "Who gets a red card?", "answer_type": "text"},
        headers=headers,
    )
    replaced = answer(client, pool, bet, headers, "Bruno")

    # Then each action is refused without changing questions or answers
    assert added.status_code == 400
    assert replaced.status_code == 400
    assert [stored.id for stored in pool_repo.pools[0].bets] == [bet["id"]]
    assert pick_repo.get(bet["id"], ana.id).answer == TextAnswer("Ana")


@pytest.mark.parametrize("offset", [0, 1], ids=["at", "after"])
def test_first_answer_is_refused_at_or_after_the_deadline(
    client, user_repo, pool_repo, pick_repo, monkeypatch, offset,
):
    # 28.7 Given an open-ended Bet without my answer, and the clock at or after the deadline
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = text_bet(client, pool["id"], headers)
    freeze_clock(monkeypatch, pool_repo, offset)

    # When I submit an answer
    response = answer(client, pool, bet, headers, "Ana")

    # Then it is refused and nothing is stored
    assert response.status_code == 400
    assert pick_repo.picks == {}


def test_other_answers_stay_hidden_before_the_deadline(client, user_repo):
    # 28.8 Given Ana and Bruno have answers before the deadline
    ana, ana_headers = sign_in(user_repo, name="Ana")
    _, bruno_headers = sign_in(user_repo, name="Bruno")
    pool = create_pool(client, ana_headers)
    bet = text_bet(client, pool["id"], ana_headers)
    answer(client, pool, bet, ana_headers, "Ronaldo")
    answer(client, pool, bet, bruno_headers, "Messi")

    # When Ana requests the Bet's answers
    visible = picks(client, pool, ana_headers)

    # Then she sees her own answer but Bruno's is not disclosed
    assert [(pick["user"]["id"], pick["answer_text"]) for pick in visible] == [(ana.id, "Ronaldo")]


def test_answers_are_revealed_from_the_deadline(client, user_repo, pool_repo, monkeypatch):
    # 28.9 Given Ana and Bruno have answers, and another Bet has none
    ana, ana_headers = sign_in(user_repo, name="Ana")
    bruno, bruno_headers = sign_in(user_repo, name="Bruno")
    _, carla_headers = sign_in(user_repo, name="Carla")
    pool = create_pool(client, ana_headers)
    bet = text_bet(client, pool["id"], ana_headers)
    empty = text_bet(client, pool["id"], ana_headers, statement="Who gets a red card?")
    answer(client, pool, bet, ana_headers, "Ronaldo")
    answer(client, pool, bet, bruno_headers, "Messi")
    answer(client, pool, bet, ana_headers, "Mbappé")

    # When the clock reaches the deadline and another participant views the Pool
    freeze_clock(monkeypatch, pool_repo, 0)
    visible = picks(client, pool, carla_headers)

    # Then both names and their latest answers are visible; the other Bet has none
    assert {(pick["user"]["name"], pick["answer_text"]) for pick in visible} == {
        (ana.name, "Mbappé"), (bruno.name, "Messi"),
    }
    assert [pick for pick in visible if pick["bet_id"] == empty["id"]] == []


def test_answer_cannot_be_saved_for_someone_else(client, user_repo, pick_repo):
    # 28.10 Given Ana has an answer
    ana, ana_headers = sign_in(user_repo, name="Ana")
    _, bruno_headers = sign_in(user_repo, name="Bruno")
    pool = create_pool(client, ana_headers)
    bet = text_bet(client, pool["id"], ana_headers)
    answer(client, pool, bet, ana_headers, "Ronaldo")
    url = f"/api/pools/{pool['id']}/bets/{bet['id']}/picks"

    # When someone signed out, or signed in as Bruno, tries to save an answer as Ana
    signed_out = client.post(url, json={"answer_text": "Messi", "user_id": ana.id})
    as_bruno = client.post(url, json={"answer_text": "Messi", "user_id": ana.id}, headers=bruno_headers)
    unknown_token = client.post(
        url, json={"answer_text": "Messi"}, headers=bearer(token_for("not-a-user")),
    )

    # Then the action is refused and Ana's answer is unchanged
    assert signed_out.status_code == 401
    assert as_bruno.status_code == 400
    assert unknown_token.status_code in (401, 403)
    assert pick_repo.get(bet["id"], ana.id).answer == TextAnswer("Ronaldo")
    assert len(pick_repo.picks) == 1


def test_text_bet_cannot_be_resolved_yet(client, user_repo, pool_repo, monkeypatch):
    # Judging text answers is US33; until then the Resolve endpoint refuses text Bets.
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = text_bet(client, pool["id"], headers)
    freeze_clock(monkeypatch, pool_repo, 1)

    response = client.post(
        f"/api/pools/{pool['id']}/bets/{bet['id']}/resolve",
        json={"winning_outcome_id": "anything"},
        headers=headers,
    )

    assert response.status_code == 400
    assert pool_repo.pools[0].bets[0].winning_outcome_id is None


def test_text_picks_count_as_neither_win_nor_loss(client, user_repo, pool_repo, monkeypatch):
    ana, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    bet = text_bet(client, pool["id"], headers)
    answer(client, pool, bet, headers, "Ronaldo")
    freeze_clock(monkeypatch, pool_repo, 1)

    response = client.get(f"/api/pools/{pool['id']}/leaderboard")

    assert response.get_json() == [
        {"user": {"id": ana.id, "name": ana.name}, "wins": 0, "losses": 0, "rank": 1}
    ]
