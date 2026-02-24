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
allowed-tools: 'Bash(curl:*) Bash(jf:*) Bash(docker:*) Bash(python:*)'
compatibility: >-
  Requires network access to JFrog instance (SaaS or self-hosted). JFrog CLI
  (jf) recommended.
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    - jfrog
    - artifactory
    - xray
    - devops
    - docker
    - security
    - artifacts
  display_name:
    he: JFrog DevOps
    en: Jfrog Devops
  display_description:
    he: ניהול חבילות ב-Artifactory וסריקות אבטחה ב-Xray
    en: >-
      Manage JFrog Artifactory repositories, artifacts, Docker registry, build
      info, and Xray security scanning for DevOps workflows. Use when user asks
      about JFrog, Artifactory, Xray, artifact management, "deploy artifact",
      Docker registry with Artifactory, build promotion, vulnerability scanning
      with Xray, or DevOps artifact pipeline. Covers REST API operations, JFrog
      CLI usage, Docker registry configuration, and security scanning patterns.
      Do NOT use for general Docker or CI/CD questions unrelated to JFrog.
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
| Cleanup old artifacts | Artifactory | AQL + delete or retention policies | Yes (admin) |

### Step 2: Configure Authentication

**Option A: JFrog CLI (recommended):**
```bash
# Configure JFrog CLI with access token (recommended)
jf config add my-server \
  --url="https://mycompany.jfrog.io" \
  --access-token="YOUR_ACCESS_TOKEN" \
  --interactive=false

# Verify connection
jf rt ping
```

**Option B: REST API with curl:**
```bash
# Using access token (recommended)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "https://mycompany.jfrog.io/artifactory/api/system/ping"

# Using API key
curl -H "X-JFrog-Art-Api: YOUR_API_KEY" \
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
# Login to Artifactory Docker registry
docker login mycompany.jfrog.io

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
  --build-name=myapp-build --build-number=42

# Pull with build info collection
jf docker pull mycompany.jfrog.io/docker-remote/nginx:latest \
  --build-name=myapp-build --build-number=42
```

### Step 4: Build Info and Promotion

**Publish build info from CI pipeline:**
```bash
# Collect environment variables
jf rt build-collect-env myapp-build 42

# Upload artifacts with build info
jf rt upload "target/*.jar" libs-release-local/com/mycompany/myapp/1.0.0/ \
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
jf docker scan mycompany.jfrog.io/docker-local/myapp:1.0.0

# Scan with fail threshold (for CI)
jf audit --fail --min-severity=High
```

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
- `scripts/artifactory_client.py` — Full-featured JFrog Artifactory REST API client supporting health checks, repository listing/creation, artifact upload/download/delete, AQL search, property management, build info retrieval, and build promotion. Authenticates via access token (CLI arg or JFROG_ACCESS_TOKEN env var). Run: `python scripts/artifactory_client.py --help`
- `scripts/xray_client.py` — JFrog Xray REST API client for vulnerability scanning, security policy and watch management, violation search, and vulnerability report generation. Use to scan artifacts for CVEs, create security gates that block critical vulnerabilities, and generate compliance reports. Run: `python scripts/xray_client.py --help`

### References
- `references/api-reference.md` — Quick reference for Artifactory and Xray REST API endpoints organized by category (system, repositories, artifacts, search, properties, build info, scanning, policies, violations), JFrog CLI command cheatsheet, AQL query patterns, repository type explanations, and standard repository layout conventions. Consult when constructing API calls, writing AQL queries, or setting up repository structures.

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
