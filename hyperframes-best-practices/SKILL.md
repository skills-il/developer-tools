---
name: hyperframes-best-practices
description: "Best practices for programmatic video creation using HyperFrames, plain HTML compositions with GSAP animations rendered to MP4, with full Hebrew and RTL support. Covers composition authoring, data-* timing attributes, GSAP timeline contract, layout-before-animation methodology, visual identity gate, Hebrew fonts via Google Fonts (Heebo, Rubik, Assistant), RTL text rendering with dir=\"rtl\", Hebrew TikTok/Reels-style captions via Whisper, audio-reactive visuals, scene transitions, and bidirectional Hebrew+English text. Use when building HTML-based video content or Hebrew social/marketing videos without React. Do NOT use for Remotion or general React video work, use remotion-best-practices for that."
license: Apache-2.0
---

# HyperFrames Best Practices

> Adapted from the upstream HyperFrames skill at [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) (Apache-2.0). Hebrew and RTL adaptations by [skills-il](https://agentskills.co.il).

HTML is the source of truth for video. A composition is an HTML file with `data-*` attributes for timing, a GSAP timeline for animation, and CSS for appearance. The framework handles clip visibility, media playback, and timeline sync.

## Problem

Building HTML-based videos with Hebrew text requires declaring a Hebrew Google font in a form the linter accepts (no Hebrew family is pre-bundled), explicit `dir="rtl"` on Hebrew containers, mirrored GSAP entrance directions, and Hebrew caption sync via Whisper, none of which HyperFrames documents out of the box. Hebrew voiceover is a separate gap: the local Kokoro fallback does not support Hebrew (its `SUPPORTED_LANGS` tuple holds 9 locales: en-us, en-gb, es, fr-fr, hi, it, pt-br, ja, zh), so Hebrew narration must come from a cloud TTS provider: the media-use audio engine (automatic order HeyGen Starfish, then ElevenLabs, then Kokoro; Gemini TTS, whose language table lists Hebrew, is an explicit `"provider": "gemini"` choice outside that order), or any external service whose file you import as an `<audio>` element. The `hyperframes tts` command itself is local-only and has no provider argument.

## Hebrew and RTL

<HARD-GATE>
**Never put `dir="rtl"` (or `dir="auto"`) on the `<html>` element.** It previews correctly, snapshots correctly, and can then render a fully blank black MP4, whose only tell is a file far smaller than expected. Upstream ships this as a severity-`error` lint rule, `html_dir_attribute_breaks_render`, with the note "a confirmed, silent failure". On HyperFrames 0.8.138 our local test render of such a file recovered after the renderer flagged a "suspect small frame" at frame 0, but treat that as a safety net, not a fix: the rule stands, and `render` only blocks on it with `--strict`. Keep `lang="he"` on `<html>`, and scope direction to the elements that hold text: `dir="rtl"` on the composition root div, on Hebrew text containers, and on caption word spans. Text still shapes correctly, because the browser's bidi algorithm runs off the element's own direction. This is the single highest-cost mistake available in a Hebrew composition, and it is reachable only from Hebrew.
</HARD-GATE>

For Hebrew and RTL compositions, load [references/hebrew-rtl.md](./references/hebrew-rtl.md). It covers Hebrew font loading (declare the family with a Google Fonts `<link>`; the compiler embeds it at build time), `dir="rtl"` scoping, GSAP x-axis mirroring, Hebrew caption sync via `hyperframes transcribe --language he`, Hebrew voiceover via external TTS, and bidirectional text with `<bdi>`.

## Host Capabilities

Every gate in this skill (`npx hyperframes check`, `render`, `transcribe`, `normalize-audio`, `doctor`, and the two bundled Node scripts) is a shell command needing a local Node 22+ and FFmpeg install. Split your expectations by host:

| Host tier | Hosts | What you get |
|---|---|---|
| Shell | claude-code, cursor, windsurf, github-copilot, opencode, codex | The whole skill, gates included |
| No shell | chatgpt, claude-ai, claude-desktop, manus | Authoring guidance only. You can write a correct composition; you cannot lint, contrast-audit, transcribe or render it |

On a no-shell host, say so up front and hand the user the commands to run; the Hebrew rules then have to be followed by construction, since nothing verifies them.

## Approach

Before writing HTML, settle in order: what the viewer should experience (arc, key beats), the structure (which scenes are sub-compositions, what each track carries), the timing (what drives duration, where transitions land), then the layout (end state first, see below), and only then the animation. For small edits (a color, one duration, one element), skip straight to the rules.

### Visual Identity Gate

<HARD-GATE>
Before writing ANY composition HTML, you MUST have a visual identity defined. Do NOT write compositions with default or generic colors.

Check in this order:

1. **DESIGN.md exists in the project?** → Read it. Use its exact colors, fonts, motion rules, and "What NOT to Do" constraints.
2. **visual-style.md exists?** → Read it. Apply its `style_prompt_full` and structured fields. (Note: `visual-style.md` is a project-specific file. `visual-styles.md` is the style library with 8 named presets, different files.)
3. **User named a style** (e.g., "Swiss Pulse", "dark and techy", "luxury brand")? → Read [visual-styles.md](./visual-styles.md) for the 8 named presets. Generate a minimal DESIGN.md with: `## Style Prompt` (one paragraph), `## Colors` (3-5 hex values with roles), `## Typography` (1-2 font families), `## What NOT to Do` (3-5 anti-patterns).
4. **None of the above?** → Ask 3 questions before writing any HTML:
   - What's the mood? (explosive / cinematic / fluid / technical / chaotic / warm)
   - Light or dark canvas?
   - Any specific brand colors, fonts, or visual references?
     Then generate a minimal DESIGN.md from the answers.

Every composition must trace its palette and typography back to a DESIGN.md, visual-style.md, or explicit user direction. If you're reaching for `#333`, `#3b82f6`, or `Roboto`, you skipped this step.
</HARD-GATE>

For motion defaults, sizing, entrance patterns, and easing, follow [house-style.md](./house-style.md). The house style handles HOW things move. The DESIGN.md handles WHAT things look like.

## Layout Before Animation

Position every element where it should be at its **most visible moment**, the frame where it's fully entered, correctly placed, and not yet exiting. Write this as static HTML+CSS first. No GSAP yet.

**Why this matters:** If you position elements at their animated start state (offscreen, scaled to 0, opacity 0) and tween them to where you think they should land, you're guessing the final layout. Overlaps are invisible until the video renders. By building the end state first, you can see and fix layout problems before adding any motion.

### The process

1. **Identify the hero frame** for each scene, the moment when the most elements are simultaneously visible. This is the layout you build.
2. **Write static CSS** for that frame. The `.scene-content` container MUST fill the full scene using `width: 100%; height: 100%; padding: Npx;` with `display: flex; flex-direction: column; gap: Npx; box-sizing: border-box`. Use padding to push content inward, NEVER `position: absolute; top: Npx` on a content container. Absolute-positioned content containers overflow when content is taller than the remaining space. Reserve `position: absolute` for decoratives only.
3. **Add entrances with `gsap.from()`**, animate FROM offscreen/invisible TO the CSS position. The CSS position is the ground truth; the tween describes the journey to get there.
4. **Add exits with `gsap.to()`**, animate TO offscreen/invisible FROM the CSS position.

The worked example (right and wrong CSS, entrance and exit tweens) and the two edge cases (elements sharing space across time, intentional overlap) are in [references/layout-before-animation.md](references/layout-before-animation.md).

## Data Attributes

Synced to upstream `skills/hyperframes-core/references/data-attributes.md`; read that file for the full list (`data-automation`, `data-link`, variables).

### All Clips

| Attribute          | Required                                     | Values                                                                 |
| ------------------ | -------------------------------------------- | ---------------------------------------------------------------------- |
| `id`               | Yes on `<video>`/`<audio>`, else recommended | An id-less `<audio>` is never mixed, so the render is silent           |
| `data-start`       | Yes                                          | Seconds or clip ID reference (`"el-1"`, `"intro + 2"`). Makes the element timed |
| `data-duration`    | Required for `div` and sub-compositions      | Seconds. An `img` defaults to 3s; video/audio default to the source length |
| `data-track-index` | No                                           | Integer. A Studio display lane, not a timing constraint                |
| `data-media-start` | No                                           | Trim offset into source (seconds)                                      |
| `data-volume`      | No                                           | Static gain, default 1, up to 3.98 (+12 dB). Fades and ducking: `data-automation` |
| `data-has-audio`   | On a timed `<video>` unless it is `muted`    | `"true"` keeps the footage's own sound                                 |

`data-track-index` does **not** affect visual layering (use CSS `z-index`) and it does **not** constrain timing. Upstream's linter says of it and its legacy alias `data-layer`: "Neither name is read by the render." Two clips on the same track index may overlap in time, so do not restructure tracks to free a lane.

The visibility window is half-open, `[start, start + duration)`: a clip is hidden at exactly `start + duration`, so land final tweens (a closing fade, a caption exit) slightly before it or their last frame is never rendered.

`class="clip"` is a convention the runtime never reads, but keep writing it on timed elements: it supplies the full-frame box, Studio uses it as an edit hint, and lint warns (`timed_element_missing_clip_class`) when a timed element lacks it. Omit it on `<video>` and `<audio>`.

### Composition Root and Hosts

| Attribute                    | Required                                        | Values                                       |
| ---------------------------- | ----------------------------------------------- | -------------------------------------------- |
| `data-composition-id`        | Yes on the root (matches its `window.__timelines` key); recommended on a host | Unique composition ID |
| `data-width` / `data-height` | Yes on the root; a host may omit them (backfilled from the loaded file) | 1920x1080 or 1080x1920 |
| `data-duration`              | Root: unless the runtime can infer it (registered timeline, timed clips); host: yes | Takes precedence over GSAP timeline duration |
| `data-composition-src`       | Yes on a host                                   | Path to the sub-composition HTML file        |
| `data-fps`                   | No                                              | Frame rate hint on the root; `render --fps` overrides it, else 30 |

## Composition Structure

Sub-compositions loaded via `data-composition-src` use a `<template>` wrapper. **Standalone compositions (the main index.html) do NOT use `<template>`**, they put the `data-composition-id` div directly in `<body>`. Using `<template>` on a standalone file hides all content from the browser and breaks rendering.

The runtime clones only the `<template>` contents into the host slot, so sub-composition content sits in the host DOM and inherits the host's direction. Still put `dir="rtl"` on the template's own root for Hebrew: a standalone render or snapshot of that file has no RTL ancestor. Sub-composition structure:

```html
<template>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Heebo:wght@400;800&display=swap");
    #root { position: absolute; inset: 0; font-family: "Heebo", sans-serif; }
  </style>
  <div id="root" data-composition-id="my-comp" data-width="1080" data-height="1920" dir="rtl">
    <!-- content -->
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    // tweens...
    window.__timelines["my-comp"] = tl;
  </script>
</template>
```

Everything the runtime needs (styles, markup, scripts) goes inside `<template>`; the file's `<head>` is discarded, and GSAP is loaded once by the host.

Load in root: `<div id="el-1" data-composition-id="my-comp" data-composition-src="compositions/my-comp.html" data-start="0" data-duration="10"></div>`

## Video and Audio

Silent footage and b-roll are `muted playsinline`. Footage whose own sound you want keeps it on the `<video>` with `data-has-audio="true"` and no `muted` (a timed video with neither fails lint, `video_missing_muted`). Voiceover, music and replacement audio go in separate `<audio>` elements, each with an `id`:

```html
<video id="broll" data-start="0" data-duration="30" src="broll.mp4" muted playsinline></video>
<audio id="vo-he" data-start="0" data-duration="30" src="assets/narration-he.wav"></audio>
```

## Timeline Contract

- All timelines start `{ paused: true }`, the player controls playback
- Register every timeline: `window.__timelines["<composition-id>"] = tl`, as the LAST step of the build (the runtime creates the registry for you)
- Framework auto-nests sub-timelines, do NOT manually add them
- Duration comes from `data-duration`, not from GSAP timeline length
- Never create empty tweens to set duration

## Rules (Non-Negotiable)

**Deterministic:** No `Math.random()`, `Date.now()`, `new Date()`, `performance.now()`, `requestAnimationFrame`, `gsap.utils.random()` or `"random(...)"` tween values; each is a lint error, and a lint error stops `check` early. Use a seeded PRNG (e.g. mulberry32).

**GSAP:** Prefer transforms and `opacity`. Never tween `display`, `visibility` or `autoAlpha` on a clip element (lint error `gsap_animates_clip_element`), animate a child instead, and never call `video.play()`/`audio.play()`.

**Animation conflicts:** Never animate the same property on the same element from multiple timelines simultaneously.

**No `repeat: -1`:** Without a finite root `data-duration` it is a lint error (`gsap_infinite_repeat`) and render planning can fail; with one it is only a warning, but a finite count is still the safe default. Count with `Math.floor`, never `Math.ceil`: `repeat: Math.max(0, Math.floor(Math.round((available / cycle) * 1000) / 1000) - 1)`, where `available` is the duration left after the tween's start offset and `cycle` includes any `repeatDelay` (the rounding stops float error such as `0.3 / 0.1` flooring to 2). Upstream lints the `Math.ceil(...) - 1` form as `gsap_repeat_ceil_overshoot`, because ceil runs one cycle past the end and the last cycle is cut mid-motion.

**Register last:** Building inside an async callback (for example `document.fonts.ready`) is supported; registering the key before the tweens exist is not. An empty timeline registered early renders blank (lint error `gsap_timeline_registered_before_async_build`). If you measure Hebrew text (`fitTextFontSize`), build inside `document.fonts.ready` so it measures the Hebrew face, not the fallback.

**Never do:**

1. Forget `window.__timelines` registration
2. Leave a timed `<video>` with neither `muted` nor `data-has-audio="true"`
3. Nest video inside a timed div, use a non-timed wrapper
4. Use `data-layer` (use `data-track-index`) or `data-end` (use `data-duration`)
5. Animate video element dimensions, animate a wrapper div
6. Call play/pause/seek on media, framework owns playback
7. Create a top-level container without `data-composition-id`
8. Use `repeat: -1` on any timeline or tween, always finite repeats
9. Register `window.__timelines[id]` before an async build has added its tweens
10. Use `gsap.set()` on clip elements from later scenes, they don't exist in the DOM at page load. Use `tl.set(selector, vars, timePosition)` inside the timeline at or after the clip's `data-start` time instead.
11. Use `<br>` in content text: it ignores rendered font width and doubles up with natural wrapping. Wrap via `max-width`; for a deliberate one-word-per-line title, give each word its own element.

## Scene Transitions (Non-Negotiable)

Every multi-scene composition MUST follow ALL of these rules. Violating any one of them is a broken composition.

1. **ALWAYS use transitions between scenes.** No jump cuts. No exceptions.
2. **ALWAYS use entrance animations on every scene.** Every element animates IN via `gsap.from()`. No element may appear fully-formed. If a scene has 5 elements, it needs 5 entrance tweens.
3. **NEVER use exit animations** except on the final scene. This means: NO `gsap.to()` that animates opacity to 0, y offscreen, scale to 0, or any other "out" animation before a transition fires. The transition IS the exit. The outgoing scene's content MUST be fully visible at the moment the transition starts.
4. **Final scene only:** The last scene may fade elements out (e.g., fade to black). This is the ONLY scene where `gsap.to(..., { opacity: 0 })` is allowed.

Wrong and right code for rule 3 is in [references/layout-before-animation.md](references/layout-before-animation.md).

## Animation Guardrails

- Offset first animation 0.1-0.3s (not t=0)
- Vary eases across entrance tweens, use at least 3 different eases per scene
- Don't repeat an entrance pattern within a scene
- Avoid full-screen linear gradients on dark backgrounds (H.264 banding, use radial or solid + localized glow)
- 60px+ headlines, 20px+ body, 16px+ data labels for rendered video
- `font-variant-numeric: tabular-nums` on number columns

When no `visual-style.md` or animation direction is provided, follow [house-style.md](./house-style.md) for aesthetic defaults.

## Typography and Assets

- **Fonts:** 18 families (Inter, Roboto, Montserrat and others, none Hebrew) are pre-bundled. Any other family, every Hebrew one included, must be declared, or lint fires `font_family_without_font_face`. See the Hebrew font Gotcha below.
- Never put `crossorigin` on `<video>`/`<audio>`: lint rejects it (`media_crossorigin_breaks_preview`, error), because it can blank the media in Studio preview. It is only for reading pixels back from a CORS host.
- For dynamic text overflow, use `window.__hyperframes.fitTextFontSize(text, { maxWidth, fontFamily, fontWeight })`. It returns an object `{ fontSize, fits }`, not a number, so read `.fontSize`. The full option set is `maxWidth, baseFontSize, minFontSize, fontWeight, fontFamily, step`. Defaults are `maxWidth: 1600` and `fontFamily: "Outfit"`, so a portrait Hebrew caption must pass both
- Asset paths are root-relative everywhere, sub-compositions included (`assets/narration-he.wav`). A `../` path is a lint error (`invalid_parent_traversal_in_asset_path`): compositions are served with the project root as their base URL

## Editing Existing Compositions

- Read the full composition first, match existing fonts, colors, animation patterns
- Only change what was requested
- Preserve timing of unrelated clips

## Output Checklist

For a Reel, start from `npx hyperframes init <name> --resolution portrait`: changing only `data-width`/`data-height` leaves `html`, `body` and the viewport meta at 1920x1080, and a stale `body { overflow: hidden }` clips the frame while lint only warns (`root_dimensions_mismatch`). `npx hyperframes catalog` and `npx hyperframes add <name>` install ready-made registry blocks (transitions among them); their names and tags are English, so search in English.

- [ ] Previewed with `npx hyperframes preview`, where a Hebrew reader catches word order, bidi and font fallback before paying for a render
- [ ] `npx hyperframes check --strict` passes (plain `check` while iterating; for Reels add `--caption-zone` with a `seek` list to keep headlines out of the caption band, see references/hebrew-rtl.md). A timed root-level element with nested layout raises the warning `nested_structure_needs_subcomposition`; untimed scene divs driven by the root timeline (the transitions catalog pattern) do not. It runs lint, runtime, layout, motion and the WCAG contrast pass in one browser session, but a lint error stops it before that session ("Browser session never ran"), so the other passes silently report nothing. `--strict` also fails on warnings such as `root_dimensions_mismatch`. `validate`, `inspect` and `layout` are compatibility aliases; `lint` is not
- [ ] Contrast failures fixed (see Quality Checks below)
- [ ] Animation choreography verified (see Quality Checks below)
- [ ] Rendered with `npx hyperframes render --strict`. Without `--strict`, render encodes straight through lint errors, `html_dir_attribute_breaks_render` included. Output flags: `--fps` (else the root `data-fps`, else 30), `--quality draft|looks|delivery` (default `looks`, CRF 16), `--format mp4|webm|mov|gif|png-sequence|hls`, `--crf`, and `--resolution portrait|portrait-4k`, whose aspect ratio must match the composition

## Quality Checks

### Contrast

`hyperframes check` runs a WCAG AA contrast audit by default (`--contrast` defaults to true; `--no-contrast` turns it off). It audits five frames, samples the background behind every text element and computes contrast ratios. Each failure is an error, so it fails `check`, and comes with a suggested color:

```
Contrast
  ✗ div > div > p:nth-of-type(1) 1.88:1 (need 3:1, t=1.389s)
    Try rgb(90,95,122); source index.html
```

WCAG 2.2 asks 4.5:1 for normal text and 3:1 for large text, meaning 18pt (24px) or 14pt bold (about 18.66px). `check` draws the bold cutoff at 19px, so bold text between 18.66px and 19px can be flagged by `check` while passing WCAG; the bundled `contrast-report.mjs` uses the WCAG cutoff. To fix:

- On dark backgrounds brighten the failing color, on light backgrounds darken it
- Stay within the palette family, don't invent a new color, adjust the existing one
- Re-run `hyperframes check` until clean

Use `--no-contrast` only while iterating, and `--snapshots` to persist the five audited frames as PNGs under `snapshots/`.

### Animation Map

After authoring animations, run the bundled `scripts/animation-map.mjs` (see Bundled Scripts below). Its `animation-map.json` holds per-tween summaries, an ASCII timeline, stagger intervals, dead zones over 1s, element lifecycles, snapshots at 5 timestamps, and the flags `offscreen`, `collision`, `invisible`, `paced-fast` (under 0.2s) and `paced-slow` (over 2s). Check every flag, fix or justify it, and re-run after fixes. Skip it on small edits; run it on new compositions and significant animation changes.

---

## References (loaded on demand)

- **[references/captions.md](references/captions.md)**, Captions, lyrics and karaoke synced to audio: style detection, per-word styling, overflow, exits, grouping. Read for any text synced to audio.
- **[references/tts.md](references/tts.md)**, Text-to-speech with Kokoro-82M. Voice selection, speed tuning, TTS+captions workflow. Read when generating narration or voiceover.
- **[references/audio-reactive.md](references/audio-reactive.md)**, Map frequency bands and amplitude to GSAP properties.
- **[references/css-patterns.md](references/css-patterns.md)**, CSS+GSAP marker highlighting: highlight, circle, burst, scribble, sketchout. Deterministic, fully seekable. Read when adding visual emphasis to text.
- **[references/typography.md](references/typography.md)**, Typography: font pairing, OpenType features, dark-background adjustments, font discovery script. **Always read**, every composition has text.
- **[references/motion-principles.md](references/motion-principles.md)**, Easing, timing, choreography, pacing and anti-patterns. Read when choreographing GSAP animations.
- **[visual-styles.md](visual-styles.md)**, 8 named visual styles (Swiss Pulse, Velvet Standard, Deconstructed, Maximalist Type, Data Drift, Soft Signal, Folk Frequency, Shadow Cut) with hex palettes, GSAP easing signatures, and shader pairings. Read when user names a style or when generating DESIGN.md.
- **[house-style.md](house-style.md)**, Default motion, sizing, and color palettes when no style is specified.
- **[patterns.md](patterns.md)**, PiP, title cards, slide show patterns.
- **[data-in-motion.md](data-in-motion.md)**, Data, stats, and infographic patterns.
- **[references/transcript-guide.md](references/transcript-guide.md)**, Transcription commands, whisper models, external APIs, troubleshooting.
- **[references/dynamic-techniques.md](references/dynamic-techniques.md)**, Dynamic caption animation techniques (karaoke, clip-path, slam, scatter, elastic, 3D).
- **[references/hebrew-rtl.md](references/hebrew-rtl.md)**, Hebrew and RTL compositions: `dir="rtl"` scoping, declaring Heebo/Rubik/Assistant with a Google Fonts `<link>`, GSAP x-axis mirroring, Hebrew captions via `hyperframes transcribe --language he`, Hebrew voiceover via external TTS, bidirectional text with `<bdi>`. Read for any composition with Hebrew text.

- **[references/transitions.md](references/transitions.md)**, Scene transitions: crossfades, wipes, reveals, shader transitions. Energy/mood selection, CSS vs WebGL guidance. **Always read for multi-scene compositions**, scenes without transitions feel like jump cuts.
  - [transitions/catalog.md](references/transitions/catalog.md), Hard rules, scene template, and routing to per-type implementation code.
  - Shader transitions are in `@hyperframes/shader-transitions` (`packages/shader-transitions/`), read package source, not skill files.

For GSAP timeline patterns and easing, follow [house-style.md](./house-style.md) and [references/motion-principles.md](references/motion-principles.md) in this skill, plus the official GSAP docs at https://gsap.com/docs/v3/.

## Bundled Scripts

`scripts/` holds two Node tools vendored from upstream at `d94708e` (`animation-map.mjs` with its helper `animation-map-sampling.mjs`, `contrast-report.mjs`, and the shared `package-loader.mjs`). Run them from the project root and point at the skill folder; they resolve `@hyperframes/producer`, `@hyperframes/core` and `sharp` from your working directory first. A fresh `hyperframes init` project has no `node_modules`, so install them first; if one is missing the script stops and prints the exact `npm install` line. Unlike upstream, this copy never spawns an install itself.

```bash
# Portrait (TikTok / Reels). BOTH scripts default to a 1920x1080 viewport, so a
# portrait composition MUST be given --width/--height.
npm install --save-dev @hyperframes/producer@"$(npx hyperframes --version)" @hyperframes/core@"$(npx hyperframes --version)" sharp
node <skill-dir>/scripts/animation-map.mjs . --width 1080 --height 1920 --out .hyperframes/anim-map
node <skill-dir>/scripts/contrast-report.mjs . --width 1080 --height 1920 --samples 10 --out .hyperframes/contrast
```

Both also accept `--fps` (default 30). Match it to your render, and set `data-fps` on the composition root if you are not rendering at 30.

| Script | What it does |
|---|---|
| `scripts/animation-map.mjs` | Enumerates every tween in `window.__timelines`, samples bounding boxes, and emits `animation-map.json` with per-tween summaries, an ASCII timeline, stagger detection, dead zones and flags. |
| `scripts/contrast-report.mjs` | WCAG 2.2 audit with a `contrast-overlay.png` sprite grid (magenta fails AA, yellow AA only, green AAA, grey unmeasured), which `check` does not produce; `check` stays the gate. Exits 1 on an AA failure, 3 when text could not be measured (unparseable color, transparent backdrop), never passing it. Its verdicts matched `check` on the cases in `scripts/test/contrast-report.regression.mjs`. |

Both require Node 22+ (the producer package declares `"engines": { "node": ">=22" }`).

## Gotchas

These are agent failure modes specific to Hebrew/RTL HyperFrames work. Generic HyperFrames gotchas (see upstream) still apply.

- **Declare every Hebrew font with a Google Fonts `<link>`; don't rely on a bare `font-family: 'Heebo'`.** No Hebrew family is pre-bundled. A bare family still renders locally, because the compiler fetches it (`packages/core/src/fonts/deterministicFonts.ts`), but lint raises `font_family_without_font_face` at severity error, and that error stops `npx hyperframes check` before its browser session, so the contrast, layout and motion passes never run (measured on 0.8.138). The `<link>` is lint-clean, and the compiler fetches exactly the linked weights at build time (as it fetches a bare family) and injects deterministic `@font-face` rules. Lint checks each file alone, so every sub-composition that names a Hebrew family needs its own `@import` at the top of the `<style>` inside its `<template>` (a sub-composition's `<head>` is discarded). Details in references/hebrew-rtl.md.
- **Don't reach for the built-in `hyperframes tts` command for Hebrew narration.** It is local-only, described upstream as "Generate speech audio from text using a local AI model (Kokoro-82M)", and its arguments are exactly `input, text-file, output, voice, speed, lang, list, json`. There is no provider argument, so no environment variable can make this command speak Hebrew. Kokoro maps 9 locales via voice-ID prefix, `a`=American English, `b`=British English, `e`=Spanish, `f`=French, `h`=Hindi, `i`=Italian, `j`=Japanese, `p`=Brazilian Portuguese, `z`=Mandarin. Hebrew is not among them. Two paths that do work: (a) the media-use audio engine, whose automatic order is HeyGen Starfish, then ElevenLabs (needs `ELEVENLABS_API_KEY` **and** the `elevenlabs` Python module importable), then local Kokoro, plus Gemini TTS as an explicit `"provider": "gemini"` with `"lang": "he"` (Google lists Hebrew for its 3.8 TTS models). `hyperframes doctor` checks only the Kokoro dependencies, so it cannot show the cloud pick. (b) Generate the WAV/MP3 with any external service (ElevenLabs, OpenAI TTS, Google Cloud TTS Hebrew) and drop the file into the composition as a normal `<audio>` clip. Path (b) is the one that works with no account and no Python deps.
- **Always pass `--language he` to `transcribe`.** The default model is `small.en`, and without `--language` the CLI forces English, so a Hebrew file comes back as English text. With `--language he` the CLI swaps any `.en` model for its multilingual twin, and `--engine auto` falls back to Whisper because Parakeet has no Hebrew. Use `npx hyperframes transcribe audio.wav --model medium --language he` (`small` is weak for Hebrew ASR; `large-v3` for noisy audio). **`references/captions.md` is upstream text and prescribes a flat `--model small`; for Hebrew that rule is superseded by this one**, because per-word effects (karaoke, slam, marker sweep) key off word boundaries that `small` gets wrong.
- **Don't forget `dir="rtl"` on Hebrew text containers and on each sub-composition's own root.** A sub-composition inherits the host's direction in the full render, but not when that file is rendered or snapshotted alone. GSAP `x:` tweens also don't auto-mirror. A title that uses `gsap.from({x: -80})` enters from the left in both LTR and RTL, for Hebrew, flip to `x: 80` so it enters from the right, matching reading direction.
- **Don't "fix" a Hebrew entrance because `animation-map.mjs` says it moves the wrong way.** The map describes motion from screen-space bounding-box deltas, with no notion of writing direction. In an RTL composition a correct Hebrew entrance, `gsap.from(".subtitle", { x: 80 })` so the text flies in from the right, is reported as moving left (for example `moves 32px left`; the pixel figure varies with sampling). That prose is accurate about pixels and misleading about intent. Read the summaries for choreography and flags, not for direction, and never flip a tween's sign to make the wording read "right".
- **Hebrew narration over a music bed: group the voices, then generate the carve.** Put only the voiceover clips in an audio group (`data-audio-group="voiceover"`); never the music, SFX or the bed itself. The bed is ducked by a carve, but a hand-written `data-fx-carve` does nothing: upstream says the carve's own settings "are never read at playback", only the `data-fx-chain` and `data-automation` it generates play. Generate it with Studio's carve module or upstream's `skills/hyperframes-audio/scripts/carve.mjs --comp index.html`, and confirm both attributes were written before rendering. Without either, put a `data-automation` volume lane on the bed. Loudness: `npx hyperframes normalize-audio --target <element-id> --lufs -16 --write` (`--target` is the clip id; `--lufs` defaults to -16).
- **Don't paste English brand names into Hebrew paragraphs without `<bdi>` or `unicode-bidi: isolate`.** Without isolation, the Unicode bidi algorithm reorders mixed-direction runs and can place punctuation on the wrong side of the brand name or visually reverse it. Wrap brand names: `הצטרפו ל־<bdi>HyperFrames</bdi> עכשיו`.

## Hebrew Bidi Details

A bare digit run needs no wrapper (`2025` beside Hebrew stays left-to-right, it does NOT become `5202`). A digit touching a symbol, range or Latin token does: `<bdi>15%</bdi> הנחה`, `<bdi>₪199</bdi>`, `<bdi>10-20</bdi>`. Never hand-swap `(` and `)`; a `dir="rtl"` container mirrors them. Line-breaking and punctuation details are in references/hebrew-rtl.md.

## Troubleshooting

### `hyperframes` command not found / render fails immediately
HyperFrames requires Node 22+ and FFmpeg on PATH. Confirm `node --version` is 22 or higher and `ffmpeg -version` resolves. On macOS install FFmpeg with `brew install ffmpeg`; on Debian/Ubuntu use `apt install ffmpeg`. Without FFmpeg the compiler cannot encode the MP4 and aborts before rendering any frames.

### Lint reports `font_family_without_font_face`, or Hebrew renders in a fallback font
Hebrew families are not pre-bundled, so each must be declared. Add a Google Fonts `<link rel="stylesheet">` (or `@import`) naming the family and weights, e.g. `family=Heebo:wght@400;800`, and keep `font-family: 'Heebo', sans-serif;` in the CSS. The lint message says text "will fall back to a generic font", but on a local 0.8.138 render a real Google family was still embedded; the real cost is that the error stops `check` early. A fallback face in the MP4 means a misspelled family or a failed fetch; a licensed non-Google face needs your own `@font-face` pointing at a project file.

### WCAG contrast audit fails (`hyperframes check`)
`check` samples background pixels behind each text element in five audited frames and fails on ratios under 4.5:1 (normal text) or 3:1 (large text). Fix by adjusting the failing color WITHIN the palette family: brighten it on dark backgrounds, darken it on light backgrounds. Do not invent a new color. Re-run `hyperframes check` until clean. Use `--no-contrast` only while iterating, never as the final state.

### Composition renders blank or content is invisible
**If the composition is Hebrew and it previews fine but the MP4 is black, check `<html>` for a `dir` attribute first.** `<html dir="rtl">` or `dir="auto"` can produce a blank render while preview and snapshot look correct; remove it, keep `lang`, and scope `dir="rtl"` to the text-bearing elements instead. `npx hyperframes check` reports this as `html_dir_attribute_breaks_render` at severity error. Otherwise, the most common cause is a `<template>` wrapper on a standalone composition. The main `index.html` must put the `data-composition-id` div directly in `<body>`, not inside `<template>`. Also check that every timeline is registered via `window.__timelines["<composition-id>"] = tl` and that an async build registers its key only after adding its tweens (`gsap_timeline_registered_before_async_build`); an empty timeline registered early renders blank.

### Hebrew title enters from the wrong side
GSAP `x:` tweens do not auto-mirror. Flip the sign (`x: 80`, entering from the right); directional transitions are covered in `references/hebrew-rtl.md`.

## Reference Links

| Source | URL | What to Check |
|---|---|---|
| HyperFrames GitHub | https://github.com/heygen-com/hyperframes | Upstream repo, issues, releases |
| HyperFrames docs | https://hyperframes.heygen.com/quickstart | CLI, Node 22+, FFmpeg requirement |
| Compiler font logic | https://github.com/heygen-com/hyperframes/blob/main/packages/core/src/fonts/deterministicFonts.ts | Bundled font list, Google Fonts fetch, cache path |
| Composition contract | https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-core/references/data-attributes.md | Current `data-*` attributes, `class="clip"`, required fields |
| Kokoro TTS voices | https://github.com/heygen-com/hyperframes/blob/main/skills/media-use/audio/references/tts.md | Kokoro voice prefixes across 9 locales (no Hebrew) |
| Whisper model guide | https://github.com/skills-il/developer-tools/blob/master/hyperframes-best-practices/references/transcript-guide.md | `.en` vs multilingual models, `--language` flag |
| Google Fonts Hebrew | https://fonts.google.com/?subset=hebrew | Heebo, Rubik, Assistant, Alef, Frank Ruhl Libre, Noto Sans Hebrew |
| Unicode bidi spec | https://developer.mozilla.org/en-US/docs/Web/CSS/unicode-bidi | `isolate`, `<bdi>`, mixed-direction text |
