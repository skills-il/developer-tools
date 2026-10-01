# Domain checklist: cloudinary-assets

Coverage contract for the skill. Every Must/Should item cites an official Cloudinary page that was
fetched on 2026-10-01 (HTTP 200) and grepped for the topic named in brackets. A skill update that
drops a Must item, or contradicts its cited page, fails review.

## Must cover (core)

1. **Signed vs unsigned upload, and where the signature is generated.** Signed requests sign every
   parameter except `file`, `cloud_name`, `resource_type`, `api_key` (and the signature itself),
   sorted, with the API secret appended. For browser or Next.js uploads, generate the signature on
   the server (`api_sign_request`) and never ship `api_secret` to the client. Unsigned uploads need an
   unsigned `upload_preset`.
   https://cloudinary.com/documentation/authentication_signatures [api_sign_request] ,
   https://cloudinary.com/documentation/client_side_uploading [signed / unsigned, CORS] ,
   https://cloudinary.com/documentation/upload_presets [unsigned]
2. **Locking down unsigned presets for user-generated content** (`allowed_formats`, `disallow_public_id`,
   incoming transformations, moderation), because the preset name is public. Presets have NO per-preset
   file-size limit; enforce size client-side (Upload Widget `maxFileSize`).
   https://cloudinary.com/documentation/upload_presets ,
   https://cloudinary.com/documentation/moderate_assets
3. **Folder mode**: `asset_folder` (dynamic mode, does not change the public ID) vs `folder`
   (fixed mode, becomes part of the public ID). New product environments are dynamic.
   https://cloudinary.com/documentation/folder_modes [asset_folder]
4. **Resource type is part of every endpoint**: `image` / `video` / `raw` (and `auto` for upload).
   `destroy` is per resource type, and should pass `invalidate=true` when the delivered copy must
   disappear, because delivered assets stay cached on the CDN for up to 30 days.
   https://cloudinary.com/documentation/image_upload_api_reference [destroy, invalidate] ,
   https://cloudinary.com/documentation/invalidate_cached_media_assets_on_the_cdn ["up to 30 days"]
5. **Large files**: anything over 100 MB must use chunked upload (`upload_large`). This hits video
   first.
   https://cloudinary.com/documentation/upload_images [upload_large, "larger than 100 MB"]
6. **Admin API pagination and rate limits**: `max_results` up to 500, follow `next_cursor`; Admin API
   is rate limited (Free 500/h, paid from 2000/h), returns HTTP 420, exposes `X-FeatureRateLimit-*`.
   The Upload API is not hourly rate limited, but heavy parallel uploads can still get HTTP 420.
   https://cloudinary.com/documentation/admin_api [next_cursor, 420, X-FeatureRateLimit] ,
   https://cloudinary.com/documentation/upload_images ["Parallel uploads and rate limiting"]
7. **Automatic optimization**: `f_auto` and `q_auto` as the final components of every delivery URL,
   for images AND videos. `f_auto` without an extension on a video needs `f_auto:video`.
   https://cloudinary.com/documentation/image_optimization [f_auto] ,
   https://cloudinary.com/documentation/video_optimization ["Add q_auto and f_auto to every delivery URL"] ,
   https://cloudinary.com/documentation/transformation_reference [f_auto:video]
8. **Responsive images**: `srcset`/`sizes` with width breakpoints, `c_limit` so small originals are
   not upscaled, `dpr_auto` / `w_auto` (client hints) and their named-transformation limitation.
   https://cloudinary.com/documentation/responsive_images [srcset]
9. **Video delivery and adaptive streaming**: `/video/upload/` delivery, poster frames (`so_`), and
   adaptive bitrate streaming with `sp_auto` (or a named streaming profile) plus a `.m3u8` (HLS) or
   `.mpd` (DASH) extension. `q_auto` alone on an `.m3u8` is not adaptive streaming.
   https://cloudinary.com/documentation/adaptive_bitrate_streaming [sp_auto, .m3u8] ,
   https://cloudinary.com/documentation/transformation_reference [sp_auto, so_]
10. **Credits and transformation counting**: 1 credit = 1,000 transformations or 1 GB storage or
    1 GB image bandwidth, one shared pool. Each upload counts as a transformation; video derivatives
    are counted PER SECOND by output resolution and codec (SD 2 tx/s, HD 4 tx/s on h264).
    https://cloudinary.com/documentation/transformation_counts ["Derived HD videos", "Parts of seconds"] ,
    https://cloudinary.com/pricing [credit]
11. **Framework integration for the app the user is in**: for Next.js, `next-cloudinary`
    (`CldImage`, `CldUploadWidget` with `signatureEndpoint`, `CldVideoPlayer`); for React,
    `@cloudinary/url-gen` + `@cloudinary/react`.
    https://cloudinary.com/documentation/nextjs_integration [next-cloudinary] ,
    https://next.cloudinary.dev/clduploadwidget/signed-uploads [signatureEndpoint, api_sign_request]

## Should cover (advanced)

1. **Eager and incoming transformations, as the REST API actually takes them**: `eager` is a
   pipe-separated string (`eager=w_150,h_150,c_fill,g_face|w_800,c_limit`) and is a signed
   parameter; `eager_async` + `eager_notification_url` for video. Incoming transformations go in the
   `transformation` parameter. `f_auto` has no effect in eager and must NEVER be used in an incoming
   transformation.
   https://cloudinary.com/documentation/eager_and_incoming_transformations ["pipe character", "Never use f_auto"]
2. **Layers**: image overlays `l_<public_id>` with `fl_layer_apply` closing the layer component,
   positioning (`g_`, `x_`, `y_`), and folder separators in overlay IDs.
   https://cloudinary.com/documentation/layers [fl_layer_apply]
3. **Text overlays** `l_text:<font>_<size>_<style>:<encoded text>`, Hebrew-capable fonts, encoding.
   https://cloudinary.com/documentation/layers [l_text]
4. **Named transformations** (`t_<name>`), and that `dpr_auto` / `w_auto` are ineffective inside them.
   https://cloudinary.com/documentation/responsive_images [named transformations]
5. **Strict transformations, signed delivery URLs, token auth**.
   https://cloudinary.com/documentation/control_access_to_media [strict]
6. **Webhooks**: `notification_url`, `X-Cld-Signature` + `X-Cld-Timestamp` (legacy HMAC-SHA1) and
   `X-Cld-Signature_v2` (EdDSA) depending on the trigger's `auth_scheme`.
   https://cloudinary.com/documentation/notifications [X-Cld-Signature]
7. **Upload widget** as the no-code browser upload path.
   https://cloudinary.com/documentation/client_side_uploading
8. **Video player** for adaptive streams in the browser.
   https://cloudinary.com/documentation/cloudinary_video_player [cld-video-player]
9. **Generative AI effects and background removal**, with their special transformation counts.
   https://cloudinary.com/documentation/generative_ai_transformations ,
   https://cloudinary.com/documentation/background_removal
10. **CDN cache invalidation and versioned URLs** when overwriting an asset.
    https://cloudinary.com/documentation/invalidate_cached_media_assets_on_the_cdn

## Out of scope (explicit)

- **Cloudinary DAM / Assets UI workflows (collections, portals, approvals)**: admin console work, not API integration.
- **Structured metadata and Search API expressions in depth**: a catalog-management topic, mention only.
- **Video AI (auto-chaptering, transcription, translation add-ons)**: add-on specific, changes often, separate skill.
- **Self-hosting or migrating off Cloudinary / non-Cloudinary CDNs**: the skill's Do-NOT-use clause.
- **Local image processing (Pillow, sharp, ffmpeg)**: no cloud upload involved.
- **Per-plan limits beyond file size** (megapixels, per-plan rate tiers above 2000/h): change with the plan catalogue; point to https://cloudinary.com/pricing/compare-plans. Max file sizes per plan ARE covered in Troubleshooting. Re-checked 2026-10-01.
- **Mobile SDKs (iOS/Android/Flutter)**: the skill targets web and server use.

## Authoritative sources

- Docs home: https://cloudinary.com/documentation
- Upload API reference: https://cloudinary.com/documentation/image_upload_api_reference
- Admin API reference: https://cloudinary.com/documentation/admin_api
- Transformation URL reference: https://cloudinary.com/documentation/transformation_reference
- Adaptive streaming: https://cloudinary.com/documentation/adaptive_bitrate_streaming
- Transformation counts: https://cloudinary.com/documentation/transformation_counts
- Pricing: https://cloudinary.com/pricing
- Next.js SDK: https://cloudinary.com/documentation/nextjs_integration and https://next.cloudinary.dev/clduploadwidget/signed-uploads
- JS URL-gen SDK: https://github.com/cloudinary/js-url-gen
