---
name: jfrog-devops
description: Manage JFrog Artifactory repositories, artifacts, Docker registry, build info, ML model registry (JFrog ML / AI Catalog), and Xray security scanning for DevOps and MLOps workflows. Use when user asks about JFrog, Artifactory, Xray, Curation, Frogbot, JFrog ML, AI Catalog, artifact management, "deploy artifact", Docker registry with Artifactory, Hugging Face / MLflow model registry, build promotion, vulnerability scanning, SBOM (SPDX/CycloneDX/VEX), or DevOps artifact pipeline. Covers REST API operations, JFrog CLI usage, Docker registry configuration, OIDC with GitHub Actions, and security scanning patterns. Do NOT use for general Docker or CI/CD questions unrelated to JFrog.
license: MIT
allowed-tools: Bash(curl:*) Bash(jf:*) Bash(docker:*) Bash(python3:*)
compatibility: Requires network access to JFrog instance (SaaS or self-hosted). JFrog CLI 2.75.0+ (jf) is the floor for OIDC; 2.122.0 is current as of August 2026.
---

# JFrog DevOps

## Instructions

### Step 1: Identify the DevOps Operation
| Operation | JFrog Tool | API/CLI | Auth Required |
|-----------|-----------|---------|---------------|
| Upload/deploy artifact | Artifactory | PUT /{repo}/{path} or jf rt upload | Yes |
| Download artifact | Artifactory | GET /{repo}/{path} or jf rt download | Yes (unless anonymous) |
| Search artifacts | Artifactory | AQL or jf rt search | Yes |
| Docker push/pull | Artifactory | Docker API or jf docker | Yes |
| Publish build info | Artifactory | PUT /api/build or jf rt build-publish | Yes |
| Promote build | Artifactory | POST /api/build/promote | Yes (admin) |
| Scan for CVEs | Xray | POST /api/v1/scanArtifact or jf xr scan | Yes |
| Create watch/policy | Xray | POST /api/v2/watches | Yes (admin) |
| Generate report | Xray | POST /api/v1/reports/vulnerabilities | Yes |
| Export SBOM (SPDX or CycloneDX) | Xray | POST /xray/api/v2/component/exportDetails, or jf scan --format=cyclonedx (CycloneDX only) | Yes |
| Vet OSS packages before download | Curation | Configured per remote repo | Yes (admin) |
| Manage ML model (Hugging Face, MLflow, NIM) | Artifactory ML repo | jf rt upload or FrogML SDK | Yes |
| Cleanup old artifacts | Artifactory | AQL + delete or retention policies | Yes (admin) |

### Step 2: Configure Authentication

**Option A: JFrog CLI (recommended):**
```bash
# Configure JFrog CLI with access token (recommended)
jf config add my-server \
  --url="https://acme.jfrog.io" \
  --access-token="YOUR_ACCESS_TOKEN" \
  --interactive=false

# Verify connection
jf rt ping
```

**Option B: REST API with curl:**
```bash
# Read the host and token from the environment so neither is hardcoded
# or left in shell history. JF_URL is your platform base URL.
export JF_URL="https://acme.jfrog.io"

# Using access token (recommended)
curl -H "Authorization: Bearer $JF_ACCESS_TOKEN" \
  "$JF_URL/artifactory/api/system/ping"

# Using identity token (reference token, also works as Bearer)
curl -H "Authorization: Bearer $JF_REFERENCE_TOKEN" \
  "$JF_URL/artifactory/api/system/ping"
```

> Legacy API keys (`X-JFrog-Art-Api` header) reached end of life in Q4 2024 and are disabled by default in Artifactory 7.98+. Use access tokens or reference tokens (both sent as `Authorization: Bearer`).

**Option C: OIDC for CI (no long-lived secrets):**
```yaml
# GitHub Actions example with jfrog/setup-jfrog-cli
- uses: jfrog/setup-jfrog-cli@v5
  with:
    oidc-provider-name: my-github-oidc-provider
  env:
    JF_URL: https://acme.jfrog.io
```
> v5 runs on the node24 Actions runtime. v4 stays on node20 and is still supported, so pin `@v4` only if your runner is held back; otherwise use `@v5`.
Configure the OIDC integration once in JFrog (Administration > Identity and Access > Integrations > OIDC), then CI jobs exchange a short-lived JWT for an access token at runtime. JFrog-recommended path for GitHub Actions, GitLab, Buildkite, and Jenkins.

**Option D: Python client:**
```python
import requests

class ArtifactoryClient:
    """Client for JFrog Artifactory REST API."""

    def __init__(self, base_url, access_token):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })

    def ping(self):
        """Health check."""
        r = self.session.get(f"{self.base_url}/api/system/ping")
        return r.text == "OK"

    def list_repos(self, repo_type=None):
        """List repositories, optionally filtered by type."""
        params = {}
        if repo_type:
            params["type"] = repo_type
        r = self.session.get(f"{self.base_url}/api/repositories", params=params)
        return r.json()

    def deploy_artifact(self, repo_key, path, file_path, properties=None):
        """Deploy (upload) an artifact to a repository."""
        url = f"{self.base_url}/{repo_key}/{path}"
        if properties:
            prop_str = ";".join(f"{k}={v}" for k, v in properties.items())
            url += f";{prop_str}"
        with open(file_path, "rb") as f:
            r = self.session.put(url, data=f,
                                 headers={"Content-Type": "application/octet-stream"})
        return r.json()

    def download_artifact(self, repo_key, path, dest_path):
        """Download an artifact from a repository."""
        r = self.session.get(f"{self.base_url}/{repo_key}/{path}", stream=True)
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest_path

    def search_aql(self, aql_query):
        """Search using Artifactory Query Language."""
        r = self.session.post(
            f"{self.base_url}/api/search/aql",
            data=aql_query,
            headers={"Content-Type": "text/plain"}
        )
        return r.json()

    def get_build_info(self, build_name, build_number):
        """Get build information."""
        r = self.session.get(f"{self.base_url}/api/build/{build_name}/{build_number}")
        return r.json()

    def promote_build(self, build_name, build_number, target_repo,
                      status="released", copy=False):
        """Promote a build to a target repository."""
        r = self.session.post(
            f"{self.base_url}/api/build/promote/{build_name}/{build_number}",
            json={
                "status": status, "targetRepo": target_repo,
                "copy": copy, "artifacts": True, "dependencies": False
            }
        )
        return r.json()
```

### Step 3: Docker Registry Operations

**Configure Docker to use Artifactory:**
```bash
# Login to the Artifactory Docker registry.
# The registry hostname depends on how the platform is reached:
#   SaaS / subdomain method:      acme.jfrog.io/<repo-key>
#   repository-path method:       <host>/artifactory/api/docker/<repo-key>
#   port method (self-hosted):    <host>:<port>
# Only the first form is shown below. On self-hosted Artifactory WITHOUT a
# reverse proxy configured for the subdomain method, the short form does not
# resolve and you must use one of the other two.
docker login acme.jfrog.io

# Push image through Artifactory
docker tag myapp:latest acme.jfrog.io/docker-local/myapp:1.0.0
docker push acme.jfrog.io/docker-local/myapp:1.0.0

# Pull image through Artifactory (also caches remote images)
docker pull acme.jfrog.io/docker-remote/nginx:latest
```

> **`jf config add` does not log the Docker daemon in.** It configures the JFrog CLI's own credential store. Under OIDC (Option C) there is no long-lived password to feed `docker login` at all, which is the point of OIDC. Three working routes: run `jf docker push/pull`, which proxies the daemon using the CLI's configuration; or export the exchanged access token and pipe it, `echo "$JF_ACCESS_TOKEN" | docker login acme.jfrog.io -u <username> --password-stdin`; or let `jfrog/setup-jfrog-cli` export the token into the job and use the same pipe. Never put the token in the `docker login -p` argument, which lands it in argv and in shell history.

**Using JFrog CLI for Docker (adds build info):**
```bash
# Push with build info collection
jf docker push acme.jfrog.io/docker-local/myapp:1.0.0 \
  --build-name=myapp-build --build-number=42

# Pull with build info collection
jf docker pull acme.jfrog.io/docker-remote/nginx:latest \
  --build-name=myapp-build --build-number=42
```

### Step 4: Build Info and Promotion

**Publish build info from CI pipeline:**
```bash
# Collect environment variables
jf rt build-collect-env myapp-build 42

# Upload artifacts with build info
jf rt upload "target/*.jar" libs-release-local/com/acme/myapp/1.0.0/ \
  --build-name=myapp-build --build-number=42

# Publish build info
jf rt build-publish myapp-build 42

# Promote build from staging to release
jf rt build-promote myapp-build 42 libs-release-local \
  --status="released" --copy
```

**Promotion pipeline pattern:**
```
[Build] -> libs-snapshot-local (dev)
        -> libs-staging-local (QA approved)
        -> libs-release-local (production ready)
```

### Step 5: Xray Security Scanning

**Using JFrog CLI for scanning:**
```bash
# Audit current project dependencies
jf audit --watches "prod-security-watch"

# Scan a specific Docker image
jf docker scan acme.jfrog.io/docker-local/myapp:1.0.0

# Real CI gate on the SOURCE tree: the policy comes from an Xray watch,
# not from --min-severity
jf audit --watches=prod-security-watch --fail=true   # exit code 3 when a Fail Build rule matches

# Real CI gate on the BUILD you just published (this is the one most pipelines want)
jf build-scan my-build 42 --fail --vuln

# --min-severity only filters what is DISPLAYED. Without --watches, --project or
# --repo-path no policy violations are evaluated at all, so this gates nothing:
jf audit --min-severity=High

# Generate SBOM in CycloneDX (with VEX data from Xray 3.67+)
jf scan --format=cyclonedx --sbom "build/libs/*.jar" > sbom.cdx.json
```

> `--fail` already defaults to true, so passing it changes nothing on its own. The flag that makes a gate real is `--watches`, `--project`, or `--repo-path`, and **those three are mutually exclusive**: `--watches` is documented as "Incompatible with --project and --repo-path", and each of the other two is accepted "only if" the other two are absent. Passing two is a hard CLI error, not a narrowing.
>
> **`jf audit` and `jf build-scan` gate different objects.** `audit` resolves the source tree's declared dependencies. `build-scan <name> <number>` scans the build info and the artifacts the pipeline actually published, which is what catches a CVE that lives in a shaded, vendored or base-image layer and never appears in your manifest. Publish build info (Step 4), then gate with `build-scan`. Its flags are `--fail`, `--vuln`, `--violations`, `--rescan`, `--trigger-scan-retries`, `--format`, `--project`.
>
> **What silently turns a gate into a no-op**, in rough order of how often it bites:
> 1. The target repository is not indexed by Xray. Nothing is indexed by default; see the indexing note below. An unindexed repo yields zero violations and a green build.
> 2. The watch exists but is not active, or its policy has no rule with `fail_build` set. `block_download` is a different action and does not fail a build.
> 3. The watch's resources do not actually include the repo or build being scanned.
> 4. An ignore rule or waiver already suppresses the violation.
> 5. `--format=cyclonedx` is set: the CLI's own flag help warns that the CycloneDX format carries vulnerabilities, not violations, so policy context is lost.
> 6. `--vuln` is set, which reports all vulnerabilities regardless of policy.
> 7. SAST, IaC and contextual analysis are JFrog Advanced Security entitlements, so a structurally correct gate can still be scanning less than you assume.
> 8. Exit code 3 is swallowed by `continue-on-error`, `|| true`, or a pipe. Check that the step actually fails.
>
> **Xray indexing is a prerequisite, not a troubleshooting step.** On a new repository Xray indexes nothing until you add it under Indexed Resources, and only supported package types are indexed at all. Verify the repo is indexed AND that the specific artifact has been scanned (`POST /xray/api/v1/artifact/status`, or `scan-status` in the bundled `xray_client.py`) before you treat an empty result as clean. Note the asymmetry: `jf audit` needs no indexing because it reads your manifests, while `jf docker scan`, `jf build-scan`, watches and the summary API all do.
> CycloneDX is the only SBOM format JFrog CLI emits. There is no `jf scan --format=spdx`; the CLI rejects it, and its own help for the enrich command says "Input must be CycloneDX JSON; SPDX or other formats are not accepted." SPDX comes only from the Xray UI (Scans List, then More Options, then Export Scan Data) or from `POST /xray/api/v2/component/exportDetails` with `"spdx": true` **plus** `"spdx_format"` (`json` or `tag-value`), which is required whenever `spdx` is selected; the call returns 400 if you send no content selector at all.
> `jf docker scan` accepts the SAME `--format` values as `jf scan` (table, json, simple-json, sarif, cyclonedx) because both commands share one flag definition, so you can emit an image SBOM directly from `jf docker scan --format=cyclonedx`.
> `--sbom` is a BOOLEAN display toggle, not an input selector: it makes the output list every SBOM component rather than only the affected ones, and it is ignored unless `--format` is `table` or `cyclonedx`. The scan target is still the positional path argument.

CBOM here means **Cryptography** Bill of Materials, not a secrets report. With JFrog Advanced Security, the CBOM option enriches a CycloneDX SBOM with the cryptographic assets that secrets scanning found, embedding each as a `cryptographic-asset` component (certificates, API and secret keys, generic secrets). It is an enrichment of the SBOM, not an export of the secrets findings. Xray also ingests external SPDX and CycloneDX SBOMs (including VEX contextual analysis) for vetting third-party artifacts.

**Frogbot for pull-request scanning:**
```yaml
# .github/workflows/frogbot-scan-pr.yml
- uses: jfrog/frogbot@v3
  env:
    JF_URL: ${{ secrets.JF_URL }}
    JF_ACCESS_TOKEN: ${{ secrets.JF_ACCESS_TOKEN }}
    JF_GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
Frogbot scans PRs and comments on findings, and can open fix PRs. Frogbot itself is open source and free to run, but the scanners are not uniform: SCA needs a JFrog Platform connection, while SAST, IaC and contextual analysis are JFrog Advanced Security features. Confirm which of them your subscription actually entitles you to before promising a PR gate. It is still a good first step for an Israeli OSS project. Pin `@v3`: V3 scans statically without executing your package managers, so it still returns results when the build fails, and it auto-detects nested and multi-package repos. V2 is in sunset mode (critical bug and security fixes only, no new features).

### Step 5b: AI / ML Model Management (JFrog ML + AI Catalog)

JFrog ML (March 2025, from the Qwak acquisition) and the AI Catalog (September 2025) extend Artifactory and Xray to ML models. The **Machine Learning** repository type stores Hugging Face models alongside PyTorch, ONNX, .pkl, .joblib, .pth, and .cbm files in one format-agnostic repo, with FrogML SDK support. 7.111.1 is not a minimum: Hugging Face repositories are supported from Artifactory 7.77, and 7.111.1 is the version from which all new local and remote Hugging Face repositories use the Machine Learning layout **by default**. Xet protocol support is documented for Hugging Face repositories specifically.

```bash
# Configure an ML repo (admin UI or REST):
# Administration > Repositories > Add Repository > Local > Machine Learning

# Upload a model artifact with build info
jf rt upload "model.onnx" ml-local/myapp/v1.0.0/ \
  --build-name=ml-build --build-number=42

# Scan model files for embedded code-execution payloads (needs JFrog Advanced Security)
jf malicious-scan --working-dirs=./models

# Binary-scan a model artifact you already have on disk
jf scan ./model.onnx --format=sarif
```

> Model scanning is not the Docker path. `jf docker scan` resolves images through the local Docker daemon, so pointing it at an ML repository path fails. `jf malicious-scan` (beta) targets the pickle-deserialization attack class that container scanning does not cover.

The **AI Catalog** lets central platform teams curate access to OpenAI, Anthropic, NVIDIA NIM (including Nemotron open-weight models), and Hugging Face models behind one governance layer: scanning, lineage, model cards, and one-click deployment.

### Step 6: AQL (Artifactory Query Language) Patterns

**Common AQL queries for artifact management:**

```
// Find artifacts created in last 7 days
items.find({"created": {"$last": "7d"}, "repo": "libs-release-local"})

// Find Docker images by name
items.find({
    "repo": "docker-local",
    "path": {"$match": "myapp/*"},
    "name": "manifest.json"
}).include("repo", "path", "name", "created", "size")

// Find artifacts larger than 100MB
items.find({
    "size": {"$gt": 104857600},
    "repo": {"$match": "libs-*-local"}
}).sort({"$desc": ["size"]})

// Find unused artifacts (not downloaded in 90 days)
items.find({
    "stat.downloaded": {"$before": "90d"},
    "repo": "libs-release-local"
})

// Find artifacts by property
items.find({
    "@build.name": "myapp-build",
    "@build.number": "42"
})
```

## Examples

### Example 1: Set Up Maven Repository
User says: "Set up a Maven repository structure in Artifactory"
Result: Create local repo (libs-release-local, libs-snapshot-local), remote repo (jcenter-remote pointing to Maven Central), virtual repo (libs aggregating local + remote), configure resolution and deployment.

### Example 2: Docker CI/CD Pipeline
User says: "Integrate Artifactory as Docker registry in our CI pipeline"
Result: Configure Docker virtual repository, set up docker login in CI, push images with build info using jf docker push, scan with Xray, promote from staging to production.

### Example 3: Security Gate
User says: "Block deployment of artifacts with critical CVEs"
Result: Create Xray security policy blocking critical CVEs, create watch on production repositories, configure fail_build action for CI integration, set up violation notifications.

### Example 4: Storage Cleanup
User says: "Clean up old artifacts to free Artifactory storage"
Result: Use AQL to find artifacts not downloaded in 90+ days, identify snapshot artifacts older than 30 days, create cleanup script with dry-run mode, schedule regular cleanup.

## Bundled Resources

### Scripts
- `scripts/artifactory_client.py`: JFrog Artifactory REST API client covering health checks, repository listing and creation, artifact upload / download / delete, AQL search, property management, build info retrieval, and build promotion. Reads the token from `JFROG_ACCESS_TOKEN` only, never from argv. Promotion copies by default; `--move` is opt-in. Requires `requests` (`pip3 install requests`). Run: `python3 scripts/artifactory_client.py --help`
- `scripts/xray_client.py`: JFrog Xray REST API client. `summary` READS an existing scan result and does not scan; `trigger-scan` starts one and takes a component ID (`docker://image:tag`), not a repo path; `scan-status` tells "scanned and clean" apart from "never scanned", which an empty summary cannot. Also covers policy and watch management, violation search and report generation. Reads the token from `JFROG_ACCESS_TOKEN` only, never from argv. Requires `requests` (`pip3 install requests`). Run: `python3 scripts/xray_client.py --help`

### References
- `references/domain-checklist.md`: The coverage contract for this skill, including a dated record of what it deliberately does not cover yet and why. Read it before assuming a topic is handled.
- `references/api-reference.md`: Quick reference for Artifactory and Xray REST API endpoints organized by category (system, repositories, artifacts, search, properties, build info, scanning, policies, violations), JFrog CLI command cheatsheet, AQL query patterns, repository type explanations, and standard repository layout conventions. Consult when constructing API calls, writing AQL queries, or setting up repository structures.

## Gotchas

- **JFrog Pipelines reached end of life on May 1, 2026.** New customers cannot provision Pipelines and existing customers must already be migrated. JFrog recommends GitHub Actions, GitLab CI, Jenkins, or Azure DevOps with the `jfrog/setup-jfrog-cli` action/integration. If an Israeli team is still on Pipelines, treat the migration as overdue: no feature updates and no support are available.
- **The legacy Hugging Face migration deadline passed in June 2026.** Any Hugging Face repository still on the legacy layout, which is every one created before Artifactory 7.111.1 made the new layout the default, that has not been moved to the "Machine Learning" layout is now running unsupported, and full functionality is no longer guaranteed. Treat an unmigrated repo as an incident, not a backlog item. Migration is effectively one-way (the `restore_layout` API deletes packages added after the upgrade), federated repos cannot mix layouts, and Hugging Face Hub rate limits spike during cache-warming, so plan the cutover rather than running it ad hoc.
- **API keys reached end of life Q4 2024.** Legacy keys still work on older instances but new keys cannot be generated. Migrate any `X-JFrog-Art-Api` usage to access tokens or reference tokens (both sent as `Authorization: Bearer ...`).
- **OIDC is now the JFrog-recommended GitHub Actions auth method.** Requires JFrog CLI 2.75.0+ and the workflow needs `permissions: id-token: write`. Long-lived access tokens stored in GitHub secrets are still supported but discouraged for new pipelines.
- **In-country JFrog Cloud regions: ask, do not assume.** JFrog no longer publishes a public cloud-region list. The page this skill previously cited now renders empty, `jfrog.com/cloud-service-providers-and-regions/` returns 404, and the hosting-models region page 301s to a self-managed architecture page with no regions on it (all three re-checked 2026-09-02). We therefore cannot confirm from any official source which, if any, Israeli regions JFrog SaaS offers. **Do not tell an Israeli buyer that data residency is available on JFrog SaaS without confirming it with JFrog directly.** The structural point still holds and is worth raising in procurement: the region is fixed when the subscription is created and cannot be changed later without a migration, so settle residency before onboarding rather than after.
- **Cloud tier pricing transparency varies.** JFrog publishes Pro at about $150/month and Enterprise X at about $950/month for SaaS, with Enterprise+ on quote. Self-managed pricing is not published at all; the figures that circulate for it come from third-party trackers we could not verify, so do not quote one. Israeli buyers should get current pricing directly from JFrog Israel before architecting.
- **JFrog is an Israeli company**, founded and headquartered in Netanya (NASDAQ: FROG) with a substantial R&D presence in Israel. For an Israeli team that means local-timezone enterprise support, a local sales and solution-architect org, and Hebrew-speaking SEs. That is a genuine procurement argument on its own. It does NOT extend to data residency: see the region bullet above, which we could not confirm from any official source.
- **A license violation is not always your policy talking.** Before treating one as a real blocker, check which policy the watch actually inherited: a permissive internal policy can still surface violations from a banned-license list that came in with a parent template you did not author. We have not verified how Xray models license identity internally, so read the policy rather than assuming the mechanism.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Artifactory REST API | https://docs.jfrog.com/artifactory/reference | Endpoints, query syntax, AQL. The machine-readable index is https://docs.jfrog.com/artifactory/llms.txt |
| Xray Documentation | https://jfrog.com/xray/ | Vulnerability scanning, license compliance, policies, SBOM/VEX |
| JFrog CLI Releases | https://github.com/jfrog/jfrog-cli/releases | Latest CLI version (2.122.0 as of August 2026), changelog |
| JFrog Docker Registry | https://jfrog.com/help/r/jfrog-artifactory-documentation/docker-repositories | Docker image management, Docker Hub proxy |
| JFrog ML | https://jfrog.com/jfrog-ml/ | MLOps platform (from Qwak acquisition), model registry, FrogML SDK |
| JFrog AI Catalog | https://jfrog.com/press-room/jfrog-launches-ai-catalog-to-secure-and-govern-ai-model-delivery/ | Governance for OpenAI, Anthropic, NVIDIA NIM, Hugging Face |
| Machine Learning Repositories | https://jfrog.com/help/r/jfrog-artifactory-documentation/log-hugging-face-models | New ML repo layout, June 2026 HF migration |
| JFrog Curation | https://jfrog.com/curation/ | OSS package vetting, Compliant Version Selection, and MCP tools for Curation waiver management |
| Frogbot | https://github.com/jfrog/frogbot | Free PR-scanning bot, SCA + SAST + IaC. V3 is current, V2 is sunset |
| OIDC + GitHub Actions | https://jfrog.com/help/r/jfrog-platform-administration-documentation/configure-jfrog-platform-oidc-integration-with-github-actions | Recommended auth for CI, requires CLI 2.75.0+ |
| Pipelines End of Life | https://docs.jfrog.com/releases/docs/pipeline-deprecation-end-of-life | May 1 2026 EOL, migration guidance |
| JFrog Cloud hosting models | https://docs.jfrog.com/installation/docs/system-architecture | Hosting model overview. Note: the former public region list is no longer published, so confirm region availability with JFrog directly |
| Xray SBOM Export API | https://docs.jfrog.com/security/reference/export-component-details-v1-deprecated_components-v2-openapi | POST /xray/api/v2/component/exportDetails, the only programmatic SPDX path |

## Troubleshooting

### Error: "401 Unauthorized" on API calls
Cause: Invalid or expired access token, or insufficient permissions
Solution: Generate a new access token in JFrog UI (Administration then Identity and Access then Access Tokens). Verify the token has the required permissions for the operation. API keys are being deprecated -- prefer access tokens.

### Error: "Docker push fails with unknown blob"
Cause: Docker client layer push failed or network interruption
Solution: Retry the push. If persistent, check Artifactory storage backend health. Ensure the Docker repository accepts the image architecture (linux/amd64 vs arm64). Check max upload size in Artifactory settings.

### Error: "Xray scan shows no results"
Cause: Xray indexing not enabled for the repository, or index not yet complete
Solution: Verify Xray is configured to index the target repository (Administration then Xray then Indexed Resources). New repositories need to be explicitly added. Initial indexing of large repositories may take hours.
