---
name: israeli-marketplace-seller
description: >-
  Manage online selling across Israeli marketplaces — Zap, KSP, Facebook
  Marketplace, and Instagram Shopping. Use when user asks about "sell on Zap",
  "Facebook Marketplace Israel", "Instagram Shopping Israel", "online selling
  Israel", "price comparison KSP", "product listing Hebrew", or "מכירה
  אונליין". Covers product listing creation, competitor price monitoring,
  inventory sync, review management, and sales analytics across Israeli
  marketplaces. Do NOT use for international marketplaces (Amazon, eBay) or
  physical store operations.
license: MIT
allowed-tools: "Bash(python:*) WebFetch"
compatibility: >-
  Works with Claude Code, OpenClaw, Cursor. OpenClaw recommended for scheduled
  price monitoring and multi-platform inventory sync.
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    - marketplace
    - ecommerce
    - zap
    - selling
    - price-comparison
    - israel
  display_name:
    he: מוכר בשווקים מקוונים ישראליים
    en: Israeli Marketplace Seller
  display_description:
    he: ניהול מכירות אונליין בשווקים ישראליים — זאפ, KSP, פייסבוק מרקטפלייס ואינסטגרם שופינג
    en: >-
      Manage online selling across Israeli marketplaces — Zap, KSP, Facebook
      Marketplace, and Instagram Shopping.
  openclaw:
    requires:
      bins: []
      env: []
    emoji: "🛒"
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
- Use browser automation (CDP) to scrape current prices from Zap and KSP product pages
- Track top 5 competitors per product — store price, seller name, shipping cost, and rating
- Alert when a competitor drops price below yours (configurable threshold, default: 5%)
- Generate weekly price comparison report with trends and recommendations
- Suggest optimal pricing based on competitor landscape, your margins, and market demand

Price monitoring schedule:
- Default polling interval: every 4 hours (respect rate limits)
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

### Step 4: Manage Customer Inquiries
Centralize and manage incoming messages from all platforms:
- Monitor messages from Zap, Facebook Marketplace, and Instagram in one place
- Auto-categorize inquiries: price question (שאלת מחיר), availability (זמינות), shipping (משלוח), negotiation (מיקוח)
- Draft Hebrew responses for common inquiry types:
  - **Price:** "המחיר הוא [PRICE] ש\"ח. המחיר כולל/לא כולל משלוח."
  - **Availability:** "המוצר זמין במלאי ומוכן למשלוח מיידי."
  - **Shipping:** "משלוח לכל הארץ תוך [DAYS] ימי עסקים. עלות משלוח: [COST] ש\"ח."
  - **Negotiation:** "תודה על ההצעה. המחיר הטוב ביותר שאני יכול להציע הוא [PRICE] ש\"ח."
- Track response time per platform — aim for under 1 hour during business hours (09:00-21:00 Israel time)

### Step 5: Monitor Reviews and Reputation
Track seller reputation and customer feedback across all platforms:
- Aggregate seller ratings from Zap (seller score), Facebook (marketplace rating), and Instagram (shop reviews)
- Alert immediately on negative feedback (rating below 3 stars or negative comment)
- Draft professional Hebrew responses to reviews:
  - **Positive:** "תודה רבה על הביקורת החיובית! שמחים שנהנית מהמוצר."
  - **Negative:** "מצטערים לשמוע על חוויה שלילית. נשמח לפתור את הבעיה — אנא צרו איתנו קשר ב-[CONTACT]."
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
3. Analyze your margins — calculate break-even and minimum viable price
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
- `references/platform-guides.md` — Integration guides for Zap, KSP, Facebook Marketplace Israel, and Instagram Shopping. Covers listing formats, pricing structures, seller dashboards, and API/automation capabilities per platform. Consult when creating listings in Step 1 or monitoring prices in Step 2.

## Troubleshooting

### Error: "Zap listing rejected"
Cause: Listing doesn't meet Zap's product specifications format or category requirements.
Solution: Verify product category exists on Zap. Ensure all required specification fields are filled (manufacturer, model, key specs). Check Hebrew text encoding. Zap is strict about duplicate listings — search for existing listings first.

### Error: "Facebook Marketplace post not visible"
Cause: Post may be in review, violates Marketplace policies, or account has restrictions.
Solution: Check account standing in Facebook's Commerce Manager. Verify post doesn't violate prohibited items list. Wait 24 hours for review. If recurring, check if the account needs identity verification.

### Error: "Inventory sync conflict"
Cause: Simultaneous sales on multiple platforms or manual update while sync is running.
Solution: Use optimistic locking — if conflict detected, fetch latest state from all platforms, reconcile, and update. For single-item listings, immediately mark as sold on all platforms when first sale confirms.

### Error: "Price monitoring blocked"
Cause: Too frequent scraping triggers rate limiting or CAPTCHA on marketplace sites.
Solution: Reduce polling frequency (minimum 4 hours between checks). Use browser automation with human-like patterns. Rotate user agents. Respect robots.txt directives.
