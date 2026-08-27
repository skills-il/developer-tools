# Israeli Marketplace Platform Guides

## Zap (זאפ), Price Comparison & Marketplace

- **URL:** `https://www.zap.co.il`
- **Seller onboarding:** `https://www.zap.co.il/joinzap.aspx` ("הוספת חנות לזאפ"). After joining, each store gets an authenticated management dashboard.
- **Listing type:** Structured product listings with detailed specifications

### Listing Format
- **Title:** Product name in Hebrew + model number (e.g., "סמסונג גלקסי S24 128GB שחור")
- **Specifications:** Structured key-value pairs per category (manufacturer, model, color, storage, etc.)
- **Price:** NIS with VAT included, must match actual selling price
- **Photos:** clear product images on a plain background. Zap does not publish image count/dimension limits on its public onboarding page, so take the exact limits from the store management dashboard rather than assuming a number.
- **Description:** optional free-text in Hebrew. Character limits are set per category in the dashboard; do not assume a fixed cap.

### Seller Requirements

The requirement that matters depends on which of Zap's two models you join, and they are opposites on this point:

- **Price comparison:** you must have your own e-commerce website. Zap's onboarding page states it plainly: a commerce site that ships orders, including online credit-card clearing, and adapted for mobile display ("אתר סחר אינטרנטי המבצע משלוחים, כולל סליקת כרטיסי אשראי באינטרנט ומותאם לתצוגה במובייל"). Zap refers buyers onto that storefront.
- **Zap marketplace:** **no online store of your own is required.** Zap says that to join the marketplace and sell inside the site, all you need is to hold stock and supply the products ("כל שעליך לעשות הוא להחזיק מלאים ולספק את המוצרים... אין צורך שתהיה בבעלותך חנות אינטרנטית"). This is the route for a seller who has no site.

Beyond that, Zap's public onboarding page does not enumerate seller eligibility conditions. Being a registered osek and holding a lawful return policy are obligations Israeli law imposes on the seller regardless (see SKILL.md Steps 7 and 8), not documented Zap gates. Take any Zap-specific requirement or response-time commitment from your own store agreement rather than assuming one.

### Fee Structure
Zap runs two seller models with different fees, so confirm which one you are on:
- **Price-comparison listing:** a fixed monthly payment plus a per-referral charge, priced on the number of click-throughs Zap sends to the store's site ("התשלום מבוסס על כמות ההפניות המתקבלות מאתר zap השוואת מחירים לאתר החנות (Pay Per Click) + תשלום חודשי קבוע"). Zap redirects the buyer to the seller's own site and takes no commission on the sale.
- **Zap marketplace (מרקטפלייס):** a commission model, with a variable percentage per sale depending on the product category ("מודל עמלות, עם אחוז משתנה של עמלה ממכירה בהתאם לקטגוריית המוצר").

Confirm the current model and rates on the joinzap onboarding page; do not assume only one model applies.

### Automation
- No public REST API, use browser automation (CDP/Playwright) for listing management within Zap's Terms of Service
- Price monitoring: read public product/category pages. Do not hardcode a URL pattern from this document; confirm the current path shape by opening the category in a browser first, since these change.
- Seller dashboard accessible via authenticated browser session

## KSP, First-Party Electronics Retailer (price reference only)

- **URL:** `https://ksp.co.il`
- **What it is:** KSP is a first-party electronics retailer ("the Israeli Amazon") that sells its own inventory. It is NOT a third-party seller marketplace, so you cannot list your products on it.
- **Seller-facing program:** only an affiliate/referral program (earn commission marketing KSP's products). There is no public third-party "partner API" or "vendor portal" for listing your own goods, do not assume one exists.

### How to use KSP in this skill
- Treat KSP as a competitor whose retail prices you compare against (see Step 2 price monitoring).
- Price reference: read public product pages with a clearly identified client, within KSP's Terms of Service. Confirm the current URL shape by opening a product in a browser rather than assuming a legacy query-string pattern. Do not scrape aggressively or evade bot protection.

## Yad2, Israel's Dominant General Marketplace

- **URL:** `https://www.yad2.co.il/market`
- **What it is:** Israel's largest general classifieds/marketplace (the de-facto Israeli eBay/Craigslist), for both C2C and business sellers across electronics, second-hand goods, vehicles, real estate, and more.
- **Seller access:** post a listing on the Yad2 site (free basic listings; paid promotion and business "חנות" store accounts available).

### Listing Format
- **Title:** Hebrew, with brand/model and condition
- **Photos:** multiple clear photos
- **Category:** pick the accurate category (Yad2 is category-driven)
- **Price + location:** NIS price (including VAT for an osek murshe) and the seller's area
- **Contact + fulfillment:** in-platform chat/phone; payment and delivery are arranged off-platform (Bit, PayBox, cash, or courier)

### Automation
- No public third-party seller API. Manage listings via the site or a business store account; read public pages only within the Terms of Service.

## Facebook Marketplace (פייסבוק מרקטפלייס), Israel

- **URL:** `https://www.facebook.com/marketplace` (Israel locale)
- **Seller tools:** Facebook Commerce Manager (catalog and Shop setup only, see checkout note below)
- **Listing type:** Casual product posts with photos and description

> **Checkout change:** Meta's own help centre states that as of September 2025, Shops on Facebook and Instagram use website checkout, and that management of the post-purchase experience in Commerce Manager has been discontinued. Buyers are now directed to the merchant's own website to complete the purchase, and a merchant whose shop has not yet migrated must create a checkout URL. Meta does not publish a more precise cut-over date than "September 2025", so do not cite one. Facebook Marketplace C2C personal listings in Israel are a contact-the-seller flow and are unaffected, but anyone running a Facebook/Instagram **Shop** must now host their own checkout (their own e-commerce site) and collect payment there.

### Listing Format
- **Title:** Short, descriptive Hebrew title (e.g., "סמסונג גלקסי S24 חדש באריזה")
- **Price:** NIS, can mark as "free" or "negotiable" (מחיר לא קבוע)
- **Photos:** several images, first photo is the thumbnail so make it count. Take the current per-surface image cap from Commerce Manager rather than assuming a fixed number.
- **Description:** Free-text Hebrew, conversational tone, include condition and shipping info
- **Location:** City/neighborhood, critical for local buyers
- **Category:** Select from Facebook's predefined categories
- **Condition:** New, Like New, Good, Fair (חדש, כמו חדש, מצב טוב, סביר)

### Seller Requirements
- Personal Facebook account in good standing (no business license required)
- For shops: Facebook Commerce Manager setup; payment is collected on the merchant's own external checkout, not in-app (Israeli Shops have no native checkout)
- Comply with Facebook Commerce Policies (no prohibited items)
- Identity verification may be required for high-volume sellers

### Fee Structure
- Free for personal listings (C2C)
- Shops: with checkout on the merchant's own site there is no Meta-hosted transaction for a selling fee to attach to, so the fee that actually hits the margin is whatever the merchant's own payment provider charges. Meta's checkout-change page does not discuss selling fees, so confirm any current Meta fee in Commerce Manager rather than assuming there is none.
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

> **Checkout change:** the same September 2025 change covers Instagram Shops. Product tags still work for discovery, but tapping a tagged product sends the buyer to the merchant's external website to complete the purchase. There is no in-app Instagram checkout for new orders. Plan for an external e-commerce site plus an Israeli payment provider.

### Listing Format
- **Photos/Videos:** high-quality square or vertical visual content sized for feed display. Confirm current minimum dimensions in Meta's own media specs rather than assuming a fixed pixel floor.
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
- Product eligibility is restricted and the rules drift; check Meta's current commerce eligibility requirements for the seller's category rather than assuming a fixed physical-goods-only rule.

### Fee Structure
- No listing fee for organic posts
- Sales go through the merchant's external site, so the transaction fee is the merchant's own payment provider's. Confirm any current Meta fee in Commerce Manager.
- Promoted posts: paid advertising (CPC/CPM model via Ads Manager)
- Payment fees are whatever the merchant's own checkout provider charges

### Automation
- Instagram Graph API for posting and product tagging (discovery only)
- Product catalog managed through Facebook Commerce Manager API
- Insights API for engagement analytics; sales/conversion data now lives in the merchant's own store
- Scheduled posting via Business Suite or third-party tools

## Cross-Platform Comparison

| Feature | Zap | Yad2 | Facebook | Instagram |
|---------|-----|------|----------|-----------|
| Listing cost | Fixed monthly + per-click (comparison) OR per-sale commission by category (marketplace) | Free basic listing; paid promotion / business store | Free (C2C) / catalog free | Free |
| Audience | Price-conscious tech buyers | Broad general buyers (all categories) | Local community | Visual / lifestyle |
| Best for | Electronics, appliances | Second-hand goods, vehicles, general items | General items, local | Fashion, lifestyle, visual |
| Hebrew support | Full | Full | Full | Full |
| API available | No (store management dashboard only) | No (site only) | Graph API (catalog only) | Graph API (catalog only) |
| Payment processing | Zap checkout / external | Off-platform (Bit / PayBox / cash) | Merchant's own site (no native checkout for Israeli sellers) | Merchant's own site (no native checkout for Israeli sellers) |
| Shipping integration | External | Seller managed / courier | Seller managed | Seller managed |

(KSP is omitted from this table: it is a first-party retailer, not a third-party seller platform, so use it only as a price-comparison reference.)
