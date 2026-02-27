# Israeli Marketplace Platform Guides

## Zap (זאפ) — Price Comparison & Marketplace

- **URL:** `https://www.zap.co.il`
- **Seller portal:** `https://sellers.zap.co.il`
- **Listing type:** Structured product listings with detailed specifications

### Listing Format
- **Title:** Product name in Hebrew + model number (e.g., "סמסונג גלקסי S24 128GB שחור")
- **Specifications:** Structured key-value pairs per category (manufacturer, model, color, storage, etc.)
- **Price:** NIS with VAT included — must match actual selling price
- **Photos:** Up to 8 images, minimum 500x500px, white background preferred
- **Description:** Optional free-text, Hebrew, up to 2000 characters

### Seller Requirements
- Valid Israeli business license (עוסק מורשה / עוסק פטור)
- Physical address in Israel
- Return policy compliant with Israeli Consumer Protection Law (14 days)
- Response to customer inquiries within 24 hours

### Fee Structure
- Monthly listing fee per product (varies by category)
- Click-through fee (cost per lead directed to seller)
- No commission on actual sale — Zap redirects to seller's site/contact

### Automation
- No public REST API — use browser automation (CDP/Playwright) for listing management
- Price monitoring: scrape product pages at `zap.co.il/models.aspx?sog={category_id}`
- Seller dashboard accessible via authenticated browser session

## KSP — Electronics & Price Comparison

- **URL:** `https://ksp.co.il`
- **Seller portal:** Direct partnership required
- **Listing type:** Structured product catalog with technical specifications

### Listing Format
- **Title:** Brand + model + key spec (e.g., "Samsung Galaxy S24 128GB")
- **Specifications:** Technical specs table matching KSP category schema
- **Price:** NIS with VAT, updated in real-time
- **Photos:** Product images per KSP guidelines, minimum 3 angles
- **Availability:** In stock / order / out of stock status

### Seller Requirements
- Approved vendor partnership with KSP
- Warehouse or fulfillment capability
- Competitive pricing (KSP monitors price competitiveness)

### Fee Structure
- Partnership agreement based (varies by vendor volume)
- Listing included in partnership
- KSP takes margin on sales through their platform

### Automation
- Partner API available for approved vendors (contact KSP business team)
- Price scraping: product pages at `ksp.co.il/?uin={product_id}`
- Stock updates via vendor portal or partner API

## Facebook Marketplace (פייסבוק מרקטפלייס) — Israel

- **URL:** `https://www.facebook.com/marketplace` (Israel locale)
- **Seller tools:** Facebook Commerce Manager
- **Listing type:** Casual product posts with photos and description

### Listing Format
- **Title:** Short, descriptive Hebrew title (e.g., "סמסונג גלקסי S24 חדש באריזה")
- **Price:** NIS, can mark as "free" or "negotiable" (מחיר לא קבוע)
- **Photos:** Up to 10 images, first photo is thumbnail — make it count
- **Description:** Free-text Hebrew, conversational tone, include condition and shipping info
- **Location:** City/neighborhood — critical for local buyers
- **Category:** Select from Facebook's predefined categories
- **Condition:** New, Like New, Good, Fair (חדש, כמו חדש, מצב טוב, סביר)

### Seller Requirements
- Personal Facebook account in good standing (no business license required)
- For shops: Facebook Commerce Manager setup with payment processing
- Comply with Facebook Commerce Policies (no prohibited items)
- Identity verification may be required for high-volume sellers

### Fee Structure
- Free for personal listings (C2C)
- Shops: 5% selling fee per transaction (minimum 8 NIS)
- Promoted listings: paid boost available (CPC model)

### Automation
- Facebook Graph API for Commerce (requires app review and approval)
- Product catalog management via Commerce Manager API
- Inventory and order management through Facebook Business Suite
- Webhook notifications for messages and orders

## Instagram Shopping (אינסטגרם שופינג) — Israel

- **URL:** Instagram app / `https://www.instagram.com`
- **Seller tools:** Instagram Commerce (linked to Facebook Commerce Manager)
- **Listing type:** Visual product tags on posts, stories, and reels

### Listing Format
- **Photos/Videos:** High-quality visual content — minimum 1080x1080px for feed posts
- **Product tags:** Tag products in photos (linked to Facebook product catalog)
- **Description:** Short Hebrew caption + relevant hashtags
- **Hashtags:** Mix of Hebrew and English, e.g., #למכירה #סמסונג #GalaxyS24 #מבצע #ישראל
- **Stories:** Swipe-up/link sticker to product page
- **Reels:** Product showcase with shopping tags

### Seller Requirements
- Instagram Business or Creator account
- Connected to Facebook Commerce Manager
- Product catalog approved by Instagram review
- Comply with Instagram Commerce eligibility requirements
- Physical goods only (no digital products or services)

### Fee Structure
- No listing fee for organic posts
- Shopping checkout (where available): processing fee per transaction
- Promoted posts: paid advertising (CPC/CPM model via Ads Manager)
- Instagram takes no commission on external checkout sales

### Automation
- Instagram Graph API for posting and product tagging
- Product catalog managed through Facebook Commerce Manager API
- Insights API for engagement and sales analytics
- Scheduled posting via Business Suite or third-party tools

## Cross-Platform Comparison

| Feature | Zap | KSP | Facebook | Instagram |
|---------|-----|-----|----------|-----------|
| Listing cost | Monthly + CPC | Partnership | Free / 5% shops | Free |
| Audience | Price-conscious tech buyers | Electronics shoppers | Local community | Visual / lifestyle |
| Best for | Electronics, appliances | Electronics, computers | General items, local | Fashion, lifestyle, visual |
| Hebrew support | Full | Full | Full | Full |
| API available | No (scrape) | Partner only | Graph API | Graph API |
| Payment processing | External | KSP checkout | FB Pay / external | External / checkout |
| Shipping integration | External | KSP logistics | Seller managed | Seller managed |
