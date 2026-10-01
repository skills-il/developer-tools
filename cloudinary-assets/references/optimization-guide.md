# Cloudinary Optimization Guide

## Automatic Optimization

### f_auto (Automatic Format)
Cloudinary reads the requesting browser's Accept header and serves the most efficient format it supports (for example AVIF or WebP), falling back to JPEG or PNG when the browser advertises neither.

Typical bandwidth reduction vs original JPEG depends on the source and the format the browser actually accepts. Order-of-magnitude reference points published by the format owners: WebP delivers around 25-34% smaller files than JPEG at equivalent visual quality per Google's lossy comparison study. Real-world results depend heavily on the source image, the q_auto level you pair with f_auto, and which format the viewer's browser ends up receiving.

### q_auto (Automatic Quality)
Perceptual quality optimization that reduces file size without visible quality loss:
- q_auto:best - Highest quality, smaller savings
- q_auto:good - Good balance (default)
- q_auto:eco - More aggressive compression
- q_auto:low - Maximum compression

Combined f_auto + q_auto on a typical photo can cut byte size well below the original; measured savings vary by source.

### Combined: f_auto,q_auto
Always use both together for maximum optimization:
```
https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto/{public_id}
```

## Responsive Images

`c_limit` stops small originals being upscaled: `w_1920` on an 864px original delivers a 1920px image, while `w_1920,c_limit` delivers the 864px original. Reusing a srcset width for `src` avoids one extra derived asset.

### Standard Breakpoints
```
320px   - Mobile (portrait)
640px   - Mobile (landscape) / Small tablet
960px   - Tablet
1280px  - Desktop
1920px  - Large desktop / Retina
```

### HTML srcset Pattern
```html
<img
  src=".../w_960,c_limit,q_auto,f_auto/{id}"
  srcset="
    .../w_320,c_limit,q_auto,f_auto/{id} 320w,
    .../w_640,c_limit,q_auto,f_auto/{id} 640w,
    .../w_960,c_limit,q_auto,f_auto/{id} 960w,
    .../w_1280,c_limit,q_auto,f_auto/{id} 1280w,
    .../w_1920,c_limit,q_auto,f_auto/{id} 1920w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Description"
  loading="lazy"
/>
```

### DPR (Device Pixel Ratio)
For fixed-size images on retina displays:
```
w_400,dpr_auto,q_auto,f_auto
# Keep dpr_auto in the INLINE transformation. Cloudinary documents that
# dpr_auto and w_auto are not effective inside named transformations, so
# folding this recipe into a t_* named transformation silently drops the
# responsive behaviour.
```

## Lazy Loading

### Native Browser
```html
<img src="..." loading="lazy" />
```

### Blur-up LQIP (Low Quality Image Placeholder)
1. Generate tiny blurred placeholder:
   ```
   w_50,e_blur:1000,q_10,f_auto
   ```
2. Load full image and swap on load
3. Provides instant visual with ~500 byte placeholder

## Performance Checklist

1. Always use f_auto,q_auto on every image URL
2. Specify exact width needed (do not serve oversized images)
3. Use responsive srcset for images that vary by viewport
4. Add loading="lazy" for below-the-fold images
5. Use video poster images instead of autoplay for previews
6. Consider LQIP for hero images
7. Set appropriate cache headers (Cloudinary CDN handles this)

## Upload-time Optimization

### Eager Transformations
Create derived versions at upload time. Over the raw REST API (as in SKILL.md Step 3) `eager` is ONE
string of transformations separated by a pipe, and like every other upload parameter it must be in the
signed params or the upload fails with Invalid Signature:
```python
params = {
    "timestamp": timestamp,
    # thumb | web | social. No f_auto here: there is no requesting browser at
    # upload time, so f_auto has no effect in eager. Request each format you
    # need explicitly (e.g. add a f_webp variant) or let delivery pick it.
    "eager": "w_150,h_150,c_fill,g_face|w_800,c_limit,q_auto|w_1200,h_630,c_fill",
    "eager_async": "true",  # recommended for video and browser uploads
}
# then sign `params` exactly as in SKILL.md Step 3 and POST them with the file
```
The SDKs accept a list of dicts instead (`eager=[{"width": 150, ...}]`) and serialize it for you.

### Incoming Transformations
Transform the original before it is stored, via the `transformation` upload parameter (also signed),
for example to cap stored dimensions:
```python
params["transformation"] = "w_2000,h_2000,c_limit"
```
Never use `f_auto` (or `q_auto/f_auto`) in an incoming transformation: format must be chosen per request
at delivery, based on the requesting browser.
