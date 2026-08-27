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
2. **בחרו אסטרטגיית collation.** החליטו לכל עמודה אם צריך מיון תצוגה עברי (ICU לא דטרמיניסטי, מהלוקאל `he-IL`) או חיפוש תחילית מדויק (ה-collation הדטרמיניסטי שהוא ברירת המחדל). collation לא דטרמיניסטי תומך באילוץ `UNIQUE` ובאינדקס `btree`. החל מ-PostgreSQL 18 הוא תומך גם ב-`LIKE`, אבל `ILIKE` וביטויים רגולריים עדיין נכשלים, ו-`LIKE` לא יכול לנצל אינדקס `btree` לחיפוש תחילית. עיינו בטבלת האופרטורים למטה לפני שבוחרים.
3. **בחרו גישת חיפוש.** להתאמה מדויקת ולתחילית השתמשו ב-`btree`. לחיפוש מטושטש וסובלני לשגיאות בעברית השתמשו ב-`pg_trgm`. לחיפוש מדורג רב-שדות השתמשו בחיפוש טקסט מלא עם הקונפיגורציה `simple` (ראו "חיפוש טקסט מלא בעברית" למטה). להתאמה עברית שמתעלמת מניקוד, מקף וגרשיים השתמשו בפונקציה `normalize_hebrew()` שלמטה, והחילו אותה גם על העמודה וגם על השאילתה; `unaccent` מסיר רק דיאקריטיקה לטינית, לא ניקוד עברי.
4. **החילו אילוצים על טיפוסי נתונים ישראליים.** השתמשו באילוצי ה-`CHECK` ובפונקציות העזר מ-`scripts/israeli-data-types.sql` (תעודת זהות, טלפון, מיקוד, מספר עוסק, IBAN) וקראו ל-`validate_teudat_zehut()` לבדיקת ספרת הביקורת של תעודת הזהות במקום לממש אותה מחדש בקוד האפליקציה.

## אינדוקס טקסט בעברית

### הגדרת ICU Collation לעברית

פוסטגרס תומך ב-ICU collation למיון נכון של טקסט עברי. תמיד צרו collation עברי לעמודות שמכילות טקסט בעברית:

```sql
-- יצירת collation עברי.
-- locale הוא תג ICU/BCP-47, כלומר 'he-IL'. אל תעבירו 'he-IL-x-icu': זה השם של
-- ה-collation שפוסטגרס יוצר מראש, ו-'-x-icu' הוא תת-תג פרטי ש-ICU מתעלם ממנו.
CREATE COLLATION IF NOT EXISTS hebrew_icu (
  provider = icu,
  locale = 'he-IL',
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

**חשוב:** מה ש-collation לא דטרמיניסטי תומך בו השתנה ב-PostgreSQL 18, שאיפשר `LIKE` ופונקציות מיקום טקסט ש"נהגו להחזיר שגיאה" (הערות הגרסה של PG 18). נבדק על PostgreSQL 18.6:

| פעולה על עמודה לא דטרמיניסטית | PG 13-17 | PG 18 ומעלה |
|---|---|---|
| אילוץ `UNIQUE`, אינדקס `btree` | עובד (בלי דדופליקציה) | זהה |
| `LIKE` | `ERROR: nondeterministic collations are not supported for LIKE` | עובד, אבל המתכנן משתמש באינדקס כמסנן בלבד ולא כסריקת טווח תחילית |
| `ILIKE` | שגיאה | עדיין שגיאה |
| ביטויים רגולריים (`~`) | שגיאה | עדיין שגיאה |
| `pg_trgm` (`%`, `<%`) | עובד | עובד |

כלומר ההמלצה לא השתנתה גם אם הנימוק כן: שמרו עמודה **דטרמיניסטית** (או אינדקס `pg_trgm` מסוג GIN) לחיפוש תחילית ולחיפוש מטושטש, והשתמשו ב-ICU collation למיון תצוגה ולהשוואת שוויון לשונית. בנוסף, PostgreSQL 18 דורש שזוג מפתח ראשי/זר ישתמש ב-collations דטרמיניסטיים או באותו collation לא דטרמיניסטי, ותקלה בכך צצה בדרך כלל ככישלון של `pg_upgrade` או `pg_restore` על סכימה ישנה.

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

השתמשו ב-`<%` (word_similarity) ולא ב-`%` כשהשאילתה קצרה והעמודה ארוכה. הפונקציה `similarity()` משווה מחרוזות שלמות, ולכן הציון יורד ככל שהעמודה גדלה גם כשמילת החיפוש מופיעה בה מילולית, בעוד `word_similarity()` לא מושפעת מכך. ניתן לשחזר על PostgreSQL 18.6 (הגוף הבא הוא בן 104 תווים ומכיל `והחשבונית`):

```sql
\set body 'קיבלנו אתמול מהספק שלנו את והחשבונית עבור ההזמנה האחרונה של החודש שעבר ואנחנו ממתינים לאישור סופי מהמנהל'
SELECT similarity(:'body', 'חשבונית'),        -- 0.067  ולכן :'body' %  'חשבונית' הוא FALSE
       word_similarity('חשבונית', :'body');   -- 0.750  ולכן 'חשבונית' <% :'body' הוא TRUE
```

נקודת המעבר תלויה באורך ולא בעצם הימצאות המילה: הביטוי `similarity('והחשבונית נשלחה', 'חשבונית')` מחזיר 0.333 על אותו שרת ועובר את סף ברירת המחדל 0.3. לכן `%` נראה תקין בבדיקות על שורות קצרות ואז מפסיק להתאים בשקט ברגע שנטען טקסט גוף אמיתי, וזו בדיוק המלכודת. כלל אצבע: `%` לעמודות קצרות (שמות, כותרות), `<%` לעמודות גוף ותיאור, ו-`<<%` (`strict_word_similarity`) כשרוצים גבולות מילה שלמה. אינדקס `gin_trgm_ops` אחד משרת את שלושתם.

### חיפוש טקסט מלא בעברית

חיפוש הטקסט המלא של פוסטגרס משתמש בקונפיגורציית `simple` לעברית (כי אין מילון עברי ייעודי). לתוצאות טובות יותר, שלבו עם `pg_trgm`:

```sql
-- הוספת עמודת וקטור חיפוש
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    -- normalize_hebrew() על העמודות העבריות (ראו "נרמול לחיפוש בעברית" למטה).
    -- בלעדיה ניקוד וגרשיים שמורים חוסמים התאמות בשקט.
    setweight(to_tsvector('simple', normalize_hebrew(coalesce(name_he, ''))), 'A') ||
    setweight(to_tsvector('simple', normalize_hebrew(coalesce(description_he, ''))), 'B') ||
    setweight(to_tsvector('english', coalesce(name_en, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description_en, '')), 'B')
  ) STORED;

-- יצירת אינדקס GIN
CREATE INDEX idx_products_search ON products USING gin (search_vector);

-- שאילתת חיפוש (תומכת גם בעברית וגם באנגלית).
-- הווקטור מבצע stemming לעמודות האנגלית ('invoice' נשמר כלקסמה 'invoic'),
-- ולכן שאילתת 'simple' לבדה לעולם לא תתאים להן. אחדו את שתי הקונפיגורציות.
SELECT * FROM products
WHERE search_vector @@ (plainto_tsquery('simple', $1) || plainto_tsquery('english', $1))
ORDER BY ts_rank(search_vector,
         plainto_tsquery('simple', $1) || plainto_tsquery('english', $1)) DESC;
```

הקונפיגורציה `simple` לא מבצעת stemming, והעברית מצמידה את מילות היחס למילה עצמה. לכן `חשבונית`, `בחשבונית` ו-`והחשבונית` הופכות לשלוש לקסמות נפרדות, וחיפוש טקסט מלא לבדו מפספס בשקט את רוב ההטיות. נמדד על PostgreSQL 18.6: `plainto_tsquery('simple','חשבונית')` התאים לשורה אחת מתוך שלוש שמכילות את המילה. אל תסתמכו על FTS לבדו לאחזור בעברית, צרפו לכל ענף FTS ענף `<%` של trigram על אותן עמודות (ראו "חיפוש מטושטש בעברית עם Trigram" למעלה). הסקריפט `scripts/hebrew-search-setup.sql` מספק את `search_hebrew()` בנוי כך.

### נרמול לחיפוש בעברית (ניקוד, מקף וגרשיים)

שלוש מוסכמות כתיב עבריות שוברות חיפוש, ואת שלושתן צריך לנרמל גם בצד המאוחסן וגם בצד השאילתה, אחרת שני הצדדים לעולם לא נפגשים.

**1. ניקוד.** משתמשים לא יקלידו ניקוד, ולכן "שָׁלוֹם" חייב עדיין להתאים ל"שלום". **התוסף `unaccent` לא מסיר ניקוד עברי.** קובץ הכללים שלו מכסה סימנים משולבים לטיניים ויווניים (U+0300-U+0362) ואין בו אף רשומה לגוש הניקוד העברי, ולכן `unaccent('שָׁלוֹם')` מחזיר את המחרוזת ללא שינוי.

**2. מקף.** אל תסירו את כל הטווח U+0591-U+05C7 כדי להוריד ניקוד. הגוש הזה מכיל גם את U+05BE מקף (קטגוריית יוניקוד `Pd`, כלומר קו מפריד) ואת U+05C0 פסק ו-U+05C3 סוף פסוק (`Po`). אלה מפרידי מילים. מחיקה שלהם מדביקה מילים זו לזו, ולכן `תל־אביב` נשמר כלקסמה אחת `תלאביב` וחיפוש של `תל אביב` לעולם לא יתאים לו. הסירו רק את הסימנים המשולבים (`Mn`), והפכו את המפרידים לרווח.

**3. גרשיים.** מנתח ברירת המחדל של חיפוש הטקסט המלא מסווג גרשיים (U+05F4) כרווח, ולכן `בע״מ` מפורק לשתי לקסמות `בע` ו-`מ`, בזמן שהמשתמש שמחפש את החברה מקליד `בעמ`. נבדק עם `ts_debug('simple','צה״ל')` שמחזיר `צה` (מילה), `״` (רווח), `ל` (מילה). כל שם חברה ישראלי מסתיים ב-בע״מ, וגם צה״ל, ד״ר, ח״כ ו-ש״ח מתנהגים כך, ולכן זה שובר בשקט חלק ניכר מהשאילתות העבריות האמיתיות. הסירו גרש וגרשיים (וגם את `'` ו-`"` הלטיניים שקלט אמיתי מחליף בהם) משני הצדדים.

```sql
-- סימנים משולבים בלבד (Mn). לא כל הגוש U+0591-U+05C7.
CREATE FUNCTION strip_nikud(text) RETURNS text
  AS $$ SELECT regexp_replace($1, '[֑-ֽֿׁ-ׂׄ-ׇׅ]', '', 'g') $$
  LANGUAGE sql IMMUTABLE;

-- נרמול מלא לצד החיפוש. IMMUTABLE כדי שיוכל לגבות עמודה מחושבת ואינדקס ביטוי.
CREATE FUNCTION normalize_hebrew(text) RETURNS text
  AS $$
    SELECT regexp_replace(
             regexp_replace(
               regexp_replace($1, '[֑-ֽֿׁ-ׂׄ-ׇׅ]', '', 'g'),  -- ניקוד וטעמים
               '[־׀׃׆]', ' ', 'g'),                       -- מקף ודומיו הופכים לרווח
             '[׳״''"]', '', 'g')                          -- גרש וגרשיים
  $$
  LANGUAGE sql IMMUTABLE;

-- אימות שלושת ההתנהגויות (כל אחת מחזירה true):
SELECT strip_nikud('שָׁלוֹם') = 'שלום';                  -- unaccent() היה מחזיר false
SELECT normalize_hebrew('תל־אביב יפו') = 'תל אביב יפו';  -- המקף הפך לרווח
SELECT normalize_hebrew('בע״מ') = 'בעמ';                 -- הגרשיים הוסרו

-- שימוש ב-search vector כדי שניקוד וגרשיים שמורים לא יחסמו התאמות
ALTER TABLE products ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('simple', normalize_hebrew(coalesce(name_he, '')))
  ) STORED;

-- מנרמלים את השאילתה בדיוק באותו אופן
SELECT * FROM products
WHERE search_vector @@ plainto_tsquery('simple', normalize_hebrew($1));
```

הערה: `unaccent` עדיין שימושי לדיאקריטיקה לטינית בעמודות האנגלית, רק לא לעברית. אם בכל זאת משתמשים ב-`unaccent()` (שהוא `STABLE`), עטפו אותו ב-`f_unaccent(text)` מסוג `IMMUTABLE` שקורא ל-`unaccent('unaccent', $1)` לפני שימוש בעמודה מחושבת.

שני כללי אינדוקס שנובעים מכך, וקל לטעות בהם:

- אנדקסו בדיוק את הביטוי שאתם שואלים עליו. אינדקס `gin_trgm_ops` על `body_he` לא משרת תנאי שנכתב מול `normalize_hebrew(body_he)` או `coalesce(body_he,'')`. או שמתאימים מול העמודה החשופה, או שבונים את האינדקס על אותו ביטוי בדיוק, אחרת התנאי מתדרדר לסריקה סדרתית בזמן שהוא נראה מאונדקס.
- לכל אופרטור trigram יש GUC סף משלו, עם ברירות מחדל שונות בכוונה: `%` קורא את `pg_trgm.similarity_threshold` (0.3), `<%` קורא את `pg_trgm.word_similarity_threshold` (0.6), ו-`<<%` קורא את `pg_trgm.strict_word_similarity_threshold` (0.5). הגדרה של הראשון בלבד משאירה ענף `<%` חסום ב-0.6 בלי קשר למה שחשבתם שהגדרתם. גם אל תטייחו את זה בהזנת ערך אחד לשלושתם: `word_similarity` מודדת את מקטע המילה המתאים ביותר ולא את המחרוזת כולה, ולכן היא נעה גבוה יותר, וערך 0.2-0.3 שם מחזיר שורות כמעט לא קשורות.

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
-- שורה יחידה היא המבנה הלא נכון. השיעור משתנה (17% ל-18% ב-01.01.2025, והשינוי
-- הבא עוד יגיע), ושורה יחידה מתמחרת מחדש בשקט כל חשבונית היסטורית ברגע שמעדכנים
-- אותה. שמרו את ההיסטוריה ואתרו את השיעור נכון לתאריך החשבונית, בדיוק כמו בטבלת
-- שערי החליפין.
CREATE TABLE vat_rates (
  rate numeric(5, 4) NOT NULL,
  effective_from date NOT NULL PRIMARY KEY
);
INSERT INTO vat_rates (rate, effective_from)
VALUES (0.1700, '2013-06-02'), (0.1800, '2025-01-01');

-- חישוב מע"מ לפי השיעור שהיה בתוקף בתאריך החשבונית עצמה
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

השיעור משתנה גם לפי שורה ולא רק לפי תאריך: שורת ייצוא חייבת במע"מ בשיעור אפס וחלק מהעסקאות פטורות, ולכן עמודת שיעור אחת לכל החשבונית לא יכולה לייצג חשבונית מעורבת. העבירו את השיעור לרמת שורת הפריט ברגע שיש יותר ממחלקת שיעור אחת.

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

לעולם אל תאתרו שער לפי תאריך מדויק. בנק ישראל לא מפרסם שער יציג בשבתות ובחגים, ולכן `WHERE effective_date = $1` יחזיר אפס שורות לכל מסמך שתאריכו שבת, ואז עמודת המרה עם `NOT NULL` תפיל את ה-INSERT. גלגלו קדימה את השער האחרון שפורסם:

```sql
-- השער שהיה בתוקף בתאריך נתון (מגלגל את שער יום שישי דרך השבת)
SELECT rate_to_ils FROM exchange_rates
WHERE currency_code = 'USD' AND effective_date <= $1
ORDER BY effective_date DESC
LIMIT 1;
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
-- אל תכתבו WHERE (starts_at AT TIME ZONE 'Asia/Jerusalem')::date = '2026-03-14':
-- עטיפת העמודה מבטלת את האינדקס על starts_at וכופה סריקה סדרתית. השתמשו בטווח
-- חצי פתוח על העמודה החשופה, מחושב מהתאריך המקומי.
SELECT * FROM events
WHERE starts_at >= timestamp '2026-03-14 00:00' AT TIME ZONE 'Asia/Jerusalem'
  AND starts_at <  timestamp '2026-03-15 00:00' AT TIME ZONE 'Asia/Jerusalem';
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
-- STABLE ולא IMMUTABLE: AT TIME ZONE על timestamptz תלוי במסד נתוני אזורי הזמן,
-- כך שעדכון tzdata יכול לשנות את התוצאה. סימון IMMUTABLE היה מסכן ערכים שמורים/מאונדקסים שגויים.
$$ LANGUAGE plpgsql STABLE;
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

-- בידוד דיירים. קראו את ה-claim מתוך app_metadata, לא מהרמה העליונה ולא מ-user_metadata:
--   * Supabase לא מכניס claim מותאם ברמה העליונה של טוקן הגישה אלא אם הוספתם
--     custom access token hook, ולכן `auth.jwt() ->> 'tenant_id'` הוא NULL והמדיניות
--     נכשלת סגור לאפס שורות גלויות, מה שנראה כמו באג נתונים.
--   * user_metadata ניתן לכתיבה על ידי המשתמש עצמו, ולכן קריאת מזהה דייר משם היא
--     בריחה מהדייר ולא פתרון עוקף.
-- RESTRICTIVE כדי שמדיניות מתירנית מאוחרת לא תרחיב אותה, ו-TO authenticated כדי
-- שהיא לא תרוץ גם עבור תפקיד anon.
CREATE POLICY tenant_isolation ON invoices
  AS RESTRICTIVE
  TO authenticated
  USING (tenant_id = ((select auth.jwt()) -> 'app_metadata' ->> 'tenant_id')::uuid);

-- אנדקסו את העמודה שכל מדיניות מסננת לפיה, אחרת כל בדיקה היא סריקה סדרתית.
CREATE INDEX idx_invoices_tenant ON invoices (tenant_id);

-- גישת מנהל (מנהלים ישראלים רואים את כל הדיירים)
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

-- קריאה בלבד לרואה חשבון (נפוץ באפליקציות עסקיות ישראליות)
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

### חיבור Edge Function למסד הנתונים

ל-Supabase Edge Functions שמתחברות למסד הנתונים:

```typescript
// ב-Supabase Edge Functions, תמיד השתמשו בחיבור ה-pooler
// חיבור ישיר: postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
// חיבור מאוגם (מצב transaction): postgresql://postgres:password@aws-[region].pooler.supabase.com:6543/postgres
// העתיקו את הכתובת המדויקת מחלון ה-Connect של הפרויקט, אל תקבעו קידומת קשיחה.

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// מפתח ה-service role רץ כתפקיד Postgres עם התכונה bypassrls, ולכן הוא מתעלם
// מכל מדיניות שלמעלה. לעולם אל תשלחו אותו לדפדפן, ובצעו סינון דיירים במפורש
// בכל Edge Function שמשתמשת בו.
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

// לשאילתות SQL ישירות ב-Edge Functions, השתמשו ב-pooler כדי למנוע מיצוי חיבורים תחת עומס
```

## ביצועים ואופטימיזציה

### איגום חיבורים (Connection Pooling)

לאפליקציות SaaS ישראליות על Supabase, איגום חיבורים הוא קריטי:

- **Supavisor** (ה-pooler המשותף של Supabase): הכתובת היא `aws-[region].pooler.supabase.com`, פורט **6543** למצב transaction ופורט **5432** למצב session. בתיעוד הכתובת מופיעה עם ה-placeholder ‏`aws-[region]`, ולכן העתיקו את המחרוזת המדויקת מחלון ה-Connect של הפרויקט במקום לקבע קידומת.
- **PgBouncer**: זמין כ-pooler הייעודי של Supabase, וגם הבחירה הרגילה באחסון עצמי.
- גודל ה-pool אינו קבוע לפי תוכנית. זו הגדרה אחת ש-Supavisor ו-PgBouncer מתייחסים אליה שניהם, והיא מגבילה את מספר החיבורים שה-pooler פותח לצד השרת מול Postgres. מה שכן משתנה לפי דרגת המחשוב הוא תקרת "max pooler clients" נפרדת, שקובעת כמה לקוחות יכולים להתחבר ל-pooler בו זמנית, ובנוסף `max_connections` של המופע. קראו את המספרים מהפרויקט שלכם במקום לקבע מספר כלשהו.

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
-- שמרו על אילוץ ה-CHECK מקל: אילוץ נוקשה מדי זורק על מספרים תקינים (קווי שירות 1-700/1-800,
-- מספרי VoIP בקידומת 07X) וחוסם הכנסות בפרודקשן. עשו פורמט/נירמול מדויק בשכבת האפליקציה.
ALTER TABLE customers ADD COLUMN phone text CHECK (
  phone ~ '^05\d{8}$'           -- נייד: 05X + 8 ספרות (10 בסך הכל)
  OR phone ~ '^07\d{8}$'        -- VoIP / לא-גאוגרפי: 07X + 7 ספרות (10 בסך הכל)
  OR phone ~ '^0[23489]\d{7}$'  -- קווי: אזור חיוג + 7 ספרות (9 בסך הכל)
  OR phone ~ '^1[78]00\d{6}$'   -- שירות: 1-700 / 1-800 + 6 ספרות
  OR phone ~ '^\*\d{3,4}$'      -- מספרים קצרים: *XXX או *XXXX
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
1. `CREATE EXTENSION IF NOT EXISTS pg_trgm;` (ו-`unaccent` לעמודות האנגלית), ואז מגדירים את הפונקציה `normalize_hebrew(text)` מסוג `IMMUTABLE` לעברית.
2. יוצרים `products` עם `name_he`, `name_en`, `description_he`, `description_en`, ועמודה מחושבת `search_vector` שמשתמשת ב-`to_tsvector('simple', normalize_hebrew(...))` לעמודות עבריות וב-`'english'` לעמודות אנגליות.
3. מוסיפים אינדקס GIN על `search_vector` ואינדקסי GIN `gin_trgm_ops` על `name_he` ו-`name_en`.
4. שואלים עם `plainto_tsquery('simple', normalize_hebrew($1))` לתוצאות מדורגות, מאוחד עם `plainto_tsquery('english', $1)` כדי שגם עמודות האנגלית הגזועות יוכלו להתאים, ונופלים חזרה להתאמת trigram `name_he % $1` לסובלנות שגיאות.

תוצאה: משתמשים מוצאים "חשבונית" גם אם הם מקלידים "חשבונ" או כוללים ניקוד, ושאילתות באנגלית עדיין עובדות דרך אותה עמודה.

### דוגמה 2: טבלת חשבוניות ישראלית עם אילוצי מע"מ ותעודת זהות
המשתמש אומר: "צור טבלת חשבוניות שאוכפת חישוב מע"מ נכון ותעודות זהות תקינות."

פעולות:
1. מתקינים את `validate_teudat_zehut()` מ-`scripts/israeli-data-types.sql`.
2. יוצרים `invoices` עם `subtotal_nis numeric(12,2)`, `vat_rate numeric(5,4) DEFAULT 0.1800`, `vat_amount numeric(12,2)`, `total_nis numeric(12,2)`.
3. מוסיפים `CHECK (vat_amount = round(subtotal_nis * vat_rate, 2))` ו-`CHECK (total_nis = subtotal_nis + vat_amount)`.
4. מוסיפים `customer_teudat_zehut text CHECK (customer_teudat_zehut IS NULL OR validate_teudat_zehut(customer_teudat_zehut))`.
5. שומרים את שיעורי המע"מ בטבלת `vat_rates` עם תאריך תחילת תוקף, ומאתרים את השיעור נכון לתאריך החשבונית, כך ששינוי שיעור לא מתמחר מחדש חשבוניות היסטוריות.

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
| הערות הגרסה של PostgreSQL 18 | https://www.postgresql.org/docs/release/18.0/ | LIKE הותר עם collations לא דטרמיניסטיים, וכלל ה-collation למפתח ראשי/זר |
| pg_trgm של PostgreSQL | https://www.postgresql.org/docs/current/pgtrgm.html | אופרטורי trigram, סף דמיון, אינדקסי GIN |
| unaccent של PostgreSQL | https://www.postgresql.org/docs/current/unaccent.html | הסרת דיאקריטיקה לטינית (לא ניקוד עברי), עטיפת IMMUTABLE |
| Row Level Security של Supabase | https://supabase.com/docs/guides/database/postgres/row-level-security | מדיניות RLS, auth.jwt(), תבניות רב-דיירים |
| שערי חליפין של בנק ישראל | https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/ | שערים יציגים לטבלת exchange_rates |
| מזהי Locale של ICU | https://www.postgresql.org/docs/current/collation.html#ICU-CUSTOM-COLLATIONS | תחביר locale מסוג BCP-47 ל-CREATE COLLATION (he-IL, he-IL-u-ks-level1) |

## פתרון בעיות

### שגיאה: "nondeterministic collations are not supported for ILIKE" (או "... for regular expressions")
סיבה: עמודה שהוגדרה עם ה-collation הלא דטרמיניסטי `hebrew_icu` משמשת עם `ILIKE` או עם אופרטור ביטוי רגולרי. שניהם עדיין נכשלים ב-PostgreSQL 18. אופרטור `LIKE` רגיל על אותה עמודה החזיר שגיאה מקבילה עד PostgreSQL 17 והותר ב-18.
פתרון: בצעו את ההתאמה מול ביטוי דטרמיניסטי, `WHERE name_he COLLATE "default" ILIKE 'שלום%'`, או החזיקו עמודה דטרמיניסטית נפרדת (או אינדקס `pg_trgm` מסוג GIN) לחיפוש תחילית ומטושטש. שימו לב שגם היכן ש-`LIKE` מותר כעת, המתכנן משתמש באינדקס כמסנן בלבד, ולכן אינדקס `pg_trgm` נשאר המסלול המהיר לחיפוש תחילית. אילוץ `UNIQUE` ואינדקס `btree` רגיל דווקא עובדים על עמודה לא דטרמיניסטית, הם רק מאבדים דדופליקציה של B-tree.

### שגיאה: "generation expression is not immutable" בעת הוספת עמודת search_vector
סיבה: `unaccent()` הוא `STABLE` ולא `IMMUTABLE`, לכן אי אפשר להשתמש בו ישירות בתוך ביטוי `GENERATED ALWAYS AS ... STORED`.
פתרון: צרו עטיפה `IMMUTABLE`, `CREATE FUNCTION f_unaccent(text) RETURNS text AS $$ SELECT unaccent('unaccent', $1) $$ LANGUAGE sql IMMUTABLE;`, והשתמשו ב-`f_unaccent(...)` בעמודה המחושבת ובכל אינדקס ביטוי.

## מלכודות נפוצות

- טקסט בעברית ב-PostgreSQL דורש קידוד UTF-8. בסיסי נתונים שנוצרו עם SQL_ASCII או LATIN1 ישחיתו תווים עבריים. תמיד יש לוודא קידוד עם SHOW server_encoding.
- מיון עברית ב-PostgreSQL (he_IL.UTF-8) שונה מאנגלית. סוכנים עלולים להחיל collation ברירת מחדל שממיין טקסט עברי בצורה שגויה בשאילתות ORDER BY.
- ל-PostgreSQL אין מילון חיפוש טקסט מלא לעברית, ולכן `simple` היא הקונפיגורציה הנכונה לעמודות tsvector בעברית. סוכנים נוטים בטעות לבחור `'english'` (שמסיר מילות עצירה באנגלית וגוזע מילים לטיניות, מה שלא עוזר לעברית) או להמציא קונפיגורציית `'hebrew'` שלא קיימת (וזורקת שגיאה). השתמשו ב-`'simple'` לעמודות עבריות ושלבו עם `pg_trgm` ו-`normalize_hebrew()` לכיסוי טוב יותר (`unaccent` לא עוזר לכיסוי בעברית, הוא משאיר את הניקוד). שימו לב ש-`'simple'` לא עושה גזירת שורשים, אז קידומות עבריות (ו/ב/כ/ל/ה/מ/ש) וצורות רבים/נסמך הופכות ללקסמות נפרדות, ובמדידה הכיסוי היה שורה אחת מתוך שלוש; תמיד צרפו ל-FTS ענף trigram עם `<%` על אותן עמודות, כולל עמודות גוף, אחרת התאמות בצורות מוטות אובדות.
- מנתח ברירת המחדל של FTS מתייחס לגרשיים (U+05F4) כרווח, ולכן `בע״מ` הופך לשתי לקסמות `בע` ו-`מ` בזמן שמשתמשים מקלידים `בעמ`. סוכנים שומרים את התו הטיפוגרפי הנכון (וזה נכון) ואז לא מנרמלים אותו לחיפוש (וזה שובר כל ראשי תיבות: בע״מ, צה״ל, ד״ר, ח״כ, ש״ח). הסירו גרש וגרשיים גם בצד המאוחסן וגם בצד השאילתה.
- אל תסירו את כל הטווח U+0591-U+05C7 כדי להוריד ניקוד. יש בו את U+05BE מקף, קו שמפריד מילים, ולכן `תל־אביב` מתמוטט ללקסמה אחת `תלאביב` ו-`תל אביב` מפסיק להתאים. הסירו רק את הסימנים המשולבים והפכו את המפרידים לרווח.
- עמודות תאריך ישראליות צריכות לאחסן תאריכים כ-DATE או TIMESTAMPTZ (עם אזור זמן Asia/Jerusalem), לא כ-TEXT בפורמט DD/MM/YYYY. סוכנים עלולים ליצור עמודות טקסט לתאריכים מה ששובר השוואות ומיון.
