# Israeli Tax Rates and Financial Constants (2026)

> **Note:** The 10%, 14%, 35% and 47% bracket thresholds were carried forward from 2025 (no inflation indexation, frozen for 2025-2027). The 20% and 31% brackets were widened by chapter C of the Economic Efficiency Law 2026 (published 31.3.2026), effective for income derived on or after 1 January 2026. The credit point value, Bituach Leumi, health tax, and pension rates were kept at their 2025 levels for 2026. The minimum wage rose on 1 April 2026 and is updated accordingly. Always re-verify against the Tax Authority and Bituach Leumi before relying on these in a calculation.

## Income Tax Brackets (2026, after the bracket widening)
| Annual Income (NIS) | Marginal Rate | Notes |
|---------------------|---------------|-------|
| Up to 84,120 | 10% | Unchanged from 2025 |
| 84,121 - 120,720 | 14% | Unchanged from 2025 |
| 120,721 - 228,000 | 20% | Widened in 2026 (was up to 193,800) |
| 228,001 - 301,200 | 31% | Widened in 2026 (was 193,801-269,280) |
| 301,201 - 560,280 | 35% | Floor raised in 2026 (was 269,281-560,280) |
| Above 560,280 | 47% | Top statutory bracket. The official table ends here. |

The often-quoted "50% above 721,560" is not a bracket. Section 121B(a) adds a 3% surtax on taxable income above 721,560 NIS (60,130 NIS/month), giving 50% effective on personal-exertion income. Section 121B(a1) adds a FURTHER 2% on capital-source income above the same threshold, so investment income carries 5% of surtax, not 3%. The threshold is frozen for 2025-2027.

The 2026 bracket widening expanded the middle brackets (20%, 31%, 35%), reducing the tax owed by a middle-income taxpayer relative to the pre-widening schedule. The top statutory rate (47%), the surtax and the Bituach Leumi rates were not affected.

## Income Tax Brackets, non-exertion income (2026)

The ladder above is for personal-exertion income (yegia ishit). The Tax
Authority publishes a SEPARATE table for income that is not from personal
exertion (rent, investment, most passive income). It has no 10% / 14% / 20%
bands at all:

| Annual Income (NIS) | Monthly (NIS) | Marginal Rate |
|---|---|---|
| Up to 301,200 | Up to 25,100 | 31% |
| 301,201 - 560,280 | 25,101 - 46,690 | 35% |
| Above 560,280 | Above 46,690 | 47% |

Applying the personal-exertion ladder to rental or investment income understates
the tax substantially. Note also that capital-source income above 721,560 NIS
carries 5% of surtax (3% + 2%), not 3%.

## Monthly and daily bracket grids

A payslip withholds monthly against the monthly grid and reconciles
cumulatively over the year. The 2026 monthly personal-exertion thresholds are
7,010 / 10,060 / 19,000 / 25,100 / 46,690, and the credit point is 242 NIS per
month. A sheet that only divides an annual result by 12 will be wrong for anyone
with a bonus month or a mid-year start.

## Tax Credit Points (Nekudot Zikui)
- Value per point: 2,904 NIS/year (242 NIS/month)
- Israeli resident: 2.25 points (male)
- Woman: +0.5 points, so a female Israeli resident is entitled to 2.75 points in total
- Combat reserve (miluim) service: Amendment 283, published 23.11.2025, added Section 39B to the Ordinance granting credit points for combat reserve service. Check the Tax Authority guidance for the current entitlement before applying it to a payslip.
- New immigrant (year 1-1.5): +3 points
- New immigrant (year 1.5-2): +2 points
- New immigrant (year 2-3.5): +1 point

## National Insurance (Bituach Leumi), bands effective 01.01.2026
The employee rates below are for the STANDARD category only: an Israeli resident
aged 18 to retirement age. The official table breaks the employee share down by category and
several are zero-rated. See the full table in SKILL.md Step 2.5 before using
these in a payroll calculation.

| Income Range | Employee Rate (standard category) | Self-Employed Rate |
|-------------|--------------|-------------------|
| Up to 7,703 NIS/month | 1.04% | 4.47% |
| 7,704 - 51,910 NIS/month | 7.00% | 12.83% |

Employer rates for the standard category are 4.51% on the reduced band and 7.6%
on the full band. Income above 51,910 NIS/month is not insurable.

## Health Tax (Mas Briut), bands effective 01.01.2026
Standard category (resident aged 18 to retirement age):

| Income Range | Rate |
|-------------|------|
| Up to 7,703 NIS/month | 3.23% |
| 7,704 - 51,910 NIS/month | 5.17% |

Combined employee total for this category is 4.27% on the reduced band and 12.17% on the full band.

## VAT (Ma'am)
- Standard rate: 18% (raised from 17% on 2025-01-01). The Finance Ministry floated a rise to 19%, but it was not enacted and the 2026 state budget contains no such increase.
- Eilat: 0% (tax-free zone)

### VAT formula cheat sheet
- Net to gross: `gross = net * 1.18`
- Gross to net: `net = gross / 1.18`
- VAT amount inside a VAT-inclusive price: `vat = gross - gross / 1.18` (equivalently `gross * 0.18 / 1.18`)
- VAT amount on a VAT-exclusive price: `vat = net * 0.18`

## Pension Contributions (2025-2026, frozen at 2025 levels)
| Component | Employee | Employer |
|-----------|----------|----------|
| Pension savings | 6.0% | 6.5% |
| Severance fund | - | 6.0% |
| Disability insurance | - | up to 0.5%, carved out of the employer's 6.5% tagmulim, not added on top |

### Section 45a Tax Credit on Pension Contributions
Employees and self-employed who contribute to a recognized pension fund are entitled to a 35% tax credit on qualifying pension contributions under Section 45a of the Income Tax Ordinance. The credit is computed on the employee-side deposit (and the self-employed deposit for the self-employed), subject to annual ceilings set by the Tax Authority. The 2026 ceilings from the
Tax Authority's monthly deductions booklet (chapter C, table B) are:
Section 45A(d) 189 NIS/month; Section 45A(e)(1) 189 NIS/month;
Section 45A(e)(2) 19,400 NIS/month. Do not confuse these with the 9,700
NIS/month figure on the adjacent row, which is the qualifying-income ceiling
for a self-employed member under Section 47(a), not a 45A ceiling. The 2026
average wage (which caps the mandatory-pension base) is 13,769 NIS. A tlush maskoret (salary slip) spreadsheet that shows "income tax" without subtracting the 45a credit will overstate the actual tax withheld.

## Keren Hishtalmut (Education Fund)
| | Employee | Employer |
|--|----------|----------|
| Salaried | 2.5% | 7.5% |
| Self-employed | Up to 4.5% of income | - |
- Tax-exempt after 6 years (up to ceiling)
- Ceiling: 15,712 NIS/month (2025 level, carried into 2026)

## Minimum Wage (from 1 April 2026)
- Monthly: 6,443.85 NIS from 2026-04-01, up from 6,247.67 NIS
- Hourly: ~35.40 NIS (based on a 182-hour full-time month)
- Before 1 April 2026 the monthly minimum was 6,247.67 NIS. The 5,880.02 NIS/month rate dates from 1 April 2024 and is no longer current.

## Arnona (municipal property tax)

There is no national arnona rate and no single rate per city. Each local
authority publishes a `צו הארנונה` for the tax year with tariffs stated **per
sqm per YEAR**, stratified by zone, by building type and by area band. Tel
Aviv's 2026 residential order, for example, has five zones times six building
types, with tariffs from 46.64 to 139.60 NIS per sqm per year.

Never hardcode a per-city scalar into a worksheet. Read the tariff for the
specific property out of that authority's order and treat it as an input. The
bi-monthly instalment is the annual charge divided by six.
