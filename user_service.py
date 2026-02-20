"""User/staff lookup for Discord role-based permissions."""
from typing import Optional

from models import User, get_session


def get_user_role(discord_id: str) -> str:
    """Return role for discord_id; default to 'general' if not in DB."""
    session = get_session()
    try:
        user = session.query(User).filter(User.discord_id == str(discord_id)).first()
        return (user.role if user else None) or "general"
    finally:
        session.close()


def set_user_role(discord_id: str, role: str) -> User:
    """Create or update user with given Discord ID and role."""
    session = get_session()
    try:
        user = session.query(User).filter(User.discord_id == str(discord_id)).first()
        if user:
            user.role = role
        else:
            user = User(discord_id=str(discord_id), role=role)
            session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def can_edit_recipes(role: str) -> bool:
    """Only sushi_chef and admin can create/update recipes."""
    return role in ("sushi_chef", "admin")
