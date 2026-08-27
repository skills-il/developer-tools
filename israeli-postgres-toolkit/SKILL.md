---
name: israeli-postgres-toolkit
description: Best practices for PostgreSQL in Israeli apps, covering Supabase patterns, Hebrew text indexing with ICU collation, shekel/NIS currency handling, Israeli date formats, and Asia/Jerusalem timezone gotchas. Use when user asks to "set up Hebrew full-text search", "handle NIS currency in Postgres", "tipul b'ivrit b'database", or configure Israeli-specific database patterns. Includes performance tuning, RLS policies for multi-tenant Israeli SaaS, and common Israeli data type validations. Do NOT use for general PostgreSQL administration unrelated to Israeli requirements, or for non-PostgreSQL databases.
license: MIT
---

# Israeli Postgres Toolkit

Best practices, patterns, and scripts for building PostgreSQL databases tailored to Israeli applications. Covers Hebrew text handling, shekel currency, Israeli timezones, Supabase integration, and common Israeli data types.

Assumes **PostgreSQL 13+** (the patterns use `gen_random_uuid()` from core, non-deterministic ICU collations need 12+, and generated columns need 12+). Current stable is PostgreSQL 18.

## Instructions

Follow this workflow when setting up or reviewing a PostgreSQL database for an Israeli app:

1. **Verify encoding and timezone first.** Run `SHOW server_encoding;` (must be `UTF8`, never `SQL_ASCII` or `LATIN1`) and `SHOW timezone;`. Set the database timezone with `ALTER DATABASE your_db SET timezone = 'Asia/Jerusalem';`. Getting these wrong corrupts Hebrew and offsets every timestamp, and fixing it later means a data migration.
2. **Pick the collation strategy.** Decide per column whether you need Hebrew display ordering (a non-deterministic ICU collation built from locale `he-IL`) or byte-exact prefix search (the default deterministic collation). A non-deterministic collation supports `UNIQUE` constraints and `btree` indexes. From PostgreSQL 18 it also supports `LIKE`, but `ILIKE` and regular expressions still error, and `LIKE` cannot use a btree prefix index. See the operator matrix below before choosing.
3. **Choose the search approach.** For exact and prefix matching use `btree`. For fuzzy/typo-tolerant Hebrew search use `pg_trgm`. For multi-field ranked search use full-text search with the `simple` configuration (see "Full-Text Search with Hebrew" below). For Hebrew matching that ignores nikud, maqaf and gershayim use the `normalize_hebrew()` function shown below, applied to BOTH the column and the query; `unaccent` only strips Latin diacritics, not Hebrew nikud.
4. **Apply Israeli data-type constraints.** Use the `CHECK` constraints and helper functions from `scripts/israeli-data-types.sql` (teudat zehut, phone, postal code, business number, IBAN) and call `validate_teudat_zehut()` for the ID check digit rather than reimplementing it in application code.

## Hebrew Text Indexing

### ICU Collation for Hebrew

PostgreSQL supports ICU collations for proper Hebrew text sorting. Always create a Hebrew collation for columns that store Hebrew text:

```sql
-- Create Hebrew ICU collation
-- locale is the ICU/BCP-47 tag 'he-IL'. Do NOT pass 'he-IL-x-icu': that is the NAME
-- of PostgreSQL's pre-created collation, and '-x-icu' is a private-use subtag ICU
-- silently ignores. (Check with: SELECT collname, colllocale FROM pg_collation;)
CREATE COLLATION IF NOT EXISTS hebrew_icu (
  provider = icu,
  locale = 'he-IL',
  deterministic = false
);

-- Use on columns
CREATE TABLE products (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name_he text COLLATE hebrew_icu NOT NULL,
  name_en text NOT NULL
);

-- Or apply in queries
SELECT * FROM products ORDER BY name_he COLLATE hebrew_icu;
```

**Important:** what a non-deterministic collation supports changed in PostgreSQL 18, which allowed `LIKE` and the text-position functions that "used to generate an error" (PG 18 release notes). Verified on PostgreSQL 18.6:

| Operation on a non-deterministic column | PG 13-17 | PG 18+ |
|---|---|---|
| `UNIQUE` constraint, `btree` index | Works (no B-tree deduplication) | Same |
| `LIKE` | `ERROR: nondeterministic collations are not supported for LIKE` | Works, but the planner can only use an index as a *filter*, never as a prefix range scan |
| `ILIKE` | Error | Still errors |
| Regular expressions (`~`) | Error | Still errors |
| `pg_trgm` (`%`, `<%`) | Works | Works |

So the advice is unchanged even though the reason is not: keep a **deterministic** column (or a `pg_trgm` GIN index) for prefix and fuzzy search, and apply the ICU collation for display ordering and linguistic equality. PostgreSQL 18 also requires a primary/foreign key pair to use either deterministic collations or the *same* non-deterministic one, which can surface as a `pg_upgrade` or `pg_restore` failure on an older schema.

### Trigram Fuzzy Search for Hebrew

The `pg_trgm` extension works well for fuzzy Hebrew search, allowing users to find results even with minor typos:

```sql
-- Enable trigram extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create GIN trigram index on Hebrew columns
CREATE INDEX idx_products_name_he_trgm
  ON products USING gin (name_he gin_trgm_ops);

-- Fuzzy search query
SELECT name_he, similarity(name_he, 'חשבונ') AS sim
FROM products
WHERE name_he % 'חשבונ'
ORDER BY sim DESC
LIMIT 10;

-- Adjust similarity threshold (default is 0.3)
SET pg_trgm.similarity_threshold = 0.2;
```

**Use `<%` (word_similarity), not `%`, when the query is short and the column is long.** `similarity()` compares whole strings, so the score falls as the column grows even though the search term is literally present, while `word_similarity()` does not. Reproducible on PostgreSQL 18.6 (this body is 104 characters and contains `והחשבונית`):

```sql
\set body 'קיבלנו אתמול מהספק שלנו את והחשבונית עבור ההזמנה האחרונה של החודש שעבר ואנחנו ממתינים לאישור סופי מהמנהל'
SELECT similarity(:'body', 'חשבונית'),        -- 0.067  -> :'body' %  'חשבונית' is FALSE
       word_similarity('חשבונית', :'body');   -- 0.750  -> 'חשבונית' <% :'body' is TRUE
```

The crossover depends on length, not on the presence of the word: `similarity('והחשבונית נשלחה', 'חשבונית')` is 0.333 on the same server and clears the default 0.3 threshold, so `%` looks fine in testing on short rows and then silently stops matching once real body text is loaded. That is the trap. Rule of thumb: `%` for short columns (names, titles), `<%` for body and description columns, `<<%` (`strict_word_similarity`) when you want whole-word boundaries. One `gin_trgm_ops` index serves all three.

### Full-Text Search with Hebrew

PostgreSQL's built-in full-text search uses the `simple` configuration for Hebrew (since there is no dedicated Hebrew dictionary). For better results, combine with `pg_trgm`:

```sql
-- Add search vector column
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    -- normalize_hebrew() on the Hebrew columns (see "Hebrew Search Normalization"
    -- below). Without it, stored nikud and gershayim silently block matches.
    setweight(to_tsvector('simple', normalize_hebrew(coalesce(name_he, ''))), 'A') ||
    setweight(to_tsvector('simple', normalize_hebrew(coalesce(description_he, ''))), 'B') ||
    setweight(to_tsvector('english', coalesce(name_en, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description_en, '')), 'B')
  ) STORED;

-- Create GIN index
CREATE INDEX idx_products_search ON products USING gin (search_vector);

-- Search query (handles both Hebrew and English).
-- The vector stems the English columns ('invoice' is stored as the lexeme 'invoic'),
-- so a 'simple'-only query can never match them. OR both configurations together.
SELECT * FROM products
WHERE search_vector @@ (plainto_tsquery('simple', normalize_hebrew($1))
                     || plainto_tsquery('english', $1))
ORDER BY ts_rank(search_vector,
         plainto_tsquery('simple', normalize_hebrew($1))
      || plainto_tsquery('english', $1)) DESC;
```

**`simple` does no stemming, and Hebrew attaches its prepositions to the word.** `חשבונית`, `בחשבונית` and `והחשבונית` become three unrelated lexemes, so FTS alone silently misses most inflected hits. Measured on PostgreSQL 18.6, `plainto_tsquery('simple','חשבונית')` matched 1 of 3 rows containing the word. Do not rely on FTS alone for Hebrew recall, pair every FTS branch with a `<%` trigram branch over the same columns (see "Trigram Fuzzy Search" above). `scripts/hebrew-search-setup.sql` ships `search_hebrew()` wired this way.

### Hebrew Search Normalization (Nikud, Maqaf, Gershayim)

Three separate Hebrew writing conventions each break search, and all three must be normalized on **both** the stored side and the query side or the two never meet.

**1. Nikud.** Users will not type vowel points, so "שָׁלוֹם" must still match "שלום". **The `unaccent` extension does NOT strip Hebrew nikud.** Its default rule file covers Latin/Greek combining marks (U+0300-U+0362) and contains no entry for the Hebrew points block, so `unaccent('שָׁלוֹם')` returns the string unchanged.

**2. Maqaf.** Do NOT strip the whole U+0591-U+05C7 range to remove nikud. That block also holds U+05BE MAQAF (Unicode category `Pd`, a dash) and U+05C0 PASEQ / U+05C3 SOF PASUQ (`Po`). Those are word separators. Deleting them concatenates words, so `תל־אביב` indexes as the single lexeme `תלאביב` and a search for `תל אביב` can never match it. Strip only the combining marks (`Mn`), and turn the separators into spaces.

**3. Gershayim.** The default FTS parser classifies gershayim (U+05F4) as a *blank*, so `בע״מ` tokenizes as two lexemes `בע` and `מ`, while the user searching for that company types `בעמ`. Verified with `ts_debug('simple','צה״ל')`, which returns `צה` (word), `״` (blank), `ל` (word). Every Israeli company name ends in בע״מ, and צה״ל / ד״ר / ח״כ / ש״ח behave the same way, so this silently breaks a large share of real Hebrew queries. Remove geresh and gershayim (and the ASCII `'` and `"` that real input substitutes for them) from both sides.

```sql
-- Combining marks only (Mn). NOT the whole U+0591-U+05C7 block.
CREATE FUNCTION strip_nikud(text) RETURNS text
  AS $$ SELECT regexp_replace($1, '[֑-ֽֿׁ-ׂׄ-ׇׅ]', '', 'g') $$
  LANGUAGE sql IMMUTABLE;

-- Full search-side normalization. IMMUTABLE so it can back a generated column
-- and an expression index.
CREATE FUNCTION normalize_hebrew(text) RETURNS text
  AS $$
    SELECT regexp_replace(
             regexp_replace(
               regexp_replace($1, '[֑-ֽֿׁ-ׂׄ-ׇׅ]', '', 'g'),  -- nikud + cantillation
               '[־׀׃׆]', ' ', 'g'),                       -- maqaf and friends -> space
             '[׳״''"]', '', 'g')                          -- geresh / gershayim
  $$
  LANGUAGE sql IMMUTABLE;

-- Verify all three behaviours (each returns true):
SELECT strip_nikud('שָׁלוֹם') = 'שלום';                  -- unaccent() would return false
SELECT normalize_hebrew('תל־אביב יפו') = 'תל אביב יפו';  -- maqaf became a space
SELECT normalize_hebrew('בע״מ') = 'בעמ';                 -- gershayim removed

-- Use it in the search vector so stored nikud/gershayim do not block matches
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('simple', normalize_hebrew(coalesce(name_he, '')))
  ) STORED;

-- Normalize the query exactly the same way
SELECT * FROM products
WHERE search_vector @@ plainto_tsquery('simple', normalize_hebrew($1));
```

Note: `unaccent` is still useful for Latin diacritics in your English columns, just not for Hebrew. If you do use `unaccent()` (which is `STABLE`), wrap it in an `IMMUTABLE` `f_unaccent(text)` that calls `unaccent('unaccent', $1)` before putting it in a generated column or expression index.

Two indexing rules that follow from this, and that are easy to get wrong:

- **Index the same expression you query.** A `gin_trgm_ops` index on `body_he` does not serve a predicate written against `normalize_hebrew(body_he)` or `coalesce(body_he,'')`. Either match the bare column or build the index over the identical expression, otherwise the predicate degrades to a sequential scan while looking indexed.
- **Each trigram operator has its own threshold GUC**, with deliberately different defaults: `%` reads `pg_trgm.similarity_threshold` (0.3), `<%` reads `pg_trgm.word_similarity_threshold` (0.6), `<<%` reads `pg_trgm.strict_word_similarity_threshold` (0.5). Setting only the first leaves a `<%` branch gated at 0.6 no matter what you thought you configured. Do not paper over that by feeding one value into all three either: `word_similarity` scores the best-matching word extent rather than the whole string, so it runs much higher and a 0.2-0.3 setting there returns near-unrelated rows.

## Currency Handling (NIS / Shekel)

### Column Types for NIS Amounts

Always use `numeric` for monetary values. Never use `float` or `double precision`, as they cause rounding errors:

```sql
-- Correct: numeric with fixed precision
CREATE TABLE invoices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  amount_nis numeric(12, 2) NOT NULL CHECK (amount_nis >= 0),
  vat_amount numeric(12, 2) NOT NULL DEFAULT 0,
  total_nis numeric(12, 2) GENERATED ALWAYS AS (amount_nis + vat_amount) STORED,
  currency text NOT NULL DEFAULT 'ILS' CHECK (currency IN ('ILS', 'USD', 'EUR'))
);

-- Wrong: never do this for money
-- amount float NOT NULL  -- ROUNDING ERRORS!
```

### VAT Calculation

Israeli VAT (Ma'am) is 18% (raised from 17% on 2025-01-01). Store the rate in a config table so it can be updated without a code deploy when the next rate change lands:

```sql
-- A SINGLETON row is the wrong shape. The rate changes (17% to 18% on 2025-01-01,
-- and the next change will come), and a singleton silently re-prices every historical
-- invoice the moment you update it. Keep the history and look the rate up as-of the
-- invoice date, the same way the exchange-rate table does.
CREATE TABLE vat_rates (
  rate numeric(5, 4) NOT NULL,
  effective_from date NOT NULL PRIMARY KEY
);
INSERT INTO vat_rates (rate, effective_from)
VALUES (0.1700, '2013-06-02'), (0.1800, '2025-01-01');

-- Calculate VAT using the rate in force on the invoice's own date
SELECT
  i.amount_nis,
  round(i.amount_nis * v.rate, 2)       AS vat,
  round(i.amount_nis * (1 + v.rate), 2) AS total
FROM invoices i
CROSS JOIN LATERAL (
  SELECT rate FROM vat_rates
  WHERE effective_from <= i.invoice_date
  ORDER BY effective_from DESC
  LIMIT 1
) v;
```

Rate also varies by line, not only by date: an export line is zero-rated and some transactions are exempt, so a single per-invoice rate column cannot represent a mixed invoice. Put the rate on the line item once you have more than one rate class.

### Formatting NIS Amounts

Use PostgreSQL's `to_char` for display formatting:

```sql
SELECT to_char(amount_nis, 'FM999,999,990.00') || ' ₪' AS formatted_amount
FROM invoices;

-- For application code, format in the app layer:
-- JavaScript: new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' }).format(amount)
```

### BOI Exchange Rates

When integrating Bank of Israel exchange rates, store them with their effective date:

```sql
CREATE TABLE exchange_rates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  currency_code text NOT NULL,          -- 'USD', 'EUR', etc.
  rate_to_ils numeric(12, 6) NOT NULL,  -- How many ILS per 1 unit
  effective_date date NOT NULL,
  source text NOT NULL DEFAULT 'BOI',
  fetched_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (currency_code, effective_date)
);

-- Get latest rate for USD
SELECT rate_to_ils FROM exchange_rates
WHERE currency_code = 'USD'
ORDER BY effective_date DESC
LIMIT 1;
```

**Never look a rate up by exact date.** The Bank of Israel publishes no representative rate on Saturdays or Israeli holidays, so `WHERE effective_date = $1` returns zero rows for any Shabbat-dated document, and a `NOT NULL` conversion column then fails the insert. Carry the last published rate forward with an as-of lookup:

```sql
-- Rate in force ON a given date (carries Friday's rate through Shabbat)
SELECT rate_to_ils FROM exchange_rates
WHERE currency_code = 'USD' AND effective_date <= $1
ORDER BY effective_date DESC
LIMIT 1;
```

## Timezone Handling (Asia/Jerusalem)

### Database Configuration

Always store timestamps with timezone and configure the database for Israel:

```sql
-- Set database timezone (do this in your migration or DB config)
ALTER DATABASE your_db SET timezone = 'Asia/Jerusalem';

-- Verify
SHOW timezone;  -- Should return 'Asia/Jerusalem'

-- Always use timestamptz, never timestamp without timezone
CREATE TABLE events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  starts_at timestamptz NOT NULL,  -- CORRECT
  -- starts_at timestamp NOT NULL, -- WRONG: loses timezone info
  created_at timestamptz NOT NULL DEFAULT now()
);
```

### DST Transition Handling

Israel observes daylight saving time (IDT, UTC+3 in summer; IST, UTC+2 in winter). The transition dates change yearly. Key gotchas:

```sql
-- Check current offset
SELECT now(), now() AT TIME ZONE 'Asia/Jerusalem',
       EXTRACT(timezone_hour FROM now()) AS utc_offset;

-- Convert between timezones safely
SELECT starts_at AT TIME ZONE 'Asia/Jerusalem' AS local_time
FROM events;

-- CRITICAL: Friday night Shabbat edge case
-- Shabbat starts at sunset Friday. If scheduling around Shabbat times,
-- do NOT hardcode times. Use a Shabbat times API and store as timestamptz.

-- Find events happening on a specific Israeli date.
-- Do NOT write WHERE (starts_at AT TIME ZONE 'Asia/Jerusalem')::date = '2026-03-14':
-- wrapping the column kills the index on starts_at and forces a sequential scan.
-- Use a half-open range on the bare column instead, computed from the local date.
SELECT * FROM events
WHERE starts_at >= timestamp '2026-03-14 00:00' AT TIME ZONE 'Asia/Jerusalem'
  AND starts_at <  timestamp '2026-03-15 00:00' AT TIME ZONE 'Asia/Jerusalem';
```

### Scheduling Around Israeli Calendar

When building scheduling features, account for:
- Shabbat (Friday sunset to Saturday nightfall): no notifications/processing
- Jewish holidays: variable dates each year
- Israeli business hours: Sunday through Thursday (Friday is half-day)

```sql
-- Check if a timestamp falls on Israeli business hours (Sun-Thu, 9:00-17:00)
CREATE OR REPLACE FUNCTION is_israeli_business_hours(ts timestamptz)
RETURNS boolean AS $$
DECLARE
  local_ts timestamp := ts AT TIME ZONE 'Asia/Jerusalem';
  dow int := EXTRACT(dow FROM local_ts);  -- 0=Sun, 6=Sat
  hour int := EXTRACT(hour FROM local_ts);
BEGIN
  -- Sunday(0) through Thursday(4), 9:00-17:00
  RETURN dow BETWEEN 0 AND 4 AND hour BETWEEN 9 AND 16;
END;
-- STABLE, not IMMUTABLE: AT TIME ZONE on a timestamptz depends on the tz database,
-- so a tzdata update can change the result. Marking it IMMUTABLE would risk wrong
-- cached/indexed values.
$$ LANGUAGE plpgsql STABLE;
```

## Israeli Date Patterns

### Hebrew Calendar Integration

For applications that need Hebrew calendar dates alongside Gregorian, store both:

```sql
CREATE TABLE appointments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  gregorian_date date NOT NULL,
  hebrew_date_display text,  -- e.g., "י״ד אדר ב׳ תשפ״ה"
  scheduled_at timestamptz NOT NULL
);

-- Hebrew date conversion should be done in the application layer
-- (using libraries like hebcal in JavaScript or pyluach in Python)
-- Store the display string for quick rendering
```

### Israeli Date Display Formats

```sql
-- Israeli date format: DD/MM/YYYY (not MM/DD/YYYY)
SELECT to_char(created_at AT TIME ZONE 'Asia/Jerusalem', 'DD/MM/YYYY') AS israeli_date
FROM events;

-- With time
SELECT to_char(
  created_at AT TIME ZONE 'Asia/Jerusalem',
  'DD/MM/YYYY HH24:MI'
) AS israeli_datetime
FROM events;
```

## Supabase-Specific Patterns

### RLS Policies for Multi-Tenant Israeli SaaS

```sql
-- Enable RLS
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Tenant isolation. Read the claim from app_metadata, NOT from the top level and
-- NOT from user_metadata:
--   * Supabase does not put a custom top-level claim in the access token unless you
--     add a custom access token hook, so `auth.jwt() ->> 'tenant_id'` is NULL and the
--     policy fails closed to zero visible rows, which looks like a data bug.
--   * user_metadata is writable by the end user, so reading a tenant id from it is a
--     tenant escape, not a workaround.
-- RESTRICTIVE so a later permissive policy cannot widen it, and TO authenticated so
-- it does not also run for the anon role.
CREATE POLICY tenant_isolation ON invoices
  AS RESTRICTIVE
  TO authenticated
  USING (tenant_id = ((select auth.jwt()) -> 'app_metadata' ->> 'tenant_id')::uuid);

-- Index the column every policy filters on, or each check is a sequential scan.
CREATE INDEX idx_invoices_tenant ON invoices (tenant_id);

-- Admin override (Israeli admin users can see all tenants)
CREATE POLICY admin_access ON invoices
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

-- Read-only for accountant role (common in Israeli business apps)
CREATE POLICY accountant_read ON invoices
  FOR SELECT
  TO authenticated
  USING (
    tenant_id = ((select auth.jwt()) -> 'app_metadata' ->> 'tenant_id')::uuid
    AND EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role IN ('accountant', 'admin')
    )
  );
```

### PostgREST Gotchas with Hebrew

When using Supabase's PostgREST API with Hebrew content:

```sql
-- Column aliases with Hebrew work but require URL encoding
-- Better approach: use English column names, store Hebrew in values

-- Avoid: columns named with Hebrew characters
-- CREATE TABLE test (שם text);  -- DON'T DO THIS

-- Correct: English column names, Hebrew values
CREATE TABLE businesses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name_he text NOT NULL,  -- Hebrew business name
  name_en text,           -- English business name
  business_type text NOT NULL  -- English enum values
);

-- PostgREST filter with Hebrew values (URL-encode the value)
-- GET /businesses?name_he=eq.%D7%97%D7%A0%D7%95%D7%AA
```

### Edge Function + DB Connection Pooling

For Supabase Edge Functions connecting to the database:

```typescript
// In Supabase Edge Functions, always use the pooler connection.
// Direct connection: postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
// Pooled (transaction mode): postgresql://postgres:password@aws-[region].pooler.supabase.com:6543/postgres
// Copy the exact host from the project's Connect dialog; do not hardcode a prefix.

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// The service role key runs as a Postgres role with the bypassrls attribute, so it
// IGNORES every policy above. Never ship it to a browser, and do tenant filtering
// explicitly in any Edge Function that uses it.
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

// For direct SQL queries in Edge Functions, use the pooler
// This avoids connection exhaustion under load
```

## Performance Tuning

### Connection Pooling

For Israeli SaaS apps on Supabase, connection pooling is critical:

- **Supavisor** (Supabase's shared pooler): `aws-[region].pooler.supabase.com` on port **6543** for transaction mode, port **5432** for session mode. Supabase writes the host as the `aws-[region]` placeholder, copy the exact string from your project's Connect dialog rather than hardcoding a prefix.
- **PgBouncer**: available as Supabase's dedicated pooler, and the usual choice when self-hosting.
- **Pool size is not a plan constant.** It is one setting that Supavisor and PgBouncer both reference, capping the server-side connections a pooler opens to Postgres. What varies by compute tier is a separate "max pooler clients" ceiling on how many clients may connect to a pooler at once, alongside your instance's Postgres `max_connections`. Read the current numbers off your own project rather than hardcoding any figure.

### Index Strategies for Hebrew Text

```sql
-- B-tree index for exact Hebrew matches
CREATE INDEX idx_businesses_name_he ON businesses (name_he);

-- GIN trigram for fuzzy search
CREATE INDEX idx_businesses_name_he_trgm
  ON businesses USING gin (name_he gin_trgm_ops);

-- GIN for full-text search
CREATE INDEX idx_businesses_search
  ON businesses USING gin (search_vector);

-- Partial index for published Hebrew content
CREATE INDEX idx_published_he ON products (name_he)
  WHERE is_published = true;
```

### Partitioning by Israeli Fiscal Year

Israel's fiscal year aligns with the calendar year (January to December). For large transaction tables:

```sql
-- Partition invoices by year
CREATE TABLE invoices_partitioned (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  amount_nis numeric(12, 2) NOT NULL,
  invoice_date date NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (invoice_date);

-- Create yearly partitions
CREATE TABLE invoices_2024 PARTITION OF invoices_partitioned
  FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE invoices_2025 PARTITION OF invoices_partitioned
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE invoices_2026 PARTITION OF invoices_partitioned
  FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

## Common Israeli Data Types

### Teudat Zehut (Israeli ID Number)

```sql
-- Store as text (not integer) to preserve leading zeros
-- 9 digits, validated with Luhn-like algorithm
CREATE TABLE customers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  teudat_zehut text UNIQUE CHECK (
    teudat_zehut ~ '^\d{9}$'
  ),
  -- Additional identity fields
  passport_number text,
  tax_id text  -- Osek Murshe / Osek Patur number
);
```

**Note:** The `~ '^\d{9}$'` constraint only checks the format (9 digits), not the check digit. Teudat Zehut uses a Luhn-variant check digit algorithm. This skill ships a ready-made `validate_teudat_zehut(text)` function in `scripts/israeli-data-types.sql`, install it and use it in a `CHECK` constraint or a `BEFORE INSERT` trigger so invalid IDs are rejected at the database layer:

```sql
-- After installing validate_teudat_zehut() from israeli-data-types.sql
ALTER TABLE customers ADD CONSTRAINT chk_teudat_zehut_valid
  CHECK (teudat_zehut IS NULL OR validate_teudat_zehut(teudat_zehut));
```

### Israeli Phone Numbers

```sql
-- Israeli phone. Keep the DB CHECK PERMISSIVE: a too-strict constraint throws on
-- legitimate numbers (1-700/1-800 service lines, 07X VoIP/non-geographic) and blocks
-- inserts in production. Do exact formatting/normalization in the app layer.
ALTER TABLE customers ADD COLUMN phone text CHECK (
  phone ~ '^05\d{8}$'         -- Mobile: 05X + 8 digits (10 total)
  OR phone ~ '^07\d{8}$'      -- VoIP / non-geographic: 07X + 7 digits (10 total)
  OR phone ~ '^0[23489]\d{7}$' -- Landline: area code + 7 digits (9 total)
  OR phone ~ '^1[78]00\d{6}$'  -- Service: 1-700 / 1-800 + 6 digits
  OR phone ~ '^\*\d{3,4}$'     -- Short codes: *XXX or *XXXX
);

-- Or store in E.164 format for international compatibility
ALTER TABLE customers ADD COLUMN phone_e164 text CHECK (
  phone_e164 ~ '^\+972\d{8,9}$'
);
```

### Israeli Address Fields

```sql
CREATE TABLE addresses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  street_he text NOT NULL,      -- Hebrew street name
  street_en text,               -- English transliteration
  house_number text NOT NULL,   -- Text to handle "12/3" or "12א"
  apartment text,               -- Apartment/floor
  city_he text NOT NULL,
  city_en text,
  postal_code text CHECK (postal_code ~ '^\d{7}$'),  -- Israeli: 7 digits
  region text  -- 'north', 'center', 'south', 'jerusalem', 'haifa', 'tel-aviv'
);
```

## Examples

### Example 1: Bilingual product catalog with fuzzy Hebrew search
User says: "I need a products table that supports typo-tolerant search in Hebrew and English."

Actions:
1. `CREATE EXTENSION IF NOT EXISTS pg_trgm;` (and `unaccent` for the English columns), then define the `IMMUTABLE` `normalize_hebrew(text)` function for Hebrew.
2. Create `products` with `name_he`, `name_en`, `description_he`, `description_en`, plus a generated `search_vector` using `to_tsvector('simple', normalize_hebrew(...))` for Hebrew columns and `'english'` for English columns.
3. Add a GIN index on `search_vector` and GIN `gin_trgm_ops` indexes on `name_he` and `name_en`.
4. Query with `plainto_tsquery('simple', normalize_hebrew($1))` for ranked results, OR-ed with `plainto_tsquery('english', $1)` so the stemmed English columns can match too, and fall back to a `name_he % $1` trigram match for typo tolerance.

Result: Users find "חשבונית" even if they type "חשבונ" or include nikud, and English queries still work through the same column.

### Example 2: Israeli invoice table with VAT and ID constraints
User says: "Create an invoices table that enforces correct VAT math and valid Israeli IDs."

Actions:
1. Install `validate_teudat_zehut()` from `scripts/israeli-data-types.sql`.
2. Create `invoices` with `subtotal_nis numeric(12,2)`, `vat_rate numeric(5,4) DEFAULT 0.1800`, `vat_amount numeric(12,2)`, `total_nis numeric(12,2)`.
3. Add `CHECK (vat_amount = round(subtotal_nis * vat_rate, 2))` and `CHECK (total_nis = subtotal_nis + vat_amount)`.
4. Add `customer_teudat_zehut text CHECK (customer_teudat_zehut IS NULL OR validate_teudat_zehut(customer_teudat_zehut))`.
5. Store the VAT rate in the singleton `tax_config` table so a rate change is a data update, not a deploy.

Result: The database itself rejects invoices with wrong VAT arithmetic or malformed Israeli ID numbers.

## Bundled Resources

This skill includes helper scripts in the `scripts/` directory:

- `hebrew-search-setup.sql`: Sets up Hebrew full-text search with proper collation, trigram indexes, and search functions
- `israeli-data-types.sql`: Complete CREATE TABLE templates with Israeli-specific columns, constraints, and validations, including the `validate_teudat_zehut()` and `format_israeli_phone()` helper functions

And reference documents in `references/`:

- `hebrew-collation-guide.md`: Detailed ICU collation reference for Hebrew text in PostgreSQL
- `supabase-israel-patterns.md`: Supabase-specific patterns and configurations for Israeli apps

## Recommended MCP Servers

These MCP servers from the directory pair well with this skill when an Israeli database needs live external data:

- **boi-exchange**: Bank of Israel exchange rates, use to populate the `exchange_rates` table on a schedule instead of hardcoding rates.
- **hebcal**: Hebrew/Jewish calendar dates, use to fill `hebrew_date_display` columns or to drive Shabbat/holiday-aware scheduling logic that would otherwise need hardcoded dates.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| PostgreSQL Collation Support | https://www.postgresql.org/docs/current/collation.html | ICU collations, deterministic vs non-deterministic |
| PostgreSQL 18 release notes | https://www.postgresql.org/docs/release/18.0/ | LIKE now allowed with nondeterministic collations; PK/FK collation rule |
| PostgreSQL pg_trgm | https://www.postgresql.org/docs/current/pgtrgm.html | Trigram operators, similarity threshold, GIN indexes |
| PostgreSQL unaccent | https://www.postgresql.org/docs/current/unaccent.html | Latin diacritic stripping (NOT Hebrew nikud), IMMUTABLE wrapper |
| Supabase Row Level Security | https://supabase.com/docs/guides/database/postgres/row-level-security | RLS policies, auth.jwt(), multi-tenant patterns |
| Bank of Israel exchange rates | https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ | Representative rates for the exchange_rates table |
| ICU Locale identifiers | https://www.postgresql.org/docs/current/collation.html#ICU-CUSTOM-COLLATIONS | BCP-47 locale syntax for CREATE COLLATION (he-IL, he-IL-u-ks-level1) |

## Troubleshooting

### Error: "nondeterministic collations are not supported for ILIKE" (or "... for regular expressions")
Cause: A column declared with the non-deterministic `hebrew_icu` collation is being used with `ILIKE` or a regex operator. Both still error on PostgreSQL 18. Plain `LIKE` on the same column raised the equivalent error up to PostgreSQL 17 and was allowed in 18.
Solution: Do the match against a deterministic expression, `WHERE name_he COLLATE "default" ILIKE 'שלום%'`, or keep a separate deterministic column (or a `pg_trgm` GIN index) for prefix and fuzzy search. Note that even where `LIKE` is now accepted, the planner uses the index only as a filter, so a `pg_trgm` index remains the faster route for prefix search. `UNIQUE` constraints and plain `btree` indexes are fine on a non-deterministic column, they simply lose B-tree deduplication.

### Error: "generation expression is not immutable" when adding a search_vector column
Cause: `unaccent()` is `STABLE`, not `IMMUTABLE`, so it cannot be used directly inside a `GENERATED ALWAYS AS ... STORED` expression.
Solution: Create an `IMMUTABLE` SQL wrapper, `CREATE FUNCTION f_unaccent(text) RETURNS text AS $$ SELECT unaccent('unaccent', $1) $$ LANGUAGE sql IMMUTABLE;`, and use `f_unaccent(...)` in the generated column and any expression index.

## Gotchas

- Hebrew text in PostgreSQL requires UTF-8 encoding. Databases created with SQL_ASCII or LATIN1 encoding will corrupt Hebrew characters. Always verify encoding with SHOW server_encoding.
- Hebrew collation in PostgreSQL (he_IL.UTF-8) sorts differently than English. Agents may apply default collation that sorts Hebrew text incorrectly in ORDER BY queries.
- PostgreSQL has no Hebrew full-text search dictionary, so `simple` IS the correct configuration for Hebrew tsvector columns. Agents often wrongly reach for `'english'` (which strips English stopwords and stems Latin words, doing nothing useful for Hebrew) or invent a nonexistent `'hebrew'` config (which errors out). Use `'simple'` for Hebrew columns and combine it with `pg_trgm` and `normalize_hebrew()` for better recall (`unaccent` does not help Hebrew recall, it leaves nikud intact). Note `'simple'` does no stemming, so Hebrew prefixes (ו/ב/כ/ל/ה/מ/ש) and plural/construct forms become distinct lexemes, measured recall was 1 of 3 rows; always pair FTS with a `<%` trigram branch over the SAME columns, including body columns, or inflected hits are lost.
- The default FTS parser treats gershayim (U+05F4) as a blank, so `בע״מ` becomes the two lexemes `בע` and `מ` while users type `בעמ`. Agents store the typographically correct character (which is right) and then never normalize it for search (which breaks every acronym: בע״מ, צה״ל, ד״ר, ח״כ, ש״ח). Strip geresh and gershayim on both the stored and query side.
- Do not strip the whole U+0591-U+05C7 range to remove nikud. It contains U+05BE MAQAF, a word-separating dash, so `תל־אביב` collapses into the single lexeme `תלאביב` and `תל אביב` stops matching. Strip the combining marks only and map the separators to spaces.
- Israeli date columns should store dates as DATE or TIMESTAMPTZ (with timezone Asia/Jerusalem), not as TEXT in DD/MM/YYYY format. Agents may create text columns for dates, breaking comparisons and sorting.