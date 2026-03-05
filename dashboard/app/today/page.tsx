/**
 * /today — Read-only, realtime view of daily orders.
 * Phase 1: Chef / Prep / Pack summary.
 */

import { TodayClient } from './TodayClient';
import { getTodayOrders } from '@/lib/today';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function TodayPage() {
  const orders = await getTodayOrders();
  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-5xl">
        <h1 className="mb-8 font-mono text-2xl font-bold tracking-tight text-zinc-100">
          Today&apos;s Orders
        </h1>
        <TodayClient initialOrders={orders} />
      </div>
    </main>
  );
}
