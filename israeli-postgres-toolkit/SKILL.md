---
name: israeli-postgres-toolkit
description: >-
  Best practices for PostgreSQL in Israeli apps, covering Supabase patterns,
  Hebrew text indexing with ICU collation, shekel/NIS currency handling,
  Israeli date formats, and Asia/Jerusalem timezone gotchas. Use when user
  asks to "set up Hebrew full-text search", "handle NIS currency in Postgres",
  "tipul b'ivrit b'database", or configure Israeli-specific database patterns.
  Includes performance tuning, RLS policies for multi-tenant Israeli SaaS,
  and common Israeli data type validations. Do NOT use for general PostgreSQL
  administration unrelated to Israeli requirements, or for non-PostgreSQL databases.
license: MIT
allowed-tools: 'Bash(python:*), Bash(psql:*)'
compatibility: 'No special requirements. Works with Claude Code, Cursor, Windsurf.'
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    he:
      - פוסטגרס
      - בסיס-נתונים
      - עברית
      - סופאבייס
      - ישראל
    en:
      - postgres
      - database
      - hebrew
      - supabase
      - israel
  display_name:
    he: "ערכת כלים לפוסטגרס ישראלי"
    en: Israeli Postgres Toolkit
  display_description:
    he: >-
      שיטות עבודה מומלצות לפוסטגרס באפליקציות ישראליות, כולל תבניות Supabase,
      אינדוקס טקסט בעברית עם ICU collation, טיפול במטבע שקל, פורמטים ישראליים
      לתאריכים, ומלכודות אזור זמן Asia/Jerusalem.
    en: >-
      Best practices for PostgreSQL in Israeli apps, covering Supabase patterns,
      Hebrew text indexing with ICU collation, shekel/NIS currency handling,
      Israeli date formats, and Asia/Jerusalem timezone gotchas.
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
---

# Israeli Postgres Toolkit

Best practices, patterns, and scripts for building PostgreSQL databases tailored to Israeli applications. Covers Hebrew text handling, NIS currency, Israeli timezones, Supabase integration, and common Israeli data types.

## Hebrew Text Indexing

### ICU Collation for Hebrew

PostgreSQL supports ICU collations for proper Hebrew text sorting. Always create a Hebrew collation for columns that store Hebrew text:

```sql
-- Create Hebrew ICU collation
CREATE COLLATION IF NOT EXISTS hebrew_icu (
  provider = icu,
  locale = 'he-IL-x-icu',
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

**Important:** Non-deterministic collations (required for proper Hebrew sorting) cannot be used with `UNIQUE` constraints or `btree` indexes directly. Use a deterministic collation for uniqueness and the ICU collation for display ordering.

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

### Full-Text Search with Hebrew

PostgreSQL's built-in full-text search uses the `simple` configuration for Hebrew (since there is no dedicated Hebrew dictionary). For better results, combine with `pg_trgm`:

```sql
-- Add search vector column
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(name_he, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(description_he, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(name_en, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description_en, '')), 'B')
  ) STORED;

-- Create GIN index
CREATE INDEX idx_products_search ON products USING gin (search_vector);

-- Search query (handles both Hebrew and English)
SELECT * FROM products
WHERE search_vector @@ plainto_tsquery('simple', 'חשבונית')
ORDER BY ts_rank(search_vector, plainto_tsquery('simple', 'חשבונית')) DESC;
```

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

Israeli VAT (Ma'am) is 18% as of 2025. Store the rate in a config table so it can be updated:

```sql
CREATE TABLE tax_config (
  id int PRIMARY KEY DEFAULT 1 CHECK (id = 1),  -- singleton row
  vat_rate numeric(5, 4) NOT NULL DEFAULT 0.1800,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Calculate VAT
SELECT
  amount_nis,
  round(amount_nis * (SELECT vat_rate FROM tax_config), 2) AS vat,
  round(amount_nis * (1 + (SELECT vat_rate FROM tax_config)), 2) AS total
FROM invoices;
```

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

-- Find events happening on a specific Israeli date
SELECT * FROM events
WHERE (starts_at AT TIME ZONE 'Asia/Jerusalem')::date = '2025-03-14';
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
$$ LANGUAGE plpgsql IMMUTABLE;
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

-- Tenant isolation policy
CREATE POLICY tenant_isolation ON invoices
  USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Admin override (Israeli admin users can see all tenants)
CREATE POLICY admin_access ON invoices
  FOR ALL
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
  USING (
    tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
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
// In Supabase Edge Functions, always use the pooler connection
// Direct connection: postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
// Pooled connection: postgresql://postgres:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Use the service role client for Edge Functions
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

- **Supavisor** (Supabase's built-in pooler): Use port 6543 for transaction mode
- **PgBouncer**: If self-hosting, configure for transaction pooling
- Set `pool_size` based on your Supabase plan (Free: 60, Pro: 200)

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

**Note:** Teudat Zehut has a check digit algorithm. Validate in application code before inserting.

### Israeli Phone Numbers

```sql
-- Israeli phone: 10 digits starting with 05 (mobile) or 0 (landline)
ALTER TABLE customers ADD COLUMN phone text CHECK (
  phone ~ '^05\d{8}$'    -- Mobile: 05X-XXXXXXX (10 digits)
  OR phone ~ '^0[2-9]\d{7}$'  -- Landline: 0X-XXXXXXX (9 digits)
  OR phone ~ '^\*\d{4}$'  -- Short numbers: *XXXX
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

## Reference Scripts

This skill includes helper scripts in the `scripts/` directory:

- `hebrew-search-setup.sql`: Sets up Hebrew full-text search with proper collation, trigram indexes, and search functions
- `israeli-data-types.sql`: Complete CREATE TABLE templates with Israeli-specific columns, constraints, and validations

And reference documents in `references/`:

- `hebrew-collation-guide.md`: Detailed ICU collation reference for Hebrew text in PostgreSQL
- `supabase-israel-patterns.md`: Supabase-specific patterns and configurations for Israeli apps
