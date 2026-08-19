---
name: israeli-cloud-cost-comparator
description: Compare cloud hosting costs for Israeli startups and developers across AWS (il-central-1 Tel Aviv), Azure (Israel Central), GCP (me-west1 Tel Aviv), Oracle Cloud (il-jerusalem-1 Jerusalem), and Israeli providers like Kamatera. Use when the user needs to evaluate cloud pricing with Israel-specific considerations including data residency under Privacy Protection Law Amendment 13, latency from Tel Aviv, NIS billing options, startup credit programs (AWS Activate, Google for Startups, Microsoft Founders Hub, Israel Innovation Authority Telem program with subsidized Nvidia B200 GPUs), and FinOps cost optimization strategies. Do NOT use for comparing on-premise hosting, colocation services, or non-cloud SaaS pricing.
license: MIT
allowed-tools: Bash(node:*) Bash(python3:*) WebFetch
---


# Israeli Cloud Cost Comparator

## Instructions

### Step 1: Understand the User's Cloud Requirements

Gather the following information before comparing costs:

1. **Workload type**: Web application, API backend, data pipeline, ML training, static site, database
2. **Scale**: Expected traffic (requests/month), data storage (GB/TB), compute needs (vCPU/RAM)
3. **Compliance requirements**: Does the data need to stay in Israel? Are there regulatory requirements (Privacy Protection Authority, GDPR for EU users)?
4. **Budget**: Monthly budget in NIS or USD, preference for pay-as-you-go vs. committed use
5. **Technical stack**: Language/framework, database type, containerized or serverless preference
6. **Growth trajectory**: Startup (scaling fast), SMB (steady), or enterprise (predictable)
7. **Existing credits and promotions**: Ask explicitly whether the user has active credits, free-tier benefits, or promotional balances with ANY provider (AWS Free Tier, GCP $300 trial, Azure $200, AWS Activate, GCP for Startups, Founders Hub, GitHub Student Pack, hackathon credits, VC/accelerator partner credits). Existing credits can flip the comparison and must be factored in.

### Step 2: Compare AWS Israel Region (il-central-1)

AWS launched the Israel (Tel Aviv) region `il-central-1` in August 2023. Key details:

**Available services in il-central-1:**
- EC2 (compute), EBS (block storage), S3 (object storage)
- RDS (managed databases: PostgreSQL, MySQL, Aurora)
- Lambda (serverless), ECS/EKS (containers)
- ElastiCache (Redis/Memcached), DynamoDB
- CloudFront (CDN with Tel Aviv edge), Route 53

**Pricing benchmarks (il-central-1 vs. eu-west-1 Ireland):**
- EC2 instances are typically 5-15% more expensive than eu-west-1
- S3 storage is roughly equivalent
- Data transfer out is the same pricing globally
- RDS instances carry a similar 5-15% premium

**When to use il-central-1:**
- Data residency requirements mandate Israeli hosting
- Latency-sensitive applications serving Israeli users (1-3ms local vs. 40-60ms to eu-west-1)
- Financial services, healthcare, or government applications
- Compliance with Israeli Privacy Protection Authority regulations

**When eu-west-1 may be better:**
- No data residency requirements and cost is the primary concern
- Applications serving both Israeli and European users
- Broader service availability (some newer AWS services launch in eu-west-1 before il-central-1)

**Pricing URL:** `https://aws.amazon.com/ec2/pricing/on-demand/` (filter by region: Israel)

### Step 3: Compare Google Cloud Platform (me-west1)

GCP's `me-west1` region is located in Tel Aviv, opened in 2022 and reached general availability in November 2022. It is GCP's first region in the Middle East.

**Available services in me-west1:**
- Compute Engine, Cloud Storage, Cloud SQL
- GKE (Kubernetes), Cloud Run (serverless containers)
- Cloud Functions, Pub/Sub, BigQuery
- Memorystore (Redis), Cloud Spanner

**Pricing benchmarks:**
- Compute Engine is generally 5-10% cheaper than equivalent AWS EC2 in il-central-1
- Cloud Storage pricing is competitive with S3
- Sustained use discounts apply automatically (up to 30% for running instances 100% of the month)
- Committed use discounts: 1-year (37% off) or 3-year (55% off) for predictable workloads

**GCP advantages for Israeli developers:**
- BigQuery is available in me-west1 (important for data analytics with Israeli data)
- Cloud Run offers a generous free tier (2 million requests/month)
- Firebase hosting with me-west1 backend provides low-latency full-stack hosting
- GCP for Startups program is active in Israel (see Step 7)

**Pricing URL:** `https://cloud.google.com/products/compute/pricing/general-purpose` with the region selector set to Tel Aviv (me-west1). The shorter `/products/compute/pricing` and `/compute/all-pricing` URLs now redirect to a marketing page carrying no tables, which is a common way an agent ends up quoting from memory.

### Step 4: Compare Microsoft Azure

Azure serves Israel primarily through the following regions:

**Regions:**
- **Israel Central** (launched November 12, 2023): Full Azure region in Israel
- **West Europe** (Netherlands): Alternative with broader service catalog

**Available services in Israel Central:**
- Virtual Machines, Azure Blob Storage, Azure SQL
- AKS (Kubernetes), Azure Functions
- Azure Cosmos DB, Azure Cache for Redis

**Pricing benchmarks:**
- Azure VMs in Israel Central are typically 5-12% more expensive than West Europe
- Azure Blob Storage is competitively priced with S3 and Cloud Storage
- Azure offers hybrid benefit pricing: bring your own Windows/SQL Server licenses for up to 40% savings

**Azure advantages:**
- Strong Microsoft enterprise ecosystem integration (Active Directory, Office 365, Teams)
- Note that **Azure Government is not relevant here**: it is a US-sovereign cloud for US federal, state, local and DoD customers, not something an Israeli government buyer can procure. Microsoft competes for Israeli public-sector work through its commercial Israel Central region and separate government channels
- Dev/Test pricing: significant discounts for non-production workloads
- Azure Reserved Instances: 1-year (up to 40% off) or 3-year (up to 65% off)

**Pricing URL:** `https://azure.microsoft.com/en-us/pricing/calculator/`

### Step 5: Compare Oracle Cloud Infrastructure (il-jerusalem-1)

Oracle launched its Israel Central region `il-jerusalem-1` in July 2021 in a hardened underground data center beneath the Har Hotzvim tech park in Jerusalem (50 meters below ground level, four floors under a 17-story building). It was the first hyperscaler region in Israel (predating GCP me-west1, AWS il-central-1, and Azure Israel Central) and is positioned for high-security and high-availability workloads.

**Available services in il-jerusalem-1:**
- Compute (VM, bare-metal), Block Volumes, Object Storage
- Oracle Autonomous Database (the OCI flagship), MySQL HeatWave, PostgreSQL
- Container Engine for Kubernetes (OKE), Functions (serverless)
- Oracle Fusion Cloud Applications

**Pricing posture:**
- Oracle publishes a single global price list, OCI services are priced the same across regions including il-jerusalem-1 (verify on the Oracle Israel price list before quoting)
- Egress: Oracle's first 10 TB/month outbound is included free across all regions; this is one of the more aggressive egress policies among hyperscalers
- Pricing URL: `https://www.oracle.com/il-en/cloud/price-list/`
- Cost estimator: `https://www.oracle.com/il-en/cloud/costestimator.html`

**When to consider OCI il-jerusalem-1:**
- Workloads built around Oracle Database / Exadata where Oracle licensing economics already favor OCI
- High-security or critical-infrastructure deployments where the physical hardening of the underground bunker is a real requirement
- Predictable egress-heavy workloads where the free 10 TB/month allowance moves the needle
- Government and regulated industries that need an Israeli region but want a vendor outside the AWS/Google Project Nimbus contract

**Limitations:**
- Smaller third-party ecosystem and managed-service catalog than AWS/Azure/GCP
- Fewer Israeli startup credit programs and accelerator partnerships
- Some newer OCI services (especially generative-AI features) land in US/EMEA regions first

### Step 5b: Evaluate Israeli Cloud Providers

For specific use cases, Israeli cloud providers may offer advantages:

**Kamatera (`https://www.kamatera.com`):**
- Israeli-founded company with five Israeli data centers (Petah Tikva, Haifa, others)
- Competitive pricing: starting from approximately $4/month for basic VPS (1 vCPU, 1GB RAM), verify current pricing on the Kamatera pricing page before quoting
- Pay-as-you-go: pay only for what you use, billed hourly or monthly, no traffic overage surprises
- 30-day free trial available
- Good for: Small projects, development environments, Israeli-market applications
- Limitations: Smaller service catalog than hyperscalers, no managed Kubernetes
- Native NIS billing was historically advertised; if the user needs guaranteed shekel-denominated invoices, confirm with Kamatera sales directly since billing-currency policies have changed across regional resellers

**Note:** HostIL (`hostil.co.il`) is an Israeli hosting provider that has been referenced in some directories, but its current operational status could not be independently verified. Check the website directly before relying on it.

**Akamai / Linode**: Akamai has a Tel Aviv office but as of May 2026 there is no Linode Connected Cloud data center in Israel. Israeli users typically route to Linode's Frankfurt or Amsterdam regions, which adds 45-55 ms of latency. Do not recommend Linode as an "Israeli region" option.

**DigitalOcean, Vultr, Hetzner, OVH**: none operate a data center in Israel. Israeli users on these platforms typically use Frankfurt (Hetzner, DigitalOcean), Strasbourg (OVH), or Amsterdam, with 45-65 ms latency to Tel Aviv. Hetzner is the lowest-cost EU option for non-residency-sensitive workloads, but it is no longer as cheap as older comparisons suggest: its 15 June 2026 price adjustment took the entry CX23 from €3.99 to €5.49/month net, with some CPX and CCX lines rising considerably more. Quote €5.49/month as the current floor, not the €4-ish figure that circulates.

### Step 6: Compare Data Residency and Compliance

Israeli data protection considerations:

**Privacy Protection Law Amendment 13 (in force since August 14, 2025):**
- Establishes binding cross-border transfer rules. Personal data of Israeli residents may be transferred abroad only if the destination jurisdiction provides "adequate" protection (or one of the other Section 2 exceptions applies)
- The Privacy Protection Authority maintains a list of approved jurisdictions; the EU, UK, and a small set of other GDPR-aligned countries are on it
- On April 13, 2026, the PPA published a Position Paper interpreting Section 2(4) of the Cross-Border Transfer Regulations, which tightened the practical conditions for the "data controller is responsible" pathway. Treat any cross-border architecture as a documented decision rather than a default
- A Data Protection Officer (DPO) is now required for many controllers and large data holders
- Breach notification is mandatory and timelines are tighter than under the prior regime

**Sector-specific overlays still apply:**
- Financial institutions under Bank of Israel supervision typically require Israeli hosting (Proper Conduct of Banking Business Directive 357 on cloud computing remains the operative cloud framework for supervised entities)
- Healthcare data (HMO / Kupat Holim, hospitals) has strict locality requirements
- Government tenders often mandate Israeli data centers; classified workloads route via Project Nimbus (see Step 6b)
- PCI DSS still applies independently for payment-card data

**Data residency comparison:**

| Provider | Israeli Data Center | Data Sovereignty | Compliance Certs |
|----------|-------------------|------------------|-----------------|
| AWS il-central-1 | Yes (Tel Aviv) | AWS retains control | ISO 27001, SOC 2, PCI DSS |
| GCP me-west1 | Yes (Tel Aviv) | Google retains control | ISO 27001, SOC 2, PCI DSS |
| Azure Israel Central | Yes (Israel) | Microsoft retains control | ISO 27001, SOC 2, PCI DSS, IL Gov |
| Oracle il-jerusalem-1 | Yes (Jerusalem, underground) | Oracle retains control | ISO 27001, SOC 2, PCI DSS |
| Kamatera | Yes (Petah Tikva, Haifa, others) | Israeli company | ISO 27001 |
| HostIL (verify availability) | Yes (Israel) | Israeli company | Basic |

**Recommendation by compliance level:**
- **High compliance** (finance, healthcare, government civilian): Azure Israel Central or AWS il-central-1 with the relevant data-processing addendum, or Oracle il-jerusalem-1 if Oracle Database is already the system of record
- **Standard compliance** (SaaS, e-commerce serving Israeli users): Any hyperscaler with an Israeli region
- **Low compliance** (personal projects, internal tools, non-Israeli data): Consider eu-west-1 (AWS), europe-west4 (GCP Amsterdam), or Hetzner Falkenstein/Nuremberg for cost savings, make the cross-border decision explicit, not accidental

### Step 6b: Project Nimbus (Government Sovereign Cloud)

Project Nimbus is the $1.2 billion Israeli-government cloud contract awarded to AWS and Google in 2021. It is **not a public-tenant service**, it is a sovereign tenant accessible to government ministries, security services, and approved partners. Do not recommend it to general startups or commercial customers.

**When Nimbus is relevant:**
- The user is a government ministry, a defense-sector vendor, or a contractor working on a classified workload that must run inside the Nimbus tenant
- The user is evaluating which hyperscaler to align with for future government tenders (AWS and Google have the Nimbus footprint; Azure and Oracle compete via separate government channels)

**What to know:**
- Nimbus uses dedicated infrastructure inside Israel under contractual sovereignty terms that differ from public AWS/GCP regions
- Public reporting (late 2025 to early 2026) describes a "winking mechanism" requiring AWS and Google to coded-notify the Israeli Finance Ministry if a foreign court demands Nimbus data. This is not a technical control, it is a contract term, and it has drawn ongoing scrutiny from researchers and employees at both companies
- Israel does not currently operate a fully sovereign cloud (an Israeli-controlled stack with sovereign AI processing). Nimbus is a "data-stays-in-Israel" arrangement on AWS/Google infrastructure rather than a sovereign-controlled stack

### Step 7: Factor in Credits, Free Tiers, and Promotions

Credits can change the comparison entirely. A provider 20% more expensive on list price may be cheapest for 6-12 months if the user has credits there. Always check before recommending.

#### 7a and 7b: Free Tiers, Trials and Startup Credit Programmes

The per-provider trial credits, always-free catalogues, and every startup-credit programme (AWS
Activate, Google for Startups, Microsoft Founders Hub, the IIA grants and the Telem B200 programme)
live in `references/pricing-and-credits.md`, with the amounts as read on 19 August 2026.

Read that file before quoting any figure. Three things there are counter-intuitive enough to state
up front:

- **AWS's free tier is no longer per-service limits for 12 months.** It is a lump sum of up to $200,
  and the account closes itself after 6 months or when the credits run out.
- **The published startup-credit ceilings moved up sharply in 2026** and most secondary write-ups
  still quote the old ones.
- **The ceilings are ceilings.** Quote them as such, not as expected awards.

#### 7c. Other Credit Sources

- **Educational**: GitHub Student Developer Pack (AWS, GCP, Azure, DigitalOcean credits)
- **Hackathons / events**: $500-$2,000 credits distributed at Israeli developer events
- **VC / accelerator partners**: 8200 EISP, MassChallenge Israel, Techstars typically include cloud credits

#### 7d. Using Existing Credits in the Comparison

1. Calculate credit runway (months covered at estimated usage)
2. Compare across providers (user may not know other providers offer more)
3. Show "with credits" AND "after credits expire" so the user can plan ahead
4. Warn about lock-in if expiring credits push toward a more expensive long-term provider

### Step 8: Perform Latency Benchmarking

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

### Step 9: Calculate Total Cost of Ownership

**Commitment-discount programs (verify rates on provider pages, terms shift):**
- **AWS Savings Plans** (Compute and EC2 Instance): up to ~66% off on-demand for 1-3 year terms. Compute Savings Plans apply across families and regions. RIs still offered for RDS, ElastiCache, Redshift, OpenSearch.
- **GCP CUDs**: spend-based, resource-based, and Flexible CUDs (across machine families/regions). Sustained Use Discounts apply automatically to on-demand Compute Engine.
- **Azure Reservations** (1-3 year) for VMs, SQL DB, Cosmos DB, Cache for Redis, plus **Azure Savings Plan for Compute** for flexibility across regions/series.

Build a comprehensive comparison including:

1. **Compute**: On-demand vs. reserved/committed vs. savings plan vs. spot/preemptible
2. **Storage**: Object + block + database storage
3. **Network**: Egress, inter-region, CDN
4. **Managed services**: Databases, caches, queues, monitoring
5. **Support**: AWS renamed and restructured its plans. There is no longer a Developer or a Business tier; the three paid plans are **Business Support+** (minimum spend $29/month per account), **Enterprise Support** ($5k/month) and **Unified Operations** ($50k/month), each priced as the greater of the minimum spend or a percentage of monthly AWS charges. Quoting "Developer $29 / Business $100" is out of date.
6. **Currency impact**: AWS, GCP, Oracle bill in USD; Azure offers some NIS billing via Israeli enterprise agreements. The shekel has kept strengthening: the Bank of Israel representative rate was **2.985 on 19 August 2026**, against about 3.70 in 2024, having traded in the high 2.9s to low 3.0s through August. A NIS cloud budget set at the 2024 rate now buys roughly 20-25% more USD than it was sized for. For budgeting, use the Bank of Israel representative rate rather than any figure quoted here, and rebudget quarterly on a 3-month trailing average.
7. **Hidden costs**: NAT Gateway (AWS), premium networking (GCP), diagnostic logging (Azure)

**Cost comparison table format:**

| Service | AWS il-central-1 | GCP me-west1 | Azure Israel | Oracle il-jerusalem-1 | Kamatera |
|---------|-----------------|-------------|-------------|---------------------|----------|
| ~4 vCPU, 16GB VM | $X/month | $X/month | $X/month | $X/month | $X/month |
| 100GB SSD | $X/month | $X/month | $X/month | $X/month | $X/month |
| 1TB egress | $X/month | $X/month | $X/month | First 10TB free | $X/month |
| Managed PostgreSQL | $X/month | $X/month | $X/month | $X/month | N/A |
| **Total** | **$X/month** | **$X/month** | **$X/month** | **$X/month** | **$X/month** |

**2026 anchor (verify on the provider page before quoting):** GCP me-west1 `n2-standard-4` (4 vCPU, 16 GB) at ~$0.214/hr on-demand (~$156/mo). The commitment figures below are the **resource-based** CUD column, ~$0.135/hr 1yr and ~$0.096/hr 3yr; note that Flexible CUDs are *more* expensive per hour, so name which column you are quoting. Cross-check: Azure Israel Central `Standard_D4s_v5` Linux on-demand is $0.224/hr (~$164/mo) per the Azure retail price API. Sanity check: a 4 vCPU / 16 GB Israeli-region VM should land in $130-200/month on-demand at any hyperscaler, and both of those figures sit inside it.

### Step 9b: GPU and AI Workload Pricing

GPU pricing is a separate cost axis, and it is the fastest-drifting data in this skill. The current
hyperscaler and specialty per-GPU-hour rates, the H200/B200 rates, and the IIA Telem route all live
in `references/pricing-and-credits.md`.

The shape of the market, which changes more slowly than the numbers:

- Specialty clouds (Lambda, RunPod, Vast.ai) undercut hyperscaler list prices, but the gap narrowed
  through 2026 and none of them has an Israeli region, so expect 80-150 ms from Tel Aviv.
- Israeli-region GPU availability is thin; check the region's accelerator catalogue before promising
  a specific instance family in il-central-1 or me-west1.
- For an Israeli AI startup doing real training rather than inference, the IIA Telem allocation is
  worth pursuing before committing to a hyperscaler GPU reservation, both on price and because the
  training data stays in Israel.

**GPU recommendation framework:**
- **Inference, latency-sensitive, Israeli users**: an Israeli-region GPU instance if the family is
  available, otherwise accept the EU hop
- **Training, no residency requirement, budget-sensitive**: specialty providers in the EU or US
- **Training, Israeli AI R&D**: apply for IIA Telem first, fall back to specialty providers
- **Steady-state inference at scale**: commitment discounts close most of the gap with specialty
  providers above roughly 60% utilisation

### Step 10: Present Recommendations

Structure the final recommendation:

1. **Summary table**: Side-by-side cost comparison for the user's specific requirements
2. **Credit-adjusted comparison**: If the user has credits on any provider, show a separate row or table with effective monthly cost after credits. Also proactively mention comparable promotions on other providers the user may not be aware of.
3. **Primary recommendation**: Best provider for the user's use case with justification. If credits heavily favor one provider short-term, state this clearly but also recommend the best long-term choice after credits expire.
4. **Alternative recommendation**: Second-best option explaining tradeoffs
5. **Cost optimization tips**: Specific actions to reduce costs (reserved instances, spot usage, right-sizing)
6. **Migration considerations**: If the user is already on a provider, estimate migration effort and any lock-in concerns
7. **Next steps**: Links to free tier / trial offers for hands-on evaluation

## Examples

### Example 1: Startup Evaluating Cloud for a New SaaS Product

User says: "We're a seed-stage Israeli startup building a B2B SaaS product. We expect 1,000 users in year one, mostly Israeli companies. Our stack is Node.js + PostgreSQL + Redis. Budget is about 5,000 NIS/month."

Actions:
1. Estimate infrastructure needs: 2x application servers (2 vCPU, 4GB each), managed PostgreSQL (db.t3.medium equivalent), managed Redis (cache.t3.small equivalent), 50GB S3 storage
2. Calculate costs across AWS il-central-1, GCP me-west1, and Azure Israel Central
3. Check startup credit availability: recommend applying to AWS Activate, GCP for Startups, and Microsoft Founders Hub
4. Factor in data residency: B2B SaaS for Israeli companies may benefit from local hosting for sales conversations
5. Consider Kamatera as a lower-cost option for development/staging environments

Result: Recommend GCP me-west1 as primary (sustained use discounts + competitive pricing + Cloud Run for microservices) with AWS il-central-1 as alternative. Highlight that startup credits from both providers could cover 12-18 months of hosting. Suggest Kamatera for staging environment at approximately 100 NIS/month. Total estimated production cost: 1,500-2,500 NIS/month before credits.

### Example 2: Enterprise Migrating from On-Premise to Cloud

User says: "We're a financial services company in Tel Aviv with 50 servers on-premise. We need to move to cloud with Israeli data residency. Our workloads include transaction processing, reporting databases, and a customer portal."

Actions:
1. Map current infrastructure to cloud equivalents (50 servers with varying specs)
2. Identify compliance requirements: Bank of Israel regulations, PPA data residency, PCI DSS for payment processing
3. Compare AWS il-central-1 vs. Azure Israel Central (both have financial services compliance)
4. Calculate reserved instance pricing for predictable workloads (1-year and 3-year options)
5. Include migration costs: AWS Migration Hub or Azure Migrate tooling, network setup, testing

Result: Recommend Azure Israel Central as primary due to hybrid licensing benefits (bring existing Windows/SQL Server licenses) and strong financial services compliance posture. AWS il-central-1 as alternative if the team has more AWS expertise. Estimated monthly cost: $15,000-25,000/month with 3-year reserved instances. Do NOT pitch Azure Government for future Israeli government contracts: it is a US-sovereign cloud for US government customers. For Israeli public-sector work the relevant conversation is the commercial Israel Central region plus the applicable tender requirements.

### Example 3: Developer Choosing Hosting for a Side Project

User says: "I'm building a personal project, a Hebrew NLP tool. I need a small server with GPU access for inference, plus a database. Budget is minimal."

Actions:
1. Identify GPU needs: inference-only requires smaller GPU (T4 or equivalent)
2. Compare GPU pricing: AWS g4dn.xlarge, GCP n1-standard-4 + T4, Azure NC4as_T4_v3
3. Consider spot/preemptible instances for 60-80% cost savings on GPU compute
4. Check if GPU instances are available in Israeli regions (limited availability)
5. Evaluate alternatives: Kamatera GPU instances, or Lambda Labs / RunPod for inference-only

Result: For an inference-only side project the cheapest path in 2026 is a specialty GPU provider (Lambda Labs, RunPod, or Vast.ai) running an L4 or T4-class instance at roughly $0.40-$1.00/hour, paired with a small managed PostgreSQL anywhere, GCP me-west1 Cloud SQL micro, AWS RDS db.t4g.micro in il-central-1, or even a Kamatera VM for the database. If the side project needs Israeli residency or sub-5 ms latency, use GCP me-west1 with a preemptible/spot GPU instance plus Cloud SQL micro. Estimated cost in the lower-cost specialty-provider path: roughly 150-350 NIS/month at a rate near 3.0 ILS/USD (check the current Bank of Israel rate before quoting). For an Israeli AI startup with actual training (not just inference) workloads, recommend applying to the Israel Innovation Authority Telem program for subsidized Nvidia B200 access via Nebius before locking in a hyperscaler GPU reservation. For ultra-low cost, suggest running inference on CPU with quantized models if latency tolerance allows.

## Gotchas

- **Every list price in this skill has a shelf life of weeks, and the credit programmes move too.** Between the last review and this one, AWS replaced its whole free tier, renamed all three support plans, doubled Activate Portfolio, and Google restructured its startup programme; Hetzner raised prices and Lambda's H100 rate rose by roughly 60%. Treat every number here as a starting anchor to re-verify on the provider's page, and tell the user the date you checked. An agent quoting these figures as current, months later, is the single most likely failure mode of this skill.
- **The shekel moved against the dollar far more than most budgets assume.** USD/ILS was about 3.70 in 2024 and 2.985 on 19 August 2026. Any NIS budget, conversion or example carried over from older material is materially wrong, including examples inside this skill.
- **Credits blind spot**: When a user mentions having credits or promotions on one provider, agents tend to immediately recommend that provider without checking if other providers offer similar or better deals. Always compare credit programs across ALL providers before recommending. A user with $100 AWS credits may not know that GCP offers $300 in trial credits, that Azure Founders Hub offers up to $150,000 for VC-backed startups, or that the Israel Innovation Authority Telem program offers subsidized B200 GPU access for AI training.
- AWS Israel region (il-central-1) pricing differs from eu-west-1 and other regions. Agents may use global pricing that does not reflect the Israeli region premium.
- **Oracle il-jerusalem-1 is in Israel even though OCI is sometimes overlooked.** Do not tell users "there is no Oracle Israeli region", there has been one (in an underground Jerusalem bunker) since July 2021.
- **Do not confuse AWS me-south-1 (Bahrain) with the Israeli region.** AWS launched il-central-1 in Tel Aviv in August 2023; me-south-1 in Bahrain is not the closest Israeli AWS option anymore and should not be recommended as the "closest fallback" for Israeli users.
- **Akamai/Linode does not have an Israeli data center.** Akamai has a Tel Aviv office, but Linode Connected Cloud does not have an Israel location. Frankfurt is the typical fallback (45-65 ms latency).
- Israeli cloud costs should be calculated in NIS including 18% VAT for B2C, but excluding VAT for B2B with valid tax invoice. Agents may forget to add VAT for consumer-facing comparisons.
- **Cross-border transfer requires a documented basis under Privacy Protection Law Amendment 13** (in force since August 14, 2025). Do not silently default to eu-west-1 or europe-west4 for an Israeli SaaS handling personal data, the choice needs to fit one of the Section 2 exceptions (adequate jurisdiction list, controller-responsibility under the April 2026 PPA guidance, etc.). Israeli data residency requirements for government contracts may mandate hosting within Israel; agents may otherwise recommend cheaper international regions that violate these requirements.
- **Currency drift**: USD/ILS has fallen from roughly 3.70 in 2024 to **2.985 on 19 August 2026** (Bank of Israel representative rate). A NIS budget set at the older rate is now roughly 20-25% too generous in USD terms. Right-size to the current Bank of Israel representative rate rather than recycling an old conversion, including any figure quoted in this skill.
- **Project Nimbus is not a startup option.** Do not recommend Project Nimbus to commercial customers, it is a government sovereign-tenant contract on AWS and Google, not a public cloud product.
- Shabbat and holiday periods can affect spot instance pricing and availability in the Israel region differently than other regions due to reduced local demand.

## Troubleshooting

### Error: "Service not available in Israeli region"

Israeli regions are new and may lack some specialized services. Check the provider's regional availability page (AWS, GCP, Azure links in Reference Links). Options: multi-region architecture (data in Israeli region, unavailable services in nearest European region); cross-region serverless invocations if latency tolerates; contact the provider's Israeli team for roadmap.

### Error: "Costs significantly higher than estimated"

Common cost drivers: data transfer, NAT Gateway (AWS), premium networking (GCP), diagnostic logging (Azure).

1. Enable billing alerts and budgets
2. Review billing by service to find top drivers
3. Fix common culprits:
   - **NAT Gateway (AWS)**: about $0.045/GB processed, but the rate is region-dependent and this figure is the US East one, so check the il-central-1 page before quoting it to an Israeli deployment. Use VPC endpoints for S3/DynamoDB
   - **Egress**: Use CloudFront/CDN for static assets; compress API responses
   - **Idle resources**: Stopped instances, unattached EBS volumes, unused Elastic IPs
   - **Over-provisioned DBs**: RDS/Cloud SQL often at 10-20% utilization, right-size or use serverless
4. Use FinOps tools: AWS Cost Explorer, GCP Recommender, Azure Advisor

### Error: "NIS billing not available"

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
- Bank of Israel, supervised entities and cloud guidance (Proper Conduct of Banking Business Directive 357): `https://www.boi.org.il/en/`