---
name: cloudinary-assets
description: Manage media assets through Cloudinary's REST API -- upload, transform, optimize, and deliver images and videos. Use when user asks about image upload, media optimization, image transformations, responsive images, video management, CDN delivery, or mentions Cloudinary specifically. Covers Upload API, Admin API, URL-based transformations, AI-powered effects (gen_remove, gen_replace, background removal), and delivery optimization. Israeli-founded (2012) with R&D in Petah Tikva; global HQ in San Jose, California. Do NOT use for non-Cloudinary media hosting or local image processing without cloud upload.
license: MIT
allowed-tools: Bash(python:*) Bash(curl:*) WebFetch
compatibility: Requires Cloudinary account (free tier available). Needs CLOUDINARY_URL or API key/secret/cloud name environment variables.
version: 1.1.0
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
1. Sign up at https://cloudinary.com (free tier: 25 credits per month)
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

    # Note: This URL requires valid credentials and file upload
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

### Step 4b: AI-Powered Transformations (2024-2025)

Cloudinary's generative AI effects (gen_remove, gen_replace, gen_background_replace, gen_recolor, gen_fill, gen_restore) are available as URL params. Some variants may still be flagged as Beta on the docs page, so check the current status before relying on a specific effect in production:

| Param | What it does |
|-------|--------------|
| `e_gen_remove:prompt_(person)` | AI removes the matched object from the image |
| `e_gen_replace:from_(car);to_(bicycle)` | AI replaces one object with another |
| `e_gen_background_replace:prompt_(beach at sunset)` | Generative background swap |
| `e_background_removal` | Background removal (now in core, no longer a paid add-on) |
| `e_gen_restore` | AI restoration for old, blurry, or damaged photos |
| `auto_tagging:0.7` | Auto-tag uploads via AI (confidence threshold 0.0-1.0); pass at upload time |
| `f_auto:image` | Restrict auto format selection to image candidates (AVIF, WebP, JPEG) |
| `f_auto:video` | Restrict auto format selection to video candidates (mp4, webm) |

Example: remove a person from the background, then replace background:
```
https://res.cloudinary.com/{cloud_name}/image/upload/e_gen_remove:prompt_(person)/e_gen_background_replace:prompt_(modern office)/{public_id}
```

Auto-tagging at upload time:
```python
data = {
    "api_key": api_key, "timestamp": timestamp, "signature": signature,
    "categorization": "google_tagging",
    "auto_tagging": 0.7,  # accept tags with >=70% confidence
}
```

### Step 5: Optimize for Performance

**Apply automatic optimization:**
```
# Add f_auto (format) and q_auto (quality) to any URL
https://res.cloudinary.com/{cloud_name}/image/upload/f_auto,q_auto/{public_id}
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
  src="https://res.cloudinary.com/{cloud_name}/image/upload/w_800,q_auto,f_auto/{public_id}"
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
    # Note: This URL requires authentication
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

    # Note: This URL requires valid credentials and signature
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/destroy"
    response = requests.post(url, data={
        "public_id": public_id, "api_key": api_key,
        "timestamp": timestamp, "signature": signature
    })
    return response.json()
```

### Step 7: Use the URL Gen SDK (Optional)

The raw URL approach is portable and works in any language, but Cloudinary publishes typed SDKs that build the same URLs with autocomplete and less string-juggling:

- `@cloudinary/url-gen` v1.x (framework-agnostic, browser + Node)
- `@cloudinary/react` (React `<AdvancedImage />` and `<AdvancedVideo />`)
- `@cloudinary/vue` (Vue 3 components)

Install:
```bash
npm install @cloudinary/url-gen @cloudinary/react
```

Equivalent of `f_auto,q_auto,w_800` plus a face-aware crop:
```ts
import { Cloudinary } from "@cloudinary/url-gen";
import { fill } from "@cloudinary/url-gen/actions/resize";
import { focusOn } from "@cloudinary/url-gen/qualifiers/gravity";
import { face } from "@cloudinary/url-gen/qualifiers/focusOn";
import { auto as autoFormat } from "@cloudinary/url-gen/qualifiers/format";
import { auto as autoQuality } from "@cloudinary/url-gen/qualifiers/quality";
import { format, quality } from "@cloudinary/url-gen/actions/delivery";

const cld = new Cloudinary({ cloud: { cloudName: process.env.CLOUDINARY_CLOUD_NAME } });

const url = cld.image("products/shirt-blue")
  .resize(fill().width(800).height(800).gravity(focusOn(face())))
  .delivery(format(autoFormat()))
  .delivery(quality(autoQuality()))
  .toURL();
```

In React:
```tsx
import { AdvancedImage } from "@cloudinary/react";
<AdvancedImage cldImg={cld.image("products/shirt-blue").resize(fill().width(800))} />
```

### Step 8: Hebrew Text Overlays

Cloudinary's `l_text:` overlay supports Hebrew when you URL-encode the string and pick a font that ships Hebrew glyphs. Built-in fonts that include Hebrew (no font upload needed): **Heebo, Assistant, Rubik, David Libre, Frank Ruhl Libre, Suez One, Secular One**.

Pattern:
```
l_text:{font}_{size}_{style}:{url-encoded-text}
```

Example, "שלום" in Heebo 40 bold, white, on the bottom of an image:
```
https://res.cloudinary.com/{cloud_name}/image/upload/w_800,c_fill/l_text:Heebo_40_bold:%D7%A9%D7%9C%D7%95%D7%9D,co_white,g_south,y_30/{public_id}
```

Tip: encode the text with `urllib.parse.quote(text, safe="")` in Python or `encodeURIComponent()` in JS. Hebrew glyphs render correctly without explicit RTL flags as long as the font supports them.

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
- `scripts/upload_asset.py` ,  Cloudinary asset management client supporting image/video upload with folder and tag organization, URL-based transformation generation, responsive image set creation with srcset and HTML output, asset listing, and asset deletion. Reads credentials from CLOUDINARY_URL or individual env vars. Run: `python scripts/upload_asset.py --help`

### References
- `references/optimization-guide.md` ,  Cloudinary performance optimization guide covering f_auto/q_auto automatic optimization, responsive image breakpoints with HTML srcset patterns, DPR handling for retina displays, lazy loading strategies including blur-up LQIP placeholders, and upload-time eager transformations. Consult when building high-performance image delivery pipelines or optimizing page load times.
- `references/transformation-cheatsheet.md` ,  Complete Cloudinary URL transformation parameter reference including resize/crop modes, gravity positioning, quality/format options, visual effects, overlay/text parameters, responsive helpers, common recipes (thumbnail, hero, avatar, product, social share, watermark), video transformations, rate limits by plan tier, and environment setup. Consult when constructing transformation URLs or looking up specific parameter syntax.

## Gotchas

- Hebrew text overlays render correctly only when the font supports Hebrew glyphs (Heebo, Assistant, Rubik, David Libre, Frank Ruhl Libre, Suez One, Secular One). Latin-only fonts produce missing glyphs or boxes. The text value must be URL-encoded.
- Free tier includes 25 credits per month. One credit equals 1,000 transformations OR 1 GB managed storage OR 1 GB net viewing bandwidth (the metric whose consumption you exceed first is the one that bills). Usage is measured on a rolling 30-day window, not a calendar month. The Free → Plus jump is steep (around $89-99/month list price as of 2026), so model your eager-transform variants carefully before launch.
- Upload and Admin API endpoints require proper authentication. Example URLs in documentation may return 401/404 errors when accessed without valid credentials.
- Signed URLs and `auth_token`/strict transformation modes: derived URLs may be blocked unless signed. Toggle "Strict transformations" in Settings, Security, then sign delivery URLs with `s--{signature}--` or use `auth_token` for time-bound access.
- Eager vs lazy transforms: lazy (default) builds the derived asset on first request and caches it (slow first hit). Eager builds at upload time (faster first hit, costs upload credits). Use eager for predictable variants like thumbnails and social cards; let everything else stay lazy.
- Named transformations: define a reusable transformation like `t_product_card` in Settings, Transformations. URLs become `.../t_product_card/{public_id}` instead of long parameter chains, and you can change the recipe centrally without rewriting URLs.
- CORS for direct browser upload: by default, the Upload API blocks browser fetches from arbitrary origins. In Settings, Upload, Allowed CORS origins, add your site origins (no trailing slash) before calling the API from `fetch`/`XMLHttpRequest`.
- `upload_preset` in unsigned mode: unsigned upload presets let the browser upload without exposing the API secret. Lock down each preset (allowed formats, max file size, allowed folders, allowed tags) or anyone with the preset name can flood your account.
- `notification_url` webhook: pass `notification_url` in upload params (or set globally) to receive POST callbacks when async work finishes (eager transforms, video encoding, moderation). Cloudinary signs the body, verify the `X-Cld-Signature` header before trusting it.

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

### Error: "Invalid Signature" or signature mismatch on upload
Cause: Wrong parameter order, wrong API secret, or the timestamp drifted (Cloudinary rejects timestamps more than 1 hour off).
Solution: Sign the alphabetically sorted, ampersand-joined params (excluding `file`, `cloud_name`, `api_key`, `signature`), append the API secret, then SHA-1 the result. Sync your clock (NTP). When in doubt, log the exact `params_to_sign` string and compare to the docs.

### Error: "Rate limit exceeded" / 420 / 429
Cause: Free tier caps Admin API calls at 500/hour and total transformations at ~25,000/month.
Solution: Cache list/metadata responses, batch operations, or upgrade the plan. For traffic spikes, rely on the CDN cache (derived URLs are cached for 30+ days) instead of re-issuing Admin calls.

### Error: "Invalid transformation" / 400 on a derived URL
Cause: Unknown parameter, conflicting params (e.g., `c_fit` plus `g_face` makes no sense), or a chained transform missing a slash separator.
Solution: Test the URL piece by piece in the Cloudinary Media Explorer URL builder. Each chained transformation must be separated by `/`, parameters within one transformation by `,`.

### AVIF/WebP not loading in older browsers
Cause: `f_auto` picks AVIF for modern browsers, but some legacy browsers/middleboxes strip the `Accept` header so Cloudinary cannot detect support.
Solution: Cloudinary falls back to JPEG/PNG automatically. If you see broken images, force a safer fallback explicitly: `f_auto:image,q_auto` or pin `f_jpg` for the affected segment. Verify with `curl -H "Accept: image/avif" {url}` and `curl -H "Accept: */*" {url}`.

## Reference Links

- Cloudinary documentation home, https://cloudinary.com/documentation
- URL Gen SDK on GitHub, https://github.com/cloudinary/js-url-gen
- Transformation reference (URL params), https://cloudinary.com/documentation/transformation_reference
- Generative AI features overview, https://cloudinary.com/documentation/generative_ai_transformations
- Signed URLs and authenticated delivery, https://cloudinary.com/documentation/control_access_to_media
- Video transformation reference, https://cloudinary.com/documentation/video_transformation_reference