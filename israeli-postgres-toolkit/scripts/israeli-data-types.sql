-- israeli-data-types.sql
-- Complete CREATE TABLE templates with Israeli-specific columns,
-- constraints, and validations for PostgreSQL / Supabase.
--
-- Usage: Copy and adapt the relevant tables for your project.
-- These are templates, not a complete schema.

-- ============================================================================
-- 1. Israeli Customer / Contact
-- ============================================================================

CREATE TABLE IF NOT EXISTS customers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Identity
  teudat_zehut text UNIQUE CHECK (teudat_zehut ~ '^\d{9}$'),
  passport_number text,
  tax_id text,  -- Osek Murshe / Osek Patur number (9 digits)

  -- Bilingual names
  first_name_he text NOT NULL,
  last_name_he text NOT NULL,
  first_name_en text,
  last_name_en text,

  -- Contact
  email text CHECK (email ~* '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
  phone_mobile text CHECK (phone_mobile ~ '^05\d{8}$'),
  -- Landline area codes only (02/03/04/08/09), matching SKILL.md. 05X mobile and
  -- 07X VoIP are 10 digits and belong in phone_mobile / their own column.
  phone_landline text CHECK (phone_landline ~ '^0[23489]\d{7}$'),
  phone_e164 text CHECK (phone_e164 ~ '^\+972\d{8,9}$'),

  -- Preferences
  preferred_language text NOT NULL DEFAULT 'he' CHECK (preferred_language IN ('he', 'en')),

  -- Metadata
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. Israeli Address
-- ============================================================================

CREATE TABLE IF NOT EXISTS addresses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid NOT NULL REFERENCES customers(id) ON DELETE CASCADE,

  -- Address type
  address_type text NOT NULL DEFAULT 'home' CHECK (
    address_type IN ('home', 'work', 'mailing', 'billing')
  ),

  -- Street address
  street_he text NOT NULL,
  street_en text,
  house_number text NOT NULL,   -- Text to handle "12/3", "12א", etc.
  entrance text,                -- כניסה (A, B, C or א, ב, ג)
  floor text,                   -- קומה
  apartment text,               -- דירה

  -- City and region
  city_he text NOT NULL,
  city_en text,
  neighborhood_he text,         -- שכונה
  -- Israeli postal code (mikud): 7 digits since the 2013 renumbering. Older records
  -- may still hold the legacy 5-digit code, so migrate or relax this before importing
  -- historical data, and confirm the current format via Israel Post's mikud lookup.
  postal_code text CHECK (postal_code ~ '^\d{7}$'),

  -- Region classification
  region text CHECK (region IN (
    'north', 'haifa', 'center', 'tel-aviv',
    'jerusalem', 'south', 'judea-samaria'
  )),

  -- Geolocation (optional)
  latitude numeric(10, 7),
  longitude numeric(10, 7),

  -- Metadata
  is_primary boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Ensure only one primary address per customer per type
CREATE UNIQUE INDEX IF NOT EXISTS idx_addresses_primary
  ON addresses (customer_id, address_type)
  WHERE is_primary = true;

-- ============================================================================
-- 3. Israeli Business Entity
-- ============================================================================

CREATE TABLE IF NOT EXISTS businesses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Registration
  business_number text UNIQUE CHECK (business_number ~ '^\d{9}$'),
  -- ח.פ. (Hevra Pratit) or ע.מ. (Osek Murshe)
  entity_type text NOT NULL CHECK (entity_type IN (
    'osek_patur',     -- עוסק פטור (exempt dealer, under VAT threshold)
    'osek_murshe',    -- עוסק מורשה (licensed dealer)
    'hevra_pratit',   -- חברה פרטית (private company)
    'hevra_tziburit', -- חברה ציבורית (public company)
    'amuta',          -- עמותה (non-profit)
    'shutafut'        -- שותפות (partnership)
  )),

  -- Bilingual names
  name_he text NOT NULL,
  name_en text,

  -- Tax info
  vat_registered boolean NOT NULL DEFAULT true,
  tax_deduction_rate numeric(5, 4) DEFAULT 0.0000,  -- ניכוי מס במקור

  -- Contact
  phone text,
  email text,
  website text,

  -- Metadata
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================================================
-- 4. Israeli Invoice (Heshbonit Mas)
-- ============================================================================

CREATE TABLE IF NOT EXISTS invoices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Invoice identity.
  -- NOT a serial. Israeli bookkeeping requires each business to keep its OWN
  -- consecutive series, and a shared sequence gives every tenant a gapped,
  -- interleaved numbering that also leaks the platform's total invoice volume.
  -- Allocate per business and enforce it with the UNIQUE constraint below.
  invoice_number bigint NOT NULL,
  invoice_type text NOT NULL CHECK (invoice_type IN (
    'heshbonit_mas',          -- חשבונית מס (tax invoice)
    'heshbonit_mas_kabala',   -- חשבונית מס / קבלה (tax invoice / receipt)
    'kabala',                 -- קבלה (receipt)
    'heshbon_iska',           -- חשבון עסקה (transaction account)
    'tofes_50',               -- טופס 50 (withholding tax confirmation)
    'hashbonit_zikui'         -- חשבונית זיכוי (credit invoice)
  )),

  -- Parties
  business_id uuid NOT NULL REFERENCES businesses(id),
  customer_id uuid REFERENCES customers(id),

  -- Amounts (always in NIS unless otherwise specified)
  -- Sign is governed by invoice_type, not by a blanket >= 0. A credit invoice
  -- (חשבונית זיכוי) reverses an issued tax invoice and therefore carries NEGATIVE
  -- amounts, so a >= 0 CHECK here would enumerate the type above and then reject
  -- every row of it. See invoices_sign_matches_type below.
  subtotal_nis numeric(12, 2) NOT NULL,
  vat_rate numeric(5, 4) NOT NULL DEFAULT 0.1800,  -- 18% as of 2025
  vat_amount numeric(12, 2) NOT NULL,
  total_nis numeric(12, 2) NOT NULL,

  -- Withholding tax (ניכוי מס במקור)
  withholding_tax_rate numeric(5, 4) DEFAULT 0.0000,
  withholding_tax_amount numeric(12, 2) DEFAULT 0.00,
  net_payment_nis numeric(12, 2),  -- total minus withholding

  -- Foreign currency (optional)
  foreign_currency text CHECK (foreign_currency IN ('USD', 'EUR', 'GBP')),
  foreign_amount numeric(12, 2),
  exchange_rate numeric(12, 6),

  -- Dates
  invoice_date date NOT NULL DEFAULT CURRENT_DATE,
  due_date date,
  payment_date date,

  -- Status
  status text NOT NULL DEFAULT 'draft' CHECK (status IN (
    'draft', 'sent', 'paid', 'overdue', 'cancelled', 'credited'
  )),

  -- Israeli tax authority digital reporting
  allocation_number text,  -- מספר הקצאה (from ITA e-invoice system)

  -- Metadata
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),

  -- Each business numbers its own invoices independently.
  UNIQUE (business_id, invoice_number),

  -- Credit invoices are negative, every other type is positive.
  CONSTRAINT invoices_sign_matches_type CHECK (
    CASE WHEN invoice_type = 'hashbonit_zikui'
         THEN subtotal_nis <= 0
         ELSE subtotal_nis >= 0
    END
  )
);

-- Validate VAT calculation
ALTER TABLE invoices ADD CONSTRAINT check_vat_calculation
  CHECK (vat_amount = round(subtotal_nis * vat_rate, 2));

ALTER TABLE invoices ADD CONSTRAINT check_total_calculation
  CHECK (total_nis = subtotal_nis + vat_amount);

-- ============================================================================
-- 5. Tax Configuration (Singleton)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tax_config (
  id int PRIMARY KEY DEFAULT 1 CHECK (id = 1),  -- Enforce singleton

  -- Current VAT rate
  vat_rate numeric(5, 4) NOT NULL DEFAULT 0.1800,

  -- Osek Patur annual turnover ceiling. CPI-indexed every January, so treat this
  -- default as a starting value and re-check it each year against
  -- https://www.kolzchut.org.il/he/עוסק_פטור  (2026: 122,833; 2025: 120,000).
  osek_patur_threshold numeric(12, 2) NOT NULL DEFAULT 122833.00,

  -- Bituah Leumi rates: DELIBERATELY no default, and nullable.
  -- A single pair of numbers cannot represent these. Both the employee and the
  -- employer rate change at the reduced/full wage band, and the employee rate also
  -- varies by age band, pension status and disability status. Storing one value
  -- here and multiplying by it is how payroll code silently overcharges pensioners
  -- and minors. Populate per band from the current BTL rate table, or keep the
  -- calculation in a dedicated payroll component instead of this config row.
  employee_bituah_leumi_rate numeric(5, 4),
  employer_bituah_leumi_rate numeric(5, 4),

  -- Metadata
  effective_from date NOT NULL DEFAULT CURRENT_DATE,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Insert default config
INSERT INTO tax_config DEFAULT VALUES ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 6. Exchange Rates (Bank of Israel)
-- ============================================================================

CREATE TABLE IF NOT EXISTS exchange_rates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  currency_code text NOT NULL,          -- ISO 4217: USD, EUR, GBP, etc.
  rate_to_ils numeric(12, 6) NOT NULL,  -- How many ILS per 1 unit
  effective_date date NOT NULL,
  source text NOT NULL DEFAULT 'BOI',   -- Bank of Israel
  fetched_at timestamptz NOT NULL DEFAULT now(),

  UNIQUE (currency_code, effective_date)
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_exchange_rates_lookup
  ON exchange_rates (currency_code, effective_date DESC);

-- ============================================================================
-- 7. Israeli Bank Account
-- ============================================================================

CREATE TABLE IF NOT EXISTS bank_accounts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id uuid REFERENCES customers(id),
  business_id uuid REFERENCES businesses(id),

  -- Israeli bank details
  bank_code text NOT NULL CHECK (bank_code ~ '^\d{2}$'),
  -- Bank codes below are the commonly seen ones and are given as orientation only.
  -- Validate against the Bank of Israel's current bank and branch registry before
  -- relying on them: a wrong code silently misroutes a payment, and codes change
  -- when banks merge. Commonly seen: 10 (Leumi), 11 (Discount), 12 (Hapoalim),
  -- 20 (Mizrahi-Tefahot), 31 (International).
  branch_code text NOT NULL CHECK (branch_code ~ '^\d{3,4}$'),
  account_number text NOT NULL CHECK (account_number ~ '^\d{6,9}$'),

  -- IBAN (optional, for international transfers)
  -- Israeli IBAN: 'IL' plus 21 digits (23 characters total) per the ISO 13616
  -- national structure. This is a LENGTH/shape check only; it does not validate the
  -- mod-97 checksum, so do that in the application layer before initiating a transfer.
  iban text CHECK (iban ~ '^IL\d{21}$'),

  -- Display
  bank_name_he text,
  branch_name_he text,

  -- Metadata
  is_primary boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),

  -- At least one owner
  CHECK (customer_id IS NOT NULL OR business_id IS NOT NULL)
);

-- ============================================================================
-- 8. Helper Functions
-- ============================================================================

-- Validate Teudat Zehut check digit (Luhn-variant algorithm)
CREATE OR REPLACE FUNCTION validate_teudat_zehut(tz text)
RETURNS boolean AS $$
DECLARE
  digits int[];
  total int := 0;
  val int;
  i int;
BEGIN
  -- Must be exactly 9 digits
  IF tz !~ '^\d{9}$' THEN
    RETURN false;
  END IF;

  -- Parse digits
  FOR i IN 1..9 LOOP
    digits[i] := substr(tz, i, 1)::int;
  END LOOP;

  -- Apply Luhn-variant: multiply odd positions by 1, even by 2
  FOR i IN 1..9 LOOP
    IF i % 2 = 0 THEN
      val := digits[i] * 2;
    ELSE
      val := digits[i] * 1;
    END IF;

    -- Sum digits if >= 10
    IF val > 9 THEN
      val := val - 9;
    END IF;

    total := total + val;
  END LOOP;

  RETURN total % 10 = 0;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Format Israeli phone number for display
CREATE OR REPLACE FUNCTION format_israeli_phone(phone text)
RETURNS text AS $$
BEGIN
  IF phone ~ '^05\d{8}$' THEN
    -- Mobile: 050-1234567
    RETURN substr(phone, 1, 3) || '-' || substr(phone, 4);
  ELSIF phone ~ '^0[23489]\d{7}$' THEN
    -- Landline: 02-1234567 or 03-1234567 (area codes only, matching the CHECK above)
    RETURN substr(phone, 1, 2) || '-' || substr(phone, 3);
  ELSE
    RETURN phone;
  END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
