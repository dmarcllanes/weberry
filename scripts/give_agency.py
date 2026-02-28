"""
Admin utility: give all users a large credit balance (e.g. for beta testers).
Usage: uv run python scripts/give_agency.py [--amount 50]
"""
import sys
import os
import argparse

sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from user_app.db import get_client


def give_credits(amount: int = 50):
    client = get_client()
    result = client.table("users").select("id, email, paid_credits").execute()
    users = result.data

    if not users:
        print("No users found.")
        return

    print(f"Giving {amount} paid credits to {len(users)} users...")

    for u in users:
        current = u.get("paid_credits", 0)
        client.table("users").update({"paid_credits": current + amount}).eq("id", u["id"]).execute()
        print(f"  {u['email']} ({u['id']}): {current} → {current + amount} credits")

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--amount", type=int, default=50)
    args = parser.parse_args()
    give_credits(args.amount)
