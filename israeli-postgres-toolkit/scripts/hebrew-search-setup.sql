-- hebrew-search-setup.sql
-- Sets up Hebrew full-text search with proper collation, trigram indexes,
-- and search functions for PostgreSQL / Supabase.
--
-- Usage: psql -f hebrew-search-setup.sql -d your_database
-- Or run via Supabase SQL Editor.

-- ============================================================================
-- 1. Extensions
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- 2. Hebrew ICU Collation
-- ============================================================================

-- Non-deterministic collation for proper Hebrew sorting.
-- Cannot be used with UNIQUE constraints or btree indexes directly.
CREATE COLLATION IF NOT EXISTS hebrew_icu (
  provider = icu,
  locale = 'he-IL-x-icu',
  deterministic = false
);

-- ============================================================================
-- 3. Example Table with Hebrew Search Support
-- ============================================================================

-- Drop if exists for idempotent re-runs (remove in production)
-- DROP TABLE IF EXISTS searchable_content;

CREATE TABLE IF NOT EXISTS searchable_content (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Bilingual content
  title_he text NOT NULL,
  title_en text,
  body_he text,
  body_en text,

  -- Hebrew-sorted display name
  display_name_he text COLLATE hebrew_icu,

  -- Auto-generated search vector
  search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(title_he, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(body_he, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(title_en, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(body_en, '')), 'B')
  ) STORED,

  -- Metadata
  is_published boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================================================
-- 4. Indexes
-- ============================================================================

-- GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_searchable_content_fts
  ON searchable_content USING gin (search_vector);

-- Trigram indexes for fuzzy Hebrew search
CREATE INDEX IF NOT EXISTS idx_searchable_content_title_he_trgm
  ON searchable_content USING gin (title_he gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_searchable_content_body_he_trgm
  ON searchable_content USING gin (body_he gin_trgm_ops);

-- Partial index for published content only
CREATE INDEX IF NOT EXISTS idx_searchable_content_published
  ON searchable_content (created_at DESC)
  WHERE is_published = true;

-- ============================================================================
-- 5. Search Functions
-- ============================================================================

-- Combined search: full-text + fuzzy matching
-- Returns results ranked by relevance
CREATE OR REPLACE FUNCTION search_hebrew(
  query_text text,
  similarity_threshold float DEFAULT 0.2,
  max_results int DEFAULT 20
)
RETURNS TABLE (
  id uuid,
  title_he text,
  title_en text,
  rank float,
  similarity float,
  match_type text
) AS $$
BEGIN
  -- Set trigram threshold
  PERFORM set_config('pg_trgm.similarity_threshold', similarity_threshold::text, true);

  RETURN QUERY
  -- Full-text search results
  SELECT
    sc.id,
    sc.title_he,
    sc.title_en,
    ts_rank(sc.search_vector, plainto_tsquery('simple', query_text))::float AS rank,
    0.0::float AS similarity,
    'fts'::text AS match_type
  FROM searchable_content sc
  WHERE sc.search_vector @@ plainto_tsquery('simple', query_text)
    AND sc.is_published = true

  UNION ALL

  -- Fuzzy trigram results (that were not caught by FTS)
  SELECT
    sc.id,
    sc.title_he,
    sc.title_en,
    0.0::float AS rank,
    similarity(sc.title_he, query_text)::float AS similarity,
    'fuzzy'::text AS match_type
  FROM searchable_content sc
  WHERE sc.title_he % query_text
    AND sc.is_published = true
    AND NOT sc.search_vector @@ plainto_tsquery('simple', query_text)

  ORDER BY rank DESC, similarity DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql STABLE;

-- Simple prefix search for autocomplete
CREATE OR REPLACE FUNCTION autocomplete_hebrew(
  prefix text,
  max_results int DEFAULT 10
)
RETURNS TABLE (
  id uuid,
  title_he text,
  title_en text
) AS $$
BEGIN
  RETURN QUERY
  SELECT sc.id, sc.title_he, sc.title_en
  FROM searchable_content sc
  WHERE sc.title_he LIKE prefix || '%'
    AND sc.is_published = true
  ORDER BY sc.title_he COLLATE hebrew_icu
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 6. Updated_at Trigger
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_updated_at ON searchable_content;
CREATE TRIGGER trigger_update_updated_at
  BEFORE UPDATE ON searchable_content
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- 7. Sample Data (optional, remove in production)
-- ============================================================================

-- INSERT INTO searchable_content (title_he, title_en, body_he, body_en, is_published) VALUES
-- ('חשבונית מס', 'Tax Invoice', 'מסמך חשבונית מס עבור עסקאות בישראל', 'Tax invoice document for Israeli transactions', true),
-- ('דוח שנתי', 'Annual Report', 'דוח שנתי לרשויות המס בישראל', 'Annual report for Israeli tax authorities', true),
-- ('הסכם שכירות', 'Rental Agreement', 'חוזה שכירות דירה בישראל', 'Apartment rental contract in Israel', true);
