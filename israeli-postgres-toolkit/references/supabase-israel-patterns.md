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
CREATE EXTENSION IF NOT EXISTS pgcrypto;     -- UUID generation
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

**SMS Providers:** Supabase uses Twilio by default. Verify Twilio supports Israeli numbers and set the sender ID appropriately.

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

-- Only admins can modify
CREATE POLICY admin_write ON articles
  FOR ALL
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
import { serve } from 'https://deno.land/std/http/server.ts'

serve(async (req: Request) => {
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
serve(async (req: Request) => {
  // Israeli payment providers often send windows-1255 encoded data
  const body = await req.text()

  // Verify webhook signature (provider-specific)
  const signature = req.headers.get('x-webhook-signature')

  // Process payment notification
  // Israeli payment amounts are in agorot (1/100 shekel)
  // Convert: amount_nis = webhook_amount / 100

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
-- Materialized view for sorted business directory
CREATE MATERIALIZED VIEW businesses_sorted AS
SELECT * FROM businesses
WHERE is_active = true
ORDER BY name_he COLLATE hebrew_icu;

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY businesses_sorted;
```

### Supabase Plan Considerations

For Israeli SaaS applications:

- **Free tier**: 500MB database, suitable for MVP
- **Pro tier**: 8GB, enough for most Israeli startups
- **Connection limit**: Free (60), Pro (200). Use pooler mode for Edge Functions.
- **Region**: Choose `eu-central-1` (Frankfurt) for lowest latency to Israel (~30ms)

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
