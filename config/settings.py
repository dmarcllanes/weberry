import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

# AI usage limits per plan
AI_LIMITS = {
    "FREE": {
        "planner_calls": 1,
        "generation_calls": 1,
    },
    "PAID": {
        "planner_calls": 5,
        "generation_calls": 5,
    },
}

# Rate limiting: max calls per window
RATE_LIMIT_MAX_CALLS = int(os.environ.get("RATE_LIMIT_MAX_CALLS", "10"))
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60"))

# Cooldown between AI calls (seconds)
AI_COOLDOWN_SECONDS = int(os.environ.get("AI_COOLDOWN_SECONDS", "30"))

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "published-sites")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Trial
TRIAL_DURATION_DAYS = int(os.environ.get("TRIAL_DURATION_DAYS", "15"))

# App
APP_HOST = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT = int(os.environ.get("APP_PORT", os.environ.get("PORT", "5001")))
