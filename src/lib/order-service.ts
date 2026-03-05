/**
 * Daily order operations. Fetches orders and recipes for prep calculations.
 */

import { supabase } from './supabase.js';
import type { DailyOrderWithRecipe, RecipeWithItems } from '../types/index.js';

/** Fetch all recipes for dropdown/select */
export async function getRecipes(): Promise<{ id: string; name: string }[]> {
  const { data, error } = await supabase
    .from('recipes')
    .select('id, name')
    .order('name');
  if (error) throw error;
  return data ?? [];
}

/** Create a daily order */
export async function createOrder(params: {
  recipe_id: string;
  servings: number;
  notes?: string | null;
  order_date?: string;
}) {
  const { data, error } = await supabase
    .from('daily_orders')
    .insert({
      recipe_id: params.recipe_id,
      servings: params.servings,
      notes: params.notes ?? null,
      order_date: params.order_date ?? new Date().toISOString().slice(0, 10),
    })
    .select()
    .single();
  if (error) throw error;
  return data;
}

/** Fetch today's orders with full recipe + ingredient details for prep */
export async function getTodayOrdersWithDetails(
  orderDate?: string
): Promise<DailyOrderWithRecipe[]> {
  const date = orderDate ?? new Date().toISOString().slice(0, 10);
  const { data: orders, error } = await supabase
    .from('daily_orders')
    .select(
      `
      id,
      order_date,
      recipe_id,
      servings,
      notes,
      created_at,
      recipe:recipes (
        id,
        name,
        yield_servings,
        procedure,
        labor_minutes_per_100_servings
      )
    `
    )
    .eq('order_date', date)
    .order('created_at', { ascending: true });

  if (error) throw error;
  if (!orders?.length) return [];

  // Fetch recipe items (ingredients) for each unique recipe
  const recipeIds = [...new Set(orders.map((o) => o.recipe_id))];
  const { data: itemsData } = await supabase
    .from('recipe_items')
    .select(
      `
      recipe_id,
      quantity,
      ingredient:ingredients (
        id,
        name,
        unit,
        cost_per_unit,
        current_stock,
        low_stock_threshold
      )
    `
    )
    .in('recipe_id', recipeIds);

  type ItemRow = {
    recipe_id: string;
    quantity: number;
    ingredient: { id: string; name: string; unit: string; cost_per_unit: number | null; current_stock: number; low_stock_threshold: number };
  };

  const itemsByRecipe = new Map<string, ItemRow[]>();
  for (const row of (itemsData ?? []) as unknown as ItemRow[]) {
    const list = itemsByRecipe.get(row.recipe_id) ?? [];
    list.push(row);
    itemsByRecipe.set(row.recipe_id, list);
  }

  return orders.map((o) => {
    const recipe = (Array.isArray(o.recipe) ? o.recipe[0] : o.recipe) as DailyOrderWithRecipe['recipe'];
    const items = itemsByRecipe.get(o.recipe_id) ?? [];
    return {
      ...o,
      recipe: {
        ...recipe,
        recipe_items: items.map((i) => {
          const ing = Array.isArray(i.ingredient) ? i.ingredient[0] : i.ingredient;
          return {
            recipe_id: i.recipe_id,
            ingredient_id: ing.id,
            quantity: i.quantity,
            ingredient: ing,
          };
        }),
      } as RecipeWithItems,
    } as DailyOrderWithRecipe;
  });
}
