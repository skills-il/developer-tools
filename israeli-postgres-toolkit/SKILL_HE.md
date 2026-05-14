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
---

# ערכת כלים לפוסטגרס ישראלי

שיטות עבודה מומלצות, תבניות וסקריפטים לבניית בסיסי נתונים PostgreSQL שמותאמים לאפליקציות ישראליות. כולל טיפול בטקסט עברי, מטבע שקל, אזורי זמן ישראליים, אינטגרציה עם Supabase, וטיפוסי נתונים ישראליים נפוצים.

## הוראות

עבדו לפי הסדר הזה כשמקימים או סוקרים בסיס נתונים PostgreSQL לאפליקציה ישראלית:

1. **קודם כל בדקו קידוד ואזור זמן.** הריצו `SHOW server_encoding;` (חייב להיות `UTF8`, לעולם לא `SQL_ASCII` או `LATIN1`) ו-`SHOW timezone;`. הגדירו את אזור הזמן עם `ALTER DATABASE your_db SET timezone = 'Asia/Jerusalem';`. טעות בשניים האלה משחיתה עברית ומסיטה כל timestamp, ותיקון מאוחר מחייב מיגרציית נתונים.
2. **בחרו אסטרטגיית collation.** החליטו לכל עמודה אם צריך מיון תצוגה עברי (ICU לא דטרמיניסטי, `he-IL-x-icu`) או ייחודיות ואינדקס `btree` (collation דטרמיניסטי). בדרך כלל צריך את שניהם, על עמודות שונות או באמצעות אינדקסים נפרדים, כי collation לא דטרמיניסטי לא יכול לגבות אילוץ `UNIQUE` או אינדקס `btree` רגיל.
3. **בחרו גישת חיפוש.** להתאמה מדויקת ולתחילית השתמשו ב-`btree`. לחיפוש מטושטש וסובלני לשגיאות בעברית השתמשו ב-`pg_trgm`. לחיפוש מדורג רב-שדות השתמשו בחיפוש טקסט מלא עם הקונפיגורציה `simple` (ראו "חיפוש טקסט מלא בעברית" למטה). שלבו את `unaccent` כשצריך התאמה שמתעלמת מניקוד.
4. **החילו אילוצים על טיפוסי נתונים ישראליים.** השתמשו באילוצי ה-`CHECK` ובפונקציות העזר מ-`scripts/israeli-data-types.sql` (תעודת זהות, טלפון, מיקוד, מספר עוסק, IBAN) וקראו ל-`validate_teudat_zehut()` לבדיקת ספרת הביקורת של תעודת הזהות במקום לממש אותה מחדש בקוד האפליקציה.

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

### התאמה ללא ניקוד עם unaccent

טקסט עברי לפעמים נושא ניקוד שמשתמשים לא יקלידו בתיבת חיפוש. התוסף `unaccent` מסיר ניקוד (וגם דיאקריטיקה לטינית) כך ש"שָׁלוֹם" ו"שלום" מתאימים:

```sql
-- הפעלת unaccent
CREATE EXTENSION IF NOT EXISTS unaccent;

-- unaccent מסיר ניקוד עברי
SELECT unaccent('שָׁלוֹם');  -- מחזיר 'שלום'

-- שימוש בו ב-search vector כדי שניקוד שמור לא יחסום התאמות
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('simple', unaccent(coalesce(name_he, '')))
  ) STORED;

-- ומפעילים unaccent על השאילתה באותו אופן
SELECT * FROM products
WHERE search_vector @@ plainto_tsquery('simple', unaccent('שָׁלוֹם'));
```

הערה: `unaccent()` הוא `STABLE` ולא `IMMUTABLE`, לכן עטיפה ישירה שלו בעמודה מחושבת דורשת פונקציית עטיפה `IMMUTABLE` או מילון חיפוש טקסט מותאם. הגישה הפשוטה והיציבה ביותר היא פונקציית SQL קטנה `IMMUTABLE` בשם `f_unaccent(text)` שקוראת ל-`unaccent('unaccent', $1)`, ושימוש בה בעמודה המחושבת ובאינדקס ה-trigram.

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

האילוץ `~ '^\d{9}$'` בודק רק את הפורמט (9 ספרות), לא את ספרת הביקורת. תעודת זהות משתמשת באלגוריתם ספרת ביקורת מסוג Luhn. הסקיל הזה כולל פונקציה מוכנה `validate_teudat_zehut(text)` ב-`scripts/israeli-data-types.sql`, התקינו אותה והשתמשו בה ב-`CHECK` או ב-trigger מסוג `BEFORE INSERT` כדי שתעודות זהות לא תקינות יידחו בשכבת בסיס הנתונים:

```sql
-- אחרי התקנת validate_teudat_zehut() מ-israeli-data-types.sql
ALTER TABLE customers ADD CONSTRAINT chk_teudat_zehut_valid
  CHECK (teudat_zehut IS NULL OR validate_teudat_zehut(teudat_zehut));
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

## דוגמאות

### דוגמה 1: קטלוג מוצרים דו-לשוני עם חיפוש מטושטש בעברית
המשתמש אומר: "אני צריך טבלת מוצרים שתומכת בחיפוש סובלני לשגיאות בעברית ובאנגלית."

פעולות:
1. `CREATE EXTENSION IF NOT EXISTS pg_trgm;` ו-`unaccent;`
2. יוצרים `products` עם `name_he`, `name_en`, `description_he`, `description_en`, ועמודה מחושבת `search_vector` שמשתמשת ב-`to_tsvector('simple', unaccent(...))` לעמודות עבריות וב-`'english'` לעמודות אנגליות.
3. מוסיפים אינדקס GIN על `search_vector` ואינדקסי GIN `gin_trgm_ops` על `name_he` ו-`name_en`.
4. שואלים עם `plainto_tsquery('simple', unaccent($1))` לתוצאות מדורגות, ונופלים חזרה להתאמת trigram `name_he % $1` לסובלנות שגיאות.

תוצאה: משתמשים מוצאים "חשבונית" גם אם הם מקלידים "חשבונ" או כוללים ניקוד, ושאילתות באנגלית עדיין עובדות דרך אותה עמודה.

### דוגמה 2: טבלת חשבוניות ישראלית עם אילוצי מע"מ ותעודת זהות
המשתמש אומר: "צור טבלת חשבוניות שאוכפת חישוב מע"מ נכון ותעודות זהות תקינות."

פעולות:
1. מתקינים את `validate_teudat_zehut()` מ-`scripts/israeli-data-types.sql`.
2. יוצרים `invoices` עם `subtotal_nis numeric(12,2)`, `vat_rate numeric(5,4) DEFAULT 0.1800`, `vat_amount numeric(12,2)`, `total_nis numeric(12,2)`.
3. מוסיפים `CHECK (vat_amount = round(subtotal_nis * vat_rate, 2))` ו-`CHECK (total_nis = subtotal_nis + vat_amount)`.
4. מוסיפים `customer_teudat_zehut text CHECK (customer_teudat_zehut IS NULL OR validate_teudat_zehut(customer_teudat_zehut))`.
5. שומרים את שיעור המע"מ בטבלת `tax_config` היחידנית כך ששינוי שיעור הוא עדכון נתונים, לא deploy.

תוצאה: בסיס הנתונים עצמו דוחה חשבוניות עם חשבון מע"מ שגוי או מספרי תעודת זהות לא תקינים.

## משאבים מצורפים

הסקיל הזה כולל סקריפטים בתיקיית `scripts/`:

- `hebrew-search-setup.sql`: הגדרת חיפוש טקסט מלא בעברית עם collation, אינדקסים ופונקציות
- `israeli-data-types.sql`: תבניות CREATE TABLE עם עמודות, אילוצים ואימותים ישראליים, כולל פונקציות העזר `validate_teudat_zehut()` ו-`format_israeli_phone()`

ומסמכי עזר בתיקיית `references/`:

- `hebrew-collation-guide.md`: מדריך ICU collation לטקסט עברי בפוסטגרס
- `supabase-israel-patterns.md`: תבניות ספציפיות ל-Supabase לאפליקציות ישראליות

## שרתי MCP מומלצים

שרתי ה-MCP הבאים מהדירקטוריה משתלבים היטב עם הסקיל הזה כשבסיס נתונים ישראלי צריך נתונים חיצוניים חיים:

- **boi-exchange**: שערי חליפין של בנק ישראל, שימושי למילוי טבלת `exchange_rates` בתזמון במקום לקודד שערים קשיח.
- **hebcal**: תאריכים עבריים ולוח השנה היהודי, שימושי למילוי עמודות `hebrew_date_display` או להנעת לוגיקת תזמון מותאמת שבת וחגים שאחרת הייתה צריכה תאריכים קשיחים.

## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| תיעוד Collation של PostgreSQL | https://www.postgresql.org/docs/current/collation.html | ICU collations, דטרמיניסטי מול לא דטרמיניסטי |
| pg_trgm של PostgreSQL | https://www.postgresql.org/docs/current/pgtrgm.html | אופרטורי trigram, סף דמיון, אינדקסי GIN |
| unaccent של PostgreSQL | https://www.postgresql.org/docs/current/unaccent.html | הסרת ניקוד ודיאקריטיקה, עטיפת IMMUTABLE |
| Row Level Security של Supabase | https://supabase.com/docs/guides/database/postgres/row-level-security | מדיניות RLS, auth.jwt(), תבניות רב-דיירים |
| שערי חליפין של בנק ישראל | https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ | שערים יציגים לטבלת exchange_rates |
| מזהי Locale של ICU | https://www.postgresql.org/docs/current/collation.html#ICU-CUSTOM-COLLATIONS | תחביר ה-locale he-IL-x-icu |

## פתרון בעיות

### שגיאה: "could not create unique index ... because the collation is not deterministic"
סיבה: עמודה שהוגדרה עם ה-collation הלא דטרמיניסטי `hebrew_icu` משמשת באילוץ `UNIQUE` או באינדקס `btree` רגיל.
פתרון: השאירו את העמודה ב-collation דטרמיניסטי (ברירת מחדל) לייחודיות, והחילו `COLLATE hebrew_icu` רק בסעיפי `ORDER BY` או על עמודת תצוגה נפרדת. collation לא דטרמיניסטי מיועד למיון, לא לאינדוקס שוויון.

### שגיאה: "generation expression is not immutable" בעת הוספת עמודת search_vector
סיבה: `unaccent()` הוא `STABLE` ולא `IMMUTABLE`, לכן אי אפשר להשתמש בו ישירות בתוך ביטוי `GENERATED ALWAYS AS ... STORED`.
פתרון: צרו עטיפה `IMMUTABLE`, `CREATE FUNCTION f_unaccent(text) RETURNS text AS $$ SELECT unaccent('unaccent', $1) $$ LANGUAGE sql IMMUTABLE;`, והשתמשו ב-`f_unaccent(...)` בעמודה המחושבת ובכל אינדקס ביטוי.

## מלכודות נפוצות

- טקסט בעברית ב-PostgreSQL דורש קידוד UTF-8. בסיסי נתונים שנוצרו עם SQL_ASCII או LATIN1 ישחיתו תווים עבריים. תמיד יש לוודא קידוד עם SHOW server_encoding.
- מיון עברית ב-PostgreSQL (he_IL.UTF-8) שונה מאנגלית. סוכנים עלולים להחיל collation ברירת מחדל שממיין טקסט עברי בצורה שגויה בשאילתות ORDER BY.
- ל-PostgreSQL אין מילון חיפוש טקסט מלא לעברית, ולכן `simple` היא הקונפיגורציה הנכונה לעמודות tsvector בעברית. סוכנים נוטים בטעות לבחור `'english'` (שמסיר מילות עצירה באנגלית וגוזע מילים לטיניות, מה שלא עוזר לעברית) או להמציא קונפיגורציית `'hebrew'` שלא קיימת (וזורקת שגיאה). השתמשו ב-`'simple'` לעמודות עבריות ושלבו עם `pg_trgm` ו-`unaccent` לכיסוי טוב יותר.
- עמודות תאריך ישראליות צריכות לאחסן תאריכים כ-DATE או TIMESTAMPTZ (עם אזור זמן Asia/Jerusalem), לא כ-TEXT בפורמט DD/MM/YYYY. סוכנים עלולים ליצור עמודות טקסט לתאריכים מה ששובר השוואות ומיון.
