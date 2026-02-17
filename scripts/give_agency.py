import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from user_app.db import get_client
from core.models.user import PlanType

def upgrade_all_users():
    client = get_client()
    # Fetch all users
    result = client.table("users").select("*").execute()
    users = result.data
    
    if not users:
        print("No users found.")
        return

    print(f"Found {len(users)} users. Upgrading to AGENCY...")
    
    for u in users:
        print(f"Upgrading {u['email']} ({u['id']})...")
        client.table("users").update({"plan": PlanType.AGENCY.value}).eq("id", u['id']).execute()
    
    print("Done! All users are now on the AGENCY plan.")

if __name__ == "__main__":
    upgrade_all_users()
