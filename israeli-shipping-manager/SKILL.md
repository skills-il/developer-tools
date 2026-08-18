---
name: israeli-shipping-manager
description: Build and manage shipping integrations with Israeli carriers, including Israel Post, Cheetah, HFD, Mahir Li, GetPackage, and UPS Israel, plus locker pickup services (BOX2GO, Shlager, Done, UPS lockers). Use when user asks about "shipping Israel", "Cheetah delivery", "meshloach", "shipping label", "HFD", "locker pickup Israel", "tawit mishloach", "GetPackage", "UPS lockers Israel", or setting up carrier integrations for an e-commerce store. Covers carrier selection, Israeli address formatting, label generation, cross-carrier tracking system setup, customer delivery notifications, and 14-day consumer-protection returns. Do NOT use for looking up a specific package tracking status (direct the user to mypost.israelpost.co.il or hfd.co.il instead). Do NOT use for international shipping outside Israel or customs/import (see israeli-customs-duty-calculator for the personal-import USD 130 VAT threshold).
license: MIT
allowed-tools: Bash(python:*) WebFetch
compatibility: Works with Claude Code, OpenClaw, Cursor. OpenClaw recommended for automated tracking updates and customer WhatsApp/SMS notifications.
---


# Israeli Shipping Manager

## Instructions

**CRITICAL: This skill is a developer integration guide for BUILDING shipping workflows. You CANNOT look up live package tracking status. If a user asks "where is my package" or gives you a tracking number to check, you MUST:**
1. **Direct them to check on the carrier's official website** (Israel Post: mypost.israelpost.co.il, HFD: hfd.co.il, Cheetah: chita-il.com)
2. **NEVER fabricate or guess package status, pickup location, delivery address, branch name, opening hours, or any other tracking detail.** You do not have access to any carrier's tracking system.
3. **If the user needs automated tracking**, guide them to set up a tracking integration (Step 4 below) or recommend the `israel-post-tracking` community skill for Israel Post packages.

### Step 1: Select Carrier Based on Shipment
Help the user choose the right carrier for their shipment. Ask about parcel size, weight, delivery urgency, destination, and budget. Use this comparison table:

| Carrier | Best For | Speed | Price Range | Pickup Points | Integration |
|---------|----------|-------|-------------|---------------|-------------|
| Israel Post (דואר ישראל) | Standard parcels, nationwide coverage | 3-5 business days | Low-medium | Post offices + BOX2GO lockers | Datalogics API, open-source libraries |
| Cheetah (צ'יטה) | Same-day/express delivery | Same day (often within 4 hours) | Medium-high | Limited | Shopify app, private B2B API |
| HFD (Hameritz & Flash) | E-commerce fulfillment | 2-4 business days | Medium | ~1,000 pickup points + lockers | Shopify/WooCommerce plugins, private API |
| Mahir Li (מהיר לי) | Same-day B2B courier | Same day (within 9 hours) | Medium-high | Door-to-door only | Via LionWheel platform |
| UPS Israel (locker drop-off) | Small parcels, prepaid flat rate | 1-2 business days | ~27 NIS flat (incl. VAT) | 100 lockers + 150 service stores nationwide (launched March 2025) | UPS Developer Kit + locker QR-code drop-off |
| GetPackage (גט פקג'/getpackage.com) | Crowdsourced same-day courier | Same day (often 1-3 hours) | Variable (bid-based) | Door-to-door only | Web platform + REST API (B2B account) |

Additional courier companies use Baldar delivery management software (Tapuz, Hafoz, Isgav, Mach1). If a user mentions "Baldar," ask which specific courier company they use, as Baldar is software, not a carrier.

Locker/pickup services (not standalone carriers):

| Service | Operator | Locations | Notes |
|---------|----------|-----------|-------|
| BOX2GO | Israel Post + Paz | ~120 Yellow Box lockers at Paz gas stations | Integrated with Israel Post shipping |
| Shlager | Orian | Mobile smart lockers in residential areas | Automated locker network |
| Done | Done (done.co.il) | Lockers at various locations | ~30 NIS/package, max 5 kg, 3 business days |
| SafeLocker | SafeLocker | Malls and shopping centers | Locker-based pickup |
| HFD Points | HFD | ~1,000 nationwide | Part of HFD delivery network |
| UPS Lockers Israel | UPS franchisee (Israel) | 100 lockers + 150 service stores | 24/7 drop-off and pickup, ~27 NIS flat per package (launched March 2025) |

Selection criteria:
- **Delivery speed:** Same-day requires Cheetah, Mahir Li, or GetPackage; UPS Israel is 1-2 business days; standard allows all carriers
- **Parcel size/weight:** Heavy or oversized items may limit carrier options. Locker services have size limits (Done max 5 kg, UPS locker doors fit small parcels only).
- **Destination area:** Center (Gush Dan) has full coverage; periphery (Eilat, Galilee) may have limited options for some carriers
- **Budget:** Israel Post is cheapest for standard; UPS Israel offers a flat ~27 NIS locker-to-locker rate; Cheetah and Mahir Li are premium for speed
- **Pickup vs door-to-door:** BOX2GO/HFD/Done/UPS lockers for self-service drop-off and pickup; Cheetah/Mahir Li/GetPackage for guaranteed door delivery
- **Volume:** Mahir Li requires minimum 10 deliveries/day; Israel Post, HFD, UPS Israel, and GetPackage have no minimums

### Step 2: Format Israeli Address
Format addresses correctly per carrier requirements. Run `python scripts/format_address.py --validate` to check format before submission. See references/address-format.md for the complete format specification.

Required fields:
- **Street name (שם רחוב)** -- in Hebrew
- **House number (מספר בית)**
- **Apartment number (דירה)** -- if applicable
- **Entrance (כניסה)** -- if applicable (common in older buildings)
- **Floor (קומה)** -- if applicable
- **City (עיר)** -- in Hebrew
- **Mikud/ZIP (מיקוד)** -- 7 digits

Special handling:
- **Military addresses (APO):** Use IDF address format (מספר צבאי). Only Israel Post handles military mail.
- **Kibbutzim/Moshavim:** Settlement name + house number (no street)
- **Industrial zones:** Area name + building/company name
- **Arab localities:** Verify transliteration matches carrier database

### Step 3: Generate Shipping Label
Label generation depends on the carrier's integration method:

- **Israel Post:** Use the Datalogics API (`connect.datalogics.co.il/rest/w_create_shipping`) or the Israel Post Business Portal (mybusiness.israelpost.co.il)
- **Cheetah:** Use the "Cheetah DeliverIt" Shopify app, or contact Cheetah sales for direct integration
- **HFD:** Use the "HFD DeliverIt" Shopify app or the "HFD ePost Integration" WooCommerce plugin. HFD also offers a private API for direct integration (contact HFD).
- **Mahir Li:** Integration via LionWheel platform (lionwheel.com). Contact Mahir Li for business account setup.
- **UPS Israel:** Use the UPS Developer Kit (developer.ups.com) for label generation, rate calculation, and tracking. For locker drop-off flows, generate a label and present the QR code at any UPS locker (24/7). 100 lockers + 150 service stores nationwide.
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
Use AfterShip, TrackingMore, or WeShip for unified tracking across carriers. These provide documented REST APIs with webhooks.

**Option B: Direct integration per carrier**
- Israel Post: Scrape tracking via `mypost.israelpost.co.il` (requires CSRF token handling) or use open-source libraries (`bennymeg/IsraelPostalServiceAPI`, `LandRover/postil-status`)
- HFD: Track via hfd.co.il or AfterShip
- Cheetah: Track via the RUN system (chita-il.com) or the Shopify app
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
- **Pickup ready:** "החבילה שלך מחכה לך בנקודת [BOX2GO/HFD/Done] ב-[LOCATION]. קוד איסוף: [CODE]."

Respect quiet hours: no notifications between 22:00-08:00 Israel time.

### Step 6: Handle Returns and RMA
Manage return shipments under Israel's distance-selling rules (Israeli Consumer Protection Law, Distance Selling Regulations):
- Generate return label with original tracking reference
- Track return shipment back to seller
- Support different return reasons: defective, wrong item, changed mind. The buyer has 14 days from receipt to cancel a distance-selling transaction (online/phone purchase) without justification.
- **Refund deadline:** the seller must refund money in the same payment method used, within 7 business days from the date the return is received.
- **Cancellation fee:** for "changed mind" returns the seller may charge a cancellation fee of 5% of the purchase price OR 100 NIS, whichever is lower. NO cancellation fee is allowed if the item is defective, mis-described, late, or otherwise a breach of contract by the seller.
- **Exclusions:** the 14-day cancellation right does not apply to perishable goods, personalized items, undergarments, or furniture already assembled at the buyer's home.
- Calculate return shipping cost by carrier (UPS locker drop-off is often the cheapest return path for small parcels at ~27 NIS flat)
- Update order status when return is received

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
2. Use Israel Post rate calculator (public, no auth needed) via `bennymeg/IsraelPostalServiceAPI` library
3. Contact HFD for a rate quote (no public rate API)
4. Note: Mahir Li requires 10+ daily deliveries, likely not suitable for single parcels
5. Cheetah serves Eilat (branch there) but at premium pricing
6. Compare delivery times and costs
Result: Israel Post is the most accessible option with public rate calculation. For better rates on volume, contact HFD directly.

## Bundled Resources

### References
- `references/carrier-apis.md` -- Verified integration methods for each Israeli carrier: Israel Post (Datalogics API, open-source libraries), Cheetah (Shopify app, RUN system), HFD (Shopify/WooCommerce plugins), Mahir Li (LionWheel), locker services, and third-party aggregators. Consult when integrating with a specific carrier in Steps 3-4.
- `references/address-format.md` -- Complete Israeli address formatting specification: street, house, apartment, entrance, floor, city, mikud. Includes special formats for kibbutzim, military addresses, and industrial zones. Consult when formatting addresses in Step 2.

### Scripts
- `scripts/format_address.py` -- Validates and formats Israeli shipping addresses per carrier requirements. Checks mikud (ZIP) validity, normalizes Hebrew text, and handles special address types (kibbutz, military, industrial zone). Run: `python scripts/format_address.py --help`

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
- Baldar is delivery management software, not a carrier. If a user says "I ship with Baldar," they mean a courier that uses Baldar (Tapuz, Hafoz, Isgav, Mach1). Ask which carrier specifically.
- Israel Post's website uses bot protection (ShieldSquare/PerimeterX). Automated scraping of tracking or rate data may be blocked. Use the open-source libraries or Datalogics API instead.
- **Personal-import VAT threshold is USD 130, not USD 150.** The threshold was raised to USD 150 in 2025 and then walked back to USD 130 after retailer pushback. Orders at or above USD 130 (goods value, excluding shipping/insurance) attract 18% VAT and possible customs duty. If a user asks about cross-border shipping cost or customs, refer them to the `israeli-customs-duty-calculator` skill (this skill is domestic-only).
- **UPS Israel locker network is new (launched March 2025).** Older shipping documentation will not mention it. The network is 100 lockers + 150 service stores nationwide, flat ~27 NIS per package incl. VAT, 1-2 business days. It is not the same as UPS's international express service.

## Troubleshooting

### Error: "Invalid mikud (ZIP code)"
Cause: Israeli mikud must be exactly 7 digits and match the city/street combination.
Solution: Verify mikud at Israel Post's mikud lookup (mypost.israelpost.co.il/zipcodesearch). Common issue: old 5-digit codes -- all Israeli ZIP codes are now 7 digits.

### Error: "Carrier API endpoint not found" or "404 on API call"
Cause: Israeli carriers do not have publicly documented REST APIs. The endpoint you are calling likely does not exist.
Solution: Check references/carrier-apis.md for the correct integration method. Use platform plugins (Shopify, WooCommerce), the Datalogics API for Israel Post, or a third-party aggregator (AfterShip, WeShip).

### Error: "Address not recognized by carrier"
Cause: Address format doesn't match carrier's database, or Hebrew text encoding issue.
Solution: Ensure address uses UTF-8 encoded Hebrew. Run `scripts/format_address.py --validate` to check format. For Arab localities, verify the carrier accepts the specific spelling. Try alternative transliterations.

### Error: "Delivery failed -- recipient not found"
Cause: Common for apartment buildings without intercom or missing entrance/floor details.
Solution: Add entrance (כניסה) and floor (קומה) to address. Configure delivery notification to include recipient phone for courier contact. Consider switching to pickup point (HFD/BOX2GO) for repeat-failure addresses.

### Error: "Tracking data not updating"
Cause: Israel Post tracking endpoint requires CSRF token that expires. Bot protection may block automated requests.
Solution: Use the `LandRover/postil-status` or `bennymeg/IsraelPostalServiceAPI` open-source libraries which handle token refresh. Alternatively, use a third-party aggregator like AfterShip for reliable tracking.

### User asks: "Where is my package?" or provides a tracking number
Cause: The user wants a live status lookup, not a shipping integration guide.
Solution: This skill cannot look up live tracking data. Direct the user to the carrier's official tracking page: Israel Post (mypost.israelpost.co.il), HFD (hfd.co.il), or Cheetah (chita-il.com). For automated Israel Post tracking, recommend the `israel-post-tracking` community skill. NEVER guess or fabricate the package status.
