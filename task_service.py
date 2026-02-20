"""Prep list generation and role-based task assignment."""
from typing import Optional

from ai_service import ai_refine_quantities
from recipe_service import get_recipe


# Role -> types of tasks they handle
ROLE_TASKS = {
    "sushi_chef": ["rolling", "rice", "fish", "assembly", "procedure"],
    "prep_cook": ["chopping", "prep", "veggies", "slice", "dice"],
    "general": ["packing", "supplies", "tray", "lid", "container", "delivery"],
    "admin": ["rolling", "rice", "fish", "chopping", "prep", "packing", "supplies"],
}


def generate_prep_list(recipe_name: str, guests: int) -> str:
    """
    Generate a markdown prep list for the recipe scaled to guest count.
    """
    recipe = get_recipe(recipe_name)
    if not recipe:
        return f"Recipe not found: {recipe_name}"

    refined = ai_refine_quantities(recipe, guests)
    ingredients = refined.get("ingredients", [])
    supplies = refined.get("supplies", [])
    procedures = recipe.procedures or []
    total_cost = refined.get("total_cost", 0)

    lines = [
        f"# Prep list: **{recipe.name}** (for {guests} guests)",
        "",
        "## Ingredients",
    ]
    for item in ingredients:
        qty = item.get("quantity", 0)
        unit = item.get("unit", "")
        name = item.get("item", "?")
        lines.append(f"- **{name}**: {qty} {unit}")

    lines.extend(["", "## Supplies"])
    for item in supplies:
        qty = item.get("quantity", 0)
        name = item.get("item", "?")
        lines.append(f"- **{name}**: {qty}")

    if procedures:
        lines.extend(["", "## Procedures"])
        for i, step in enumerate(procedures, 1):
            lines.append(f"{i}. {step}")

    lines.extend(["", f"**Estimated cost (ingredients):** ${total_cost:.2f}"])
    return "\n".join(lines)


def assign_tasks(prep_list: str, role: str) -> str:
    """
    Filter the prep list to tasks relevant to the given role.
    Returns markdown string.
    """
    role_lower = (role or "general").lower()
    keywords = ROLE_TASKS.get(role_lower, ROLE_TASKS["general"])
    lines = prep_list.split("\n")
    out = []
    in_section = False
    section_keywords = []

    for line in lines:
        if line.startswith("## "):
            section = line[3:].strip().lower()
            in_section = any(kw in section for kw in keywords)
            section_keywords = [kw for kw in keywords if kw in section]
            if in_section:
                out.append(line)
            continue
        if line.startswith("# "):
            out.append(line)
            continue
        if in_section:
            out.append(line)
        elif line.strip().startswith("-") or line.strip() and line.strip()[0].isdigit():
            # Item line: include if any keyword matches
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                if out and out[-1] and not out[-1].startswith("## "):
                    pass
                else:
                    out.append("")
                out.append(line)

    if not out:
        return prep_list  # No role filter match; return full list
    return "\n".join(out).strip() or prep_list
