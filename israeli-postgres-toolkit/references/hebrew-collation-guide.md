# Hebrew Collation Guide for PostgreSQL

## Overview

PostgreSQL supports ICU collations that handle Hebrew text sorting correctly. This guide covers setup, usage patterns, and common pitfalls when working with Hebrew text in PostgreSQL.

## ICU Collation Basics

ICU (International Components for Unicode) provides locale-aware string comparison. For Hebrew, the key locale is `he-IL-x-icu`.

### Creating the Collation

```sql
CREATE COLLATION IF NOT EXISTS hebrew_icu (
  provider = icu,
  locale = 'he-IL-x-icu',
  deterministic = false
);
```

**Why non-deterministic?** A non-deterministic ICU collation can compare strings while ignoring differences below a chosen strength. At a reduced strength (a collation built with `u-ks-level1`) it treats strings as equal ignoring BOTH nikud AND final-vs-base (sofit) letter forms, so `'שָׁלוֹם' = 'שלום'` and `'מ' = 'ם'` both compare equal. At the DEFAULT (tertiary) strength, nikud and sofit are both significant, so `'שָׁלוֹם'` does NOT equal `'שלום'`. There is no strength that ignores nikud while keeping sofit distinct. Consequences: (1) for reliable nikud-insensitive matching prefer the `strip_nikud()` function (collation-based folding also collapses sofit and case, which you usually do not want); (2) a non-deterministic collation cannot back a `UNIQUE` constraint, a plain `btree` index, or `LIKE`/pattern matching, so use it only in `ORDER BY` or explicit comparisons.

### Deterministic vs Non-Deterministic

| Feature | Deterministic | Non-Deterministic |
|---------|--------------|-------------------|
| Hebrew sorting | Incorrect for some cases | Correct |
| UNIQUE constraints | Supported | NOT supported |
| btree indexes | Supported | NOT supported |
| Pattern matching (LIKE) | Supported | NOT supported |
| Equality comparison | Byte-level | Linguistic |

### Workaround for UNIQUE + Hebrew Sorting

Use a deterministic collation for the column (allowing UNIQUE) and apply Hebrew collation in ORDER BY:

```sql
CREATE TABLE products (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  -- Default (deterministic) collation for UNIQUE constraint
  name_he text NOT NULL UNIQUE,
  name_en text
);

-- Sort with Hebrew collation in queries
SELECT * FROM products ORDER BY name_he COLLATE hebrew_icu;
```

## Hebrew Character Considerations

### Final Forms (Sofit)

Hebrew has five letters with final forms used at the end of words:

| Regular | Final (Sofit) | Name |
|---------|---------------|------|
| כ | ך | Kaf |
| מ | ם | Mem |
| נ | ן | Nun |
| פ | ף | Pe |
| צ | ץ | Tsadi |

ICU collation handles sorting these correctly. Without ICU, they may sort in unexpected positions.

### Nikud (Vowel Points)

Hebrew text can include nikud (vowel diacritical marks). A default `he-IL-x-icu` collation keeps nikud significant, so it does NOT make pointed and unpointed text compare equal:

```sql
-- FALSE at default strength: the default ICU collation treats nikud as significant
SELECT 'שָׁלוֹם' = 'שלום' COLLATE hebrew_icu;  -- false

-- For reliable nikud-insensitive matching, strip nikud explicitly (see strip_nikud() in the skill body):
SELECT strip_nikud('שָׁלוֹם') = strip_nikud('שלום');  -- true
```

A reduced-strength collation (`u-ks-level1`) would make them equal, but it also folds final (sofit) letters and case, which is rarely what you want. Use `strip_nikud()` for nikud-insensitivity and reserve the collation for sort order.

For most applications, strip nikud before storage:

```sql
-- Remove nikud in application code before inserting
-- Unicode range for Hebrew nikud: U+0591 to U+05C7
```

### Geresh and Gershayim

Hebrew uses geresh (׳) and gershayim (״) for abbreviations and acronyms:

- צה״ל (IDF)
- ד״ר (Dr.)
- ח״כ (MK, Member of Knesset)

Store these with the proper Unicode characters (U+05F3 for geresh, U+05F4 for gershayim), not ASCII apostrophe/quote marks.

## Full-Text Search Configuration

PostgreSQL does not ship with a Hebrew dictionary for full-text search. Use the `simple` configuration:

```sql
-- 'simple' tokenizes without stemming (works for Hebrew)
SELECT to_tsvector('simple', 'שלום עולם');
-- Result: 'עולם':2 'שלום':1

-- 'english' would not tokenize Hebrew correctly
SELECT to_tsvector('english', 'שלום עולם');
-- May produce unexpected results
```

### Combining Hebrew and English Search

For bilingual content, use weighted search vectors:

```sql
-- Hebrew with 'simple', English with 'english'
setweight(to_tsvector('simple', coalesce(title_he, '')), 'A') ||
setweight(to_tsvector('english', coalesce(title_en, '')), 'A')
```

## Trigram Search for Hebrew

The `pg_trgm` extension works with Hebrew text for fuzzy matching:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Check trigrams generated for Hebrew text
SELECT show_trgm('חשבונית');
```

### Similarity Threshold

The default similarity threshold (0.3) may be too high for Hebrew due to morphological complexity. Consider lowering to 0.2:

```sql
SET pg_trgm.similarity_threshold = 0.2;
```

### Index Types for Hebrew Trigrams

```sql
-- GIN index (faster lookups, slower updates)
CREATE INDEX idx_name_he_trgm ON table USING gin (name_he gin_trgm_ops);

-- GiST index (balanced, supports distance operator)
CREATE INDEX idx_name_he_trgm ON table USING gist (name_he gist_trgm_ops);
```

GIN is recommended for most use cases. Use GiST if you need the `<->` distance operator for KNN queries.

## Common Pitfalls

1. **Mixing collations in JOINs**: If two columns use different collations, JOINs will fail. Explicitly specify collation: `a.name = b.name COLLATE "default"`.

2. **Index not used**: Non-deterministic collation indexes are not used for LIKE queries. Use trigram indexes instead.

3. **Sorting with mixed scripts**: When sorting mixed Hebrew/English content, ICU sorts Hebrew characters after Latin by default. If you need custom ordering, consider a sort key column.

4. **JSON/JSONB**: Collation does not apply inside JSON values. Extract to text columns for proper sorting.

5. **Backup/Restore**: ICU collation versions can change between PostgreSQL versions. After major upgrades, run `ALTER COLLATION hebrew_icu REFRESH VERSION;`.
