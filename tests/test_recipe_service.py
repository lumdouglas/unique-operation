"""Unit tests for recipe_service CRUD."""
import os
import pytest

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from models import Base, init_db, get_session, engine
from recipe_service import (
    create_recipe,
    get_recipe,
    update_recipe,
    delete_recipe,
    list_recipes,
)


@pytest.fixture(autouse=True)
def db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    get_session().close()


def test_create_and_get_recipe():
    data = {
        "name": "Test Roll",
        "ingredients": [{"item": "rice", "quantity": 100, "unit": "g", "cost_per_unit": 0.01}],
        "procedures": ["Step 1"],
        "supplies": [{"item": "tray", "quantity": 1}],
        "base_servings": 10,
    }
    created = create_recipe(data)
    assert created.name == "Test Roll"
    assert created.base_servings == 10

    found = get_recipe("Test Roll")
    assert found is not None
    assert found.name == "Test Roll"
    assert len(found.ingredients) == 1
    assert found.ingredients[0]["item"] == "rice"


def test_get_recipe_case_insensitive():
    create_recipe({"name": "California Roll", "base_servings": 50})
    assert get_recipe("california roll") is not None
    assert get_recipe("CALIFORNIA ROLL") is not None


def test_get_recipe_not_found():
    assert get_recipe("Nonexistent") is None


def test_update_recipe():
    create_recipe({"name": "UpdateMe", "base_servings": 20})
    updated = update_recipe("UpdateMe", {"base_servings": 30})
    assert updated is not None
    assert updated.base_servings == 30
    assert get_recipe("UpdateMe").base_servings == 30


def test_update_recipe_not_found():
    assert update_recipe("NoSuch", {"base_servings": 10}) is None


def test_delete_recipe():
    create_recipe({"name": "DeleteMe", "base_servings": 5})
    assert delete_recipe("DeleteMe") is True
    assert get_recipe("DeleteMe") is None


def test_delete_recipe_not_found():
    assert delete_recipe("NoSuch") is False


def test_list_recipes():
    create_recipe({"name": "A", "base_servings": 1})
    create_recipe({"name": "B", "base_servings": 1})
    recipes = list_recipes()
    assert len(recipes) >= 2
    names = [r.name for r in recipes]
    assert "A" in names and "B" in names
