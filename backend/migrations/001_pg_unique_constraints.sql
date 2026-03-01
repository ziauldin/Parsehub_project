-- =============================================================================
-- Migration: PostgreSQL compatibility fixes for Railway deployment
-- Run this ONCE against your Railway PostgreSQL database.
-- =============================================================================

-- 1. Ensure projects.token has a UNIQUE constraint (required for ON CONFLICT).
--    The IF NOT EXISTS guard is not available on ADD CONSTRAINT, so we use
--    a DO block to make this idempotent.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   pg_constraint
        WHERE  conname = 'projects_token_unique'
    ) THEN
        ALTER TABLE projects
            ADD CONSTRAINT projects_token_unique UNIQUE (token);
        RAISE NOTICE 'Added UNIQUE constraint projects_token_unique';
    ELSE
        RAISE NOTICE 'projects_token_unique already exists – skipping';
    END IF;
END;
$$;

-- 2. Ensure runs.run_token has a UNIQUE constraint (required for ON CONFLICT).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   pg_constraint
        WHERE  conname = 'runs_run_token_unique'
    ) THEN
        ALTER TABLE runs
            ADD CONSTRAINT runs_run_token_unique UNIQUE (run_token);
        RAISE NOTICE 'Added UNIQUE constraint runs_run_token_unique';
    ELSE
        RAISE NOTICE 'runs_run_token_unique already exists – skipping';
    END IF;
END;
$$;

-- 3. Add updated_at to runs if missing (SQLite schema did not include it).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   information_schema.columns
        WHERE  table_name  = 'runs'
          AND  column_name = 'updated_at'
    ) THEN
        ALTER TABLE runs
            ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added column runs.updated_at';
    ELSE
        RAISE NOTICE 'runs.updated_at already exists – skipping';
    END IF;
END;
$$;

-- 4. Add updated_at to projects if missing.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   information_schema.columns
        WHERE  table_name  = 'projects'
          AND  column_name = 'updated_at'
    ) THEN
        ALTER TABLE projects
            ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added column projects.updated_at';
    ELSE
        RAISE NOTICE 'projects.updated_at already exists – skipping';
    END IF;
END;
$$;

-- =============================================================================
-- Verification queries (run manually to confirm):
--
--   SELECT conname, contype FROM pg_constraint
--   WHERE  conrelid = 'projects'::regclass OR conrelid = 'runs'::regclass;
--
--   SELECT column_name, data_type FROM information_schema.columns
--   WHERE  table_name IN ('projects', 'runs')
--   ORDER  BY table_name, ordinal_position;
-- =============================================================================
