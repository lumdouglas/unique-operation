"""Recipe CRUD and business logic."""
import logging
from typing import Any, Optional

from models import Recipe, get_session, init_db

logger = logging.getLogger(__name__)


def get_recipe(name: str) -> Optional[Recipe]:
    """Get a recipe by name (case-insensitive match)."""
    session = get_session()
    try:
        return session.query(Recipe).filter(Recipe.name.ilike(name)).first()
    finally:
        session.close()


def create_recipe(data: dict) -> Recipe:
    """Create a new recipe. data: name, ingredients, procedures, supplies, base_servings."""
    session = get_session()
    try:
        recipe = Recipe(
            name=data["name"],
            ingredients=data.get("ingredients", []),
            procedures=data.get("procedures", []),
            supplies=data.get("supplies", []),
            base_servings=data.get("base_servings", 50),
        )
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
        logger.info("Created recipe: %s", recipe.name)
        return recipe
    finally:
        session.close()


def update_recipe(name: str, updates: dict) -> Optional[Recipe]:
    """Update a recipe by name; merge updates into existing fields."""
    session = get_session()
    try:
        recipe = session.query(Recipe).filter(Recipe.name.ilike(name)).first()
        if not recipe:
            return None
        for key, value in updates.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)
        session.commit()
        session.refresh(recipe)
        logger.info("Updated recipe: %s with %s", name, list(updates.keys()))
        return recipe
    finally:
        session.close()


def delete_recipe(name: str) -> bool:
    """Delete a recipe by name. Returns True if deleted."""
    session = get_session()
    try:
        recipe = session.query(Recipe).filter(Recipe.name.ilike(name)).first()
        if not recipe:
            return False
        session.delete(recipe)
        session.commit()
        logger.info("Deleted recipe: %s", name)
        return True
    finally:
        session.close()


def list_recipes() -> list[Recipe]:
    """Return all recipes."""
    session = get_session()
    try:
        return session.query(Recipe).all()
    finally:
        session.close()


def ensure_db():
    """Ensure database and tables exist."""
    init_db()
