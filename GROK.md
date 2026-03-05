# Grok Project Memory – Sushi Logistics Bot (Always read this first)

Last updated: 2026-03-04

This is the single source of truth for Grok. When I say "implement Phase X" or "update the bot", always:
1. Read the current files via GitHub (or ask me to paste latest if needed)
2. Base every change on SCHEMA.md + PHASES.md + existing code
3. Never invent new tables or commands — extend what exists
4. Keep Discord as primary UI, dashboard as chef-only cockpit
5. Output clean, production-ready TypeScript + Next.js code

Current Phase: Phase 1 (Daily Order → Instant Prep)
- We have /order-today modal working
- 3 staff embeds (Chef / Prep / Pack)
- Basic /today dashboard page
- Next step: Finish Phase 1 deployment, then move to Phase 2

Project Rules (never break these):
- All secrets in .env (never commit)
- Bot uses Supabase service_role only
- Dashboard uses Supabase Auth (email/password for chef only)
- Every feature must output to Discord channels first
- Use @references in Cursor prompts

When I ask for code:
- Give me only the files I need to create/edit
- Include exact Cursor Composer prompt I should use next
- Tell me the git commit message

GitHub repo: https://github.com/YOUR-USERNAME/sushi-logistics-bot (replace with real link)

Current status: Phase 1 is 80% done. Ready for deployment to Railway + Vercel.