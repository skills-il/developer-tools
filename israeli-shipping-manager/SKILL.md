---
name: israeli-shipping-manager
description: Build and manage shipping integrations with Israeli carriers, including Israel Post, Cheetah, HFD, Mahir Li, GetPackage, and UPS Israel, plus locker pickup services (Shlager, Done, UPS lockers). Use when user asks about "shipping Israel", "Cheetah delivery", "meshloach", "shipping label", "HFD", "locker pickup Israel", "tawit mishloach", "GetPackage", "UPS lockers Israel", or setting up carrier integrations for an e-commerce store. Covers carrier selection, Israeli address formatting, label generation, cross-carrier tracking system setup, customer delivery notifications, and 14-day consumer-protection returns. Do NOT use for looking up a specific package tracking status (direct the user to the carrier site, Israel Post at doar.israelpost.co.il or HFD at hfd.co.il). Do NOT use for international shipping outside Israel or customs/import (see israeli-customs-duty-calculator for the personal-import USD 75 VAT threshold).
license: MIT
allowed-tools: Bash(python3:*) WebFetch
compatibility: Works with Claude Code, OpenClaw, Cursor. OpenClaw recommended for automated tracking updates and customer WhatsApp/SMS notifications.
---


# Israeli Shipping Manager

## Instructions

**CRITICAL: This skill is a developer integration guide for BUILDING shipping workflows. You CANNOT look up live package tracking status. If a user asks "where is my package" or gives you a tracking number to check, you MUST:**
1. **Direct them to check on the carrier's official website** (Israel Post at israelpost.co.il, HFD at hfd.co.il, Cheetah at chitadelivery-cx.com)
2. **NEVER fabricate or guess package status, pickup location, delivery address, branch name, opening hours, or any other tracking detail.** You do not have access to any carrier's tracking system.
3. **If the user needs automated tracking**, guide them to set up a tracking integration (Step 4 below) or recommend the `israel-post-tracking` community skill for Israel Post packages.

### Step 1: Select Carrier Based on Shipment
Help the user choose the right carrier for their shipment. Ask about parcel size, weight, delivery urgency, destination, and budget. Use this comparison table:

| Carrier | Best For | Speed | Price Range | Pickup Points | Integration |
|---------|----------|-------|-------------|---------------|-------------|
| Israel Post (דואר ישראל) | Standard parcels, nationwide coverage | 3-5 business days | Low-medium | Post office branches | Datalogics API, open-source libraries |
| Cheetah (צ'יטה) | Same-day/express delivery | Same day (often within 4 hours) | Medium-high | Cheetah Shops, 35 storefronts + 1,300+ points | Shopify app, private B2B API |
| HFD (Hameritz & Flash) | E-commerce fulfillment | 2-4 business days | Medium | ~1,000 pickup points + lockers | Shopify/WooCommerce plugins, private API |
| Mahir Li (מהיר לי) | Same-day B2B courier | Same day (within 9 hours) | Medium-high | Door-to-door only | Via LionWheel platform |
| UPS Israel (locker drop-off) | Small parcels, one package up to 8 kg | 1-2 business days | 27.02 NIS incl. VAT to a pickup point, plus remote-zone surcharge (Aug 2026 price list) | Locker and service-store network (launched early 2025) | UPS Developer Kit + locker QR-code drop-off |
| GetPackage (גט פקג'/getpackage.com) | Crowdsourced same-day courier | Same day (often 1-3 hours) | Variable (bid-based) | Door-to-door only | Web platform + REST API (B2B account) |

Additional courier companies use Baldar delivery management software (Tapuz, Hafoz, Isgav, Mach1). If a user mentions "Baldar," ask which specific courier company they use, as Baldar is software, not a carrier.

Locker/pickup services (not standalone carriers):

| Service | Operator | Locations | Notes |
|---------|----------|-----------|-------|
| Shlager | Orian | Mobile smart lockers in residential areas | Automated locker network |
| Done | Done (done.co.il) | Lockers at various locations | 30 NIS/package, max 5 kg (transit time not published, ask Done) |
| HFD Points | HFD | ~1,000 nationwide | Part of HFD delivery network |
| UPS Lockers Israel | UPS franchisee (Israel), ordered via the easyship site | Locker and service-store network | 24/7 drop-off and pickup, 27.02 NIS incl. VAT per package to a pickup point, remote-zone surcharge applies |

Selection criteria:
- **Delivery speed:** Same-day requires Cheetah, Mahir Li, or GetPackage; UPS Israel is 1-2 business days; standard allows all carriers
- **Parcel size/weight:** Heavy or oversized items may limit carrier options. The caps differ per service and are easy to conflate. Done lockers take up to 5 kg. The UPS Israel **pickup-point/locker** service takes **one package of at most 8 kg** chargeable weight; its **home-delivery** scale runs to 15 kg. Chargeable weight is the greater of actual weight and volumetric weight, where volumetric weight is length x width x height in cm divided by 5000.
- **Destination area:** Center (Gush Dan) has full coverage; periphery (Eilat, Galilee) may have limited options for some carriers
- **Budget:** Israel Post is cheapest for standard; UPS Israel is 27.02 NIS incl. VAT pickup-point to pickup-point, but that rate is not flat nationwide (see the remote-zone surcharge in the Gotchas); Cheetah and Mahir Li are premium for speed
- **Pickup vs door-to-door:** HFD points (~1,000), Cheetah Shops (35 branches and 1,300+ distribution points, the largest of the networks here), Done and UPS lockers for self-service drop-off and pickup. Mahir Li and GetPackage are door-to-door only. Do not assume Cheetah is express-only, its pickup network is bigger than HFD's.
- **Volume:** Mahir Li requires minimum 10 deliveries/day; Israel Post, HFD, UPS Israel, and GetPackage have no minimums

### Step 2: Format Israeli Address
Format addresses correctly per carrier requirements. The validator needs the address fields on the command line, so run it as `python3 scripts/format_address.py --validate --street "הרצל" --house 42 --city "תל אביב-יפו" --mikud 6120001`, or pass a whole address with `--json address.json`. Running it with no fields prints usage and exits 1. See references/address-format.md for the complete format specification.

Required fields:
- **Street name (שם רחוב)** -- in Hebrew
- **House number (מספר בית)**
- **Apartment number (דירה)** -- if applicable
- **Entrance (כניסה)** -- if applicable (common in older buildings)
- **Floor (קומה)** -- if applicable
- **City (עיר)** -- in Hebrew
- **Mikud/ZIP (מיקוד)** -- 7 digits

Special handling:
- **Military addresses (APO):** Use IDF address format (`--type military --military-code NNNNN`). IDF unit postal codes begin with the digit 0. Only Israel Post handles military mail.
- **Kibbutzim/Moshavim:** Settlement name + house number, no street (`--type kibbutz --settlement "..." --house N`)
- **Localities with no street names:** recognised Bedouin localities in the Negev, parts of East Jerusalem, and newly-occupied neighbourhoods are addressed by neighbourhood or cluster plus house number, with no street at all (`--type no_street --neighbourhood "..." --house N`). Most carriers will additionally want a recipient phone number and a map pin for these.
- **Industrial zones:** Zone name + building/company name. The zone name goes in `--street`, not `--settlement` (`--type industrial --street "אזור תעשייה הר טוב" --building 8 --city "בית שמש" --mikud 9906000`)
- **Arab localities:** Verify transliteration matches carrier database

### Step 3: Generate Shipping Label
Label generation depends on the carrier's integration method:

- **Israel Post:** Use the Datalogics API (`connect.datalogics.co.il/rest/w_create_shipping`) or the Israel Post Business Portal (mybusiness.israelpost.co.il). Mikud lookup now lives at `doar.israelpost.co.il/locatezip`.
- **Cheetah:** Use the "Cheetah DeliverIt" Shopify app, or contact Cheetah sales for direct integration
- **HFD:** Use the "HFD DeliverIt" Shopify app or the "HFD ePost Integration" WooCommerce plugin. HFD also offers a private API for direct integration (contact HFD).
- **Mahir Li:** Integration via LionWheel platform (lionwheel.com). Contact Mahir Li for business account setup.
- **UPS Israel:** Use the UPS Developer Kit (developer.ups.com) for label generation, rate calculation, and tracking. For locker drop-off flows, generate a label and present the QR code at any UPS locker (24/7). The Israeli domestic price list applies only to shipments ordered through the local easyship site, so confirm which rate card the account is on before quoting.
- **GetPackage:** Use the GetPackage business platform (getpackage.com). For high-volume integrations, request REST API access via their business team.

All labels require:
- Sender details (name, address, phone)
- Recipient details (name, address, phone)
- Parcel dimensions and weight
- Service type (standard, express, registered)
- Tracking barcode

See references/carrier-apis.md for per-carrier integration details.

### Step 4: Set Up Cross-Carrier Tracking

**Important:** This step is about BUILDING a tracking system for your application, not about looking up individual package statuses. If the user wants to check a specific package right now, direct them to the carrier's website (see the critical note at the top of Instructions).

No Israeli carrier offers a public REST tracking API. Implement unified tracking using one of these approaches:

**Option A: Third-party aggregator (recommended)**
Use AfterShip, TrackingMore, or ClickPost for unified tracking across carriers. These provide documented REST APIs with webhooks. Do NOT reach for "WeShip" here, weship.com is a Mexican logistics platform with no Israeli carrier coverage.

**Option B: Direct integration per carrier**
- Israel Post: the whole `israelpost.co.il` estate (including `mypost.` and `doar.`) sits behind Radware Bot Manager, so scraping is not a dependable path. Prefer a third-party aggregator. `bennymeg/IsraelPostalServiceAPI` still exists but is unmaintained (last commit March 2023), so treat it as a starting point, not a dependency.
- HFD: Track via hfd.co.il or AfterShip
- Cheetah: customers track at `chitadelivery-cx.com/login`. `chita-il.com` is the RunCom business-customer login, not a consumer tracking page, so never send an end user there
- Mahir Li: Track via LionWheel

Normalize status codes to a common set: `pending`, `picked_up`, `in_transit`, `out_for_delivery`, `delivered`, `failed_delivery`, `returned`

Poll at configurable intervals (default: every 2 hours). Detect anomalies: package stuck in same status for >48 hours, delivery failures, address corrections.

### Step 5: Configure Customer Notifications
Set up automated customer notifications on status changes. For Hebrew SMS to Israeli numbers, use a local gateway (019/Telzar, Cellact, InforuMobile, SMS4Free) rather than Twilio. Hebrew SMS is limited to 70 characters per segment (vs 160 for Latin), and local providers handle Israeli carrier routing more reliably. See the `israeli-sms-gateway` skill for SMS-specific integration.

Notifications by status:
- **Shipped:** WhatsApp/SMS with tracking number and estimated delivery -- "החבילה שלך נשלחה! מספר מעקב: [X]. צפי הגעה: [DATE]."
- **Out for delivery:** "החבילה שלך בדרך אליך! צפי הגעה היום עד [TIME]."
- **Delivered:** "החבילה נמסרה בהצלחה! תודה על הקנייה."
- **Failed delivery:** "לא הצלחנו למסור את החבילה. נסיון נוסף מתוכנן ל-[DATE]. לתיאום: [PHONE]."
- **Pickup ready:** "החבילה שלך מחכה לך בנקודת [HFD/Done/UPS] ב-[LOCATION]. קוד איסוף: [CODE]."

Respect quiet hours: no notifications between 22:00-08:00 Israel time.

### Step 6: Handle Returns and RMA
A distance sale (online or phone) gives the buyer a right under **חוק הגנת הצרכן sections 14ג, 14ג1, 14ה and 14ט**. תקנות הגנת הצרכן (ביטול עסקה) התשע"א-2010, made under section 14ו, are a **separate and parallel** statutory right, not a rival regime that switches off when the sale is remote. They are simply less generous: the same 14-day window for goods, but the goods must be unused and undamaged and must be physically returned, and a longer exclusion list applies. A buyer in a distance sale will therefore rely on 14ג. Keep the two apart in your code, because the exclusion lists differ and mixing them is the most common way an RMA flow ends up unlawful. Section 14ט(ז) makes the split explicit: the notice rules in Step 6g do not apply to a 14ו return.

**Step 6a: Determine the cancellation window.**
- **Standard:** section 14ג(ג)(1) gives the buyer from the moment of the transaction until 14 days from receiving the goods, or from receiving the disclosure document, **whichever is later**. Do not start the clock at the order date.
- **Four-month window:** section 14ג1(ג) gives a buyer who is a person with a disability, an אזרח ותיק (65 or over), or an עולה חדש (within five years of their עולה certificate) **four months**, on the same "whichever is later" basis, **provided the contracting of THIS transaction included a conversation between seller and buyer, including a conversation by electronic communication**. Read that condition narrowly: a support widget the buyer never used on this order does not satisfy it, and the mere presence of live chat on the site is not itself the conversation. Under section 14ג1(ד) the seller may require ONE identifying document and may not demand any further proof. An עולה חדש qualifies on either a תעודת עולה **or** a תעודת זכאות כעולה from משרד העלייה והקליטה, so do not build an intake that accepts only the first.
- An RMA system that hardcodes 14 days will auto-reject lawful cancellations. Model the window as a function of buyer status, not a constant.

**Step 6b: Branch the return logistics on the REASON, because the statute does.**
- **Defect, mismatch, late delivery, or any other breach by the seller** (section 14ה(א)(2)): the buyer only has to **make the goods available at the address where they were delivered** and notify the seller. Collection is the seller's job. Do NOT send this buyer a drop-off label.
- **Changed mind** (section 14ה(ב)(2)): the buyer returns the goods **to the seller's place of business**. A prepaid drop-off label is a courtesy here, not a duty.

**Step 6c: Refund on the statutory clock.**
- Under BOTH section 14ה(א)(1) and section 14ה(ב)(1) the seller refunds **within 14 days of receiving the cancellation notice**. The trigger is the notice, not the arrival of the parcel. A flow that waits for the goods to come back before starting a clock will routinely miss the deadline.
- The seller cancels the charge and gives the buyer a copy of the charge-cancellation notice.

**Step 6d: Fees, and what the cap swallows.**
- Seller breach (14ה(א)(1)): **no cancellation fee at all**.
- Changed mind (14ה(ב)(1)): at most **5% of the price or 100 NIS, whichever is lower**. Note that section 14ג(ו) defines "מחיר הנכס" as the total price **including delivery charges**. That definition opens "בסעיף זה", so applying it to the 14ה(ב)(1) cap is a consumer-protective inference rather than an express cross-reference. In practice the 100 NIS leg usually binds first.
- Section 14ה(ד) defines דמי ביטול as **including shipping and packing costs**. The seller therefore cannot deduct the original outbound shipping on top of the cap; it is inside it. This is the single most common Israeli e-commerce refund error.
- Section 14ה(ב2): where the seller **installed goods in the buyer's home in order to provide the service under the transaction**, installation costs may be recovered up to 100 NIS. It is not a general installation-cost recovery for any goods sale.
- Section 14ה(ג): none of this removes the seller's right to sue for a significant deterioration in the goods' value.

**Step 6e: Exclusions are a closed list of five for a distance sale** (section 14ג(ד)). The right to cancel does not apply to:
1. Perishable goods (טובין פסידים)
2. Hospitality, travel, leisure or entertainment services, where cancellation falls within 7 non-rest days before the service is due
3. Information as defined in חוק המחשבים התשנ"ה-1995
4. Goods manufactured specially for the buyer as a result of the transaction
5. Recordable or reproducible goods whose original packaging the buyer opened

Undergarments, swimwear and assembled furniture are **NOT** on this list. They are excluded under the separate 2010 in-store regulations. Telling a seller to refuse an online swimwear cancellation is telling them to break the law.

**Step 6g: Build the notice INTAKE, because section 14ט mandates its shape.**

Steps 6a-6f all hang off "the cancellation notice", and section 14ט dictates how that notice must be receivable. It is the most build-relevant provision in the chapter, because it dictates UI and queue behaviour rather than policy. In short: you must accept a notice orally, by registered mail, by email, by fax if you have one, and over the internet for anything contractable online; you must put a **dedicated cancellation link on your homepage**, prominently; and the notice may require only the buyer's name and ID number, so an intake form gating cancellation behind an order number or a reason code is over-collecting. See `references/returns-law.md` for the full text of 14ט(א)-(ז), the disclosure duties, and the one narrow statutory-damages route that actually attaches to it.

**Step 6f: Operational bits.**
- Generate the return label with the original tracking reference and track the return leg back to the seller.
- Calculate return shipping cost by carrier. UPS pickup-point drop-off is often the cheapest path for a small parcel at 27.02 NIS incl. VAT, but it accepts **one package of at most 8 kg**, and the remote-zone surcharge applies to periphery addresses (see Gotchas).
- Update order status when the return is received.

## Examples

### Example 1: E-commerce Seller Shipping 50 Packages via Mixed Carriers
User says: "I need to ship 50 orders today, mix of sizes. Some need next-day to Tel Aviv, rest are standard nationwide."
Actions:
1. Analyze orders by size, destination, and urgency
2. Route express Tel Aviv orders to Cheetah via their Shopify app (12 parcels)
3. Route standard parcels to Israel Post or HFD (38 parcels) based on cost and plugin availability
4. Format all addresses and validate mikud codes using `scripts/format_address.py`
5. Generate shipping labels per carrier integration method
6. Set up unified tracking via AfterShip and configure WhatsApp notifications
Result: 50 shipping labels generated across 3 carriers. Tracking dashboard set up with WhatsApp notifications configured for each customer.

### Example 2: Setting Up HFD Pickup Point Integration for a Shopify Store
User says: "I want to offer HFD pickup point as an option for my online store on Shopify."
Actions:
1. Install "HFD DeliverIt" app from the Shopify App Store
2. Configure HFD business account credentials in the app
3. Enable HFD pickup points as a shipping option at checkout
4. Set up tracking notifications: customers get SMS when package arrives at pickup point
5. Configure auto-tracking from shipment to customer pickup
Result: HFD integration active. Customers can select from ~1,000 HFD pickup points at checkout and receive pickup notifications.

### Example 3: Rate Comparison for Heavy Parcel to Eilat
User says: "I need to ship a 15kg package to Eilat, what are my options?"
Actions:
1. Check carrier availability for Eilat (periphery area)
2. Get an Israel Post rate. Their rate-calculator endpoint now returns 403 to a plain request (it sits inside the same Radware perimeter as tracking), and the `bennymeg/IsraelPostalServiceAPI` library that wraps it is unmaintained since March 2023, so treat this as a browser or carrier-account path rather than an automatable one
3. Contact HFD for a rate quote (no public rate API)
4. Note: Mahir Li requires 10+ daily deliveries, likely not suitable for single parcels
5. Cheetah serves Eilat (branch there) but at premium pricing
6. Note that Eilat is a remote zone for UPS Israel, so the pickup-point rate carries a per-weight-band surcharge and is not the 27.02 NIS headline price. A 15 kg parcel is over the 8 kg pickup-point cap anyway, so this is a home-delivery quote
7. Compare delivery times and costs
Result: Israel Post is the most accessible option with public rate calculation. For better rates on volume, contact HFD directly.

## Bundled Resources

### References
- `references/carrier-apis.md` -- Verified integration methods for each Israeli carrier: Israel Post (Datalogics API, open-source libraries), Cheetah (Shopify app, RUN system), HFD (Shopify/WooCommerce plugins), Mahir Li (LionWheel), locker services, and third-party aggregators. Consult when integrating with a specific carrier in Steps 3-4.
- `references/returns-law.md` -- The statutory detail behind Step 6: the two parallel return regimes and why the exclusion lists differ, the full five-item 14ג(ד) list, section 14ט's notice channels and homepage-link duty in full, the refund and fee mechanics per sub-section, the four-month 14ג1 window and its two easily-missed conditions, and the one narrow statutory-damages route. Consult when building an RMA flow in Step 6.
- `references/address-format.md` -- Complete Israeli address formatting specification: street, house, apartment, entrance, floor, city, mikud. Includes special formats for kibbutzim, military addresses, and industrial zones. Consult when formatting addresses in Step 2.

### Scripts
- `scripts/format_address.py` -- Validates and formats Israeli shipping addresses per carrier requirements. Checks mikud (ZIP) validity, normalizes Hebrew text, and handles special address types (kibbutz, military, industrial zone). Run: `python3 scripts/format_address.py --help`

## Related Skills

For live Israel Post package tracking, use the **israel-post-tracking** skill:

| Skill | What it does | Link |
|-------|-------------|------|
| **Israel Post Tracking** | Track packages via Israel Post using Puppeteer with headless Chrome. One-shot status lookup or ongoing monitoring with WhatsApp notifications on status changes. Requires Google Chrome installed. | [View skill](https://agentskills.co.il/en/skills/government-services/israel-post-tracking) |

This shipping-manager skill is a **developer integration guide** for building shipping workflows. It does NOT track packages. If a user asks "where is my package?", either use the `israel-post-tracking` skill (if installed) or direct them to the carrier's official website. NEVER fabricate package status, pickup location, or delivery information.

## Gotchas

- **NEVER fabricate package tracking results.** You cannot access any carrier's tracking system. If a user provides a tracking number and asks "where is my package," do NOT invent a status, pickup location, branch name, address, or opening hours. Agents that fabricate tracking data provide dangerously wrong information (e.g., telling a user their package is at a specific store when it was already delivered to a different city). Always direct the user to the carrier's official tracking page.
- Israeli carriers do not offer publicly documented REST APIs. Integration is done through platform plugins (Shopify, WooCommerce), private B2B agreements, or third-party aggregators. Agents may attempt to call fabricated API endpoints that do not exist.
- Israel Post delivery zones differ from geographic regions. Shipping time estimates should use Israel Post zone mappings, not straight-line distance calculations.
- Israeli addresses do not use ZIP codes in the US format. Israeli postal codes (mikud) are 7 digits. Agents may validate against 5-digit US ZIP code patterns.
- Friday deliveries in Israel end by early afternoon (before Shabbat). Same-day delivery services do not operate Friday afternoon through Saturday evening.
- Israeli settlement addresses in the West Bank require special shipping handling and may not be supported by all carriers. Verify carrier coverage for these areas.
- COD (cash on delivery) is still common in Israeli e-commerce. Agents may not include this payment option when setting up shipping flows.
- **BOX2GO is discontinued and has been since 2021.** Israel Post ended the Yellow Box locker partnership with Paz: parcels ordered to a BOX2GO locker after 30/09/2021 were delivered to the street address instead, and mail addressed to a Box2Go point after 15/11/2021 was returned to sender. The service still appears widely in older documentation and in model training data, so an agent will happily offer it as a live pickup option. It is not one. Use HFD points, Done, or UPS lockers instead.
- **The Israel Post open-source libraries are cold, and one of them is dead.** `bennymeg/IsraelPostalServiceAPI` last shipped a commit in March 2023 and `Stajor/israel-post` in September 2020. `LandRover/postil-status` is worse than stale: it targets `postil.com`, a domain that no longer resolves at all, so it cannot work under any configuration. Treat all three as reference implementations to read, never as a dependency to install.
- **"WeShip" is not an Israeli platform.** `weship.com` is a Mexican logistics company. There is no Israeli WeShip carrier integration behind that name, so an agent that recommends it sends the user to the wrong country.
- Baldar is delivery management software, not a carrier. If a user says "I ship with Baldar," they mean a courier that uses Baldar (Tapuz, Hafoz, Isgav, Mach1). Ask which carrier specifically.
- Israel Post's website uses Radware Bot Manager. Automated scraping of tracking or rate data is blocked in practice, not merely "may be" blocked: a plain request to any host in the estate is answered by a `validate.perfdrive.com` challenge. Use a third-party aggregator or the Datalogics API instead. (Older write-ups attribute this to ShieldSquare/PerimeterX; the challenge served today is Radware's.)
- **Personal-import VAT threshold is USD 75, and it moved three times in six months.** It was raised to USD 150 by ministerial order, cut back to USD 75 by a Knesset vote in February 2026, re-raised to USD 130 by a further ministerial order, and then returned to USD 75 when the Knesset revoked that order 59-23 on 2 June 2026. Orders above USD 75 (goods value, excluding shipping and insurance) attract 18% VAT and possible customs duty. Any figure you remember from training data for this threshold is probably one of the superseded ones, so re-check before quoting it. If a user asks about cross-border shipping cost or customs, refer them to the `israeli-customs-duty-calculator` skill (this skill is domestic-only).
- **Every UPS Israel figure in this skill is from a price list valid for ONE MONTH.** The operator's price list closes with "מחירון זה תקף לחודש אוגוסט 2026 בלבד". Re-read site.ship.co.il before quoting any of these numbers, and tell the user the month you read. The figures below are the August 2026 list.
- **The UPS Israel pickup-point price is not flat nationwide.** The published price is 22.9 NIS before VAT (27.02 NIS incl. VAT) to a pickup point, but a shipment from or to zone 3 adds 18 NIS before VAT (21.24 NIS incl. VAT) per weight band, and zone 5 adds 28 NIS before VAT (33.04 NIS incl. VAT) per weight band. Agents that quote a single national price will under-quote every periphery address. Home delivery is a separate and much higher scale, 46.5 NIS before VAT up to 5 kg, 48.5 NIS up to 10 kg, and 63.5 NIS up to 15 kg. The network launched in early 2025, so older shipping documentation will not mention it at all, and it is not the same as UPS's international express service.
- **The pickup-point service and the home-delivery service have different caps, and conflating them quotes a service that will refuse the parcel.** Pickup point or locker takes ONE package of at most 8 kg chargeable. Home delivery runs to 15 kg and allows multi-parcel shipments, where chargeable weight is the SUM across packages, rounded up to the whole kilogram.
- **Uncollected parcels bounce fast, and the locker window is 48 hours.** An uncollected shipment returns to the sender after 5 business days at a service store, or **48 hours at a locker**. Design the pickup-ready reminder cadence around 48 hours, not around a week. A failed pickup attempt at the sender costs 15 NIS before VAT, and return-to-sender is charged at the full destination tariff.
- **Gated and restricted-access destinations are excluded and expensive.** The service does not cover destinations requiring pre-arranged entry approval, nor post office branches or embassies. The carrier may return the shipment at the sender's expense or charge 200 NIS before VAT for special distribution. This bites on military bases, secure campuses and some kibbutz gates, which is exactly where the skill's special address formats point.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Israel Post mikud lookup | https://doar.israelpost.co.il/locatezip | Current 7-digit mikud for an address. This is where the old mypost.israelpost.co.il/zipcodesearch URL now lands |
| Israel Post Datalogics integration | https://israel-post.datalogics.co.il/ | Domestic shipping and store-lookup endpoints, and whether the token flow has changed |
| HFD pickup points | https://www.hfd.co.il/en/pick-up-points/ | Current pickup-point and locker count |
| Cheetah shipment tracking | https://chitadelivery-cx.com/login | The consumer tracking entry point (chitadelivery.co.il is the marketing site) |
| UPS Israel domestic price list | https://site.ship.co.il/ | Current pickup-point and home-delivery rates, weight bands, and the zone 3 / zone 5 remote surcharges |
| Consumer cancellation regulations | https://www.gov.il/he/departments/the_consumer_protection_and_fair_trade_authority | The current excluded-goods list, the cancellation-fee cap, and the refund deadline |
| LionWheel API | https://github.com/lionwheel/api | The Mahir Li integration path, and the only actively maintained library in this skill |

## Troubleshooting

### Error: "Invalid mikud (ZIP code)"
Cause: Israeli mikud must be exactly 7 digits. **The bundled validator checks the SHAPE only.** It has no locality index and no street index, so it cannot tell you a well-formed mikud belongs to the city you paired it with. A VALIDATION PASSED result means "this is a plausible 7-digit code", never "this address is correct".
Solution: Verify mikud at Israel Post's mikud lookup, which now lives at `doar.israelpost.co.il/locatezip` (the older `mypost.israelpost.co.il/zipcodesearch` redirects there). Common issue: old 5-digit codes, all Israeli mikud codes are now 7 digits. Second common issue: a validator that hardcodes a region-prefix range and rejects Jerusalem, whose codes begin with 9.

### Error: "Carrier API endpoint not found" or "404 on API call"
Cause: Israeli carriers do not have publicly documented REST APIs. The endpoint you are calling likely does not exist.
Solution: Check references/carrier-apis.md for the correct integration method. Use platform plugins (Shopify, WooCommerce), the Datalogics API for Israel Post, or a third-party aggregator (AfterShip, TrackingMore, ClickPost).

### Error: "Address not recognized by carrier"
Cause: Address format doesn't match carrier's database, or Hebrew text encoding issue.
Solution: Ensure the address uses UTF-8 encoded Hebrew. Run `python3 scripts/format_address.py --validate` with the address fields to check the shape. Note that the script accepts ANY string as a city, so it will report VALIDATION PASSED for a misspelled or non-existent locality; it cannot settle a spelling dispute. For Arab localities, check the spelling against the carrier's own locality list and try alternative transliterations.

### Error: "Delivery failed -- recipient not found"
Cause: Common for apartment buildings without intercom or missing entrance/floor details.
Solution: Add entrance (כניסה) and floor (קומה) to address. Configure delivery notification to include recipient phone for courier contact. Consider switching to a pickup point (HFD, Done, or a UPS locker) for repeat-failure addresses.

### Error: "Tracking data not updating"
Cause: the `israelpost.co.il` estate is behind Radware Bot Manager, which intercepts automated requests before they reach the tracking endpoint. Verified: a plain request to `mypost.israelpost.co.il` or `doar.israelpost.co.il` is answered by a bot-manager challenge, not by the application.
Solution: use a third-party aggregator (AfterShip, TrackingMore, ClickPost) rather than scraping. Do NOT reach for `LandRover/postil-status`, its target domain `postil.com` no longer resolves, so it cannot work.

### User asks: "Where is my package?" or provides a tracking number
Cause: The user wants a live status lookup, not a shipping integration guide.
Solution: This skill cannot look up live tracking data. Direct the user to the carrier's official tracking page: Israel Post (israelpost.co.il), HFD (hfd.co.il), or Cheetah (chitadelivery-cx.com/login). For automated Israel Post tracking, recommend the `israel-post-tracking` community skill. NEVER guess or fabricate the package status.
