-- Add Lemon Squeezy fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS lemon_squeezy_customer_id TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS lemon_squeezy_subscription_id TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS variant_id TEXT;
