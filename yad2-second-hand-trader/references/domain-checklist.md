# Domain Coverage Checklist (yad2-second-hand-trader)

Generated: 2026-06-18 via research on: isoc.org.il (Israeli Internet Association), magazine.yad2.co.il (Yad2 official safety guidance), kolzchut.org.il (Consumer Protection Law), gov.il (police cybercrime + cyber directorate).

Scope: helping a PRIVATE individual buy and sell second-hand goods on Yad2 (Yad2 Market). Three jobs: listing writer, negotiation assistant, scam shield. Vehicles, business multi-channel selling, rentals, and retailer price comparison are out of scope (handled by sibling skills).

## Must cover (core)
- [ ] Hebrew listing structure (title, description, condition, asking price), what a strong Yad2 listing contains. source: magazine.yad2.co.il. why core: the listing-writer job is the skill's primary deliverable.
- [ ] Fair-price methodology, NOT invented price tables: instruct the agent to derive a price band from comparable ACTIVE listings (same model/condition/age) and depreciation, never from a memorized number. source: methodology, not a figure. why core: prevents fabricated prices; pricing is the top seller question.
- [ ] Scam: forged bank-transfer screenshot. Fake buyer sends a fake transfer confirmation so seller ships/hands over the item. source: isoc.org.il. why core: most common seller-side fraud.
- [ ] Scam: "pay the shipping company (GLS) yourself", buyer pushes seller to pay a courier directly. source: isoc.org.il. why core: signature Yad2 scam.
- [ ] Scam: phishing payment link impersonating a courier / Israel Post, harvests the seller's credit-card details under a "receive your credit" pretext. source: isoc.org.il. why core: credit-card theft vector.
- [ ] Scam: payment demanded in Bitcoin / crypto. source: isoc.org.il. why core: irreversible-payment red flag.
- [ ] Safety rule: never pay in advance, never abroad on a future promise. source: magazine.yad2.co.il. why core: the single most protective rule.
- [ ] Safety rule: meet in person, inspect the item against the listing before paying. source: magazine.yad2.co.il. why core: prevents misrepresentation.
- [ ] Safety rule: pay in cash or via a recognized payment app at handover. source: magazine.yad2.co.il. why core: avoids reversible/forgeable payment traps.
- [ ] Buyer-side deposit / fake-listing scam: seller asks for a מקדמה / דמי רצינות to "hold" a sought-after item, then vanishes. source: common Israeli fraud pattern. why core: the skill triggers on buyer queries, and this was a launch gap.
- [ ] Payment-rails finality: cash is safest to RECEIVE, and Bit/PayBox work when the transfer shows in your own app; a bank-transfer screenshot at the meeting is NOT cleared money; an incoming payment REQUEST sends YOUR money out. source: isoc.org.il + a dated 2022 ice guide on Bit. why core: reversibility is the hinge of every payment scam.
- [ ] Consumer-law boundary: the cooling-off / cancellation right applies to a business-to-consumer sale (עסקה צרכנית), NOT to a private peer-to-peer Yad2 sale. source: Consumer Protection Law s.1. why core: agents routinely tell private buyers they have a return right they do not have.
- [ ] Legal recourse despite no Consumer Protection Law: a seller must disclose known defects, and a deceived buyer / undisclosed hidden defect (מום נסתר) has remedies under contract + Sales Law in small claims. source: taasiri-law.co.il. why core: do not tell a defrauded private buyer they have "no recourse".
- [ ] Report + stay on Yad2: keep the chat on-platform (evidence) and report the user/listing to Yad2 itself as a first-line action; then Israel Police online complaint + National Cyber Directorate. source: gov.il + kolzchut.org.il. why core: the user needs the action after a scam.
- [ ] Payment Services Law as general information: misuse cap and refund (ss.24, 27), order cancellation (s.16), undelivered item on a guaranteed payment (s.17). The skill does not classify the user's own incident. source: nevo 502_043 + Justice Ministry opinion 30.09.2021.
- [ ] Verification-code attack, including what to do after a code was sent. source: isoc + WhatsApp help page (read in a browser 2026-11-23).
- [ ] Dealer posing as private: s.14ג and s.14ג1 windows, face-to-face deals generally outside. source: nevo 089_001.
- [ ] Sales Law duty to inspect and notify (ss.13 to 17). source: Sales Law.
- [ ] Post-fraud recovery ORDER and the correct police channel: provider notice first on every rail (Payment Services Law ss.16, 17, 24, 27), then Yad2 report, then the OFFICIAL police online complaint under `עבירת רכוש והונאה` (a request, not yet an official complaint; national identification required; 100 for emergencies; the skill names no specialist unit), then the cyber report which does not replace it. source: gov.il police service + kolzchut procedure page + gov.il cyber-event-report. why core: reviewed 2026-08-18, this is the step a defrauded user actually needs and the launch text named none of it.

## Should cover (advanced / edge cases)
- [ ] Negotiation message drafting (buyer counter-offer + seller hold-firm) in natural Hebrew. source: common practice. why: second core deliverable.
- [ ] Dealer-posing-as-private seller red flag (especially for higher-value goods). source: common practice. note: deep vehicle checks are out of scope (israeli-vehicle-manager).
- [ ] Stolen-goods risk + IMEI / activation-lock check when BUYING phones/electronics/e-bikes. source: common practice. why: biggest used-electronics burn.
- [ ] "Boost"/promoted-listing and the free manual bump (קפיצת מודעה) mechanics for a stale listing, mention as an option, do not invent prices.
- [ ] Safe handover logistics (public place, daytime, bring a friend, do not share home address until committed; personal-safety dimension).
- [ ] Non-scripted weirdness: no-shows, time-wasters, endless "still available?". A representative or courier sent to collect is a scam signal, not weirdness. source: common practice.
- [ ] Yad2's orange-check service (verified 2026-11-23 from its terms) vs a buyer-arranged courier: charge timing, seller fee, seller never enters a card, 24-hour claim window. Do not brand all shipping as the scam.
- [ ] Photo guidance for listings (real photos, multiple angles, show flaws to build trust).

## Out of scope (explicit, with rationale, re-checked 2026-11-23)
- Vehicle ownership, registration, test, lien/history checks. related skill: israeli-vehicle-manager handles it. This skill only helps WRITE a vehicle listing or spot a scam, not verify ownership.
- Business multi-channel selling ops (Zap, KSP, Facebook/Instagram inventory sync, sales analytics). related skill: israeli-marketplace-seller.
- Rental apartment hunting on Yad2. related skill: israeli-apartment-hunting.
- Retailer/new-product price comparison (KSP, Ivory, Zap retail). related skill: israeli-product-price-comparator.

## Authoritative sources
- https://www.isoc.org.il/digital-literacy/cybersafe/yad2-shipping-scams : the GLS/shipping scam mechanics (Israeli Internet Association, moved from isoc.org.il).
- https://www.yad2.co.il/market : the Yad2 Market second-hand platform.
- https://www.kolzchut.org.il/he/ביטול_עסקה_שנעשתה_באינטרנט_או_בטלפון : the 14-day distance-sale cancellation right.
- https://www.nevo.co.il/law_html/law01/089_001.htm : who is a business and a consumer (s.1), distance sales (ss.14ג, 14ג1), contrary terms (s.36).
- https://www.gov.il/he/service/cyber-event-report : National Cyber Directorate phishing/incident reporting (states it does NOT replace a police report).
- https://www.gov.il/he/service/request-file-complaint-online-during-emergency : Israel Police official complaint service; the `עבירת רכוש והונאה` subject and the 100 emergency route.
