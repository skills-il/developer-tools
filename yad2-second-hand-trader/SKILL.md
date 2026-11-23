---
name: yad2-second-hand-trader
description: >-
  Buy and sell second-hand goods safely on Yad2 (Yad2 Market): writes optimized Hebrew
  listings with a comparable-based fair-price band, drafts buyer/seller negotiation
  messages, and runs a fraud red-flag checklist against suspicious buyers or sellers.
  Use when a private person asks to "write a Yad2 listing", "sell my used X on Yad2",
  "is this Yad2 buyer a scam", "מוכר ביד2", "קונה ביד2", or wants to negotiate a Yad2
  price. Knows the current Israeli scam playbook (fake GLS shipping payments, forged
  bank-transfer screenshots, phishing "Israel Post" credit-card links, Bitcoin demands)
  and the safety rules (never pay in advance, meet and inspect, cash or known payment
  apps). Do NOT use for vehicle ownership or registration checks (use israeli-vehicle-manager),
  business multi-channel selling on Zap/KSP/Facebook (use israeli-marketplace-seller),
  rental apartment hunting (use israeli-apartment-hunting), or retailer price comparison
  (use israeli-product-price-comparator).
license: MIT
allowed-tools: ''
compatibility: >-
  Pure text generation (listings, messages, scam risk ratings). No local shell, API key, or
  network access required. Works on Claude Code, Claude.ai, Claude Desktop, Cursor,
  ChatGPT, Gemini CLI, and other agents.
---

# Yad2 Second-Hand Trade & Scam Shield

## Legal notice

This is a free information tool operating through an AI model. It explains, in general terms, how second-hand trading on Yad2 works, what the common fraud patterns look like, and which law generally applies to a private sale. It is not legal advice, and its scam risk rating is an indication, not a determination that any person committed an offence. An AI model can err, miss a detail, or reach a wrong conclusion, and a deal the tool calls "looks normal" can still be a fraud.

Any listing or negotiation message the tool drafts is an automatic draft for your own personal use only. It is not a document prepared by a lawyer, no lawyer reviewed it, and it must not be relied on as evidence. The tool is not a substitute for advice that takes into account each person's particular facts and needs, and any use of its output is the user's sole responsibility. Whether the Consumer Protection Law, the Sales Law, or any other right applies to your specific transaction depends on facts the tool has not verified. Before suing, signing, or filing anything with an authority or a court, consult a lawyer. Reporting a suspected offence is a matter for Israel Police.

## Problem

Yad2 is where Israelis buy and sell almost everything second-hand, but a private seller has no protection net to rely on: an ordinary Yad2 deal has no escrow behind it (only listings in Yad2's orange-check service run the payment through Yad2), the Consumer Protection Law's cancellation right does not cover private peer-to-peer sales, and the platform is a constant target for a well-known set of scams. People lose money to forged bank-transfer screenshots and fake "pay the courier first" requests, undersell good items because they do not know the going rate, and write weak listings that sit unanswered for weeks. This skill writes a strong Hebrew listing with a defensible price, drafts the negotiation messages, and screens any suspicious buyer or seller against the current Israeli fraud playbook before money changes hands.

## Instructions

This skill does three jobs. Identify which one the user needs, then follow the matching section. A single conversation often chains them (write a listing, then a buyer replies and you screen them).

### Job 1: Write a Yad2 listing (seller)

Collect from the user: item (model/brand if relevant), condition, age, reason for selling, city/area, and any flaws. Then produce a complete Hebrew listing.

A strong Yad2 listing has four parts:

| Part | What to write |
|------|---------------|
| Title (כותרת) | Brand + model + key spec + condition word. Searchable, no clickbait. e.g. `ספה תלת-מושבית IKEA EKTORP אפורה, מצב מצוין` |
| Description (תיאור) | 3 to 6 short lines: what it is, age, why selling, condition honestly (state real flaws, this builds trust and cuts time-wasters), what is included, pickup area. |
| Condition (מצב) | One of: חדש באריזה / כמו חדש / מצוין / טוב / סביר / דורש תיקון. Be honest, a buyer who drives over and finds hidden damage walks away. |
| Asking price (מחיר) | A defensible number, see the pricing method below. |

**Pricing method (never invent a number from memory).** Do not state a price as if it were a known market rate. Instead:
1. Tell the user to open Yad2 Market and search the same item, filtering to active listings of the same model, condition, and rough age.
2. Take the cluster of comparable asking prices, drop outliers, and propose a band (low / fair / quick-sale).
3. Adjust for condition and age relative to the original retail price (more wear = lower; rare/discontinued = can hold value).
4. Present it as: "based on comparable Yad2 listings you find, expect roughly X to Y; price at the higher end if you can wait, lower for a fast sale." If the user has no comparables yet, ask them to gather 3 to 5 first.

Add photo guidance: real photos (not catalog images), multiple angles, natural light, and a photo of any flaw you mentioned.

**If a listing sits unanswered for weeks**, do not jump straight to a price cut. Under Yad2's current terms a basic second-hand listing is free for up to 40 days and can be bumped manually (קפיצת מודעה) once every 24 hours, so tell the user to use that free bump first, refresh the photos and title, and consider Yad2's paid promotion only if comparables show their price is already right. The terms say a listing past its time limit cannot be extended, so check in the app what happens at expiry rather than promising a renewal.

### Job 2: Draft negotiation messages

Israeli second-hand haggling is normal and expected. Draft short, polite, direct Hebrew messages. Match the user's role:

- **Buyer lowering a price:** acknowledge the item, give a concrete reason for a lower offer (cash now, immediate pickup, a visible flaw, comparable cheaper listings), and name a specific number. Avoid insulting lowballs.
- **Seller holding or countering:** thank, justify the price briefly (condition, what's included, recent comparable sales), and offer a small concession (round down, throw in an accessory) rather than a big drop.

Keep messages WhatsApp-length. Always close toward a concrete next step (a pickup time and place), because a deal that never sets a meeting time is usually a deal that dies or a scammer stalling.

Do not draft a cancellation, defect notice, or claim. List what such a message usually contains and let the user write it in their own words.

### Job 3: Scam shield (screen a suspicious interaction)

First ask (or infer) which side the user is on, because the scams differ. Score the interaction against the matching table and return a clear risk rating: **likely scam / suspicious, slow down / looks normal**.

**If the user is the SELLER (they posted the item):**

| Red flag | Why it is a scam signal |
|----------|------------------------|
| Buyer wants to pay before seeing the item and arrange shipping (especially via GLS) | The signature Yad2 seller scam: the buyer pushes the seller to pay the courier first. |
| A bank-transfer confirmation screenshot arrives but no money is in your account | Forged transfer screenshots are a core tactic. A screenshot is not a payment. Only your own bank balance (or, for Bit/PayBox, your own app) proves payment. |
| A "payment" or "credit" link is sent for you to enter card details (often dressed as Israel Post / דואר ישראל) | The link harvests your credit-card details. Couriers never need YOUR card to pay YOU. |
| Payment demanded in Bitcoin / crypto | Irreversible, untraceable. Legitimate local second-hand deals do not use crypto. |
| "I overpaid by mistake, refund me the difference" | Overpayment scam. The original payment is fake or will be reversed; your refund is real money out. |
| Pressure to move off Yad2 chat fast, urgency, "I'm abroad / in Eilat / soldier / relocating" | Classic social-engineering framing to justify shipping and remote payment. Contact typically moves to WhatsApp right after the listing goes up. |
| Buyer asks you to send them a verification CODE you just received by SMS | Account-takeover, not a purchase. That code is the registration code for YOUR WhatsApp (or another account); handing it over hands over the account, which is then used to scam your contacts. Never send a code to anyone, for any reason. If one was already sent, go to the recovery steps below. |
| The "buyer" runs a WhatsApp **Business** account and writes fluent Hebrew | Do NOT read either as reassurance. Per the Israeli Internet Association, scammers deliberately set the account to business and write in Hebrew (sometimes with errors, but not always) precisely to look credible. Good Hebrew clears nobody. |

**If the user is the BUYER (they are responding to a listing):**

| Red flag | Why it is a scam signal |
|----------|------------------------|
| Seller asks for a deposit / "holding fee" (מקדמה / דמי רצינות) before you see the item | The deposit scam: fake listing for a hot item (PS5, concert tickets, a puppy, an apartment), you pay to "reserve", the seller vanishes. Never send money to hold an item you have not inspected. |
| Price is far below market for the model/condition | Too-good-to-be-true is bait. Pull comparables first. |
| Listing photos look like stock or stolen images | Run a reverse-image search. Fake listings reuse photos. |
| Seller refuses to meet in person or give a real pickup location | Without a physical handover you have no way to inspect or recover anything. |
| Phone / laptop / e-bike priced suspiciously low, seller dodges proof of origin | Possible stolen goods. Buying stolen property can mean it gets seized and you are out the money. Ask for the box, receipt, or serial. |
| Seller asks you to send them a code you received by SMS | Account takeover, not a sale. Never send a code to anyone. |
| For phones: seller will not let you verify it on the spot | Before paying, power it on, insert a SIM, and confirm it is not iCloud/Google activation-locked or reported lost/stolen. A locked phone is a brick. |

**The two rules that defeat almost every Yad2 scam, per Yad2's own guidance:**
1. Never transfer money in advance, and certainly never abroad on a future promise.
2. Meet in person, inspect the item against the listing, and pay/receive at handover.

**Payment-rails reality (the part that actually protects a seller).** "Cash or a recognized app" is not all equal:
- **Cash** is safest, instant and final.
- **Bit / PayBox** are much safer to RECEIVE than a screenshot, because you can see the transfer in your own app, and the Israeli Internet Association recommends apps with an instant payment indication. A 2022 ice guide says a Bit transfer cannot be cancelled once approved, and that money from an approved request reaches the bank by the end of the next business day. Check the app for the current terms, including any PayBox cancellation option, rather than promising one. Confirm receipt by opening YOUR OWN app, never from the buyer's phone or a screenshot. At handover the proof is the transfer in your own app, not necessarily your bank balance yet.
- A **bank transfer "confirmation" shown at the meeting is NOT proof** the money cleared. Do not hand over the item against a screenshot; wait until it actually shows in your balance.
- A **cheque** is not payment until your bank confirms it cleared. Do not hand over the item or refund any "difference" before that.
- Beware a **payment REQUEST (בקשת תשלום)** sent to you: approving a request sends YOUR money out, it is the opposite of receiving a payment. Scammers disguise a request as "I'm paying you, just approve."

**The BUYER's side (say this before anyone pays a stranger).** A payment that is hard to reverse is good to receive and bad to send to someone you have not met.

**What the law says about getting money back (general information).** Explain these rules in general terms. Do not tell the user which category their incident falls into, whether they are liable, or whether they are owed a refund. In every case the first action is the same: tell the payment provider immediately and ask for its position in writing.

- The Payment Services Law limits a payer's liability for **misuse** (use by someone not entitled): nothing after notice, and before notice no more than NIS 450 if notice is given within 30 days of the first misuse, with the rest refunded within 8 business days (ss.24, 27). There is an exception, and a payment the customer approved is generally treated differently. Whether an approval obtained by deception counts is contested, and this tool does not decide it. ss.16 and 17 can stop a payment in some cases.
- Read `references/payment-law.md` before explaining any of this.

What to do by payment type:

| If the user paid by | Action now | How this payment method works |
|---|---|---|
| Credit card | Call the issuer: block the card and report charges you do not recognize. If the agreed delivery date has passed and the item never came, the user can write the seller a short cancellation in their own words, then tell the issuer. | Has misuse rules and a statutory stop route for an undelivered item (see `references/payment-law.md`). |
| Bit | Call the bank or the app now and report what happened. | A 2022 ice guide says an approved transfer cannot be cancelled. |
| PayBox | Call PayBox or the bank now, and check the app for any cancellation option. | Any cancellation option is shown in the app. Do not assume one exists. |
| Bank transfer | Call the bank now and ask to stop it (s.16). If it already went through, ask what it can do to help trace it. | Can be stopped only while the bank can still halt it. You hold the beneficiary's account details, which is useful evidence. |
| Cash | No provider to call. | No provider and no record, which is why it is right at a handover and wrong in advance. |

**Stay on Yad2 chat and report.** Prefer Yad2's built-in chat, because pressure to move off it is itself a scam pattern. Yad2's terms say it has no access to chat content (messages are encrypted and only the parties can read them), so a report does not hand Yad2 the conversation: screenshot it first. If something is a scam, report the user/listing to Yad2 itself (דיווח על משתמש / מודעה) as the first-line action, in addition to the steps below.

**Safe handover.** Meet in a public place in daylight. Do not share your home address until you are committed, and prefer a building lobby or a public spot, especially if meeting alone. Furniture and appliances are the awkward case, since you cannot carry a sofa to a cafe: for those, never be alone in the home, agree a fixed time rather than an open window, and hand over at the door or lobby where possible.

**Beyond scams (time-wasters and weird buyers).** Not every odd buyer is a fraud. A buyer who haggles hard then no-shows, or asks "still available?" endlessly without committing, is usually a time-waster, not a thief. A buyer who wants to send a representative or courier to collect is different: that is how the forged-transfer scam takes the item, so hand it over only after the money shows in your own app or bank balance. Set a concrete pickup time, do not hold the item without one, and move on if they stall.

**Consumer-law reality check (state this when relevant).** The Consumer Protection Law's cooling-off / cancellation right applies to a consumer buying from a business (עסקה צרכנית מול עוסק). A private Yad2 sale between two individuals is NOT covered, so do not tell a buyer from a genuinely private seller that they have a 14-day return right, it generally does not apply. The test is the seller's status, not the website: someone who sells in the course of business is an עוסק even on a "private" listing. If the seller looks like a dealer (many similar items, a shop, invoices) and the deal followed the dealer's remote marketing without the parties meeting, the distance-sale rules may apply: s.14ג allows cancellation until 14 days from receipt or from the required written disclosure, whichever is later, with some goods excluded, and s.14ג1 extends this to four months for a person with a disability, someone aged 65 or over, or a new immigrant within five years of aliyah, where the deal included a conversation. A deal closed face to face is generally outside these rules. The law overrides contrary terms (s.36), so Yad2's 24-hour process does not replace any such right, and anyone relying on it should give written notice before the window ends. Flag this as something to check, not something the tool decides. And "no Consumer Protection Law" does NOT mean "no recourse": a seller must still disclose known defects, and a buyer who was deceived or sold an item with an undisclosed hidden defect (מום נסתר) can pursue remedies under general contract law and the Sales Law (חוק המכר), typically in small claims court (`israeli-small-claims-court`). The Sales Law ties this to notice: inspect right after receipt and tell the seller about a defect immediately on finding it, with reasonable detail, because a buyer who does not notify can lose the right to rely on it (ss.13 to 17). Inspect before paying anyway, it is far easier than suing.

**A buyer-arranged courier vs Yad2's own orange-check service (וי כתום).** The shipping scam is a BUYER-ARRANGED courier the seller is told to pay. The orange check is a real, different service, offered only for eligible listings. Its terms can change, so check them before relying on a figure.

- **Buyer:** start from the listing inside Yad2, never from a link someone sent. The card is entered on a separate payment page, which is normal only when reached that way. Before the charge date the terms describe a hold on the credit line, depending on the card. The card is charged finally 24 hours after receipt or 6 days after the payment instruction, whichever comes first, so if the item has not arrived by about day 5, tell Yad2 in writing that the deal is not complete. Check the item on receipt: Yad2's process takes a written, reasoned non-conformity claim within 24 hours of receipt. Those hours run through Friday and Shabbat, while the phone line works Sunday to Thursday 09:00 to 16:00, so do not wait for it. The claim clause names no channel, so write the same day through the written routes the terms list (contact@yad2.co.il or the cancellation link at the bottom of the site), with photos, and keep a copy. Tell the seller at the same time, because the Sales Law notice goes to the seller and Yad2 is not a party. Later disputes are directly with the seller. Not responding or cooperating in the process counts as a full waiver toward Yad2, the decision is at its sole discretion, and handling and delivery fees are deducted from a refund. Yad2 does not commit to a physical inspection, and it is not a party to the sale.
- **Seller:** the fee is 30% of the price under the current terms, the money arrives within 4 business days of delivery, you commit not to sell the item another way during the service, and stopping it after it starts carries a charge. Bank details, an ID copy and an account confirmation go only inside your logged-in Yad2 account, opened by you. A link from a buyer or a chat asking for any of these, or for a seller's card, is phishing.

The rule is not "never ship", it is "never pay a courier the other side arranged, and never pay to receive money".

**If the user was already scammed, in this order:**
1. Stop paying and stop responding. Enter nothing more and send no further code. Keep every screenshot, the listing URL, and the counterparty's phone/username.
2. **Money and accounts first, before paperwork.**
   - **A WhatsApp code was sent:** open WhatsApp now, tap Log back in, and enter the new 6-digit code, which logs every other device out. If it asks for a PIN you do not know, WhatsApp says to wait 7 days and try again. Tell family and friends by phone or another channel, because the attacker can impersonate you.
   - **Anything else was paid or shared:** phone the bank, card company, or payment app NOW, using the number in its official app or on the card. Report what happened and ask to stop or block anything still possible. Where a payment counts as misuse, the law ties liability to the time of notice, so report first either way, without waiting for a police report. Banks must run a human fraud line around the clock, Shabbat included, under Bank of Israel Directive 426 (in force since 31.05.2026).
   - **Paid by card and the item never came:** after that call, if the agreed delivery date has passed, the user can write the seller a short cancellation in their own words, then tell the issuer.
   - **The provider refuses:** ask for the answer and reasons in writing. A complaint about a bank or card company goes first to its public complaints commissioner, which generally answers within 45 days, and then to the Banking Supervision public enquiries unit at the Bank of Israel. A lawyer remains an option.
3. Report the user and the listing to Yad2 itself.
4. **File the police complaint through the official Israel Police online service** (see Reference Links), choosing the **`עבירת רכוש והונאה`** subject. Two things to tell the user plainly, because both surprise people:
   - The online form is a **request** to file; it is not an official complaint until police investigators complete the process. Filing at the nearest station is the alternative.
   - It requires identification through the national identification system (הזדהות לאומית).
   For an emergency, or anything needing an officer at the scene, call **100** instead.
5. Report phishing links to the National Cyber Directorate. Note this explicitly for the user: a cyber report is **not** a substitute for the police complaint, and the Directorate itself says so.

## Examples

### Example 1: Write a listing
User says: "Write me a Yad2 listing for my 2-year-old IKEA EKTORP 3-seat sofa, grey, very good condition, selling because we're moving, in Ramat Gan."
Actions:
1. Produce a Hebrew title, description (3 to 5 lines, honest condition, pickup in Ramat Gan), condition tag `מצוין`.
2. Do NOT state a price as fact. Tell the user to pull comparable active EKTORP listings on Yad2 Market, then propose a band relative to retail and condition.
3. Add photo guidance (multiple angles, daylight, any flaw shown).
Result: A ready-to-paste Hebrew listing plus a pricing instruction.

### Example 2: Scam screen
User says: "A buyer on Yad2 says they'll pay extra and arrange a GLS courier, but I need to pay the courier first via a link they sent. Is this real?"
Actions:
1. Match red flags: pay-courier-first + external link + pay before seeing = the signature Yad2 shipping scam.
2. Return the risk rating: likely scam. Explain the link harvests card details and the courier never needs the seller to pay.
3. Tell them to refuse, only accept payment they can see in their account or cash at handover, and report the link to the National Cyber Directorate.
Result: A clear "likely scam" rating with the reason and next step.

### Example 3: Negotiate
User says: "A seller listed a used PS5 above what comparable listings show. Help me offer less, I can pick up today and pay cash."
Actions:
1. Draft a short polite Hebrew message offering a concrete lower number, leveraging cash + same-day pickup, and referencing comparable listings if any.
2. Close with a proposed pickup time/place.
Result: A WhatsApp-length Hebrew counter-offer message.

## Bundled Resources

### Scripts
- `scripts/scam_score.py` -- flags known scam wording in a described Yad2 interaction. Offline, stdlib-only, no network call. Run: `python3 scripts/scam_score.py --text "..."`. It is a keyword helper and misses naturally phrased scams, so the red-flag tables above are always the real check, and a run with no match never clears a deal. On a host without a shell (Claude.ai, ChatGPT, Manus) use the tables directly.

### References
- `references/scam-playbook.md` -- the full Israeli Yad2 scam catalog with the exact buyer/seller scripts and the safe-deal checklist. Consult when screening any suspicious interaction.
- `references/payment-law.md` -- the exact Payment Services Law rules (ss.16, 17, 24, 27) and the Justice Ministry opinion, in English and Hebrew. Consult before explaining liability, refunds, or stopping a payment.
- `references/listing-and-pricing.md` -- listing templates by category (furniture, electronics, baby gear, appliances) and the comparable-based pricing method. Consult when writing a listing.
- `references/domain-checklist.md` -- coverage contract for this skill (used by maintenance).

## Recommended MCP Servers

No MCP server currently exposes Yad2 second-hand listing data, so this skill is standalone (it generates listings, messages, and scam risk ratings from the user's own description and from live comparables the user pulls on Yad2).

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Israeli Internet Association | https://www.isoc.org.il/digital-literacy/cybersafe/yad2-shipping-scams | The GLS/shipping scam mechanics and warning to sellers |
| Yad2 safety guide | https://magazine.yad2.co.il/shopping/קונים-אונליין-ככה-תשמרו-על-עצמכם-מהונא/23647 | Yad2's official buyer-safety tips |
| Yad2 Market | https://www.yad2.co.il/market | The second-hand goods marketplace |
| Kol-Zchut: cancelling a distance (online/phone) purchase | https://www.kolzchut.org.il/he/ביטול_עסקה_שנעשתה_באינטרנט_או_בטלפון | The 14-day distance-sale cancellation right |
| Smart consumer guide (private sales) | https://taasiri-law.co.il/מדריך-לצרכן-הנבון-120-שאלות-ותשובות-בדינ/ | A seller must disclose known defects even in a private sale; recourse via general law |
| Yad2 terms of use | https://www.2.yad2.co.il/en/eula | Free basic listing period, manual bump, and that Yad2 has no access to chat content |
| Yad2 orange-check terms | https://www.2.yad2.co.il/en/verified-terms-conditions | Charge timing, seller fee, 24-hour claim window, no commitment to a physical inspection |
| Payment Services Law, 2019 | https://www.nevo.co.il/law_html/law01/502_043.htm | ss.16, 17, 24, 27: cancelling an order, stopping a charge, the liability cap, the 8-business-day refund |
| Justice Ministry opinion on s.24 (2021) | https://www.gov.il/BlobFolder/reports/phishing-opition/he/internternational-law_media_phishing-opition.pdf | Impersonation and handing over a code |
| Bank of Israel Directive 426 | https://www.boi.org.il/media/k23b3lzq/h2834.pdf | The 24/7 human fraud line at banks |
| Consumer Protection Law | https://www.nevo.co.il/law_html/law01/089_001.htm | Who counts as an עוסק and a צרכן, ss.14ג and 14ג1 on distance sales |
| Sales Law, 1968 | https://he.wikisource.org/wiki/חוק_המכר | ss.13 to 17: inspection and the duty to notify the seller of a defect |
| WhatsApp: recover a compromised account | https://faq.whatsapp.com/1131652977717250 | Logging back in with a new code, and the 7-day wait for an unknown PIN |
| Kol-Zchut: complaint to the Banking Supervision public enquiries unit | https://www.kolzchut.org.il/he/הגשת_תלונה_ליחידה_לפניות_הציבור_של_הפיקוח_על_הבנקים | The bank or card company's complaints commissioner comes first, and its 45-day reply period |
| Bit transfer guide (ice, 2022) | https://www.ice.co.il/digital-140/news/article/845420 | A Bit transfer cannot be cancelled once approved, and when the money reaches the bank |
| Israel Police: file a complaint (official service) | https://www.gov.il/he/service/request-file-complaint-online-during-emergency | The subject list including `עבירת רכוש והונאה`, and that emergencies go to 100 |
| Kol-Zchut: online police complaint (procedure) | https://www.kolzchut.org.il/he/בקשה_להגשת_תלונה_במשטרה_דרך_האינטרנט | That the online form is a request, not an official complaint until police complete it |
| National Cyber Directorate | https://www.gov.il/he/service/cyber-event-report | Report phishing links and cyber incidents |

## Gotchas

- **Never invent a price.** Agents confidently state "a used X goes for Y shekel" from memory. Second-hand prices are local and volatile. Always derive the band from comparable ACTIVE Yad2 listings the user pulls, and present it as a range with a method, not a fact.
- **A bank-transfer screenshot is not a payment.** Agents (and sellers) treat a transfer confirmation image as proof. It is trivially forged and is the core of the Yad2 seller scam. Only the seller's own bank balance, or their own Bit/PayBox app, proves payment.
- **Do not promise a private buyer a return/cancellation right.** The Consumer Protection Law 14-day cooling-off applies to a distance purchase from a business (עוסק), not to a private person selling a used item. Telling a buyer from a genuinely private seller they can return it within 14 days is wrong and creates disputes. If the seller may be a dealer, flag it as something to check.
- **A courier never needs YOU to pay to send money TO you.** Any "pay the shipping company / pay this link to receive your credit" framing is a scam, full stop.
- **Do not treat all payment apps as equal, and do not confuse a payment with a payment request.** Cash is the safest to RECEIVE, and Bit or PayBox work when the transfer shows in your own app; a bank-transfer screenshot at the meeting is NOT cleared money. A "payment request" (בקשת תשלום) approved by the user sends THEIR money out, the reverse of getting paid.
- **A buyer faces a different scam from a seller.** When the user is buying, watch for a request to pay a מקדמה to "hold" a fake listing. Do not give a buyer only the seller-side shipping warning.
- **Keep negotiation messages short and Hebrew-native.** Long, formal, translated-sounding messages read as bot or scam. Israeli haggling is brief, direct, and friendly.

## Troubleshooting

### Error: "I gave the buyer a price but it's much lower/higher than other listings"
Cause: priced from memory instead of comparables.
Solution: pull 3 to 5 active comparable Yad2 listings for the same model/condition first, then set the band.

### Error: "The buyer's bank transfer 'went through' but the money isn't in my account"
Cause: either a forged screenshot or a real transfer still on its way. The Israeli Internet Association says a bank transfer usually takes about two to three days.
Solution: do not hand over the item until the money shows in your own bank balance. A delay alone proves nothing. Pressure to ship or hand over in the meantime is a strong red flag.

### Error: "Is it safe to ship the item to a buyer I haven't met?"
Cause: shipping + pre-payment is the highest-risk pattern on Yad2.
Solution: prefer in-person handover with cash or a recognized payment app. If shipping is unavoidable, never pay any courier yourself and never enter card details in a link the buyer sends.
