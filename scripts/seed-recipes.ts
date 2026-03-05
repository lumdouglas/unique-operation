/**
 * Seed sample recipes and ingredients for Phase 1 testing.
 * Run: npx tsx scripts/seed-recipes.ts
 * Requires: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY in env
 */

import { createClient } from '@supabase/supabase-js';

const url = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !key) {
  console.error('Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

const supabase = createClient(url, key);

async function seed() {
  // Ingredients
  const { data: ingredients, error: ingErr } = await supabase
    .from('ingredients')
    .upsert(
      [
        { name: 'Sushi rice', unit: 'cups', cost_per_unit: 0.5 },
        { name: 'Nori', unit: 'sheets', cost_per_unit: 0.15 },
        { name: 'Tuna', unit: 'lb', cost_per_unit: 12 },
        { name: 'Salmon', unit: 'lb', cost_per_unit: 14 },
        { name: 'Cucumber', unit: 'each', cost_per_unit: 0.5 },
        { name: 'Avocado', unit: 'each', cost_per_unit: 1.2 },
        { name: 'Soy sauce', unit: 'oz', cost_per_unit: 0.1 },
        { name: 'Sriracha', unit: 'oz', cost_per_unit: 0.08 },
      ],
      { onConflict: 'name' }
    )
    .select('id, name');

  if (ingErr) {
    console.error('Ingredients error:', ingErr);
    process.exit(1);
  }

  const byName = new Map((ingredients ?? []).map((i) => [i.name, i.id]));

  // Recipes
  const { data: recipes, error: recErr } = await supabase
    .from('recipes')
    .upsert(
      [
        {
          name: 'Spicy Tuna Roll',
          yield_servings: 50,
          procedure: [
            { step: 'Dice tuna, mix with sriracha mayo', role: 'Chef' },
            { step: 'Roll with rice and nori', role: 'Prep' },
            { step: 'Slice and portion', role: 'Pack' },
          ],
        },
        {
          name: 'Salmon Nigiri',
          yield_servings: 40,
          procedure: [
            { step: 'Slice salmon for nigiri', role: 'Chef' },
            { step: 'Form rice balls, top with salmon', role: 'Prep' },
            { step: 'Arrange on tray', role: 'Pack' },
          ],
        },
        {
          name: 'California Roll',
          yield_servings: 48,
          procedure: [
            { step: 'Prep crab mix', role: 'Chef' },
            { step: 'Roll cucumber, avocado, crab', role: 'Prep' },
            { step: 'Slice and pack', role: 'Pack' },
          ],
        },
      ],
      { onConflict: 'name' }
    )
    .select('id, name');

  if (recErr) {
    console.error('Recipes error:', recErr);
    process.exit(1);
  }

  const recipeByName = new Map((recipes ?? []).map((r) => [r.name, r.id]));

  // Recipe items
  const recipeItems = [
    { recipe: 'Spicy Tuna Roll', ingredient: 'Tuna', quantity: 2 },
    { recipe: 'Spicy Tuna Roll', ingredient: 'Sushi rice', quantity: 8 },
    { recipe: 'Spicy Tuna Roll', ingredient: 'Nori', quantity: 25 },
    { recipe: 'Spicy Tuna Roll', ingredient: 'Sriracha', quantity: 4 },
    { recipe: 'Salmon Nigiri', ingredient: 'Salmon', quantity: 1.5 },
    { recipe: 'Salmon Nigiri', ingredient: 'Sushi rice', quantity: 6 },
    { recipe: 'California Roll', ingredient: 'Sushi rice', quantity: 6 },
    { recipe: 'California Roll', ingredient: 'Nori', quantity: 24 },
    { recipe: 'California Roll', ingredient: 'Cucumber', quantity: 4 },
    { recipe: 'California Roll', ingredient: 'Avocado', quantity: 6 },
  ];

  for (const ri of recipeItems) {
    const recipeId = recipeByName.get(ri.recipe);
    const ingredientId = byName.get(ri.ingredient);
    if (recipeId && ingredientId) {
      await supabase.from('recipe_items').upsert(
        { recipe_id: recipeId, ingredient_id: ingredientId, quantity: ri.quantity },
        { onConflict: 'recipe_id,ingredient_id' }
      );
    }
  }

  console.log('Seeded', ingredients?.length ?? 0, 'ingredients,', recipes?.length ?? 0, 'recipes');
}

seed().catch(console.error);
