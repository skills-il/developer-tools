---
name: israeli-product-price-comparator
description: Compare product prices across major Israeli retailers and e-commerce platforms including Zap.co.il, KSP, iDigital, Ivory, Bug, and more. Use when the user wants to find the best price for electronics, appliances, computers, or consumer goods in Israel, needs to compare local vs. import pricing, or wants guidance on price tracking tools and Israeli consumer protection rights. Do NOT use for comparing grocery or food prices, real estate, or financial products.
license: MIT
allowed-tools: WebFetch
---


# Israeli Product Price Comparator

## Instructions

### Step 1: Identify the Product and Category

Determine the exact product the user is looking for. Classify it into one of these categories:

- **Electronics**: smartphones, TVs, headphones, cameras, gaming consoles
- **Computers**: laptops, desktops, monitors, peripherals, components
- **Appliances**: refrigerators, washing machines, ovens, air conditioners
- **Home & Garden**: furniture, lighting, tools, garden equipment
- **Pharmacy & Health**: cosmetics, vitamins, personal care products

Ask clarifying questions if the product is ambiguous. Get the exact model number when possible, as Israeli retailers often carry different SKUs than international markets.

### Step 2: Search Zap.co.il as the Primary Comparison Source

Zap.co.il is Israel's dominant price comparison engine with over 2 million monthly visitors and thousands of partnered retailers.

1. **Search by product name or model number** at the Zap website
2. **Review the comparison table** which shows:
   - Store name and rating (1-5 stars based on user reviews)
   - Current price in NIS
   - Shipping cost and estimated delivery time
   - Whether the product is in stock
3. **Check the price history graph** on the product page to see price trends over the last 30/90/180 days
4. **Read store reviews** before recommending less-known retailers. Focus on stores with 4+ star ratings and 100+ reviews
5. **Note Zap's "lowest price" badge** which indicates the cheapest current offer

Key Zap categories with dedicated comparison engines:
- **Cellphones**: Available through Zap's cellphone section
- **Laptops**: Available through Zap's laptop section
- **TVs**: Available through Zap's TV section
- **Air Conditioners**: Available through Zap's air conditioning section

### Step 3: Check Major Retailer Direct Prices

Cross-reference Zap results with direct retailer websites, as some retailers offer exclusive online-only prices not listed on Zap:

**Electronics Specialists:**
- **KSP**: Israel's largest electronics retailer. Offers a price-match guarantee, matching any lower price from an authorized retailer. Check their "Daily Deals" section. KSP also has physical stores for pickup.
- **iDigital** (`https://www.idigital.co.il`): Apple Premium Reseller. Best for Apple products, often has bundle deals with AppleCare. Also carries Samsung, Bose, and other premium brands.
- **Ivory** (`https://www.ivory.co.il`): Wide electronics selection. Known for competitive pricing on computers and peripherals. Check their "Clearance" section for discounts.
- **Bug**: Strong in computer components and peripherals. Good for custom PC builds. Has a used/refurbished section.

**Home & Appliances:**
- **Home Center** (`https://www.homecenter.co.il`): Large home improvement retailer. Good for appliances, tools, and home equipment.
- **Machsanei Hashmal**: Electrical appliance warehouse. Often competitive on large appliances.
- **IKEA Israel**: Furniture and home goods with Israeli-specific pricing.
- **ACE** (`https://www.ace.co.il`): Hardware and home improvement. Check for seasonal sales.

**Pharmacy & Health:**
- **Super-Pharm** (`https://shop.super-pharm.co.il`): Israel's largest pharmacy chain. "1+1" and "1+50%" deals are common.
- **Be** (`https://www.bestore.co.il`): Pharmacy and beauty products, owned by Shufersal. Frequent promotions competing with Super-Pharm.

### Step 4: Evaluate Import vs. Local Purchase

For products that may be cheaper abroad, compare:

1. **AliExpress / Amazon Global**: Check the product price including shipping to Israel
2. **Customs duty calculation** (thresholds updated February 25, 2026 via executive order, raised from the previous $75 limit):
   - **Up to 130 USD**: Fully exempt from customs, VAT, and purchase tax
   - **130-500 USD**: VAT only (18%), no customs duty
   - **Above 500 USD**: Full customs + VAT + purchase tax (where applicable). Standard customs rate: 12% + 18% VAT (applied on product + shipping + customs)
   - Electronics: Often reduced or zero customs duty, but VAT still applies above the $130 threshold
   - The effective additional cost for products above $130 is approximately 18-30% of the declared value
3. **Warranty considerations**: Products bought internationally typically have no local warranty. Israeli retailers are required by law to provide warranty (minimum 1 year for electronics).
4. **Delivery time**: Local purchase is 1-5 days. International shipping is 2-6 weeks.

**Recommendation framework**:
- Buy locally if the price difference is less than 20% (warranty + delivery time value)
- Buy internationally if the price difference exceeds 30% and warranty is not critical
- For products priced under 130 USD internationally, always check AliExpress (no customs duty or VAT)

### Step 5: Leverage Price Tracking and Coupon Tools

**Price tracking:**
- **"Sham Ze Zol Yoter"** (There It's Cheaper) Chrome extension: Automatically shows price comparisons while browsing retailer sites
- **Zap price alerts**: Set up email notifications when a product drops below a target price
- **Last Price**: Alternative price comparison site with its own retailer network

**Coupon aggregators:**
- **TopCash** (`https://www.topcash.co.il`): Cashback platform (via American Express) offering 1-10% back from partnered retailers
- **Cashback.co.il** (`https://www.cashback.co.il`): Israel's largest independent cashback platform with 250,000+ users and 500+ partnered stores
- **Check retailer newsletters**: KSP, Ivory, and iDigital send weekly promotions to subscribers

**Best times to buy:**
- **Black Friday (November)**: Israeli retailers participate heavily. Discounts of 15-40% are common.
- **Singles Day (11.11)**: Best for AliExpress purchases with additional discounts
- **End of financial year (December)**: Retailers clear inventory
- **Model changeover periods**: Old model electronics drop 20-30% when new models launch (typically September for phones, January for TVs)

### Step 6: Apply Israeli Consumer Protection Rules

Inform the user of their rights under Israeli consumer protection law:

1. **Online purchases**: 14-day return policy from delivery date (Consumer Protection Law, Section 14C). The retailer may charge a cancellation fee of 5% of the purchase price or 100 NIS, whichever is lower. Exceptions apply for depreciable goods, opened software, and customized products.
2. **Physical store purchases**: 7-day return policy for products over 50 NIS, if the product is unused and in original packaging.
3. **Warranty rights**: Minimum 1-year warranty on electronics. The retailer (not just the manufacturer) is responsible for warranty service.
4. **Price display**: All prices must be displayed including VAT. If a retailer shows a price without VAT, the displayed price is the legally binding one.
5. **Credit card payments**: Consumers have the right to pay in installments (tashlumim). Retailers with annual revenue over a certain threshold must offer at least 3 interest-free payments for purchases over 500 NIS.

### Step 7: Present the Comparison Results

Structure the comparison output as follows:

1. **Product summary**: Full product name, model, key specs
2. **Price comparison table**: Sorted by total price (product + shipping), showing retailer name, price, shipping cost, availability, and store rating
3. **Recommendation**: Best overall value considering price, warranty, delivery time, and retailer reliability
4. **Alternative options**: Suggest similar products if the user might benefit from a different model or brand
5. **Savings tips**: Any applicable coupons, cashback, or optimal purchase timing

## Examples

### Example 1: Comparing Smartphone Prices

User says: "I want to buy a Samsung Galaxy S24 Ultra, where is the cheapest place in Israel?"

Actions:
1. Search Zap.co.il for "Samsung Galaxy S24 Ultra" to get the price comparison across retailers
2. Check KSP directly for any exclusive bundles or price-match offers
3. Check iDigital for any trade-in promotions
4. Compare with Amazon.com price + estimated customs (product over 130 USD threshold)
5. Check if TopCash offers cashback on any of the retailers

Result: Present a table with prices from Zap (aggregated), KSP, iDigital, Ivory, and Amazon (with customs estimate). Recommend the retailer offering the best combination of price, warranty, and delivery. Note the 14-day online return policy.

### Example 2: Finding the Best Deal on a Home Appliance

User says: "I need a new air conditioner for a 20 sqm room, what should I buy and where?"

Actions:
1. Determine the appropriate BTU rating for a 20 sqm room (approximately 18,000-24,000 BTU depending on floor level and sun exposure)
2. Search Zap.co.il air conditioning category with BTU filter
3. Check Home Center and Machsanei Hashmal for appliance-specific deals
4. Factor in installation costs (typically 400-800 NIS for standard installation)
5. Compare models from Electra (Israeli brand with local service), Tadiran, Midea, and Samsung

Result: Recommend 2-3 models at different price points. Include total cost of ownership (unit + installation). Highlight that air conditioner installation in Israel requires a licensed technician and that major retailers offer installation packages. Note the end-of-winter sales (February-March) as the best time to buy.

### Example 3: Evaluating Import vs. Local Purchase

User says: "Should I buy Sony WH-1000XM5 headphones from Amazon or locally?"

Actions:
1. Check current price on Amazon.com and calculate landed cost (product + shipping + customs/VAT if over 130 USD)
2. Search Zap.co.il for current Israeli prices
3. Check KSP price-match policy applicability
4. Compare warranty terms: Amazon (international warranty, no local service) vs. local retailer (full local warranty)

Result: Present side-by-side comparison showing Amazon price with customs estimate vs. best local price. Factor in warranty value (Sony Israel service center vs. international warranty process). Recommend local purchase if the price difference is less than 150-200 NIS given the warranty advantage.

## Gotchas

- All Israeli consumer prices must include 18% VAT by law. Agents may scrape or compare prices excluding VAT, producing incorrect comparisons.
- Israeli price comparison sites (Zap, Pricez) list prices in NIS. Agents may convert to USD for comparison, which introduces exchange rate fluctuations that mislead users.
- The personal import duty-free threshold was raised from $75 to $130 via executive order effective February 25, 2026 (a $150 proposal was rejected by the Knesset). Agents using older training data may still reference the $75 or $150 limits, producing incorrect import cost estimates. The current tiers are: up to $130 = fully exempt, $130-$500 = VAT only (18%), above $500 = full customs + VAT.
- Zap.co.il prices are cached and may lag behind actual retailer prices by hours or days. Agents must verify the final price on the retailer's own website before presenting a recommendation.
- Most Israeli retail and comparison sites (Zap, ksp.co.il, ivory.co.il, ikea.co.il, and others) deploy anti-bot protection and return 403 Forbidden or a CAPTCHA challenge to automated requests. WebFetch will frequently fail or return an error page instead of product data. Treat scraping as best-effort, when a fetch is blocked, tell the user the site must be checked manually rather than presenting stale or empty results as if they were live prices. Never fabricate a price to fill a gap.

## Recommended MCP Servers

- **supermarket-prices**: Israeli supermarket and grocery price comparison. This skill explicitly does NOT cover groceries or food, when a user asks to compare supermarket prices, hand off to the `supermarket-prices` MCP instead of trying to answer here.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Zap price comparison | https://www.zap.co.il | Primary Israeli price comparison engine |
| Israel Tax Authority customs calculator | https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/he/PersonalImportTax/Home/Calc | Official personal-import tax estimate by product and value |
| Personal import rights (Kol Zchut) | https://www.kolzchut.org.il/he/יבוא_אישי | Consumer rights and conditions for personal import |
| Personal import guide (gov.il) | https://www.gov.il/en/departments/topics/customs-personal-import/govil-landing-page | Official customs rules, exemption thresholds |

## Troubleshooting

### Error: "Product not found on Zap"

Cause: The product may be listed under a different name in the Israeli market, or it may not be officially sold in Israel.

Solution:
1. Try searching by model number instead of product name
2. Search in Hebrew (many products are listed with Hebrew names on Zap)
3. Check if the product is available under a different regional SKU
4. If the product is not sold in Israel, advise the user on international purchase options with customs estimation

### Error: "Price discrepancy between Zap and retailer website"

Cause: Zap's prices may be cached and not reflect real-time changes. Retailers update Zap feeds periodically (usually daily, but sometimes with delays).

Solution:
1. Always verify the final price on the retailer's actual website before purchasing
2. Check the "last updated" timestamp on the Zap listing
3. If the retailer's price is higher than shown on Zap, contact the retailer and reference the Zap listing. Many retailers will honor the Zap price.
4. Report significant discrepancies via Zap's feedback mechanism

### Error: "Customs duty calculation uncertainty"

Cause: Customs rates vary by product category, and the declared value may be assessed differently by Israeli customs authorities.

Solution:
1. Use the Israeli Customs Authority calculator for official rates
2. For electronics, the customs duty is typically 0% but VAT (18%) still applies on the total value (product + shipping + insurance)
3. Note that customs authorities may reassess the declared value upward if they believe it is understated
4. For high-value purchases (over 1,000 USD), consider using a customs broker or a shipping service that handles customs clearance

### Error: "WebFetch returns 403 / CAPTCHA instead of product prices"

Cause: Zap and most Israeli retailers (KSP, Ivory, IKEA Israel, and others) block automated requests with anti-bot protection. Their Terms of Service generally prohibit scraping.

Solution:
1. Do not retry aggressively, repeated blocked requests can get the IP rate-limited or banned.
2. Tell the user plainly that the site is bot-protected and the price must be checked manually in a browser, then provide the direct search URL.
3. Use any results that did come through, but label them with the source and note they could be stale.
4. Never invent or estimate a price to paper over a blocked fetch, present only verified data.