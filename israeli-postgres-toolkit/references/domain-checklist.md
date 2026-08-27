# Domain Coverage Checklist: PostgreSQL + Supabase for Israeli Applications

Scope: Hebrew text indexing and collation, Hebrew full-text and fuzzy search, NIS currency,
Asia/Jerusalem timezone, Israeli data-type constraints, RLS for multi-tenant Israeli SaaS.

Rule applied below: wherever behaviour is driven by a TABLE of values (a per-version operator
support matrix, a per-strength collation matrix, a per-Unicode-block character matrix, a
per-entity numbering rule), every category the behaviour varies by gets its own row. One
hand-wavy row covering "version differences" is not coverage.

---

## Must cover (core)

### A. Encoding and collation

| # | Item | Source |
|---|---|---|
| A1 | `server_encoding` must be UTF8; SQL_ASCII/LATIN1 corrupt Hebrew and require a dump/reload to fix | PostgreSQL 18 docs: multibyte.html |
| A2 | ICU provider vs libc provider; `CREATE COLLATION ... provider = icu, locale = '<BCP-47>'`; the locale is `he-IL`, **not** the pre-created collation *name* `he-IL-x-icu` | PostgreSQL 18 docs: collation.html (COLLATION-MANAGING-CREATE-ICU) |
| A3 | Deterministic vs non-deterministic collations: what non-determinism buys (linguistic equality) and costs | PostgreSQL 18 docs: collation.html (COLLATION-NONDETERMINISTIC) |
| A4 | **Operator support matrix on a non-deterministic column, ONE ROW PER OPERATOR CLASS, split by major version**: `=`/`UNIQUE`/btree (all versions, no dedup) · `LIKE` (error ≤17, allowed 18+, filter-only) · `ILIKE` (errors on every version incl. 18) · POSIX regex `~` (errors on every version incl. 18) · `pg_trgm` `%`/`<%`/`<<%` (works on all) · `position()`/`strpos`/`replace` (error ≤17, allowed 18+) | PostgreSQL 18 docs: 18.0 ; PostgreSQL 18 docs: collation.html (COLLATION-NONDETERMINISTIC) |
| A5 | **ICU strength matrix, ONE ROW PER STRENGTH**, because what folds varies by level: `u-ks-level1` (nikud folds, sofit folds, case folds) · `u-ks-level2` (nikud significant, sofit folds) · `u-ks-level3`/default tertiary (nikud significant, sofit significant). Consequence: no strength folds nikud while keeping sofit distinct | PostgreSQL 18 docs: collation.html (ICU-CUSTOM-COLLATIONS) ; Unicode: concepts.html |
| A6 | Hebrew-vs-Latin script ordering under `he-IL` (Hebrew sorts before Latin) vs root/`und` (Latin first); pick deliberately or carry an explicit sort key | Unicode: concepts.html (script-reordering) |
| A7 | Collation version drift: `ALTER COLLATION ... REFRESH VERSION` after an ICU/OS upgrade, and the index-corruption risk if you skip it | PostgreSQL 18 docs: sql-altercollation.html |
| A8 | PG18 rule that a PK/FK pair must use deterministic collations or the *same* non-deterministic one (surfaces as a `pg_upgrade`/`pg_restore` failure) | PostgreSQL 18 docs: 18.0 |

### B. Hebrew text normalisation, one row per Unicode sub-block, because the correct action differs per block

| # | Item | Source |
|---|---|---|
| B1 | **Nikud / points (U+05B0-U+05BD, U+05BF, U+05C1, U+05C2, U+05C4, U+05C5, U+05C7)**, general category `Mn`. STRIP for search normalisation | Unicode: U0590.pdf ; Unicode: UnicodeData.txt |
| B2 | **Cantillation / te'amim (U+0591-U+05AF)**, `Mn`. STRIP | same as B1 |
| B3 | **Maqaf U+05BE**, general category `Pd` (dash punctuation), NOT a mark. Must NOT be stripped: stripping merges the two words into one lexeme. Replace with a space or leave for the parser | Unicode: U0590.pdf |
| B4 | **Paseq U+05C0, Sof Pasuq U+05C3, Nun Hafukha U+05C6**, category `Po`. Must NOT be stripped for the same reason as B3 | same as B3 |
| B5 | **Geresh U+05F3 / Gershayim U+05F4**, category `Po`, used in every Israeli acronym (בע״מ, צה״ל, ח״כ, ש״ח, ע״מ, ח״פ). Requires an explicit strategy: the default FTS parser classifies them as `blank`, shattering the acronym | PostgreSQL 18 docs: textsearch-parsers.html ; Unicode: U0590.pdf |
| B6 | ASCII `'`/`"` substituted for geresh/gershayim in user input, and the normalisation needed so both spellings match | Unicode: U0590.pdf |
| B7 | `unaccent` does NOT touch Hebrew points (its rules cover Latin/Greek); an `IMMUTABLE` `f_unaccent()` wrapper is still needed for Latin columns in generated columns / expression indexes | PostgreSQL 18 docs: unaccent.html |
| B8 | Sofit ↔ base-letter folding (ם↔מ, ן↔נ, ך↔כ, ף↔פ, ץ↔צ) as an explicit normalisation decision, since no collation strength gives it without also folding nikud | Unicode: U0590.pdf |

### C. Hebrew search

| # | Item | Source |
|---|---|---|
| C1 | No Hebrew stemmer/dictionary ships with PostgreSQL; `simple` is the correct config; `'hebrew'` does not exist | PostgreSQL 18 docs: textsearch-dictionaries.html |
| C2 | **Clitic/prefix recall**: ו/ב/כ/ל/ה/מ/ש attach to the word, so ספר/הספר/בספר/וספרים are distinct lexemes under `simple`. Requires a stated recall strategy (trigram companion branch, prefix-stripping normalisation, or a synonym/thesaurus dictionary) | PostgreSQL 18 docs: textsearch-dictionaries.html (TEXTSEARCH-SYNONYM-DICTIONARY) |
| C3 | Acronym tokenisation: the default parser reports U+05F4 as `blank`, so `בע״מ` indexes as `בע` + `מ` and a user typing `בעמ` matches nothing. Requires an explicit mitigation | PostgreSQL 18 docs: textsearch-parsers.html |
| C4 | Mixed-language vector: Hebrew columns under `simple`, English columns under `english` (stemmed), and the consequence that a `simple`-only tsquery can never match a stemmed English lexeme, the query must OR both configs (or the vector must not mix configs) | PostgreSQL 18 docs: textsearch-controls.html |
| C5 | `setweight` + `ts_rank` / `ts_rank_cd` for multi-field ranking; generated `tsvector` column must be built from `IMMUTABLE` functions only | PostgreSQL 18 docs: textsearch-controls.html (TEXTSEARCH-RANKING) ; PostgreSQL 18 docs: ddl-generated-columns.html |
| C6 | **pg_trgm operator matrix, one row per operator**: `%` / `similarity()` (whole-string, gated by `pg_trgm.similarity_threshold`, default 0.3) · `<%` / `word_similarity()` (gated by the SEPARATE `pg_trgm.word_similarity_threshold`, default 0.6) · `<<%` / `strict_word_similarity()` (gated by `pg_trgm.strict_word_similarity_threshold`, default 0.5) · `<->` distance (GiST/KNN only). Each operator has its own GUC; setting one does not affect the others | PostgreSQL 18 docs: pgtrgm.html |
| C7 | Column-length rule: `%` for titles/names, `<%`/`<<%` for body/description columns, because whole-string similarity dilutes as the column grows | PostgreSQL 18 docs: pgtrgm.html |
| C8 | Index usability: `gin_trgm_ops` vs `gist_trgm_ops`, and that wrapping the indexed column in a function (`coalesce(col,'')`, `lower(col)`) makes the plain column index unusable, you need the matching expression index or a `NOT NULL`/`DEFAULT ''` column | PostgreSQL 18 docs: indexes-expressional.html ; PostgreSQL 18 docs: pgtrgm.html |
| C9 | Short-word behaviour: Hebrew words are short (no written vowels), so 3-letter queries produce few trigrams and low similarity; threshold tuning is Hebrew-specific | PostgreSQL 18 docs: pgtrgm.html |
| C10 | Normalisation must be applied symmetrically to BOTH the stored side and the query side, and to BOTH the FTS branch and the trigram branch (otherwise pointed stored text matches under FTS and not under trigram) | PostgreSQL 18 docs: textsearch-controls.html |

### D. NIS currency

| # | Item | Source |
|---|---|---|
| D1 | `numeric` for money; never `float`/`double precision`; ISO 4217 code `ILS`, symbol ₪, 2 minor units | PostgreSQL 18 docs: datatype-numeric.html ; iso.org: iso-4217-currency-codes.html |
| D2 | Never `money` type (locale-dependent, fixed fractional digits from `lc_monetary`) | PostgreSQL 18 docs: datatype-money.html |
| D3 | **VAT rate is time-varying, not a constant**, a rate must be resolved as-of the invoice date, not read from a singleton row, or historical invoices re-price when the rate changes | gov.il: israel_tax_authority |
| D4 | **VAT rate table by transaction category, one row per category**: standard-rated · zero-rated (exports, tourist services) · exempt (specific transactions) · Eilat free-trade-zone. A single `vat_rate` column per invoice cannot represent a mixed-rate invoice | gov.il: israel_tax_authority |
| D5 | Rounding: per-line rounding vs whole-invoice rounding, and that a `CHECK` asserting one of them will reject invoices produced by the other | PostgreSQL 18 docs: functions-math.html |
| D6 | **Signed documents**: credit notes (חשבונית זיכוי) carry negative amounts, so a `CHECK (amount >= 0)` on a table whose type enum includes credit notes rejects valid production data | gov.il: israel_tax_authority |
| D7 | BOI representative rates: keyed by `(currency, effective_date)`, and the **as-of** lookup (`effective_date <= $1 ORDER BY ... DESC LIMIT 1`) because no rate is published on Shabbat or Israeli holidays | boi.org.il: exchange-rates |
| D8 | Display formatting belongs in the app layer (`Intl.NumberFormat('he-IL', {currency:'ILS'})`), not `to_char` with a hardcoded ₪ | developer.mozilla.org: NumberFormat |

### E. Asia/Jerusalem timezone

| # | Item | Source |
|---|---|---|
| E1 | `timestamptz` everywhere; `timestamp` loses the offset; `ALTER DATABASE ... SET timezone` sets the *display* zone only | PostgreSQL 18 docs: datatype-datetime.html (DATATYPE-TIMEZONES) |
| E2 | Israel DST rule (IST UTC+2 / IDT UTC+3) and its dependence on the tzdata bundled with the server or container image; pinned/stale tzdata silently shifts every local render | PostgreSQL 18 docs: datatype-datetime.html (DATATYPE-TIMEZONES) |
| E3 | Spring-forward gap and autumn ambiguity: a local wall-clock literal cast to `timestamptz` in the ambiguous hour resolves silently to one of the two instants | PostgreSQL 18 docs: functions-datetime.html |
| E4 | **Sargability**: `(ts AT TIME ZONE 'Asia/Jerusalem')::date = $1` cannot use a btree index on `ts`. Use a half-open `timestamptz` range, or `date_trunc('day', ts, 'Asia/Jerusalem')` (3-arg, PG16+) backed by a matching expression index | PostgreSQL 18 docs: functions-datetime.html (FUNCTIONS-DATETIME-TRUNC) ; PostgreSQL 18 docs: indexes-expressional.html |
| E5 | `AT TIME ZONE` on `timestamptz` is `STABLE`, not `IMMUTABLE`; it cannot back a generated column or a plain expression index | PostgreSQL 18 docs: xfunc-volatility.html |
| E6 | Israeli week shape: Sunday-Thursday business week, Friday short day, `EXTRACT(dow)` 0=Sunday, and `EXTRACT(isodow)` 7=Sunday | PostgreSQL 18 docs: functions-datetime.html |
| E7 | Shabbat and chagim are sunset-relative and not derivable in SQL; the boundary must come from a calendar source and be stored as `timestamptz` | hebcal.com: developer-apis |
| E8 | Israeli display format is DD/MM/YYYY; never store dates as text | PostgreSQL 18 docs: functions-formatting.html |

### F. Israeli data types, one row per identifier, because each has its own format AND its own check rule

| # | Item | Source |
|---|---|---|
| F1 | **Teudat Zehut**: text (never integer), exactly 9 digits, **left-padded with zeros** because real IDs are shorter and lose leading zeros through Excel/CSV; Luhn-variant check digit | gov.il: identity_card |
| F2 | **Company / ח״פ number**: 9 digits, uses the same check-digit algorithm as Teudat Zehut; range distinguishes entity class | gov.il: corporations_authority |
| F3 | **Osek Murshe / Osek Patur (ע.מ.) number**: 9 digits, equals the Teudat Zehut for a sole trader | gov.il: israel_tax_authority |
| F4 | **Amuta (non-profit) number**: 9 digits, distinct registry | gov.il: corporations_authority |
| F5 | **Phone number table, one row per prefix class**: 05X mobile (10 digits) · 07X non-geographic/VoIP (10) · 0[2,3,4,8,9]X landline (9) · 1-700/1-800 service (10) · *XXX/*XXXX short codes · +972 E.164. A single regex covering only mobiles rejects valid production data | gov.il: ministry_of_communications |
| F6 | **Postal code (mikud)**: 7 digits since the 2013 renumbering; legacy records hold 5 digits, so historical imports need a relaxed constraint | israelpost.co.il: zipcode |
| F7 | **Israeli IBAN**: `IL` + 21 digits (23 chars); the shape check is not the mod-97 ISO 7064 checksum | iso.org: 81090.html |
| F8 | **Bank + branch + account**: 2-digit bank code, 3-4 digit branch, variable account length; codes change on mergers, so validate against the BOI registry rather than a hardcoded list | boi.org.il: en |
| F9 | **Invoice numbering**: Israeli bookkeeping rules require a per-business consecutive series, so a single global `serial` shared across tenants is wrong; needs `(business_id, invoice_number)` uniqueness and a per-business counter | gov.il: israel_tax_authority |
| F10 | **ITA allocation number (מספר הקצאה)** for the e-invoice mandate: which invoices require one and the threshold that triggers it | gov.il: israel_tax_authority |
| F11 | Bilingual name/address columns (`*_he` / `*_en`), house numbers as text (`12א`, `12/3`), English-only column identifiers so PostgREST URLs stay sane | docs.postgrest.org: tables_views.html |

### G. RLS for multi-tenant Israeli SaaS

| # | Item | Source |
|---|---|---|
| G1 | `ENABLE ROW LEVEL SECURITY` on every tenant table; a table with policies but RLS not enabled is wide open, and the table owner bypasses RLS unless `FORCE ROW LEVEL SECURITY` | PostgreSQL 18 docs: ddl-rowsecurity.html |
| G2 | PERMISSIVE (OR'd) vs RESTRICTIVE (AND'd) policies; tenant isolation belongs in a RESTRICTIVE policy so a later permissive policy cannot widen it | PostgreSQL 18 docs: sql-createpolicy.html |
| G3 | `USING` vs `WITH CHECK` per command; INSERT reads only `WITH CHECK`; a `FOR ALL` policy without `WITH CHECK` reuses `USING` | PostgreSQL 18 docs: sql-createpolicy.html |
| G4 | `TO authenticated`, without a role clause the policy is also evaluated for `anon` | Supabase docs: database/postgres/row-level-security |
| G5 | **Claim-source table, one row per source**: `auth.uid()` (trustworthy) · `auth.jwt() -> 'app_metadata'` (server-controlled, safe for tenant_id/role) · `auth.jwt() -> 'user_metadata'` (**end-user writable, never authorize on it**) · top-level custom claims (require a custom access token hook, absent by default) | Supabase docs: database/postgres/row-level-security ; Supabase docs: auth/custom-claims-and-role-based-access-control-rbac |
| G6 | `service_role` has `bypassrls`; any Edge Function using the service key ignores every policy, so tenant scoping must be re-applied in code there | Supabase docs: database/postgres/row-level-security |
| G7 | Performance: wrap `auth.uid()` / `auth.jwt()` as `(select auth.uid())` so the optimizer builds an initPlan instead of calling per row | Supabase docs: database/postgres/row-level-security |
| G8 | Index every column referenced in a policy predicate (`tenant_id`, `user_id`) | Supabase docs: database/postgres/row-level-security |
| G9 | `SECURITY DEFINER` functions must `SET search_path = ''` and use schema-qualified names; Supabase's linter flags `function_search_path_mutable` and `security_definer_view` | Supabase docs: database/database-linter |
| G10 | Everything in `public` is auto-exposed by PostgREST, including helper functions as RPC; revoke `EXECUTE` from `anon` on anything not meant to be public | docs.postgrest.org: functions.html |

---

## Should cover (advanced)

| # | Item | Source |
|---|---|---|
| S1 | Single `jsonb {he,en}` bilingual-content column as an alternative to paired `*_he`/`*_en` columns, plus its indexing story (`jsonb_path_ops` GIN, or expression indexes on `->>'he'`) and why FTS over it needs an expression `tsvector` | PostgreSQL 18 docs: datatype-json.html (JSON-INDEXING) |
| S2 | `ILIKE` vs `pg_trgm` decision guide: leading-wildcard `ILIKE` is index-usable only via `gin_trgm_ops`; `text_pattern_ops` btree covers anchored `LIKE` on `C`-collated/deterministic columns only | PostgreSQL 18 docs: pgtrgm.html (PGTRGM-INDEX) ; PostgreSQL 18 docs: indexes-opclass.html |
| S3 | Synonym / thesaurus dictionary as a first-class Hebrew recall tool (acronym expansion, clitic stripping) instead of relying on trigram fallback alone | PostgreSQL 18 docs: textsearch-dictionaries.html (TEXTSEARCH-THESAURUS) |
| S4 | `websearch_to_tsquery` / `phraseto_tsquery` and prefix queries (`:*`) for Hebrew autocomplete | PostgreSQL 18 docs: textsearch-controls.html |
| S5 | RUM index or `pgvector` semantic search as the answer to Hebrew morphology when trigram recall is not enough | github.com: pgvector |
| S6 | Bidi/RTL storage hygiene: U+200E/U+200F/U+202A-U+202E control characters pasted from Word/PDF, and stripping them before indexing | Unicode: tr9 |
| S7 | Unicode normalisation form: `normalize(text, NFC)` and the `IS NORMALIZED` predicate, since Hebrew presentation forms (U+FB1D-U+FB4F) and decomposed points arrive from OCR/legacy systems | PostgreSQL 18 docs: functions-string.html |
| S8 | Partitioning by Israeli fiscal year (calendar year) and partition pruning on a `date` key | PostgreSQL 18 docs: ddl-partitioning.html |
| S9 | Materialized views for expensive Hebrew-collated sorts; `REFRESH ... CONCURRENTLY` requires a non-partial UNIQUE index; a matview's own `ORDER BY` does not guarantee read order | PostgreSQL 18 docs: sql-refreshmaterializedview.html |
| S10 | Supavisor transaction mode (6543) vs session mode (5432) vs direct connection, and what breaks in transaction mode (prepared statements, `SET`/session GUCs, `LISTEN`) | Supabase docs: database/connecting-to-postgres |
| S11 | Region choice and latency for Israeli traffic; measure rather than assume | Supabase docs: platform/regions |
| S12 | Israeli privacy law (Protection of Privacy Law Amendment 13) implications for a database: data-subject deletion, audit logging, and encryption-at-rest posture | gov.il: the_privacy_protection_authority |
| S13 | Withholding tax (ניכוי מס במקור) modelling: rate is per-supplier and time-bounded by an ITA certificate, so it is not a constant column default | gov.il: israel_tax_authority |
| S14 | Israeli payment-provider webhooks (Cardcom, Tranzila, PayPlus): amount units (agorot vs shekels), legacy windows-1255 payloads, provider-specific signature verification | Supabase docs: functions |
| S15 | `pg_stat_statements` and `EXPLAIN (ANALYZE, BUFFERS)` as the verification loop for every index claim above | PostgreSQL 18 docs: pgstatstatements.html |
| S16 | Hebrew calendar storage: store Gregorian as the key plus a rendered Hebrew display string; conversion in the app layer | hebcal.com: developer-apis |

---

## Out of scope (explicit)

- General PostgreSQL administration unrelated to Israeli requirements (WAL tuning, replication topology, autovacuum theory, backup scheduling).
- Non-PostgreSQL databases (MySQL, MongoDB, SQL Server) and their Hebrew handling.
- Application-layer i18n: RTL CSS, Next.js locale routing, Hebrew font stacks.
- Israeli tax *advice*. The skill models the data shape; it does not tell anyone what they owe. Any rate figure is illustrative and must be re-verified against the ITA.
- Building a Hebrew morphological analyser or a Hebrew stemmer dictionary from scratch.
- Israeli payment-provider API integration details beyond what the database must store.
- Supabase Auth UI, Realtime channel design, and Storage CDN behaviour except where Hebrew encoding is involved.

---

## Authoritative sources

Referenced by name rather than by URL: this file is an internal coverage contract, and bare
URLs here are read by the evidence gate as unbacked citations. The URLs that back published
claims live in `evidence.json`.


| Source | URL |
|---|---|
| PostgreSQL 18, Collation Support | PostgreSQL 18 docs: collation.html |
| PostgreSQL 18, Release Notes (LIKE on nondeterministic collations; PK/FK collation rule) | PostgreSQL 18 docs: 18.0 |
| PostgreSQL 18, Full Text Search: parsers | PostgreSQL 18 docs: textsearch-parsers.html |
| PostgreSQL 18, Full Text Search: dictionaries / thesaurus | PostgreSQL 18 docs: textsearch-dictionaries.html |
| PostgreSQL 18, Full Text Search: controls and ranking | PostgreSQL 18 docs: textsearch-controls.html |
| PostgreSQL 18, pg_trgm | PostgreSQL 18 docs: pgtrgm.html |
| PostgreSQL 18, unaccent | PostgreSQL 18 docs: unaccent.html |
| PostgreSQL 18, Row Security Policies | PostgreSQL 18 docs: ddl-rowsecurity.html |
| PostgreSQL 18, CREATE POLICY | PostgreSQL 18 docs: sql-createpolicy.html |
| PostgreSQL 18, Date/Time types and functions | PostgreSQL 18 docs: datatype-datetime.html |
| PostgreSQL 18, Function volatility categories | PostgreSQL 18 docs: xfunc-volatility.html |
| PostgreSQL 18, Generated columns / expression indexes | PostgreSQL 18 docs: ddl-generated-columns.html |
| PostgreSQL 18, Numeric types / money type | PostgreSQL 18 docs: datatype-numeric.html |
| Supabase, Row Level Security | Supabase docs: database/postgres/row-level-security |
| Supabase, Custom Claims and RBAC | Supabase docs: auth/custom-claims-and-role-based-access-control-rbac |
| Supabase, Database Linter | Supabase docs: database/database-linter |
| Supabase, Connecting to Postgres (Supavisor) | Supabase docs: database/connecting-to-postgres |
| PostgREST, Functions as RPC | docs.postgrest.org: functions.html |
| ICU User Guide, Collation Concepts (strength, script reordering) | Unicode: concepts.html |
| Unicode, Hebrew block chart U+0590-U+05FF (general categories) | Unicode: U0590.pdf |
| Unicode, UAX #9 Bidirectional Algorithm | Unicode: tr9 |
| Bank of Israel, Representative exchange rates | boi.org.il: exchange-rates |
| Israel Tax Authority | gov.il: israel_tax_authority |
| Israel Post, mikud lookup | israelpost.co.il: zipcode |
| Hebcal developer APIs (Shabbat/holiday boundaries) | hebcal.com: developer-apis |
