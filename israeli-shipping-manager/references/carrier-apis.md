# Israeli Carrier API Reference

## Israel Post (דואר ישראל) — EMS API

- **Base URL:** `https://www.israelpost.co.il/ems/api/v1`
- **Auth:** API key via header `X-API-Key`
- **Registration:** Apply at Israel Post business portal (requires business license)
- **Rate limit:** 60 requests/minute

### Endpoints
- `POST /shipment` — Create shipment, returns tracking number
- `GET /shipment/{tracking_number}` — Get tracking status
- `POST /rate` — Calculate shipping rate by weight, dimensions, destination
- `GET /mikud/{code}` — Validate mikud (ZIP) code
- `GET /branches` — List post office branches and locker locations

### Notes
- Tracking numbers: 13-character format (e.g., `RR123456789IL`)
- Supports registered mail, parcels, and EMS express
- Mikud validation endpoint useful for address verification

## Cheetah / Zrizi (צ'יטה)

- **Base URL:** `https://api.cheetah.co.il/v2`
- **Auth:** OAuth2 Bearer token (client credentials flow)
- **Registration:** Requires signed shipping contract with Cheetah sales
- **Rate limit:** 120 requests/minute

### Endpoints
- `POST /deliveries` — Create delivery order
- `GET /deliveries/{id}/track` — Get delivery status
- `POST /deliveries/rate` — Get rate quote
- `POST /webhooks` — Register status change webhook
- `GET /coverage` — Check delivery coverage area

### Notes
- Webhook support for real-time status updates (preferred over polling)
- Same-day delivery available in Gush Dan area only
- Requires pickup scheduling for sender location

## HFD (H.F.D.)

- **Base URL:** `https://api.hfd.co.il/api/v1`
- **Auth:** API key + merchant ID via headers
- **Registration:** Sign up at HFD business portal
- **Rate limit:** 100 requests/minute

### Endpoints
- `POST /shipments` — Create shipment with label
- `GET /shipments/{barcode}/status` — Get tracking status
- `POST /shipments/rate` — Calculate rate
- `GET /pickup-points` — List HFD pickup point locations
- `GET /shipments/{barcode}/label` — Download shipping label (PDF)

### Notes
- Returns PDF label ready for printing
- Pickup points searchable by city or coordinates
- Supports bulk shipment creation (up to 100 per request)

## Baldar (בלדר)

- **Integration:** Limited API — browser automation recommended
- **Portal:** `https://www.baldar.co.il/business`
- **Auth:** Username/password login (session-based)

### Browser Automation Flow
1. Navigate to Baldar business portal
2. Login with credentials
3. Fill shipment form: sender, recipient, parcel details
4. Submit and capture tracking number from confirmation page
5. Track via portal search page

### Notes
- No public REST API; use CDP/Playwright for automation
- Best for low-volume express/document deliveries
- Tracking available by phone or portal only

## Mahir Li (מהיר לי)

- **Base URL:** `https://api.mahirli.co.il/v1`
- **Auth:** API key via `Authorization: Bearer {key}`
- **Registration:** Apply at Mahir Li merchant portal
- **Rate limit:** 80 requests/minute

### Endpoints
- `POST /orders` — Create shipping order
- `GET /orders/{id}/tracking` — Get tracking information
- `POST /orders/calculate` — Calculate shipping cost
- `GET /points` — List pickup point locations

### Notes
- Budget-friendly option for standard e-commerce
- Pickup points in shopping centers and convenience stores
- Bulk order upload via CSV supported

## BOX (בוקס) — Locker API

- **Base URL:** `https://api.box-il.co.il/api/v2`
- **Auth:** API key + merchant secret (HMAC signed requests)
- **Registration:** Partner program at BOX business site
- **Rate limit:** 100 requests/minute

### Endpoints
- `POST /parcels` — Create parcel for locker delivery
- `GET /parcels/{id}/status` — Get parcel status
- `GET /lockers` — List all BOX locker locations with availability
- `GET /lockers/nearby?lat={lat}&lon={lon}` — Find nearest lockers
- `GET /parcels/{id}/pickup-code` — Get pickup code for customer

### Notes
- Locker availability changes in real-time; check before creating parcel
- Pickup code sent automatically to customer phone on deposit
- Parcels held for 3 days before return to sender
- Maximum parcel size: 60x40x40 cm

## Common Status Codes (Normalized)

All carriers map to these unified statuses:

| Unified Status | Israel Post | Cheetah | HFD | Mahir Li | BOX |
|----------------|-------------|---------|-----|----------|-----|
| `pending` | Registered | Created | New | Created | Created |
| `picked_up` | Accepted | Picked up | Collected | Picked up | Received |
| `in_transit` | In transit | On the way | In delivery | In transit | In transit |
| `out_for_delivery` | Out for delivery | Delivering | Last mile | Delivering | At locker |
| `delivered` | Delivered | Delivered | Delivered | Delivered | Picked up |
| `failed_delivery` | Failed attempt | Failed | Undelivered | Failed | Expired |
| `returned` | Returned to sender | Returned | Returned | Returned | Returned |

## Rate Calculation — Common Fields

All rate endpoints accept these fields:
- `weight_kg` (float) — Parcel weight in kilograms
- `length_cm`, `width_cm`, `height_cm` (int) — Parcel dimensions
- `origin_mikud` (string) — Sender ZIP code (7 digits)
- `destination_mikud` (string) — Recipient ZIP code (7 digits)
- `service_type` (string) — "standard", "express", "registered"
