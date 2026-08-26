---
name: cloudinary-assets
description: Manage media assets through Cloudinary's REST API -- upload, transform, optimize, and deliver images and videos. Use when user asks about image upload, media optimization, image transformations, responsive images, video management, CDN delivery, or mentions Cloudinary specifically. Covers Upload API, Admin API, URL-based transformations, AI-powered effects (gen_remove, gen_replace, background removal), and delivery optimization. Israeli-founded (2012) with R&D in Petah Tikva; global HQ in San Jose, California. Do NOT use for non-Cloudinary media hosting or local image processing without cloud upload.
license: MIT
allowed-tools: Bash(python:*) Bash(curl:*) WebFetch
compatibility: Requires Cloudinary account (free tier available). Needs CLOUDINARY_URL or API key/secret/cloud name environment variables.
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
                 folder="", asset_folder="", tags=None):
    """Upload image to Cloudinary."""
    timestamp = str(int(time.time()))

    # EVERY upload parameter except file, cloud_name, api_key, resource_type
    # and signature itself must be in the signed string, sorted alphabetically.
    # Signing only a subset (e.g. omitting tags) yields "Invalid Signature".
    params = {"timestamp": timestamp}
    if folder:
        params["folder"] = folder            # fixed folder mode
    if asset_folder:
        params["asset_folder"] = asset_folder  # dynamic folder mode (new accounts)
    if tags:
        params["tags"] = ",".join(tags)

    params_to_sign = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    signature = hashlib.sha1(
        f"{params_to_sign}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    data = {"api_key": api_key, "signature": signature, **params}

    with open(file_path, "rb") as f:
        response = requests.post(url, data=data, files={"file": f}, timeout=(10, 180))
    response.raise_for_status()
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

**Folder mode matters.** Cloudinary has two modes and new product environments are created in
**dynamic folder mode**. In dynamic folder mode the parameter that places an asset in the folder
tree is `asset_folder`, and it does NOT affect the public ID. The older `folder` parameter is the
fixed-folder-mode parameter, where the folder becomes part of the public ID. Passing `folder` on a
dynamic-folder account therefore does not do what a fixed-folder tutorial implies. Check your
product environment's folder mode in Settings before scripting bulk uploads, and pass
`asset_folder` when you are in dynamic mode.

### Step 4b: AI-Powered Transformations

Cloudinary's generative AI effects (gen_remove, gen_replace, gen_background_replace, gen_recolor, gen_restore) are available as `e_gen_*` URL params. Generative fill is the exception: it is a **background qualifier** `b_gen_fill:prompt_<text>` used with a padding crop in the SAME component, e.g. `c_pad,w_1600,h_900,b_gen_fill:prompt_beach` (200). Two traps: the prompt is unparenthesized like `e_gen_background_replace` (`b_gen_fill:prompt_(beach)` returns HTTP 500 `General Error`), and without a padding crop it returns HTTP 400 `gen_fill only available for padding crop modes` that fills a padded area, NOT an `e_gen_fill` effect (constructing `e_gen_fill:...` returns a 400). Some variants may still be flagged as Beta on the docs page, so check the current status before relying on a specific effect in production:

| Param | What it does |
|-------|--------------|
| `e_gen_remove:prompt_(person)` | AI removes the matched object from the image |
| `e_gen_replace:from_(car);to_(bicycle)` | AI replaces one object with another |
| `e_gen_background_replace:prompt_beach%20at%20sunset` | Generative background swap. Note the prompt is NOT parenthesized for this effect: `prompt_(beach)` returns HTTP 500 `General Error`, while `prompt_beach` returns 200. The parenthesized form is correct for `e_gen_remove` but not here |
| `e_background_removal` | Background removal, a built-in transformation (no separate add-on subscription; the legacy add-on is closed to new accounts from Feb 1 2026). It is NOT free, it bills via special transformation counting. |
| `e_gen_restore` | AI restoration for old, blurry, or damaged photos |
| `auto_tagging:0.7` | Auto-tag uploads via AI (confidence threshold 0.0-1.0); pass at upload time. Unlike the `e_gen_*` effects this is NOT built in: it requires registering a tagging add-on (Google Auto Tagging, AWS Rekognition, Imagga) on the Add-ons page first, otherwise the upload returns an error instead of tags |
| `f_auto:image` | Restrict auto format selection to image candidates (AVIF, WebP, JPEG) |
| `f_auto:video` | Restrict auto format selection to video candidates (mp4, webm) |

Example: remove a person from the background, then replace background:
```
https://res.cloudinary.com/{cloud_name}/image/upload/e_gen_remove:prompt_(person)/e_gen_background_replace:prompt_modern%20office/{public_id}
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
def list_assets(cloud_name, api_key, api_secret, resource_type="image",
                max_results=30, all_pages=False):
    """List assets in Cloudinary media library.

    The Admin API returns at most 500 per call and paginates with next_cursor.
    Ignoring the cursor truncates a "list everything" call at the first page
    with no error, so the short list looks complete.
    """
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/{resource_type}"
    params = {"max_results": min(max_results, 500)}
    resources = []
    while True:
        response = requests.get(url, params=params,
                                auth=(api_key, api_secret), timeout=(10, 60))
        response.raise_for_status()
        payload = response.json()
        resources.extend(payload.get("resources", []))
        cursor = payload.get("next_cursor")
        if not all_pages or not cursor:
            payload["resources"] = resources
            return payload
        params["next_cursor"] = cursor
```

**Delete an asset:**
```python
def delete_asset(public_id, cloud_name, api_key, api_secret,
                 resource_type="image"):
    """Delete an asset from Cloudinary.

    destroy is per resource type. Calling the image endpoint for a video
    returns "not found", which reads as "already deleted" while the asset is
    still there consuming storage credits, so pass the type you uploaded with.
    """
    timestamp = str(int(time.time()))
    signature = hashlib.sha1(
        f"public_id={public_id}&timestamp={timestamp}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/destroy"
    response = requests.post(url, data={
        "public_id": public_id, "api_key": api_key,
        "timestamp": timestamp, "signature": signature
    }, timeout=(10, 60))
    response.raise_for_status()
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

Cloudinary's `l_text:` overlay supports Hebrew when you URL-encode the string and pick a font that ships Hebrew glyphs. Built-in fonts that include Hebrew (no font upload needed): **Heebo, Assistant, Rubik, Frank Ruhl Libre, Suez One, Secular One**. `David Libre` and `Noto Sans Hebrew` are NOT Cloudinary font families: they return HTTP 400 with `x-cld-error: Unsupported font family`.

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

- Percent-encode EVERY space inside a transformation component. A raw space (for example `prompt_modern office`) makes the URL malformed: `curl` rejects it locally with exit code 3 and never sends a request, and `requests` behaves the same way. Browsers hide this by encoding silently. Use `%20`, or `urllib.parse.quote`.

- Hebrew text overlays need a font family Cloudinary actually ships. Verified working: Heebo, Assistant, Rubik, Frank Ruhl Libre, Suez One, Secular One. `David Libre` and `Noto Sans Hebrew` are NOT available and return HTTP 400 `Unsupported font family`, so an unrecognised name fails the whole URL rather than falling back. A Latin family like Arial is accepted (HTTP 200) rather than rejected, so the failure mode here is typographic rather than a 400. Pick a Hebrew family for typographic control; if you use a Latin one, inspect the rendered image yourself instead of trusting the 200. The text value must be URL-encoded.
- Free tier includes 25 credits per month. Per the pricing page, one credit equals 1,000 transformations OR 1GB managed storage OR 1GB IMAGE bandwidth. Video bandwidth is 2GB per credit and is PAID PLANS ONLY, so free-tier video delivery gets no boost. Credits are a single shared pool spent across transformations, storage and bandwidth together, not three separate allowances. The Free → Plus jump is steep (Plus lists at $99/month billed monthly, $89/month billed yearly, for 225 monthly credits as of 2026), so model your eager-transform variants carefully before launch.
- Upload and Admin API endpoints require proper authentication. Example URLs in documentation may return 401/404 errors when accessed without valid credentials.
- Signed URLs and `auth_token`/strict transformation modes: derived URLs may be blocked unless signed. Toggle "Strict transformations" in Settings, Security, then sign delivery URLs with `s--{signature}--` or use `auth_token` for time-bound access.
- Eager vs lazy transforms: lazy (default) builds the derived asset on first request and caches it (slow first hit). Eager builds at upload time (faster first hit, costs upload credits). Use eager for predictable variants like thumbnails and social cards; let everything else stay lazy.
- Named transformations: define a reusable transformation like `t_product_card` in Settings, Transformations. URLs become `.../t_product_card/{public_id}` instead of long parameter chains, and you can change the recipe centrally without rewriting URLs.
- CORS for direct browser upload: by default, the Upload API blocks browser fetches from arbitrary origins. In Settings, Upload, Allowed CORS origins, add your site origins (no trailing slash) before calling the API from `fetch`/`XMLHttpRequest`.
- Prefer an official server SDK over hand-rolled signing for backend work. `cloudinary` on npm (2.x) and `cloudinary` on PyPI (1.x) implement signing, retries and the folder-mode parameters for you; the bundled `scripts/upload_asset.py` hand-rolls SHA-1 signing so it stays dependency-light for one-off CLI use, which is not a reason to hand-roll it inside an application.

- `upload_preset` in unsigned mode: unsigned upload presets let the browser upload without exposing the API secret. Lock down each preset (allowed formats, max file size, allowed folders, allowed tags) or anyone with the preset name can flood your account.
- `notification_url` webhook: pass `notification_url` in upload params (or set globally) to receive POST callbacks when async work finishes (eager transforms, video encoding, moderation). Cloudinary signs the body, verify the `X-Cld-Signature` header before trusting it. The signature is `SHA-1(body + timestamp + api_secret)` where the timestamp comes from `X-Cld-Timestamp`, so verification is: `hashlib.sha1((raw_body + ts + api_secret).encode()).hexdigest() == received_signature`, compared with `hmac.compare_digest`. Reject anything older than about two hours. Use the raw request body, not a re-serialized JSON dict, or the digest will not match.

## Troubleshooting

### Error: "401 Unauthorized"
Cause: Invalid API key/secret or missing credentials
Solution: Verify CLOUDINARY_URL or individual env vars. Check API key is active in Cloudinary Dashboard.

### Error: "File too large"
Cause: Exceeds your plan's upload size limit. Cloudinary does not publish per-plan file-size caps in its public docs, so read the limits for your own plan in Console Settings rather than assuming a number. Any file larger than 100 MB must go through `upload_large` (chunked upload) regardless of plan.
Solution: Compress before upload, or upgrade Cloudinary plan. Use eager transformations to create smaller versions on upload.

### Error: "Resource not found"
Cause: Invalid public_id or asset was deleted
Solution: Verify public_id with Admin API list. Check folder paths are included in public_id.

### Error: "Invalid Signature" or signature mismatch on upload
Cause: Wrong parameter order, wrong API secret, or the timestamp drifted (Cloudinary rejects timestamps more than 1 hour off).
Solution: Sign the alphabetically sorted, ampersand-joined params (excluding `file`, `cloud_name`, `api_key`, `resource_type` and `signature` itself, and including EVERY other parameter you send, `tags` and `asset_folder` included), append the API secret, then SHA-1 the result. Sync your clock (NTP). When in doubt, log the exact `params_to_sign` string and compare to the docs. Cloudinary defaults to SHA-1 and also supports SHA-256 (pass `signature_algorithm=sha256`); the SHA-1 code above still works.

### Error: "Rate limit exceeded" / 420 / 429
Admin API rate limiting returns HTTP **420** (not 429) and carries `X-FeatureRateLimit-Limit`, `X-FeatureRateLimit-Remaining` and `X-FeatureRateLimit-Reset` headers; read `Remaining` to back off before you are cut off. The Upload API is not rate-limited this way.

Cause: the free tier caps Admin API calls at 500/hour and gives 25 monthly credits shared across transformations, storage and bandwidth. Do not read that as 25,000 transformations per month: that number is only reachable if storage and bandwidth consume zero credits, which cannot happen once the account holds assets.
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