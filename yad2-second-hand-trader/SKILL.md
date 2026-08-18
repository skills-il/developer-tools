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
  Pure text generation (listings, messages, scam verdicts). No local shell, API key, or
  network access required. Works on Claude Code, Claude.ai, Claude Desktop, Cursor,
  ChatGPT, Gemini CLI, and other agents.
---

# Yad2 Second-Hand Trade & Scam Shield

## Legal notice

This is a free information tool operating through an AI model. It explains, in general terms, how second-hand trading on Yad2 works, what the common fraud patterns look like, and which law generally applies to a private sale. It is not legal advice, and its scam verdicts are a risk indication, not a determination that any person committed an offence. An AI model can err, miss a detail, or reach a wrong conclusion, and a deal the tool calls "looks normal" can still be a fraud.

Any listing, negotiation message, or complaint text the tool drafts is an automatic draft for your own personal use only. It is not a document prepared by a lawyer and must not be relied on as evidence. Whether the Consumer Protection Law, the Sales Law, or any other right applies to your specific transaction depends on facts the tool has not verified. Before suing, signing, or filing anything with an authority or a court, consult a lawyer. Reporting a suspected offence is a matter for Israel Police.

## Problem

Yad2 is where Israelis buy and sell almost everything second-hand, but a private seller has no protection net to rely on: do not assume an escrow stands behind your deal, the Consumer Protection Law's cancellation right does not cover private peer-to-peer sales, and the platform is a constant target for a well-known set of scams. People lose money to forged bank-transfer screenshots and fake "pay the courier first" requests, undersell good items because they do not know the going rate, and write weak listings that sit unanswered for weeks. This skill writes a strong Hebrew listing with a defensible price, drafts the negotiation messages, and screens any suspicious buyer or seller against the current Israeli fraud playbook before money changes hands.

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

**If a listing sits unanswered for weeks**, the lever is rarely the price alone. Tell the user to bump/renew the listing (קפיצת מודעה / חידוש מודעה) so it returns to the top of search, refresh the photos and title, and consider Yad2's paid promotion only if comparables show their price is already right. Re-publishing a stale listing usually does more than another price cut.

### Job 2: Draft negotiation messages

Israeli second-hand haggling is normal and expected. Draft short, polite, direct Hebrew messages. Match the user's role:

- **Buyer lowering a price:** acknowledge the item, give a concrete reason for a lower offer (cash now, immediate pickup, a visible flaw, comparable cheaper listings), and name a specific number. Avoid insulting lowballs.
- **Seller holding or countering:** thank, justify the price briefly (condition, what's included, recent comparable sales), and offer a small concession (round down, throw in an accessory) rather than a big drop.

Keep messages WhatsApp-length. Always close toward a concrete next step (a pickup time and place), because a deal that never sets a meeting time is usually a deal that dies or a scammer stalling.

### Job 3: Scam shield (screen a suspicious interaction)

First ask (or infer) which side the user is on, because the scams differ. Score the interaction against the matching table and return a clear verdict: **likely scam / suspicious, slow down / looks normal**.

**If the user is the SELLER (they posted the item):**

| Red flag | Why it is a scam signal |
|----------|------------------------|
| Buyer wants to pay before seeing the item and arrange shipping (especially via GLS) | The signature Yad2 seller scam: the buyer pushes the seller to pay the courier first. |
| A bank-transfer confirmation screenshot arrives but no money is in your account | Forged transfer screenshots are a core tactic, with apps that fake the confirmation. A screenshot is not a payment. Only your own bank balance proves payment. |
| A "payment" or "credit" link is sent for you to enter card details (often dressed as Israel Post / דואר ישראל) | The link harvests your credit-card details. Couriers never need YOUR card to pay YOU. |
| Payment demanded in Bitcoin / crypto | Irreversible, untraceable. Legitimate local second-hand deals do not use crypto. |
| "I overpaid by mistake, refund me the difference" | Overpayment scam. The original payment is fake or will be reversed; your refund is real money out. |
| Pressure to move off Yad2 chat fast, urgency, "I'm abroad / in Eilat / soldier / relocating" | Classic social-engineering framing to justify shipping and remote payment. Contact typically moves to WhatsApp right after the listing goes up. |
| Buyer asks you to send them a verification CODE you just received by SMS | Account-takeover, not a purchase. That code is the registration code for YOUR WhatsApp (or another account); handing it over hands over the account, which is then used to scam your contacts. Never send a code to anyone, for any reason. |
| The "buyer" runs a WhatsApp **Business** account and writes fluent Hebrew | Do NOT read either as reassurance. Per the Israeli Internet Association, scammers deliberately set the account to business and write in Hebrew (sometimes with errors, but not always) precisely to look credible. Good Hebrew clears nobody. |

**If the user is the BUYER (they are responding to a listing):**

| Red flag | Why it is a scam signal |
|----------|------------------------|
| Seller asks for a deposit / "holding fee" (מקדמה / דמי רצינות) before you see the item | The deposit scam: fake listing for a hot item (PS5, concert tickets, a puppy, an apartment), you pay to "reserve", the seller vanishes. Never send money to hold an item you have not inspected. |
| Price is far below market for the model/condition | Too-good-to-be-true is bait. Pull comparables first. |
| Listing photos look like stock or stolen images | Run a reverse-image search. Fake listings reuse photos. |
| Seller refuses to meet in person or give a real pickup location | Without a physical handover you have no way to inspect or recover anything. |
| Phone / laptop / e-bike priced suspiciously low, seller dodges proof of origin | Possible stolen goods. Buying stolen property can mean it gets seized and you are out the money. Ask for the box, receipt, or serial. |
| For phones: seller will not let you verify it on the spot | Before paying, power it on, insert a SIM, and confirm it is not iCloud/Google activation-locked or reported lost/stolen. A locked phone is a brick. |

**The two rules that defeat almost every Yad2 scam, per Yad2's own guidance:**
1. Never transfer money in advance, and certainly never abroad on a future promise.
2. Meet in person, inspect the item against the listing, and pay/receive at handover.

**Payment-rails reality (the part that actually protects a seller).** "Cash or a recognized app" is not all equal:
- **Cash** is safest, instant and final.
- **Bit / PayBox** are good to RECEIVE because a transfer between people is immediate and effectively final (a Bit transfer cannot be cancelled once sent; treat a PayBox transfer as final too, and check the exact cancellation window in the app itself rather than promising the user one). That finality is exactly why a scammer prefers tricks over really sending one.
- A **bank transfer "confirmation" shown at the meeting is NOT proof** the money cleared. Do not hand over the item against a screenshot; wait until it actually shows in your balance.
- Beware a **payment REQUEST (בקשת תשלום)** sent to you: approving a request sends YOUR money out, it is the opposite of receiving a payment. Scammers disguise a request as "I'm paying you, just approve."

**The same finality read from the BUYER's side (say this before anyone pays a stranger).** Every property that makes a rail good to RECEIVE makes it bad to PAY WITH to someone you have not met. Rank the rails by what recovery actually exists after the money is gone:

| If the user paid by | Recovery route | Realistic odds |
|---|---|---|
| Credit card | Dispute the charge with the card company / bank. Call immediately, it is time-sensitive. | The only rail with a genuine built-in reversal route. This is why a card is the least-bad way to pay a stranger, and why blocking the card is step 2 after a fraud. |
| Bit | None by cancellation, a sent transfer cannot be cancelled. Getting it back depends on the recipient voluntarily returning it. | Poor. Report to the bank/app and rely on the police complaint. |
| PayBox | Any cancellation window is short and app-dependent, verify it in the app; assume none. | Poor. Do not rely on being able to pull it back. |
| Bank transfer | No unilateral reversal. The bank may help trace the account, which matters for the police complaint. | Poor for recovery, useful for evidence: you have the beneficiary's account details. |
| Cash | None. No record, no counterparty identity. | None. Its finality is exactly why it is right at a handover and wrong in advance. |

So the advice is not "use Bit, it is safe": Bit is safe **to be paid with**, and close to unrecoverable **to pay with** sight-unseen. A deposit is the one payment users most want to send and the one with the worst recovery.

**Stay on Yad2 chat and report.** Keep the conversation inside Yad2's in-app chat (it preserves evidence and is what lets Yad2 act). If something is a scam, report the user/listing to Yad2 itself (דיווח על משתמש / מודעה) as the first-line action, in addition to the steps below.

**Safe handover.** Meet in a public place in daylight. Do not share your home address until you are committed, and prefer a building lobby or a public spot, especially if meeting alone. Furniture and appliances are the awkward case, since you cannot carry a sofa to a cafe: for those, never be alone in the home, agree a fixed time rather than an open window, and hand over at the door or lobby where possible.

**Beyond scams (time-wasters and weird buyers).** Not every odd buyer is a fraud. A buyer who haggles hard then no-shows, asks "still available?" endlessly without committing, or wants to send a "representative" to pick up and pay is usually a time-waster, not a thief. Set a concrete pickup time, do not hold the item without a deposit you trust, and move on if they stall.

**Consumer-law reality check (state this when relevant).** The Consumer Protection Law's cooling-off / cancellation right applies to a consumer buying from a business (עסקה צרכנית מול עוסק). A private Yad2 sale between two individuals is NOT covered, so do not tell a private buyer they have a 14-day return right, they do not. But "no Consumer Protection Law" does NOT mean "no recourse": a seller must still disclose known defects, and a buyer who was deceived or sold an item with an undisclosed hidden defect (מום נסתר) can pursue remedies under general contract law and the Sales Law (חוק המכר), typically in small claims court (`israeli-small-claims-court`). Inspect before paying anyway, it is far easier than suing.

**If the buyer-arranged courier vs Yad2's own shipping.** The shipping scam is a BUYER-ARRANGED courier the seller is told to pay. Yad2's own in-app protected payment / delivery option (if it is offered in the user's app) is a different, legitimate flow. The rule is not "never ship", it is "never pay a courier the other side arranged, and never pay to receive money".

**If the user was already scammed, in this order:**
1. Stop all contact and payment. Keep every screenshot, the listing URL, and the counterparty's phone/username.
2. **Money first, before paperwork.** If card details were entered anywhere, phone the credit-card company / bank NOW to block the card and dispute the charge. A card charge is the one rail with a real chargeback route, which is why it is the first call and why it is time-sensitive.
3. Report the user and the listing to Yad2 itself.
4. **File the police complaint through the official Israel Police online service** (see Reference Links), choosing the **`עבירת רכוש והונאה`** subject. Two things to tell the user plainly, because both surprise people:
   - The online form is a **request** to file; it is not an official complaint until police investigators complete the process. Filing at the nearest station is the alternative.
   - It requires identification through the national identification system (הזדהות לאומית).
   For an emergency, or anything needing an officer at the scene, call **100** instead. Do not send a fraud victim to a specialist national unit such as להב 433, which is not a public intake channel for an individual complaint.
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
2. Return verdict: likely scam. Explain the link harvests card details and the courier never needs the seller to pay.
3. Tell them to refuse, only accept payment they can see in their account or cash at handover, and report the link to the National Cyber Directorate.
Result: A clear "likely scam" verdict with the reason and next step.

### Example 3: Negotiate
User says: "A seller listed a used PS5 above what comparable listings show. Help me offer less, I can pick up today and pay cash."
Actions:
1. Draft a short polite Hebrew message offering a concrete lower number, leveraging cash + same-day pickup, and referencing comparable listings if any.
2. Close with a proposed pickup time/place.
Result: A WhatsApp-length Hebrew counter-offer message.

## Bundled Resources

### Scripts
- `scripts/scam_score.py` -- scores a described Yad2 interaction against the known fraud flags and returns a verdict. Offline, stdlib-only, no network call. Run: `python3 scripts/scam_score.py --text "..."`. Optional: on a host without a shell (Claude.ai, ChatGPT, Manus) score the interaction directly against the red-flag tables above, which is the same logic.

### References
- `references/scam-playbook.md` -- the full Israeli Yad2 scam catalog with the exact buyer/seller scripts and the safe-deal checklist. Consult when screening any suspicious interaction.
- `references/listing-and-pricing.md` -- listing templates by category (furniture, electronics, baby gear, appliances) and the comparable-based pricing method. Consult when writing a listing.
- `references/domain-checklist.md` -- coverage contract for this skill (used by maintenance).

## Recommended MCP Servers

No MCP server currently exposes Yad2 second-hand listing data, so this skill is standalone (it generates listings, messages, and scam verdicts from the user's own description and from live comparables the user pulls on Yad2). If a Yad2 marketplace MCP is added later, pair it here for automated comparable-price lookups.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Israeli Internet Association (Block) | https://block.org.il/news/yad2-shipping-scams/ | The GLS/shipping scam mechanics and warning to sellers |
| Yad2 safety guide | https://magazine.yad2.co.il/shopping/קונים-אונליין-ככה-תשמרו-על-עצמכם-מהונא/23647 | Yad2's official buyer-safety tips |
| Yad2 Market | https://www.yad2.co.il/market | The second-hand goods marketplace |
| Kol-Zchut: cancelling a distance (online/phone) purchase | https://www.kolzchut.org.il/he/ביטול_עסקה_שנעשתה_באינטרנט_או_בטלפון | Confirms the cancellation right is a consumer right against a business, so it does not reach a private Yad2 deal |
| Smart consumer guide (private sales) | https://taasiri-law.co.il/מדריך-לצרכן-הנבון-120-שאלות-ותשובות-בדינ/ | A seller must disclose known defects even in a private sale; recourse via general law |
| PayBox FAQ | https://www.payboxapp.com/faq/ | The cancellation terms for a transfer, under the transfers category |
| Bit FAQ | https://www.bitpay.co.il/he/private-faq | A Bit transfer cannot be cancelled once sent |
| Israel Police: file a complaint (official service) | https://www.gov.il/he/service/request-file-complaint-online-during-emergency | The subject list including `עבירת רכוש והונאה`, and that emergencies go to 100 |
| Kol-Zchut: online police complaint (procedure) | https://www.kolzchut.org.il/he/בקשה_להגשת_תלונה_במשטרה_דרך_האינטרנט | That the online form is a request, not an official complaint until police complete it |
| National Cyber Directorate | https://www.gov.il/he/service/cyber-event-report | Report phishing links and cyber incidents |

## Gotchas

- **Never invent a price.** Agents confidently state "a used X goes for Y shekel" from memory. Second-hand prices are local and volatile. Always derive the band from comparable ACTIVE Yad2 listings the user pulls, and present it as a range with a method, not a fact.
- **A bank-transfer screenshot is not a payment.** Agents (and sellers) treat a transfer confirmation image as proof. It is trivially forged and is the core of the Yad2 seller scam. Only the seller's own account balance proves payment.
- **Do not promise a private buyer a return/cancellation right.** The Consumer Protection Law 14-day cooling-off applies to business sellers (עוסק), not to a private person selling a used item. Telling a Yad2 buyer they can return it within 14 days is wrong and creates disputes.
- **A courier never needs YOU to pay to send money TO you.** Any "pay the shipping company / pay this link to receive your credit" framing is a scam, full stop. This is counter-intuitive enough that people fall for it.
- **Do not treat all payment apps as equal, and do not confuse a payment with a payment request.** Cash, Bit, and PayBox are good to RECEIVE (instant, effectively final once confirmed); a bank-transfer screenshot at the meeting is NOT cleared money. A "payment request" (בקשת תשלום) approved by the user sends THEIR money out, the reverse of getting paid.
- **The buyer's biggest risk is the deposit scam, not the GLS scam.** When the user is buying, the dominant fraud is paying a מקדמה to "hold" a fake listing. Do not give a buyer only the seller-side shipping warning.
- **Keep negotiation messages short and Hebrew-native.** Long, formal, translated-sounding messages read as bot or scam. Israeli haggling is brief, direct, and friendly.

## Troubleshooting

### Error: "I gave the buyer a price but it's much lower/higher than other listings"
Cause: priced from memory instead of comparables.
Solution: pull 3 to 5 active comparable Yad2 listings for the same model/condition first, then set the band.

### Error: "The buyer's bank transfer 'went through' but the money isn't in my account"
Cause: forged transfer screenshot, a known scam.
Solution: do not hand over the item. Payment is real only when it shows in your own bank balance. Treat the screenshot as a red flag and stop the deal.

### Error: "Is it safe to ship the item to a buyer I haven't met?"
Cause: shipping + pre-payment is the highest-risk pattern on Yad2.
Solution: prefer in-person handover with cash or a recognized payment app. If shipping is unavoidable, never pay any courier yourself and never enter card details in a link the buyer sends.
