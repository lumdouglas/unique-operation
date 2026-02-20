"""AI-powered recipe updates and quantity refinements via Gemini API."""
import json
import logging
from typing import Any, Optional

from config import GEMINI_API_KEY
from models import Recipe

logger = logging.getLogger(__name__)

# Default Gemini model for text generation
GEMINI_MODEL = "gemini-2.0-flash"


def _get_client():
    """Lazy import and return Gemini client."""
    try:
        from google import genai
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.warning("Gemini client unavailable: %s", e)
        return None


def _generate(prompt: str) -> Optional[str]:
    """Call Gemini and return response text, or None on failure."""
    client = _get_client()
    if not client or not GEMINI_API_KEY:
        return None
    try:
        from google.genai import types
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2),
        )
        return (response.text or "").strip() if response else None
    except Exception as e:
        logger.warning("Gemini generate_content failed: %s", e)
        return None


def ai_parse_update(recipe: Recipe, user_input: str) -> dict:
    """
    Parse user input into structured recipe updates using the LLM.
    Returns a dict of field names to new values (e.g. ingredients, procedures, supplies).
    """
    recipe_data = recipe.to_dict()
    prompt = (
        "You are a sushi catering assistant. Parse the user's request into JSON updates "
        "that can be applied to the recipe. Only output valid JSON with keys that exist on the recipe: "
        "name, ingredients, procedures, supplies, base_servings. "
        "Keep existing structure: ingredients is a list of objects with item, quantity, unit, cost_per_unit; "
        "procedures is a list of strings; supplies is a list of objects with item, quantity.\n\n"
        f"Current recipe (JSON):\n{json.dumps(recipe_data, indent=2)}\n\n"
        f"User input: {user_input}\n\n"
        "Output only the JSON object with the fields to update (no markdown, no explanation)."
    )
    text = _generate(prompt)
    if not text:
        return _fallback_parse_update(recipe, user_input)
    try:
        # Strip markdown code block if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        return json.loads(text)
    except (json.JSONDecodeError, IndexError, AttributeError) as e:
        logger.warning("AI parse failed, using fallback: %s", e)
        return _fallback_parse_update(recipe, user_input)


def _fallback_parse_update(recipe: Recipe, user_input: str) -> dict:
    """Simple fallback when API is unavailable: return empty updates."""
    return {}


def _ingredient_cost(ingredients: list[dict]) -> float:
    """Sum cost for ingredients: quantity * cost_per_unit per item."""
    total = 0.0
    for item in ingredients or []:
        qty = float(item.get("quantity", 0))
        cost = float(item.get("cost_per_unit", 0))
        total += qty * cost
    return round(total, 2)


def ai_refine_quantities(
    recipe: Recipe, guests: int, feedback: str = ""
) -> dict:
    """
    Scale quantities for guest count and optionally apply AI optimization from feedback.
    Returns dict with adjusted ingredients, supplies, total_cost, and scale_factor.
    """
    if recipe.base_servings <= 0:
        raise ValueError("base_servings must be positive")
    factor = guests / recipe.base_servings

    client = _get_client()
    if not client or not GEMINI_API_KEY or not feedback:
        # Simple scaling without AI
        ingredients = []
        for item in (recipe.ingredients or []):
            ingredients.append({
                **item,
                "quantity": round(float(item.get("quantity", 0)) * factor, 2),
            })
        supplies = []
        for item in (recipe.supplies or []):
            supplies.append({
                **item,
                "quantity": max(1, int(float(item.get("quantity", 0)) * factor)),
            })
        total_cost = _ingredient_cost(ingredients)
        return {
            "ingredients": ingredients,
            "supplies": supplies,
            "total_cost": total_cost,
            "scale_factor": factor,
            "guests": guests,
        }

    # AI refinement with feedback
    recipe_data = recipe.to_dict()
    prompt = (
        "You are a sushi catering assistant. Scale the recipe quantities for the given number of guests. "
        f"Base servings: {recipe.base_servings}. Guests: {guests}. Scale factor = {factor:.2f}. "
        f"Optional feedback to optimize for: {feedback or 'none'}. "
        "Output a single JSON object with keys: ingredients (list with item, quantity, unit, cost_per_unit), "
        "supplies (list with item, quantity), total_cost (number). Use the same structure as the recipe. "
        "Quantities should be scaled appropriately; total_cost = sum(quantity * cost_per_unit) for ingredients.\n\n"
        f"Recipe (JSON):\n{json.dumps(recipe_data, indent=2)}\n\n"
        "Output only the JSON object (no markdown, no explanation)."
    )
    text = _generate(prompt)
    if text:
        try:
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            out = json.loads(text)
            out.setdefault("ingredients", recipe.ingredients or [])
            out.setdefault("supplies", recipe.supplies or [])
            if "total_cost" not in out:
                out["total_cost"] = _ingredient_cost(out["ingredients"])
            out["scale_factor"] = factor
            out["guests"] = guests
            return out
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            logger.warning("AI refine failed, using simple scale: %s", e)
    ingredients = []
    for item in (recipe.ingredients or []):
        ingredients.append({
            **item,
            "quantity": round(float(item.get("quantity", 0)) * factor, 2),
        })
    supplies = []
    for item in (recipe.supplies or []):
        supplies.append({
            **item,
            "quantity": max(1, int(float(item.get("quantity", 0)) * factor)),
        })
    return {
        "ingredients": ingredients,
        "supplies": supplies,
        "total_cost": _ingredient_cost(ingredients),
        "scale_factor": factor,
        "guests": guests,
    }
