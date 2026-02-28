-- =============================================================
-- OKENABA — Fresh Database Schema
-- Run in Supabase SQL Editor after running drop_all.sql.
--
-- Does NOT include:
--   - RLS policies (app uses SERVICE_KEY which bypasses RLS)
--   - Auth setup (managed by Supabase — auth.users is separate)
--   - Storage bucket (create manually: Storage → New bucket
--                     Name: okenaba-assets  |  Public: ON)
--
-- Business context:
--   Okenaba is a Rapid Idea Validator. Users fill a Brain Dump
--   wizard → one AI call generates a complete static site →
--   user previews, edits images, then publishes.
--   Business model: 1 credit = 1 published page.
--   Signup gives 1 free credit valid for 7 days. Purchased credits never expire.
-- =============================================================


-- =============================================================
-- EXTENSIONS
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- =============================================================
-- TABLE: users
--
-- Business model: credit-based. 1 credit = 1 published page.
--   free_credits   — 1 credit granted on signup, expires after 7 days.
--   paid_credits   — purchased via Lemon Squeezy one-time packs. Never expire.
--   Pages published with a free credit get a 7-day trial (is_paused after).
--   Pages published with a paid credit are permanent (no trial).
--
-- id = Supabase Auth user ID (always provided by auth, no auto-gen needed).
-- avatar_url is stored in the session cookie only — never written to DB.
-- lemon_squeezy_customer_id kept for purchase tracking.
-- =============================================================

CREATE TABLE users (
    id                             UUID        PRIMARY KEY,
    email                          TEXT        NOT NULL UNIQUE,
    full_name                      TEXT,

    -- credits
    paid_credits                   INT         NOT NULL DEFAULT 0,
    free_credits                   INT         NOT NULL DEFAULT 1,
    free_credits_expires_at        TIMESTAMPTZ,
    -- set to created_at + 7 days on user creation (see upsert_user in db.py)

    -- billing — Lemon Squeezy one-time purchase tracking
    lemon_squeezy_customer_id      TEXT,

    created_at                     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =============================================================
-- TABLE: pages
--
-- Business rules:
--   One row = one page/site the user is building or has built.
--   Called "pages" everywhere in the UI and HTTP routes (/pages/{id}).
--
-- State machine (Brain Dump flow):
--   DRAFT → INPUT_READY → MEMORY_READY → SITE_GENERATED → PREVIEW → PUBLISHED
--   (PLAN_READY and PLAN_APPROVED are legacy states, kept for compatibility)
--   ERROR = AI call failed mid-flow; retry button re-runs generation.
--
-- JSONB columns store serialized Python dataclasses (see user_app/db.py).
-- updated_at is maintained automatically by the trigger below.
-- trial_ends_at is set 15 days after the first publish.
-- is_paused = true when trial has expired and user has not upgraded.
-- =============================================================

CREATE TABLE pages (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    state           TEXT        NOT NULL DEFAULT 'draft',
    -- state values:
    --   draft | input_ready | memory_ready | plan_ready |
    --   plan_approved | site_generated | preview | published | error

    template_id     TEXT,
    -- selected template path, e.g. "tech/saas" or "creative/portfolio"
    -- matches the folder structure under templates/

    brand_memory    JSONB,
    -- shape: {
    --   business_name: str, website_type: str, primary_goal: str,
    --   description: str, theme: str, primary_color: str (#hex),
    --   secondary_color: str (#hex), contact_email: str,
    --   contact_phone: str, address: str, tagline: str,
    --   services: [str],          <- industry stored here (single element)
    --   project_intent: str,      <- "validation" | "presence"
    --   labeled_assets: [{url, label, width, height, orientation}]
    -- }

    ai_usage        JSONB       NOT NULL DEFAULT '{"planner_calls": 0, "generation_calls": 0, "last_ai_call_at": null}'::jsonb,
    -- shape: {
    --   planner_calls: int,
    --   generation_calls: int,
    --   last_ai_call_at: iso_string | null
    -- }
    -- Tier limits enforced in core/billing/entitlements.py

    site_plan       JSONB,
    -- shape: {
    --   page_title: str, meta_description: str,
    --   sections: [{id, title, purpose, content_notes}],
    --   copy_blocks: [{placeholder_key, content}],
    --   active_sections: [str],
    --   selected_template: str,
    --   image_keywords: {slot_name: keyword},
    --   image_overrides: {slot_name: public_url}
    -- }

    site_version    JSONB,
    -- shape: {
    --   html: str,          <- full rendered HTML (no <script> tags)
    --   css: str,           <- full rendered CSS (Jinja2 color vars resolved)
    --   version: int,
    --   is_published: bool
    -- }
    -- Nav JS and inline CSS are injected at serve time, not stored here.

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at    TIMESTAMPTZ,
    trial_ends_at   TIMESTAMPTZ,
    -- set to published_at + 7 days only when published using a free credit.
    -- NULL when published with a paid credit (page never expires).

    is_paused       BOOLEAN     NOT NULL DEFAULT FALSE
    -- true when trial_ends_at has passed (free-credit pages only)
);


-- =============================================================
-- TABLE: published_pages
--
-- Business rules:
--   Audit log of every publish event.
--   One row per publish — version increments on each republish.
--   storage_path = path inside the Supabase Storage bucket (okenaba-assets).
--   public_url = CDN-accessible URL served at /sites/{page_id}.
--   html_hash / css_hash = SHA-256 fingerprints for change detection.
--   Rows are deleted automatically when the parent page is deleted.
-- =============================================================

CREATE TABLE published_pages (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    page_id         UUID        NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    version         INTEGER     NOT NULL,
    storage_path    TEXT        NOT NULL,
    public_url      TEXT        NOT NULL,
    html_hash       TEXT,
    css_hash        TEXT,
    published_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =============================================================
-- INDEXES
-- =============================================================

-- Most common query: "get all pages for this user"
CREATE INDEX idx_pages_user_id          ON pages(user_id);

-- Admin / monitoring: "show all pages in state X"
CREATE INDEX idx_pages_state            ON pages(state);

-- Used by delete_page() to clean up published_pages rows
CREATE INDEX idx_published_pages_page_id ON published_pages(page_id);


-- =============================================================
-- TRIGGER: keep updated_at current on every page save
-- =============================================================

CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pages_updated_at
    BEFORE UPDATE ON pages
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();


-- =============================================================
-- SEED: development stub user
--
-- STUB_USER_ID matches the hardcoded dev user in user_app/auth.
-- Insert only in local / staging environments.
-- Skip this block in production.
-- =============================================================

INSERT INTO users (id, email, paid_credits, free_credits, free_credits_expires_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'dev@okenaba.local',
    999,
    999,
    '2099-12-31 00:00:00+00'  -- never expires for dev
)
ON CONFLICT (id) DO NOTHING;
