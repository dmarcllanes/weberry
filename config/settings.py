import os

HF_API_KEY = os.environ.get("HF_API_KEY", "")
HF_INFERENCE_URL = "https://router.huggingface.co/models"
HF_BASE_URL = "https://router.huggingface.co/v1"

# Model Router
HF_MODELS = {
    # Logic Engine: Metadata analysis, routing, simple decisions
    "logic": "meta-llama/Llama-3.3-70B-Instruct",
    # Copywriter: Sales letters, bio, creative text (Planner)
    "copy": "meta-llama/Llama-3.3-70B-Instruct",
    # Architect: Valid HTML/CSS generation
    "code": "meta-llama/Llama-3.3-70B-Instruct",
}

# Rate limiting: max calls per window
RATE_LIMIT_MAX_CALLS = int(os.environ.get("RATE_LIMIT_MAX_CALLS", "10"))
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60"))

# Cooldown between AI calls (seconds)
AI_COOLDOWN_SECONDS = int(os.environ.get("AI_COOLDOWN_SECONDS", "30"))

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")  # anon key for frontend JS client
SUPABASE_STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "published-sites")
SUPABASE_ASSETS_BUCKET = os.environ.get("SUPABASE_ASSETS_BUCKET", "public-assets")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Trial durations
FREE_CREDIT_TRIAL_DAYS  = int(os.environ.get("FREE_CREDIT_TRIAL_DAYS", "7"))   # signup free credit
PAID_CREDIT_TRIAL_DAYS  = int(os.environ.get("PAID_CREDIT_TRIAL_DAYS", "30"))  # purchased credits

# Lemon Squeezy
LEMON_SQUEEZY_API_KEY = os.environ.get("LEMON_SQUEEZY_API_KEY", "")
LEMON_SQUEEZY_WEBHOOK_SECRET = os.environ.get("LEMON_SQUEEZY_WEBHOOK_SECRET", "")
LEMON_SQUEEZY_STORE_ID = os.environ.get("LEMON_SQUEEZY_STORE_ID", "")

# Credit pack variant IDs → credits awarded on purchase (one-time products).
# Get Variant IDs from your Lemon Squeezy dashboard → product → Variants tab.
LEMON_SQUEEZY_CREDIT_PACKS: dict[str, int] = {
    os.environ.get("LEMON_SQUEEZY_VARIANT_STARTER", ""): 5,   # Starter: 5 credits / $9
    os.environ.get("LEMON_SQUEEZY_VARIANT_GROWTH", ""):  15,  # Growth:  15 credits / $19
    os.environ.get("LEMON_SQUEEZY_VARIANT_STUDIO", ""):  50,  # Studio:  50 credits / $49
}

# Cloudflare Turnstile
# Get your keys at https://dash.cloudflare.com → Turnstile
# Default values are Cloudflare's official test keys (always pass in dev)
TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY", "1x00000000000000000000AA")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "1x0000000000000000000000000000000AA")

# App
APP_HOST = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT = int(os.environ.get("APP_PORT", os.environ.get("PORT", "5001")))
