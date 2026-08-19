---
name: israeli-startup-toolkit
description: Not legal advice and not tax advice. Guide Israeli startup operations including company formation, Innovation Authority grants, investment agreements, R&D tax benefits, and employee stock options (Option 102). Use when user asks about starting a company in Israel, IIA grants, "Innovation Authority", SAFE agreements (Israeli), convertible notes, Option 102, employee stock options in Israel, R&D tax benefits, preferred enterprise, Yozma 2.0, Delaware flip, or Israeli startup legal/financial setup. Do NOT use for non-Israeli company formation or international tax advice. Always recommend consulting with Israeli lawyer and accountant for binding decisions.
license: MIT
allowed-tools: Bash(python:*) WebFetch
compatibility: No API keys required. Network access helpful for IIA portal reference. Always consult licensed Israeli professionals for legal/tax decisions.
---

# Israeli Startup Toolkit

## Legal notice

Not legal advice and not tax advice. This skill explains how Israeli company
formation, Innovation Authority grants, investment instruments, Section 102
plans and the Encouragement of Capital Investments Law work. It does not
practise law and it does not represent you before any authority.

Any wording this skill drafts, whether a SAFE, a convertible note, articles of
association or an ESOP plan, is an automatic draft for your own preparation
only. It is not a document prepared by a lawyer and it may not be relied on as
evidence. Before signing anything, filing with the Companies Registrar, the
Israel Tax Authority, the Israel Innovation Authority or a court, consult a
licensed Israeli lawyer.

Any tax figure it produces is an estimate. Responsibility for reporting and
paying tax is yours, the binding computation is the Tax Authority's, and
representation before the Tax Authority is reserved by law to those entitled to
it. Consult a licensed Israeli accountant or tax adviser before acting.

## Description

Help Israeli founders execute the legal, tax, and funding mechanics of building a startup in 2026: registering a חברה בע"מ at the Israeli Corporations Authority (Rasham HaChevarot), choosing an Israel Innovation Authority program (Tnufa, R&D Fund, incubator, BIRD, Horizon Europe, Yozma 2.0), structuring SAFE or convertible-note rounds under Israeli law, setting up a Section 102 trustee plan, applying for Preferred Technological Enterprise status, and deciding whether to do a Delaware Flip.

Use when the user asks about any of these mechanics. Do NOT use for non-Israeli company formation, US tax advice, or cap-table modeling of public-company stock; route those elsewhere. For deep coverage of Section 102 employee tax (the employee side), prefer `israeli-stock-options-tax`. Always recommend a licensed Israeli lawyer and רואה חשבון before binding decisions; this skill produces drafts and checklists, not legal opinions.

## Instructions

**IMPORTANT DISCLAIMER:** This skill provides general guidance only. Israeli corporate law, tax law, and securities regulation are complex and change frequently (the 2025 Arrangements Law and OECD Pillar Two QDMTT both took effect for tax years starting after 31 December 2025). Always consult with a licensed Israeli lawyer and accountant before binding decisions.

### Step 1: Identify Startup Stage

| Stage | Typical Needs | Key Actions |
|-------|--------------|-------------|
| Idea / Pre-seed | Company formation, initial funding | Register Ltd, apply to Tnufa |
| Seed | First investment, team building | SAFE/convertible note, Option 102 plan |
| Series A | Growth funding, scaling | Priced round, Preferred Technological Enterprise status |
| Growth | Expansion, international | IP regime, binational grants, Delaware Flip decision |

### Step 2: Company Formation

**Register an Israeli Ltd (חברה בע"מ):**

```
Step-by-step registration:

1. Choose company name
   - Check availability: ica.justice.gov.il
   - Must be unique, Hebrew or English
   - Suffix: בע"מ (Ltd)

2. Prepare Articles of Association (takanon)
   - Standard template available from Companies Registrar
   - Customize: share classes, board composition, transfer restrictions
   - Recommended: Use lawyer-drafted articles for startups

3. Appoint initial directors
   - Minimum: 1 director
   - Israeli residency not required (but practical for banking)
   - Director ID (teudat zehut) or passport for foreign directors

4. Register online
   - Portal: ica.justice.gov.il
   - Registration fee (2026 tariff, one-time): NIS 2,559 online (reduced), NIS 3,123 otherwise, NIS 893 for a chevra le-toelet ha-tzibur (chalatz)
   - Annual fee: NIS 1,338 if paid by 31 March 2026, NIS 1,777 from 1 April 2026
   - First-year exemption: no annual fee in the calendar year of registration
   - Timeline: 3-7 business days
   - Documents: Articles, director appointments, registered address

5. Post-registration
   - Open corporate bank account (Bank Leumi, Hapoalim, Discount, Mizrahi-Tefahot)
     Digital options: Pepper Business (Leumi), One Zero
   - Register for tax at local tax office (pakid shuma)
   - Register for VAT if expected revenue exceeds threshold
     - Osek Patur ceiling 2026: NIS 122,833 (most tech companies skip straight to Osek Murshe / Chevra)
     - Standard VAT rate as of 2026: 18% (raised from 17% on 1 January 2025)
   - Register for National Insurance (Bituach Leumi) as employer
```

**Founder share allocation example:**
```python
def calculate_founder_allocation(founders, vesting_months=48, cliff_months=12):
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

**IIA program selection (2026):**

| Program | Stage | Funding | Max Amount | Repayment |
|---------|-------|---------|------------|-----------|
| Tnufa (Ideation) | Pre-seed | Up to 80% | Up to NIS 200,000 over 12 months (NIS 250K budget cap) | Royalties 3-5% |
| Startup Fund | Pre-seed / seed | Up to 50% (up to 75% periphery) | Per budget, typical NIS 2-5M | Royalties 3-5% |
| R&D Fund | Seed-Growth | Up to 50% (up to 75% periphery) | Per budget | Royalties 3-5% |
| Technological Venture Incubator | Early stage | Up to 85% | Up to ~NIS 9M over 2 years | Royalties + incubator equity |
| BIRD General (US-Israel) | Any | Up to 50% | USD 1.5M | Royalties if reach sales |
| BIRD HLS (Homeland Security) | Any | Up to 50% | USD 1M | Royalties if reach sales |
| Horizon Europe | Any | Varies | Varies | Depends on track |
| Yozma 2.0 (fund-of-funds) | Seed-Series A | Co-investment with institutional LPs | Varies (USD 700M first round, 2024) | Equity, not a startup grant |
| Magnet / Magneton / Nofar | Academic-industry | Varies | Varies | Royalties / non-repayable for academic side |

Yozma 2.0 is an LP-side government commitment that backs Israeli VC funds at a roughly 0.3:1 government:institutional ratio; founders do not apply directly. The 2024 government stimulus also created a Revolutionary Startup Fund that co-invests with private investors in pre-seed, seed, and Series A rounds.

**Grant application checklist:**
```
IIA R&D Fund Application:

- Company registered in Israel
- R&D conducted primarily in Israel
- IP owned by the company (not founders personally)
- Technological innovation (not just business model)
- Detailed R&D plan (12-24 months)
- Budget breakdown (salaries, subcontractors, materials, equipment)
- Team qualifications (CVs of key R&D personnel)
- Market analysis and business potential
- No parallel funding for same R&D from other government sources
- Commitment to report progress and financials

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

**Israeli SAFE template structure (Y Combinator post-money SAFE is the de-facto norm in Israel; Israeli law applies via choice-of-law clause):**
```
Israeli SAFE Key Terms:

1. Investment Amount: [Amount] NIS or USD
2. Valuation Cap: [Cap] (post-money standard, pre-money still seen in older templates)
   Typical 2026 caps: USD 3-8M pre-seed, USD 8-20M seed
3. Discount Rate: 15-25% typical (20% common)
4. Governing Law: Laws of the State of Israel (or Delaware if flipped)
5. Dispute Resolution: Tel Aviv courts / arbitration
6. Conversion Trigger: Equity Financing of at least [Amount]
7. MFN Clause: [Yes/No] Most Favored Nation
8. Pro-rata Rights: [Yes/No] right to participate in next round
9. Israeli Tax: Subject to Israeli tax withholding on conversion

Important Israeli-specific clauses:
- IIA notification (if company received grants)
- Section 102 interaction (for employee investors)
- Israeli securities law exemptions (private placement, max 35 offerees in 12 months)
- Anti-money laundering compliance (Hok Issur Halbanat Hon)
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
Option 102 Capital Gains Track Setup Steps:

1. Draft ESOP (Employee Stock Option Plan)
   - Hire Israeli employment/tax lawyer
   - Define: pool size, vesting schedule, exercise price, trustee

2. Select ITA-approved trustee
   - Major trustees: Bank Leumi Trust, Bank Hapoalim Trust, ESOP Excellence,
     IBI Trust, Altshuler Shaham Trust
   - Fee: Setup fee + annual per-participant fee

3. File plan with Israel Tax Authority (ITA)
   - Submit plan document to local pakid shuma
   - The notice must be filed at least 30 days BEFORE the grant date
   - The plan and the trustee are deemed approved if the assessing officer
     does not reply within 90 days of receiving the notice

4. Grant options to employees
   - Board resolution for each grant
   - Option agreement signed by employee
   - Trustee notified and manages deposit

5. Vesting and holding period
   - Standard: 4-year vesting, 1-year cliff
   - 24-month holding period running from the date the shares were allotted
     and deposited with the trustee (Section 102(a), definition of "tom
     ha-tkufa"). It is NOT measured from the end of the tax year of grant,
     which was the pre-2003 rule.
   - Income track: 12 months from the same date
   - Shares held by trustee during holding period

6. Exercise and sale
   - Employee exercises options (pays exercise price)
   - After holding period: capital gains tax 25% flat
     (+ 3% surtax under Section 121B(a) above NIS 721,560 of taxable income,
      + a further 2% under Section 121B(a1) on capital-source income above the
      same threshold, so up to 30% effective on a large exit)
     (a controlling shareholder cannot use Section 102 at all, see below)
   - Trustee handles withholding and reporting
```

**Option 102 tax comparison:**
```python
def compare_option_102_tracks(grant_value, exercise_price, sale_price,
                              high_earner=False):
    """Compare tax outcomes for Option 102 tracks (2026 rates)."""
    gain = sale_price - exercise_price
    # Sec. 121B(a) adds 3% and Sec. 121B(a1) adds a further 2% on
    # capital-source income above NIS 721,560 (2024-2027 threshold).
    surtax = 0.05 if high_earner else 0.0

    capital_gains_track = {
        "track": "Capital Gains (Trustee)",
        "holding_period": "24 months from allotment and deposit with trustee",
        "tax_rate": 0.25 + surtax,
        "tax_amount": gain * (0.25 + surtax),
        "net_to_employee": gain * (0.75 - surtax),
        "employer_deduction": False,
    }

    income_track = {
        "track": "Income (Trustee)",
        "holding_period": "12 months from allotment and deposit with trustee",
        "tax_rate": 0.50,
        "tax_amount": gain * 0.50,
        "net_to_employee": gain * 0.50,
        "employer_deduction": True,
    }

    # A controlling shareholder (Sec. 32(9)) is excluded from Sec. 102 entirely;
    # a "material shareholder" selling outside 102 pays 30% under Sec. 91(b)(2).
    non_trustee = {
        "track": "Non-Trustee 102 (3(i) for non-employees)",
        "holding_period": "None",
        "tax_rate": 0.50,
        "tax_amount": gain * 0.50,
        "net_to_employee": gain * 0.50,
        "employer_deduction": True,
    }

    return [capital_gains_track, income_track, non_trustee]
```

### Step 6: R&D Tax Benefits

**Tax benefit eligibility check (2026):**
```
Preferred Enterprise (Mafal Mutaaf):
- Condition: "competitive enterprise" test in Section 18A(c) of the
  Encouragement of Capital Investments Law. For industry this is a
  market-concentration test, not a flat export floor: no more than 75% of
  income from any one market, or at least 25% of income from sales into a
  single foreign market of 14 million residents or more.
- Tax rate: 7.5% (Area A / Negev / Galilee) or 16% (elsewhere)
- Applies to: Industrial or tech companies

Preferred Technological Enterprise (PTE / Mafal Tehnologi Mutaaf):
Section 51X of the Encouragement of Capital Investments Law. Conditions (1)
AND (2) must both hold (or, alternatively, condition (3)), plus (4) and (5):
  1. R&D expenses averaged >= 7% of the company's revenue over the 3 prior
     years, OR exceeded NIS 75M per year
  2. AND at least one of: 20%+ of employees are R&D employees (or 200+ such
     employees); a venture capital fund invested at least NIS 8M; revenue grew
     25%+ on average over 3 years with turnover >= NIS 10M in each; headcount
     grew 25%+ on average over 3 years with at least 50 employees in each
  3. (alternative) the Chief Scientist certified the enterprise as
     innovation-promoting and the Innovation Authority approved it
  4. Group revenue in the tax year below NIS 10 billion
  5. The enterprise meets the Section 18A(c) competitive-enterprise test
- Tax rate: 12% on preferred technological income (7.5% in Area A)
- "Preferred technological income" is the PORTION of technological income
  arising from R&D performed in Israel, computed as a nexus ratio under the
  2017 regulations. There is no "20% of revenue from Israeli IP" threshold.
- Reduced withholding on dividends (4-20%)

Special Preferred Technological Enterprise (SPTE):
- For very large groups (consolidated revenue > NIS 10 billion)
- Tax rate: 6% on qualifying IP income (nexus approach)

R&D Expense Deduction (Section 20a):
- Full deduction of R&D expenses in the year incurred
- Applies to: All R&D conducted in Israel
- No need for IIA approval (separate from grants)

Angels benefit (Encouragement of Knowledge-Intensive Industry Law
(Temporary Order), 2023, NOT Section 20c of the Ordinance):
- Section 2: a TAX CREDIT (zikui), not a deduction, for a cash investment in
  the shares of a qualifying R&D company. Maximum qualifying investment
  NIS 4 million, reduced by the investor's and relatives' other investments in
  the same company. The credit equals the qualifying investment multiplied by
  the capital gains rate the investor would have paid on a sale.
- The three-year period is the BENEFIT period (from the start of the tax year
  of the investment), not a schedule for spreading the deduction. There is no
  "first 4 years of company life" test; the R&D-company tests are financial.
- Section 3: a separate rollover DEDUCTION for reinvesting an exit gain,
  capped at NIS 5.5 million per investment.
- TEMPORARY ORDER: in force 31.7.2023 to 31.12.2026. Confirm it has been
  extended before relying on it for an investment made after that date.

OECD Pillar Two QDMTT (effective tax years from 1 Jan 2026):
- Multinational groups with global revenue >= EUR 750M
- Top-up tax if effective Israeli rate < 15%
- PTE companies may need to model exposure
```

### Step 7: Delaware Flip Decision

By 2025 roughly 45% of newly-formed Israeli tech startups incorporated abroad first (Delaware C-Corp parent + Israeli R&D subsidiary), up from ~20% in 2022. The driver is the US VC ecosystem, not Israeli law.

```
Delaware Flip Decision Checklist:

Strong reasons to flip (or start as Delaware parent):
- Plan to raise from US-only VCs (most Tier-1 funds prefer C-Corp)
- US-based founding team or US-first GTM
- M&A by US acquirer is the likely exit
- Plan to issue US-style stock options to US employees

Reasons to stay Israeli-only:
- Plan to claim Preferred Technological Enterprise (12% / 7.5%)
- Plan to take IIA grants (transfer-abroad approval and 6x penalty risk)
- Israeli investors prefer Israeli entity
- Small / bootstrapped, no foreign capital plan

Flip cost: USD 25K-75K legal + tax pre-ruling, 2-4 months timeline.
Tax pre-ruling (mas mukdam) from ITA recommended to avoid deemed exit tax.
IIA approval required if any IIA grants received before the flip.
```

## Examples

### Example 1: New Startup Registration
User says: "I want to register a new tech startup in Israel with my co-founder"
Actions:
1. Guide through company name check at ica.justice.gov.il
2. Recommend standard articles with startup-friendly provisions
3. Calculate founder allocation (e.g., 50/50 with 4-year vesting)
4. List post-registration steps (bank, tax, VAT at 18%, Bituach Leumi)
5. Quote the fees: NIS 2,559 online registration (NIS 3,123 otherwise) one-time, then the NIS 1,338 / NIS 1,777 annual fee split with no annual fee in the year of registration
Result: Step-by-step registration guide with allocation table.

### Example 2: IIA Grant Application
User says: "We want to apply for Innovation Authority funding for our AI product"
Actions:
1. Assess stage and recommend program (Tnufa up to NIS 200K for early, R&D Fund or Startup Fund for later)
2. Walk through application requirements
3. Highlight IP restrictions and royalty obligations (3-5%)
4. Provide budget template guidance
5. Note that grant acceptance constrains a future Delaware Flip
Result: Program recommendation with application checklist.

### Example 3: ESOP Setup
User says: "I need to set up stock options for my first 5 employees"
Actions:
1. Recommend Option 102 Capital Gains Track
2. Suggest pool size (10-15% of company)
3. Recommend trustee options (Bank Leumi Trust, ESOP Excellence, IBI, Altshuler Shaham)
4. Outline filing process with ITA (notice at least 30 days before grant, deemed approved if no reply within 90 days)
5. Provide standard vesting terms (4y / 1y cliff)
6. Explicitly state the holding period is 24 months from allotment and deposit with the trustee, and that a 10%+ founder cannot be in the plan at all
Result: Complete Option 102 setup plan with trustee comparison.

### Example 4: Delaware Flip
User says: "We want to raise from a US VC, should we flip to Delaware?"
Actions:
1. Map fund preferences and exit path
2. Run flip decision checklist (Step 7)
3. Flag IIA grant constraint and transfer-abroad approval
4. Recommend pre-ruling from ITA (mas mukdam) before executing
5. Quote rough cost (USD 25K-75K) and timeline (2-4 months)
Result: Flip decision memo with checklist and next steps.

## Bundled Resources

### References
- `references/iia-programs-guide.md`: Detailed guide to Israel Innovation Authority grant programs including R&D Fund, Tnufa (early stage), Startup Fund, Technological Venture Incubators, BIRD (US-Israel binational), Horizon Europe, and Yozma 2.0 fund-of-funds. Covers funding percentages, maximum amounts, repayment terms, eligibility requirements, application process, and approval rates. Consult when helping users select the right IIA program or prepare grant applications.
- `references/investment-term-sheets.md`: Israeli investment agreement templates including post-money SAFE and convertible note structures with Israeli-specific clauses (IIA notification, Section 102 interaction, Israeli securities law private-placement exemptions, anti-money laundering). Typical 2026 cap/discount ranges. Consult when drafting or reviewing early-stage investment terms under Israeli law.
- `references/option-102-reference.md`: Complete reference for Section 102 of the Israeli Income Tax Ordinance covering all three tracks (Capital Gains Trustee, Income Trustee, Non-Trustee / 3(i)), holding periods (24 months from allotment and deposit with the trustee for capital gains), tax rates (25%, plus 3% under Section 121B(a) and a further 2% under Section 121B(a1) on capital-source income for high earners), employer deduction rules, ITA-approved trustees, filing procedures, and common pitfalls. Consult when setting up an ESOP or advising on employee equity compensation tax implications.

## Gotchas

- Israeli startups register as "Chevra Baam" (Ltd) at the Israeli Corporations Authority (Rasham HaChevarot), not at a US Secretary of State. Foreign-trained agents may describe US incorporation processes.
- Tnufa is capped at NIS 200,000 over 12 months (80% of a NIS 250K budget), NOT 1 million NIS. Skills or articles citing 1M NIS are stale.
- The Section 102 capital-gains holding period is 24 months from the date the shares were allotted and deposited with the trustee, per the definition of "tom ha-tkufa" in Section 102(a). It is NOT measured from the end of the tax year of grant; that was the pre-2003 regime and is still widely repeated in older guides.
- IIA-funded IP must stay in Israel; transfer abroad requires approval and a fee of up to 6x the grant received. This constrains the Delaware Flip and many M&A deals.
- Israeli VAT rose to 18% on 1 January 2025 (from 17%). Pricing pages, invoices, and accounting templates copied from older sources are stale.
- Closely-held companies (chevrat me'atim, 5 or fewer shareholders) pay a 2% annual surcharge on undistributed excess profits under Section 81B, added by Amendment 277 and applying from tax year 2025. It is paid BY THE COMPANY at 2%, not allocated to shareholders at marginal rates. It does not apply in a year where losses exceed 10% of opening accumulated profits, or where dividends distributed exceed 50% of excess profits, or where dividends are 6% or more of opening accumulated profits. A separate rule (Section 62A(a1)) does attribute income to an active shareholder at marginal rates, but it is gated on a profitability test, not on non-distribution.
- Israeli tax year runs January to December (like the US), but corporate filing deadlines differ. Standard corporate tax rate is 23%. PTE rate is 12% (7.5% in Area A), NOT 16%; SPTE is 6%. Older skills citing 7.5% / 16% are using the older Preferred Enterprise tiers, not the PTE tech-specific rates.
- A controlling shareholder cannot participate in a Section 102 plan at all. The definition of "employee" in Section 102(a) expressly excludes a controlling shareholder, and trustee allotment requires that the employee is not one at grant or as a result of it. Founders holding 10%+ are outside 102; a material shareholder selling securities is taxed at 30% under Section 91(b)(2), which is a different provision entirely.
- The surtax on a Section 102 exit is not 3%. Section 121B(a) adds 3% above NIS 721,560 of taxable income, and Section 121B(a1) adds a FURTHER 2% on capital-source income above the same threshold, so a large capital-track gain is taxed at up to 30%.
- Israeli startups that flip to Delaware typically incorporate Delaware C-Corp as parent with the Israeli entity as a subsidiary, not the reverse. Agents may suggest the opposite.
- The Companies Registrar annual fee has a calendar-quarter cliff: NIS 1,338 if paid by 31 March 2026, NIS 1,777 from 1 April 2026. Pay in Q1 to save NIS 439.

## Recommended MCP Servers

- `israel-tax-authority-mcp` (if available): query ITA forms, pre-ruling status, Section 102 trustee lists.
- `israel-corporations-authority-mcp` (if available): company name availability, registration status, annual fee status.

If these MCPs are not installed, fall back to the official portals listed in Reference Links.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Israel Innovation Authority | https://innovationisrael.org.il/en | Grants, R&D programs, eligibility criteria |
| Israeli Tax Authority | https://www.gov.il/en/departments/israel_tax_authority | Option 102, R&D tax benefits, corporate tax |
| ICA Companies Registrar | https://www.gov.il/en/departments/israeli_corporations_authority | Company formation, annual filings, fees |
| Ministry of Justice | https://www.gov.il/en/departments/ministry_of_justice | Corporate law, IP registration |
| Start-Up Nation Central | https://www.startupnationcentral.org | Ecosystem data, funding trends, Finder DB |
| Israel Securities Authority | https://www.isa.gov.il/en | Securities law, private placement exemptions |
| Calcalist Tech | https://www.calcalistech.com | Funding rounds, exits, ecosystem news (EN) |
| Geektime | https://www.geektime.co.il | Israeli tech news (EN), startup launches |
| Globes (Tech) | https://en.globes.co.il/en/startups.tag | Funding and exit reporting (EN) |
| BIRD Foundation | https://www.birdf.com | US-Israel binational R&D grants |

## Israeli Ecosystem Context (2024-2026)

After the October 2023 war, Israeli startup funding contracted in late 2023 then partially rebounded through 2024-2025, with cyber, AI infrastructure, and defense tech absorbing most growth-stage capital. Key data points:

- **Funding volume**: 2024 raised roughly USD 12B across ~600 rounds per Start-Up Nation Central; 2025 H1 trended ahead of 2024 driven by AI and cyber megadeals.
- **Government stimulus**: The 2024 high-tech stimulus injected roughly USD 1B into the ecosystem over 2024-2026, including the Yozma 2.0 fund-of-funds (0.3:1 government:institutional ratio, USD 700M first round in Q3 2024) and a new Revolutionary Startup Fund co-investing in pre-seed / seed / Series A.
- **Active local VCs**: Pitango (multi-stage, ~USD 2B AUM), Aleph (Series A/B), 83North (Series A/B), Vertex Ventures Israel (early growth), Vintage Investment Partners (Vintage X closed at USD 400M+ in 2024, secondaries plus fund-of-funds), OurCrowd (online platform plus partner funds), Viola Group, Jerusalem Venture Partners (JVP), TLV Partners, Glilot Capital (cyber), Team8 (cyber/AI foundry), Insight Partners (heavy IL deployment), Amiti Ventures (early stage).
- **Accelerators / programs**: MassChallenge Israel (zero-equity, Jerusalem), OurCrowd Pitch (pitch competition plus syndicate), 8200 EISP (alumni-driven), Microsoft for Startups Israel, Google for Startups TLV. Bizzabo is an Israeli scale-up, not an accelerator; correct any agent that says otherwise.
- **Recent exits / IPOs**: Mobileye (NASDAQ 2022), Wix (NASDAQ 2013), Lemonade (NYSE 2020), Riskified (NYSE 2021), monday.com (NASDAQ 2021); 2024-2025 saw renewed M&A (Wiz reportedly in advanced talks with Google for ~USD 23B in 2024, status confirmed in 2025) and several mid-cap cyber acquisitions.
- **Delaware Flip trend**: Roughly 45% of new Israeli tech startups incorporated abroad in 2025 (up from ~20% in 2022), almost always Delaware C-Corp parent with Israeli R&D subsidiary. Driver is US VC preference, not Israeli law.
- **Tax landscape**: Corporate tax 23% (unchanged through 2026). VAT 18% (raised from 17% in January 2025). PTE rate 12% (7.5% Area A); SPTE 6%. Section 102 capital-gains rate 25%, plus 3% (Section 121B(a)) and a further 2% (Section 121B(a1)) on capital-source income above NIS 721,560. OECD Pillar Two QDMTT applies for tax years starting after 31 December 2025. Closely-held companies pay a 2% company-level surcharge on undistributed excess profits under Section 81B from tax year 2025. Always verify current rates with the ITA before quoting.

## Troubleshooting

### Issue: "IIA rejected our application"
Cause: Insufficient technological innovation, weak R&D plan, or budget issues.
Solution: Request feedback from IIA reviewer, strengthen innovation component, consider reapplying in next cycle. IIA allows resubmission.

### Issue: "Option 102 holding period not met"
Cause: Employee left or shares sold before 24 months from the date of allotment and deposit with the trustee.
Solution: Tax difference applies. Gain taxed as employment income (up to 50%) instead of capital gains (25%). Trustee withholds at the higher rate. Plan for this in employment agreements and grant timing.

### Issue: "Cannot transfer IP abroad"
Cause: IIA-funded IP has transfer restrictions.
Solution: Apply to IIA for transfer approval. Be prepared to pay transfer fee (up to 6x grant amount). Consider structuring with an Israeli subsidiary retaining IP, or negotiate the transfer as part of an M&A deal.

### Issue: "Delaware Flip and IIA grants conflict"
Cause: Flipping to a US parent triggers IIA review of any funded IP.
Solution: Get IIA written approval and an ITA pre-ruling (mas mukdam) before executing the flip. Budget the transfer fee. Some founders choose to repay outstanding royalties early to simplify approval.
