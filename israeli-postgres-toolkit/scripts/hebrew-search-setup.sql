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

-- Strip Hebrew nikud and cantillation so pointed and unpointed text match.
-- NOTE: the unaccent extension does NOT strip Hebrew nikud.
--
-- The class below is the COMBINING MARKS only (Unicode category Mn). Do NOT use the
-- whole U+0591-U+05C7 block: it also contains U+05BE MAQAF (category Pd) and
-- U+05C0 PASEQ / U+05C3 SOF PASUQ / U+05C6 NUN HAFUKHA (category Po). Those are word
-- separators, and deleting them concatenates words, so 'תל־אביב' would index as the
-- single lexeme 'תלאביב' and a search for 'תל אביב' could never match it.
-- IMMUTABLE so it can back the generated column and indexes below.
CREATE OR REPLACE FUNCTION strip_nikud(text) RETURNS text
  AS $$ SELECT regexp_replace($1, '[֑-ֽֿׁ-ׂׄ-ׇׅ]', '', 'g') $$
  LANGUAGE sql IMMUTABLE;

-- Full search-side normalisation: nikud removed, Hebrew punctuation separators turned
-- into spaces, and geresh/gershayim removed.
--
-- The last part matters more than it looks. The default FTS parser classifies gershayim
-- (U+05F4) as a BLANK token, so 'בע״מ' tokenises as two lexemes 'בע' and 'מ', while a
-- user searching for a company types 'בעמ'. Same for צה״ל, ד״ר, ח״כ, ש״ח. Stripping the
-- mark on BOTH the stored and the query side makes them meet. The ASCII apostrophe and
-- quote are included because real-world Hebrew input routinely substitutes them.
-- Apply this to the query as well as to the column, or the two sides will not agree.
CREATE OR REPLACE FUNCTION normalize_hebrew(text) RETURNS text
  AS $$
    SELECT regexp_replace(
             regexp_replace(
               regexp_replace($1, '[֑-ֽֿׁ-ׂׄ-ׇׅ]', '', 'g'),  -- nikud + cantillation (Mn)
               '[־׀׃׆]', ' ', 'g'),                       -- maqaf, paseq, sof pasuq, nun hafukha
             '[׳״''"]', '', 'g')                          -- geresh, gershayim, ASCII ' and "
  $$
  LANGUAGE sql IMMUTABLE;

-- ============================================================================
-- 2. Hebrew ICU Collation
-- ============================================================================

-- Non-deterministic collation for proper Hebrew sorting.
-- UNIQUE constraints and btree indexes DO work on such a column (they only lose
-- B-tree deduplication). ILIKE and regular expressions error; plain LIKE errors
-- before PostgreSQL 18 and is allowed from 18 onward, but cannot use a prefix index.
-- 'he-IL' is the ICU/BCP-47 locale. 'he-IL-x-icu' is the NAME of the pre-created
-- collation, not a locale, so do not pass it here.
CREATE COLLATION IF NOT EXISTS hebrew_icu (
  provider = icu,
  locale = 'he-IL',
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
    setweight(to_tsvector('simple', normalize_hebrew(coalesce(title_he, ''))), 'A') ||
    setweight(to_tsvector('simple', normalize_hebrew(coalesce(body_he, ''))), 'B') ||
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
-- Trigram indexes over the NORMALIZED expression, not the raw column. The FTS vector
-- is normalized, so if the trigram branch matched raw text the two halves of the search
-- would disagree: pointed text like 'שָׁלוֹם עוֹלָם' scores similarity 0.05 against 'שלום'
-- (invisible to the fuzzy branch) but 0.5 once normalized. The predicates in
-- search_hebrew() use the identical expression so these indexes are actually usable.
CREATE INDEX IF NOT EXISTS idx_searchable_content_title_he_trgm
  ON searchable_content USING gin (normalize_hebrew(title_he) gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_searchable_content_body_he_trgm
  ON searchable_content USING gin (normalize_hebrew(body_he) gin_trgm_ops);

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
  similarity_threshold float DEFAULT 0.2,       -- gates % on title_he
  max_results int DEFAULT 20,
  word_similarity_threshold float DEFAULT 0.6   -- gates <% on body_he
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
  -- Each trigram operator reads its OWN GUC, and PostgreSQL gives them different
  -- defaults on purpose:
  --   %   -> pg_trgm.similarity_threshold              (default 0.3)
  --   <%  -> pg_trgm.word_similarity_threshold         (default 0.6)
  --   <<% -> pg_trgm.strict_word_similarity_threshold  (default 0.5)
  -- Setting only the first leaves the <% body branch gated at 0.6 whatever the caller
  -- passes, which silently disables it. Do NOT fix that by feeding one value into all
  -- three: word_similarity scores the best-matching word extent rather than the whole
  -- string, so it runs much higher, and 0.2-0.3 there returns near-unrelated rows.
  -- Hence two separate parameters with the operators' own defaults.
  PERFORM set_config('pg_trgm.similarity_threshold', similarity_threshold::text, true);
  PERFORM set_config('pg_trgm.word_similarity_threshold', word_similarity_threshold::text, true);

  -- The stored vector stems English columns with the 'english' config ('invoice'
  -- is stored as 'invoic'), so a 'simple' query alone can NEVER match them. OR the
  -- two configs together or English search silently returns nothing.
  RETURN QUERY
  -- Full-text search results
  SELECT
    sc.id,
    sc.title_he,
    sc.title_en,
    ts_rank(sc.search_vector, (plainto_tsquery('simple', normalize_hebrew(query_text)) || plainto_tsquery('english', query_text)))::float AS rank,
    0.0::float AS similarity,
    'fts'::text AS match_type
  FROM searchable_content sc
  WHERE sc.search_vector @@ (plainto_tsquery('simple', normalize_hebrew(query_text)) || plainto_tsquery('english', query_text))
    AND sc.is_published = true

  UNION ALL

  -- Fuzzy trigram results (that were not caught by FTS).
  -- title_he uses % (whole-string similarity); body_he uses <% (word_similarity),
  -- because whole-string similarity on a long body is diluted below the threshold
  -- even when the term is present verbatim. Without the <% branch the body trigram
  -- index below is never used and inflected body-only hits are lost entirely.
  SELECT
    sc.id,
    sc.title_he,
    sc.title_en,
    0.0::float AS rank,
    greatest(
      similarity(normalize_hebrew(sc.title_he), normalize_hebrew(query_text)),
      coalesce(word_similarity(normalize_hebrew(query_text), normalize_hebrew(sc.body_he)), 0)
    )::float AS similarity,
    'fuzzy'::text AS match_type
  FROM searchable_content sc
  -- The predicate must use EXACTLY the expression the index was built on. Wrapping the
  -- column in anything the index does not know (a coalesce, a different function) makes
  -- PostgreSQL fall back to a sequential scan while the query still looks indexed.
  -- A NULL body_he yields NULL here, which the WHERE discards anyway.
  WHERE (normalize_hebrew(sc.title_he) % normalize_hebrew(query_text)
         OR normalize_hebrew(query_text) <% normalize_hebrew(sc.body_he))
    AND sc.is_published = true
    AND NOT sc.search_vector @@ (plainto_tsquery('simple', normalize_hebrew(query_text)) || plainto_tsquery('english', query_text))

  ORDER BY rank DESC, similarity DESC
  LIMIT max_results;
END;
-- VOLATILE, not STABLE: set_config() above is a volatile call.
$$ LANGUAGE plpgsql VOLATILE;

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
