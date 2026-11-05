"""Real migrations, Auth token verification and SQL repositories against PostgreSQL."""

import json
import os
from pathlib import Path
import uuid

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
import pytest

from app import create_app
from shared.auth import TokenVerifier
from shared.db import get_connection_factory
from tests.acceptance.steps import SIGNING_KEY, bearer, bet_payload, pool_payload, token_for

MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"
UPGRADE = "20261105000100_pool_transactions.sql"
pytestmark = pytest.mark.skipif(not os.environ.get("TEST_DATABASE_URL"), reason="needs TEST_DATABASE_URL")


def migrate(connect, name):
    with connect() as conn:
        conn.autocommit = True
        conn.execute((MIGRATIONS / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def template_database():
    # Existing Supabase migrations explicitly target public/auth. Give tests
    # generated databases, never rewrite public in the supplied base database.
    admin_url = os.environ["TEST_DATABASE_URL"]
    template = "issue31_template_" + uuid.uuid4().hex
    with psycopg.connect(admin_url, autocommit=True) as conn:
        if not conn.execute("SELECT 1 FROM pg_roles WHERE rolname = 'service_role'").fetchone():
            conn.execute("CREATE ROLE service_role NOLOGIN")
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(template)))
    template_url = make_conninfo(admin_url, dbname=template)
    connect = lambda: psycopg.connect(template_url)
    try:
        with connect() as conn:
            # Minimal Auth schema needed by the real signup migration; no mock
            # app tables or replacement repository code.
            conn.execute("""CREATE SCHEMA auth;
                CREATE TABLE auth.users (id UUID PRIMARY KEY, email TEXT,
                                         raw_user_meta_data JSONB NOT NULL DEFAULT '{}');""")
        for name in ["001_init.sql", "003_enable_rls.sql", "003a_create_user_on_signup.sql",
                     "003b_remove_guest_user.sql", "004_multiple_choice.sql",
                     "20261104210948_pool_contains_bets.sql"]:
            migrate(connect, name)
        yield admin_url, template
    finally:
        with psycopg.connect(admin_url, autocommit=True) as conn:
            conn.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(template)))


@pytest.fixture
def legacy_database(template_database, monkeypatch):
    admin_url, template = template_database
    name = "issue31_test_" + uuid.uuid4().hex
    with psycopg.connect(admin_url, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE DATABASE {} TEMPLATE {}").format(
            sql.Identifier(name), sql.Identifier(template),
        ))
    monkeypatch.setenv("DATABASE_URL", make_conninfo(admin_url, dbname=name))
    try:
        yield get_connection_factory()
    finally:
        with psycopg.connect(admin_url, autocommit=True) as conn:
            conn.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))


@pytest.fixture
def database(legacy_database):
    migrate(legacy_database, UPGRADE)
    return legacy_database


def seed_account(connect):
    user_id = str(uuid.uuid4())
    with connect() as conn:
        conn.execute("INSERT INTO auth.users (id, email, raw_user_meta_data) VALUES (%s, %s, %s)",
                     (user_id, f"{user_id}@example.com", json.dumps({"name": "Ana"})))
    return user_id, bearer(token_for(user_id))


@pytest.fixture
def client(database):
    app = create_app(token_verifier=TokenVerifier.for_public_key(SIGNING_KEY.public_key()))
    app.testing = True
    return app.test_client()


@pytest.fixture
def reject_option(database):
    with database() as conn:
        conn.execute("""
            CREATE FUNCTION reject_option() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
              IF NEW.label = '__fail__' THEN
                RAISE EXCEPTION 'forced failure after % bets and % options',
                  (SELECT count(*) FROM bets WHERE pool_id = (SELECT pool_id FROM bets WHERE id = NEW.bet_id)),
                  (SELECT count(*) FROM outcomes WHERE bet_id IN
                    (SELECT id FROM bets WHERE pool_id = (SELECT pool_id FROM bets WHERE id = NEW.bet_id)))
                  USING ERRCODE = '23514';
              END IF;
              RETURN NEW;
            END; $$;
            CREATE TRIGGER reject_option BEFORE INSERT ON outcomes
              FOR EACH ROW EXECUTE FUNCTION reject_option();
        """)


def snapshot(connect):
    with connect() as conn:
        return {table: conn.execute(sql.SQL("SELECT * FROM {} ORDER BY id").format(
            sql.Identifier(table),
        )).fetchall() for table in ("users", "pools", "rounds", "bets", "outcomes", "picks")}


@pytest.mark.parametrize("bet_index, option_index, progress", [(0, 1, "1 bets and 1 options"),
                                                             (1, 1, "2 bets and 3 options")])
def test_pool_creation_rolls_back_then_valid_request_succeeds(
    client, database, reject_option, caplog, bet_index, option_index, progress,
):
    _, headers = seed_account(database)
    existing = client.post("/api/pools", json=pool_payload(name="Existing"), headers=headers).get_json()
    before = snapshot(database)
    bets = [bet_payload(statement="First?"), bet_payload(statement="Second?")]
    bets[bet_index]["options"][option_index] = "__fail__"

    response = client.post("/api/pools", json=pool_payload(initial_bets=bets), headers=headers)

    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error."}
    assert f"forced failure after {progress}" in caplog.text
    assert snapshot(database) == before
    assert client.get("/api/pools").get_json() == [existing]

    bets[bet_index]["options"][option_index] = "Valid"
    response = client.post("/api/pools", json=pool_payload(initial_bets=bets), headers=headers)
    assert response.status_code == 201
    created = response.get_json()
    assert len(created["bets"]) == 2
    assert [bet["statement"] for bet in created["bets"]] == ["First?", "Second?"]
    assert all(len(bet["options"]) == 2 for bet in created["bets"])
    assert client.get(f"/api/pools/{created['id']}").get_json() == created
    saved = snapshot(database)
    assert {t: len(saved[t]) for t in ("pools", "rounds", "bets", "outcomes")} == {
        "pools": 2, "rounds": 2, "bets": 2, "outcomes": 4,
    }


def test_adding_bet_rolls_back_without_changing_existing_bets_or_picks(client, database, reject_option):
    _, headers = seed_account(database)
    pool = client.post("/api/pools", json=pool_payload(initial_bets=[bet_payload()]), headers=headers).get_json()
    bet = pool["bets"][0]
    pick_url = f"/api/pools/{pool['id']}/bets/{bet['id']}/picks"
    assert client.post(pick_url, json={"outcome_id": bet["options"][0]["id"]}, headers=headers).status_code == 201
    before = snapshot(database)
    url = f"/api/pools/{pool['id']}/bets"

    response = client.post(url, json=bet_payload(options=["Saved first", "__fail__"]), headers=headers)
    assert response.status_code == 500
    assert snapshot(database) == before

    response = client.post(url, json=bet_payload(options=["A", "B", "C"], presentation="dropdown"), headers=headers)
    assert response.status_code == 201
    updated = client.get(f"/api/pools/{pool['id']}").get_json()
    assert updated["bets"][0] == bet
    assert [o["label"] for o in response.get_json()["options"]] == ["A", "B", "C"]
    assert response.get_json()["presentation"] == "dropdown"
    # The third repository must still replace a Pick and preserve its identity.
    response = client.post(pick_url, json={"outcome_id": bet["options"][1]["id"]}, headers=headers)
    assert response.status_code == 201
    assert str(before["picks"][0]["id"]) == response.get_json()["id"]
    assert client.get(f"/api/pools/{pool['id']}/picks", headers=headers).get_json()["picks"] == [response.get_json()]


@pytest.mark.parametrize("initial_bets", [None, "not-an-array", [bet_payload(options=["Only one"])]])
def test_invalid_initial_bets_are_rejected_without_writes(client, database, initial_bets):
    _, headers = seed_account(database)
    before = snapshot(database)
    response = client.post("/api/pools", json=pool_payload(initial_bets=initial_bets), headers=headers)
    assert response.status_code == 400
    assert snapshot(database) == before


def test_migration_backfills_round_without_changing_existing_data(legacy_database):
    connect = legacy_database
    user_id, _ = seed_account(connect)
    with connect() as conn:
        pool_id = conn.execute("""INSERT INTO pools (name, deadline, creator_id, decider_id)
            VALUES ('Existing', '2030-01-01T00:00:00Z', %s, %s) RETURNING id""", (user_id, user_id)).fetchone()["id"]
        bet_id = conn.execute("INSERT INTO bets (pool_id, statement) VALUES (%s, 'Old?') RETURNING id", (pool_id,)).fetchone()["id"]
        outcome_id = conn.execute("INSERT INTO outcomes (bet_id, label, position) VALUES (%s, 'A', 0) RETURNING id", (bet_id,)).fetchone()["id"]
        conn.execute("UPDATE bets SET winning_outcome_id = %s WHERE id = %s", (outcome_id, bet_id))
        conn.execute("INSERT INTO picks (bet_id, user_id, outcome_id) VALUES (%s, %s, %s)", (bet_id, user_id, outcome_id))
        picks = conn.execute("SELECT * FROM picks").fetchall()
    migrate(connect, UPGRADE)
    with connect() as conn:
        assert conn.execute("SELECT * FROM picks").fetchall() == picks
        row = conn.execute("SELECT * FROM bets WHERE id = %s", (bet_id,)).fetchone()
        assert row["winning_outcome_id"] == outcome_id
        assert conn.execute("SELECT pool_id FROM rounds WHERE id = %s", (row["round_id"],)).fetchone()["pool_id"] == pool_id
