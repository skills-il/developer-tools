# Changelog

## 1.4.0 - 2026-08-19

- Added the full employee Bituach Leumi and health tax category table (18 rows)
  in both languages. The skill previously carried only the standard row, so a
  generated payroll sheet over-deducted from under-18 employees and working
  pensioners, who are zero-rated on the employee side.
- Removed the hardcoded per-city arnona constants. They were wrong in value and
  in unit: municipalities publish tariffs per sqm per YEAR, stratified by zone
  and building type, and the script was multiplying a supposed bi-monthly figure
  by six. The tariff is now a user input read from the municipality's tzav
  arnona.
- Corrected the credit-point entitlement: 2.25 for a male resident, 2.75 for a
  female resident.
- Stopped presenting the Section 121B surtax as a 50% tax bracket. The statutory
  ladder ends at 47%; the surtax is 3% on personal-exertion income and 5% on
  capital-source income above 721,560 NIS.
- Added the separate non-exertion bracket table (31/35/47) and the monthly
  bracket grid.
- Corrected the Section 45A ceilings, which had been mapped one row off the Tax
  Authority booklet.
- Replaced the unsourced "Amendment 288" citation with the law the booklet
  actually names, chapter C of the Economic Efficiency Law 2026.
- The invoice and salary templates now emit live formulas. Previously both wrote
  zeros and empty cells while the documentation claimed they computed VAT, the
  deductions and net pay.
- Fixed the Excel currency token to the hex LCID form, corrected the Smart Fill
  naming and menu guidance, labelled the Hebcal geonameid, and removed an
  unsourced Hebrew-sort error-rate statistic.

## 1.3.1 - 2026-08-13

Corrected the National Insurance and health-tax rates and bands embedded in the generated spreadsheet formulas. The skill used pre-2025 employee rates (0.4% / 3.1% / 5%) and 2024 bands (7,122 / 49,030). Current BTL figures are 1.04% / 3.23% / 5.17% on bands of 7,703 and 51,910, effective 01.01.2026. Self-employed reduced rate corrected from 2.87% to 4.47%.

