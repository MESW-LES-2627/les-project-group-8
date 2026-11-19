"""US15 reveal and US16 privacy, including the exact deadline boundary."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tests.acceptance.steps import create_bet, create_pool, pick_payload, sign_in


@pytest.mark.parametrize("offset", [-1, 0, 1], ids=["before", "at", "after"])
def test_visibility_changes_exactly_at_deadline(
    client, user_repo, pool_repo, monkeypatch, offset,
):
    ana, headers = sign_in(user_repo, name="Ana")
    bruno, bruno_headers = sign_in(user_repo, name="Bruno")
    pool = create_pool(client, headers)
    bet = create_bet(client, pool["id"], headers, options=["A", "B"])
    for actor_headers, option in zip((headers, bruno_headers), bet["options"]):
        response = client.post(
            f"/api/pools/{pool['id']}/bets/{bet['id']}/picks",
            json=pick_payload(option["id"]),
            headers=actor_headers,
        )
        assert response.status_code == 201

    deadline = pool_repo.pools[0].deadline

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return deadline + timedelta(microseconds=offset)

    monkeypatch.setattr("pools.models.datetime", Clock)
    response = client.get(f"/api/pools/{pool['id']}/picks", headers=headers)
    assert response.status_code == 200
    picks = response.get_json()["picks"]
    expected = [(ana, bet["options"][0])]
    if offset >= 0:
        expected.append((bruno, bet["options"][1]))
    assert {(pick["user"]["id"], pick["user"]["name"], pick["outcome_id"]) for pick in picks} == {
        (user.id, user.name, option["id"]) for user, option in expected
    }
    assert all(pick["user_id"] == pick["user"]["id"] for pick in picks)
    assert len(picks) == len(expected)


def test_closed_pool_without_picks_returns_empty_list(client, user_repo, pool_repo):
    _, headers = sign_in(user_repo)
    pool = create_pool(client, headers)
    create_bet(client, pool["id"], headers)
    pool_repo.pools[0] = replace(
        pool_repo.pools[0], deadline=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    response = client.get(f"/api/pools/{pool['id']}/picks", headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"picks": []}

