# Israeli Carrier Integration Reference

Israeli shipping carriers generally do not offer publicly documented REST APIs. Integration is done through platform-specific plugins (Shopify, WooCommerce, Magento), private B2B agreements, third-party aggregators, or delivery management software. This reference documents the verified integration methods for each carrier.

## Israel Post (דואר ישראל)

- **Website:** israelpost.co.il
- **Business Portal:** mybusiness.israelpost.co.il (business customers only)
- **No public REST API.** API access is restricted to business customers who send items through Israel Post. There is no publicly documented API for general developers.

### Verified Integration Points

**Tracking (unofficial, web scraping):**
- Endpoint: `POST https://mypost.israelpost.co.il/umbraco/Surface/ItemTrace/GetItemTrace`
- Auth: Requires CSRF token (`__RequestVerificationToken`) extracted from the tracking page, plus session cookies
- Parameters: `itemCode` (tracking number), `lcid` (locale)
- Built on Umbraco CMS

**Rate calculation (public, no auth):**
- Endpoint: `GET https://www.israelpost.co.il/npostcalc.nsf/CalcPrice?openagent&...`
- Built on Lotus Notes/Domino
- Parameters appended as query string (weight, dimensions, destination)

**Domestic shipping (via Datalogics third-party):**
- Endpoint: `POST https://connect.datalogics.co.il/rest/w_create_shipping`
- Store lookup: `GET https://connect.datalogics.co.il/rest/w_get_shipping_stores`
- Auth: Token passed in JSON body (`"token": "YOUR_TOKEN"`)
- Documentation: israel-post.datalogics.co.il

**Mikud (ZIP) search:**
- Web interface: `mypost.israelpost.co.il/zipcodesearch`
- No public API. Third-party Python library `mikud` scrapes this page.

### Open-Source Libraries
- `bennymeg/IsraelPostalServiceAPI` (TypeScript) -- rate calculation
- `LandRover/postil-status` (Node.js) -- tracking
- `Stajor/israel-post` (PHP) -- tracking

### Notes
- Tracking numbers: 13-character UPU S10 format (e.g., `RR123456789IL`)
- Prefixes: `RR` = registered parcel, `EE` = EMS express, `CP` = parcel
- Supports registered mail, parcels, and EMS express
- Bot protection (ShieldSquare/PerimeterX) on the main website may block automated requests

## Cheetah (צ'יטה)

- **Website:** chitadelivery.co.il
- **Group site:** cheetah-group.net
- **No public REST API.** Integration is done through platform-specific plugins and private B2B contracts.

### Verified Integration Methods

**Shopify:** "Cheetah DeliverIt" app by BOA Ideas on Shopify App Store. Handles order sync, label generation, and tracking.

**Other platforms:** Contact Cheetah sales directly via chitadelivery.co.il or WhatsApp (0559577119).

**Internal system:** Cheetah uses a "RUN" delivery management system at chita-il.com. Business customers access this for order entry and tracking, but it is not a public API.

### Notes
- Full name: Cheetah Deliveries Ltd., headquartered in Petah Tikva
- 9 branches nationwide (Kiryat Ata to Eilat), same-day delivery is not limited to Gush Dan
- Same-day delivery service with express deliveries often completed within 4 hours
- B2B focus: contact sales for business account setup

## HFD (Hameritz & Flash)

- **Website:** hfd.co.il
- **No publicly documented REST API.** HFD mentions having an "API tool" for e-commerce integration on their website, but technical documentation is not public. Contact HFD directly for API access.

### Verified Integration Methods

**Shopify:** "HFD DeliverIt" app on Shopify App Store. Automatic order sync, label generation, tracking.

**WooCommerce:** "HFD ePost Integration" plugin on WordPress.org.

**Other platforms:** Integrations available for Magento, Konimbo, and Wix. Contact HFD for details.

### Notes
- Founded 1995, one of the largest B2C e-commerce delivery companies in Israel
- ~1,000 pickup points and lockers nationwide
- Pickup points searchable on hfd.co.il/en/pick-up-points/
- Tracking: hfd.co.il with barcode number
- Third-party tracking via AfterShip, WeShip

## Baldar (בלדר) -- Delivery Management Software

**Important:** Baldar is NOT a shipping carrier. It is delivery management software (SaaS) used by Israeli courier companies.

- **Website:** baldar.co.il
- **Used by:** Tapuz Delivery, Hafoz, Isgav, Mach1, and other Israeli couriers

### How It Works
Baldar provides white-label CRM portals for courier companies. Each carrier hosts their own Baldar instance:
- `crm.tapuzdelivery.co.il/baldar/Login.aspx`
- `portal.hafoz.co.il/baldar/Login.aspx`
- `baldar.isgav.co.il/Baldar/Login.aspx`
- `manui.mach1.co.il/Baldar/Login.aspx`

### Integration
- **nopCommerce plugin** available for sending orders to the Baldar courier system
- Business customers get username/password to the ordering portal of their chosen carrier
- ASP.NET WebForms-based CRM with session authentication
- No public REST API

### Notes
- If a user says "I use Baldar," they mean one of the courier companies that licenses Baldar software. Ask which carrier specifically.
- The Baldar software handles: order entry, route management, SMS notifications, driver apps, invoicing

## Mahir Li (מהיר לי)

- **Website:** mahirli.com
- **No public API.** Mahir Li uses LionWheel as their delivery management platform. Integration is via LionWheel's system.

### Verified Integration Methods

**LionWheel platform:** Mahir Li operates on LionWheel (lionwheel.com), which has its own REST API documented at `github.com/lionwheel/api`. Integrations go through LionWheel, not Mahir Li directly.

**Direct:** Contact Mahir Li via mahirli.com for business account setup. Minimum 10 deliveries per day.

### Notes
- Same-day courier service: delivery within 9 hours from pickup
- Coverage: Beer Sheva to Nahariya (not nationwide for all services)
- Founded by two partners from Gush Katif, operates from Petah Tikva
- B2B focused: requires minimum volume

## UPS Israel (Locker Network)

- **Website:** ups.com/il
- **Developer portal:** developer.ups.com (UPS Developer Kit -- shared with global UPS)
- **Launched:** March 2025 by the UPS franchisee in Israel

### Verified Integration Methods

**UPS Developer Kit:** UPS provides documented REST APIs for label generation, rate calculation, and tracking. These work for the Israeli locker network as well. Sign up at developer.ups.com.

**Locker drop-off flow:** Generate a label via the API, present the QR code at any UPS locker (24/7 access). 100 locker stations + 150 service stores nationwide.

### Notes
- Flat rate ~27 NIS per package (incl. VAT) for the locker-to-locker domestic service
- Delivery: 1-2 business days to most localities
- No minimum volume requirement
- Targets private customers and small businesses (under-served by traditional carriers' B2B contracts)
- This is the UPS Israel franchisee's domestic locker network, distinct from UPS Express international service

## GetPackage (גט פקג')

- **Website:** getpackage.com
- **Model:** SaaS platform connecting businesses and individuals with crowd-sourced couriers (collaborative-economy / on-demand)

### Verified Integration Methods

**Web platform:** Order day-to-day deliveries through the GetPackage web interface. Select pickup point + dropoff point; the platform finds available couriers.

**REST API:** Available for business accounts (B2B). Contact GetPackage business team for API credentials.

### Notes
- Same-day delivery, typically 1-3 hours from pickup
- Variable pricing (bid-based / dynamic)
- Door-to-door only; no locker network of their own
- No minimum volume
- Common alternative to Cheetah / Mahir Li for sellers without a B2B contract

## Locker and Pickup Point Services

Israel has several locker and self-service pickup networks. There is no single "BOX" carrier. The main services:

### BOX2GO (Israel Post + Paz/Yellow Box)
- Israel Post's locker service using Yellow Box lockers at Paz gas stations
- ~120 locations nationwide
- Integrated with Israel Post shipping
- Pickup code sent via SMS

### Shlager (שלאגר) by Orian
- Smart locker network for receiving and returning online purchases
- Mobile stations in residential areas
- Website: orian.com

### Done (דאן)
- Locker-based delivery service
- Website: done.co.il
- Cost: ~30 NIS per package, max 5 kg
- Delivery in 3 working days

### SafeLocker
- Lockers at malls and shopping centers
- Website: safelocker.co.il

### HFD Pickup Points
- ~1,000 pickup point locations
- Searchable at hfd.co.il

### UPS Lockers Israel
- 100 lockers + 150 service stores nationwide (launched March 2025)
- 24/7 drop-off AND pickup (most other Israeli locker networks are pickup-only)
- Flat ~27 NIS per package (incl. VAT)
- 1-2 business days
- Locator: ups.com/il

## Third-Party Aggregators

For unified multi-carrier integration, consider these aggregator APIs:

| Aggregator | Coverage | Notes |
|-----------|----------|-------|
| AfterShip | Tracking only | Supports Israel Post, HFD, and many others |
| TrackingMore | Tracking only | Israel Post tracking API with webhooks and SDKs |
| ClickPost | Full integration | 150+ carriers including Israeli carriers |
| WeShip (weship.com) | Full integration | Multi-carrier Israeli shipping platform |
| LionWheel | Full integration | Used by Mahir Li and other Israeli couriers |
| UPS Developer Kit | Full integration | Official UPS APIs, also cover the new Israeli locker network |
| GetPackage Business API | Full integration | Crowd-sourced same-day couriers in Israel; requires business account |

These aggregators provide the unified REST API experience that individual Israeli carriers lack.

## Common Status Codes (Normalized)

When building a unified tracking system across carriers, normalize to these statuses:

| Unified Status | Description |
|----------------|-------------|
| `pending` | Shipment created, not yet picked up |
| `picked_up` | Carrier has collected the parcel |
| `in_transit` | Parcel moving between facilities |
| `out_for_delivery` | On the delivery vehicle / at locker |
| `delivered` | Successfully delivered or picked up by customer |
| `failed_delivery` | Delivery attempt failed |
| `returned` | Returned to sender |

Map each carrier's native statuses to this set. Status names vary by carrier and must be mapped individually based on the tracking data format you receive from each integration method.

## Rate Calculation

There is no unified rate API across Israeli carriers. Options:

1. **Israel Post rate calculator** (public, no auth): Use the Lotus Notes endpoint or the `bennymeg/IsraelPostalServiceAPI` TypeScript library
2. **Carrier-specific quotes:** Contact each carrier for rate agreements (usually volume-based)
3. **Aggregator APIs:** WeShip and ClickPost offer multi-carrier rate comparison
4. **Manual rate tables:** Request current rate cards from carrier sales teams
