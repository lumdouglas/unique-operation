# A-Unique-Operation

Sushi catering operation automation.

## Sushi Catering Management System

Centralized recipe management for sushi, poke bowls, and event prep. Uses a local SQLite database, optional AI (Google Gemini) for updates and quantity refinements, and a **Discord bot** for daily staff commands.

## Features

- **Recipe CRUD**: Create, read, update, delete recipes (ingredients, procedures, supplies, base servings).
- **AI updates**: Natural language updates (e.g. “Update avocado cost to $2 and increase quantity 20%”) via Gemini.
- **Quantity refinements**: Scale for event size; optional AI optimization from feedback (e.g. reduce waste, cap cost).
- **Prep lists**: Generate daily prep lists; filter by staff role (sushi_chef, prep_cook, general).
- **Role-based access**: Only `sushi_chef` or `admin` can add/update recipes; enforced in the bot.

## Tech Stack

- **Python 3.x**
- **SQLAlchemy** (SQLite; can switch to PostgreSQL via `DATABASE_URL`)
- **discord.py** (slash commands)
- **Google Gemini API** (optional; falls back to simple scaling if missing)
- **python-dotenv** for env vars

## Setup

1. **Clone / create project folder**

   ```bash
   cd "Sushi Catering"
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment**

   Copy `.env.example` to `.env` and set:

   - `DISCORD_TOKEN` – from [Discord Developer Portal](https://discord.com/developers/applications) (Bot token).
   - `GEMINI_API_KEY` – from [Google AI Studio](https://aistudio.google.com/apikey) (optional; needed for AI parse/refine).

3. **Database and seed data**

   ```bash
   python seed_recipes.py
   ```

4. **Run the bot**

   ```bash
   python bot.py
   ```

   Invite the bot to your server with scope `applications.commands` and `bot`. Slash commands will appear after sync.

5. **Make yourself admin (first time only)**

   In a terminal (with venv active):

   ```bash
   python set_admin.py YOUR_DISCORD_USER_ID
   ```

   To get your Discord ID: enable Developer Mode in Discord (Settings → App Settings → Advanced), then right‑click your name and choose “Copy User ID”.

---

## Owner guide: first day vs day to day

### First day (one-time setup)

1. **Install and configure**
   - Open the project folder in a terminal.
   - Create and activate the venv, install deps:  
     `python3 -m venv venv` → `source venv/bin/activate` (or `venv\Scripts\activate` on Windows) → `pip install -r requirements.txt`.
   - Copy `.env.example` to `.env`. Add your **DISCORD_TOKEN** (Discord Developer Portal → your app → Bot → Reset/Copy Token). Optionally add **GEMINI_API_KEY** (from [Google AI Studio](https://aistudio.google.com/apikey)) for natural-language recipe updates and smarter scaling.

2. **Create the database and sample recipes**
   - Run: `python seed_recipes.py`  
   - This creates `sushi.db` and adds 5 sample recipes (California Roll, Spicy Tuna Roll, Poke Bowl, Salmon Nigiri, Vegetable Roll).

3. **Invite the bot to your Discord server**
   - In the Discord Developer Portal: your application → OAuth2 → URL Generator. Select scopes **bot** and **applications.commands**, then copy the URL and open it to add the bot to your server.

4. **Start the bot**
   - Run: `python bot.py`  
   - Keep this terminal (or process) running so the bot stays online. For 24/7 use, run it on a server or a host like Replit/Heroku.

5. **Set yourself as admin**
   - Get your Discord User ID (right‑click your name → Copy User ID; Developer Mode must be on).
   - Run: `python set_admin.py YOUR_DISCORD_ID`  
   - You can now use `/set_role` in Discord to assign roles to staff.

6. **Assign staff roles (optional)**
   - In Discord, use `/set_role` with a staff member’s Discord ID and role: `sushi_chef`, `prep_cook`, `general`, or `admin`.  
   - Only users with `sushi_chef` or `admin` can add or edit recipes.

---

### Day-to-day use

**You (owner) or a sushi chef**

- **Update a recipe (costs, quantities, steps)**  
  `/update_recipe` → recipe name → natural-language instruction, e.g. *“Update avocado cost to $2 each and increase quantity by 20% for waste.”*

- **Add a new recipe**  
  `/add_recipe` → name, then paste or type ingredients/procedures/supplies as JSON (see `/help` or README for format). Set base servings (e.g. 50).

- **Scale for an event and get cost**  
  `/refine_quantities` → recipe name → number of guests → optional feedback (e.g. *“Reduce rice waste by 10%”*). Use the reply to order ingredients and plan cost.

**Any staff (daily prep)**

- **See what to prep today**  
  `/get_prep_list` → recipe name → number of guests. The list is filtered by the staff member’s role (sushi_chef / prep_cook / general).

- **Check what’s in the system**  
  `/list_recipes` to see all recipe names.

**Quick reference**

| Goal                         | Command              | Who can use      |
|------------------------------|----------------------|------------------|
| Scale for event + cost       | `/refine_quantities` | Anyone           |
| Today’s prep list (by role)  | `/get_prep_list`     | Anyone           |
| Change a recipe              | `/update_recipe`     | sushi_chef, admin|
| Add recipe                   | `/add_recipe`        | sushi_chef, admin|
| Assign staff role            | `/set_role`          | admin only       |
| List recipes                 | `/list_recipes`      | Anyone           |

---

## Discord Commands

| Command | Description |
|--------|-------------|
| `/help` | List all commands. |
| `/add_recipe` | Add recipe (name, ingredients/procedures/supplies as JSON, base_servings). **sushi_chef / admin only.** |
| `/update_recipe` | Update recipe by natural language. **sushi_chef / admin only.** |
| `/refine_quantities` | Scale quantities for guest count; optional feedback for AI. |
| `/get_prep_list` | Prep list for recipe + guests, filtered by your role. |
| `/list_recipes` | List all recipe names. |
| `/set_role` | Set a user's role (discord_id, role). **Admin only.** |

## Staff Roles

Roles are stored in the database (table `users`). Default is `general`. Use `/set_role` (admin only) or `python set_admin.py <discord_id>` to assign roles. Roles used:

- **sushi_chef** – rolling, rice, fish, procedures.
- **prep_cook** – chopping, veggies, prep.
- **general** – packing, supplies.
- **admin** – full access.

## Project Layout

```
Sushi Catering/
├── config.py          # Env and config
├── models.py          # SQLAlchemy Recipe, User; engine and session
├── recipe_service.py  # CRUD for recipes
├── ai_service.py      # AI parse update, refine quantities
├── task_service.py    # Prep list, assign by role
├── user_service.py    # User role lookup, can_edit_recipes
├── bot.py             # Discord slash commands
├── seed_recipes.py    # Seed sample recipes
├── requirements.txt
├── .env.example
└── README.md
```

## Deployment

- **Local**: Run `python bot.py` with `.env` set.
- **Replit / Heroku**: Set `DISCORD_TOKEN` and `GEMINI_API_KEY` in environment; use `DATABASE_URL` for PostgreSQL if needed. Run `python bot.py` (and `seed_recipes.py` once).

## Optional: Unit Tests

Example focus areas:

- `recipe_service`: create, get, update, delete.
- `ai_service`: `ai_refine_quantities` with mock or no API (simple scaling path).
- `task_service`: `generate_prep_list`, `assign_tasks` by role.

Use prompts like: *“Write unit tests for ai_refine_quantities”* or *“Evaluate this function for edge cases (e.g. invalid guests).”*

## Security Notes

- Keep `.env` out of version control; use `.env.example` only.
- Bot checks roles from DB; ensure only trusted users get `sushi_chef`/`admin`.
- For production, consider rate limiting and logging of who changed what.
