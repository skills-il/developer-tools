---
name: cloudinary-assets
description: >-
  Manage media assets through Cloudinary's REST API -- upload, transform,
  optimize, and deliver images and videos. Use when user asks about image
  upload, media optimization, image transformations, responsive images, video
  management, CDN delivery, or mentions Cloudinary specifically. Covers Upload
  API, Admin API, URL-based transformations, and delivery optimization.
  Israeli-founded platform (Tel Aviv, 2012). Do NOT use for non-Cloudinary media
  hosting or local image processing without cloud upload.
license: MIT
allowed-tools: 'Bash(python:*) Bash(curl:*) WebFetch'
compatibility: >-
  Requires Cloudinary account (free tier available). Needs CLOUDINARY_URL or API
  key/secret/cloud name environment variables.
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags:
    - cloudinary
    - media
    - images
    - video
    - cdn
    - optimization
    - israel
  display_name:
    he: ניהול מדיה ב-Cloudinary
    en: Cloudinary Assets
  display_description:
    he: 'ניהול תמונות, וידאו וקבצי מדיה דרך Cloudinary API'
    en: >-
      Manage media assets through Cloudinary's REST API -- upload, transform,
      optimize, and deliver images and videos. Use when user asks about image
      upload, media optimization, image transformations, responsive images,
      video management, CDN delivery, or mentions Cloudinary specifically.
      Covers Upload API, Admin API, URL-based transformations, and delivery
      optimization. Israeli-founded platform (Tel Aviv, 2012). Do NOT use for
      non-Cloudinary media hosting or local image processing without cloud
      upload.
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
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
        return {"url": cloudinary_url}

    # Option 2: Individual variables
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    if all([cloud_name, api_key, api_secret]):
        return {"cloud_name": cloud_name, "api_key": api_key, "api_secret": api_secret}

    return None  # Credentials not configured
```

If not configured, guide the user:
1. Sign up at https://cloudinary.com (free tier: 25 credits/month)
2. Find credentials in Dashboard, then Programmable Media, then API Keys
3. Set CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME

### Step 2: Choose Operation

| Operation | API | Method | When |
|-----------|-----|--------|------|
| Upload image | Upload API | POST /image/upload | New image to store |
| Upload video | Upload API | POST /video/upload | New video to store |
| Transform image | URL-based | GET (URL) | Resize, crop, effects |
| Optimize delivery | URL-based | GET (URL) | Performance improvement |
| List assets | Admin API | GET /resources | Browse media library |
| Delete asset | Upload API | POST /image/destroy | Remove media |
| Get asset details | Admin API | GET /resources/{id} | Check metadata |

### Step 3: Upload Media

**Upload an image:**
```python
import requests
import hashlib
import time

def upload_image(file_path, cloud_name, api_key, api_secret,
                 folder="", tags=None):
    """Upload image to Cloudinary."""
    timestamp = str(int(time.time()))
    params_to_sign = f"timestamp={timestamp}"
    if folder:
        params_to_sign = f"folder={folder}&{params_to_sign}"

    signature = hashlib.sha1(
        f"{params_to_sign}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    data = {"api_key": api_key, "timestamp": timestamp, "signature": signature}
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
| Thumbnail | w_150,h_150,c_fill,g_face | Face-aware 150x150 thumbnail |
| Hero image | w_1200,h_600,c_fill,q_auto,f_auto | Optimized hero banner |
| Profile avatar | w_200,h_200,c_thumb,g_face,r_max | Circular face crop |
| Product image | w_800,h_800,c_pad,b_white | Padded on white background |
| Social share | w_1200,h_630,c_fill | OpenGraph image size |
| Watermarked | l_watermark,w_200,o_50,g_south_east | Semi-transparent watermark |

### Step 5: Optimize for Performance

**Apply automatic optimization:**
```
# Add f_auto (format) and q_auto (quality) to any URL
https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto/{public_id}
```

**Generate responsive breakpoints:**
```python
def get_responsive_urls(cloud_name, public_id, widths=None):
    """Generate responsive image URLs."""
    if widths is None:
        widths = [320, 640, 960, 1280, 1920]

    base = f"https://res.cloudinary.com/{cloud_name}/image/upload"
    urls = {}
    for w in widths:
        urls[w] = f"{base}/w_{w},q_auto,f_auto/{public_id}"

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
def list_assets(cloud_name, api_key, api_secret, resource_type="image", max_results=30):
    """List assets in Cloudinary media library."""
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/{resource_type}"
    response = requests.get(url, params={"max_results": max_results},
                            auth=(api_key, api_secret))
    return response.json()
```

**Delete an asset:**
```python
def delete_asset(public_id, cloud_name, api_key, api_secret):
    """Delete an asset from Cloudinary."""
    timestamp = str(int(time.time()))
    signature = hashlib.sha1(
        f"public_id={public_id}&timestamp={timestamp}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/destroy"
    response = requests.post(url, data={
        "public_id": public_id, "api_key": api_key,
        "timestamp": timestamp, "signature": signature
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
4. Provide complete HTML img tag with srcset and sizes
Result: Copy-paste-ready responsive image HTML.

### Example 3: Video Upload
User says: "Upload a video and get a streaming URL"
Actions:
1. Upload via /video/upload endpoint
2. Generate adaptive streaming URL with q_auto
3. Provide poster image URL (first frame transformation)
Result: Video URL with optimized delivery and poster image.

## Bundled Resources

### Scripts
- `scripts/upload_asset.py` — Cloudinary asset management client supporting image/video upload with folder and tag organization, URL-based transformation generation, responsive image set creation with srcset and HTML output, asset listing, and asset deletion. Reads credentials from CLOUDINARY_URL or individual env vars. Run: `python scripts/upload_asset.py --help`

### References
- `references/optimization-guide.md` — Cloudinary performance optimization guide covering f_auto/q_auto automatic optimization, responsive image breakpoints with HTML srcset patterns, DPR handling for retina displays, lazy loading strategies including blur-up LQIP placeholders, and upload-time eager transformations. Consult when building high-performance image delivery pipelines or optimizing page load times.
- `references/transformation-cheatsheet.md` — Complete Cloudinary URL transformation parameter reference including resize/crop modes, gravity positioning, quality/format options, visual effects, overlay/text parameters, responsive helpers, common recipes (thumbnail, hero, avatar, product, social share, watermark), video transformations, rate limits by plan tier, and environment setup. Consult when constructing transformation URLs or looking up specific parameter syntax.

## Troubleshooting

### Error: "401 Unauthorized"
Cause: Invalid API key/secret or missing credentials
Solution: Verify CLOUDINARY_URL or individual env vars. Check API key is active in Cloudinary Dashboard.

### Error: "File too large"
Cause: Exceeds plan upload limits (free: 10MB image, 100MB video)
Solution: Compress before upload, or upgrade Cloudinary plan. Use eager transformations to create smaller versions on upload.

### Error: "Resource not found"
Cause: Invalid public_id or asset was deleted
Solution: Verify public_id with Admin API list. Check folder paths are included in public_id.

