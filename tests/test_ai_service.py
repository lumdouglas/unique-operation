"""Unit tests for ai_service (scaling and fallback behavior)."""
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["GEMINI_API_KEY"] = ""  # Use simple scaling, no API

from models import Recipe
from ai_service import ai_refine_quantities, _ingredient_cost


def test_ingredient_cost():
    ingredients = [
        {"quantity": 10, "cost_per_unit": 2},
        {"quantity": 5, "cost_per_unit": 4},
    ]
    assert _ingredient_cost(ingredients) == 40.0
    assert _ingredient_cost([]) == 0.0


def test_ai_refine_quantities_simple_scale():
    recipe = Recipe(
        name="Test",
        base_servings=50,
        ingredients=[
            {"item": "rice", "quantity": 1000, "unit": "g", "cost_per_unit": 0.01},
            {"item": "fish", "quantity": 500, "unit": "g", "cost_per_unit": 0.02},
        ],
        supplies=[{"item": "tray", "quantity": 10}],
    )
    # 100 guests = 2x scale
    result = ai_refine_quantities(recipe, 100, feedback="")
    assert result["scale_factor"] == 2.0
    assert result["guests"] == 100
    assert len(result["ingredients"]) == 2
    assert result["ingredients"][0]["quantity"] == 2000
    assert result["ingredients"][1]["quantity"] == 1000
    assert result["supplies"][0]["quantity"] == 20
    assert result["total_cost"] == 40.0  # 2000*0.01 + 1000*0.02


def test_ai_refine_quantities_invalid_base_servings():
    recipe = Recipe(name="Bad", base_servings=0, ingredients=[])
    import pytest
    with pytest.raises(ValueError, match="base_servings"):
        ai_refine_quantities(recipe, 10)
