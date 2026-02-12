-- Okenaba Data Model
-- Run in Supabase SQL Editor (Script 1: Migration, Script 2: Seed)

-- ============================================
-- SCRIPT 1: MIGRATION (create tables)
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    plan TEXT NOT NULL DEFAULT 'FREE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    state TEXT NOT NULL DEFAULT 'draft',
    brand_memory JSONB,
    ai_usage JSONB NOT NULL DEFAULT '{"planner_calls": 0, "generation_calls": 0, "last_ai_call_at": null}'::jsonb,
    site_plan JSONB,
    site_version JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    trial_ends_at TIMESTAMPTZ,
    is_paused BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS published_sites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    version INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    public_url TEXT NOT NULL,
    html_hash TEXT,
    css_hash TEXT,
    published_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_published_sites_project_id ON published_sites(project_id);

-- ============================================
-- SCRIPT 2: SEED (create dev user)
-- ============================================

INSERT INTO users (id, email, plan)
VALUES ('00000000-0000-0000-0000-000000000001', 'dev@okenaba.local', 'FREE')
ON CONFLICT (id) DO NOTHING;
