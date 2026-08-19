---
name: israeli-cloud-cost-comparator
description: Compare cloud hosting costs for Israeli startups and developers across AWS (il-central-1 Tel Aviv), Azure (Israel Central), GCP (me-west1 Tel Aviv), Oracle Cloud (il-jerusalem-1 Jerusalem), and Israeli providers like Kamatera. Use when the user needs to evaluate cloud pricing with Israel-specific considerations including data residency under Privacy Protection Law Amendment 13, latency from Tel Aviv, NIS billing options, startup credit programs (AWS Activate, Google for Startups, Microsoft Founders Hub, Israel Innovation Authority Telem program with subsidized Nvidia B200 GPUs), and FinOps cost optimization strategies. Do NOT use for comparing on-premise hosting, colocation services, or non-cloud SaaS pricing.
license: MIT
allowed-tools: Bash(node:*) Bash(python3:*) WebFetch
---


# Israeli Cloud Cost Comparator

## Instructions

### Step 1: Understand the User's Cloud Requirements

Gather before comparing:

1. **Workload type**: web app, API backend, data pipeline, ML training, static site, database
2. **Scale**: traffic (requests/month), storage (GB/TB), compute (vCPU/RAM), and **egress volume**, which is the line item most often forgotten and, in the Israeli region, the largest cost difference
3. **Compliance**: must the data stay in Israel? Any sector overlay (Bank of Israel supervision, health, government)?
4. **Budget**: monthly, in NIS or USD, and whether pay-as-you-go or committed spend is preferred
5. **Technical stack**: language, database, containerized or serverless
6. **Growth trajectory**: startup scaling fast, SMB steady, or enterprise predictable. This decides whether a commitment is safe at all
7. **Existing credits and promotions**: ask explicitly whether the user has active credits, free-tier benefits or promotional balances with ANY provider (AWS Activate, Google for Startups, Microsoft Founders Hub, GitHub Student Pack, hackathon or accelerator credits). Credits can flip the comparison and must be factored in

### Step 2: Compare AWS Israel Region (il-central-1)

AWS launched the Israel (Tel Aviv) region `il-central-1` in August 2023. Key details:

**Available services in il-central-1:**
- EC2 (compute), EBS (block storage), S3 (object storage)
- RDS (managed databases: PostgreSQL, MySQL, Aurora)
- Lambda (serverless), ECS/EKS (containers)
- ElastiCache (Redis/Memcached), DynamoDB
- CloudFront (CDN with Tel Aviv edge), Route 53

**Pricing benchmarks (il-central-1 vs. eu-west-1 Ireland):**
- EC2 instances carry a flat **~5%** premium over eu-west-1. Measured August 2026 across all 324 shared Linux instance types present in both regions via the AWS Price List API: median 5.0%, range 4.3-5.9%. It does not vary by family (t3.medium 5.0%, m7i.xlarge 5.0%, r6i.xlarge 5.0%, g5.xlarge 5.0%). Do not model a 5-15% band and take the midpoint; that doubles the real gap.
- S3 storage is roughly equivalent
- **Data transfer out is NOT the same globally, and it is the largest Israeli-region cost difference by far.** Internet egress from il-central-1 is **$0.110/GB** for the first 10 TB/month against **$0.090/GB** from eu-west-1 and us-east-1, a 22% premium. Inter-region transfer OUT of Tel Aviv is **$0.08/GB** to every destination checked, against $0.02/GB out of Ireland, and the charge is asymmetric. Full tiers, destination list and the architectural consequence are in `references/cost-mechanics.md`.
- **The Israeli-region cost story is a network story, not a compute story.** Compute is a flat ~5% premium; network is 22% and 4x. A comparison that models a 10% compute premium and zero egress delta has it backwards on both counts.
**When to use il-central-1:**
- Data residency requirements mandate Israeli hosting
- Latency-sensitive applications serving Israeli users (1-3 ms local vs. 45-65 ms to Western Europe)
- Financial services, healthcare, or government applications
- Compliance with Israeli Privacy Protection Authority regulations

**When eu-west-1 may be better:**
- No data residency requirements and cost is the primary concern
- Applications serving both Israeli and European users
- Broader service availability (some newer AWS services launch in eu-west-1 before il-central-1)

**Pricing URL:** `https://aws.amazon.com/ec2/pricing/on-demand/` (filter by region: Israel)

### Step 3: Compare Google Cloud Platform (me-west1)

GCP's `me-west1` region is located in Tel Aviv and opened in 2022. (An earlier version of this skill dated general availability to November 2022 and called it Google's first Middle East region; neither could be sourced, and me-central1 in Doha complicates the second claim, so both were dropped rather than carried forward.)

**Available services in me-west1:**
- Compute Engine, Cloud Storage, Cloud SQL
- GKE (Kubernetes), Cloud Run (serverless containers)
- Cloud Functions, Pub/Sub, BigQuery
- Memorystore (Redis), Cloud Spanner

**Pricing benchmarks:**
- Compute Engine is generally 5-10% cheaper than equivalent AWS EC2 in il-central-1
- Cloud Storage pricing is competitive with S3
- Sustained use discounts apply automatically (up to 30% for running instances 100% of the month)
- Committed use discounts: roughly 37% (1-year) and 55% (3-year) off for predictable workloads, but see the commitment-obligations table in Step 9 first: a GCP resource-based CUD cannot be cancelled and is bound to a region and machine series

**GCP advantages for Israeli developers:**
- BigQuery is available in me-west1 (important for data analytics with Israeli data)
- Cloud Run has a free tier; check its current monthly request and compute allowances on the Cloud Run pricing page rather than quoting a remembered figure
- Firebase hosting with me-west1 backend provides low-latency full-stack hosting
- GCP for Startups program is active in Israel (see Step 7)

**Pricing URL:** `https://cloud.google.com/products/compute/pricing/general-purpose` with the region selector set to Tel Aviv (me-west1). The shorter `/products/compute/pricing` and `/compute/all-pricing` URLs now redirect to a marketing page carrying no tables, which is a common way an agent ends up quoting from memory.

### Step 4: Compare Microsoft Azure

Azure serves Israel primarily through the following regions:

**Regions:**
- **Israel Central** (launched late 2023): Full Azure region in Israel
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
- Azure Reservations: Microsoft advertises up to 72% against pay-as-you-go for one-year or three-year terms. See the commitment-obligations table in Step 9 for the cancellation cap and the 1 February 2027 exchange change

**Pricing URL:** `https://azure.microsoft.com/en-us/pricing/calculator/`

### Step 5: Compare Oracle Cloud Infrastructure (il-jerusalem-1)

Oracle's Israel Central region `il-jerusalem-1` sits in a hardened underground data center beneath the Har Hotzvim tech park in Jerusalem. (The commonly-repeated specifics, a July 2021 launch and a 17-story building above it, trace to press coverage that is not currently fetchable, so treat them as approximate rather than quoting them.) It is a **single-availability-domain** region, which matters if the pitch is high availability.

**Available services:** Compute (VM and bare-metal), Block Volumes, Object Storage, Autonomous Database, MySQL HeatWave, PostgreSQL, OKE (Kubernetes), Functions, Fusion Cloud Applications.

**Pricing posture:**
- Oracle publishes a single global price list: "OCI services are priced the same for all global regions (including government regions)". This is unusual and genuinely simplifies a comparison, but verify on the Israel price list before quoting
- Egress: the first 10 TB/month outbound is included free, one of the more aggressive egress policies among the hyperscalers and a real differentiator given AWS's Israeli egress premium
- Price list: `https://www.oracle.com/il-en/cloud/price-list/` (renders unit prices only under JavaScript). Cost estimator: `https://www.oracle.com/il-en/cloud/costestimator.html`

**When to consider it:** Oracle Database or Exadata workloads where licensing economics already favour OCI; high-security deployments where the physical hardening is a genuine requirement; egress-heavy predictable workloads where the free 10 TB moves the needle; regulated buyers who want an Israeli region from a vendor outside the AWS/Google Nimbus contract.

**Limitations:** smaller third-party ecosystem and managed-service catalogue than AWS/Azure/GCP, fewer Israeli startup-credit programmes and accelerator partnerships, and some newer OCI services (generative-AI features especially) reach US/EMEA regions first.

### Step 5b: Evaluate Israeli Cloud Providers

**Kamatera (`https://www.kamatera.com`):**
- Israeli-founded. Its pricing page lists a single Israeli location, **Tel Aviv**; if a user needs a specific Israeli site, confirm the current footprint with Kamatera rather than assuming several
- Entry pricing from about **$4/month** for a basic VPS (1 vCPU, 1 GB RAM, 20 GB NVMe, 5 TB traffic), billed hourly or monthly, with a 30-day free trial
- Good for small projects, dev and staging environments, and Israeli-market applications
- Limitations: smaller service catalogue than the hyperscalers and no managed Kubernetes, so a side-by-side that includes a managed-database or managed-K8s row should note that you operate those yourself
- Native NIS billing was historically advertised; confirm with Kamatera sales if shekel-denominated invoices are a requirement, since billing-currency policies have shifted across regional resellers

**Note:** HostIL (`hostil.co.il`) appears in some directories but its current operational status could not be verified. Check the site directly before relying on it.

**Akamai / Linode**: Akamai has a Tel Aviv office but there is no Linode Connected Cloud data center in Israel. Israeli users route to Frankfurt or Amsterdam, adding roughly 45-65 ms. Do not present Linode as an "Israeli region" option.

**DigitalOcean, Vultr, Hetzner, OVH**: none operates a data center in Israel. Israeli users typically use Frankfurt, Strasbourg or Amsterdam at 45-65 ms to Tel Aviv. Hetzner remains the lowest-cost EU option for workloads with no residency requirement, but it is no longer as cheap as older comparisons suggest: its 15 June 2026 price adjustment took the entry CX23 from EUR 3.99 to **EUR 5.49/month net**, with some CPX and CCX lines rising considerably more.

### Step 6: Compare Data Residency and Compliance

Israeli data-protection and sector rules decide the shortlist before price does. The full treatment,
including the per-provider residency table and Project Nimbus, is in `references/compliance.md`.

The points that change a recommendation:

- **Privacy Protection Law Amendment 13** has been in force since 14 August 2025. Note what it did
  and did not do: the cross-border transfer rules live in the 2001 transfer regulations and predate
  it; Amendment 13 is the enforcement, DPO and breach-notification overhaul. Do not tell a user their
  pre-2025 architecture was previously unregulated.
- **Cross-border transfer needs a documented basis**, not a default. Do not silently fall back to
  eu-west-1 or europe-west4 for an Israeli service handling personal data. The Privacy Protection
  Authority has tightened the practical conditions for the "controller is responsible" pathway; its
  site is not fetchable by an agent, so send the user to check the current guidance.
- **Bank of Israel supervised entities**: the binding constraint is a supervisory process, not a
  hosting location. Directive 364 (in force 18/05/2026, replacing 357, 361 and 363) governs IT,
  information-security and cyber risk. What is tested is the outsourcing assessment, materiality,
  exit and reversibility planning, contractual audit rights and the subcontractor chain. Region
  choice falls out of that, so engage compliance and the supervisor before shortlisting.
- **Healthcare and government**: HMO/hospital data and government tenders commonly carry Israeli
  locality requirements, but they are imposed by specific circulars and tender clauses. Ask for the
  actual clause before designing to it rather than assuming the strictest reading.
- **Residency is not sovereignty.** Every hyperscaler Israeli region keeps data in Israel while the
  operator stays subject to its home jurisdiction.
- **PCI DSS applies independently** for payment-card data.

### Step 6b: Project Nimbus (Government Sovereign Cloud)

Project Nimbus is the $1.2 billion Israeli-government cloud contract awarded to AWS and Google in 2021. It is **not a public-tenant service**: it is a sovereign tenant for government ministries, security services and approved partners. **Do not recommend it to startups or commercial customers.** It is relevant only if the user is a ministry, a defence-sector vendor or a contractor on a classified workload, or is deciding which hyperscaler to align with for future government tenders. Full detail, including the contractual sovereignty terms, is in `references/compliance.md`.

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

Rough round-trip times from Tel Aviv: **1-3 ms** to any of the three Tel Aviv regions (AWS il-central-1, GCP me-west1, Azure Israel Central), **3-6 ms** to Oracle il-jerusalem-1, **45-65 ms** to Western Europe, **130-160 ms** to US East. The full table is in `references/cost-mechanics.md`, with the caveat that **none of these figures has a published provider source**, so use them to shortlist and measure from the user's own network if a decision turns on latency.

For user-facing applications serving Israeli users, a local region's sub-5 ms is noticeably better than 50 ms+, and the difference is amplified by the number of sequential calls an API makes. For batch processing and data pipelines latency matters little; optimize for cost. A CDN mitigates latency for static assets regardless of origin region.

### Step 9: Calculate Total Cost of Ownership

**Commitment discounts** (AWS Savings Plans up to 72%, GCP CUDs, Azure Reservations up to 72%) are covered with their obligations, cancellation terms and the 1 February 2027 Azure exchange change in `references/cost-mechanics.md`. Read it before recommending a term: commit to the trailing-90-day floor rather than the average, never commit mid-migration, and never commit while credits are still covering the bill.

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

Structure the answer as:

1. **Summary table** for the user's actual requirements, with every cell labelled by pricing column and date checked, and an **egress line** included
2. **Credit-adjusted comparison**: effective monthly cost after credits, plus comparable programmes on other providers the user may not know about
3. **Primary recommendation** with justification. If credits favour one provider short-term, say so, but also name the best long-term choice after they expire
4. **Alternative** with the tradeoff stated
5. **Cost optimization**: right-sizing, spot, and commitments only where the workload is genuinely steady (see the obligations table before recommending a term)
6. **Migration considerations**: effort, lock-in, and the egress cost of leaving
7. **Next steps**: links to the free tiers and trials for hands-on evaluation

State whether every figure is ex-VAT or inc-VAT, and give the date each price was checked.

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
3. Compare AWS il-central-1 vs. Azure Israel Central, but do the outsourcing assessment and engage the Banking Supervision Department first; for a supervised entity the region shortlist falls out of that process
4. Calculate commitment pricing for the workloads that are genuinely predictable, and read the commitment-obligations table in Step 9 before recommending a term. A 3-year capacity commitment taken mid-migration, before the instance mix has settled, is the classic way to lock in the wrong shape
5. Include migration costs: AWS Migration Hub or Azure Migrate tooling, network setup, testing

Result: Recommend Azure Israel Central as primary due to hybrid licensing benefits (bring existing Windows/SQL Server licenses) and strong financial services compliance posture. AWS il-central-1 as alternative if the team has more AWS expertise. Estimated monthly cost: $15,000-25,000/month. Do NOT default to 3-year reservations here: this is a migration, so commit only to the trailing steady-state floor once it exists, start with the flexible instrument, and note that Azure reservations bought from 1 February 2027 lose exchange rights for savings-plan-eligible services. Quote whether the figure is ex-VAT or inc-VAT. Do NOT pitch Azure Government for future Israeli government contracts: it is a US-sovereign cloud for US government customers. For Israeli public-sector work the relevant conversation is the commercial Israel Central region plus the applicable tender requirements.

### Example 3: Developer Choosing Hosting for a Side Project

User says: "I'm building a personal project, a Hebrew NLP tool. I need a small server with GPU access for inference, plus a database. Budget is minimal."

Actions:
1. Identify GPU needs: inference-only requires smaller GPU (T4 or equivalent)
2. Compare GPU pricing: AWS g4dn.xlarge, GCP n1-standard-4 + T4, Azure NC4as_T4_v3
3. Consider spot/preemptible instances for 60-80% cost savings on GPU compute
4. Check if GPU instances are available in Israeli regions (limited availability)
5. Evaluate alternatives: Kamatera GPU instances, or Lambda Labs / RunPod for inference-only

Result: For inference-only, the cheapest path in 2026 is a specialty GPU provider (Lambda, RunPod or Vast.ai) on an L4 or T4-class instance, paired with a small managed PostgreSQL anywhere: GCP me-west1 Cloud SQL micro, AWS RDS db.t4g.micro in il-central-1, or a Kamatera VM. If the project needs Israeli residency or sub-5 ms latency, use GCP me-west1 with a spot GPU plus Cloud SQL micro, and price the egress rather than assuming it is free. Quote the NIS figure at the current Bank of Israel rate rather than a remembered one. For an Israeli AI startup doing real training rather than inference, apply to the IIA Telem programme before locking in a hyperscaler GPU reservation. For ultra-low cost, CPU inference with quantized models is worth considering if latency allows.

## Gotchas

- **Every list price here has a shelf life of weeks, and the credit programmes move too.** Between the last review and this one AWS replaced its whole free tier, renamed all three support plans and doubled Activate Portfolio, Google restructured its startup programme, Hetzner raised prices and Lambda's H100 rate rose roughly 60%. Treat every number as an anchor to re-verify, and tell the user the date you checked. **If a fetch fails or returns no price table, say the figure is unverified and give the user the URL. Never present an embedded figure as current after a failed fetch.** An agent quoting these figures as current months later is this skill's most likely failure mode.
- **Credits blind spot**: when a user has credits with one provider, agents tend to recommend that provider without checking the others. Always compare credit programmes across ALL providers first. Note also that credits have expiry dates independent of consumption, unused balances are forfeited, and buying a committed-spend instrument while credits are covering the bill wastes both.
- **Get the region roster right.** Israel has four hyperscaler regions: AWS il-central-1, GCP me-west1, Azure Israel Central and Oracle il-jerusalem-1. Do not tell a user Oracle has no Israeli region, and do not offer AWS me-south-1 (Bahrain) as the "closest fallback"; it stopped being that when il-central-1 opened. Akamai/Linode has a Tel Aviv office but no Israeli data center, so Frankfurt is the usual fallback there. Note also that il-central-1 pricing differs from eu-west-1, so global list prices understate it.
- **Israeli VAT: get the mechanism right and say which number you are quoting.** Where a provider bills through an Israeli-registered entity, the invoice carries 18% VAT for business customers too, and a VAT-registered business recovers it as input tax (מס תשומות) rather than being billed net. That changes two different numbers: cash outlay (the invoice is 18% above an ex-VAT quote) and true cost (a fully-deducting business bears none of it; an entity that cannot fully deduct bears all of it). Always state ex-VAT or inc-VAT, verify per provider whether the billing entity is Israeli-registered, and send anyone whose deduction position is not straightforward to their accountant.
- **Cross-border transfer requires a documented basis under Privacy Protection Law Amendment 13** (in force since August 14, 2025). Do not silently default to eu-west-1 or europe-west4 for an Israeli SaaS handling personal data, the choice needs to fit one of the Section 2 exceptions (adequate jurisdiction list, controller-responsibility under the April 2026 PPA guidance, etc.). Israeli data residency requirements for government contracts may mandate hosting within Israel; agents may otherwise recommend cheaper international regions that violate these requirements.
- **Currency drift**: USD/ILS has fallen from roughly 3.70 in 2024 to **2.985 on 19 August 2026** (Bank of Israel representative rate), so a NIS budget set at the older rate is roughly 20-25% too generous in USD terms. Right-size to the current rate rather than recycling an old conversion, including any figure quoted in this skill.
- **Project Nimbus is not a startup option.** Do not recommend Project Nimbus to commercial customers, it is a government sovereign-tenant contract on AWS and Google, not a public cloud product.
- **Spot capacity in a small region is thinner and more volatile than in eu-west-1**, because there are fewer zones and less spare fleet, so build capacity-aware fallback. Do not attribute spot swings to Shabbat or holiday demand: that mechanism is unsourced and AWS spot has not been demand-auction-priced since 2017.

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

AWS, GCP and Oracle bill in USD. Azure offers some NIS billing via Israeli enterprise agreements (contact Microsoft Israel), and Kamatera bills natively in NIS. For USD providers, set budgets with a currency buffer, pull the current Bank of Israel representative rate rather than reusing an old conversion, and rebudget quarterly on a 3-month trailing average. Fuller guidance, including how to size the buffer and when a forward contract is worth it, is in `references/cost-mechanics.md`.

## Reference Links

**Machine-readable price APIs (prefer these; they are fetchable and re-checkable, unlike the marketing pages):**
- AWS Price List API, data transfer: `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/index.json`
- AWS Price List API, EC2 per region: `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/il-central-1/index.json`
- Azure retail price API: `https://prices.azure.com/api/retail/prices`

**Provider pricing pages (treat as the source of truth for list prices, but note several render prices only in JavaScript):**
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
