/**
 * Type definitions matching SCHEMA.md
 */

export interface Ingredient {
  id: string;
  name: string;
  unit: string;
  cost_per_unit: number | null;
  current_stock: number;
  low_stock_threshold: number;
  last_updated_at: string;
}

export interface Recipe {
  id: string;
  name: string;
  yield_servings: number;
  procedure: ProcedureStep[] | null;
  labor_minutes_per_100_servings: number;
}

export interface ProcedureStep {
  step: string;
  role: 'Chef' | 'Prep' | 'General';
}

export interface RecipeItem {
  recipe_id: string;
  ingredient_id: string;
  quantity: number;
}

export interface DailyOrder {
  id: string;
  order_date: string;
  recipe_id: string;
  servings: number;
  notes: string | null;
  created_at: string;
}

/** Recipe with joined ingredient details for prep calculations */
export interface RecipeWithItems extends Recipe {
  recipe_items: (RecipeItem & {
    ingredient: Ingredient;
  })[];
}

/** Daily order with recipe details */
export interface DailyOrderWithRecipe extends DailyOrder {
  recipe: Recipe;
}
