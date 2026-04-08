-- CV Converter — run in Supabase SQL Editor
-- Auth0 JWT sub is stored as profiles.id

-- pgvector in a dedicated schema (avoids "Extension in Public" warning)
CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

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

-- Vacancies: templatized job postings
CREATE TABLE IF NOT EXISTS vacancies (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  raw_input         TEXT NOT NULL,
  input_type        TEXT NOT NULL DEFAULT 'text',
  original_filename TEXT,
  case_study_json   JSONB,
  case_study_md     TEXT,
  status            TEXT DEFAULT 'pending',
  error_message     TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vacancies_user_id ON vacancies(user_id);
CREATE INDEX IF NOT EXISTS idx_vacancies_created_at ON vacancies(created_at DESC);

-- Generated CVs from vacancies
CREATE TABLE IF NOT EXISTS generated_cvs (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  vacancy_id        UUID NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
  md_content        TEXT,
  json_data         JSONB,
  pdf_storage_path  TEXT,
  pdf_filename      TEXT,
  include_header    BOOLEAN DEFAULT TRUE,
  status            TEXT DEFAULT 'draft',
  error_message     TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_generated_cvs_user_id ON generated_cvs(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_cvs_vacancy_id ON generated_cvs(vacancy_id);
CREATE INDEX IF NOT EXISTS idx_generated_cvs_created_at ON generated_cvs(created_at DESC);

-- Vector embeddings for semantic search (case studies, vacancies, generated CVs)
CREATE TABLE IF NOT EXISTS document_embeddings (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  doc_type    TEXT NOT NULL,
  doc_id      UUID,
  source_file TEXT,
  content     TEXT NOT NULL,
  metadata    JSONB DEFAULT '{}'::jsonb,
  embedding   extensions.vector(3072) NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_document_embeddings_doc_type ON document_embeddings(doc_type);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_source_file ON document_embeddings(source_file);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector
  ON document_embeddings USING ivfflat (embedding extensions.vector_cosine_ops) WITH (lists = 100);

-- Semantic search function
CREATE OR REPLACE FUNCTION public.match_documents(
  query_embedding extensions.vector(3072),
  match_count int DEFAULT 5,
  filter_doc_type text DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  doc_type text,
  doc_id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
SET search_path = ''
AS $$
BEGIN
  RETURN QUERY
  SELECT
    de.id, de.doc_type, de.doc_id, de.content, de.metadata,
    1 - (de.embedding <=> query_embedding) AS similarity
  FROM public.document_embeddings de
  WHERE (filter_doc_type IS NULL OR de.doc_type = filter_doc_type)
  ORDER BY de.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Admin-editable prompts
CREATE TABLE IF NOT EXISTS prompts (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug        TEXT UNIQUE NOT NULL,
  name        TEXT NOT NULL,
  description TEXT DEFAULT '',
  content     TEXT NOT NULL,
  version     INTEGER DEFAULT 1,
  updated_by  TEXT REFERENCES profiles(id),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- RLS: enable so Supabase Security Advisor is satisfied. No policies = deny for anon/authenticated
-- via PostgREST; backend uses service_role and bypasses RLS (see IMPLEMENTATION_PLAN).
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE allowed_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE vacancies ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;

-- Storage: in Dashboard create private bucket `cv-pdfs`, or via SQL (service role bypasses RLS for backend uploads):
-- insert into storage.buckets (id, name, public) values ('cv-pdfs', 'cv-pdfs', false) on conflict (id) do nothing;

-- Trigger function to keep updated_at current on row updates
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_conversions BEFORE UPDATE ON conversions
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at_vacancies BEFORE UPDATE ON vacancies
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at_generated_cvs BEFORE UPDATE ON generated_cvs
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at_prompts BEFORE UPDATE ON prompts
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
