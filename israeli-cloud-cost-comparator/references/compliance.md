# Israeli Data Residency and Compliance

The full detail behind Step 6 of SKILL.md: Privacy Protection Law Amendment 13 and the cross-border
transfer position, the sector overlays (banking, healthcare, government), the per-provider residency
table, and Project Nimbus.

Read this before advising on any architecture that moves Israeli personal data out of the country.

### Step 6: Compare Data Residency and Compliance

Israeli data protection considerations:

**Privacy Protection Law Amendment 13 (in force since August 14, 2025):**
- Note what Amendment 13 did and did not do. The cross-border transfer rules live in the 2001 transfer regulations and long predate it; Amendment 13 is the enforcement, DPO and breach-notification overhaul. An agent that thinks the transfer regime began in 2025 will tell a user their pre-2025 architecture was previously unregulated, which is the wrong remediation story. Personal data of Israeli residents may be transferred abroad only if the destination jurisdiction provides "adequate" protection (or one of the other Section 2 exceptions applies)
- The Privacy Protection Authority maintains a list of approved jurisdictions; the EU, UK, and a small set of other GDPR-aligned countries are on it
- The Privacy Protection Authority has published interpretive guidance on the "data controller is responsible" pathway in the cross-border transfer regulations, tightening the practical conditions for relying on it. The PPA site is not fetchable by an agent, so check the current guidance directly rather than relying on a date or a summary from here. Treat any cross-border architecture as a documented decision rather than a default
- A Data Protection Officer (DPO) is now required for many controllers and large data holders
- Breach notification is mandatory and timelines are tighter than under the prior regime

**Sector-specific overlays still apply:**
- **Financial institutions under Bank of Israel supervision: the binding constraint is a supervisory process, not a hosting location.** The operative framework is Proper Conduct of Banking Business Directive 364 on management of IT, information security and cyber protection risks, in force from 18/05/2026, which repealed the former Directives 357, 361 and 363. What the supervisor actually tests is the outsourcing assessment, materiality, exit and reversibility planning, contractual audit and inspection rights, and the subcontractor chain. Region choice is an output of that process, not an input, so engage compliance and the Banking Supervision Department before shortlisting a provider
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
| Kamatera | Yes (Tel Aviv; its pricing page lists one Israeli location) | Israeli company | ISO 27001 |
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

## Two things to keep straight

**Amendment 13 did not create the cross-border transfer regime.** Those rules live in the 2001
transfer regulations and long predate it. Amendment 13 (in force 14 August 2025) is the enforcement,
DPO and breach-notification overhaul. An agent that believes the transfer regime began in 2025 will
tell a user their pre-2025 architecture was previously unregulated, which is the wrong remediation
story.

**Residency is not sovereignty.** Every hyperscaler Israeli region keeps data physically in Israel
while the operator remains subject to its home jurisdiction. The residency table's "operator retains
control" column is the point, not a footnote, and it is why Project Nimbus exists as a separate
contractual arrangement rather than as a region.
