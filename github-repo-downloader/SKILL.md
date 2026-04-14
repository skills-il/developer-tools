---
name: github-repo-downloader
description: "Download entire GitHub repositories or subdirectories using the GitHub REST API without authentication. Recursively fetches all files and directories while maintaining folder structure. Handles API rate limiting, HTTP errors, and empty directories. Supports any public GitHub repo. Use when: user provides a GitHub repo URL or path, wants to download/clone a repo locally, needs to scrape repo structure, or wants to package a skill/folder into a zip."
compatibility: "Any environment with Python 3.6+, urllib, json stdlib (no external dependencies). Tested with skills-il organization repos."
license: "EKACL-2.2 (Erez Kalman Attribution Copyleft License v2.2) — Free for non-commercial use; commercial use requires explicit license. All software using this Work must remain free forever, provide full source code (including connected services), and maintain attribution. All enhancements automatically assigned to copyright holder."
---

# GitHub Repository Recursive Download

## Overview

Download entire GitHub repositories, subdirectories, or specific folders using the GitHub REST API without requiring authentication or Git installation. The method recursively traverses directories, maintains folder structure, handles errors gracefully, and respects API rate limits.

**Use cases:**
- Download a public repo without `git clone`
- Scrape specific GitHub folders
- Package skills or documentation into zip files
- Mirror repo structure locally
- Automate repo downloads in sandboxed environments

## Core Method

Use GitHub's `/repos/{owner}/{repo}/contents/{path}` REST API endpoint to list directory contents, then recursively download files via their `download_url` field.

### API Endpoint

```
https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}?ref={BRANCH}
```

**Parameters:**
- `OWNER`: Repository owner (e.g., `skills-il`)
- `REPO`: Repository name (e.g., `tax-and-finance`)
- `PATH`: File/directory path relative to repo root (e.g., `israeli-tax-returns`)
- `BRANCH`: Git branch (default: `master`, `main`, or any branch name)

**Returns:** JSON array of items (files/dirs) OR single file object

### Response Structure

Each item in the JSON array contains:

```json
{
  "name": "filename.md",
  "path": "folder/filename.md",
  "type": "file|dir",
  "size": 1024,
  "download_url": "https://raw.githubusercontent.com/owner/repo/branch/path...",
  "url": "https://api.github.com/repos/.../contents/...",
  "sha": "commit-hash"
}
```

**Critical fields for download:**
- `type`: Determines action (`"file"` = download, `"dir"` = recurse)
- `download_url`: Raw GitHub content URL; only present for files
- `path`: Relative path for maintaining folder structure

## Implementation

### Complete Working Code

```python
import os
import json
import urllib.request
from urllib.error import HTTPError
import time

def fetch_github_repo(owner, repo, path, branch="master", work_dir="/tmp/repo"):
    """
    Recursively download GitHub repo/folder.
    
    Args:
        owner: GitHub owner (e.g., 'skills-il')
        repo: Repository name (e.g., 'tax-and-finance')
        path: Path within repo (e.g., 'israeli-tax-returns')
        branch: Git branch (default 'master')
        work_dir: Local output directory
    """
    os.makedirs(work_dir, exist_ok=True)
    
    def fetch_dir(rel_path, depth=0):
        if depth > 20:  # Prevent infinite recursion
            print(f"Max depth reached at {rel_path}")
            return
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{rel_path}?ref={branch}"
        
        try:
            req = urllib.request.Request(url)
            # Optional: Add auth header for higher rate limits
            # req.add_header('Authorization', f'token {GITHUB_TOKEN}')
            
            with urllib.request.urlopen(req) as resp:
                items = json.loads(resp.read())
        except HTTPError as e:
            print(f"HTTP {e.code} on {rel_path}: {e.reason}")
            return
        except Exception as e:
            print(f"Network error on {rel_path}: {e}")
            return
        
        # Validate response
        if isinstance(items, dict):
            if 'message' in items:
                print(f"API error on {rel_path}: {items['message']}")
                return
            items = [items]  # Single file response
        
        for item in items:
            filepath = item['path']
            item_type = item['type']
            local_path = os.path.join(work_dir, filepath)
            
            if item_type == 'file':
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                try:
                    download_url = item.get('download_url')
                    if not download_url:
                        print(f"⚠ No download_url for {filepath}")
                        continue
                    
                    with urllib.request.urlopen(download_url) as resp:
                        with open(local_path, 'wb') as f:
                            f.write(resp.read())
                    print(f"✓ {filepath}")
                except Exception as e:
                    print(f"✗ {filepath}: {e}")
            
            elif item_type == 'dir':
                os.makedirs(local_path, exist_ok=True)
                time.sleep(0.5)  # Rate limit throttle
                fetch_dir(filepath, depth + 1)
    
    fetch_dir(path)
    print(f"Complete. Files in: {work_dir}")

# Usage example
# fetch_github_repo("skills-il", "tax-and-finance", "israeli-tax-returns")
```

### Usage in Claude

Call directly in an artifact or bash script:

```python
fetch_github_repo("skills-il", "localization", "hebrew-document-generator", 
                  branch="master", work_dir="/tmp/skill_download")
```

After download, package into zip:

```bash
cd /tmp && zip -r skill.zip skill_download/hebrew-document-generator
```

## Rate Limiting

**Unauthenticated requests:** 60 requests/hour per IP
- 1 API call per file + 1 per directory = O(n+d) complexity
- Large repos (1000+ files) may hit limit

**Check rate limit headers in response:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1681234567  # Unix timestamp when limit resets
```

**Adaptive mitigation strategies:**

1. **Monitor remaining requests:**
   ```python
   resp = urllib.request.urlopen(url)
   remaining = int(resp.headers.get('X-RateLimit-Remaining', 60))
   if remaining < 10:  # Approaching limit
       time.sleep(2)   # Increase backoff
   ```

2. **Add time.sleep() between directory traversals:**
   ```python
   time.sleep(0.5-1)  # Between API calls to avoid hitting limit
   ```

3. **Retry on 403 with exponential backoff:**
   ```python
   import time
   retries = 3
   for attempt in range(retries):
       try:
           # API call
           break
       except HTTPError as e:
           if e.code == 403:
               wait = 2 ** attempt  # 1s, 2s, 4s
               print(f"Rate limited. Waiting {wait}s...")
               time.sleep(wait)
           else:
               raise
   ```

4. **Use authentication for higher limits:**
   ```python
   req.add_header('Authorization', f'token {GITHUB_TOKEN}')
   # 5000 req/hour instead of 60
   ```

5. **For very large repos (1000+ files):**
   - Use authentication (higher limit)
   - Batch downloads in phases
   - Run at off-peak times

## Error Handling

### HTTP Errors

| Code | Cause | Action |
|------|-------|--------|
| 403 Forbidden | Empty dirs, special dirs, or rate limit | Log and continue; if rate limit, wait and retry with exponential backoff (1s, 2s, 4s) |
| 404 Not Found | Invalid path | Skip (shouldn't happen in valid repos) |
| 500–599 | Server error | Retry or skip item |

**Rate Limit Detection:**
```python
try:
    with urllib.request.urlopen(url) as resp:
        remaining = int(resp.headers.get('X-RateLimit-Remaining', 60))
        if remaining < 10:
            print(f"Approaching rate limit: {remaining} requests remaining")
            time.sleep(2)  # Increase backoff
except HTTPError as e:
    if e.code == 403:
        reset_time = e.headers.get('X-RateLimit-Reset')
        print(f"Rate limit exceeded. Reset at: {reset_time}")
        # Wait until reset or use exponential backoff
```

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| 403 on empty dirs | GitHub API quirk for empty/special directories | Ignore; items still listed in parent directory—recursion continues normally |
| 403 rate limit | Exceeded 60 req/hour (unauthenticated) | Wait (check X-RateLimit-Reset header) OR add `time.sleep(0.5-1)` between API calls OR use authentication |
| 403 rate limit retry | Need to recover from exhausted limit | Use exponential backoff: sleep 1s, 2s, 4s before retrying |
| Missing `download_url` | Submodules or special files | Check `item['type']` == `'file'` before access |
| Infinite recursion | Circular symlinks (rare) | Add `depth` counter (max 20 in code above) |
| Binary corrupted | Text-mode file write | Use `'wb'` (binary), never `'w'` (text) |
| Large repo timeout | Too many API calls (1000+ files) | Use authentication, add sleep between calls, batch in phases |
| Encoding errors | Non-UTF8 files | Read as binary (`'rb'`), decode selectively |

## Directory Traversal Algorithm

```
1. Build API URL: api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}
2. Fetch JSON response (array of items)
3. For each item:
   a. If type == 'file':
      - Extract download_url
      - Create parent directories
      - Download to local_path (binary mode)
   b. If type == 'dir':
      - Create local directory
      - Recursive call with full relative path
4. Validate response (check for error messages)
5. Handle HTTP errors gracefully (log, continue)
```

**Key design:** Each recursive call passes the full `item['path']` (not just dir name), so local structure mirrors GitHub structure exactly.

## File Structure Preservation

Local directory structure is preserved by using `item['path']` directly:

```python
local_path = os.path.join(WORK_DIR, item['path'])
os.makedirs(os.path.dirname(local_path), exist_ok=True)
```

This ensures:
- Nested folders created automatically
- File names identical to GitHub
- No path collisions
- Structure valid for zipping into skills

## Authentication (Optional)

For higher rate limits or private repos:

```python
req = urllib.request.Request(url)
req.add_header('Authorization', f'token {GITHUB_TOKEN}')
```

**Token types:**
- **Personal Access Token (PAT):** `ghp_...` — 5000 req/hour
- **Fine-grained token:** Scoped permissions, safer
- **GitHub App:** Automation, 10,000+ req/hour

## Integration with Skill Packaging

After download, create a skill zip:

```bash
# Download
python3 -c "from script import fetch_github_repo; fetch_github_repo(...)"

# Package
cd /tmp && zip -r skill.zip repo_folder/

# Move to outputs
cp skill.zip /mnt/user-data/outputs/
```

## Limitations

- **Public repos only** (without authentication)
- **API rate limits** (60/hour unauthenticated)
- **No Git history** (just current state)
- **Binary files downloaded as-is** (no preprocessing)
- **GitHub size limits** (repos >1GB may timeout)

## When to Use This Skill

✅ Download public GitHub repos or folders  
✅ Clone without git in sandboxed environments  
✅ Scrape repo structure  
✅ Package skills/documentation  
✅ Automate repo backups  
✅ Extract specific subdirectories  

❌ Private repositories (use SSH/HTTPS with auth)  
❌ Large repos (>5000 files; consider filtering by path)  
❌ Real-time sync (static snapshot only)  
