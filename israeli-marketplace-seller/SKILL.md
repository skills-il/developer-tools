---
name: israeli-marketplace-seller
description: Manage online selling across Israeli marketplaces (Zap, KSP, Facebook Marketplace, and Instagram Shopping). Use when user asks about "sell on Zap", "Facebook Marketplace Israel", "Instagram Shopping Israel", "online selling Israel", "price comparison KSP", "product listing Hebrew", or "מכירה אונליין". Covers product listing creation, competitor price monitoring, inventory sync, review management, sales analytics, business-registration (osek murshe/patur) and consumer-protection obligations across Israeli marketplaces. Do NOT use for international marketplaces (Amazon, eBay) or physical store operations.
license: MIT
allowed-tools: Bash(python:*) WebFetch
compatibility: Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, OpenClaw, Antigravity, Gemini CLI. OpenClaw recommended for scheduled price monitoring and multi-platform inventory sync.
---


# Israeli Marketplace Seller

## Instructions

### Step 1: Create Product Listings
Help the user create Hebrew product listings with the required fields: title, description, price (NIS), photos, category, condition, and shipping options. Format listings according to each platform's requirements:

| Platform | Format | Listing Style | Key Requirements |
|----------|--------|---------------|------------------|
| Zap (זאפ) | Structured specs | Manufacturer, model, features, price comparison format | Full product specifications table, category-compliant |
| KSP | Specs table | Comparison-ready product data | Technical specs, model numbers, feature highlights |
| Facebook Marketplace (פייסבוק מרקטפלייס) | Casual | Photo-first, location-based Hebrew description | Clear photos, local area targeting, conversational tone |
| Instagram Shopping (אינסטגרם שופינג) | Visual-first | Short description, hashtags, story-friendly | High-quality images, Hebrew + English hashtags, shopping tags |

SEO optimization:
- Use common Israeli search terms in both Hebrew and transliterated English (e.g., "סמסונג גלקסי" and "Samsung Galaxy")
- Include model numbers, colors, and condition in title
- Add relevant Hebrew keywords to description: חדש, משלוח חינם, אחריות, מבצע

See references/platform-guides.md for detailed listing format specifications per platform.

### Step 2: Monitor Competitor Prices
Track competitor pricing across Zap and KSP to maintain competitive positioning:
- Read publicly listed prices from Zap and KSP product pages. Prefer an official partner API where one is available (KSP offers a partner API for approved vendors); otherwise read the public product pages with a clearly identified client.
- Track top 5 competitors per product, store price, seller name, shipping cost, and rating
- Alert when a competitor drops price below yours (configurable threshold, default: 5%)
- Generate weekly price comparison report with trends and recommendations
- Suggest optimal pricing based on competitor landscape, your margins, and market demand

Price monitoring schedule and access etiquette:
- Default polling interval: every 4 hours. Keep request volume low and well-spaced.
- Respect each site's Terms of Service and `robots.txt`. Do not try to evade rate limits or bot protection (no user-agent spoofing, no CAPTCHA bypass). If a site blocks automated access, switch to a manual check or an official data feed.
- Store price history in persistent memory or export to `price-history.json`
- Flag unusual patterns: sudden drops (clearance?), coordinated increases, new entrants

### Step 3: Sync Inventory Across Platforms
Maintain a single source of truth for inventory across all connected platforms:
- Keep a master inventory count per product (SKU-based)
- When an item sells on one platform, immediately update availability on all others
- Alert when stock reaches configurable low threshold (default: 2 units)
- Handle platform-specific inventory management:
  - **Zap:** Update listing status (in stock / out of stock)
  - **KSP:** Update availability flag
  - **Facebook Marketplace:** Mark post as sold or update quantity
  - **Instagram Shopping:** Update product catalog availability

Use optimistic locking to prevent overselling on simultaneous purchases.

**Where the sale actually closes (2025 change):** Meta removed native checkout from Facebook and Instagram Shops (phase-out began June 2025, fully deprecated September 4, 2025). Facebook/Instagram now only drive discovery; the buyer is redirected to the merchant's own website to pay. If the user runs a Facebook or Instagram Shop, the real inventory source of truth, order management, and payment all live on their own e-commerce site, and the Meta catalog is just a mirror for product tags. Facebook Marketplace C2C personal listings were never a native-checkout flow and are unaffected (buyer and seller arrange payment directly).

### Step 4: Manage Customer Inquiries
Centralize and manage incoming messages from all platforms:
- Monitor messages from Zap, Facebook Marketplace, and Instagram in one place
- Auto-categorize inquiries: price question (שאלת מחיר), availability (זמינות), shipping (משלוח), negotiation (מיקוח)
- Draft Hebrew responses for common inquiry types:
  - **Price:** "המחיר הוא [PRICE] ש\"ח. המחיר כולל/לא כולל משלוח."
  - **Availability:** "המוצר זמין במלאי ומוכן למשלוח מיידי."
  - **Shipping:** "משלוח לכל הארץ תוך [DAYS] ימי עסקים. עלות משלוח: [COST] ש\"ח."
  - **Negotiation:** "תודה על ההצעה. המחיר הטוב ביותר שאני יכול להציע הוא [PRICE] ש\"ח."
- Track response time per platform, aim for under 1 hour during business hours (09:00-21:00 Israel time)

### Step 5: Monitor Reviews and Reputation
Track seller reputation and customer feedback across all platforms:
- Aggregate seller ratings from Zap (seller score), Facebook (marketplace rating), and Instagram (shop reviews)
- Alert immediately on negative feedback (rating below 3 stars or negative comment)
- Draft professional Hebrew responses to reviews:
  - **Positive:** "תודה רבה על הביקורת החיובית! שמחים שנהנית מהמוצר."
  - **Negative:** "מצטערים לשמוע על חוויה שלילית. נשמח לפתור את הבעיה, אנא צרו איתנו קשר ב-[CONTACT]."
- Track trends over time: average rating, common complaints, satisfaction by product category
- Monthly reputation summary with actionable insights

### Step 6: Track Sales Analytics
Provide comprehensive sales data and insights across all platforms:
- Revenue by platform and by product (in NIS)
- Profit margins after platform fees (Zap listing fees, Facebook/Instagram commission)
- Best selling items ranked by units and by revenue
- Time-based trends: daily, weekly, monthly sales patterns
- Conversion rates per platform: views to inquiries to sales ratio
- Monthly performance summary with month-over-month comparison

Report format:
```
Platform    | Sales | Revenue (NIS) | Avg Order | Margin
------------|-------|---------------|-----------|-------
Zap         |    8  |       22,000  |    2,750  |   18%
Facebook    |   15  |       12,000  |      800  |   22%
Instagram   |    3  |        4,500  |    1,500  |   20%
------------|-------|---------------|-----------|-------
Total       |   26  |       38,500  |    1,481  |   20%
```

### Step 7: Confirm Business Registration Status

Before helping someone sell regularly online, confirm they are set up legally. Selling goods as an ongoing activity in Israel is a business, and a business must be registered.

- **Osek patur (עוסק פטור):** for low annual turnover (the threshold is set yearly by the Tax Authority). Does not charge or remit VAT, but still must register and report.
- **Osek murshe (עוסק מורשה):** required above the osek-patur turnover threshold, or by default for certain professions. Charges 18% VAT on sales, files periodic VAT returns, and can deduct input VAT.
- **The exception:** genuinely occasional, personal C2C sales (selling your own used phone on Facebook Marketplace) are not a business and do not require registration. The line is "regular, profit-seeking activity" vs "clearing out personal items".
- A registered osek is also what platforms like Zap and KSP require for a seller account, and it is what makes the consumer-protection obligations in Step 8 enforceable against the seller.

If the user is unsure which status applies or where their turnover lands, tell them to confirm with an accountant or the Israel Tax Authority. Do not guess the current thresholds, they change yearly.

### Step 8: Apply Consumer-Protection and Returns Rules

Israeli online selling is governed by the Consumer Protection Law (חוק הגנת הצרכן), and its remote-sale (מכר מרחוק) rules apply to every marketplace sale, not just sales on the seller's own site.

- **14-day cooling-off period:** for most remote purchases the buyer may cancel within 14 days of receiving the product (or of receiving the disclosure document, whichever is later). Some categories are exempt (perishables, custom-made goods, opened software/media). Refund timelines and a possible cancellation fee are capped by law.
- **Mandatory disclosure:** the seller must give the buyer, in writing, the business details, the main product characteristics, the full price including VAT, shipping costs, and the cancellation-right terms. Publish a clear return policy on every listing.
- **Refund timeline:** once a valid cancellation is made, the refund must be issued within the period set by law, and the seller may only deduct the limited cancellation fee the law allows.
- Draft return policies and cancellation responses that state these rights plainly in Hebrew. Do not write a return policy that is more restrictive than the law allows, it is unenforceable and exposes the seller.
- For specifics (current cooling-off exemptions, fee caps, exact timelines), point the user to the Consumer Protection Law text and the Consumer Protection and Fair Trade Authority. Do not invent numbers.

## Examples

### Example 1: Listing a Product Across All Platforms
User says: "I want to sell a Samsung Galaxy S24 on Zap, Facebook, and Instagram"
Actions:
1. Create master listing with specs, price, photos
2. Format for Zap (structured specs, price comparison format, category: smartphones)
3. Create Facebook Marketplace post (casual Hebrew description, Tel Aviv area, 6 photos)
4. Create Instagram Shopping post (visual carousel, Hebrew + English hashtags)
5. Set up competitor price monitoring on Zap for Galaxy S24
6. Configure inventory tracking (1 unit across 3 platforms)
Result: Product listed on 3 platforms. Zap listing shows competitive pricing at 3,200 NIS (market average: 3,350 NIS). Facebook and Instagram posts published with Hebrew descriptions. Price alert set for any competitor below 3,100 NIS.

### Example 2: Competitor Dropped Their Price
User says: "Someone on Zap is now selling the same item for 200 NIS less than me"
Actions:
1. Pull competitor listing details and price history from monitoring data
2. Check if it's a one-time clearance or permanent price drop (review 7-day trend)
3. Analyze your margins, calculate break-even and minimum viable price
4. Present options: match price, partial match, add value (bundle, warranty, free shipping)
5. If adjusting: update price across all platforms simultaneously via inventory sync
Result: Analysis shows competitor's lower price is from a temporary clearance (stock of 2 units). Recommendation: hold current price but add free shipping as a value proposition. Updated listings with "משלוח חינם!" across all platforms.

### Example 3: Monthly Sales Report Across Platforms
User says: "Give me a breakdown of my sales this month"
Actions:
1. Pull sales data from all connected platforms for the current month
2. Calculate totals: 15 sales on Facebook (12,000 NIS), 8 on Zap (22,000 NIS), 3 on Instagram (4,500 NIS)
3. Calculate profit margins after platform fees per channel
4. Identify best-performing products and platforms
5. Generate month-over-month comparison with previous period
Result: Total monthly revenue: 38,500 NIS across 26 sales. Zap has highest average order value (2,750 NIS). Facebook has most volume. Top product: Galaxy S24 (8 units sold). Suggested focus: list more electronics on Zap for higher margins.

## Bundled Resources

### References
- `references/platform-guides.md`, Integration guides for Zap, KSP, Facebook Marketplace Israel, and Instagram Shopping. Covers listing formats, pricing structures, seller dashboards, the 2025 Meta native-checkout removal, and API/automation capabilities per platform. Consult when creating listings in Step 1 or monitoring prices in Step 2.

## Gotchas

- Israeli marketplace platforms use NIS pricing that must include 18% VAT (raised from 17% on 2025-01-01) for any seller registered as osek murshe. Agents may list prices excluding VAT or using the outdated 17% rate, which is illegal for consumer-facing listings.
- Israeli classifieds and local selling happen on Israeli platforms (Zap, KSP, Facebook Marketplace, Yad2), not Craigslist or eBay. This skill covers Zap, KSP, Facebook Marketplace, and Instagram Shopping. Yad2 is a large Israeli classifieds site but is out of scope here; do not assume its listing format matches the platforms above, and do not recommend international platforms for Israeli local selling.
- Israeli marketplace shipping typically uses Israel Post or courier services (Mahirpak, ShipBob IL), not FedEx/UPS for domestic orders. Agents may recommend international carriers with higher costs.
- Product descriptions on Israeli marketplaces should be in Hebrew first, with English optional. Agents may default to English-first content that gets less visibility.
- Israeli consumer protection law applies to all marketplace sales, including the 14-day cooling-off period for remote purchases. Agents may not mention this legal obligation for sellers. See Step 8.
- **Meta removed native checkout in 2025.** Facebook and Instagram Shops no longer process payments in-app (deprecated September 4, 2025). Since Meta no longer collects money for the seller, plan a separate payment-collection path: an external e-commerce site checkout for Shops, or, for Facebook Marketplace C2C, a direct Israeli payment method between buyer and seller (Bit, PayBox, bank transfer, or credit-card clearing via the seller's own provider). Agents may still assume an in-app Instagram/Facebook checkout that no longer exists.

## Troubleshooting

### Error: "Zap listing rejected"
Cause: Listing doesn't meet Zap's product specifications format or category requirements.
Solution: Verify product category exists on Zap. Ensure all required specification fields are filled (manufacturer, model, key specs). Check Hebrew text encoding. Zap is strict about duplicate listings, search for existing listings first.

### Error: "Facebook Marketplace post not visible"
Cause: Post may be in review, violates Marketplace policies, or account has restrictions.
Solution: Check account standing in Facebook's Commerce Manager. Verify post doesn't violate prohibited items list. Wait 24 hours for review. If recurring, check if the account needs identity verification.

### Error: "Inventory sync conflict"
Cause: Simultaneous sales on multiple platforms or manual update while sync is running.
Solution: Use optimistic locking. If a conflict is detected, fetch latest state from all platforms, reconcile, and update. For single-item listings, immediately mark as sold on all platforms when first sale confirms.

### Error: "Price monitoring blocked"
Cause: Reading marketplace pages too frequently triggers rate limiting or CAPTCHA.
Solution: Reduce polling frequency (minimum 4 hours between checks) and keep requests well-spaced. Respect `robots.txt` and each site's Terms of Service. Do not attempt to evade the block (no user-agent spoofing, no CAPTCHA bypass). Prefer an official partner data feed where one exists (KSP offers a partner API for approved vendors). If automated access stays blocked, fall back to a manual periodic check.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Zap, add a store | https://www.zap.co.il/joinzap.aspx | Seller onboarding, commission model, management dashboard |
| Meta, changes to Shops and Checkout | https://www.facebook.com/business/help/1314349509894768 | Native checkout deprecation, external-checkout migration |
| Instagram Shopping for business | https://business.instagram.com/shopping | Catalog setup, product tags, eligibility |
| Israel Tax Authority | https://www.gov.il/he/departments/israel_tax_authority | Osek patur vs murshe, current turnover thresholds, VAT |
| Consumer Protection and Fair Trade Authority | https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority | Remote-sale rules, 14-day cooling-off, mandatory disclosure |
| Israel Post business shipping | https://www.israelpost.co.il | Domestic shipping options and rates for marketplace orders |

## Recommended MCP Servers

There is no MCP server specific to Israeli marketplaces (Zap, KSP, Facebook Marketplace, Instagram Shopping). None of these platforms publishes an MCP integration, and no community MCP wraps them. Do not invent or recommend one. Use this skill's guidance directly, the official partner APIs where they exist (KSP partner API, Meta Graph API for catalog management), and a general browser-automation tool for reading public listing pages within each site's Terms of Service.