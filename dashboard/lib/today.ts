/**
 * Fetch today's orders with recipe + ingredient details.
 * Used by server components and realtime subscription.
 */

import { supabase } from './supabase';

export interface TodayOrder {
  id: string;
  order_date: string;
  recipe_id: string;
  servings: number;
  notes: string | null;
  created_at: string;
  recipe: {
    id: string;
    name: string;
    yield_servings: number;
    procedure: { step: string; role: string }[] | null;
    recipe_items: {
      quantity: number;
      ingredient: { name: string; unit: string };
    }[];
  };
}

export async function getTodayOrders(
  date?: string
): Promise<TodayOrder[]> {
  const orderDate = date ?? new Date().toISOString().slice(0, 10);
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
        recipe_items (
          quantity,
          ingredient:ingredients (name, unit)
        )
      )
    `
    )
    .eq('order_date', orderDate)
    .order('created_at', { ascending: true });

  if (error) throw error;
  return (orders ?? []) as unknown as TodayOrder[];
}
