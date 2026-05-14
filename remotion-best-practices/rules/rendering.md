---
name: rendering
description: Rendering Remotion videos locally and in the cloud (Lambda, Cloud Run)
metadata:
  tags: render, lambda, cloudrun, cli, export, concurrency
---

# Rendering Remotion videos

Studio (`npx remotion studio`) is for previewing. To produce a final video file you must render it.

## Local CLI render

```bash
npx remotion render [composition-id] out/video.mp4
```

Run `npx remotion render` with no composition id to get an interactive picker.

Common flags (verify against https://www.remotion.dev/docs/cli/render for the version you use):

- `--codec` -- output codec: `h264` (default), `h265`, `vp8`, `vp9`, `av1`, `prores`, plus audio-only `mp3`, `aac`, `wav`.
- `--concurrency` -- how many frames render in parallel. Higher uses more CPU/RAM; tune it down on memory-constrained machines, up on many-core machines.
- `--scale` -- scales output frames by the factor passed (greater than 0, up to 16, default 1). Use `--scale=2` for a 4K render of a 1080p composition; use a small value like `--scale=0.25` for a fast low-res preview render.
- `--frames` -- render only a frame range instead of the whole composition.
- `--image-format` -- image format used for intermediate frames.

Render a single still frame instead of a video:

```bash
npx remotion still [composition-id] --scale=0.25 --frame=30
```

## Cloud rendering

For rendering at scale or from a server (no local CPU cost, parallel across many functions):

- **AWS Lambda** -- `@remotion/lambda`. Mature, recommended cloud option. Deploy a Lambda function and an S3 site, then trigger renders via `renderMediaOnLambda()` or the `npx remotion lambda` CLI.
- **Google Cloud Run** -- `@remotion/cloudrun`. Alpha as of the 4.0.x line; the Remotion team plans to align its runtime with Lambda. Prefer Lambda for production until Cloud Run is stable.

Install whichever you need with `npx remotion add @remotion/lambda` (or `@remotion/cloudrun`). All Remotion packages must share the exact same version as `remotion` itself, so a single render package install will pull the matching version.

## Licensing reminder

Rendering, in Studio or in the cloud, is covered by the Remotion license. Remotion is free for individuals, non-profits, and for-profit organizations with 3 or fewer employees; organizations of 4 or more need a paid Company License. See [./../SKILL.md](../SKILL.md) Gotchas and https://www.remotion.dev/docs/license.

## Performance notes

- Lower `--concurrency` if a render runs out of memory; raise it on many-core machines for faster renders.
- `--scale` below 1 gives a fast draft render; above 1 gives a higher-resolution master at higher cost.
- Prefer `<OffthreadVideo>` over `<Video>` for embedded video during rendering. `<OffthreadVideo>` extracts frames off the main thread and renders them deterministically; `<Video>` can drop or duplicate frames during export.
- Keep `calculateMetadata` cheap and lazy. It runs before every render, so avoid heavy synchronous work; fetch only what is needed to compute duration, dimensions, and props.
- A single still or low-`--scale` render is the cheapest way to sanity-check layout before committing to a full render.
