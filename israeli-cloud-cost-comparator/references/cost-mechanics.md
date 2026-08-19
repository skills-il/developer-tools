# Cost Mechanics: Egress and Commitments

The two places an Israeli cloud comparison actually goes wrong. Both were measured from
machine-readable provider APIs on **19 August 2026**, which are re-checkable, unlike the marketing
pricing pages.

## AWS egress, and why the Israeli region is the expensive end

Internet data transfer out, per GB, read from the AWS Price List API
(`https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/index.json`,
`transferType = AWS Outbound`):

| Monthly band | il-central-1 (Tel Aviv) | eu-west-1 (Ireland) | us-east-1 |
|---|---|---|---|
| First 10 TB | **$0.110** | $0.090 | $0.090 |
| Next 40 TB | $0.085 | $0.085 | $0.085 |
| Next 100 TB | $0.077 | $0.070 | $0.070 |
| Over 150 TB | $0.055 | $0.050 | $0.050 |

Tel Aviv carries a **22% premium at the first tier**, where most workloads live.

Inter-region transfer out (`transferType = InterRegion Outbound`) is the sharper difference:

| Leaving | Rate to every destination checked |
|---|---|
| il-central-1 | **$0.08/GB** |
| eu-west-1 | $0.02/GB |

Destinations checked from Tel Aviv: Ireland, Frankfurt, N. Virginia, Cape Town, Lagos, Hong Kong,
Tokyo, Taipei. All $0.08, and $0.08 is the rate for 99 of the 104 destinations in the offer file.
**It is not uniform, though**: the Australian regions (ap-southeast-2, -4, -6) are $0.15/GB, nearly
double, so size an APAC replication leg from the offer file rather than from the headline rate. The charge is **asymmetric**: traffic INTO Tel Aviv from another region is
billed at the sending region's ordinary rate, so a chatty two-way data plane is expensive in one
direction only.

**Why this matters more than the compute premium.** Compute in il-central-1 is a flat ~5% above
eu-west-1 (median 5.0% across all 324 shared instance types, range 4.3-5.9%). Network is 22% on
internet egress and 4x on inter-region. The Israeli-region cost story is a network story, not a
compute story, and a comparison that models a 10% compute premium and zero network delta has it
backwards on both counts.

**The architecture this skill otherwise recommends generates the expensive leg.** Keeping data in
the Israeli region and reaching a European region for services il-central-1 lacks is exactly the
$0.08/GB path. At 5 TB/month that single leg is roughly $400/month.

## Commitment discounts: what you are actually signing

**What a commitment actually obliges you to. State this before recommending one, because the discount headline is the easy half:**

| Provider | Cancellable? | Committed to what | Scope | Escape hatch |
|---|---|---|---|---|
| GCP resource-based CUD | **No.** Google's docs: "After you purchase a commitment, you can't cancel or delete it. The commitment remains active until its specified end date" | Capacity | Bound to a region and machine series | None |
| GCP Flexible CUD | No | Spend | Across families and regions, at a higher hourly rate | None |
| AWS Savings Plans | No | Dollars per hour | Compute plans span families and regions | None; the shortfall is billed |
| Azure Reservation | Exchange/refund, but capped | Capacity | Region and series, with flexibility options | Cancelled commitment capped at **$50,000 per rolling 12 months**, and **from 1 February 2027 reservations bought after that date are no longer exchangeable** where the service is savings-plan-eligible (Azure VMs, App Service, SQL Database). Reservations bought before that date keep one final exchange |

**Decision rules:**
- Commit no higher than the trailing-90-day floor of steady-state usage, not the average and never the peak.
- Do not commit during a migration or before the instance mix has settled. Example 2 below is a migration, and a 3-year capacity commitment there is exactly the mistake this table exists to prevent.
- Do not buy a commitment while credits are covering the bill. You burn both at once and get the benefit of neither.
- Prefer the flexible or spend-based instrument first; move to the cheaper capacity-bound one only once the workload's shape is boring.
- The February 2027 Azure date falls inside the horizon of any 3-year decision taken today.

## How to use this file

Re-read the two API endpoints above and the four provider commitment pages before quoting any of
these numbers. The egress tables in particular are the kind of figure that silently decides a
recommendation, so they are worth the extra fetch.


## Currency and NIS billing

AWS and GCP bill in USD. Azure offers some NIS billing via Israeli enterprise agreements (contact Microsoft Israel). Kamatera bills natively in NIS. For USD providers: set budgets with a 10% currency buffer, time reserved-instance purchases to favorable rates, use corporate FX accounts, consider forward contracts for large committed spends, track USD/NIS and rebudget quarterly.

## Reference Links

**Provider pricing pages (always treat as the source of truth, since list prices change quarterly):**
- AWS EC2 on-demand pricing: `https://aws.amazon.com/ec2/pricing/on-demand/`
- AWS pricing calculator: `https://calculator.aws/`
- GCP Compute Engine pricing (deep links, the old `/compute/all-pricing` and `/products/compute/pricing` URLs now redirect to a marketing page with no price tables): general-purpose `https://cloud.google.com/products/compute/pricing/general-purpose`, accelerators `https://cloud.google.com/products/compute/pricing/accelerator-optimized`
- GCP pricing calculator: `https://cloud.google.com/products/calculator`
- Azure pricing calculator: `https://azure.microsoft.com/en-us/pricing/calculator/`
- Azure VMs pricing: `https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/`
- Oracle Cloud Israel price list: `https://www.oracle.com/il-en/cloud/price-list/`
- Oracle Cloud cost estimator: `https://www.oracle.com/il-en/cloud/costestimator.html`

**Israeli region announcements and service availability:**
- AWS Israel (Tel Aviv) region launch: `https://aws.amazon.com/blogs/aws/now-open-aws-israel-tel-aviv-region/`
- AWS regional service availability: `https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/`
- GCP locations and services per region: `https://cloud.google.com/about/locations`
- Azure products by region: `https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/`
- Oracle Israel (Jerusalem) region overview: `https://www.oracle.com/il-en/cloud/cloud-regions/israel/`

**Commitment discounts:**
- AWS Savings Plans: `https://aws.amazon.com/savingsplans/`
- GCP Committed Use Discounts: `https://cloud.google.com/docs/cuds`
- Azure Reservations: `https://azure.microsoft.com/en-us/pricing/reserved-vm-instances/`
- Azure Savings Plan for Compute: `https://azure.microsoft.com/en-us/pricing/offers/savings-plan-compute/`

**Startup credit programs:**
- AWS Activate: `https://aws.amazon.com/startups/credits/`
- Google for Startups Cloud Program: `https://cloud.google.com/startup`
- Microsoft for Startups Founders Hub: `https://www.microsoft.com/en-us/startups`
- Israel Innovation Authority: `https://innovationisrael.org.il`
- Israel Innovation Authority, Telem supercomputer access (Nebius B200): `https://innovationisrael.org.il/en/press_release/supercomputer-access-2026/`

**Israeli cloud providers:**
- Kamatera: `https://www.kamatera.com`
- Kamatera pricing: `https://www.kamatera.com/pricing/`

**Privacy and data-protection references:**
- Privacy Protection Authority (PPA): `https://www.gov.il/en/departments/the_privacy_protection_authority`
- Proper Conduct of Banking Business Directive 364 (which replaced 357, 361 and 363): `https://kamakama.gov.il/roles/supervisionregulation/nbt/nbt364/`. Note that boi.org.il itself is bot-protected and cannot be read by an agent, so send the user there rather than trying to summarise it
- Bank of Israel USD/ILS representative rate, machine-readable and fetchable: `https://edge.boi.org.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/RER_USD_ILS?format=csv`


## Latency from Tel Aviv (indicative only)

**None of these figures has a published provider source.** They are consistent with fibre distance and with
common third-party measurement, but treat them as bands for shortlisting, not as numbers to quote. If a
decision turns on latency, measure it from the user's own network.

Latency from Tel Aviv to major cloud regions (approximate round-trip time):

| Region | Provider | Latency from TLV |
|--------|----------|-----------------|
| il-central-1 | AWS | 1-3 ms |
| me-west1 | GCP | 1-3 ms |
| Israel Central | Azure | 1-3 ms |
| il-jerusalem-1 | Oracle | 3-6 ms (Jerusalem, slightly higher than Tel Aviv regions for TLV-origin traffic) |
| me-central-1 (UAE) | AWS | 25-40 ms |
| eu-west-1 (Ireland) | AWS | 50-65 ms |
| europe-west1 (Belgium) | GCP | 45-55 ms |
| europe-west4 (Netherlands) | GCP | 45-55 ms |
| West Europe (Netherlands) | Azure | 45-55 ms |
| us-east-1 (Virginia) | AWS | 130-160 ms |
| eu-south-1 (Milan) | AWS | 25-35 ms |
| Hetzner Falkenstein (Germany) | Hetzner | 60-75 ms |

**Latency considerations:**
- For user-facing web applications serving Israeli users, sub-5ms latency (local region) provides noticeably better UX than 50ms+ (European region)
- For API backends, the difference is amplified by the number of sequential calls
- For batch processing and data pipelines, latency matters less; optimize for cost
- CDN (CloudFront, Cloud CDN, Azure CDN) can mitigate latency for static assets regardless of origin region


## מחויבויות והנחות התחייבות (עברית)

**למה מחויבות באמת מחייבת אתכם. אמרו את זה לפני שאתם ממליצים על אחת, כי כותרת ההנחה היא החצי הקל:**

| ספק | ניתן לביטול? | המחויבות היא ל... | היקף | דרך מילוט |
|---|---|---|---|---|
| GCP CUD מבוסס-משאב | **לא.** התיעוד של גוגל: "After you purchase a commitment, you can't cancel or delete it" | קיבולת | כבול לאזור ולסדרת מכונות | אין |
| GCP Flexible CUD | לא | הוצאה | חוצה משפחות ואזורים, בתעריף שעתי גבוה יותר | אין |
| AWS Savings Plans | לא | דולרים לשעה | תוכניות Compute חוצות משפחות ואזורים | אין; ההפרש מחויב |
| Azure Reservation | החלפה/החזר, אך מוגבל | קיבולת | אזור וסדרה, עם אפשרויות גמישות | מחויבות מבוטלת מוגבלת ל-**50,000 דולר בכל 12 חודשים מתגלגלים**, ו**מ-1 בפברואר 2027 רזרבציות שנרכשו אחרי התאריך אינן ניתנות להחלפה** כששירות מכוסה על ידי savings plans (Azure VMs, App Service, SQL Database). רזרבציות שנרכשו לפני כן שומרות על החלפה אחת אחרונה |

**כללי החלטה:**
- אל תתחייבו מעל לרצפת השימוש היציב של 90 הימים האחרונים, לא הממוצע ובוודאי לא השיא.
- אל תתחייבו במהלך הגירה או לפני שתמהיל המכונות התייצב. דוגמה 2 בהמשך היא הגירה, ומחויבות קיבולת ל-3 שנים שם היא בדיוק הטעות שהטבלה הזו נועדה למנוע.
- אל תרכשו מחויבות בזמן שקרדיטים מכסים את החשבון. אתם שורפים את שניהם בו-זמנית ולא נהנים מאף אחד.
- העדיפו קודם את המכשיר הגמיש או מבוסס-ההוצאה; עברו למכשיר הזול הכבול-לקיבולת רק כשצורת העומס משעממת.
- תאריך פברואר 2027 של Azure נופל בתוך אופק כל החלטה לשלוש שנים שמתקבלת היום.


## השהיה מתל אביב (אינדיקטיבי בלבד, עברית)

השהיה מתל אביב לאזורי ענן מרכזיים (זמן הלוך-חזור משוער):

| אזור | ספק | השהיה מ-TLV |
|-------|------|-------------|
| il-central-1 | AWS | 1-3 מ"ש |
| me-west1 | GCP | 1-3 מ"ש |
| Israel Central | Azure | 1-3 מ"ש |
| il-jerusalem-1 | Oracle | 3-6 מ"ש (ירושלים, מעט יותר גבוה מאזורי תל אביב לתעבורה ממוצאי TLV) |
| me-central-1 (איחוד אמירויות) | AWS | 25-40 מ"ש |
| eu-west-1 (אירלנד) | AWS | 50-65 מ"ש |
| europe-west1 (בלגיה) | GCP | 45-55 מ"ש |
| europe-west4 (הולנד) | GCP | 45-55 מ"ש |
| West Europe (הולנד) | Azure | 45-55 מ"ש |
| us-east-1 (וירג'יניה) | AWS | 130-160 מ"ש |
| eu-south-1 (מילאנו) | AWS | 25-35 מ"ש |
| Hetzner Falkenstein (גרמניה) | Hetzner | 60-75 מ"ש |

**שיקולי השהיה:**
- לאפליקציות ווב הפונות למשתמשים ישראליים, השהיה של פחות מ-5 מ"ש (אזור מקומי) מספקת חוויית משתמש טובה בהרבה מ-50+ מ"ש (אזור אירופי)
- עבור backends של API, ההבדל מוגבר במספר הקריאות הרציפות
- לעיבוד batch וצינורות נתונים, ההשהיה פחות חשובה; אופטימיזציה לעלות
- CDN (CloudFront, Cloud CDN, Azure CDN) יכול למתן בעיות השהיה לנכסים סטטיים ללא תלות באזור המקור
