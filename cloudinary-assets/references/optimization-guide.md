# Cloudinary Optimization Guide

## Automatic Optimization

### f_auto (Automatic Format)
Cloudinary detects the browser's capabilities and serves the best format:
- Chrome/Edge: AVIF or WebP
- Safari: WebP (modern) or JPEG
- Older browsers: JPEG or PNG

Typical savings: 30-50% smaller than JPEG

### q_auto (Automatic Quality)
Perceptual quality optimization that reduces file size without visible quality loss:
- q_auto:best - Highest quality, smaller savings
- q_auto:good - Good balance (default)
- q_auto:eco - More aggressive compression
- q_auto:low - Maximum compression

Typical savings: 40-80% smaller files

### Combined: f_auto,q_auto
Always use both together for maximum optimization:
```
https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto/{public_id}
```

## Responsive Images

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
  src=".../w_800,q_auto,f_auto/{id}"
  srcset="
    .../w_320,q_auto,f_auto/{id} 320w,
    .../w_640,q_auto,f_auto/{id} 640w,
    .../w_960,q_auto,f_auto/{id} 960w,
    .../w_1280,q_auto,f_auto/{id} 1280w,
    .../w_1920,q_auto,f_auto/{id} 1920w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Description"
  loading="lazy"
/>
```

### DPR (Device Pixel Ratio)
For fixed-size images on retina displays:
```
w_400,dpr_auto,q_auto,f_auto
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
Create optimized versions at upload time:
```python
eager_transforms = [
    {"width": 150, "height": 150, "crop": "fill", "gravity": "face"},  # thumb
    {"width": 800, "crop": "limit", "quality": "auto", "fetch_format": "auto"},  # web
    {"width": 1200, "height": 630, "crop": "fill"},  # social
]
```

### Incoming Transformations
Optimize the original on upload:
```python
incoming = {"quality": "auto", "fetch_format": "auto"}
```
