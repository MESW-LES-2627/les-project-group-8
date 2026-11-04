"""ADR 0003: Flask is the only door to the app tables. These tests knock on the back door,
Supabase's REST API with the publishable key, against the real project, and check that
row-level security keeps it shut. Skipped unless SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are set."""

import os

import pytest
from dotenv import load_dotenv
from postgrest.exceptions import APIError
from supabase import create_client

load_dotenv()
URL = os.environ.get("SUPABASE_URL")
PUBLISHABLE_KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY")
SECRET_KEY = os.environ.get("SUPABASE_KEY")

pytestmark = pytest.mark.skipif(
    not URL or not PUBLISHABLE_KEY,
    reason="needs SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY (see backend/.env.example)",
)

# Postgres "insufficient privilege": what PostgREST returns when RLS refuses a write.
RLS_REFUSED = "42501"
NO_SUCH_USER = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def back_door():
    return create_client(URL, PUBLISHABLE_KEY)


def test_pools_cannot_be_read_with_the_publishable_key(back_door):
    # Given pools exist (checked with the secret key when it is available)
    if SECRET_KEY and SECRET_KEY.startswith("sb_secret_"):
        flask_side = create_client(URL, SECRET_KEY)
        if not flask_side.table("pools").select("id").limit(1).execute().data:
            pytest.skip("no pools in the database, so an empty read proves nothing")

    # When I read them straight from Supabase with the publishable key
    rows = back_door.table("pools").select("id").limit(1).execute().data

    # Then RLS hides every row (with no policies it filters reads instead of erroring)
    assert rows == []


def test_pools_cannot_be_inserted_with_the_publishable_key(back_door):
    # Given a pool naming a User that does not exist, so nothing could be saved even if RLS were off
    row = {
        "name": "Back door",
        "statement": "RLS lets this through",
        "deadline": "2030-01-01T00:00:00+00:00",
        "creator_id": NO_SUCH_USER,
        "decider_id": NO_SUCH_USER,
    }

    # When I insert it straight into Supabase with the publishable key
    with pytest.raises(APIError) as refused:
        back_door.table("pools").insert(row).execute()

    # Then RLS refuses it (a foreign-key error, 23503, would mean RLS let it through)
    assert refused.value.code == RLS_REFUSED
