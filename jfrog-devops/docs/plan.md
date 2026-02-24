# JFrog DevOps Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a skill for working with JFrog Artifactory and the JFrog Platform for DevOps workflows — artifact management, Docker registry operations, build info publishing, and Xray security scanning.

**Architecture:** Domain-Specific Intelligence skill. Embeds knowledge of JFrog REST APIs, Artifactory repository management, Docker registry operations, build pipelines, and Xray vulnerability scanning workflows.

**Tech Stack:** SKILL.md, JFrog REST API reference, CLI examples, security scanning patterns.

---

## Research

### JFrog Platform Overview
- **JFrog Artifactory:** Universal artifact repository manager — supports 30+ package types
- **JFrog Xray:** Universal security scanning — CVE detection, license compliance, malware detection
- **JFrog Pipelines:** CI/CD automation platform
- **JFrog Distribution:** Release bundle management and global distribution
- **Founded:** 2008 in Netanya, Israel — one of Israel's major DevOps companies
- **Deployment:** SaaS (cloud), Self-hosted, Hybrid

### JFrog REST API — Artifactory Endpoints
- **Base URL:** `https://{server}/artifactory/api/`
- **Authentication:** API key, access token (recommended), or basic auth
- **Key endpoint groups:**

**System & Configuration:**
- `GET /api/system/ping` — Health check
- `GET /api/system/version` — Version info
- `GET /api/storageinfo` — Storage summary

**Repository Management:**
- `GET /api/repositories` — List all repositories
- `PUT /api/repositories/{repoKey}` — Create/update repository
- `DELETE /api/repositories/{repoKey}` — Delete repository
- Repository types: local, remote, virtual, federated

**Artifact Operations:**
- `PUT /{repoKey}/{path}` — Deploy artifact
- `GET /{repoKey}/{path}` — Download artifact
- `DELETE /{repoKey}/{path}` — Delete artifact
- `POST /api/copy/{srcRepo}/{srcPath}?to=/{destRepo}/{destPath}` — Copy artifact
- `POST /api/move/{srcRepo}/{srcPath}?to=/{destRepo}/{destPath}` — Move artifact

**Search:**
- `GET /api/search/artifact?name={name}` — Quick search by name
- `GET /api/search/gavc?g={group}&a={artifact}&v={version}` — GAVC search (Maven)
- `POST /api/search/aql` — Artifactory Query Language (most powerful)
- `GET /api/search/dates?dateFields=created&from={timestamp}` — Search by date

**Properties & Metadata:**
- `PUT /api/storage/{repoKey}/{path}?properties=key=value` — Set properties
- `GET /api/storage/{repoKey}/{path}?properties` — Get properties
- `DELETE /api/storage/{repoKey}/{path}?properties=key` — Delete properties

**Build Info:**
- `PUT /api/build` — Publish build info
- `GET /api/build/{buildName}` — Get build runs
- `GET /api/build/{buildName}/{buildNumber}` — Get specific build info
- `POST /api/build/promote/{buildName}/{buildNumber}` — Promote build

### JFrog REST API — Xray Endpoints
- **Base URL:** `https://{server}/xray/api/`
- **Key endpoints:**

**Scanning:**
- `POST /api/v1/scanArtifact` — Scan a specific artifact
- `GET /api/v1/scan/status/{scan_id}` — Check scan status
- `POST /api/v2/summary/artifact` — Get vulnerability summary for an artifact

**Watches & Policies:**
- `POST /api/v2/watches` — Create a watch (monitoring rule)
- `GET /api/v2/watches` — List watches
- `POST /api/v2/policies` — Create security/license policy
- `GET /api/v2/policies` — List policies

**Violations:**
- `POST /api/v1/violations` — Search violations
- `GET /api/v1/violations/{violation_id}` — Get violation details

**Reports:**
- `POST /api/v1/reports/vulnerabilities` — Generate vulnerability report
- `GET /api/v1/reports/{report_id}` — Get report status/results

### Docker Registry Operations
- JFrog Artifactory acts as a Docker V2 registry
- **Docker endpoints:** Standard Docker registry API v2
- `GET /v2/_catalog` — List repositories
- `GET /v2/{name}/tags/list` — List tags for an image
- `GET /v2/{name}/manifests/{reference}` — Get image manifest
- **Configuration:** Docker repository (local, remote for proxy, virtual for aggregation)
- **Login:** `docker login {server}.jfrog.io` with API key or access token

### JFrog CLI (jf)
- Modern CLI tool replacing `jfrog` command
- Key commands:
  - `jf rt upload` — Upload artifacts
  - `jf rt download` — Download artifacts
  - `jf rt search` — Search artifacts
  - `jf docker push/pull` — Docker operations through Artifactory
  - `jf rt build-publish` — Publish build info
  - `jf xr scan` — Scan for vulnerabilities
  - `jf audit` — Audit project dependencies

### Use Cases
1. **Artifact management** — Upload, download, search, and organize artifacts in Artifactory
2. **Docker registry** — Push/pull Docker images through Artifactory as a registry
3. **Build info** — Publish and manage build metadata for traceability
4. **Security scanning** — Scan artifacts for CVEs and license violations with Xray
5. **Cleanup and retention** — Manage storage with automated cleanup policies

---

## Build Steps

### Task 1: Create SKILL.md

```markdown
---
name: jfrog-devops
description: >-
  Manage JFrog Artifactory repositories, artifacts, Docker registry, build info,
  and Xray security scanning for DevOps workflows. Use when user asks about
  JFrog, Artifactory, Xray, artifact management, "deploy artifact", Docker
  registry with Artifactory, build promotion, vulnerability scanning with Xray,
  or DevOps artifact pipeline. Covers REST API operations, JFrog CLI usage,
  Docker registry configuration, and security scanning patterns. Do NOT use for
  general Docker or CI/CD questions unrelated to JFrog.
license: MIT
allowed-tools: "Bash(curl:*) Bash(jf:*) Bash(docker:*) Bash(python:*)"
compatibility: "Requires network access to JFrog instance (SaaS or self-hosted). JFrog CLI (jf) recommended."
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags: [jfrog, artifactory, xray, devops, docker, security, artifacts]
---

# JFrog DevOps

## Instructions

### Step 1: Identify the DevOps Operation
| Operation | JFrog Tool | API/CLI | Auth Required |
|-----------|-----------|---------|---------------|
| Upload/deploy artifact | Artifactory | `PUT /{repo}/{path}` or `jf rt upload` | Yes |
| Download artifact | Artifactory | `GET /{repo}/{path}` or `jf rt download` | Yes (unless anonymous) |
| Search artifacts | Artifactory | AQL or `jf rt search` | Yes |
| Docker push/pull | Artifactory | Docker API or `jf docker` | Yes |
| Publish build info | Artifactory | `PUT /api/build` or `jf rt build-publish` | Yes |
| Promote build | Artifactory | `POST /api/build/promote` | Yes (admin) |
| Scan for CVEs | Xray | `POST /api/v1/scanArtifact` or `jf xr scan` | Yes |
| Create watch/policy | Xray | `POST /api/v2/watches` | Yes (admin) |
| Generate report | Xray | `POST /api/v1/reports/vulnerabilities` | Yes |
| Cleanup old artifacts | Artifactory | AQL + delete or retention policies | Yes (admin) |

### Step 2: Configure Authentication

**Option A: JFrog CLI (recommended):**
```bash
# Configure JFrog CLI with access token (recommended)
jf config add my-server \
  --url="https://mycompany.jfrog.io" \
  --access-token="<ACCESS_TOKEN>" \
  --interactive=false

# Verify connection
jf rt ping
```

**Option B: REST API with curl:**
```bash
# Using access token (recommended)
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "https://mycompany.jfrog.io/artifactory/api/system/ping"

# Using API key
curl -H "X-JFrog-Art-Api: <API_KEY>" \
  "https://mycompany.jfrog.io/artifactory/api/system/ping"
```

**Option C: Python client:**
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
            params["type"] = repo_type  # local, remote, virtual, federated
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
        r = self.session.get(
            f"{self.base_url}/api/build/{build_name}/{build_number}"
        )
        return r.json()

    def promote_build(self, build_name, build_number, target_repo,
                      status="released", copy=False):
        """Promote a build to a target repository."""
        r = self.session.post(
            f"{self.base_url}/api/build/promote/{build_name}/{build_number}",
            json={
                "status": status,
                "targetRepo": target_repo,
                "copy": copy,
                "artifacts": True,
                "dependencies": False
            }
        )
        return r.json()
```

### Step 3: Docker Registry Operations

**Configure Docker to use Artifactory:**
```bash
# Login to Artifactory Docker registry
docker login mycompany.jfrog.io
# Username: <email or username>
# Password: <access token or API key>

# Push image through Artifactory
docker tag myapp:latest mycompany.jfrog.io/docker-local/myapp:1.0.0
docker push mycompany.jfrog.io/docker-local/myapp:1.0.0

# Pull image through Artifactory (also caches remote images)
docker pull mycompany.jfrog.io/docker-remote/nginx:latest
```

**Using JFrog CLI for Docker (adds build info):**
```bash
# Push with build info collection
jf docker push mycompany.jfrog.io/docker-local/myapp:1.0.0 \
  --build-name=myapp-build \
  --build-number=42

# Pull with build info collection
jf docker pull mycompany.jfrog.io/docker-remote/nginx:latest \
  --build-name=myapp-build \
  --build-number=42
```

### Step 4: Build Info and Promotion

**Publish build info from CI pipeline:**
```bash
# Collect environment variables
jf rt build-collect-env myapp-build 42

# Upload artifacts with build info
jf rt upload "target/*.jar" libs-release-local/com/mycompany/myapp/1.0.0/ \
  --build-name=myapp-build \
  --build-number=42

# Publish build info
jf rt build-publish myapp-build 42

# Promote build from staging to release
jf rt build-promote myapp-build 42 libs-release-local \
  --status="released" \
  --copy
```

**Promotion pipeline pattern:**
```
[Build] -> libs-snapshot-local (dev)
        -> libs-staging-local (QA approved)
        -> libs-release-local (production ready)
```

### Step 5: Xray Security Scanning

**Scan artifacts for vulnerabilities:**
```python
class XrayClient:
    """Client for JFrog Xray REST API."""

    def __init__(self, base_url, access_token):
        self.base_url = base_url.rstrip('/').replace('/artifactory', '/xray')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })

    def get_artifact_summary(self, repo_path):
        """Get vulnerability summary for an artifact."""
        r = self.session.post(
            f"{self.base_url}/api/v2/summary/artifact",
            json={
                "paths": [repo_path]
            }
        )
        return r.json()

    def create_security_policy(self, name, rules):
        """Create a security policy with CVE severity rules.

        rules = [
            {"name": "critical", "severity": "Critical", "action": "block_download"},
            {"name": "high", "severity": "High", "action": "notify"}
        ]
        """
        policy_rules = []
        for rule in rules:
            policy_rules.append({
                "name": rule["name"],
                "criteria": {
                    "min_severity": rule["severity"]
                },
                "actions": {
                    "block_download": {
                        "active": rule["action"] == "block_download"
                    },
                    "notify_watch_recipients": {
                        "active": rule["action"] == "notify"
                    },
                    "fail_build": rule.get("fail_build", False)
                }
            })

        r = self.session.post(
            f"{self.base_url}/api/v2/policies",
            json={
                "name": name,
                "type": "security",
                "rules": policy_rules
            }
        )
        return r.json()

    def create_watch(self, name, repos, policy_name):
        """Create a watch to monitor repositories with a policy."""
        r = self.session.post(
            f"{self.base_url}/api/v2/watches",
            json={
                "general_data": {"name": name},
                "project_resources": {
                    "resources": [
                        {"type": "repository", "name": repo}
                        for repo in repos
                    ]
                },
                "assigned_policies": [
                    {"name": policy_name, "type": "security"}
                ]
            }
        )
        return r.json()

    def get_violations(self, watch_name=None, severity=None, limit=100):
        """Search for security violations."""
        filters = {"pagination": {"limit": limit, "order_by": "created"}}
        if watch_name:
            filters["filters"] = {"watch_name": watch_name}
        if severity:
            filters["filters"] = filters.get("filters", {})
            filters["filters"]["severity"] = severity

        r = self.session.post(
            f"{self.base_url}/api/v1/violations",
            json=filters
        )
        return r.json()

    def generate_vulnerability_report(self, repos, severity_filter="High"):
        """Generate a vulnerability report for repositories."""
        r = self.session.post(
            f"{self.base_url}/api/v1/reports/vulnerabilities",
            json={
                "name": f"vuln-report-{repos[0]}",
                "resources": {
                    "repositories": [
                        {"name": repo} for repo in repos
                    ]
                },
                "filters": {
                    "severity": [severity_filter, "Critical"]
                }
            }
        )
        return r.json()
```

**Using JFrog CLI for scanning:**
```bash
# Audit current project dependencies
jf audit --watches "prod-security-watch"

# Scan a specific Docker image
jf docker scan mycompany.jfrog.io/docker-local/myapp:1.0.0

# Scan with fail threshold (for CI)
jf audit --fail --min-severity=High
```

### Step 6: AQL (Artifactory Query Language) Patterns

**Common AQL queries for artifact management:**

```
// Find artifacts created in last 7 days
items.find({
    "created": {"$last": "7d"},
    "repo": "libs-release-local"
})

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
Result: Configure Docker virtual repository, set up `docker login` in CI, push images with build info using `jf docker push`, scan with Xray, promote from staging to production.

### Example 3: Security Gate
User says: "Block deployment of artifacts with critical CVEs"
Result: Create Xray security policy blocking critical CVEs, create watch on production repositories, configure fail_build action for CI integration, set up violation notifications.

### Example 4: Storage Cleanup
User says: "Clean up old artifacts to free Artifactory storage"
Result: Use AQL to find artifacts not downloaded in 90+ days, identify snapshot artifacts older than 30 days, create cleanup script with dry-run mode, schedule regular cleanup.

## Troubleshooting

### Error: "401 Unauthorized" on API calls
Cause: Invalid or expired access token, or insufficient permissions
Solution: Generate a new access token in JFrog UI (Administration > Identity and Access > Access Tokens). Verify the token has the required permissions for the operation. API keys are being deprecated — prefer access tokens.

### Error: "Docker push fails with 'unknown blob'"
Cause: Docker client layer push failed or network interruption
Solution: Retry the push. If persistent, check Artifactory storage backend health. Ensure the Docker repository accepts the image architecture (linux/amd64 vs arm64). Check max upload size in Artifactory settings.

### Error: "Xray scan shows no results"
Cause: Xray indexing not enabled for the repository, or index not yet complete
Solution: Verify Xray is configured to index the target repository (Administration > Xray > Indexed Resources). New repositories need to be explicitly added. Initial indexing of large repositories may take hours.
```
