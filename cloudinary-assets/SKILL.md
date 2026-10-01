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
2. Find the cloud name, API key and secret on the API Keys page of the Console Settings
3. Set CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME

### Step 2: Choose Operation

| Operation | API | Method | When |
|-----------|-----|--------|------|
| Upload image | Upload API | POST /image/upload | New image to store |
| Upload video | Upload API | POST /video/upload | New video to store |
| Transform image | URL-based | GET (URL) | Resize, crop, effects |
| Optimize delivery | URL-based | GET (URL) | Performance improvement |
| List assets | Admin API | GET /resources | Browse media library |
| Delete asset | Upload API | POST /{resource_type}/destroy | Remove media (image, video or raw) |
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

**Files over 100 MB (most real videos)** cannot go through this single POST. Cloudinary requires chunked
upload for them: use the server SDK's `upload_large` (`cloudinary.uploader.upload_large` in Python,
`cloudinary.v2.uploader.upload_large` in Node) and ALWAYS pass `resource_type="video"` for a video. Do
not rely on the SDK default: in the current SDK source `upload_large` falls back to `raw`, and a raw
asset gets no video transformations, so every `/video/upload/` URL for it fails. Chunking does not lift
your plan's size cap (see Troubleshooting). For video eager transformations also pass
`eager_async=true` so encoding runs in the background instead of blocking the upload, and
`eager_notification_url` to be told when it finishes.

**Uploads from a browser or Next.js app.** Never ship `api_secret` to the client. There are two
documented routes, and either one is also the fix for a "blocked by CORS policy" error on a direct
browser upload:

1. **Signed (preferred for user uploads).** The browser asks your server for a signature, then uploads
   directly. With `next-cloudinary`, give `CldUploadWidget` a `signatureEndpoint`:
   ```ts
   // app/api/sign-cloudinary-params/route.ts (server only)
   import { v2 as cloudinary } from "cloudinary";
   export async function POST(request: Request) {
     // Authenticate the caller first: this route signs whatever it is sent.
     const { paramsToSign } = await request.json();
     const signature = cloudinary.utils.api_sign_request(paramsToSign, process.env.CLOUDINARY_API_SECRET!);
     return Response.json({ signature });
   }
   ```
   ```tsx
   import { CldUploadWidget } from "next-cloudinary";
   <CldUploadWidget signatureEndpoint="/api/sign-cloudinary-params">
     {({ open }) => <button onClick={() => open()}>Upload</button>}
   </CldUploadWidget>
   ```
   Env: `NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME`, `NEXT_PUBLIC_CLOUDINARY_API_KEY` (the key may be public),
   `CLOUDINARY_API_SECRET` (server only). `next-cloudinary` also ships `CldImage` and `CldVideoPlayer`
   for delivery.
2. **Unsigned.** An unsigned `upload_preset` named in the request. Anyone who sees the preset name can
   upload with it, so harden it (see Gotchas).

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
| Watermarked | l_{your_logo_public_id},w_200,o_50/fl_layer_apply,g_south_east | Semi-transparent watermark. Replace the placeholder with a real public ID: `l_watermark` on an account without that asset returns 400 `Resource not found - watermark` |

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
| `e_gen_replace:from_car;to_bicycle` | AI replaces one object with another (documented form is unparenthesized). A 400 `Invalid input for gen_replace` usually means the `from` object was not found in the image, not that the syntax is wrong |
| `e_gen_background_replace:prompt_beach%20at%20sunset` | Generative background swap. Note the prompt is NOT parenthesized for this effect: `prompt_(beach)` returns HTTP 500 `General Error`, while `prompt_beach` returns 200. The parenthesized form is correct for `e_gen_remove` but not here |
| `e_background_removal` | Background removal, a built-in transformation (no separate add-on subscription; the legacy add-on is closed to new accounts from Feb 1 2026). It is NOT free, it bills via special transformation counting. |
| `e_gen_restore` | AI restoration for old, blurry, or damaged photos |
| `auto_tagging:0.7` | Auto-tag uploads via AI (confidence threshold 0.0-1.0); pass at upload time. Unlike the `e_gen_*` effects this is NOT built in: it requires registering a tagging add-on (Google Auto Tagging, AWS Rekognition, Imagga) on the Add-ons page first, otherwise the upload returns an error instead of tags |

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
# categorization and auto_tagging are upload parameters, so both must be in the
# signed string too, or the upload fails with Invalid Signature.
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
        # c_limit: never upscale. Without it, w_1920 on an 864px original
        # delivers a 1920px image.
        urls[w] = f"{base}/w_{w},c_limit,q_auto,f_auto/{public_id}"

    srcset = ", ".join(f"{url} {w}w" for w, url in urls.items())
    return urls, srcset
```

**HTML responsive image tag:**
```html
<img
  src="https://res.cloudinary.com/{cloud_name}/image/upload/w_960,c_limit,q_auto,f_auto/{public_id}"
  srcset="{generated_srcset}"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Description"
  loading="lazy"
/>
```

**Video delivery.** Deliver from `/video/upload/`, not `/image/upload/` (the same public ID under the
image path is a different asset, usually a 404):

| Goal | URL |
|------|-----|
| Optimized progressive MP4/WebM | `.../video/upload/q_auto,f_auto:video/{public_id}` (use `f_auto:video` when the URL has no extension: with plain `f_auto`, a request whose Accept header lists image types, as a browser navigation does, gets an AVIF image instead of the video) |
| Adaptive bitrate streaming (HLS) | `.../video/upload/sp_auto/{public_id}.m3u8` (`.mpd` for DASH). Play it with an HLS/DASH-capable player such as the Cloudinary Video Player |
| Poster frame | `.../video/upload/so_5,w_800,h_450,c_fill,q_auto,f_jpg/{public_id}` |

`q_auto` on an `.m3u8` is NOT adaptive streaming: it returns a single-rendition playlist. Only `sp_auto`
(or a named streaming profile) produces the multi-rendition master playlist. Restrict an image URL to
image candidates with `f_auto:image`.

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
    invalidate=true also purges CDN copies; without it delivered versions can
    stay cached for up to 30 days after deletion.
    """
    timestamp = str(int(time.time()))
    signature = hashlib.sha1(
        f"invalidate=true&public_id={public_id}&timestamp={timestamp}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/destroy"
    response = requests.post(url, data={
        "public_id": public_id, "invalidate": "true", "api_key": api_key,
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

Cloudinary's `l_text:` overlay supports Hebrew when you URL-encode the string and pick a font that ships Hebrew glyphs. Built-in fonts that include Hebrew (no font upload needed): **Heebo, Assistant, Rubik, Frank Ruhl Libre, Suez One, Secular One**. Other Google Fonts, such as `David Libre` or `Noto Sans Hebrew`, are not in the built-in list, so the bare name returns HTTP 400 `Unsupported font family`; load them from Google Fonts by appending `@google` to the family name, e.g. `l_text:David%20Libre@google_40_700:...`. With `@google` the weight must be NUMERIC (`700`, not `bold`): `Heebo@google_40_bold` returns 400.

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
1. Upload via Upload API with `asset_folder` (dynamic folder mode, the default for new accounts; `folder` only on fixed-mode accounts) and tags
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
1. Upload via /video/upload endpoint (SDK `upload_large` with `resource_type="video"` if the file is over 100 MB)
2. Generate the adaptive streaming URL with `sp_auto` and a `.m3u8` extension (HLS), plus a progressive `q_auto,f_auto:video` fallback
3. Provide poster image URL (`so_0` or another offset, `f_jpg`)
Result: Adaptive HLS URL, progressive fallback and poster image.

## Bundled Resources

### Scripts
- `scripts/upload_asset.py` ,  Cloudinary asset management client supporting image/video upload with folder and tag organization, URL-based transformation generation, responsive image set creation with srcset and HTML output, asset listing, and asset deletion with CDN invalidation. Refuses files over 100 MB (use the SDK's `upload_large`), rejects face gravity with crop modes that would 400, percent-encodes public IDs and prints `X-Cld-Error`. Reads credentials from CLOUDINARY_URL or individual env vars. Run: `python scripts/upload_asset.py --help`

### References
- `references/optimization-guide.md` ,  Cloudinary performance optimization guide covering f_auto/q_auto automatic optimization, responsive image breakpoints with HTML srcset patterns, DPR handling for retina displays, lazy loading strategies including blur-up LQIP placeholders, and upload-time eager transformations. Consult when building high-performance image delivery pipelines or optimizing page load times.
- `references/domain-checklist.md` ,  Coverage contract for this skill: the Must/Should topics a complete Cloudinary integration needs, each tied to an official docs page, plus the explicit out-of-scope list. Consult before claiming the skill covers a scenario.
- `references/transformation-cheatsheet.md` ,  Complete Cloudinary URL transformation parameter reference including resize/crop modes, gravity positioning, quality/format options, visual effects, overlay/text parameters, responsive helpers, common recipes (thumbnail, hero, avatar, product, social share, watermark), video transformations, rate limits by plan tier, and environment setup. Consult when constructing transformation URLs or looking up specific parameter syntax.

## Gotchas

- Percent-encode EVERY space inside a transformation component. A raw space (for example `prompt_modern office`) makes the URL malformed: `curl` rejects it locally with exit code 3 and never sends a request, and `requests` behaves the same way. Browsers hide this by encoding silently. Use `%20`, or `urllib.parse.quote`.

- Hebrew text overlays need a font family Cloudinary actually ships. Verified working built-ins: Heebo, Assistant, Rubik, Frank Ruhl Libre, Suez One, Secular One. A bare `David Libre` or `Noto Sans Hebrew` returns HTTP 400 `Unsupported font family` (use the `@google` suffix with a numeric weight instead), so an unrecognised name fails the whole URL rather than falling back. A Latin family like Arial is accepted (HTTP 200) rather than rejected, so the failure mode here is typographic rather than a 400. Pick a Hebrew family for typographic control; if you use a Latin one, inspect the rendered image yourself instead of trusting the 200. The text value must be URL-encoded.
- Free tier includes 25 credits per month. Per the pricing page, one credit equals 1,000 transformations OR 1GB managed storage OR 1GB IMAGE bandwidth. Video bandwidth is 2GB per credit and is PAID PLANS ONLY, so free-tier video delivery gets no boost. Credits are a single shared pool spent across transformations, storage and bandwidth together, not three separate allowances. The Free → Plus jump is steep (Plus lists at $99/month billed monthly, $89/month billed yearly, for 225 monthly credits as of 2026), so model your eager-transform variants carefully before launch. Video transformations are counted PER SECOND of output, not per URL: on h264, 2 per second for SD and 4 per second for HD (AV1 costs 16 and 32), and parts of seconds count as a full second. A 60-second HD rendition is 240 transformations. Adaptive streaming with `sp_auto` costs more: 8 per second up to 1080p, 12 at 1440p and 24 at 4K, whatever the number of renditions, so the same 60-second clip via `sp_auto` is 480. Every upload, and every overwrite of an existing public ID, also counts as one transformation.
- Upload and Admin API endpoints require proper authentication. Example URLs in documentation may return 401/404 errors when accessed without valid credentials.
- Signed URLs and `auth_token`/strict transformation modes: derived URLs may be blocked unless signed. Toggle "Strict transformations" in Settings, Security, then sign delivery URLs with `s--{signature}--` or use `auth_token` for time-bound access.
- Overwriting an asset (`overwrite=true` with the same public ID) leaves the old version on the CDN for up to 30 days. Pass `invalidate=true` on the upload as well, or deliver with the version component from the upload response (`v<version>/` in the URL), which takes effect immediately.
- Eager vs lazy transforms: lazy (default) builds the derived asset on first request and caches it (slow first hit). Eager builds at upload time (faster first hit, costs upload credits). Use eager for predictable variants like thumbnails and social cards; let everything else stay lazy.
- Named transformations: define a reusable transformation like `t_product_card` in Settings, Transformations. URLs become `.../t_product_card/{public_id}` instead of long parameter chains, and you can change the recipe centrally without rewriting URLs.
- "Blocked by CORS policy" on a direct browser upload: the documented fix is an unsigned upload preset or a backend-generated signature (Step 3), not a console origin setting.
- Prefer an official server SDK over hand-rolled signing for backend work. `cloudinary` on npm (2.x) and `cloudinary` on PyPI (1.x) implement signing, retries and the folder-mode parameters for you; the bundled `scripts/upload_asset.py` hand-rolls SHA-1 signing so it stays dependency-light for one-off CLI use, which is not a reason to hand-roll it inside an application.

- `upload_preset` in unsigned mode: unsigned upload presets let the browser upload without exposing the API secret, but anyone with the preset name can use them. Harden each preset with `allowed_formats`, `disallow_public_id` and incoming transformations that normalize dimensions. Presets do NOT support a per-preset file-size limit, so enforce size on the client (the Upload Widget's `maxFileSize`). Never put `f_auto` in an incoming transformation: format must be chosen per request at delivery. For user-generated content also set `moderation` (a manual queue or an AI moderation add-on) so nothing is published unreviewed.
- `notification_url` webhook: pass `notification_url` in upload params (or set globally) to receive POST callbacks when async work finishes (eager transforms, video encoding, moderation). Cloudinary signs the body, verify the `X-Cld-Signature` header before trusting it. The signature is `SHA-1(body + timestamp + api_secret)` where the timestamp comes from `X-Cld-Timestamp`, so verification is: `hashlib.sha1((raw_body + ts + api_secret).encode()).hexdigest() == received_signature`, compared with `hmac.compare_digest`. Reject anything older than about two hours. Use the raw request body, not a re-serialized JSON dict, or the digest will not match. The digest may also be SHA-256, and the SDK helpers (`cloudinary.utils.verify_notification_signature` in Python, `cloudinary.utils.verifyNotificationSignature` in Node) do this for you. Triggers created with `auth_scheme` `eddsa_v2` send only `X-Cld-Signature_v2` (Ed25519) and no legacy header, so the SHA-1 check above cannot verify them.

## Troubleshooting

### Error: "401 Unauthorized"
Cause: Invalid API key/secret or missing credentials
Solution: Verify CLOUDINARY_URL or individual env vars. Check API key is active in Cloudinary Dashboard.

### Error: "File too large"
Cause: Exceeds your plan's maximum file size. Per Cloudinary's Compare Plans page: Free allows 10 MB images, 100 MB videos and 10 MB raw files; Plus 20 MB, 2 GB and 20 MB; Advanced 40 MB, 4 GB and 40 MB; Enterprise is custom. Separately, any file over 100 MB must be sent with chunked upload (`upload_large`), but chunking does not raise the plan cap.
Solution: Compress or resize before upload (a Free-plan photo over 10 MB will be rejected however it is sent), use `upload_large` with the right `resource_type` for anything over 100 MB, or upgrade the plan.

### Error: "Resource not found"
Cause: Invalid public_id or asset was deleted
Solution: Verify public_id with Admin API list. Check folder paths are included in public_id.

### Error: "Invalid Signature" or signature mismatch on upload
Cause: Wrong parameter order, wrong API secret, or the timestamp drifted (Cloudinary rejects timestamps more than 1 hour off).
Solution: Sign the alphabetically sorted, ampersand-joined params (excluding `file`, `cloud_name`, `api_key`, `resource_type` and `signature` itself, and including EVERY other parameter you send, `tags` and `asset_folder` included), append the API secret, then SHA-1 the result. Sync your clock (NTP). When in doubt, log the exact `params_to_sign` string and compare to the docs. Cloudinary defaults to SHA-1 and also accepts SHA-256. In the SDKs that is the `signature_algorithm=sha256` configuration parameter, not an upload field; over raw REST you simply hash with SHA-256. The SHA-1 code above still works.

### Error: "Rate limit exceeded" / 420 / 429
Admin API rate limiting is documented as HTTP **420** and carries `X-FeatureRateLimit-Limit`, `X-FeatureRateLimit-Remaining` and `X-FeatureRateLimit-Reset` headers; read `Remaining` to back off before you are cut off. The current official SDKs also treat **429** as rate-limited, so handle both codes. The Upload API has no hourly limit, but heavy parallel uploads (bulk migrations) can still get 420: start around 10 concurrent uploads and retry with exponential backoff.

Cause: the free tier caps Admin API calls at 500/hour and gives 25 monthly credits shared across transformations, storage and bandwidth. Do not read that as 25,000 transformations per month: that number is only reachable if storage and bandwidth consume zero credits, which cannot happen once the account holds assets.
Solution: Cache list/metadata responses, batch operations, or upgrade the plan. Cache Admin API responses in your own app; the CDN (which can cache delivered assets for up to 30 days) serves delivery URLs, never Admin API metadata calls.

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
- Adaptive bitrate streaming, https://cloudinary.com/documentation/adaptive_bitrate_streaming
- Client-side (browser) uploading, https://cloudinary.com/documentation/client_side_uploading
- Next.js SDK (next-cloudinary), https://cloudinary.com/documentation/nextjs_integration