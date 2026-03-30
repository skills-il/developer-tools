---
name: israeli-shipping-manager
description: Manage shipping operations across Israeli carriers, including Israel Post, Cheetah, HFD, and Mahir Li, plus locker pickup services (BOX2GO, Shlager, Done). Use when user asks about "shipping Israel", "Israel Post tracking", "Cheetah delivery", "meshloach", "shipping label", "package tracking Israel", "HFD", "locker pickup Israel", or "tawit mishloach". Covers carrier selection, Israeli address formatting, label generation, cross-carrier tracking, and customer delivery notifications. Do NOT use for international shipping outside Israel or customs/import.
license: MIT
allowed-tools: Bash(python:*) WebFetch
compatibility: Works with Claude Code, OpenClaw, Cursor. OpenClaw recommended for automated tracking updates and customer WhatsApp/SMS notifications.
---


# Israeli Shipping Manager

## Instructions

### Step 1: Select Carrier Based on Shipment
Help the user choose the right carrier for their shipment. Ask about parcel size, weight, delivery urgency, destination, and budget. Use this comparison table:

| Carrier | Best For | Speed | Price Range | Pickup Points | Integration |
|---------|----------|-------|-------------|---------------|-------------|
| Israel Post (דואר ישראל) | Standard parcels, nationwide coverage | 3-5 business days | Low-medium | Post offices + BOX2GO lockers | Datalogics API, open-source libraries |
| Cheetah (צ'יטה) | Same-day/express delivery | Same day (often within 4 hours) | Medium-high | Limited | Shopify app, private B2B API |
| HFD (Hameritz & Flash) | E-commerce fulfillment | 2-4 business days | Medium | ~1,000 pickup points + lockers | Shopify/WooCommerce plugins, private API |
| Mahir Li (מהיר לי) | Same-day B2B courier | Same day (within 9 hours) | Medium-high | Door-to-door only | Via LionWheel platform |

Additional courier companies use Baldar delivery management software (Tapuz, Hafoz, Isgav, Mach1). If a user mentions "Baldar," ask which specific courier company they use, as Baldar is software, not a carrier.

Locker/pickup services (not standalone carriers):

| Service | Operator | Locations | Notes |
|---------|----------|-----------|-------|
| BOX2GO | Israel Post + Paz | ~120 Yellow Box lockers at Paz gas stations | Integrated with Israel Post shipping |
| Shlager | Orian | Mobile smart lockers in residential areas | Automated locker network |
| Done | Done (done.co.il) | Lockers at various locations | ~30 NIS/package, max 5 kg, 3 business days |
| SafeLocker | SafeLocker | Malls and shopping centers | Locker-based pickup |
| HFD Points | HFD | ~1,000 nationwide | Part of HFD delivery network |

Selection criteria:
- **Delivery speed:** Same-day requires Cheetah or Mahir Li; standard allows all carriers
- **Parcel size/weight:** Heavy or oversized items may limit carrier options. Locker services have size limits.
- **Destination area:** Center (Gush Dan) has full coverage; periphery (Eilat, Galilee) may have limited options for some carriers
- **Budget:** Israel Post is cheapest for standard; Cheetah and Mahir Li are premium for speed
- **Pickup vs door-to-door:** BOX2GO/HFD/Done for self-service pickup; Cheetah/Mahir Li for guaranteed door delivery
- **Volume:** Mahir Li requires minimum 10 deliveries/day; Israel Post and HFD have no minimums

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

All labels require:
- Sender details (name, address, phone)
- Recipient details (name, address, phone)
- Parcel dimensions and weight
- Service type (standard, express, registered)
- Tracking barcode

See references/carrier-apis.md for per-carrier integration details.

### Step 4: Set Up Cross-Carrier Tracking
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
Set up automated customer notifications on status changes:
- **Shipped:** WhatsApp/SMS with tracking number and estimated delivery -- "החבילה שלך נשלחה! מספר מעקב: [X]. צפי הגעה: [DATE]."
- **Out for delivery:** "החבילה שלך בדרך אליך! צפי הגעה היום עד [TIME]."
- **Delivered:** "החבילה נמסרה בהצלחה! תודה על הקנייה."
- **Failed delivery:** "לא הצלחנו למסור את החבילה. נסיון נוסף מתוכנן ל-[DATE]. לתיאום: [PHONE]."
- **Pickup ready:** "החבילה שלך מחכה לך בנקודת [BOX2GO/HFD/Done] ב-[LOCATION]. קוד איסוף: [CODE]."

Respect quiet hours: no notifications between 22:00-08:00 Israel time.

### Step 6: Handle Returns and RMA
Manage return shipments:
- Generate return label with original tracking reference
- Track return shipment back to seller
- Support different return reasons: defective, wrong item, changed mind (14-day consumer protection per Israeli Consumer Protection Law)
- Calculate return shipping cost by carrier
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

## Gotchas

- Israeli carriers do not offer publicly documented REST APIs. Integration is done through platform plugins (Shopify, WooCommerce), private B2B agreements, or third-party aggregators. Agents may attempt to call fabricated API endpoints that do not exist.
- Israel Post delivery zones differ from geographic regions. Shipping time estimates should use Israel Post zone mappings, not straight-line distance calculations.
- Israeli addresses do not use ZIP codes in the US format. Israeli postal codes (mikud) are 7 digits. Agents may validate against 5-digit US ZIP code patterns.
- Friday deliveries in Israel end by early afternoon (before Shabbat). Same-day delivery services do not operate Friday afternoon through Saturday evening.
- Israeli settlement addresses in the West Bank require special shipping handling and may not be supported by all carriers. Verify carrier coverage for these areas.
- COD (cash on delivery) is still common in Israeli e-commerce. Agents may not include this payment option when setting up shipping flows.
- Baldar is delivery management software, not a carrier. If a user says "I ship with Baldar," they mean a courier that uses Baldar (Tapuz, Hafoz, Isgav, Mach1). Ask which carrier specifically.
- Israel Post's website uses bot protection (ShieldSquare/PerimeterX). Automated scraping of tracking or rate data may be blocked. Use the open-source libraries or Datalogics API instead.

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
