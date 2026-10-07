# Changelog

## 1.3.0 - 2026-10-07

Validated against upstream heygen-com/hyperframes @ d94708e (release v0.8.138, 2026-10-06), 1,247 commits after the previous anchor. Every behavioural claim below was either read in upstream source or measured on a 1080x1920 Hebrew test composition with the 0.8.138 CLI.

### Fixed

- **Hebrew font guidance was inverted.** The skill said never to add a Google Fonts `<link>` and to write a bare `font-family: 'Heebo'`. That form raises the lint error `font_family_without_font_face`, and a lint error stops `hyperframes check` before its browser session, so contrast, layout and motion never ran on any Hebrew composition that followed the skill. A `<link>` is lint-clean, and the compiler embeds exactly the linked weights as deterministic `@font-face` rules. Rewritten in SKILL.md, SKILL_HE.md, references/hebrew-rtl.md, typography.md, transitions/catalog.md and the domain checklist.
- The compiler font module moved from `packages/producer/src/services/` to `packages/core/src/fonts/deterministicFonts.ts`; the Reference Link 404'd.
- `transcribe` now swaps any `.en` model for its multilingual twin when `--language` is non-English. The real trap is omitting `--language he`, since the default `small.en` then forces English. Gotcha, hebrew-rtl.md and transcript-guide.md updated.
- `hyperframes doctor` checks only the local Kokoro dependencies; the claim that it shows which TTS engine would be picked was wrong.
- Data Attributes re-synced to upstream `hyperframes-core`: `data-track-index` is not required, `id` is required on media (an id-less `<audio>` renders silent), `img` defaults to 3s, `data-volume` goes to 3.98, new `data-has-audio`, `data-fps`, and the `class="clip"` convention (prior-cycle carry).
- Video with its own sound keeps it via `data-has-audio="true"`; the old "always muted video plus separate audio" rule was stale.
- Async timeline builds are supported; the rule is to register `window.__timelines[id]` last. `repeat: -1` is a lint error only without a finite root `data-duration`.
- `crossorigin` on media is now a lint error, and `../` asset paths are a lint error; the skill recommended both.
- Audio mixing: group only the voices, and duck the bed with a generated carve (see below), instead of grouping voice and music together.
- `check` contrast failures are errors with a suggested color, not warnings. Output Checklist now says "0 errors", explains that a lint error silences the other passes, and renders with `--strict`.
- **Bundled scripts re-vendored from upstream `d94708e`** (`animation-map.mjs`, `animation-map-sampling.mjs`, `contrast-report.mjs`, `package-loader.mjs`). The old `contrast-report.mjs` sampled a 4px ring outside each text box, so a dark caption on a blue pill read 1.21:1 against the surround instead of its real 2.08:1. The scripts now resolve packages from the project and can bootstrap them (`HYPERFRAMES_SKILL_BOOTSTRAP_DEPS=1`), so they no longer need copying into the project.
- `scripts/contrast-report.mjs` skills-il changes on top of upstream: WCAG 2.2 luminance threshold 0.04045; large bold text from 14pt (18.67px) instead of 19px; it lifts the capture pipeline's transparent-background override for its sampling screenshot, so solid, gradient, semi-transparent and html-level page backgrounds are measured as rendered (light text on a white body had been measured against black and passed at 13.08:1, real 1.61:1); it resolves non-rgb() colors such as Tailwind v4's oklch() through a canvas instead of reading them as black; and it skips text under a hidden ancestor. On four test compositions it now reports the same ratios as `check`.
- Voice-over-music: a hand-written `data-fx-carve` is never read at playback; the carve must be generated (Studio or upstream `carve.mjs`). `normalize-audio --target` is the element id and `--lufs` the loudness.
- Fonts are declared per composition file: a sub-composition needs its own `@import` inside its `<template>` (measured). `references/captions.md` gained the matching Hebrew rule.
- Determinism list extended (`new Date()`, `performance.now()`, `requestAnimationFrame`, `gsap.utils.random()`); half-open visibility window documented; sub-composition template re-synced to upstream (no per-file GSAP load, portrait, `dir`, font `@import`).
- `contrast-report.mjs` never passes what it cannot measure: an unresolvable color or a transparent backdrop is reported UNMEASURED (grey in the overlay) and the script exits 3. `scripts/test/contrast-report.regression.mjs` covers solid, gradient, semi-transparent, class-set, html-only, image and no-background pages.
- The repeat-count formula now rounds the division before flooring and counts from the time left after the tween's start offset, including `repeatDelay`.
- `--caption-zone` documented for what it does: it fails non-caption text in the caption band (caption compositions are exempt) and checks only the last frame unless given a `seek` list (measured on a 30-second composition).
- Output Checklist: `preview` before `check --strict`; Reels safe-zone gate with `--caption-zone` and a Hebrew transcript QA step in references/hebrew-rtl.md (both carried since 1.1.1).
- `references/transitions/css-push.md` re-vendored: upstream added `opacity: 1` to every push to-vars (#4314).
- The `<html dir>` blank-render rule is kept, but no longer claimed to be guaranteed: a local 0.8.138 render of such a file recovered after a "suspect small frame" re-capture.
- Sub-compositions inherit the host's direction (template contents are cloned into the host DOM); the old "they set their own direction context" rationale was wrong. `dir="rtl"` on the sub-composition root is still advised for standalone renders.

### Added

- Gemini TTS (explicit `"provider": "gemini"`, Hebrew listed by Google) as a Hebrew voiceover route through the media-use audio engine.
- Portrait scaffolding (`init --resolution portrait`), render output flags, registry (`catalog`, `add`), inline `var TRANSCRIPT` requirement, `init --audio --language he`, and RTL plus portrait handling for directional transitions (prior-cycle carries).
- SKILL_HE.md now carries the Data Attributes tables, the four Scene Transitions rules and the Output Checklist (carried three cycles).
- Bundled Scripts install step: a fresh `init` project has no `node_modules`.

### Changed

- The Layout Before Animation worked example moved to `references/layout-before-animation.md` to stay under the 5,000-word cap.

## 1.2.1 - 2026-08-26

Citation corrections in `references/domain-checklist.md`, found by the Independent Judge re-verifying every cited path and line against upstream @ 4f00336.

### Fixed

- Row M12 listed `inspect` among the commands deprecated in favour of `check`. `validate.ts` and `layout.ts` do carry `deprecated: true`; `inspect.ts` carries no deprecation marker and `inspect` is a live command. Corrected.
- Row S2 cited `registry.json` as 154 blocks and 219 components. It parses to 154 blocks, 218 components and 9 examples.
- Row M11 cited `browser/manager.ts:191` for the chrome-headless-shell auto-download; line 191 is a type export. The substantive line is 45 (`PUPPETEER_CACHE_DIR`).

## 1.2.0 - 2026-08-26

Validated against upstream heygen-com/hyperframes @ 4f00336 (release v0.8.15, 2026-08-26).

### Fixed

- `hyperframes validate` is deprecated upstream in favour of `hyperframes check`, which runs lint, runtime, layout, motion and the WCAG contrast pass in one browser session. Updated the Output Checklist, the Contrast section and both Troubleshooting entries in EN and HE. `lint` is not deprecated and stays.
- The animation-map invocation pointed at `skills/hyperframes/scripts/animation-map.mjs`, a path that does not exist upstream (it is `skills/hyperframes-animation/scripts/`). Corrected in SKILL.md and in both bundled scripts' own usage headers.
- Kokoro was described as supporting "8 languages" while listing nine. Upstream's `SUPPORTED_LANGS` tuple holds nine locales. Corrected in six places across SKILL.md, SKILL_HE.md, references/tts.md and references/hebrew-rtl.md.
- `data-track-index` was documented as "same-track clips cannot overlap". It is a Studio display lane; upstream's linter states that neither it nor `data-layer` is read by the render. Removed the false constraint.
- The claim that `$ELEVENLABS_API_KEY` makes `hyperframes tts` route to ElevenLabs is wrong: the command is local-only and has no provider argument. The HeyGen Starfish, then ElevenLabs, then Kokoro order belongs to the media-use audio path. Rewritten in EN and HE.
- Kokoro TTS reference link 404'd (`skills/hyperframes-media/...`); the file lives at `skills/media-use/audio/references/tts.md`.
- `references/tts.md` claimed `tts --list` shows "54 voices (8 languages)". The CLI bundles 12 voices covering 6 of the 9 locales.
- GSAP pin moved 3.15.0 to 3.14.2 to match the version upstream scaffolds into `templates/blank/index.html`, so a composition does not end up loading two GSAP builds.
- `fitTextFontSize` returns `{ fontSize, fits }`, not a number.

### Added

- `## Bundled Scripts` (EN + HE): both scripts import `@hyperframes/producer`, which Node resolves relative to the script file, so they must be copied into the project before they run. Verified by executing both end to end against a 1080x1920 Hebrew RTL composition. `contrast-report.mjs` was previously undocumented.
- Gotcha: `animation-map.mjs` describes motion in screen space, so a correct Hebrew entrance (`x: 80`, entering from the right) is reported as "moves left". Measured, not inferred.
- Gotcha: audio groups (`data-audio-group`), the summed FX bus (`data-fx-chain`) and `hyperframes normalize-audio` for layering Hebrew narration over a music bed.
- `hyperframes transcribe --engine` (auto/parakeet/whisper) noted alongside the existing `.en`-model warning.

## 1.1.2 - 2026-08-19

### Fixed

- Translated section headings that had been left in English in SKILL_HE.md, where they rendered as-is on the Hebrew page. Hebrew is the site's default locale, and the skill validator never checked the Hebrew file, so these went unnoticed.

