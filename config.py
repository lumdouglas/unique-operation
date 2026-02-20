"""Configuration and environment loading."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sushi.db")

# API keys (required for bot and AI)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Optional: role names that map to permissions
ALLOWED_ROLES = {"sushi_chef", "prep_cook", "general", "admin"}
