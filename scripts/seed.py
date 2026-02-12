"""
Seed script: creates a stub dev user for local development.

Usage: python -m scripts.seed
Requires: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables
"""

import os
import sys

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

STUB_USER_ID = "00000000-0000-0000-0000-000000000001"
STUB_USER_EMAIL = "dev@okenaba.local"


def run():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY are required")
        sys.exit(1)

    client = create_client(url, key)

    existing = client.table("users").select("id").eq("id", STUB_USER_ID).execute()
    if existing.data:
        print(f"Stub user already exists: {STUB_USER_ID}")
        return

    client.table("users").insert({
        "id": STUB_USER_ID,
        "email": STUB_USER_EMAIL,
        "plan": "FREE",
    }).execute()

    print(f"Stub user created: {STUB_USER_ID} ({STUB_USER_EMAIL})")


if __name__ == "__main__":
    run()
