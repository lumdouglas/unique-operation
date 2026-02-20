"""
Discord bot for Sushi Catering Management System.
Slash commands: /help, /add_recipe, /update_recipe, /refine_quantities, /get_prep_list.
Role-based auth: only sushi_chef/admin can update recipes.
"""
import json
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from config import DISCORD_TOKEN
from recipe_service import (
    create_recipe,
    get_recipe,
    list_recipes,
    update_recipe,
    ensure_db,
)
from ai_service import ai_parse_update, ai_refine_quantities
from task_service import generate_prep_list, assign_tasks
from user_service import get_user_role, can_edit_recipes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)


def _parse_json_arg(value: str, name: str) -> list:
    """Parse a JSON string to list; return [] on failure."""
    if not value or not value.strip():
        return []
    try:
        out = json.loads(value)
        return out if isinstance(out, list) else [out]
    except json.JSONDecodeError:
        logger.warning("Invalid JSON for %s: %s", name, value[:100])
        return []


def _parse_ingredients(value: str) -> list:
    """Parse ingredients string to list of dicts (item, quantity, unit, cost_per_unit)."""
    data = _parse_json_arg(value, "ingredients")
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append({
                "item": item.get("item", "?"),
                "quantity": float(item.get("quantity", 0)),
                "unit": item.get("unit", ""),
                "cost_per_unit": float(item.get("cost_per_unit", 0)),
            })
    return result


def _parse_procedures(value: str) -> list:
    """Parse procedures string to list of step strings."""
    data = _parse_json_arg(value, "procedures")
    return [str(s) for s in data]


def _parse_supplies(value: str) -> list:
    """Parse supplies string to list of dicts (item, quantity)."""
    data = _parse_json_arg(value, "supplies")
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append({
                "item": item.get("item", "?"),
                "quantity": int(item.get("quantity", 0)),
            })
    return result


@bot.event
async def on_ready():
    ensure_db()
    try:
        synced = await bot.tree.sync()
        logger.info("Synced %s slash command(s).", len(synced))
    except Exception as e:
        logger.exception("Failed to sync commands: %s", e)
    logger.info("Bot ready as %s", bot.user)


@bot.tree.command(name="help", description="List all bot commands and usage.")
async def help_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="Sushi Catering Bot – Help",
        description="Commands for recipes, prep lists, and quantity refinements.",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="/add_recipe",
        value="Add a new recipe. Args: name, ingredients (JSON), procedures (JSON), supplies (JSON), base_servings. (sushi_chef/admin only)",
        inline=False,
    )
    embed.add_field(
        name="/update_recipe",
        value="Update a recipe using natural language. Args: name, input. (sushi_chef/admin only)",
        inline=False,
    )
    embed.add_field(
        name="/refine_quantities",
        value="Scale and optionally optimize quantities for guest count. Args: name, guests, feedback (optional).",
        inline=False,
    )
    embed.add_field(
        name="/get_prep_list",
        value="Get prep list for a recipe and guest count, filtered by your role.",
        inline=False,
    )
    embed.add_field(
        name="/list_recipes",
        value="List all recipe names.",
        inline=False,
    )
    embed.add_field(
        name="/set_role",
        value="Set a user's role: discord_id, role (admin only).",
        inline=False,
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(
    name="add_recipe",
    description="Add a new recipe (ingredients, procedures, supplies as JSON strings).",
)
@app_commands.describe(
    name="Recipe name",
    ingredients='JSON array, e.g. [{"item":"fish","quantity":200,"unit":"g","cost_per_unit":15}]',
    procedures='JSON array of steps, e.g. ["Rinse rice","Cook 20min"]',
    supplies='JSON array, e.g. [{"item":"tray","quantity":10}]',
    base_servings="Base serving count for scaling (default 50)",
)
async def add_recipe(
    interaction: discord.Interaction,
    name: str,
    ingredients: str = "[]",
    procedures: str = "[]",
    supplies: str = "[]",
    base_servings: int = 50,
):
    role = get_user_role(str(interaction.user.id))
    if not can_edit_recipes(role):
        await interaction.response.send_message(
            "You don't have permission to add recipes. (Need role: sushi_chef or admin.)",
            ephemeral=True,
        )
        return

    await interaction.response.defer()
    try:
        data = {
            "name": name.strip(),
            "ingredients": _parse_ingredients(ingredients),
            "procedures": _parse_procedures(procedures),
            "supplies": _parse_supplies(supplies),
            "base_servings": max(1, base_servings),
        }
        recipe = create_recipe(data)
        await interaction.followup.send(f"Recipe **{recipe.name}** created successfully.")
    except Exception as e:
        logger.exception("add_recipe failed")
        await interaction.followup.send(f"Error: {e}", ephemeral=True)


@bot.tree.command(
    name="update_recipe",
    description="Update a recipe using natural language (e.g. change cost or quantity).",
)
@app_commands.describe(
    name="Recipe name",
    input="What to change, e.g. 'Update avocado cost to $2 and increase quantity by 20%'",
)
async def update_recipe_cmd(interaction: discord.Interaction, name: str, input: str):
    role = get_user_role(str(interaction.user.id))
    if not can_edit_recipes(role):
        await interaction.response.send_message(
            "You don't have permission to update recipes. (Need role: sushi_chef or admin.)",
            ephemeral=True,
        )
        return

    await interaction.response.defer()
    recipe = get_recipe(name)
    if not recipe:
        await interaction.followup.send(f"Recipe not found: **{name}**.")
        return

    try:
        updates = ai_parse_update(recipe, input.strip())
        if not updates:
            await interaction.followup.send("No changes parsed from your input. Try being more specific.")
            return
        updated = update_recipe(name, updates)
        if updated:
            await interaction.followup.send(f"Recipe **{name}** updated with: {list(updates.keys())}.")
        else:
            await interaction.followup.send("Update failed.")
    except Exception as e:
        logger.exception("update_recipe failed")
        await interaction.followup.send(f"Error: {e}", ephemeral=True)


@bot.tree.command(
    name="refine_quantities",
    description="Scale quantities for guest count; optional feedback for AI optimization.",
)
@app_commands.describe(
    name="Recipe name",
    guests="Number of guests",
    feedback="Optional: e.g. 'Reduce rice waste by 10%' or 'Minimize cost under $100'",
)
async def refine_quantities(
    interaction: discord.Interaction,
    name: str,
    guests: int,
    feedback: str = "",
):
    if guests < 1:
        await interaction.response.send_message("Guests must be at least 1.", ephemeral=True)
        return

    await interaction.response.defer()
    recipe = get_recipe(name)
    if not recipe:
        await interaction.followup.send(f"Recipe not found: **{name}**.")
        return

    try:
        refined = ai_refine_quantities(recipe, guests, feedback.strip())
        lines = [
            f"**{name}** – scaled for **{guests}** guests (factor {refined['scale_factor']:.2f})",
            "",
            "**Ingredients**",
        ]
        for item in refined.get("ingredients", []):
            lines.append(f"- {item.get('item')}: {item.get('quantity')} {item.get('unit', '')}")
        lines.append("")
        lines.append("**Supplies**")
        for item in refined.get("supplies", []):
            lines.append(f"- {item.get('item')}: {item.get('quantity')}")
        lines.append("")
        lines.append(f"**Estimated cost:** ${refined.get('total_cost', 0):.2f}")
        await interaction.followup.send("\n".join(lines))
    except ValueError as e:
        await interaction.followup.send(str(e), ephemeral=True)
    except Exception as e:
        logger.exception("refine_quantities failed")
        await interaction.followup.send(f"Error: {e}", ephemeral=True)


@bot.tree.command(
    name="get_prep_list",
    description="Get prep list for a recipe and guest count (filtered by your role).",
)
@app_commands.describe(name="Recipe name", guests="Number of guests")
async def get_prep_list_cmd(interaction: discord.Interaction, name: str, guests: int):
    if guests < 1:
        await interaction.response.send_message("Guests must be at least 1.", ephemeral=True)
        return

    await interaction.response.defer()
    role = get_user_role(str(interaction.user.id))
    prep_list = generate_prep_list(name, guests)
    assigned = assign_tasks(prep_list, role)
    if len(assigned) > 1900:
        await interaction.followup.send(assigned[:1900] + "\n… (truncated)")
    else:
        await interaction.followup.send(assigned)


@bot.tree.command(
    name="set_role",
    description="Set a staff member's role (admin only).",
)
@app_commands.describe(
    discord_id="Discord user ID (right-click user → Copy ID)",
    role="Role: sushi_chef, prep_cook, general, or admin",
)
async def set_role_cmd(
    interaction: discord.Interaction, discord_id: str, role: str
):
    if get_user_role(str(interaction.user.id)) != "admin":
        await interaction.response.send_message(
            "Only admin can set roles.", ephemeral=True
        )
        return
    role = role.lower().strip()
    if role not in ("sushi_chef", "prep_cook", "general", "admin"):
        await interaction.response.send_message(
            "Invalid role. Use: sushi_chef, prep_cook, general, admin.",
            ephemeral=True,
        )
        return
    from user_service import set_user_role
    set_user_role(discord_id, role)
    await interaction.response.send_message(
        f"Set role **{role}** for user {discord_id}.", ephemeral=True
    )


@bot.tree.command(name="list_recipes", description="List all recipe names.")
async def list_recipes_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    recipes = list_recipes()
    if not recipes:
        await interaction.followup.send("No recipes yet. Use /add_recipe to create one.", ephemeral=True)
        return
    names = ", ".join(f"**{r.name}**" for r in recipes)
    await interaction.followup.send(f"Recipes: {names}", ephemeral=True)


def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set in .env")
        return
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
