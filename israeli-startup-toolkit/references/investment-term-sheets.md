# Israeli Investment Terms Reference

This file explains the terms Israeli early-stage instruments turn on so a founder
can negotiate them and brief a lawyer. It deliberately does NOT contain
fill-in-the-blank agreements. Drafting a SAFE, a convertible note, a share
purchase agreement or articles for another person is work reserved to a licensed
Israeli lawyer, and an executable-looking skeleton is the thing most likely to be
signed without one.

## Israeli SAFE (Simple Agreement for Future Equity)

### What to settle before instructing counsel

This is a checklist of the decisions a SAFE turns on, not a document. Drafting the
instrument itself is work for a licensed Israeli lawyer; bring these answers to them.

**Commercial terms to decide**
- Investment amount, and the currency it is denominated in
- Valuation cap, and whether it is pre-money or post-money (they are not
  interchangeable, and the post-money form is now the market default)
- Discount rate, if any, and how it interacts with the cap
- What size of equity financing triggers conversion
- Which conversion basis applies when both a cap and a discount are in play
- Whether the investor gets MFN, pro-rata rights, or information rights

**Israeli-specific questions to raise with counsel**
- Whether the company has IIA grants that require notification
- Which securities-law exemption the round relies on, and the offeree count
  under it (see the securities discussion in SKILL.md)
- Whether tax is withheld on conversion, and on whom the obligation falls
- Anti-money-laundering identification of the investor
- Governing law and forum, and whether the document is executed in Hebrew,
  English, or both

Understanding these lets you negotiate. It does not replace the drafted agreement.

### Israeli SAFE vs Y Combinator SAFE

| Aspect | YC SAFE | Israeli SAFE |
|--------|---------|-------------|
| Governing law | Delaware/California | Israeli law |
| Dispute resolution | US courts/arbitration | Tel Aviv courts |
| Tax treatment | US tax rules | Israeli tax withholding |
| Securities exemption | Reg D | Israeli private placement |
| IIA provisions | N/A | Required if IIA-funded |
| Language | English | Hebrew and/or English |
| Currency | USD | USD or NIS |

## Convertible Note

### What to settle before instructing counsel

A convertible note is a debt instrument. Because it can become repayable, the
consequences of getting it wrong are heavier than for a SAFE, and the drafting is
work for a licensed Israeli lawyer. Decide these points first.

**Commercial terms to decide**
- Principal amount and currency
- Interest rate, and whether interest converts along with principal
- Maturity, and what happens if no qualified financing has occurred by then:
  repayment on demand, automatic conversion, or an extension by agreement
- What counts as a qualified financing for automatic conversion
- Discount and valuation cap, and how they interact
- Whether the note is secured against company assets, and if so which

**Israeli-specific questions to raise with counsel**
- How interest is taxed and withheld year by year, which differs from the SAFE
  treatment where there is no interest at all
- Whether conversion is a taxable event on these facts, and whether an ITA
  ruling is warranted
- The same IIA, securities-exemption and AML questions as for a SAFE

Note the asymmetry worth understanding before you choose: a SAFE has no interest,
no maturity and no repayment obligation, so it cannot put the company into default;
a note can.

## Priced Round (Series A)

### Document Set
1. **Term Sheet** - Non-binding summary of key terms
2. **Share Purchase Agreement (SPA)** - Binding purchase terms
3. **Investors Rights Agreement** - Protective provisions
4. **Articles Amendment** - New share class definition
5. **Shareholders Agreement** - Governance and rights

### Standard Series A Terms (Israeli Market)

```
Investment: [Amount] USD
Pre-money Valuation: [Valuation] USD
Share Class: Series A Preferred
Price Per Share: [Price]

Liquidation Preference:
  - 1x non-participating preferred (standard)
  - Participating preferred (less common, more investor-friendly)

Anti-dilution:
  - Broad-based weighted average (standard)
  - Full ratchet (rare, very investor-friendly)

Board Composition:
  - [2] Founders / Common
  - [1] Series A Investor
  - [1] Independent (mutually agreed)
  - [1] Observer seat (optional)

Protective Provisions (require investor consent):
  - New share class issuance
  - Change of articles
  - M&A / sale of company
  - Increase in option pool
  - Related party transactions
  - Debt above [threshold]

Information Rights:
  - Monthly management report
  - Quarterly financial statements
  - Annual audited financials
  - Annual budget and operating plan

Registration Rights: [Demand / Piggyback]
Right of First Refusal: Company then investors
Co-sale Rights: Tag-along with founders
Drag-along: [Majority percentage] of preferred

Founder Vesting:
  - Reverse vesting on founder shares
  - 4-year schedule, credit for time served
  - Single trigger acceleration: [None / Partial]
  - Double trigger acceleration: [12 months]

ESOP:
  - Expand option pool to [15-20]% post-money
  - Option 102 capital gains track

IIA Provisions:
  - Represent grant obligations
  - Indemnification for IP transfer restrictions
```

## Due Diligence Checklist (Israeli Startup)

```
Corporate:
  - Company registration certificate (Rasham HaChavarot)
  - Current articles of association
  - Shareholder register
  - Board resolutions
  - Cap table (fully diluted)

IP:
  - Patent applications/grants
  - IP assignment agreements from founders/employees
  - IIA grant agreements and IP restrictions
  - Open source usage audit

Financial:
  - Audited/reviewed financial statements
  - Tax returns (corporate, VAT)
  - IIA royalty obligations
  - Outstanding debts and commitments

Employment:
  - Employment agreements
  - Option 102 plan and trustee agreement
  - Pension and severance (Bituach Menahalim)
  - Non-compete/non-solicit agreements

Regulatory:
  - IIA grants and conditions
  - Privacy/data protection compliance
  - Industry-specific licenses
  - International sanctions compliance
```
