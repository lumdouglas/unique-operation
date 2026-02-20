"""
Seed the database with sample sushi/poke recipes.
Run: python seed_recipes.py
"""
from recipe_service import create_recipe, get_recipe, ensure_db

SAMPLE_RECIPES = [
    {
        "name": "California Roll",
        "ingredients": [
            {"item": "sushi rice", "quantity": 2000, "unit": "g", "cost_per_unit": 0.004},
            {"item": "crab stick", "quantity": 500, "unit": "g", "cost_per_unit": 0.02},
            {"item": "avocado", "quantity": 5, "unit": "each", "cost_per_unit": 1.50},
            {"item": "cucumber", "quantity": 2, "unit": "each", "cost_per_unit": 0.80},
            {"item": "nori", "quantity": 20, "unit": "sheets", "cost_per_unit": 0.25},
        ],
        "procedures": [
            "Cook and season sushi rice; cool to room temp.",
            "Slice cucumber and avocado into strips.",
            "Place nori on mat, spread rice, add crab, avocado, cucumber, roll tightly.",
            "Slice into 8 pieces per roll.",
        ],
        "supplies": [{"item": "tray", "quantity": 10}, {"item": "lids", "quantity": 50}],
        "base_servings": 50,
    },
    {
        "name": "Spicy Tuna Roll",
        "ingredients": [
            {"item": "sushi rice", "quantity": 2000, "unit": "g", "cost_per_unit": 0.004},
            {"item": "tuna", "quantity": 800, "unit": "g", "cost_per_unit": 0.03},
            {"item": "sriracha", "quantity": 100, "unit": "ml", "cost_per_unit": 0.02},
            {"item": "mayo", "quantity": 150, "unit": "g", "cost_per_unit": 0.01},
            {"item": "nori", "quantity": 20, "unit": "sheets", "cost_per_unit": 0.25},
        ],
        "procedures": [
            "Dice tuna, mix with sriracha and mayo.",
            "Spread rice on nori, add spicy tuna, roll and slice.",
        ],
        "supplies": [{"item": "tray", "quantity": 10}, {"item": "lids", "quantity": 50}],
        "base_servings": 50,
    },
    {
        "name": "Poke Bowl",
        "ingredients": [
            {"item": "sushi rice", "quantity": 2500, "unit": "g", "cost_per_unit": 0.004},
            {"item": "ahi tuna", "quantity": 1200, "unit": "g", "cost_per_unit": 0.035},
            {"item": "soy sauce", "quantity": 200, "unit": "ml", "cost_per_unit": 0.015},
            {"item": "sesame oil", "quantity": 50, "unit": "ml", "cost_per_unit": 0.05},
            {"item": "green onion", "quantity": 3, "unit": "bunch", "cost_per_unit": 1.00},
            {"item": "cucumber", "quantity": 4, "unit": "each", "cost_per_unit": 0.80},
            {"item": "edamame", "quantity": 500, "unit": "g", "cost_per_unit": 0.02},
        ],
        "procedures": [
            "Cook rice and portion into bowls.",
            "Cube tuna, toss with soy and sesame oil.",
            "Chop cucumber and green onion; top bowls with tuna, veggies, edamame.",
        ],
        "supplies": [{"item": "bowl", "quantity": 50}, {"item": "lid", "quantity": 50}],
        "base_servings": 50,
    },
    {
        "name": "Salmon Nigiri",
        "ingredients": [
            {"item": "sushi rice", "quantity": 1800, "unit": "g", "cost_per_unit": 0.004},
            {"item": "salmon", "quantity": 1000, "unit": "g", "cost_per_unit": 0.028},
            {"item": "rice vinegar", "quantity": 80, "unit": "ml", "cost_per_unit": 0.02},
        ],
        "procedures": [
            "Season rice with vinegar, form small oblong portions.",
            "Slice salmon; place slice on each rice portion.",
        ],
        "supplies": [{"item": "tray", "quantity": 15}, {"item": "lids", "quantity": 50}],
        "base_servings": 50,
    },
    {
        "name": "Vegetable Roll",
        "ingredients": [
            {"item": "sushi rice", "quantity": 1500, "unit": "g", "cost_per_unit": 0.004},
            {"item": "cucumber", "quantity": 3, "unit": "each", "cost_per_unit": 0.80},
            {"item": "carrot", "quantity": 4, "unit": "each", "cost_per_unit": 0.50},
            {"item": "avocado", "quantity": 4, "unit": "each", "cost_per_unit": 1.50},
            {"item": "nori", "quantity": 15, "unit": "sheets", "cost_per_unit": 0.25},
        ],
        "procedures": [
            "Julienne cucumber, carrot; slice avocado.",
            "Roll rice and veggies in nori; slice.",
        ],
        "supplies": [{"item": "tray", "quantity": 8}, {"item": "lids", "quantity": 40}],
        "base_servings": 40,
    },
]


def main():
    ensure_db()
    for data in SAMPLE_RECIPES:
        existing = get_recipe(data["name"])
        if existing:
            print(f"Skip (exists): {data['name']}")
            continue
        create_recipe(data)
        print(f"Created: {data['name']}")
    print("Seed done.")


if __name__ == "__main__":
    main()
