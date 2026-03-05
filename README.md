# Sushi Logistics Bot & Dashboard

**Production tool for a sushi chef catering business**  
Manages daily orders → prep quantities → staff tasks → packing → COGS.  

**Main communication = Discord** (kitchen mobile-first)  
**Chef-only cockpit = Next.js dashboard** (reports, editing, history)

## Architecture (Headless)
- **Brain**: Supabase (Postgres + Storage + Realtime + Edge Functions)
- **Primary UI**: Discord Bot (Node.js + discord.js)
- **Secondary UI**: Next.js 15 dashboard (Vercel)
- **AI Clerk**: Gemini 2.0 Flash (invoice parsing)
- **Hosting**: Railway (bot) + Vercel (dashboard)

## Project Phases (Use in order)

**Phase 1 – Daily Order → Instant Prep** (Launch first weekend)  
Chef runs `/order-today` → bot posts prep lists in 3 channels instantly.

**Phase 2 – Calendar + Multi-Day Consolidation**  
`/event-add` creates threads, `/prep-for-date` aggregates everything.

**Phase 3 – COGS & Labor Tracking**  
Real ingredient costs + labor minutes per order.

**Phase 4 – Smart Packing System**  
Per-order packing slips, checklists, labels.

## Quick Start (After Supabase setup)

1. Run the schema in Supabase SQL Editor (see `SCHEMA.md`).
2. Create channels: `#chef-view`, `#prep-view`, `#pack-view` in your Discord server.
3. Bot:
   ```bash
   npm install
   cp .env.example .env
   # Fill DISCORD_*, SUPABASE_*, channel IDs
   npm run deploy:commands   # Register slash commands
   npm run dev
   ```
4. Dashboard:
   ```bash
   cd dashboard
   npm install
   cp .env.example .env.local
   # Fill NEXT_PUBLIC_SUPABASE_*
   npm run dev
   ```
   Open http://localhost:3001/today