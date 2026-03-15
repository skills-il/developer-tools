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

# ערכת כלים לפוסטגרס ישראלי

שיטות עבודה מומלצות, תבניות וסקריפטים לבניית בסיסי נתונים PostgreSQL שמותאמים לאפליקציות ישראליות. כולל טיפול בטקסט עברי, מטבע שקל, אזורי זמן ישראליים, אינטגרציה עם Supabase, וטיפוסי נתונים ישראליים נפוצים.

## אינדוקס טקסט בעברית

### הגדרת ICU Collation לעברית

פוסטגרס תומך ב-ICU collation למיון נכון של טקסט עברי. תמיד צרו collation עברי לעמודות שמכילות טקסט בעברית:

```sql
-- יצירת collation עברי
CREATE COLLATION IF NOT EXISTS hebrew_icu (
  provider = icu,
  locale = 'he-IL-x-icu',
  deterministic = false
);

-- שימוש בעמודות
CREATE TABLE products (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name_he text COLLATE hebrew_icu NOT NULL,
  name_en text NOT NULL
);

-- או בזמן שאילתה
SELECT * FROM products ORDER BY name_he COLLATE hebrew_icu;
```

**חשוב:** Collation לא דטרמיניסטי (שנדרש למיון עברי תקין) לא עובד עם אילוצי `UNIQUE` או אינדקסים מסוג `btree` ישירות. השתמשו ב-collation דטרמיניסטי לייחודיות וב-ICU collation להצגה.

### חיפוש מטושטש בעברית עם Trigram

התוסף `pg_trgm` עובד טוב לחיפוש מטושטש בעברית, ומאפשר למצוא תוצאות גם עם שגיאות כתיב קלות:

```sql
-- הפעלת תוסף trigram
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- יצירת אינדקס GIN trigram על עמודות עבריות
CREATE INDEX idx_products_name_he_trgm
  ON products USING gin (name_he gin_trgm_ops);

-- שאילתת חיפוש מטושטש
SELECT name_he, similarity(name_he, 'חשבונ') AS sim
FROM products
WHERE name_he % 'חשבונ'
ORDER BY sim DESC
LIMIT 10;

-- התאמת סף דמיון (ברירת מחדל 0.3)
SET pg_trgm.similarity_threshold = 0.2;
```

### חיפוש טקסט מלא בעברית

חיפוש הטקסט המלא של פוסטגרס משתמש בקונפיגורציית `simple` לעברית (כי אין מילון עברי ייעודי). לתוצאות טובות יותר, שלבו עם `pg_trgm`:

```sql
-- הוספת עמודת וקטור חיפוש
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(name_he, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(description_he, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(name_en, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description_en, '')), 'B')
  ) STORED;

-- יצירת אינדקס GIN
CREATE INDEX idx_products_search ON products USING gin (search_vector);

-- שאילתת חיפוש (תומכת גם בעברית וגם באנגלית)
SELECT * FROM products
WHERE search_vector @@ plainto_tsquery('simple', 'חשבונית')
ORDER BY ts_rank(search_vector, plainto_tsquery('simple', 'חשבונית')) DESC;
```

## טיפול במטבע (שקל / NIS)

### טיפוסי עמודות לסכומים בשקלים

תמיד השתמשו ב-`numeric` לערכים כספיים. לעולם אל תשתמשו ב-`float` או `double precision` כי הם גורמים לשגיאות עיגול:

```sql
-- נכון: numeric עם דיוק קבוע
CREATE TABLE invoices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  amount_nis numeric(12, 2) NOT NULL CHECK (amount_nis >= 0),
  vat_amount numeric(12, 2) NOT NULL DEFAULT 0,
  total_nis numeric(12, 2) GENERATED ALWAYS AS (amount_nis + vat_amount) STORED,
  currency text NOT NULL DEFAULT 'ILS' CHECK (currency IN ('ILS', 'USD', 'EUR'))
);

-- לא נכון: לעולם אל תעשו ככה עם כסף
-- amount float NOT NULL  -- שגיאות עיגול!
```

### חישוב מע"מ

מע"מ בישראל עומד על 18% נכון ל-2025. שמרו את השיעור בטבלת קונפיגורציה כדי שאפשר יהיה לעדכן:

```sql
CREATE TABLE tax_config (
  id int PRIMARY KEY DEFAULT 1 CHECK (id = 1),  -- שורה יחידה
  vat_rate numeric(5, 4) NOT NULL DEFAULT 0.1800,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- חישוב מע"מ
SELECT
  amount_nis,
  round(amount_nis * (SELECT vat_rate FROM tax_config), 2) AS vat,
  round(amount_nis * (1 + (SELECT vat_rate FROM tax_config)), 2) AS total
FROM invoices;
```

### עיצוב סכומים בשקלים

```sql
SELECT to_char(amount_nis, 'FM999,999,990.00') || ' ₪' AS formatted_amount
FROM invoices;

-- בקוד אפליקציה, עצבו בשכבת האפליקציה:
-- JavaScript: new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' }).format(amount)
```

### שערי חליפין של בנק ישראל

כשמשלבים שערי חליפין של בנק ישראל, שמרו אותם עם תאריך התוקף:

```sql
CREATE TABLE exchange_rates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  currency_code text NOT NULL,
  rate_to_ils numeric(12, 6) NOT NULL,
  effective_date date NOT NULL,
  source text NOT NULL DEFAULT 'BOI',
  fetched_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (currency_code, effective_date)
);
```

## טיפול באזור זמן (Asia/Jerusalem)

### קונפיגורציית בסיס הנתונים

תמיד שמרו timestamps עם timezone והגדירו את בסיס הנתונים לישראל:

```sql
-- הגדרת אזור הזמן (עשו זאת במיגרציה או בקונפיגורציה)
ALTER DATABASE your_db SET timezone = 'Asia/Jerusalem';

-- תמיד השתמשו ב-timestamptz, לעולם לא ב-timestamp בלי timezone
CREATE TABLE events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  starts_at timestamptz NOT NULL,  -- נכון
  -- starts_at timestamp NOT NULL, -- לא נכון: מאבד מידע על timezone
  created_at timestamptz NOT NULL DEFAULT now()
);
```

### טיפול במעבר שעון קיץ/חורף

ישראל מפעילה שעון קיץ (IDT, UTC+3 בקיץ; IST, UTC+2 בחורף). תאריכי המעבר משתנים מדי שנה:

```sql
-- בדיקת offset נוכחי
SELECT now(), now() AT TIME ZONE 'Asia/Jerusalem',
       EXTRACT(timezone_hour FROM now()) AS utc_offset;

-- המרה בטוחה בין אזורי זמן
SELECT starts_at AT TIME ZONE 'Asia/Jerusalem' AS local_time
FROM events;

-- קריטי: מקרה קצה של ליל שבת
-- שבת נכנסת בשקיעה ביום שישי. אם מתזמנים סביב זמני שבת,
-- אל תקשיחו זמנים בקוד. השתמשו ב-API של זמני שבת ושמרו כ-timestamptz.

-- מציאת אירועים בתאריך ישראלי מסוים
SELECT * FROM events
WHERE (starts_at AT TIME ZONE 'Asia/Jerusalem')::date = '2025-03-14';
```

### בדיקת שעות פעילות ישראליות

```sql
-- בדיקה אם timestamp נופל בשעות עבודה ישראליות (א'-ה', 9:00-17:00)
CREATE OR REPLACE FUNCTION is_israeli_business_hours(ts timestamptz)
RETURNS boolean AS $$
DECLARE
  local_ts timestamp := ts AT TIME ZONE 'Asia/Jerusalem';
  dow int := EXTRACT(dow FROM local_ts);  -- 0=ראשון, 6=שבת
  hour int := EXTRACT(hour FROM local_ts);
BEGIN
  -- ראשון(0) עד חמישי(4), 9:00-17:00
  RETURN dow BETWEEN 0 AND 4 AND hour BETWEEN 9 AND 16;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

## תאריכים ישראליים

### אינטגרציה עם הלוח העברי

לאפליקציות שצריכות תאריכים עבריים לצד לועזיים:

```sql
CREATE TABLE appointments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  gregorian_date date NOT NULL,
  hebrew_date_display text,  -- למשל "י״ד אדר ב׳ תשפ״ה"
  scheduled_at timestamptz NOT NULL
);

-- המרת תאריך עברי צריכה להתבצע בשכבת האפליקציה
-- (באמצעות ספריות כמו hebcal ב-JavaScript או pyluach ב-Python)
```

### פורמטים ישראליים לתאריכים

```sql
-- פורמט ישראלי: DD/MM/YYYY (לא MM/DD/YYYY)
SELECT to_char(created_at AT TIME ZONE 'Asia/Jerusalem', 'DD/MM/YYYY') AS israeli_date
FROM events;

-- עם שעה
SELECT to_char(
  created_at AT TIME ZONE 'Asia/Jerusalem',
  'DD/MM/YYYY HH24:MI'
) AS israeli_datetime
FROM events;
```

## תבניות ספציפיות ל-Supabase

### מדיניות RLS ל-SaaS ישראלי רב-דיירים

```sql
-- הפעלת RLS
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- מדיניות בידוד דיירים
CREATE POLICY tenant_isolation ON invoices
  USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- גישת מנהל (מנהלים ישראלים רואים את כל הדיירים)
CREATE POLICY admin_access ON invoices
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

-- קריאה בלבד לרואה חשבון (נפוץ באפליקציות עסקיות ישראליות)
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

### מלכודות PostgREST עם עברית

כשמשתמשים ב-API של PostgREST עם תוכן עברי:

```sql
-- שמות עמודות בעברית עובדים אבל דורשים URL encoding
-- גישה מומלצת: שמות עמודות באנגלית, ערכים בעברית

-- הימנעו: עמודות עם שמות בעברית
-- CREATE TABLE test (שם text);  -- אל תעשו את זה

-- נכון: שמות עמודות באנגלית, ערכים בעברית
CREATE TABLE businesses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name_he text NOT NULL,
  name_en text,
  business_type text NOT NULL
);
```

## ביצועים ואופטימיזציה

### אסטרטגיות אינדוקס לטקסט עברי

```sql
-- אינדקס B-tree להתאמה מדויקת
CREATE INDEX idx_businesses_name_he ON businesses (name_he);

-- GIN trigram לחיפוש מטושטש
CREATE INDEX idx_businesses_name_he_trgm
  ON businesses USING gin (name_he gin_trgm_ops);

-- GIN לחיפוש טקסט מלא
CREATE INDEX idx_businesses_search
  ON businesses USING gin (search_vector);

-- אינדקס חלקי לתוכן עברי מפורסם בלבד
CREATE INDEX idx_published_he ON products (name_he)
  WHERE is_published = true;
```

### חלוקה לפי שנת מס ישראלית

שנת המס בישראל תואמת לשנה הקלנדרית (ינואר עד דצמבר). לטבלאות עסקאות גדולות:

```sql
CREATE TABLE invoices_partitioned (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  amount_nis numeric(12, 2) NOT NULL,
  invoice_date date NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (invoice_date);

CREATE TABLE invoices_2024 PARTITION OF invoices_partitioned
  FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE invoices_2025 PARTITION OF invoices_partitioned
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

## טיפוסי נתונים ישראליים נפוצים

### תעודת זהות

```sql
-- שמירה כטקסט (לא מספר שלם) כדי לשמור אפסים מובילים
-- 9 ספרות, מאומת עם אלגוריתם ספרת ביקורת
CREATE TABLE customers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  teudat_zehut text UNIQUE CHECK (
    teudat_zehut ~ '^\d{9}$'
  ),
  passport_number text,
  tax_id text  -- מספר עוסק מורשה / עוסק פטור
);
```

### מספרי טלפון ישראליים

```sql
ALTER TABLE customers ADD COLUMN phone text CHECK (
  phone ~ '^05\d{8}$'           -- נייד: 05X-XXXXXXX (10 ספרות)
  OR phone ~ '^0[2-9]\d{7}$'    -- קווי: 0X-XXXXXXX (9 ספרות)
  OR phone ~ '^\*\d{4}$'        -- מספרים קצרים: *XXXX
);
```

### שדות כתובת ישראלית

```sql
CREATE TABLE addresses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  street_he text NOT NULL,
  street_en text,
  house_number text NOT NULL,   -- טקסט כדי לטפל ב-"12/3" או "12א"
  apartment text,
  city_he text NOT NULL,
  city_en text,
  postal_code text CHECK (postal_code ~ '^\d{7}$'),  -- מיקוד: 7 ספרות
  region text
);
```

## סקריפטים ומסמכי עזר

הסקיל הזה כולל סקריפטים בתיקיית `scripts/`:

- `hebrew-search-setup.sql`: הגדרת חיפוש טקסט מלא בעברית עם collation, אינדקסים ופונקציות
- `israeli-data-types.sql`: תבניות CREATE TABLE עם עמודות, אילוצים ואימותים ישראליים

ומסמכי עזר בתיקיית `references/`:

- `hebrew-collation-guide.md`: מדריך ICU collation לטקסט עברי בפוסטגרס
- `supabase-israel-patterns.md`: תבניות ספציפיות ל-Supabase לאפליקציות ישראליות
