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

Zap.co.il is Israel's dominant price comparison engine, aggregating offers from a large network of Israeli retailers. (Zap publishes no audited traffic or partner-count figure, so do not quote one.)

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

Also check **Google Shopping (Israel)** as a second aggregator. It now indexes many Israeli retailers, including some that have reduced their Zap presence, and can surface offers Zap misses. Treat Zap and Google Shopping as complementary rather than relying on Zap alone.

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

1. **AliExpress / Amazon**: Check the product price including shipping to Israel. There is no local `amazon.co.il` storefront, Amazon orders ship from abroad (usually amazon.com) and count toward the personal-import threshold below.
2. **Customs duty calculation** (the personal-import duty-free threshold is 75 USD as of June 2, 2026, see Gotchas for the 2026 history):
   - **Up to 75 USD**: Fully exempt from customs, VAT, and purchase tax. Eligibility for the exemption is judged on the goods value alone, excluding shipping and insurance if they are itemized separately. Tobacco and alcohol are excluded from the exemption.
   - **75-500 USD**: VAT (18%), no customs duty. Purchase tax (mas kniya) may also apply to some categories such as TVs.
   - **Above 500 USD**: Full customs + VAT + purchase tax (where applicable). Standard customs rate where it applies is around 12%, on top of 18% VAT.
   - **Two different bases, do not confuse them**: the $75 exemption is judged on the goods value only, but once a shipment exceeds $75 the 18% VAT is charged on the full CIF value (goods + shipping + insurance) from the first dollar, not only on the amount above $75 and not on the product price alone. Computing VAT on the product-only or on the excess over $75 under-estimates the landed cost.
   - **Courier handling/clearance fees**: on a taxable parcel add the carrier's customs-clearance fee (Israel Post charges a fixed handling fee; private couriers such as DHL/FedEx/UPS add a percentage or minimum brokerage charge). On a low-value item these flat fees can exceed the VAT itself and flip the import-vs-local decision.
   - Electronics: Often reduced or zero customs duty, but VAT still applies above the $75 threshold.
   - The effective additional cost for products above $75 is approximately 18-30% of the declared value, before courier handling fees.
3. **Warranty considerations**: Products bought internationally typically have no local warranty. Israeli importers and manufacturers are required by law to provide a warranty on electronics (minimum 1 year for products over 150 NIS). Note that "gray-market" or parallel-import (yevu makbil) products sold cheaply by some local stores carry only the seller's warranty, not the official Israeli importer's, verify which warranty applies before buying on price alone.
4. **Delivery time**: Local purchase is 1-5 days. International shipping is 2-6 weeks.

**Recommendation framework**:
- Buy locally if the price difference is less than 20% (warranty + delivery time value)
- Buy internationally if the price difference exceeds 30% and warranty is not critical
- For products priced under 75 USD internationally, always check AliExpress (no customs duty or VAT)

### Step 5: Leverage Price Tracking and Coupon Tools

**Price tracking:**
- **Browser price-comparison extensions** such as "Sham Ze Zol Yoter" (There It's Cheaper) can show price comparisons while browsing retailer sites. Availability changes over time, so verify the extension is still published before recommending it; the Cashback.co.il and TopCash extensions are reliable alternatives
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

1. **Online purchases**: 14-day return policy from delivery date (Consumer Protection Law, Section 14C). The retailer may charge a cancellation fee of 5% of the purchase price or 100 NIS, whichever is lower. On a voluntary cancellation the consumer normally returns the product at their own cost; if the cancellation is due to a defect or misrepresentation, the seller bears the return cost and no fee applies. Exceptions apply for depreciable goods, opened software, and customized products.
2. **Physical store purchases**: under the Consumer Protection (Cancellation of Transaction) Regulations, electronics and appliances over 50 NIS may be returned within 14 days of receipt as long as the product was not damaged, against the same 5% / 100 NIS cancellation fee. Returning it unused in the original packaging is the simplest proof of non-use, but that is a safe harbor, not a strict precondition, an opened-but-undamaged product is still returnable. The real carve-outs are copyable goods such as opened software or recorded media. This is a statutory right, not a goodwill policy. Clothing and footwear have a shorter window (2 business days).
3. **Warranty rights**: under the Consumer Protection (Warranty and After-Sale Service) Regulations 2006, electrical and electronic products over 150 NIS carry a minimum 1-year warranty from delivery. The legal warranty obligation falls on the importer or manufacturer, not the retailer, the retailer's duty is to hand over the manufacturer's warranty certificate at the point of sale.
4. **Price display**: All prices must be displayed including VAT. If a retailer shows a price without VAT, the displayed price is the legally binding one.
5. **Credit card payments**: paying in interest-free installments (tashlumim) is a widespread market norm in Israeli retail (commonly 3-12 payments), not a statutory consumer right. Whether a store offers it, and how many payments, is the retailer's commercial choice, so confirm the installment terms rather than assuming they apply.

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
4. Compare with Amazon.com price + estimated customs (product over the 75 USD threshold)
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
1. Check current price on Amazon.com and calculate landed cost (product + shipping + customs/VAT if over 75 USD)
2. Search Zap.co.il for current Israeli prices
3. Check KSP price-match policy applicability
4. Compare warranty terms: Amazon (international warranty, no local service) vs. local retailer (full local warranty)

Result: Present side-by-side comparison showing Amazon price with customs estimate vs. best local price. Factor in warranty value (Sony Israel service center vs. international warranty process). Recommend local purchase if the price difference is less than 150-200 NIS given the warranty advantage.

## Gotchas

- All Israeli consumer prices must include 18% VAT by law. Agents may scrape or compare prices excluding VAT, producing incorrect comparisons.
- Israeli price comparison sites (Zap and others) list prices in NIS. Agents may convert to USD for comparison, which introduces exchange rate fluctuations that mislead users. (Pricez is a supermarket/grocery comparison app and is out of scope for this skill, do not cite it for electronics.)
- The personal-import duty-free threshold is $75 USD as of June 2, 2026. In early 2026 the Finance Minister issued an order raising it (first toward $150, then a transitional $130 cap applied 25 Feb to 1 Jun 2026), but the Knesset voted to revoke the order, restoring the long-standing $75 threshold from June 2, 2026. Agents whose training data is from the Feb-May 2026 window may still reference $130 or $150 and produce incorrect import-cost estimates. The current tiers are: up to $75 = fully exempt, $75-$500 = VAT only (18%, plus purchase tax on some items), above $500 = full customs + VAT + purchase tax.
- Zap.co.il prices are cached and may lag behind actual retailer prices by hours or days. Agents must verify the final price on the retailer's own website before presenting a recommendation.
- Most Israeli retail and comparison sites (Zap, ksp.co.il, ivory.co.il, ikea.co.il, and others) deploy anti-bot protection and return 403 Forbidden or a CAPTCHA challenge to automated requests. WebFetch will frequently fail or return an error page instead of product data. Treat scraping as best-effort, when a fetch is blocked, tell the user the site must be checked manually rather than presenting stale or empty results as if they were live prices. Never fabricate a price to fill a gap.

## Recommended MCP Servers

- **supermarket-prices**: Israeli supermarket and grocery price comparison. This skill explicitly does NOT cover groceries or food, when a user asks to compare supermarket prices, hand off to the `supermarket-prices` MCP instead of trying to answer here.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Zap price comparison | https://www.zap.co.il/search.aspx?keyword=PRODUCT_NAME | Primary Israeli price comparison engine |
| Israel Tax Authority customs calculator | https://shaarolami-query.customs.mof.gov.il/CustomspilotWeb/he/PersonalImportTax/Home/Calc | Official personal-import tax estimate by product and value |
| Personal import rights (Kol Zchut) | https://www.kolzchut.org.il/he/זכותון_בנושא_יבוא_אישי_(חבילות_מחו"ל) | Consumer rights and conditions for personal import |
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