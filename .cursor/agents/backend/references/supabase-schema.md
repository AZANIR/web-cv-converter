# Supabase Schema Conventions

## Migration File

All migrations are append-only SQL in `backend/supabase/schema.sql`.

Rules:
- NEVER drop tables or columns
- NEVER remove RLS policies
- Append new `CREATE TABLE`, `ALTER TABLE`, or `CREATE POLICY` statements at the end
- Comment each migration block with date and purpose

```sql
-- 2026-04-08: Add {feature} table
CREATE TABLE IF NOT EXISTS {table_name} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS: users can only access their own rows
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

CREATE POLICY "{table_name}_user_select"
    ON {table_name} FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "{table_name}_user_insert"
    ON {table_name} FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "{table_name}_user_update"
    ON {table_name} FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "{table_name}_user_delete"
    ON {table_name} FOR DELETE
    USING (auth.uid() = user_id);
```

## Naming Conventions

| Object | Convention | Example |
|---|---|---|
| Tables | `snake_case`, plural | `cv_conversions` |
| Columns | `snake_case` | `user_id`, `created_at` |
| Foreign keys | `{table}_id` | `profile_id` |
| Indexes | `idx_{table}_{column}` | `idx_cv_conversions_user_id` |
| RLS Policies | `"{table}_{role}_{action}"` | `"cv_conversions_user_select"` |

## Existing Tables

- `profiles` — user profiles (id, email, full_name, avatar_url, role)
- `allowed_emails` — email allowlist for access control
- Check `backend/supabase/schema.sql` for the full current schema before adding tables.

## RLS Requirement

Every new table MUST have RLS enabled and appropriate policies. Minimum: SELECT, INSERT, UPDATE, DELETE policies for the owning user.
