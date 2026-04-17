---
name: remotion-best-practices
description: "Best practices for Remotion video creation in React with Hebrew RTL support. Use when dealing with Remotion code, creating programmatic videos, building Hebrew video content with RTL captions and text animations, or generating social media videos with Hebrew fonts. Covers animations, compositions, sequencing, transitions, audio/video, captions, 3D, charts, voiceover, and Hebrew/RTL text rendering. Do NOT use for non-Remotion video editing, general React development, or static image generation."
license: MIT
---

# Remotion Best Practices for Israeli Developers

## Problem

Creating programmatic videos with Hebrew text in Remotion is broken by default. Standard Remotion patterns produce left-aligned text, left-to-right typewriter reveals, and captions that render backwards for RTL content. Israeli developers waste hours debugging RTL layout issues, loading Hebrew fonts incorrectly, and fighting bidirectional text bugs that standard Remotion docs do not address.

## Instructions

### When to use

Use this skill whenever you are dealing with Remotion code to obtain domain-specific knowledge, especially when creating Hebrew or bilingual video content.

### New project setup

When in an empty folder or workspace with no existing Remotion project, scaffold one using:

```bash
npx create-video@latest --yes --blank --no-tailwind my-video
```

Replace `my-video` with a suitable project name.

### Starting preview

Start the Remotion Studio to preview a video:

```bash
npx remotion studio
```

### Optional: one-frame render check

You can render a single frame with the CLI to sanity-check layout, colors, or timing.
Skip it for trivial edits, pure refactors, or when you already have enough confidence from Studio or prior renders.

```bash
npx remotion still [composition-id] --scale=0.25 --frame=30
```

At 30 fps, `--frame=30` is the one-second mark (`--frame` is zero-based).

### Hebrew & RTL Video Production

For any Hebrew video content, load the [./rules/hebrew-rtl.md](./rules/hebrew-rtl.md) file. It covers:

- Hebrew Google Fonts (Heebo, Rubik, Assistant, Noto Sans Hebrew) with `subsets: ["hebrew"]`
- RTL text direction (`direction: "rtl"`, `textAlign: "right"`)
- Bidirectional text handling (Unicode bidi isolates for mixed Hebrew/English)
- Hebrew captions with RTL word highlighting
- Hebrew typewriter effects (right-to-left character reveal)
- Hebrew voiceover with ElevenLabs multilingual v2
- Israeli map coordinates and Hebrew map labels

### Captions

When dealing with captions or subtitles, load the [./rules/subtitles.md](./rules/subtitles.md) file for more information.

### Using FFmpeg

For some video operations, such as trimming videos or detecting silence, FFmpeg should be used. Load the [./rules/ffmpeg.md](./rules/ffmpeg.md) file for more information.

### Silence detection

When needing to detect and trim silent segments from video or audio files, load the [./rules/silence-detection.md](./rules/silence-detection.md) file.

### Audio visualization

When needing to visualize audio (spectrum bars, waveforms, bass-reactive effects), load the [./rules/audio-visualization.md](./rules/audio-visualization.md) file for more information.

### Sound effects

When needing to use sound effects, load the [./rules/sfx.md](./rules/sfx.md) file for more information.

### Rule files

Read individual rule files for detailed explanations and code examples:

- [rules/hebrew-rtl.md](rules/hebrew-rtl.md) - Hebrew RTL text, fonts, captions, bidi, and Israeli maps
- [rules/3d.md](rules/3d.md) - 3D content in Remotion using Three.js and React Three Fiber
- [rules/animations.md](rules/animations.md) - Fundamental animation skills for Remotion
- [rules/assets.md](rules/assets.md) - Importing images, videos, audio, and fonts into Remotion
- [rules/audio.md](rules/audio.md) - Using audio and sound in Remotion
- [rules/calculate-metadata.md](rules/calculate-metadata.md) - Dynamically set composition duration, dimensions, and props
- [rules/can-decode.md](rules/can-decode.md) - Check if a video can be decoded by the browser
- [rules/charts.md](rules/charts.md) - Chart and data visualization patterns for Remotion
- [rules/compositions.md](rules/compositions.md) - Defining compositions, stills, folders, default props
- [rules/display-captions.md](rules/display-captions.md) - TikTok-style captions with word highlighting
- [rules/extract-frames.md](rules/extract-frames.md) - Extract frames from videos at specific timestamps
- [rules/fonts.md](rules/fonts.md) - Loading Google Fonts and local fonts in Remotion
- [rules/get-audio-duration.md](rules/get-audio-duration.md) - Getting audio duration with Mediabunny
- [rules/get-video-dimensions.md](rules/get-video-dimensions.md) - Getting video width and height
- [rules/get-video-duration.md](rules/get-video-duration.md) - Getting video duration in seconds
- [rules/gifs.md](rules/gifs.md) - Displaying GIFs synchronized with Remotion timeline
- [rules/images.md](rules/images.md) - Embedding images using the Img component
- [rules/import-srt-captions.md](rules/import-srt-captions.md) - Importing .srt subtitle files
- [rules/light-leaks.md](rules/light-leaks.md) - Light leak overlay effects
- [rules/lottie.md](rules/lottie.md) - Embedding Lottie animations
- [rules/maps.md](rules/maps.md) - Map animations with Mapbox
- [rules/measuring-dom-nodes.md](rules/measuring-dom-nodes.md) - Measuring DOM element dimensions
- [rules/measuring-text.md](rules/measuring-text.md) - Measuring text dimensions and fitting text
- [rules/parameters.md](rules/parameters.md) - Make a video parametrizable with Zod schema
- [rules/sequencing.md](rules/sequencing.md) - Sequencing patterns for timing and delay
- [rules/silence-detection.md](rules/silence-detection.md) - Adaptive silence detection with FFmpeg
- [rules/tailwind.md](rules/tailwind.md) - Using TailwindCSS in Remotion
- [rules/text-animations.md](rules/text-animations.md) - Typography and text animation patterns
- [rules/timing.md](rules/timing.md) - Interpolation curves, easing, and spring animations
- [rules/transcribe-captions.md](rules/transcribe-captions.md) - Transcribing audio to generate captions
- [rules/transitions.md](rules/transitions.md) - Scene transition patterns
- [rules/transparent-videos.md](rules/transparent-videos.md) - Rendering video with transparency
- [rules/trimming.md](rules/trimming.md) - Trimming patterns for animations
- [rules/videos.md](rules/videos.md) - Embedding videos with trimming, volume, speed
- [rules/voiceover.md](rules/voiceover.md) - AI-generated voiceover with ElevenLabs TTS

## Gotchas

1. **CSS animations are forbidden in Remotion.** Never use `transition-*`, `animate-*`, `@keyframes`, or Tailwind animation classes. All motion must be driven by `useCurrentFrame()`. CSS animations will not render correctly during video export.

2. **Hebrew text without `direction: "rtl"` renders backwards.** Punctuation, numbers, and parentheses will appear on the wrong side. Every Hebrew text container must explicitly set RTL direction.

3. **Whisper `medium.en` model does not support Hebrew.** Use `medium` (the multilingual model) for Hebrew transcription. Using `medium.en` produces garbage output for Hebrew audio.

4. **`useFrame()` from React Three Fiber is forbidden.** Inside `<ThreeCanvas>`, only `useCurrentFrame()` from Remotion is allowed. Using `useFrame()` causes flickering during rendering because it animates outside Remotion's frame-based timeline.

5. **Native `<img>` and `<video>` elements cause blank frames.** Always use `<Img>` from `remotion` and `<Video>` from `@remotion/media`. These components ensure assets are fully loaded before rendering.

6. **RTL flips `flex-start` and `flex-end`.** In an RTL flex container, `flex-start` = RIGHT and `flex-end` = LEFT. To right-align icon+text rows in Hebrew, use `justifyContent: "flex-start"` (not `flex-end`). The RTL direction already reverses DOM order, so the first child (icon) renders on the right. Do not use `flexDirection: "row-reverse"` in RTL containers -- it double-reverses back to LTR order.

7. **Hebrew text wraps to a second line at the same font size English fits on one line.** Hebrew fonts (Heebo, Rubik, Assistant) at display weights render 20-30% wider than English at the same size. If an English title works at `fontSize: 72`, the Hebrew equivalent needs `54-60`. Also set `flexWrap: "nowrap"` and `whiteSpace: "nowrap"` on any flex row containing display-size Hebrew words to prevent unwanted line breaks mid-phrase.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Remotion Docs | https://www.remotion.dev/docs | API reference, latest version changes |
| Remotion GitHub | https://github.com/remotion-dev/remotion | Source code, issues, releases |
| @remotion/google-fonts | https://www.remotion.dev/docs/google-fonts | Available Google Fonts with Hebrew subset support |
| @remotion/captions | https://www.remotion.dev/docs/captions | Caption types, TikTok-style captions API |
| ElevenLabs TTS | https://elevenlabs.io/docs | Multilingual v2 model, Hebrew voice support |
| Google Fonts Hebrew | https://fonts.google.com/?subset=hebrew | Browse Hebrew-supporting fonts |

## Troubleshooting

### Hebrew text appears left-aligned
Add `direction: "rtl"` and `textAlign: "right"` to the text container style. For full-frame layouts, set `direction: "rtl"` on the `<AbsoluteFill>`.

### Captions show words in wrong order
The caption container needs `direction: "rtl"` and `whiteSpace: "pre"`. Without RTL direction, token rendering order is LTR.

### Hebrew font not rendering (shows squares or fallback)
Ensure you loaded the font with `subsets: ["hebrew"]` and called `waitUntilDone()` before rendering. Without the subset, the Hebrew glyphs are not downloaded.

### Numbers appear on wrong side of Hebrew text
Use Unicode bidi isolates: wrap numbers with `\u2066...\u2069` (LTR isolate) when embedded in Hebrew text.

### Whisper produces gibberish for Hebrew audio
Switch from `medium.en` to `medium` model. The `.en` suffix means English-only.

### Icons appear on the wrong side in flex rows
In an RTL container, `justifyContent: "flex-start"` aligns to the RIGHT, not left. Do not use `flexDirection: "row-reverse"` -- it double-reverses the order. Just put the icon as the first child in the DOM.
