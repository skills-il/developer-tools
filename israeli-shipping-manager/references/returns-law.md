# Israeli Distance-Selling Returns: The Statutory Detail

This file carries the full text-level detail behind Step 6 of SKILL.md. The skill body has the
operational rules; this file has the section numbers, the exact conditions, and the traps.

All references are to **חוק הגנת הצרכן, התשמ"א-1981** unless stated otherwise.

## Two parallel regimes, not one

| | Distance sale (section 14ג) | Voluntary return (section 14ו + the 2010 regulations) |
|---|---|---|
| Instrument | חוק הגנת הצרכן 14ג / 14ג1 / 14ה / 14ט | תקנות הגנת הצרכן (ביטול עסקה), התשע"א-2010 |
| Window for goods | 14 days from receipt of the goods **or** the disclosure document, whichever is later | Also 14 days from receipt for the main goods case |
| Condition of goods | Not a precondition of the right | Must be unused and undamaged, and physically returned |
| Exclusions | Closed list of five in 14ג(ד) | A much longer list, including undergarments and assembled furniture |
| Notice rules | Section 14ט applies | Section 14ט(ז) expressly disapplies 14ט |

They are **parallel**, not mutually exclusive. The 2010 regulations do not switch off when a sale is
remote; they are simply less generous, which is why a distance buyer relies on 14ג. Code them
separately, because the exclusion lists differ.

## The exclusions actually differ, and this is where sellers get it wrong

Section 14ג(ד) excludes exactly five things from a distance sale:

1. Perishable goods (טובין פסידים)
2. Hospitality, travel, leisure or entertainment services, where cancellation falls within 7
   non-rest days before the service is due
3. Information as defined in חוק המחשבים, התשנ"ה-1995
4. Goods manufactured specially for the buyer as a result of the transaction
5. Recordable or reproducible goods whose original packaging the buyer opened

Closed as the statute stands, but 14ג(ה) lets the Minister add categories by order, and 14ג2 carves
out tourism services performed wholly abroad.

**Undergarments (including swimwear) and furniture assembled in the buyer's home are NOT on this
list.** They are exclusions in the 2010 regulations, which govern the other regime. A seller who
refuses an online swimwear cancellation on that basis is acting unlawfully.

## Section 14ט: the notice intake, in full

This is the provision most relevant to anyone actually building an RMA feature, because it dictates
UI and queue behaviour rather than policy.

- **14ט(א)** the seller must allow a cancellation notice through each of: (1) orally, by phone or in
  person at the place of business, except where the law requires written notice; (2) registered
  mail; (3) email; (4) fax, if the seller has one; (5) the internet, for a transaction that can be
  contracted by that means; (6) any other means the Minister prescribes. The seller must honour the
  contact details it published under 14ט(ד) for each channel.
- **14ט(ב)** for any transaction contractable online, a dedicated cancellation link on the **main
  page** of the website, `שימוקם באופן מובלט וברור`.
- **14ט(ג)** the notice carries the consumer's name and ID number, plus one further agreed
  identifying detail for an oral notice. The seller may not require more. An intake form gating
  cancellation behind an order number, a reason code or a photo is over-collecting.
- **14ט(ד)** the channels, their contact details, and the required notice contents must be disclosed
  in writing no later than supply of the goods or services. "In writing" includes the contract, a
  disclosure form, or a document setting out the main terms.
- **14ט(ה)** the same information must also appear on invoices, receipts and payment notices sent to
  the consumer, and, if the seller has a website, on its main page beside the dedicated link.
- **14ט(ו)** all of that information must appear adjacent to one another,
  `בהבלטה מיוחדת ובאותיות ברורות וקריאות`.
- **14ט(ז)** none of section 14ט applies to a 14ו return.

## Enforcement: the narrow version is the true one

It is often said that any breach of 14ט carries statutory damages. That does not survive reading the
statute. Searching sections 23 and 31א for references to 14ט yields one limb:

**Section 31א(א)(2ב)** allows פיצויים לדוגמה without proof of damage where a consumer cancelled a
**continuing** transaction (עסקה מתמשכת) by a 14ט notice and the seller kept charging them, contrary
to section 13ד(ג). Section 31א(א) caps such damages at 10,000 NIS.

Use the narrow statement. It is enough reason to build the intake correctly.

## Refund and fee mechanics

- **14ה(א)(1)** seller breach: refund within 14 days of receiving the cancellation **notice**,
  cancel the charge, provide a copy of the charge-cancellation notice, and charge **no**
  cancellation fee.
- **14ה(ב)(1)** any other reason: same 14-day-from-notice clock, and at most 5% of the price or
  100 NIS, whichever is lower.
- **14ה(א)(2)** on seller breach the buyer only makes the goods available **at the place they were
  delivered** and notifies the seller. Collection is the seller's job.
- **14ה(ב)(2)** on change of mind the buyer returns the goods to the seller's **place of business**.
- **14ה(ד)** דמי ביטול is defined as **including** shipping and packing costs, so outbound shipping
  cannot be deducted on top of the cap.
- **14ה(ב2)** where the seller installed goods in the buyer's home in order to provide the service
  under the transaction, installation costs may be recovered up to 100 NIS.
- **14ה(ג)** none of this removes the seller's right to sue for a significant deterioration in the
  goods' value.
- **14ג(ו)** defines מחיר הנכס as the total price including delivery. That definition opens
  `בסעיף זה`, so carrying it into the 14ה(ב)(1) cap is a consumer-protective inference rather than
  an express cross-reference. The 100 NIS leg usually binds first anyway.

## The four-month window (14ג1)

Four months, instead of 14 days, for a buyer who is:
- an אדם עם מוגבלות as defined in חוק שוויון זכויות לאנשים עם מוגבלות, התשנ"ח-1998
- an אזרח ותיק, meaning 65 or over
- an עולה חדש, meaning within five years of a תעודת עולה **or** a תעודת זכאות כעולה from
  משרד העלייה והקליטה

Two conditions people get wrong:
1. **14ג1(ג) requires that the contracting of THIS transaction included a conversation** between
   seller and buyer, including by electronic communication. A support widget the buyer never used on
   this order does not satisfy it, and the mere existence of live chat on the site is not the
   conversation.
2. **14ג1(ד)** the seller may require ONE identifying document and may not demand further proof.
   The statute lists the acceptable documents; an intake accepting only תעודת עולה will wrongly
   reject qualifying buyers.

14ג(ד) applies to the four-month window too, so the same five exclusions hold.
