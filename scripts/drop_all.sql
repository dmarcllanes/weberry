-- =============================================================
-- OKENABA — Drop Everything (old schema)
-- WARNING: This permanently destroys all data.
-- Use only in development or when rebuilding from scratch.
--
-- Targets the OLD table names (projects, published_sites).
-- After running this, apply schema.sql to create the new schema
-- with the correct names (pages, published_pages).
--
-- Does NOT touch:
--   - Supabase Auth (auth.users) — managed by Supabase, not us
--   - Storage buckets — delete manually in the dashboard
--
-- Run in Supabase SQL Editor.
-- =============================================================


-- Step 1: Drop triggers (old name)
DROP TRIGGER IF EXISTS trg_projects_updated_at ON projects;
DROP TRIGGER IF EXISTS trg_pages_updated_at    ON pages;


-- Step 2: Drop functions
DROP FUNCTION IF EXISTS fn_set_updated_at()    CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;


-- Step 3: Drop tables — old names first, then new names as fallback
-- Child tables first (FK constraints), then parents
DROP TABLE IF EXISTS published_sites  CASCADE;
DROP TABLE IF EXISTS published_pages  CASCADE;
DROP TABLE IF EXISTS projects         CASCADE;
DROP TABLE IF EXISTS pages            CASCADE;
DROP TABLE IF EXISTS users            CASCADE;
