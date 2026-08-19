# Israeli Carrier Integration Reference

Israeli shipping carriers generally do not offer publicly documented REST APIs. Integration is done through platform-specific plugins (Shopify, WooCommerce, Magento), private B2B agreements, third-party aggregators, or delivery management software. This reference documents the verified integration methods for each carrier.

## Israel Post (דואר ישראל)

- **Website:** israelpost.co.il
- **Business Portal:** mybusiness.israelpost.co.il (business customers only)
- **No public REST API.** API access is restricted to business customers who send items through Israel Post. There is no publicly documented API for general developers.

### Verified Integration Points

**Tracking (unofficial, and no longer a workable path):**
- The whole `israelpost.co.il` estate, `mypost.` and `doar.` subdomains included, sits behind Radware Bot Manager. Verified August 2026: a plain HTTPS request is answered by a `validate.perfdrive.com` bot-manager challenge rather than by the application, so the historical Umbraco surface-controller flow (`POST /umbraco/Surface/ItemTrace/GetItemTrace` with a `__RequestVerificationToken` and session cookies) cannot be driven from a script.
- Use a third-party aggregator for tracking instead. Do not build a scraper against this host.

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
- Web interface: `doar.israelpost.co.il/locatezip`. The older `mypost.israelpost.co.il/zipcodesearch` URL now redirects here (verified August 2026).
- No public API, and the page is behind the same bot-manager wall as the rest of the estate.

### Open-Source Libraries

All three are unmaintained. Read them for the request shapes; do not take a production dependency on any of them.

| Library | Language | Scope | Last commit | Status |
|---------|----------|-------|-------------|--------|
| `bennymeg/IsraelPostalServiceAPI` | TypeScript | Rate calculation | March 2023 | Unmaintained but the request shape is still the best documented reference |
| `Stajor/israel-post` | PHP | Tracking and rate | September 2020 | Unmaintained |
| `LandRover/postil-status` | Node.js | Tracking | December 2020 | Dead. It targets `postil.com`, a domain that no longer resolves, so it cannot function |

### Notes
- Tracking numbers: 13-character UPU S10 format (e.g., `RR123456789IL`)
- Prefixes: `RR` = registered parcel, `EE` = EMS express, `CP` = parcel
- Supports registered mail, parcels, and EMS express
- Bot protection (ShieldSquare/PerimeterX) on the main website may block automated requests

## Cheetah (צ'יטה)

- **Website:** chitadelivery.co.il (the public site; SKILL.md previously pointed users at chita-il.com, which is the business login)
- **Customer tracking:** chitadelivery-cx.com/login
- **Group site:** cheetah-group.net
- **No public REST API.** Integration is done through platform-specific plugins and private B2B contracts.

### Verified Integration Methods

**Shopify:** "Cheetah DeliverIt" app by BOA Ideas on Shopify App Store. Handles order sync, label generation, and tracking.

**Other platforms:** Contact Cheetah sales directly via chitadelivery.co.il. (An earlier version of this file listed a WhatsApp number that does not appear anywhere on Cheetah's own site; it has been removed rather than carried forward unsourced.)

**Internal system:** Cheetah runs a RunCom-based business system reached from `chita-il.com/RunCom.Server/Request.aspx?APPNAME=run&PRGNAME=call_knisa`, linked from their site as "כניסת לקוחות". It is a business-customer login, not a public API and not a consumer tracking page. Customers track their shipment at `chitadelivery-cx.com/login`.

### Notes
- Full name: Cheetah Deliveries Ltd., headquartered in Petah Tikva
- 9 branches nationwide, "מהצפון ועד אילת" per their own site, so same-day delivery is not limited to Gush Dan
- **Cheetah Shops is the largest pickup network in this reference**: their site states "רשת צ'יטה שופס המונה 35 סניפים ויותר מ-1,300 נקודות חלוקה בפריסה ארצית", i.e. more distribution points than HFD's ~1,000. Do not classify Cheetah as express-and-door-to-door only.
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
- Third-party tracking via AfterShip or TrackingMore

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

**Locker drop-off flow:** Generate a label via the API, present the QR code at any UPS locker (24/7 access). Note that the Israeli domestic price list is tied to the local easyship ordering site, so confirm which rate card an account is on before quoting a price from the UPS global API.

### Published Israeli Price List

From the Israeli operator's domestic price list (site.ship.co.il), which applies to shipments ordered through the local easyship site.

**This price list is valid for ONE MONTH.** Its closing line reads `מחירון זה תקף לחודש אוגוסט 2026 בלבד`. The figures below are the August 2026 list. Re-read the source before quoting any of them, and tell the user which month you read.

| Service | Before VAT | Incl. VAT |
|---------|-----------|-----------|
| To a pickup point (store or locker) | 22.9 NIS | 27.02 NIS |
| Home delivery up to 5 kg | 46.5 NIS | 54.87 NIS |
| Home delivery up to 10 kg | 48.5 NIS | 57.23 NIS |
| Home delivery up to 15 kg | 63.5 NIS | 74.93 NIS |

Remote-zone surcharges, applied per weight band, on top of the above:

| Zone | Before VAT | Incl. VAT |
|------|-----------|-----------|
| From or to zone 3 | 18 NIS | 21.24 NIS |
| From or to zone 5 | 28 NIS | 33.04 NIS |

Chargeable weight is the greater of actual weight and volumetric weight, where volumetric weight is length x width x height in cm divided by 5000. For a multi-parcel shipment the chargeable weight is the SUM across all packages, rounded up to the whole kilogram.

**The two services have DIFFERENT caps, and conflating them is how an agent quotes a service that will refuse the parcel:**

| Service | Cap |
|---------|-----|
| Pickup point or locker | ONE package only, maximum 8 kg physical or volumetric, whichever is higher (`ניתן למסור בחנות שירות או לוקר ... משלוח הכולל חבילה אחת בלבד, במשקל מקסימלי של 8 ק"ג`) |
| Home delivery | Up to 15 kg chargeable, multi-parcel allowed |

Beyond 15 kg an excess weight/size fee applies (2.75 NIS per kg before VAT from the first kg, not less than 63.5 NIS, plus a 50 NIS per-package excess fee).

### Exception Handling and Its Costs

| Event | Consequence |
|-------|-------------|
| Parcel not collected from a service store | Returned to sender after 5 business days from arrival |
| Parcel not collected from a locker | Returned to sender after **48 hours** |
| Return to sender | Charged at the full tariff for the relevant destination |
| Shipment not ready when the courier arrives | 15 NIS before VAT per pickup or pickup attempt |
| Destination requires pre-arranged entry approval, or is a post office branch or embassy | Not covered. The carrier may return the shipment at the sender's expense, or charge 200 NIS before VAT for special distribution |

The 48-hour locker window is short enough that a pickup-ready notification flow needs a reminder inside it, not a next-day one.

### Notes
- The pickup-point price is NOT flat nationwide. Quoting 27.02 NIS for a periphery address under-quotes it by the zone surcharge.
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

### BOX2GO (Israel Post + Paz/Yellow Box) -- DISCONTINUED

**Do not offer this service. It ended in 2021.** Israel Post's Yellow Box locker partnership with Paz (launched March 2018, roughly 120 stations at Paz fuel stations) was wound down: parcels ordered for delivery to a BOX2GO locker after 30/09/2021 were delivered to the shipping address on the order instead, and mail arriving for distribution with a Box2Go address after 15/11/2021 was returned to sender. Israel Post's own BOX2GO page now redirects to their homepage with no BOX2GO content (verified August 2026).

It is kept in this reference only as a negative entry, because the service is still described as live across a great deal of older documentation and it is a predictable thing for an agent to recommend. Use HFD pickup points, Done, or the UPS Israel locker network instead.

### Shlager (שלאגר) by Orian
- Smart locker network for receiving and returning online purchases
- Mobile stations in residential areas
- Website: shlager.com (operated by Orian, orian.com)

### Done (דאן)
- Locker-based delivery service
- Website: done.co.il
- Cost: 30 NIS per package, max 5 kg (verbatim from done.co.il/price-list/)
- Transit time is not published on their pricing page; ask Done rather than quoting a figure

### SafeLocker -- not a parcel network

`safelocker.co.il` is a locker HARDWARE vendor (סייפ לוקר בע"מ), an importer and reseller of physical locker cabinets for schools, offices and gyms. It has no parcel pickup network and no shipping integration. Do not list it as a pickup option.

### HFD Pickup Points
- ~1,000 pickup point locations
- Searchable at hfd.co.il

### UPS Lockers Israel
- Locker and service-store network nationwide, launched early 2025. The "100 lockers + 150 service stores" figures come from launch coverage and the operator does not publish a current count, so treat them as launch-era and do not quote them as today's footprint.
- 24/7 drop-off AND pickup (most other Israeli locker networks are pickup-only)
- 27.02 NIS incl. VAT per package to a pickup point, plus the zone 3 / zone 5 remote surcharge
- 1-2 business days
- Locator: ups.com/il

## Third-Party Aggregators

For unified multi-carrier integration, consider these aggregator APIs:

| Aggregator | Coverage | Notes |
|-----------|----------|-------|
| AfterShip | Tracking only | Supports Israel Post, HFD, and many others |
| TrackingMore | Tracking only | Israel Post tracking API with webhooks and SDKs |
| ClickPost | Full integration | Publishes an Israel Post integration page. Its Israeli coverage beyond Israel Post was not verified, so confirm your specific carrier is supported before committing |
| LionWheel | Full integration | Used by Mahir Li and other Israeli couriers. Public API repo at github.com/lionwheel/api, actively maintained (commits as recent as July 2026) |
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
3. **Aggregator APIs:** ClickPost offers multi-carrier rate comparison. Note that `weship.com` is a MEXICAN logistics platform with no Israeli carrier coverage, despite occasionally being cited as an Israeli multi-carrier option
4. **Manual rate tables:** Request current rate cards from carrier sales teams
