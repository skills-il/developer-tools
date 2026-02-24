# JFrog REST API Quick Reference

## Authentication Methods

| Method | Header | Notes |
|--------|--------|-------|
| Access Token (recommended) | Authorization: Bearer TOKEN | Platform-wide, scoped |
| API Key (deprecated) | X-JFrog-Art-Api: KEY | Being phased out |
| Basic Auth | Authorization: Basic base64(user:pass) | Least preferred |

## Artifactory API Endpoints

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/system/ping | Health check |
| GET | /api/system/version | Version info |
| GET | /api/storageinfo | Storage summary |

### Repositories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/repositories | List all repos |
| GET | /api/repositories?type=local | Filter by type |
| PUT | /api/repositories/{key} | Create/update repo |
| DELETE | /api/repositories/{key} | Delete repo |

### Artifacts
| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | /{repo}/{path} | Deploy artifact |
| GET | /{repo}/{path} | Download artifact |
| DELETE | /{repo}/{path} | Delete artifact |
| POST | /api/copy/{src}?to=/{dest} | Copy artifact |
| POST | /api/move/{src}?to=/{dest} | Move artifact |

### Search
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/search/artifact?name=X | Quick search |
| GET | /api/search/gavc?g=X&a=Y&v=Z | Maven GAVC search |
| POST | /api/search/aql | AQL query |
| GET | /api/search/dates?dateFields=created&from=X | Date search |

### Properties
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/storage/{repo}/{path}?properties | Get properties |
| PUT | /api/storage/{repo}/{path}?properties=k=v | Set properties |
| DELETE | /api/storage/{repo}/{path}?properties=k | Delete property |

### Build Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | /api/build | Publish build info |
| GET | /api/build/{name} | List build runs |
| GET | /api/build/{name}/{number} | Get build details |
| POST | /api/build/promote/{name}/{number} | Promote build |

## Xray API Endpoints

### Scanning
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/scanArtifact | Scan artifact |
| GET | /api/v1/scan/status/{id} | Scan status |
| POST | /api/v2/summary/artifact | Vulnerability summary |

### Policies and Watches
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v2/policies | Create policy |
| GET | /api/v2/policies | List policies |
| POST | /api/v2/watches | Create watch |
| GET | /api/v2/watches | List watches |

### Violations and Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/violations | Search violations |
| POST | /api/v1/reports/vulnerabilities | Generate report |
| GET | /api/v1/reports/{id} | Get report |

## JFrog CLI (jf) Quick Reference

### Setup
```bash
jf config add SERVER --url=URL --access-token=TOKEN --interactive=false
jf rt ping
```

### Artifacts
```bash
jf rt upload "*.jar" repo-local/path/
jf rt download "repo-local/path/*.jar" ./local/
jf rt search "repo-local/path/"
jf rt delete "repo-local/path/old-*.jar"
```

### Docker
```bash
jf docker push server.jfrog.io/docker-local/image:tag --build-name=X --build-number=Y
jf docker pull server.jfrog.io/docker-remote/image:tag
jf docker scan server.jfrog.io/docker-local/image:tag
```

### Build
```bash
jf rt build-collect-env BUILD_NAME BUILD_NUMBER
jf rt upload "*.jar" repo/ --build-name=X --build-number=Y
jf rt build-publish BUILD_NAME BUILD_NUMBER
jf rt build-promote BUILD_NAME BUILD_NUMBER target-repo --status=released
```

### Security
```bash
jf audit
jf audit --fail --min-severity=High
jf xr scan path/to/artifact
```

## AQL Query Patterns

```
# Find by name
items.find({"name": {"$match": "*.jar"}})

# Find in repo
items.find({"repo": "libs-release-local"})

# Find recent
items.find({"created": {"$last": "7d"}})

# Find large files
items.find({"size": {"$gt": 104857600}})

# Find by property
items.find({"@build.name": "myapp"})

# Combine conditions
items.find({
    "$and": [
        {"repo": "libs-release-local"},
        {"created": {"$last": "30d"}},
        {"name": {"$match": "*.jar"}}
    ]
}).include("name", "repo", "path", "size", "created").sort({"$desc": ["created"]}).limit(50)
```

## Repository Types

| Type | Purpose | Example |
|------|---------|---------|
| local | Store your artifacts | libs-release-local |
| remote | Proxy external repos | maven-central-remote |
| virtual | Aggregate repos | libs (combines local + remote) |
| federated | Multi-site sync | libs-federated |

## Common Repository Layout

```
libs-snapshot-local     -> Development builds
libs-staging-local      -> QA-approved builds
libs-release-local      -> Production releases
docker-local            -> Docker images (internal)
docker-remote           -> Docker Hub proxy
docker                  -> Virtual (aggregates local + remote)
npm-local               -> Internal npm packages
npm-remote              -> npmjs.org proxy
```
