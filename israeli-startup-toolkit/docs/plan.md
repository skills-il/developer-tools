# Israeli Startup Toolkit Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a skill for Israeli startup operations — covering Israel Innovation Authority grants, company formation, investment agreements, R&D tax benefits, and employee stock option plans (Option 102).

**Architecture:** MCP Enhancement skill (Category 3). Guides entrepreneurs through Israeli startup legal, financial, and operational requirements with practical templates and regulatory references.

**Tech Stack:** SKILL.md, references for IIA programs, Israeli Companies Law, tax authority guidelines, and Option 102 regulations.

---

## Research

### Israel Innovation Authority (IIA)
- **Website:** innovationisrael.org.il
- **Role:** Government body supporting R&D and innovation
- **Budget:** ~1.8B NIS annually
- **Key programs:**
  - **R&D Fund (Keren HaMechkar):** Up to 50% of approved R&D budget, conditionally repayable via royalties (3-5% of revenue)
  - **Startup Division (Tnufa):** Up to 85% of budget, max 800K NIS for early-stage
  - **Incubator Program:** Up to 85% funding, 2-year program in approved incubators
  - **Binational funds:** BIRD (US-Israel), CIIRDF (Canada-Israel), KORIL (Korea-Israel)
  - **Multinational programs:** Horizon Europe, bilateral agreements
- **Eligibility:** Israeli registered company, R&D conducted in Israel, IP owned by company
- **Application:** Online via IIA portal, reviewed by professional committee
- **Restrictions:** IP cannot be transferred abroad without IIA approval and payment

### Israeli Company Formation
- **Entity types:**
  - **Chevra Ba'am (Ltd / בע"מ):** Private limited company — most common for startups
  - **Chevra Tziburit:** Public company (for later stage)
  - **Shutafut:** Partnership (less common for tech)
- **Registration:** Rasham HaChavarot (Companies Registrar), Ministry of Justice
- **Requirements:**
  - Minimum 1 shareholder, 1 director
  - Registered address in Israel
  - Articles of association (takanon)
  - Registration fee: ~2,600 NIS
- **Timeline:** 3-7 business days online registration
- **Annual obligations:** Annual report to registrar, tax returns, VAT if applicable

### Investment Agreement Types
- **SAFE (Simple Agreement for Future Equity):**
  - Israeli version similar to Y Combinator SAFE
  - Common for pre-seed/seed in Israeli startups
  - Typically includes valuation cap and/or discount
  - Israeli legal adaptations: governing law (Israeli), dispute resolution
- **Convertible Note:**
  - Debt instrument converting to equity at next round
  - Interest rate: typically 5-8% annually
  - Maturity: 12-24 months
  - Israeli tax implications differ from US
- **Preferred Share Round (Series A+):**
  - Standard NVCA-style documents adapted for Israeli law
  - Israeli Companies Law governs (not Delaware)
  - Common terms: liquidation preference, anti-dilution, board seats
  - Investor rights agreement, shareholders agreement, articles amendment
- **R&D Partnership (Shutafut Mechkar):**
  - Unique Israeli structure for R&D tax benefits
  - Investors get R&D tax deductions
  - Less common post-2016 tax reform

### R&D Tax Benefits
- **Section 20a (Income Tax Ordinance):** R&D expenses deductible in year incurred
- **Reduced corporate tax:** "Preferred Enterprise" — 7.5% in Area A, 16% elsewhere
- **IP regime:** "Preferred Technological Enterprise" — 6% on IP income in Area A, 12% elsewhere
- **Angel Law (Section 20c):** Tax deduction for investors in qualifying R&D companies (up to 5M NIS investment)
- **Accelerated depreciation:** For R&D equipment and facilities

### Option 102 (Employee Stock Options)
- **Section 102 of Income Tax Ordinance:** Israeli employee equity compensation framework
- **Tracks:**
  - **Capital Gains Track (Trustee — 102):** Most common
    - Shares held by trustee for 24-month holding period
    - Taxed as capital gains (25%) instead of income (up to 50%)
    - Employer gets no tax deduction
  - **Income Track (Trustee — 102):** Less common
    - Shares held by trustee for 12-month holding period
    - Taxed as income (up to 50%)
    - Employer gets tax deduction
  - **Non-Trustee Track (102):**
    - No trustee, no holding period
    - Taxed as income (up to 50%)
  - **Section 3(i):** For non-employees (consultants, advisors)
    - Taxed as income, no special benefit
- **Trustee:** Must be an ITA-approved trustee (banks, trust companies)
- **Filing:** Plan filed with ITA, 30-day objection period
- **Common vesting:** 4-year vesting, 1-year cliff (standard globally)

### Use Cases
1. **Company formation** — Register an Israeli startup (Ltd/בע"מ)
2. **Grant applications** — Apply to IIA R&D Fund, Tnufa, incubators
3. **Investment structure** — Draft SAFE, convertible note, or priced round
4. **Tax optimization** — R&D deductions, preferred enterprise status
5. **Employee equity** — Set up Option 102 plan with trustee

---

## Build Steps

### Task 1: Create SKILL.md

**Files:**
- Create: `repos/developer-tools/israeli-startup-toolkit/SKILL.md`

```markdown
---
name: israeli-startup-toolkit
description: >-
  Guide Israeli startup operations including company formation, Innovation
  Authority grants, investment agreements, R&D tax benefits, and employee
  stock options (Option 102). Use when user asks about starting a company in
  Israel, IIA grants, "Innovation Authority", SAFE agreements (Israeli),
  convertible notes, Option 102, employee stock options in Israel, R&D tax
  benefits, preferred enterprise, or Israeli startup legal/financial setup.
  Do NOT use for non-Israeli company formation or international tax advice.
  Always recommend consulting with Israeli lawyer and accountant for binding
  decisions.
license: MIT
allowed-tools: "Bash(python:*) WebFetch"
compatibility: "No API keys required. Network access helpful for IIA portal reference. Always consult licensed Israeli professionals for legal/tax decisions."
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags: [startup, company-formation, grants, investment, tax, option-102, israel]
---

# Israeli Startup Toolkit

## Instructions

**IMPORTANT DISCLAIMER:** This skill provides general guidance only. Israeli corporate law, tax law, and securities regulation are complex. Always consult with a licensed Israeli lawyer (עורך דין) and accountant (רואה חשבון) before making binding decisions.

### Step 1: Identify Startup Stage

| Stage | Typical Needs | Key Actions |
|-------|--------------|-------------|
| Idea / Pre-seed | Company formation, initial funding | Register Ltd, apply to Tnufa |
| Seed | First investment, team building | SAFE/convertible note, Option 102 plan |
| Series A | Growth funding, scaling | Priced round, preferred enterprise status |
| Growth | Expansion, international | IP regime, binational grants |

### Step 2: Company Formation

**Register an Israeli Ltd (חברה בע"מ):**

```
Step-by-step registration:

1. Choose company name
   - Check availability: ica.justice.gov.il
   - Must be unique, Hebrew or English
   - Suffix: בע"מ (Ltd)

2. Prepare Articles of Association (תקנון)
   - Standard template available from Companies Registrar
   - Customize: share classes, board composition, transfer restrictions
   - Recommended: Use lawyer-drafted articles for startups

3. Appoint initial directors
   - Minimum: 1 director
   - Israeli residency not required (but practical for banking)
   - Director ID (teudat zehut) or passport for foreign directors

4. Register online
   - Portal: ica.justice.gov.il
   - Fee: ~2,600 NIS
   - Timeline: 3-7 business days
   - Documents: Articles, director appointments, registered address

5. Post-registration
   - Open corporate bank account (Bank Leumi, Hapoalim, Discount)
   - Register for tax at local tax office (pakid shuma)
   - Register for VAT if expected revenue > threshold
   - Register for National Insurance (Bituach Leumi) as employer
```

**Founder share allocation example:**
```python
def calculate_founder_allocation(founders: list, vesting_months: int = 48,
                                 cliff_months: int = 12):
    """Calculate founder share allocation with vesting."""
    total_shares = 10_000_000  # Common Israeli startup starting point
    allocation = []

    for founder in founders:
        shares = int(total_shares * founder["percentage"] / 100)
        allocation.append({
            "name": founder["name"],
            "shares": shares,
            "percentage": founder["percentage"],
            "vesting_months": vesting_months,
            "cliff_months": cliff_months,
            "shares_at_cliff": shares * cliff_months // vesting_months,
            "monthly_vesting_after_cliff": shares // vesting_months,
            "share_class": "Ordinary",
        })

    return {
        "total_authorized": total_shares,
        "allocations": allocation,
        "unallocated": total_shares - sum(a["shares"] for a in allocation),
        "note": "Reserve 10-15% for employee option pool (ESOP)"
    }
```

### Step 3: Innovation Authority Grants

**IIA program selection:**

| Program | Stage | Funding | Max Amount | Repayment |
|---------|-------|---------|------------|-----------|
| Tnufa | Pre-seed | Up to 85% | 800K NIS | Royalties 3-5% |
| R&D Fund | Seed-Growth | Up to 50% | Per budget | Royalties 3-5% |
| Incubator | Early stage | Up to 85% | Per program | Royalties |
| BIRD (US-Israel) | Any | Up to 50% | $1M | Royalties |
| Horizon Europe | Any | Varies | Varies | Depends on track |

**Grant application checklist:**
```
IIA R&D Fund Application:

□ Company registered in Israel (Chevra Ba'am)
□ R&D conducted primarily in Israel
□ IP owned by the company (not founders personally)
□ Technological innovation (not just business model)
□ Detailed R&D plan (12-24 months)
□ Budget breakdown (salaries, subcontractors, materials, equipment)
□ Team qualifications (CVs of key R&D personnel)
□ Market analysis and business potential
□ No parallel funding for same R&D from other government sources
□ Commitment to report progress and financials

Application portal: innovationisrael.org.il
Review period: 2-4 months typically
Approval rate: ~40-50% for R&D Fund
```

**Key IIA restrictions:**
- IP developed with IIA funding cannot be transferred abroad without approval
- Transfer fee: up to 6x the grant amount received
- Royalty payments: 3-5% of revenue until grant repaid (with interest)
- Manufacturing preference: IIA prefers production in Israel
- Annual reporting requirements on funded R&D

### Step 4: Investment Agreements

**Israeli SAFE template structure:**
```
Israeli SAFE — Key Terms:

1. Investment Amount: [Amount] NIS or USD
2. Valuation Cap: [Cap] (pre-money)
3. Discount Rate: [15-25%] typical
4. Governing Law: Laws of the State of Israel
5. Dispute Resolution: Tel Aviv courts / arbitration
6. Conversion Trigger: Equity Financing of at least [Amount]
7. MFN Clause: [Yes/No] — Most Favored Nation
8. Pro-rata Rights: [Yes/No] — right to participate in next round
9. Israeli Tax: Subject to Israeli tax withholding on conversion

Important Israeli-specific clauses:
- IIA notification (if company received grants)
- Section 102 interaction (for employee investors)
- Israeli securities law exemptions (private placement)
- Anti-money laundering compliance
```

**Convertible note vs SAFE comparison:**
```
                    SAFE            Convertible Note
Interest rate:      None            5-8% annually
Maturity date:      None            12-24 months
Repayment:          No              Yes (at maturity if no conversion)
Israeli tax:        On conversion   Interest taxed annually
Complexity:         Simple          More complex
Investor protection: Lower          Higher (debt status)
Common in Israel:   Pre-seed/seed   Seed/bridge rounds
```

### Step 5: Option 102 Setup

**Set up employee stock option plan:**

```
Option 102 Capital Gains Track — Setup Steps:

1. Draft ESOP (Employee Stock Option Plan)
   - Hire Israeli employment/tax lawyer
   - Define: pool size, vesting schedule, exercise price, trustee

2. Select ITA-approved trustee
   - Major trustees: Bank Leumi Trust, Bank Hapoalim Trust,
     IBI Trust, Altshuler Shaham
   - Fee: Setup fee + annual per-participant fee

3. File plan with Israel Tax Authority (ITA)
   - Submit plan document to local pakid shuma
   - 30-day objection period (ITA can object or modify)
   - Plan effective after 30 days if no objection

4. Grant options to employees
   - Board resolution for each grant
   - Option agreement signed by employee
   - Trustee notified and manages deposit

5. Vesting and holding period
   - Standard: 4-year vesting, 1-year cliff
   - 24-month holding period from grant date (for capital gains treatment)
   - Shares held by trustee during holding period

6. Exercise and sale
   - Employee exercises options (pays exercise price)
   - After holding period: capital gains tax (25%)
   - Trustee handles withholding and reporting
```

**Option 102 tax comparison:**
```python
def compare_option_102_tracks(grant_value: float, exercise_price: float,
                               sale_price: float):
    """Compare tax outcomes for Option 102 tracks."""
    gain = sale_price - exercise_price
    spread_at_exercise = grant_value - exercise_price  # Not relevant for CG track

    capital_gains_track = {
        "track": "Capital Gains (Trustee)",
        "holding_period": "24 months",
        "tax_rate": 0.25,
        "tax_amount": gain * 0.25,
        "net_to_employee": gain * 0.75,
        "employer_deduction": False,
    }

    income_track = {
        "track": "Income (Trustee)",
        "holding_period": "12 months",
        "tax_rate": 0.50,  # Marginal income tax up to 50%
        "tax_amount": gain * 0.50,
        "net_to_employee": gain * 0.50,
        "employer_deduction": True,
    }

    non_trustee = {
        "track": "Non-Trustee (102)",
        "holding_period": "None",
        "tax_rate": 0.50,
        "tax_amount": gain * 0.50,
        "net_to_employee": gain * 0.50,
        "employer_deduction": True,
    }

    return [capital_gains_track, income_track, non_trustee]
```

### Step 6: R&D Tax Benefits

**Tax benefit eligibility check:**
```
Preferred Enterprise (מפעל מועדף):
- Conditions: 25%+ revenue from exports
- Tax rate: 7.5% (Area A) or 16% (elsewhere)
- Applies to: Industrial or tech companies

Preferred Technological Enterprise (מפעל טכנולוגי מועדף):
- Conditions: Significant R&D activity, IP ownership
- Tax rate: 6% on qualifying IP income (Area A), 12% (elsewhere)
- Additional: Reduced withholding on dividends (4-20%)

R&D Expense Deduction (Section 20a):
- Full deduction of R&D expenses in the year incurred
- Applies to: All R&D conducted in Israel
- No need for IIA approval (separate from grants)

Angel Law (Section 20c):
- Individual investors can deduct up to 5M NIS investment
- Company must be qualifying R&D company
- Investment in first 4 years of company life
- Deduction spread over 3 years
```

## Examples

### Example 1: New Startup Registration
User says: "I want to register a new tech startup in Israel with my co-founder"
Actions:
1. Guide through company name check at ica.justice.gov.il
2. Recommend standard articles with startup-friendly provisions
3. Calculate founder allocation (e.g., 50/50 with 4-year vesting)
4. List post-registration steps (bank, tax, VAT, Bituach Leumi)
Result: Step-by-step registration guide with allocation table.

### Example 2: IIA Grant Application
User says: "We want to apply for Innovation Authority funding for our AI product"
Actions:
1. Assess stage and recommend program (Tnufa for early, R&D Fund for later)
2. Walk through application requirements
3. Highlight IP restrictions and royalty obligations
4. Provide budget template guidance
Result: Program recommendation with application checklist.

### Example 3: ESOP Setup
User says: "I need to set up stock options for my first 5 employees"
Actions:
1. Recommend Option 102 Capital Gains Track
2. Suggest pool size (10-15% of company)
3. Recommend trustee options
4. Outline filing process with ITA
5. Provide standard vesting terms
Result: Complete Option 102 setup plan with trustee comparison.

## Troubleshooting

### Issue: "IIA rejected our application"
Cause: Insufficient technological innovation, weak R&D plan, or budget issues
Solution: Request feedback from IIA reviewer, strengthen innovation component, consider reapplying in next cycle. IIA allows resubmission.

### Issue: "Option 102 holding period not met"
Cause: Employee left or shares sold before 24-month holding period
Solution: Tax difference applies — gains taxed as income (up to 50%) instead of capital gains (25%). Trustee will withhold at higher rate. Plan for this in employment agreements.

### Issue: "Cannot transfer IP abroad"
Cause: IIA-funded IP has transfer restrictions
Solution: Apply to IIA for transfer approval. Be prepared to pay transfer fee (up to 6x grant amount). Consider structuring with Israeli subsidiary retaining IP.
```

**Step 2: Create references**
- `references/iia-programs-guide.md` — Detailed guide to all IIA programs and application process
- `references/option-102-reference.md` — Complete Option 102 tax tracks, trustee list, and filing procedures
- `references/investment-term-sheets.md` — Israeli SAFE and convertible note term sheet templates

**Step 3: Validate and commit**
