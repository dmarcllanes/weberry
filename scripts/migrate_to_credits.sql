-- =============================================================
-- MIGRATION: subscription model → credit-based model
--
-- Run this in Supabase SQL Editor on an existing database.
-- Safe to run multiple times (uses IF EXISTS / IF NOT EXISTS).
-- =============================================================

-- 1. Add credit columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS paid_credits              INT         NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS free_credits              INT         NOT NULL DEFAULT 1;
ALTER TABLE users ADD COLUMN IF NOT EXISTS free_credits_expires_at   TIMESTAMPTZ;

-- 2. Backfill free_credits_expires_at for existing users
--    Give them 7 days from now if they don't have a value yet.
UPDATE users
SET free_credits_expires_at = NOW() + INTERVAL '7 days'
WHERE free_credits_expires_at IS NULL;

-- 3. Remove subscription columns (no longer used)
ALTER TABLE users DROP COLUMN IF EXISTS plan;
ALTER TABLE users DROP COLUMN IF EXISTS lemon_squeezy_subscription_id;
ALTER TABLE users DROP COLUMN IF EXISTS subscription_status;
ALTER TABLE users DROP COLUMN IF EXISTS variant_id;

-- 4. Update pages: change trial comment (no data change needed — column stays)
--    trial_ends_at is now only set for free-credit pages, not all published pages.
--    Existing published pages with trial_ends_at = NULL are already treated as permanent.

-- 5. Bump the dev seed user to have unlimited credits
UPDATE users
SET paid_credits              = 999,
    free_credits              = 999,
    free_credits_expires_at   = '2099-12-31 00:00:00+00'
WHERE id = '00000000-0000-0000-0000-000000000001';
