
---

### 3. `PHASES.md`

```markdown
# Implementation Phases

## Phase 1 – Daily Order → Instant Prep (Priority – build first)
- Tables needed: recipes, recipe_items, ingredients, daily_orders
- Discord commands:
  - /order-today (modal: recipe select + servings + notes)
  - /prep-today
- Output: 3 Discord embeds posted to #chef-view, #prep-view, #pack-view
- Dashboard: single page /today (read-only, realtime)

## Phase 2 – Calendar Thread + Multi-Day
- New tables: events, event_recipes
- Commands:
  - /event-add (creates Discord thread + stores thread_id)
  - /prep-for-date YYYY-MM-DD
- Dashboard: /calendar page with weekly view + "Send to Discord" button

## Phase 3 – COGS & Labor
- Add to recipes: labor_minutes_per_100_servings
- Add supplies table
- Invoice parsing now updates ingredient costs
- Dashboard: /cogs page with table + charts (food cost %, margin)

## Phase 4 – Packing System
- New table: packing_lists
- After prep, button "Generate Packing"
- Creates per-order thread with checklist + printable PDF slip
- Supplies auto-calculated (bowls, lids, chopsticks, etc.)

Build order recommendation:
1. Supabase schema (full from SCHEMA.md)
2. Phase 1 bot + dashboard
3. Deploy bot to Railway
4. Deploy dashboard to Vercel
5. Then Phase 2, 3, 4 one weekend at a time