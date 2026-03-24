---
title: Okenaba
emoji: 🦅
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Okenaba — Rapid Idea Validator

Validate a business hypothesis in 60 seconds. Generate static, high-performance landing pages via AI + Jinja2 templates.

## Stack
- **FastHTML** (Python web framework)
- **Supabase** (database + auth + file storage)
- **Google Gemini** (AI copy generation)

## Running Locally
```bash
uv run python user_app/main.py  # port 5001
```

## Environment Variables
| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `SUPABASE_ANON_KEY` | Supabase anon key (frontend) |
| `DATABASE_URL` | PostgreSQL connection string |
| `SESSION_SECRET` | Secret key for sessions |
| `TURNSTILE_SITE_KEY` | Cloudflare Turnstile site key |
| `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile secret key |
