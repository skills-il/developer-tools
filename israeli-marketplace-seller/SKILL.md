---
name: israeli-marketplace-seller
description: Manage online selling across Israeli marketplaces (Zap, Yad2, Facebook Marketplace, and Instagram Shopping). Use when user asks about "sell on Zap", "sell on Yad2", "Facebook Marketplace Israel", "Instagram Shopping Israel", "online selling Israel", "product listing Hebrew", or "מכירה אונליין". Covers product listing creation, competitor price monitoring (including against retailers like KSP), inventory sync, review management, sales analytics, business registration (osek murshe/patur), tax-invoice and Israel-Invoice (allocation-number) obligations, and consumer-protection rules across Israeli marketplaces. Do NOT use for international marketplaces (Amazon, eBay) or physical store operations.
license: MIT
allowed-tools: WebFetch
compatibility: Works with Claude Code, Cursor, GitHub Copilot, Windsurf, OpenCode, Codex, OpenClaw, Antigravity, Gemini CLI. OpenClaw recommended for scheduled price monitoring and multi-platform inventory sync.
---


# Israeli Marketplace Seller

## Instructions

### Step 1: Create Product Listings
Help the user create Hebrew product listings with the required fields: title, description, price (NIS), photos, category, condition, and shipping options. Format listings according to each platform's requirements:

| Platform | Format | Listing Style | Key Requirements |
|----------|--------|---------------|------------------|
| Zap (זאפ) | Structured specs | Manufacturer, model, features, price comparison format | Full product specifications table, category-compliant |
| Yad2 (יד2) | Title + photos + price | Israel's dominant general marketplace (C2C and business); category-driven, location-based Hebrew listing | Clear photos, accurate category, Hebrew title with model/condition |
| Facebook Marketplace (פייסבוק מרקטפלייס) | Casual | Photo-first, location-based Hebrew description | Clear photos, local area targeting, conversational tone |
| Instagram Shopping (אינסטגרם שופינג) | Visual-first | Short description, hashtags, story-friendly | High-quality images, Hebrew + English hashtags, shopping tags |

Note: **KSP is a first-party electronics retailer ("the Israeli Amazon"), not a third-party seller marketplace.** You cannot list your own products on KSP; treat it only as a competitor whose retail prices you compare against (Step 2). KSP runs an affiliate/referral program, not a vendor-selling program.

**Establish early whether the seller has their own e-commerce site, because it selects which channels are open.** Ask before planning:
- **Zap runs two different models, and only one of them needs a site.** For the price-comparison system you must have a commerce site that ships orders, including online credit-card clearing, and adapted for mobile display; Zap then refers buyers to that site. For the **Zap marketplace** you sell inside zap.co.il itself, and Zap states you need only to hold stock and supply the products, with no online store of your own required. So a seller with no site is not shut out of Zap, they belong on the marketplace model.
- **Facebook and Instagram Shops** send the buyer to the merchant's own site to pay (see Step 3), so they do need a checkout URL configured in Commerce Manager.
- **Yad2 and Facebook Marketplace** C2C listings need no storefront either.
Pick the model that matches what the seller actually has, rather than assuming a storefront is a precondition for selling online in Israel.

SEO optimization:
- Use common Israeli search terms in both Hebrew and transliterated English (e.g., "סמסונג גלקסי" and "Samsung Galaxy")
- Include model numbers, colors, and condition in title
- Add relevant Hebrew keywords to description: חדש, משלוח חינם, אחריות, מבצע

See references/platform-guides.md for detailed listing format specifications per platform.

### Step 2: Monitor Competitor Prices
Track competitor pricing across Zap (the price-comparison aggregator) and KSP (a large first-party retailer) to maintain competitive positioning:
- Read publicly listed prices from Zap and KSP product pages with a clearly identified client. Neither offers a public third-party "seller" API for this (KSP is first-party retail and runs only an affiliate program), so use the official seller integrations where they exist (a Zap store gets a management dashboard, ממשק ניהול, reporting its sales and referred traffic) and otherwise read public pages within each site's Terms of Service. Do not assume a bulk product feed exists on a platform until you have seen it documented in that platform's own seller materials.
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
  - **Yad2:** Mark the listing sold / remove it, or update quantity
  - **Facebook Marketplace:** Mark post as sold or update quantity
  - **Instagram Shopping:** Update product catalog availability

Use optimistic locking to prevent overselling on simultaneous purchases.

**Where the sale actually closes:** Facebook and Instagram Shops drive discovery; the buyer is redirected to the merchant's own website to pay. (Meta's help centre states that as of September 2025 Shops on both platforms use website checkout. Whatever a given shop did before, the checkout for an Israeli seller now lives on their own site, and a shop that has not migrated must create a checkout URL.) If the user runs a Facebook or Instagram Shop, the real inventory source of truth, order management, and payment all live on their own e-commerce site, and the Meta catalog is just a mirror for product tags. Facebook Marketplace C2C personal listings in Israel are unaffected: buyer and seller arrange payment directly.

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
- Profit margins after platform fees. Charge the fees that actually apply per channel: Zap takes a monthly listing fee plus per-click on the comparison model, or a category-dependent per-sale commission on its marketplace. For Facebook and Instagram, **the fee to deduct is the merchant's own payment-provider fee**, because the transaction now happens on the merchant's site rather than on Meta. Do not deduct a Meta sale commission you have not confirmed; check current fees in Commerce Manager.
- Best selling items ranked by units and by revenue
- Time-based trends: daily, weekly, monthly sales patterns
- Conversion rates per platform: views to inquiries to sales ratio
- Monthly performance summary with month-over-month comparison

Report format:
```
Platform    | Sales | Revenue (NIS) | Avg Order | Margin
------------|-------|---------------|-----------|-------
Zap         |    8  |       22,000  |    2,750  |   18%
Yad2        |   11  |        9,900  |      900  |   24%
Facebook    |   15  |       12,000  |      800  |   22%
Instagram   |    3  |        4,500  |    1,500  |   20%
------------|-------|---------------|-----------|-------
Total       |   37  |       48,400  |    1,308  |   21%

(Illustrative shape only. These are not benchmarks, use the seller's own figures.)
```

### Step 7: Confirm Business Registration Status

Before helping someone sell regularly online, confirm they are set up legally. Selling goods as an ongoing activity in Israel is a business, and a business must be registered.

- **Osek patur (עוסק פטור):** for low annual turnover, up to NIS 122,833 in 2026 (NIS 120,000 in 2025). The ceiling is re-set yearly, so re-check it each January. Does not charge or remit VAT, but still must register and report. Some professions must register as osek murshe regardless of turnover.
- **Osek murshe (עוסק מורשה):** required above the osek-patur turnover threshold, or by default for certain professions. Charges 18% VAT on sales, files periodic VAT returns, and can deduct input VAT.
- **The exception:** genuinely occasional, personal C2C sales (selling your own used phone on Facebook Marketplace) are not a business and do not require registration. The line is "regular, profit-seeking activity" vs "clearing out personal items".
- A registered osek is also what a business seller account on platforms like Zap requires, and it is what makes the consumer-protection obligations in Step 8 enforceable against the seller.
- **Document every sale, but issue the RIGHT document.** The two statuses do not use the same paperwork, and getting this backwards is a reporting error, not a style choice:
  - An **osek murshe** issues a tax invoice (חשבונית מס) showing the 18% VAT, plus a receipt (קבלה) when paid.
  - An **osek patur** is **not permitted to issue a חשבונית מס at all**. It issues a payment demand (חשבונית עסקה) and a receipt (קבלה) immediately on receiving payment.
  This applies to marketplace sales, not only sales on the seller's own site.
- **Israel Invoice (חשבוניות ישראל) allocation number.** Under the 2024 reform, a tax invoice above a threshold needs a real-time allocation number (מספר הקצאה) from the Tax Authority, or **the buyer** cannot deduct the input VAT. The threshold has been ratcheting down and the current step is already in force: **from 01.06.2026 it is NIS 5,000 before VAT.** Earlier invoices go by the threshold in force when they were issued (NIS 10,000 for first-half-2026 invoices, NIS 20,000 for 2025, NIS 25,000 for 2024). An allocation number can be requested retroactively up to a year after the invoice was issued, but past six months it needs a VAT manager's approval.
  This bites on **B2B sales only**, since it governs the buyer's input-VAT deduction, so a seller whose buyers are consumers will rarely meet it. It never applies to an osek patur, who cannot issue a חשבונית מס in the first place.
- **Register with all three authorities, not just VAT.** Opening a business means מע"מ, מס הכנסה, and ביטוח לאומי. Business buyers routinely ask for an אישור ניהול ספרים (bookkeeping-compliance certificate) before they will pay an invoice, so tell the user to obtain one early.

If the user is unsure which status applies or where their turnover lands, tell them to confirm with an accountant or the Israel Tax Authority. State the figures above with their year attached, and do not project them forward into a year you have not checked.

### Step 8: Apply Consumer-Protection and Returns Rules

Israeli online selling is governed by the Consumer Protection Law (חוק הגנת הצרכן), and its remote-sale (מכר מרחוק) rules apply to every marketplace sale, not just sales on the seller's own site.

- **14-day cooling-off period:** the right to cancel exists from the moment the transaction is made and expires 14 days after the LATER of receiving the product or receiving the transaction document. Non-cancellable categories: goods that lose value quickly (flowers), goods made to the customer's special order, recordable or copyable goods whose original packaging the buyer opened (a book, a disc), and **digital information** (a file or e-book stored on a computer or storage medium), which is its own category and does not depend on packaging.
- **Cancellation notice can be oral.** It does not have to be in writing or on the seller's form. If the sale was made through a website, that site's **home page must carry a link for sending a cancellation notice**. A seller operating their own storefront (which Zap price-comparison and Meta Shops both require) owes this link.
- **Refund deadline: 14 days from the day the seller received the cancellation notice.** This is the hardest deadline the seller owes. For a continuing service, refund only the unused portion.
- **Cancellation fee, and when it may not be charged at all.** On an ordinary change of mind the seller may deduct up to **5% of the price of the goods or the transaction, or NIS 100, whichever is lower**, and nothing beyond that. But the fee is **forbidden entirely** where the buyer cancelled because of a defect, a mismatch between the goods or service and the information the seller gave, non-delivery on the agreed date, or any other breach of the transaction terms by the seller. Never draft a policy that charges a cancellation fee on a defect return.
- **Who pays return shipping, and it follows the same split.** On a cancellation for any reason OTHER than seller breach, **the consumer returns the product at the consumer's own expense**. Where the cancellation IS due to seller breach (defect, late delivery, non-conformity), the consumer returns it **at the place it was delivered**, meaning the seller collects it from the buyer's home at the seller's cost. Say which case applies in the return policy; a policy that stays silent concedes a cost the seller need not bear.
- **Mandatory disclosure, in writing, and it is longer than most sellers think.** The buyer must be given: the seller's name, ID or osek number, and address in Israel (and abroad if applicable); the main characteristics of the goods or service; the full price including VAT and shipping costs; the date and method of delivery; the period the offer stays valid; the terms of the cancellation right; and warranty details. A separate written document carrying this plus the manufacturer's name and country of manufacture and how to exercise cancellation must reach the buyer **no later than the time of delivery**. For a business (non-C2C) seller, the osek number and business address belong on the listing itself.
- **Extended cancellation populations, and the condition that gates them:** a consumer who is a person with a disability, is **65 or older**, or is a new immigrant may cancel within **4 months** of the agreement, of delivery, or of receiving the disclosure document, whichever is later. It applies where a conversation took place with a representative of the business during the transaction, and **a conversation means by phone, chat, email, or any other electronic exchange**, not a phone call only. Since marketplace sellers answer buyer questions by DM and email constantly, treat this as the common case rather than an edge case. The seller may require one document proving the consumer's status.
- **What it costs to get this wrong.** A consumer can sue for the refund and, on top of it, statutory damages of **up to NIS 10,000 without proving any damage at all**, and can complain to the Consumer Protection and Fair Trade Authority.
- Draft return policies and cancellation responses that state these rights plainly in Hebrew. Do not write a return policy more restrictive than the law allows, it is unenforceable and exposes the seller.
- Note the regime attaches to Israeli websites. For specifics not stated above (the cancellation clocks for services, courses, hospitality and continuing services, which differ from the goods rule above), point the user to the Consumer Protection Law text and the Authority. Do not invent numbers.

## Examples

### Example 1: Listing a Product Across All Platforms
User says: "I want to sell a Samsung Galaxy S24 on Zap, Yad2, Facebook, and Instagram"
Actions:
1. Create master listing with specs, price, photos
2. Ask which Zap model fits: the seller has a commerce site with online card clearing, so the price-comparison model is open to them. Without one, route them to the Zap marketplace instead, which needs no store of their own.
3. Format for Zap (structured specs, price comparison format, category: smartphones)
4. Create the Yad2 listing (Hebrew title carrying model and condition, accurate category, location, clear photos). No storefront needed, so this is the channel that works even for a seller with no site.
5. Create Facebook Marketplace post (casual Hebrew description, Tel Aviv area, 6 photos)
6. Create Instagram Shopping post (visual carousel, Hebrew + English hashtags)
7. Set up competitor price monitoring on Zap for Galaxy S24
8. Configure inventory tracking (1 unit across 4 platforms). With one unit, whichever channel sells first must immediately close the listing on the other three.
Result: Product listed on 4 platforms. Zap listing shows competitive pricing at 3,200 NIS (market average: 3,350 NIS). Facebook and Instagram posts published with Hebrew descriptions. Price alert set for any competitor below 3,100 NIS.

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
2. Calculate totals: 15 sales on Facebook (12,000 NIS), 11 on Yad2 (9,900 NIS), 8 on Zap (22,000 NIS), 3 on Instagram (4,500 NIS)
3. Calculate profit margins after platform fees per channel
4. Identify best-performing products and platforms
5. Generate month-over-month comparison with previous period
Result: Total monthly revenue: 48,400 NIS across 37 sales. Zap has highest average order value (2,750 NIS). Facebook has most volume, with Yad2 second. Top product: Galaxy S24 (8 units sold). Suggested focus: list more electronics on Zap for higher margins.

## Bundled Resources

### References
- `references/platform-guides.md`, Integration guides for Zap, Yad2, Facebook Marketplace Israel, and Instagram Shopping (plus KSP as a price-comparison reference). Covers listing formats, pricing structures, seller dashboards, the Meta external-checkout reality, and API/automation capabilities per platform. Consult when creating listings in Step 1 or monitoring prices in Step 2.

## Gotchas

- Israeli marketplace platforms use NIS pricing that must include VAT at the current 18% rate for any seller registered as osek murshe. The rate was raised in recent years, so agents may quote a lower legacy rate, or list prices excluding VAT altogether. Either is illegal for a consumer-facing listing. Re-check the rate in force rather than reusing one from memory.
- Israeli classifieds and local selling happen on Israeli platforms (Zap, Yad2, Facebook Marketplace), not Craigslist or eBay. This skill covers Zap, Yad2, Facebook Marketplace, and Instagram Shopping. KSP is a first-party electronics retailer ("the Israeli Amazon"), NOT a third-party seller marketplace, so you compare prices against it (Step 2) but cannot list your own products on it. Do not recommend international platforms for Israeli local selling.
- Israeli marketplace shipping typically uses Israel Post or domestic couriers (HFD, Cheetah/צ'יטה, Baldar) and pickup-locker networks, not FedEx/UPS for domestic orders. Agents may recommend international carriers with higher costs.
- Product descriptions on Israeli marketplaces should be in Hebrew first, with English optional. Agents may default to English-first content that gets less visibility.
- Israeli consumer protection law applies to all marketplace sales, including the 14-day cooling-off period for remote purchases. Agents may not mention this legal obligation for sellers. See Step 8.
- **Plan a payment path outside Meta.** Facebook and Instagram Shops do not process payments in-app for Israeli sellers (as of September 2025 Meta's Shops use website checkout on both platforms). Plan a separate payment-collection path: an external e-commerce checkout for Shops, or, for Facebook Marketplace C2C, a direct Israeli method between buyer and seller (Bit, PayBox, bank transfer, or card clearing via the seller's own provider such as Tranzila, Cardcom, Meshulam, or Grow/PayPlus). Agents may wrongly assume an in-app Instagram/Facebook checkout.

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
Solution: Reduce polling frequency (minimum 4 hours between checks) and keep requests well-spaced. Respect `robots.txt` and each site's Terms of Service. Do not attempt to evade the block (no user-agent spoofing, no CAPTCHA bypass). Use an official seller integration where one exists (a Zap store has a management dashboard for its own sales and traffic data). KSP is first-party retail with no third-party seller API, so read only its public pages. If automated access stays blocked, fall back to a manual periodic check.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Zap, add a store | https://www.zap.co.il/joinzap.aspx | Seller onboarding, commission model, management dashboard |
| Yad2 | https://www.yad2.co.il/market | Israel's dominant general marketplace: posting a listing, categories, business accounts |
| Meta, changes to Shops and Checkout | https://www.facebook.com/business/help/1314349509894768 | Native checkout deprecation, external-checkout migration |
| Instagram Shopping for business | https://www.facebook.com/business/instagram | Catalog setup, product tags, eligibility |
| Israel Invoice (allocation number), Tax Authority | https://www.gov.il/he/pages/sa311225-1 | The allocation-number threshold schedule (10,000 from 01.01.2026, 5,000 from 01.06.2026, both before VAT) |
| Israel Tax Authority | https://www.gov.il/he/departments/israel_tax_authority | Osek patur vs murshe, current turnover thresholds, VAT |
| Consumer Protection and Fair Trade Authority | https://www.gov.il/he/departments/consumer_protection_and_fair_trade_authority | Remote-sale rules, 14-day cooling-off, mandatory disclosure |
| Israel Post business shipping | https://www.israelpost.co.il | Domestic shipping options and rates for marketplace orders |

## Recommended MCP Servers

There is no MCP server specific to Israeli marketplaces (Zap, Yad2, Facebook Marketplace, Instagram Shopping). None of these platforms publishes an MCP integration, and no community MCP wraps them. Do not invent or recommend one. Use this skill's guidance directly, the official integrations where they exist (the Zap store management dashboard, Meta Graph API for catalog management), and a general browser-automation tool for reading public listing pages within each site's Terms of Service.