'use client';

/**
 * Client component with Realtime subscription.
 * Re-fetches when daily_orders changes.
 */

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { TodayOrder } from '@/lib/today';

interface TodayClientProps {
  initialOrders: TodayOrder[];
}

function buildChefView(orders: TodayOrder[]) {
  const byRecipe = new Map<
    string,
    { name: string; servings: number; procedures: { step: string; role: string }[] }
  >();
  for (const o of orders) {
    const r = o.recipe;
    const procedures =
      Array.isArray(r.procedure) && r.procedure.length
        ? r.procedure
        : [{ step: 'See recipe card', role: 'General' }];
    const existing = byRecipe.get(r.id);
    if (existing) {
      existing.servings += o.servings;
    } else {
      byRecipe.set(r.id, {
        name: r.name,
        servings: o.servings,
        procedures,
      });
    }
  }
  return Array.from(byRecipe.values());
}

function buildPrepView(orders: TodayOrder[]) {
  const byIng = new Map<string, { name: string; unit: string; qty: number }>();
  for (const o of orders) {
    const mult = o.servings / o.recipe.yield_servings;
    for (const item of o.recipe.recipe_items ?? []) {
      const ing = item.ingredient as { name: string; unit: string };
      const key = ing.name;
      const qty = item.quantity * mult;
      const existing = byIng.get(key);
      if (existing) {
        existing.qty += qty;
      } else {
        byIng.set(key, { name: ing.name, unit: ing.unit, qty });
      }
    }
  }
  return Array.from(byIng.values()).sort((a, b) =>
    a.name.localeCompare(b.name)
  );
}

function buildPackView(orders: TodayOrder[]) {
  const byRecipe = new Map<
    string,
    { name: string; servings: number; count: number; notes: string[] }
  >();
  for (const o of orders) {
    const r = o.recipe;
    const existing = byRecipe.get(r.id);
    if (existing) {
      existing.servings += o.servings;
      existing.count += 1;
      if (o.notes) existing.notes.push(o.notes);
    } else {
      byRecipe.set(r.id, {
        name: r.name,
        servings: o.servings,
        count: 1,
        notes: o.notes ? [o.notes] : [],
      });
    }
  }
  return Array.from(byRecipe.values());
}

async function fetchOrders(): Promise<TodayOrder[]> {
  const date = new Date().toISOString().slice(0, 10);
  const { data, error } = await supabase
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
    .eq('order_date', date)
    .order('created_at', { ascending: true });
  if (error) throw error;
  return (data ?? []) as unknown as TodayOrder[];
}

export function TodayClient({ initialOrders }: TodayClientProps) {
  const [orders, setOrders] = useState<TodayOrder[]>(initialOrders);

  useEffect(() => {
    const channel = supabase
      .channel('daily_orders_changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'daily_orders' },
        () => {
          fetchOrders().then(setOrders);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  const chefView = buildChefView(orders);
  const prepView = buildPrepView(orders);
  const packView = buildPackView(orders);
  const date = new Date().toISOString().slice(0, 10);

  return (
    <div className="grid gap-8 md:grid-cols-3">
      {/* Chef View */}
      <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
        <h2 className="mb-4 font-mono text-sm font-semibold uppercase tracking-wider text-red-400">
          Chef View
        </h2>
        {chefView.length === 0 ? (
          <p className="text-sm text-zinc-500">No orders for today.</p>
        ) : (
          <ul className="space-y-4">
            {chefView.map((item) => (
              <li key={item.name}>
                <p className="font-medium text-zinc-200">
                  {item.name} — {item.servings} servings
                </p>
                <ul className="mt-2 space-y-1 text-sm text-zinc-400">
                  {item.procedures.map((p, i) => (
                    <li key={i}>
                      [{p.role}] {p.step}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Prep View */}
      <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
        <h2 className="mb-4 font-mono text-sm font-semibold uppercase tracking-wider text-blue-400">
          Prep View
        </h2>
        {prepView.length === 0 ? (
          <p className="text-sm text-zinc-500">No prep needed.</p>
        ) : (
          <ul className="space-y-2">
            {prepView.map((item) => (
              <li key={item.name} className="text-sm text-zinc-300">
                <span className="font-medium">{item.name}</span> —{' '}
                {formatQty(item.qty)} {item.unit}
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Pack View */}
      <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
        <h2 className="mb-4 font-mono text-sm font-semibold uppercase tracking-wider text-green-400">
          Pack View
        </h2>
        {packView.length === 0 ? (
          <p className="text-sm text-zinc-500">No orders to pack.</p>
        ) : (
          <ul className="space-y-3">
            {packView.map((item) => (
              <li key={item.name}>
                <p className="font-medium text-zinc-200">
                  {item.name} — {item.servings} servings ({item.count} order
                  {item.count > 1 ? 's' : ''})
                </p>
                {item.notes.length > 0 && (
                  <ul className="mt-1 text-sm text-zinc-500">
                    {item.notes.map((n, i) => (
                      <li key={i}>_{n}_</li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function formatQty(n: number): string {
  if (Number.isInteger(n)) return String(n);
  return n.toFixed(2).replace(/\.?0+$/, '');
}
