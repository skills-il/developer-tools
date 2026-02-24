# Cloudinary Transformation Cheatsheet

## URL Pattern
```
https://res.cloudinary.com/{cloud_name}/image/upload/{transformations}/{public_id}.{format}
```

## Resize and Crop

| Parameter | Values | Description |
|-----------|--------|-------------|
| w_{width} | pixels | Width |
| h_{height} | pixels | Height |
| c_fill | | Fill dimensions, may crop |
| c_fit | | Fit within dimensions |
| c_limit | | Like fit but never upscale |
| c_pad | | Pad to dimensions |
| c_thumb | | Thumbnail with face detection |
| c_crop | | Crop to exact dimensions |
| c_scale | | Scale to dimensions |

## Gravity (Positioning)

| Parameter | Description |
|-----------|-------------|
| g_face | Detect and focus on face |
| g_faces | Multiple faces |
| g_auto | Automatic content-aware |
| g_center | Center (default) |
| g_north | Top |
| g_south | Bottom |
| g_east | Right |
| g_west | Left |
| g_north_east | Top-right |
| g_south_east | Bottom-right |

## Quality and Format

| Parameter | Values | Description |
|-----------|--------|-------------|
| q_auto | | Automatic quality optimization |
| q_auto:best | | Highest auto quality |
| q_auto:good | | Balanced auto quality |
| q_auto:eco | | Economy auto quality |
| q_auto:low | | Lowest auto quality |
| q_{1-100} | 1-100 | Manual quality percentage |
| f_auto | | Auto format (WebP, AVIF, etc.) |
| f_webp | | Force WebP |
| f_avif | | Force AVIF |
| f_jpg | | Force JPEG |
| f_png | | Force PNG |

## Effects

| Parameter | Description |
|-----------|-------------|
| e_blur:{strength} | Gaussian blur (1-2000) |
| e_grayscale | Convert to grayscale |
| e_sepia | Sepia tone effect |
| e_sharpen | Sharpen image |
| e_brightness:{level} | Adjust brightness |
| e_contrast:{level} | Adjust contrast |
| e_saturation:{level} | Adjust saturation |
| e_background_removal | AI background removal |
| e_gen_remove:{prompt} | AI generative remove |

## Overlays and Text

| Parameter | Description |
|-----------|-------------|
| l_{public_id} | Image overlay |
| l_text:{style}:{text} | Text overlay |
| o_{0-100} | Opacity of overlay |
| g_{position} | Overlay position |
| x_{offset} | X offset in pixels |
| y_{offset} | Y offset in pixels |

## Responsive and Performance

| Parameter | Description |
|-----------|-------------|
| dpr_auto | Automatic device pixel ratio |
| dpr_{1.0-5.0} | Manual DPR |
| w_auto | Automatic width (needs client hints) |
| fl_progressive | Progressive JPEG |
| fl_lossy | Allow lossy for PNG/GIF |

## Common Recipes

### Thumbnail (face-aware)
```
w_150,h_150,c_fill,g_face,q_auto,f_auto
```

### Hero Banner
```
w_1200,h_600,c_fill,q_auto,f_auto
```

### Profile Avatar (circular)
```
w_200,h_200,c_thumb,g_face,r_max,q_auto,f_auto
```

### Product Image (white background)
```
w_800,h_800,c_pad,b_white,q_auto,f_auto
```

### OpenGraph / Social Share
```
w_1200,h_630,c_fill,q_auto,f_auto
```

### Blurred Placeholder (LQIP)
```
w_50,h_50,c_fill,e_blur:1000,q_10,f_auto
```

### Watermark Overlay
```
l_watermark,w_200,o_50,g_south_east,x_10,y_10
```

## Video Transformations

| Parameter | Description |
|-----------|-------------|
| w_{width} | Video width |
| h_{height} | Video height |
| c_fill | Fill and crop |
| q_auto | Auto quality |
| f_auto | Auto format (mp4/webm) |
| so_{seconds} | Start offset |
| eo_{seconds} | End offset |
| du_{seconds} | Duration |
| ac_none | Remove audio |

### Video Thumbnail (poster)
```
# Get frame at 5 seconds as image
https://res.cloudinary.com/{cloud}/video/upload/so_5,w_800,h_450,c_fill,q_auto,f_jpg/{video_id}
```

## Rate Limits

| Plan | Requests/Hour | Transformations/Month |
|------|--------------|----------------------|
| Free | 500 | ~25,000 |
| Plus | 5,000 | ~225,000 |
| Advanced | 10,000 | ~2,250,000 |

## Environment Setup

```bash
# Single URL (preferred)
export CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME

# Or individual variables
export CLOUDINARY_CLOUD_NAME=mycloud
export CLOUDINARY_API_KEY=123456789
export CLOUDINARY_API_SECRET=abcdef123456
```
