-- Fix: municipality and place code columns should be INTEGER to match SQLAlchemy models
-- Run: psql -U autoshkolla -d autoshkolla_pro -f backend/migrations/002_fix_code_columns.sql

-- Drop the unique constraint on municipalities.code first (uses varchar)
ALTER TABLE municipalities DROP CONSTRAINT IF EXISTS municipalities_code_key;

-- Change municipalities.code from VARCHAR to INTEGER
ALTER TABLE municipalities ALTER COLUMN code TYPE INTEGER USING code::INTEGER;

-- Re-add unique constraint
ALTER TABLE municipalities ADD CONSTRAINT municipalities_code_key UNIQUE (code);

-- Places: rename zip_code to code and change type to INTEGER
ALTER TABLE places RENAME COLUMN zip_code TO code;
ALTER TABLE places ALTER COLUMN code TYPE INTEGER USING code::INTEGER;
