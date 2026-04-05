-- CV Converter — run in Supabase SQL Editor
-- Auth0 JWT sub is stored as profiles.id

CREATE TABLE IF NOT EXISTS profiles (
  id          TEXT PRIMARY KEY,
  email       TEXT UNIQUE NOT NULL,
  full_name   TEXT,
  avatar_url  TEXT,
  role        TEXT NOT NULL DEFAULT 'user',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS allowed_emails (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email      TEXT UNIQUE NOT NULL,
  added_by   TEXT REFERENCES profiles(id),
  note       TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversions (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  original_filename TEXT NOT NULL,
  md_content        TEXT NOT NULL,
  json_data         JSONB,
  pdf_storage_path  TEXT,
  pdf_filename      TEXT,
  status            TEXT DEFAULT 'pending',
  error_message     TEXT,
  include_header    BOOLEAN DEFAULT TRUE,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversions_user_id ON conversions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversions_created_at ON conversions(created_at DESC);

-- RLS: enable so Supabase Security Advisor is satisfied. No policies = deny for anon/authenticated
-- via PostgREST; backend uses service_role and bypasses RLS (see IMPLEMENTATION_PLAN).
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE allowed_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversions ENABLE ROW LEVEL SECURITY;

-- Storage: in Dashboard create private bucket `cv-pdfs`, or via SQL (service role bypasses RLS for backend uploads):
-- insert into storage.buckets (id, name, public) values ('cv-pdfs', 'cv-pdfs', false) on conflict (id) do nothing;
