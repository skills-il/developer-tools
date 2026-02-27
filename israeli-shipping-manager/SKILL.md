---
name: israeli-shipping-manager
description: >-
  Manage shipping operations across Israeli carriers — Israel Post, Cheetah,
  HFD, Baldar, Mahir Li, and BOX pickup points. Use when user asks about
  "shipping Israel", "Israel Post API", "Cheetah delivery", "meshloach",
  "shipping label", "package tracking Israel", "BOX pickup", "HFD", "Baldar",
  or "tawit mishloach". Covers carrier selection, Israeli address formatting,
  label generation, cross-carrier tracking, and customer delivery notifications.
  Do NOT use for international shipping outside Israel or customs/import.
license: MIT
allowed-tools: "Bash(python:*) WebFetch"
compatibility: >-
  Works with Claude Code, OpenClaw, Cursor. OpenClaw recommended for automated
  tracking updates and customer WhatsApp/SMS notifications.
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    he:
      - משלוחים
      - לוגיסטיקה
      - מסחר-אלקטרוני
      - משלוח
      - דואר-ישראל
      - ישראל
    en:
      - shipping
      - logistics
      - ecommerce
      - delivery
      - israel-post
      - israel
  display_name:
    he: מנהל משלוחים ישראלי
    en: Israeli Shipping Manager
  display_description:
    he: ניהול משלוחים ומעקב חבילות מול שלדנים ישראליים — דואר ישראל, צ'יטה, HFD, בלדר, מהיר לי ונקודות BOX
    en: >-
      Manage shipping operations across Israeli carriers — Israel Post, Cheetah,
      HFD, Baldar, Mahir Li, and BOX pickup points.
  openclaw:
    requires:
      bins: []
      env: []
    emoji: "📦"
---

# Israeli Shipping Manager

## Instructions

### Step 1: Select Carrier Based on Shipment
Help the user choose the right carrier for their shipment. Ask about parcel size, weight, delivery urgency, destination, and budget. Use this comparison table:

| Carrier | Best For | Speed | Price Range | Pickup Points | API Available |
|---------|----------|-------|-------------|---------------|---------------|
| Israel Post (דואר ישראל) | Standard parcels, nationwide coverage | 3-5 business days | Low-medium | Post offices + lockers | Yes (EMS) |
| Cheetah / Zrizi (צ'יטה) | Same-day/next-day urban delivery | Same day - next day | Medium-high | Limited | Yes |
| HFD (H.F.D.) | E-commerce fulfillment | 2-4 business days | Medium | Pickup points | Yes |
| Baldar (בלדר) | Express courier, documents | Same day - next day | High | Door-to-door | Limited |
| Mahir Li (מהיר לי) | Budget e-commerce shipping | 3-5 business days | Low | Pickup points | Yes |
| BOX (בוקס) | Self-service locker pickup | 2-4 business days | Low-medium | BOX lockers nationwide | Yes |

Selection criteria:
- **Parcel size/weight:** Heavy or oversized items may limit carrier options
- **Delivery speed:** Same-day requires Cheetah or Baldar; standard allows all carriers
- **Destination area:** Center (Gush Dan) has full coverage; periphery (Eilat, Galilee) may have limited options
- **Budget:** Mahir Li and Israel Post are cheapest; Baldar and Cheetah are premium
- **Pickup vs door-to-door:** BOX/HFD for self-service pickup; Baldar for guaranteed door delivery

### Step 2: Format Israeli Address
Format addresses correctly per carrier requirements. Run `python scripts/format_address.py --validate` to check format before submission. See references/address-format.md for the complete format specification.

Required fields:
- **Street name (שם רחוב)** — in Hebrew
- **House number (מספר בית)**
- **Apartment number (דירה)** — if applicable
- **Entrance (כניסה)** — if applicable (common in older buildings)
- **Floor (קומה)** — if applicable
- **City (עיר)** — in Hebrew
- **Mikud/ZIP (מיקוד)** — 7 digits

Special handling:
- **Military addresses (APO):** Use IDF address format (מספר צבאי)
- **Kibbutzim/Moshavim:** Settlement name + house number (no street)
- **Industrial zones:** Area name + building/company name
- **Arab localities:** Verify transliteration matches carrier database

### Step 3: Generate Shipping Label
For each carrier, generate shipping labels with required fields:
- Sender details (name, address, phone)
- Recipient details (name, address, phone)
- Parcel dimensions and weight
- Service type (standard, express, registered)
- Tracking barcode
- Carrier-specific fields (see references/carrier-apis.md)

Integration methods vary by carrier — some offer REST APIs, others require browser automation. See references/carrier-apis.md for per-carrier integration details.

### Step 4: Set Up Cross-Carrier Tracking
Implement unified tracking across all carriers:
- Normalize status codes to a common set: `pending`, `picked_up`, `in_transit`, `out_for_delivery`, `delivered`, `failed_delivery`, `returned`
- Poll carrier tracking endpoints at configurable intervals (default: every 2 hours)
- Store tracking data in persistent memory for historical analysis. If persistent memory is unavailable, export to `tracking-data.json`
- Detect anomalies: package stuck in same status for >48 hours, delivery failures, address corrections

### Step 5: Configure Customer Notifications
Set up automated customer notifications on status changes:
- **Shipped:** WhatsApp/SMS with tracking number and estimated delivery — "החבילה שלך נשלחה! מספר מעקב: [X]. צפי הגעה: [DATE]."
- **Out for delivery:** "החבילה שלך בדרך אליך! צפי הגעה היום עד [TIME]."
- **Delivered:** "החבילה נמסרה בהצלחה! תודה על הקנייה."
- **Failed delivery:** "לא הצלחנו למסור את החבילה. נסיון נוסף מתוכנן ל-[DATE]. לתיאום: [PHONE]."
- **Pickup ready:** "החבילה שלך מחכה לך בנקודת [BOX/Post/HFD] ב-[LOCATION]. קוד איסוף: [CODE]."

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
2. Route next-day Tel Aviv orders to Cheetah (12 parcels)
3. Route standard parcels to Israel Post/Mahir Li (38 parcels) based on cost
4. Format all addresses and validate mikud codes
5. Generate shipping labels per carrier
6. Set up tracking and customer notifications for all 50
Result: 50 shipping labels generated across 3 carriers. Tracking dashboard set up with WhatsApp notifications configured for each customer. Estimated total shipping cost: 1,850 NIS.

### Example 2: Setting Up BOX Pickup Point Integration
User says: "I want to offer BOX locker pickup as an option for my online store"
Actions:
1. Register for BOX API access (or guide through browser registration)
2. Get list of nearby BOX locations for the seller's area
3. Configure shipping label generation with BOX as destination type
4. Set up pickup-ready notification with locker code
5. Configure auto-tracking from BOX deposit to customer pickup
Result: BOX integration active. Customers can select BOX locker at checkout, receive pickup code via WhatsApp when package arrives. Average cost per shipment: 22 NIS.

### Example 3: Rate Comparison for Heavy Parcel to Eilat
User says: "I need to ship a 15kg package to Eilat, what are my options?"
Actions:
1. Check carrier availability for Eilat (periphery area)
2. Get rate quotes: Israel Post (registered), HFD, Mahir Li
3. Note: Cheetah/Baldar may not serve Eilat or charge premium
4. Compare delivery times and costs
5. Recommend best option based on price/speed tradeoff
Result: Comparison table showing Israel Post at 45 NIS (5 days), HFD at 55 NIS (3 days), Mahir Li at 38 NIS (5 days). Recommendation: Mahir Li for budget, HFD for speed.

## Bundled Resources

### References
- `references/carrier-apis.md` — API endpoints, authentication methods, and integration guides for each Israeli carrier (Israel Post, Cheetah, HFD, Baldar, Mahir Li, BOX). Includes rate calculation endpoints and tracking APIs. Consult when integrating with a specific carrier in Steps 3-4.
- `references/address-format.md` — Complete Israeli address formatting specification: street, house, apartment, entrance, floor, city, mikud. Includes special formats for kibbutzim, military addresses, and industrial zones. Consult when formatting addresses in Step 2.

### Scripts
- `scripts/format_address.py` — Validates and formats Israeli shipping addresses per carrier requirements. Checks mikud (ZIP) validity, normalizes Hebrew text, and handles special address types (kibbutz, military, industrial zone). Run: `python scripts/format_address.py --help`

## Troubleshooting

### Error: "Invalid mikud (ZIP code)"
Cause: Israeli mikud must be exactly 7 digits and match the city/street combination.
Solution: Verify mikud at Israel Post's mikud lookup (israelpost.co.il). Common issue: old 5-digit codes — all Israeli ZIP codes are now 7 digits.

### Error: "Carrier API authentication failed"
Cause: API credentials expired or account not activated for API access.
Solution: Check API key validity with the carrier's developer portal. Some carriers (Cheetah, HFD) require a signed contract before API access is granted. See references/carrier-apis.md for per-carrier setup.

### Error: "Address not recognized by carrier"
Cause: Address format doesn't match carrier's database, or Hebrew text encoding issue.
Solution: Ensure address uses UTF-8 encoded Hebrew. Run `scripts/format_address.py --validate` to check format. For Arab localities, verify the carrier accepts the specific spelling. Try alternative transliterations.

### Error: "Delivery failed — recipient not found"
Cause: Common for apartment buildings without intercom or missing entrance/floor details.
Solution: Add entrance (כניסה) and floor (קומה) to address. Configure delivery notification to include recipient phone for courier contact. Consider switching to pickup point (BOX/HFD) for repeat-failure addresses.
