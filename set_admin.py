"""
One-time script to set the first admin user (Discord ID).
Run: python set_admin.py YOUR_DISCORD_ID
Then use /set_role in Discord to assign other staff.
"""
import sys
from recipe_service import ensure_db
from user_service import set_user_role

def main():
    ensure_db()
    if len(sys.argv) < 2:
        print("Usage: python set_admin.py <discord_id>")
        sys.exit(1)
    discord_id = sys.argv[1].strip()
    set_user_role(discord_id, "admin")
    print(f"Set {discord_id} as admin. They can now use /set_role in Discord.")

if __name__ == "__main__":
    main()
