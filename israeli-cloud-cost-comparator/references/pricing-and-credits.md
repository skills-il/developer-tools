# Cloud Pricing and Credits Reference (Israel)

**Every figure in this file has a shelf life of weeks.** It is kept separate from SKILL.md precisely
so it can be re-checked and replaced as a unit. Each figure below was read on the provider's own page
on **19 August 2026**. Before quoting any of them to a user, re-read the source and tell the user the
date you checked.

#### 7a. Free Tier and Trial Credits

| Provider | Trial Credits | Trial Duration | Always-Free Tier |
|----------|--------------|----------------|------------------|
| AWS | Up to $200 ($100 on signup, up to $100 more earned by exploring services) | 6 months, or until credits run out | Free usage of select services |
| GCP | $300 | Free-tier trial | 20+ free products |
| Azure | $200 | 30 days | 65+ always-free services |

**AWS overhauled its free tier in 2025 and it is no longer what most documentation describes.** It is now a lump-sum credit ("up to $200 over 6 months to build, break things, and experiment"), and **the account closes on its own 6 months after opening or when the credits run out, whichever comes first**. The old model, 12 months of per-service monthly limits with no lump sum, applies only to accounts created before the change. Do not tell a user AWS "gives service-based limits, not credits"; that is now false, and the 6-month self-closing account is a planning constraint the other providers do not have.

#### 7b. Startup Credit Programs (For Registered Companies)

| Program | Credits | Duration | How to Apply |
|---------|---------|----------|--------------|
| AWS Activate (Portfolio) | Up to $200,000 | Pre-Series B | Through approved accelerators, or the AWS Israeli startup team. `https://aws.amazon.com/startups/credits/` |
| AWS Activate Founders (self-funded) | Up to $5,000, starting at $1,000 | Bootstrapped or self-funded | Apply directly via the AWS Activate console |
| AWS Credits for AI Startups | $200,000+ | Invite only, post-Activate-Portfolio | Not self-service. Note this is NOT a published "$300,000 Generative AI tier"; that figure does not appear on the AWS page |
| Google for Startups Cloud, early stage | $200,000, or up to $350,000 for AI-first startups | Seed to Series A | Through Google for Startups. `https://cloud.google.com/startup` |
| Google for Startups Cloud, pre-funded | $2,000 to build an MVP | Pre-funded | Same programme, lower tier. Easy to miss and worth applying for early |
| Microsoft Founders Hub | Up to $150,000 | VC- or accelerator-backed | `https://www.microsoft.com/en-us/startups`. A lower self-serve tier exists but its amount is not published on that page, so ask rather than quoting a figure |
| Israel Innovation Authority, standard R&D grant | Typically 20-50% of approved R&D expenses (including cloud) | Per approved project | Israel Innovation Authority, repayable as royalties if the company commercializes |
| Israel Innovation Authority, Telem Program (subsidized B200 access via Nebius) | Reduced-price access to a slice of a 1,000-Nvidia-B200 supercomputer, split 70% hi-tech / 30% academic research | Allocations run in months, confirm the current terms | `https://innovationisrael.org.il`. **The IIA site is behind Cloudflare and returns 403 to automated fetches**, so an agent cannot read the current terms and must send the user to the page rather than summarising it. The published minimum-request figures could not be verified this cycle, so ask rather than quoting them |

**Recommendation**: Early-stage startups should apply to all three hyperscaler programs in parallel. On current published figures the combined ceiling is well into six figures (AWS Activate Portfolio up to $200,000, Google up to $350,000 for AI-first, Founders Hub up to $150,000), which covers 1-2 years of near-free hosting for most seed-stage infrastructure. Quote the ceilings as ceilings, not as expected awards. AI-heavy startups should also apply for the IIA Telem allocation, which is materially cheaper per B200-hour than on-demand H100/H200 at the hyperscalers and keeps training data inside Israel.

### Step 9b: GPU and AI Workload Pricing

GPU pricing is a separate cost axis. The 2026 market has bifurcated:

**Hyperscaler list (per H100 GPU-hour, on-demand):** AWS ~$6.88 (p5 8-GPU $55-60/hr); GCP A3 ~$10-11 (8-GPU $80-90/hr); Azure NC-H100 ~$6.98 (East US). AWS savings plans / reserved capacity bring effective rates closer to ~$1.90/GPU-hr.

**Specialty clouds (per H100 GPU-hour, on-demand, checked August 2026):** Lambda H100 SXM $3.99-$4.19 (its on-demand rate rose materially, older quotes near $2.50 are stale); RunPod H100 PCIe $1.99, NVL $2.59, SXM $2.69 on Community Cloud; Vast.ai is a marketplace whose floor moves hourly. Still cheaper than hyperscaler list, but the gap has narrowed, and none has an Israeli presence (80-150 ms latency) or a comparable managed-service catalog. **Re-read the provider page before quoting: these rates move month to month, and this is the fastest-drifting section of this skill.**

**H200 / B200 (August 2026):** RunPod H200 from $3.59/hr and B200 from $5.98/hr on Community Cloud; Lambda B200 $6.69-$6.99/hr; Lambda GH200 $2.29/hr. Lambda did not list an H200 on-demand rate when checked, so do not quote one.

**IIA Telem Program (Nebius):** Subsidized B200 access for Israeli companies and academic groups, 70/30 hi-tech/academia split. Allocation-period and minimum-request figures are NOT stated on the IIA announcement, so ask the user to check the live programme terms rather than quoting any. Reduced pricing vs. commercial, data stays in Israel. Most cost-effective AI training option for Israeli startups that can plan allocations ahead; apply before committing to a hyperscaler GPU reservation.

**GPU recommendation framework:**
- **Inference, latency-sensitive, Israeli users**: GCP me-west1 T4/L4 if available, or AWS il-central-1
- **Training, no residency, budget-sensitive**: Lambda / RunPod / Vast.ai in EU or US
- **Training, Israeli AI R&D**: Apply for IIA Telem first; fall back to specialty providers
- **Steady-state inference at scale**: AWS Savings Plans on g5/g6 or GCP CUDs close most of the gap with specialty providers above ~60% utilization

## Why this file exists

Between the previous review of this skill and 19 August 2026:

- AWS replaced its entire free tier (per-service limits for 12 months became a lump sum of up to
  $200 with a self-closing 6-month account)
- AWS renamed all three paid support plans and retired the Developer and Business tiers
- AWS Activate Portfolio doubled from $100,000 to $200,000, and Founders rose from $1,000 to up to
  $5,000
- Google restructured its startup programme to $200,000 / $350,000 AI-first, plus a $2,000
  pre-funded tier
- Hetzner raised cloud prices on 15 June 2026 (entry CX23 from EUR 3.99 to EUR 5.49/month net)
- Lambda's on-demand H100 rate rose roughly 60%
- USD/ILS fell from about 3.10 to 2.985

That is six months of drift in the numbers a cost comparison rests on. Treat anything here that has
not been re-verified as a lead, not a fact.
