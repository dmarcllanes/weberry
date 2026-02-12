"""
Database migration script.
Creates all tables needed for Okenaba.

Usage: python -m scripts.migrate
Requires: DATABASE_URL environment variable
"""

import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DDL = """
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
"""


def run():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is required")
        sys.exit(1)

    print("Connecting to database...")
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()
        print("Migration complete. All tables created.")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
