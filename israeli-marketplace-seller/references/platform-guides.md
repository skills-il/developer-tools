# Israeli Marketplace Platform Guides

## Zap (זאפ), Price Comparison & Marketplace

- **URL:** `https://www.zap.co.il`
- **Seller onboarding:** `https://www.zap.co.il/joinzap.aspx` ("הוספת חנות לזאפ"). After joining, each store gets an authenticated management dashboard. Zap also operates a separate inventory tool, ZapSeller, offered through the Zap Group sales team.
- **Listing type:** Structured product listings with detailed specifications

### Listing Format
- **Title:** Product name in Hebrew + model number (e.g., "סמסונג גלקסי S24 128GB שחור")
- **Specifications:** Structured key-value pairs per category (manufacturer, model, color, storage, etc.)
- **Price:** NIS with VAT included, must match actual selling price
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
- No commission on actual sale, Zap redirects to seller's site/contact

### Automation
- No public REST API, use browser automation (CDP/Playwright) for listing management within Zap's Terms of Service
- Price monitoring: scrape product pages at `zap.co.il/models.aspx?sog={category_id}`
- Seller dashboard accessible via authenticated browser session

## KSP, Electronics & Price Comparison

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

## Facebook Marketplace (פייסבוק מרקטפלייס), Israel

- **URL:** `https://www.facebook.com/marketplace` (Israel locale)
- **Seller tools:** Facebook Commerce Manager (catalog and Shop setup only, see checkout note below)
- **Listing type:** Casual product posts with photos and description

> **Checkout change (effective 2025):** Meta discontinued native checkout on Facebook and Instagram Shops. The phase-out began June 2025 and native checkout was fully deprecated on September 4, 2025. Payment processing, order management, and the Commerce Manager Inbox were all discontinued for Shops. Buyers are now redirected to the merchant's own website to complete the purchase. Facebook Marketplace C2C personal listings were always a contact-the-seller flow and are unaffected, but anyone running a Facebook/Instagram **Shop** must now host their own checkout (their own e-commerce site) and collect payment there.

### Listing Format
- **Title:** Short, descriptive Hebrew title (e.g., "סמסונג גלקסי S24 חדש באריזה")
- **Price:** NIS, can mark as "free" or "negotiable" (מחיר לא קבוע)
- **Photos:** Up to 10 images, first photo is thumbnail, make it count
- **Description:** Free-text Hebrew, conversational tone, include condition and shipping info
- **Location:** City/neighborhood, critical for local buyers
- **Category:** Select from Facebook's predefined categories
- **Condition:** New, Like New, Good, Fair (חדש, כמו חדש, מצב טוב, סביר)

### Seller Requirements
- Personal Facebook account in good standing (no business license required)
- For shops: Facebook Commerce Manager setup with payment processing
- Comply with Facebook Commerce Policies (no prohibited items)
- Identity verification may be required for high-volume sellers

### Fee Structure
- Free for personal listings (C2C)
- Shops: no Meta native selling fee anymore, since native checkout was removed in 2025 there is no on-platform transaction for Meta to charge a fee on. Payment fees are now whatever the merchant's own checkout provider charges.
- Promoted listings: paid boost available (CPC model)

### Automation
- Facebook Graph API for Commerce (requires app review and approval). Catalog and Shop product management is still available; the order-management and payment endpoints were retired with native checkout.
- Product catalog management via Commerce Manager API
- Order fulfillment and payment now happen on the merchant's own site, not in Commerce Manager
- Webhook notifications for messages (order webhooks no longer apply for Meta-hosted orders)

## Instagram Shopping (אינסטגרם שופינג), Israel

- **URL:** Instagram app / `https://www.instagram.com`
- **Seller tools:** Instagram Commerce (linked to Facebook Commerce Manager)
- **Listing type:** Visual product tags on posts, stories, and reels

> **Checkout change (effective 2025):** As with Facebook, Meta removed native checkout from Instagram Shops on September 4, 2025. Product tags still work for discovery, but tapping a tagged product now sends the buyer to the merchant's external website to complete the purchase. There is no in-app Instagram checkout for new orders. Plan for an external e-commerce site plus an Israeli payment provider.

### Listing Format
- **Photos/Videos:** High-quality visual content, minimum 1080x1080px for feed posts
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
- No Instagram native checkout fee, native checkout was removed in 2025; all sales go through the merchant's external site
- Promoted posts: paid advertising (CPC/CPM model via Ads Manager)
- Payment fees are whatever the merchant's own checkout provider charges

### Automation
- Instagram Graph API for posting and product tagging (discovery only)
- Product catalog managed through Facebook Commerce Manager API
- Insights API for engagement analytics; sales/conversion data now lives in the merchant's own store
- Scheduled posting via Business Suite or third-party tools

## Cross-Platform Comparison

| Feature | Zap | KSP | Facebook | Instagram |
|---------|-----|-----|----------|-----------|
| Listing cost | Commission on sale (by category), no upfront fee | Partnership | Free (C2C) / catalog free | Free |
| Audience | Price-conscious tech buyers | Electronics shoppers | Local community | Visual / lifestyle |
| Best for | Electronics, appliances | Electronics, computers | General items, local | Fashion, lifestyle, visual |
| Hebrew support | Full | Full | Full | Full |
| API available | No (scrape) | Partner only | Graph API (catalog only) | Graph API (catalog only) |
| Payment processing | Zap checkout / external | KSP checkout | Merchant's own site (no native checkout since 2025) | Merchant's own site (no native checkout since 2025) |
| Shipping integration | External | KSP logistics | Seller managed | Seller managed |
