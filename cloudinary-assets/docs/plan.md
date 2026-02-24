# Cloudinary Assets Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a skill for managing media assets through Cloudinary's REST API — uploading, transforming, optimizing, and delivering images and videos with Israeli-founded cloud media management.

**Architecture:** MCP Enhancement skill (Category 3). Guides integration with Cloudinary's Upload, Admin, and Transformation APIs for media lifecycle management.

**Tech Stack:** SKILL.md, references for Cloudinary REST API, transformation URL syntax, and optimization best practices.

---

## Research

### Cloudinary Platform
- **Founded:** 2012, Tel Aviv, Israel (Itai Lahan, Nadav Soferman, Tal Lev-Ami)
- **Users:** 1M+ developers, 10,000+ customers globally
- **Core service:** Cloud-based image and video management platform
- **API types:** Upload API, Admin API, URL-based transformations
- **SDKs:** Python, Node.js, Ruby, PHP, Java, .NET, Go, and more
- **Free tier:** 25 credits/month (~25K transformations or 25GB storage)

### Cloudinary REST API
- **Base URL:** `https://api.cloudinary.com/v1_1/{cloud_name}/`
- **Auth:** Basic auth with API Key + API Secret, or unsigned upload presets
- **Key Endpoints:**
  - `POST /image/upload` — Upload image
  - `POST /video/upload` — Upload video
  - `POST /raw/upload` — Upload non-media files
  - `GET /resources` — List assets (Admin API)
  - `DELETE /resources` — Delete assets (Admin API)
  - `GET /resources/{public_id}` — Get asset details
  - `POST /image/destroy` — Delete single image
- **Admin API Base:** `https://api.cloudinary.com/v1_1/{cloud_name}/resources/`
- **Rate limits:** 500 requests/hour (free), higher on paid plans

### Transformation URL Syntax
- **Pattern:** `https://res.cloudinary.com/{cloud_name}/image/upload/{transformations}/{public_id}.{format}`
- **Common transformations:**
  - `w_400,h_300,c_fill` — Resize to 400x300, fill crop
  - `w_800,q_auto,f_auto` — Width 800, auto quality, auto format
  - `e_blur:300` — Blur effect
  - `l_watermark,g_south_east` — Overlay watermark
  - `ar_16:9,c_fill` — Aspect ratio 16:9
  - `dpr_auto` — Auto device pixel ratio
  - `e_background_removal` — AI background removal

### Optimization Features
- **Auto format (f_auto):** Delivers WebP, AVIF, or JPEG-XL based on browser support
- **Auto quality (q_auto):** Perceptual quality optimization, reduces file size 40-80%
- **Responsive breakpoints:** Auto-generate srcset for responsive images
- **Lazy loading:** Placeholder + blur-up technique
- **CDN:** Global CDN with edge caching

### Use Cases
1. **Image upload** — Upload and store images with automatic optimization
2. **Image transformation** — Resize, crop, watermark, effects via URL
3. **Video management** — Upload, transcode, and stream video content
4. **Responsive delivery** — Generate responsive image sets for web
5. **Media optimization** — Auto-format, auto-quality for performance
6. **Asset management** — List, search, tag, and organize media library

---

## Build Steps

### Task 1: Create SKILL.md

**Files:**
- Create: `repos/developer-tools/cloudinary-assets/SKILL.md`

```markdown
---
name: cloudinary-assets
description: >-
  Manage media assets through Cloudinary's REST API — upload, transform,
  optimize, and deliver images and videos. Use when user asks about image
  upload, media optimization, image transformations, responsive images,
  video management, CDN delivery, or mentions Cloudinary specifically.
  Covers Upload API, Admin API, URL-based transformations, and delivery
  optimization. Israeli-founded platform (Tel Aviv, 2012). Do NOT use for
  non-Cloudinary media hosting or local image processing without cloud upload.
license: MIT
allowed-tools: "Bash(python:*) Bash(curl:*) WebFetch"
compatibility: "Requires Cloudinary account (free tier available). Needs CLOUDINARY_URL or API key/secret/cloud name environment variables."
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags: [cloudinary, media, images, video, cdn, optimization, israel]
---

# Cloudinary Assets

## Instructions

### Step 1: Verify Cloudinary Configuration
Check for Cloudinary credentials:

```python
import os

def get_cloudinary_config():
    """Get Cloudinary config from environment."""
    # Option 1: CLOUDINARY_URL (preferred)
    cloudinary_url = os.environ.get('CLOUDINARY_URL')
    if cloudinary_url:
        # Format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
        return {"url": cloudinary_url}

    # Option 2: Individual variables
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    if all([cloud_name, api_key, api_secret]):
        return {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret
        }

    return None  # Credentials not configured
```

If not configured, guide the user:
1. Sign up at https://cloudinary.com (free tier: 25 credits/month)
2. Find credentials in Dashboard > Programmable Media > API Keys
3. Set `CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME`

### Step 2: Choose Operation

| Operation | API | Method | When |
|-----------|-----|--------|------|
| Upload image | Upload API | POST `/image/upload` | New image to store |
| Upload video | Upload API | POST `/video/upload` | New video to store |
| Transform image | URL-based | GET (URL) | Resize, crop, effects |
| Optimize delivery | URL-based | GET (URL) | Performance improvement |
| List assets | Admin API | GET `/resources` | Browse media library |
| Delete asset | Upload API | POST `/image/destroy` | Remove media |
| Get asset details | Admin API | GET `/resources/{id}` | Check metadata |

### Step 3: Upload Media

**Upload an image:**
```python
import requests
import hashlib
import time

def upload_image(file_path: str, cloud_name: str, api_key: str, api_secret: str,
                 folder: str = "", tags: list = None):
    """Upload image to Cloudinary."""
    timestamp = str(int(time.time()))
    params_to_sign = f"timestamp={timestamp}"
    if folder:
        params_to_sign = f"folder={folder}&{params_to_sign}"

    signature = hashlib.sha1(
        f"{params_to_sign}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    data = {
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": signature,
    }
    if folder:
        data["folder"] = folder
    if tags:
        data["tags"] = ",".join(tags)

    with open(file_path, "rb") as f:
        response = requests.post(url, data=data, files={"file": f})

    return response.json()
```

### Step 4: Transform Images via URL

Build transformation URLs using this pattern:
```
https://res.cloudinary.com/{cloud_name}/image/upload/{transformations}/{public_id}.{format}
```

**Common transformation recipes:**

| Goal | Transformation | Example |
|------|---------------|---------|
| Thumbnail | `w_150,h_150,c_fill,g_face` | Face-aware 150x150 thumbnail |
| Hero image | `w_1200,h_600,c_fill,q_auto,f_auto` | Optimized hero banner |
| Profile avatar | `w_200,h_200,c_thumb,g_face,r_max` | Circular face crop |
| Product image | `w_800,h_800,c_pad,b_white` | Padded on white background |
| Social share | `w_1200,h_630,c_fill` | OpenGraph image size |
| Watermarked | `l_watermark,w_200,o_50,g_south_east` | Semi-transparent watermark |

### Step 5: Optimize for Performance

**Apply automatic optimization:**
```
# Add f_auto (format) and q_auto (quality) to any URL
https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto/{public_id}
```

**Generate responsive breakpoints:**
```python
def get_responsive_urls(cloud_name: str, public_id: str, widths: list = None):
    """Generate responsive image URLs."""
    if widths is None:
        widths = [320, 640, 960, 1280, 1920]

    base = f"https://res.cloudinary.com/{cloud_name}/image/upload"
    urls = {}
    for w in widths:
        urls[w] = f"{base}/w_{w},q_auto,f_auto/{public_id}"

    # Generate srcset string for HTML
    srcset = ", ".join(f"{url} {w}w" for w, url in urls.items())
    return urls, srcset
```

**HTML responsive image tag:**
```html
<img
  src="https://res.cloudinary.com/{cloud}/image/upload/w_800,q_auto,f_auto/{id}"
  srcset="{generated_srcset}"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Description"
  loading="lazy"
/>
```

### Step 6: Manage Assets

**List all assets:**
```python
def list_assets(cloud_name: str, api_key: str, api_secret: str,
                resource_type: str = "image", max_results: int = 30):
    """List assets in Cloudinary media library."""
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/{resource_type}"
    response = requests.get(
        url,
        params={"max_results": max_results},
        auth=(api_key, api_secret)
    )
    return response.json()
```

**Delete an asset:**
```python
def delete_asset(public_id: str, cloud_name: str, api_key: str, api_secret: str):
    """Delete an asset from Cloudinary."""
    timestamp = str(int(time.time()))
    signature = hashlib.sha1(
        f"public_id={public_id}&timestamp={timestamp}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/destroy"
    response = requests.post(url, data={
        "public_id": public_id,
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": signature
    })
    return response.json()
```

## Examples

### Example 1: Upload and Optimize
User says: "Upload a product image and generate optimized URLs"
Actions:
1. Upload via Upload API with folder and tags
2. Generate transformation URLs for thumbnail, product page, and social share
3. Apply f_auto,q_auto for each variant
Result: Public ID and multiple optimized URLs ready for use.

### Example 2: Responsive Image Set
User says: "Create responsive images for my website hero banner"
Actions:
1. Take the existing public_id
2. Generate srcset with breakpoints at 320, 640, 960, 1280, 1920px
3. Add f_auto,q_auto to each breakpoint URL
4. Provide complete HTML <img> tag with srcset and sizes
Result: Copy-paste-ready responsive image HTML.

### Example 3: Video Upload
User says: "Upload a video and get a streaming URL"
Actions:
1. Upload via /video/upload endpoint
2. Generate adaptive streaming URL with q_auto
3. Provide poster image URL (first frame transformation)
Result: Video URL with optimized delivery and poster image.

## Troubleshooting

### Error: "401 Unauthorized"
Cause: Invalid API key/secret or missing credentials
Solution: Verify CLOUDINARY_URL or individual env vars. Check API key is active in Cloudinary Dashboard.

### Error: "File too large"
Cause: Exceeds plan upload limits (free: 10MB image, 100MB video)
Solution: Compress before upload, or upgrade Cloudinary plan. Use `eager` transformations to create smaller versions on upload.

### Error: "Resource not found"
Cause: Invalid public_id or asset was deleted
Solution: Verify public_id with Admin API list. Check folder paths are included in public_id.
```

**Step 2: Create references**
- `references/transformation-cheatsheet.md` — Complete list of Cloudinary transformation parameters
- `references/optimization-guide.md` — Performance optimization best practices with f_auto, q_auto, responsive images

**Step 3: Validate and commit**
