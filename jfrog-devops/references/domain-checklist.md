# Domain Coverage Checklist: JFrog DevOps

Coverage contract for this skill. Each row states whether the skill covers the topic
and where. Rows marked "Out of scope (explicit)" must be re-litigated on every update:
if a user would plausibly ask for it, or it became capturable since the last review,
promote it.

Last reviewed: 2026-09-02 (v1.4.0). Bootstrapped this cycle from the JFrog
documentation structure and an expert review, so the "not covered" rows below are a
deliberate record of what is missing, not an oversight.

## Artifact management

| Topic | Status | Where |
|-------|--------|-------|
| Operation routing (which product handles what) | Covered | Step 1 |
| Repository types: local, remote, virtual, federated | Noted, not explained | Step 1 table, references/api-reference.md |
| Repository CRUD via REST and CLI | Covered | Step 1, api-reference.md, scripts/artifactory_client.py |
| Artifact deploy / download / delete / copy / move | Covered | api-reference.md, scripts/artifactory_client.py |
| AQL query patterns | Covered | Step 6 |
| Properties (get / set / delete) | Covered in the client, not exposed on its CLI | scripts/artifactory_client.py |
| Docker registry configuration, including the subdomain / repository-path / port hostname methods | Covered | Step 3 |
| Build info publish and promotion, copy-vs-move semantics and the permission each needs | Covered | Step 4, scripts/artifactory_client.py |

## Security

| Topic | Status | Where |
|-------|--------|-------|
| Access tokens, reference tokens, and the API-key end of life | Covered | Step 2, api-reference.md |
| OIDC with GitHub Actions, and why it does not authenticate the Docker daemon | Covered | Step 2 Option C, Step 3 |
| Xray scanning commands and their differences (audit vs docker scan vs build-scan) | Covered | Step 5 |
| What makes a CI gate real, and the eight ways one silently becomes a no-op | Covered | Step 5 |
| Xray indexing as a gate prerequisite | Covered | Step 5, Troubleshooting |
| Watch and policy modelling (policy, rule, priority, fail_build vs block_download) | Partially covered | Step 5, scripts/xray_client.py |
| SBOM formats: CycloneDX from the CLI, SPDX only from the UI or exportDetails | Covered | Step 5 |
| CBOM as a Cryptography Bill of Materials | Covered | Step 5 |
| Frogbot for PR scanning, and which scanners need Advanced Security | Covered | Step 5 |
| Curation | Noted, not explained | Step 1 table, Reference Links |
| ML model scanning (jf malicious-scan) | Covered | Step 5b |

## MLOps

| Topic | Status | Where |
|-------|--------|-------|
| Machine Learning repository type and the Hugging Face layout migration | Covered | Step 5b, Gotchas |
| JFrog ML and the AI Catalog | Covered | Step 5b |
| FrogML SDK, Xet protocol scope | Covered | Step 5b |

## Israel-specific

| Topic | Status | Where |
|-------|--------|-------|
| JFrog as an Israeli vendor: local support, sales, SEs | Covered | Gotchas |
| SaaS pricing tiers that JFrog publishes | Covered | Gotchas |
| Data residency and in-country cloud regions | Covered as UNVERIFIABLE | Gotchas. JFrog no longer publishes a region list; the skill says so and tells the reader to confirm with JFrog rather than asserting availability |
| Pipelines end of life and its effect on Israeli teams still on it | Covered | Gotchas |

## Not covered (carried, with rationale)

These are real gaps that an expert review raised on 2026-09-02. They are recorded
here rather than silently omitted, and they are the queue for the next cycle. None of
them makes the skill's existing content wrong; each makes it incomplete.

| Topic | Why not this cycle | Re-open when |
|-------|--------------------|--------------|
| Permissions and access model: Permission Targets, the Read/Annotate/Deploy/Delete/Manage actions, scoped vs platform tokens, and which permission each documented operation needs | Substantial new section; this cycle's budget went to correcting four wrong technical claims and repairing the two bundled scripts. The one place it bites today is documented inline (promote-with-move needs Delete on the source) | Next cycle. This is the highest-value addition: in practice most failures on this skill's happy path are permission failures, and Troubleshooting currently answers 401 with "generate a new token", which is wrong for the more common 403 shape |
| Release Bundles v2, Lifecycle, Distribution, and AppTrust / Evidence (`jf rbv2`, `jf evd`) | Was already logged as the top deferred item before this cycle and is still deferred. It supersedes build-info promotion as the current promotion model, so Step 4 points at the previous generation | Next cycle, together with a forward pointer from Step 4 |
| Virtual repository resolution ORDER, locals-first, default deployment repository, remote caching and missed-retrieval TTLs, exclude patterns as dependency-confusion mitigation | Example 1 tells the reader to create a virtual repo and explains none of it | Next cycle |
| Checksum-based storage and deduplication, and the consequence that DELETE does not free space until garbage collection; the trash can and its retention window; built-in Cleanup Policies | Example 4 promises a cleanup script with dry-run and the skill ships neither the policy context nor the safety model | Next cycle. Pair it with the AQL caveat that `stat.downloaded` is empty for never-downloaded artifacts, so the documented "find unused artifacts" query misses exactly those |
| Projects: project keys, project-scoped repos and the `<key>-<repo>` convention, project-scoped watches and roles | `--project` is offered in Step 5 as a gate selector with no explanation of what a project is | Next cycle, alongside the permissions section |
| Replication, Federated repository conflict and full-sync semantics, Edge nodes, and disaster recovery (system export/import, the filestore-plus-database pairing) | Platform-operations scope rather than the artifact-pipeline scope this skill takes | When a user asks, or when the skill grows a platform-administration section |
| REST API operational limits: SaaS rate limits and 429 handling, AQL result caps and `range.total` pagination, the violations API 100-per-page cap | The bundled clients set timeouts and back off on 429. Retries are split: idempotent methods retry on 429 and 5xx, while the read-shaped POSTs (AQL search, Xray summary, scan status, violations) retry on 429 ONLY, and the writes (deploy, promote, create policy/watch, trigger scan) are never retried, because a 429 means the request was not processed whereas a 5xx on a write may mean it was. Docstrings warn about pagination, but the skill body does not discuss it and the clients still do not walk pages | Next cycle |
| Repository naming conventions (`<team>-<tech>-<maturity>-<locator>`), suffix discipline, and repo keys being effectively immutable | The layout block shows example keys with no rules behind them | Next cycle |

## Out of scope (explicit)

| Topic | Why out of scope | Re-open when |
|-------|------------------|--------------|
| General Docker and CI/CD questions with no JFrog involvement | Stated in the description's "Do NOT use for" clause | Never |
| Writing the application build itself (Maven, Gradle, npm configuration beyond resolution against Artifactory) | Different domain; the skill starts where the artifact exists | Never |

## Authoritative sources

- JFrog documentation index: https://docs.jfrog.com/llms.txt (every page has a `.md` variant)
- Artifactory REST API: https://docs.jfrog.com/artifactory/reference
- Xray / Security REST API: https://docs.jfrog.com/security/llms.txt
- JFrog CLI source of truth for commands and flags: https://github.com/jfrog/jfrog-cli-security (`cli/docs/flags.go`, `cli/scancommands.go`) and https://github.com/jfrog/jfrog-cli
- Frogbot: https://github.com/jfrog/frogbot
