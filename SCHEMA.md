# Full Supabase Schema (Run in SQL Editor)

-- Run this entire file first

create extension if not exists "uuid-ossp";

-- Ingredients
create table ingredients (
  id uuid primary key default uuid_generate_v4(),
  name text unique not null,
  unit text not null,
  cost_per_unit numeric(10,4),
  current_stock numeric(10,2) default 0,
  low_stock_threshold numeric(10,2) default 5,
  last_updated_at timestamptz default now()
);

-- Recipes
create table recipes (
  id uuid primary key default uuid_generate_v4(),
  name text unique not null,
  yield_servings int not null,
  procedure jsonb, -- array of {step: string, role: 'Chef'|'Prep'|'General'}
  labor_minutes_per_100_servings int default 60
);

create table recipe_items (
  recipe_id uuid references recipes on delete cascade,
  ingredient_id uuid references ingredients on delete cascade,
  quantity numeric(10,3) not null,
  primary key (recipe_id, ingredient_id)
);

-- Supplies (packing)
create table supplies (
  id uuid primary key default uuid_generate_v4(),
  name text unique not null,
  unit text not null,
  qty_per_50_servings int not null,
  cost_per_unit numeric(10,4)
);

-- Daily orders (Phase 1)
create table daily_orders (
  id uuid primary key default uuid_generate_v4(),
  order_date date not null default current_date,
  recipe_id uuid references recipes,
  servings numeric(10,2) not null,
  notes text,
  created_at timestamptz default now()
);

-- Events (Phase 2+)
create table events (
  id uuid primary key default uuid_generate_v4(),
  event_date date not null,
  client_name text,
  headcount int not null,
  thread_id text, -- Discord thread ID
  status text default 'upcoming',
  notes text
);

create table event_recipes (
  event_id uuid references events on delete cascade,
  recipe_id uuid references recipes,
  servings_multiplier numeric(10,2) default 1.0,
  primary key (event_id, recipe_id)
);

-- Invoices (AI clerk)
create table invoices (
  id uuid primary key default uuid_generate_v4(),
  image_url text,
  vendor text,
  invoice_date date,
  parsed_items jsonb,
  processed_at timestamptz default now()
);

-- Packing (Phase 4)
create table packing_lists (
  id uuid primary key default uuid_generate_v4(),
  event_id uuid references events,
  order_date date,
  items jsonb, -- menu + supplies
  generated_at timestamptz default now()
);

-- Enable realtime on these tables
alter publication supabase_realtime add table daily_orders, events, ingredients;

-- RLS: Dashboard (anon) can read Phase 1 tables. Bot uses service_role (bypasses RLS).
alter table daily_orders enable row level security;
alter table recipes enable row level security;
alter table recipe_items enable row level security;
alter table ingredients enable row level security;

create policy "Allow anon read daily_orders" on daily_orders for select to anon using (true);
create policy "Allow anon read recipes" on recipes for select to anon using (true);
create policy "Allow anon read recipe_items" on recipe_items for select to anon using (true);
create policy "Allow anon read ingredients" on ingredients for select to anon using (true);