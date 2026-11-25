"""Each answer validation strategy on its own, and how PickService selects one."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from picks.answers import ChoiceAnswerValidator, TextAnswerValidator, default_answer_validators
from picks.models import ChoiceAnswer, TextAnswer
from picks.service import PickService
from pools.models import AnswerType, Bet, NewBet, NewPool, Outcome, UserSummary
from pools.service import PoolService
from shared.errors import ValidationError
from tests.fakes import FakePickRepository, FakePoolRepository, FakeUserRepository
from users.models import User

NOW = datetime.now(timezone.utc)

CHOICE_BET = Bet(
    id="bet", pool_id="pool", statement="Who wins?",
    options=(Outcome("a", "A"), Outcome("b", "B")),
    winning_outcome_id=None, created_at=NOW,
)
TEXT_BET = replace(CHOICE_BET, options=(), answer_type=AnswerType.TEXT)


class TestChoiceAnswerValidator:
    def test_accepts_an_outcome_of_the_bet(self):
        assert ChoiceAnswerValidator().validate({"outcome_id": "b"}, CHOICE_BET) == ChoiceAnswer("b")

    @pytest.mark.parametrize(
        "payload",
        [{}, {"outcome_id": "other"}, {"outcome_id": 1}, {"outcome_id": "a", "answer_text": "A"}],
        ids=["missing", "foreign", "not-a-string", "text-field"],
    )
    def test_rejects_anything_else(self, payload):
        with pytest.raises(ValidationError):
            ChoiceAnswerValidator().validate(payload, CHOICE_BET)


class TestTextAnswerValidator:
    @pytest.mark.parametrize(
        "raw, text",
        [("A", "A"), ("  Ana\n", "Ana"), ("x" * 500, "x" * 500), ("😀" * 500, "😀" * 500)],
        ids=["one", "trimmed", "500", "500-emoji"],
    )
    def test_accepts_1_to_500_code_points_after_trimming(self, raw, text):
        assert TextAnswerValidator().validate({"answer_text": raw}, TEXT_BET) == TextAnswer(text)

    @pytest.mark.parametrize(
        "payload",
        [
            {}, {"answer_text": None}, {"answer_text": 5}, {"answer_text": " \t "},
            {"answer_text": "x" * 501}, {"answer_text": "Ana", "outcome_id": "a"},
        ],
        ids=["missing", "null", "number", "whitespace", "501", "choice-field"],
    )
    def test_rejects_anything_else(self, payload):
        with pytest.raises(ValidationError):
            TextAnswerValidator().validate(payload, TEXT_BET)

    def test_limit_is_configurable(self):
        validator = TextAnswerValidator(max_length=3)
        assert validator.validate({"answer_text": "abc"}, TEXT_BET) == TextAnswer("abc")
        with pytest.raises(ValidationError):
            validator.validate({"answer_text": "abcd"}, TEXT_BET)


def test_default_mapping_covers_every_answer_type():
    validators = default_answer_validators()
    assert set(validators) == set(AnswerType)
    assert isinstance(validators[AnswerType.CHOICE], ChoiceAnswerValidator)
    assert isinstance(validators[AnswerType.TEXT], TextAnswerValidator)


class RecordingValidator:
    """Stands in for a strategy to see what the context hands it."""

    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def validate(self, payload, bet):
        self.calls.append((payload, bet.id))
        return self.answer


@pytest.fixture
def setup():
    users = FakeUserRepository()
    ana = User(id="ana", name="Ana")
    users.add(ana)
    pools = FakePoolRepository()
    creator = UserSummary.of(ana)
    pool = pools.create_pool(NewPool("Final", "", NOW + timedelta(days=1), creator, creator))
    picks = FakePickRepository(users)
    return ana, pool, pools, picks


def add_bet(pools, pool, answer_type):
    options = ("A", "B") if answer_type == AnswerType.CHOICE else ()
    return pools.create_bet(pool.id, NewBet("Q?", options, answer_type=answer_type))


@pytest.mark.parametrize("answer_type", list(AnswerType))
def test_service_uses_the_strategy_for_the_bets_answer_type(setup, answer_type):
    ana, pool, pools, picks = setup
    bet = add_bet(pools, pool, answer_type)
    chosen = RecordingValidator(TextAnswer("from the chosen strategy"))
    other = RecordingValidator(TextAnswer("wrong"))
    validators = {kind: (chosen if kind == answer_type else other) for kind in AnswerType}
    service = PickService(picks, PoolService(pools), validators=validators)

    pick = service.save_pick(pool.id, bet.id, {"anything": 1}, ana)

    assert chosen.calls == [({"anything": 1}, bet.id)]
    assert other.calls == []
    assert pick.answer == TextAnswer("from the chosen strategy")


def test_service_refuses_a_type_without_a_strategy(setup):
    ana, pool, pools, picks = setup
    bet = add_bet(pools, pool, AnswerType.TEXT)
    service = PickService(
        picks, PoolService(pools), validators={AnswerType.CHOICE: ChoiceAnswerValidator()},
    )

    with pytest.raises(ValidationError):
        service.save_pick(pool.id, bet.id, {"answer_text": "Ana"}, ana)
    assert picks.picks == {}


def test_strategy_is_not_consulted_once_the_pool_is_locked(setup):
    ana, pool, pools, picks = setup
    bet = add_bet(pools, pool, AnswerType.TEXT)
    pools.pools[0] = replace(pools.pools[0], deadline=NOW - timedelta(seconds=1))
    validator = RecordingValidator(TextAnswer("Ana"))
    service = PickService(picks, PoolService(pools), validators={AnswerType.TEXT: validator})

    with pytest.raises(ValidationError):
        service.save_pick(pool.id, bet.id, {"answer_text": "Ana"}, ana)
    assert validator.calls == []
