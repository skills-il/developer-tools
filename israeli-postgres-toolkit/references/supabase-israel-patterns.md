# Supabase Patterns for Israeli Apps

## Overview

This guide covers Supabase-specific patterns and configurations for building Israeli applications. Includes RLS policies, Edge Function patterns, authentication setup, and performance optimization.

## Database Configuration

### Timezone Setup

Set the database timezone to Israel:

```sql
-- In a migration file
ALTER DATABASE postgres SET timezone = 'Asia/Jerusalem';

-- Verify after restart
SHOW timezone;
```

**Note:** Supabase projects default to UTC. Always set to Asia/Jerusalem if your application primarily serves Israeli users.

### Extensions for Israeli Apps

```sql
-- Enable commonly needed extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- Fuzzy Hebrew search
-- UUIDs need NO extension: gen_random_uuid() is in PostgreSQL core since v13
-- (pgcrypto's copy is obsolete). Enable pgcrypto only for digest()/hmac()/crypt().
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;  -- Query performance
```

## Authentication

### Israeli Phone Auth

Supabase supports phone auth (OTP via SMS). For Israeli numbers:

```typescript
// Sign in with Israeli phone number
const { data, error } = await supabase.auth.signInWithOtp({
  phone: '+972501234567',  // Always E.164 format
})
```

**SMS Providers:** Supabase phone auth is backed by a third-party SMS provider you configure per project (Twilio is one of the supported options). Check which providers your project offers, confirm the one you pick delivers to Israeli numbers, and set the sender ID appropriately.

### Social Auth for Israeli Users

Configure multiple providers for Israeli audience:

- **Google**: Most popular in Israel. Configure Hebrew locale in OAuth consent screen.
- **GitHub**: Common for developer-facing apps.
- **Apple**: Required if you have an iOS app.

```sql
-- After auth, create profile with Israeli defaults
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, preferred_language, timezone)
  VALUES (
    NEW.id,
    'he',                  -- Default to Hebrew
    'Asia/Jerusalem'       -- Default timezone
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## RLS Policies

### Multi-Tenant Israeli SaaS

Common pattern for Israeli B2B SaaS (accounting software, CRM, etc.):

```sql
-- Tenant isolation
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Users see only their tenant's data
CREATE POLICY tenant_select ON invoices
  FOR SELECT
  USING (tenant_id = (auth.jwt() -> 'app_metadata' ->> 'tenant_id')::uuid);

-- Role-based within tenant
CREATE POLICY accountant_crud ON invoices
  FOR ALL
  USING (
    tenant_id = (auth.jwt() -> 'app_metadata' ->> 'tenant_id')::uuid
    AND (auth.jwt() -> 'app_metadata' ->> 'role') IN ('admin', 'accountant')
  );

-- Read-only for regular employees
CREATE POLICY employee_read ON invoices
  FOR SELECT
  USING (
    tenant_id = (auth.jwt() -> 'app_metadata' ->> 'tenant_id')::uuid
    AND (auth.jwt() -> 'app_metadata' ->> 'role') = 'employee'
  );
```

### Public Bilingual Content

For content that should be readable by everyone but only editable by admins:

```sql
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Anyone can read published content
CREATE POLICY public_read ON articles
  FOR SELECT
  USING (is_published = true);

-- Only admins can modify.
-- Note: a FOR ALL policy needs WITH CHECK to constrain what a row may become.
-- When WITH CHECK is omitted PostgreSQL reuses the USING expression, which is
-- what you want here but is worth stating rather than relying on. Add an explicit
-- `TO authenticated` on any policy that should not also apply to the anon role.
CREATE POLICY admin_write ON articles
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );
```

## PostgREST API Patterns

### Filtering Hebrew Content

```typescript
// Supabase client filtering with Hebrew values
const { data } = await supabase
  .from('businesses')
  .select('*')
  .eq('city_he', 'תל אביב')
  .order('name_he')

// Text search in Hebrew
const { data } = await supabase
  .from('businesses')
  .select('*')
  .textSearch('search_vector', 'חשבונאות', {
    config: 'simple'  // Use 'simple' for Hebrew
  })
```

### Column Naming Conventions

Always use English column names, store Hebrew in values:

```sql
-- Correct
CREATE TABLE products (
  name_he text NOT NULL,
  name_en text,
  description_he text,
  description_en text
);

-- Incorrect (causes PostgREST URL encoding issues)
CREATE TABLE products (
  "שם" text NOT NULL,
  "תיאור" text
);
```

### Bilingual API Responses

Use PostgREST computed columns for locale-aware responses:

```sql
-- Create a function that returns content based on locale
CREATE OR REPLACE FUNCTION get_localized_name(
  item products,
  locale text DEFAULT 'he'
)
RETURNS text AS $$
BEGIN
  IF locale = 'en' AND item.name_en IS NOT NULL THEN
    RETURN item.name_en;
  END IF;
  RETURN item.name_he;
END;
$$ LANGUAGE plpgsql STABLE;
```

## Edge Functions

### Hebrew Response Headers

Set proper headers for Hebrew content in Edge Functions:

```typescript
// Use the built-in Deno.serve. The old std/http/server.ts serve() is marked
// @deprecated in the current std release ("Use Deno.serve instead"), and the
// unpinned std/ URL floats to whatever version is latest.
Deno.serve(async (req: Request) => {
  return new Response(
    JSON.stringify({ message: 'שלום עולם' }),
    {
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Language': 'he',
      },
    }
  )
})
```

### Connection Pooling

Always use the pooled connection string in Edge Functions:

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// The Supabase client handles pooling automatically
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

// For direct SQL (if needed), use the pooler endpoint on port 6543
// NOT the direct connection on port 5432
```

### Webhook for Israeli Payment Providers

Common pattern for handling webhooks from Israeli payment providers (Cardcom, Tranzila, etc.):

```typescript
Deno.serve(async (req: Request) => {
  // Some older Israeli payment integrations still send windows-1255 rather than
  // UTF-8. Confirm the encoding against the provider's own docs before decoding.
  const body = await req.text()

  // Signature verification is provider-specific. Do NOT assume a header name:
  // providers differ (some sign a header, some put a key in the body, some use
  // GET query parameters rather than a JSON POST). Read that provider's docs.
  //
  // The amount UNIT is also provider-specific and getting it wrong is a 100x
  // financial error. Some send agorot (1/100 shekel), others send decimal
  // shekels. Verify against the provider's API reference before dividing by 100.

  return new Response('OK', { status: 200 })
})
```

## Storage

### Hebrew File Names

Supabase Storage handles Hebrew file names but URL-encodes them:

```typescript
// Upload with Hebrew filename
const { data, error } = await supabase.storage
  .from('documents')
  .upload('חשבוניות/2025/חשבונית-001.pdf', file)

// The path will be URL-encoded in the public URL
// Use the download method for proper filename in Content-Disposition
```

### File Organization for Israeli Business

```
documents/
  invoices/        -- חשבוניות
    2025/
  receipts/        -- קבלות
    2025/
  contracts/       -- חוזים
  tax-reports/     -- דוחות מס
    annual/
    vat-monthly/
```

## Performance Tips

### Israeli Locale Sorting Performance

Hebrew collation sorts are slower than default binary sorts. Optimize:

1. **Cache sorted results** in a materialized view for frequently accessed data
2. **Use partial indexes** for common filters (e.g., city, region)
3. **Limit result sets** before sorting

```sql
-- Materialized view for sorted business directory.
-- Store an explicit sort key: a matview's own ORDER BY does not guarantee the
-- order of a later SELECT, so consumers must still ORDER BY something.
CREATE MATERIALIZED VIEW businesses_sorted AS
SELECT *, row_number() OVER (ORDER BY name_he COLLATE hebrew_icu) AS sort_key
FROM businesses
WHERE is_active = true;

-- CONCURRENTLY requires a UNIQUE index with no WHERE clause on the view.
-- Without it the refresh fails with:
--   ERROR: cannot refresh materialized view "public.businesses_sorted" concurrently
CREATE UNIQUE INDEX businesses_sorted_pkey ON businesses_sorted (id);

-- Refresh periodically (readers are not blocked)
REFRESH MATERIALIZED VIEW CONCURRENTLY businesses_sorted;

-- Read it back in order
SELECT * FROM businesses_sorted ORDER BY sort_key;
```

### Supabase Plan Considerations

For Israeli SaaS applications:

- **Storage and compute quotas** vary by plan and are revised regularly. Read the current limits from supabase.com/pricing or your project's usage page rather than from a document like this one.
- **Connections**: pool size is not a plan constant. It is a single setting that Supavisor and PgBouncer both reference, capping the server-side connections a pooler opens to Postgres. The tier-dependent ceiling is a separate "max pooler clients" limit on concurrent clients, plus your compute instance's `max_connections`. Read both off your own project instead of hardcoding a number. Use pooler mode for Edge Functions.
- **Region**: pick the closest available region to your users and measure it, rather than trusting a quoted latency figure. `eu-central-1` (Frankfurt) is the usual European choice for Israeli traffic.

### Realtime for Hebrew Content

Supabase Realtime works with Hebrew content out of the box:

```typescript
const channel = supabase
  .channel('hebrew-updates')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'messages' },
    (payload) => {
      console.log('New message:', payload.new.content_he)
    }
  )
  .subscribe()
```
