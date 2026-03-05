/**
 * Aggregates orders into Chef / Prep / Pack views.
 * - Chef: procedures by role, total servings per recipe
 * - Prep: scaled ingredient quantities
 * - Pack: menu summary, order counts
 */

import type { DailyOrderWithRecipe, RecipeWithItems } from '../types/index.js';

export interface ChefViewItem {
  recipeName: string;
  totalServings: number;
  procedures: { step: string; role: string }[];
}

export interface PrepViewItem {
  ingredientName: string;
  unit: string;
  totalQuantity: number;
  lowStock?: boolean;
}

export interface PackViewItem {
  recipeName: string;
  totalServings: number;
  orderCount: number;
  notes: string[];
}

/** Build Chef view: procedures grouped by recipe */
export function buildChefView(orders: DailyOrderWithRecipe[]): ChefViewItem[] {
  const byRecipe = new Map<string, ChefViewItem>();
  for (const order of orders) {
    const recipe = order.recipe as RecipeWithItems;
    const existing = byRecipe.get(recipe.id);
    const procedures =
      Array.isArray(recipe.procedure) && recipe.procedure.length
        ? recipe.procedure.map((p: { step: string; role: string }) => ({
            step: p.step,
            role: p.role,
          }))
        : [{ step: 'See recipe card', role: 'General' }];

    if (existing) {
      existing.totalServings += order.servings;
    } else {
      byRecipe.set(recipe.id, {
        recipeName: recipe.name,
        totalServings: order.servings,
        procedures,
      });
    }
  }
  return Array.from(byRecipe.values());
}

/** Build Prep view: aggregated ingredient quantities */
export function buildPrepView(orders: DailyOrderWithRecipe[]): PrepViewItem[] {
  const byIngredient = new Map<string, PrepViewItem>();
  for (const order of orders) {
    const recipe = order.recipe as RecipeWithItems;
    const multiplier = order.servings / recipe.yield_servings;
    for (const item of recipe.recipe_items ?? []) {
      const ing = item.ingredient as { name: string; unit: string; low_stock_threshold?: number; current_stock?: number };
      const key = ing.name;
      const qty = item.quantity * multiplier;
      const existing = byIngredient.get(key);
      if (existing) {
        existing.totalQuantity += qty;
      } else {
        byIngredient.set(key, {
          ingredientName: ing.name,
          unit: ing.unit,
          totalQuantity: qty,
          lowStock:
            ing.low_stock_threshold != null &&
            (ing.current_stock ?? 0) < ing.low_stock_threshold,
        });
      }
    }
  }
  return Array.from(byIngredient.values()).sort((a, b) =>
    a.ingredientName.localeCompare(b.ingredientName)
  );
}

/** Build Pack view: menu summary per recipe */
export function buildPackView(orders: DailyOrderWithRecipe[]): PackViewItem[] {
  const byRecipe = new Map<string, PackViewItem>();
  for (const order of orders) {
    const recipe = order.recipe as RecipeWithItems;
    const existing = byRecipe.get(recipe.id);
    const notes = order.notes ? [order.notes] : [];
    if (existing) {
      existing.totalServings += order.servings;
      existing.orderCount += 1;
      if (order.notes) existing.notes.push(order.notes);
    } else {
      byRecipe.set(recipe.id, {
        recipeName: recipe.name,
        totalServings: order.servings,
        orderCount: 1,
        notes,
      });
    }
  }
  return Array.from(byRecipe.values());
}
