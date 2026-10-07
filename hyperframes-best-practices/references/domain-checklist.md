# Domain checklist: Hebrew/RTL adaptation layer over HyperFrames

**Scope.** This skill is an adaptation layer, not a fork. It sits over
`heygen-com/hyperframes` (anchored at `d94708e`, release **v0.8.138**, 2026-10-06; previous cycle `4f00336`, v0.8.15) and its job is (a) to carry
the parts of the upstream contract an agent will get wrong if it improvises, and (b) to supply the
Hebrew/RTL knowledge upstream **does not have at all**.

That second half is not a figure of speech. An exhaustive grep of the upstream tree
(`docs/`, `packages/*/src`, `skills/`, `registry/`) returns:

| Term | Real hits upstream |
|---|---|
| `hebrew` | **0** (only false positives inside base64 font blobs) |
| `bidi` | 2, both comments in `packages/lint/src/rules/composition.ts:846,865` |
| `rtl` | the `html_dir_attribute_breaks_render` lint rule; a `ltr\|rtl` sweep-direction *variable* in `registry/blocks/weight-wave`; 2 Studio comments |
| `i18n` | 0 conceptual hits |
| Hebrew font in `CANONICAL_FONTS` | 0 of 18 (only non-Latin is `noto-sans-jp`) |

So every Hebrew item below is load-bearing: there is no upstream doc to fall back on.

Category: `developer-tools`. Hosts declared: `claude-code, cursor, windsurf, github-copilot,
opencode, codex, chatgpt, claude-ai, claude-desktop, manus`.

---

## 1. Must cover (core)

An item is "Must" when omitting it causes a **wrong decision, a lint error, or a silently broken
render**.

### 1.1 Upstream contract

| # | Item | Upstream source that makes it core |
|---|---|---|
| M1 | **`<html dir="rtl">` (or `dir="auto"`) must NEVER be set.** Upstream documents that it previews and snapshots correctly but can render a fully blank/black MP4, with the undersized output file as the only tell. Keep `lang`, scope `direction: rtl` / `dir="rtl"` to text-containing elements. On 0.8.138 a local test render recovered (the renderer flagged a "suspect small frame" at frame 0 and re-captured), so the blank output is no longer guaranteed, but the rule stands and `render` blocks on it only with `--strict`. | `packages/lint/src/rules/composition.ts:1138-1168`, rule `html_dir_attribute_breaks_render`, **severity `error`**, "a confirmed, silent failure"; `packages/cli/src/commands/render.ts:270-279` (`--strict`) |
| M2 | Composition anatomy: root `data-composition-id` + `data-width`/`data-height`; `data-start` is what makes an element a clip; visibility window is half-open `[start, start+duration)`. | `skills/hyperframes-core/references/data-attributes.md` |
| M3 | `class="clip"` on visible timed elements, a convention the runtime ignores but the scaffold's shared `.clip { position:absolute; inset:0 }` rule depends on for a full-frame scene box, and lint warns without it. Omit on `<video>`/`<audio>`. | `skills/hyperframes-core/references/data-attributes.md:25`; lint code `timed_element_missing_clip_class` |
| M4 | `data-track-index` is a Studio display lane only; the render never reads it, and neither it nor legacy `data-layer` constrains timing or z-order. | `skills/hyperframes-core/references/data-attributes.md`; lint `deprecated_data_layer` |
| M5 | GSAP timeline contract: one `gsap.timeline({paused:true})` per composition, registered at `window.__timelines[compositionId]`, never `tl.play()`, duration from `data-duration`. | `skills/hyperframes-core/references/determinism-rules.md`; lint `gsap_timeline_registered_before_async_build` |
| M6 | Determinism ban list: `Date.now()`, `performance.now()`, unseeded `Math.random()`, `requestAnimationFrame`, render-time network fetches for required assets, hover/scroll/pointer state. | `determinism-rules.md`; lint `non_deterministic_code`, `requestanimationframe_in_composition`, `base64_media_prohibited` |
| M7 | **Finite repeats computed with `Math.floor`, not `Math.ceil`**: `repeat: Math.max(0, Math.floor(total / cycle) - 1)`. `Math.ceil(x) - 1` overshoots the composition duration and is itself a lint finding. | `packages/lint/src/rules/gsap.ts:1563-1583`, rule `gsap_repeat_ceil_overshoot`, fixHint spells out floor; and `gsap_infinite_repeat` for `repeat: -1` |
| M8 | Standalone `index.html` must NOT wrap the composition in `<template>`; only `data-composition-src` sub-compositions do. | lint `standalone_composition_wrapped_in_template` |
| M9 | Media: silent footage and b-roll are `muted playsinline`; footage whose own sound you want keeps it with `data-has-audio="true"`; voiceover, music and replacement audio are separate `<audio>` elements, each with an `id`. Never nest a timed video inside another timed plain element; the framework owns playback. | `skills/hyperframes-core/references/variables-and-media.md:69`; lint `video_missing_muted`, `media_missing_id` |
| M10 | Root duration source: `data-duration` is read **once at compile time** and cannot be changed by script or `--variables`. There is no `--duration` render flag. Required outright for Three.js / infinite-CSS / no-animation-signal roots. | `packages/cli/src/commands/render/plan.ts`; lint `root_composition_missing_duration_source` |
| M11 | Host toolchain: **Node >= 22**, FFmpeg on PATH, and a **Puppeteer-managed `chrome-headless-shell`** that the CLI auto-downloads into its cache. Everything the skill instructs is a shell command. | `packages/cli/package.json:76`, `packages/producer/package.json:119`, `packages/cli/src/browser/manager.ts:45` (`PUPPETEER_CACHE_DIR`) |
| M12 | `check` is the gate (`lint` + runtime + layout + motion + WCAG contrast in one browser session, `--samples` default **9**), `--strict` to gate warnings; `validate`, `inspect` and `layout` remain only as compatibility aliases. | `packages/cli/src/commands/check.ts:44-112`; `skills/hyperframes-cli/SKILL.md:69` |
| M13 | `render` output surface: `--format mp4\|webm\|mov\|gif\|png-sequence\|hls`, `--resolution` presets (`portrait` 1080x1920, `landscape` 1920x1080, `square`, 4k variants; aspect must match the composition), `--quality draft\|looks\|delivery` (default `looks`, CRF 16), `--crf` XOR `--video-bitrate`, `--fps` resolving explicit → root `data-fps` → **default 30**, `--strict` / `--strict-all` to block on lint. | `packages/cli/src/commands/render.ts:151-185, 227-236, 270-279, 320-323` |
| M14 | Font resolution: 18 bundled families embed with no declaration. Any other family must be declared (Google Fonts `<link>`/`@import`, or an own `@font-face`), or lint raises `font_family_without_font_face` at severity error, which also stops `check` before its browser session. A declared Google family is fetched at build time (exactly the linked weights) and injected as deterministic base64 `@font-face` rules, cached at `~/.cache/hyperframes/fonts/<slug>/<weight>-<style>-<subset>.woff2`. An undeclared real Google family still embeds on a local render (measured), but upstream documents that implicit path as fail-closed in distributed renders. | `packages/core/src/fonts/deterministicFonts.ts:1083, 1099-1134, 1499, 1630`; `packages/lint/src/rules/fonts.ts:191-221`; `skills/hyperframes-creative/references/typography.md:3`; upstream commit `918e39e78` (embed the linked Google font) |

### 1.2 Hebrew / RTL

| # | Item | Source that makes it core |
|---|---|---|
| M15 | **Hebrew glyph coverage is a hard font-selection constraint.** Not one of the 18 canonical fonts has a Hebrew subset. Any font-picking guidance in this skill must filter on the Google Fonts `hebrew` subset, not the `latin` subset, or the composition renders tofu/fallback. | `packages/core/src/fonts/deterministicFonts.ts:397` (`CANONICAL_FONTS`); Google Fonts metadata `subsets[]` at `https://fonts.google.com/metadata/fonts` |
| M16 | Per-subset `unicode-range` is preserved and the disk cache is keyed by subset (`cachedWoff2Path(slug, weight, style, subset)`). A Google family with a Hebrew subset gets that subset fetched and injected, which is why a declared `<link>` for Heebo renders Hebrew glyphs. | `packages/core/src/fonts/deterministicFonts.ts:1133-1134` |
| M17 | Scoping direction the sanctioned way: `dir="rtl"` on the composition root `<div>` and on individual text containers, never on `<html>`. A sub-composition's `<template>` contents are cloned into the host DOM, so it inherits the host direction in the full render; it still needs `dir="rtl"` on its own root for standalone render/snapshot. | M1; `skills/hyperframes-core/references/sub-compositions.md:26-35` |
| M18 | GSAP `x`/`xPercent`/`translateX` do not mirror for RTL. Hebrew entrances use positive `x` (from the right); exits mirror too. Applies equally to wipe/push transitions and to caption sweeps. | No upstream mirroring exists, `registry/blocks/weight-wave`'s `ltr\|rtl` variable is the only direction switch in the tree, and it reverses a sweep index, not text |
| M19 | Bidi isolation for mixed runs: `<bdi>` / `unicode-bidi: isolate` around Latin brand names, URLs, and any digit adjacent to a symbol/range (`15%`, `₪199`, `10-20`). Bare integers need no wrapper. Mirrored characters (`()[]""`) must be left to the browser, never hand-swapped. | UAX #9 (Unicode Bidirectional Algorithm), rules X5a-c and BD16; MDN `unicode-bidi`. Upstream contributes nothing (2 comment hits) |
| M20 | Hebrew captions: always pass `--language he`. The default model is `small.en`; without `--language` the CLI forces English. With a non-English `--language` the CLI swaps any `.en` model for its multilingual twin before download, and `--engine auto` falls back to Whisper because Parakeet's language list has no `he`. Word-level timestamps land in `transcript.json`, which a caption composition must embed inline as `var TRANSCRIPT = [...]` (a `fetch()` is the lint error `caption_transcript_not_inline`). | `packages/cli/src/whisper/manager.ts:10`; `packages/cli/src/whisper/transcribe.ts:425-431, 487-488`; `packages/cli/src/whisper/parakeet.ts:31-38`; `packages/lint/src/rules/captions.ts:69-100` |
| M21 | **No Hebrew voice in the CLI's own TTS.** `hyperframes tts` is local-only Kokoro-82M with no provider argument; 9 phonemizer locales, none Hebrew. Hebrew narration comes from the media-use audio engine with Gemini (explicit `"provider": "gemini"`, added upstream 2026-09-24; Google lists Hebrew for its 3.8 TTS models) or from any external service imported as an `<audio>` clip. `doctor` checks only the Kokoro deps and cannot show which cloud provider the engine would pick. | `packages/cli/src/commands/tts.ts:43-82`; `packages/cli/src/tts/manager.ts:23-33`; `skills/media-use/audio/references/tts.md:115-186`; `packages/cli/src/commands/doctor.ts:388-389`; ai.google.dev/gemini-api/docs/speech-generation |
| M22 | Hebrew has no hyphenation and no case. Line-breaking must be word-boundary-only via `max-width`; `<br>` is banned by the layout rules; and any rule phrased as "ALL CAPS", `.toUpperCase()`, or small-caps is a **no-op** on Hebrew and must not be presented as a Hebrew emphasis mechanism. | Unicode: Hebrew block U+05D0-U+05EA is caseless (no `Lu`/`Ll` pairs); `determinism-rules.md` layout section bans `<br>` |
| M23 | Host-executability statement. Every gate in this skill (`check`, `render`, `transcribe`, `normalize-audio`, `node scripts/*.mjs`) is a shell invocation against a local Node 22 + FFmpeg + Chromium install. On `chatgpt`, `claude-ai`, `claude-desktop`, and `manus` there is no shell, so the skill's happy path terminates at "author the HTML" and every verification step is unreachable. This must be stated, not implied. | M11's toolchain requirements + the declared `supported_agents` list in `metadata.json` |
| M24 | **A lint error silences the rest of `check`.** When lint reports an error, `check` prints "Browser session never ran" and its runtime, layout, motion and contrast sections are empty placeholders, not a clean pass. Hebrew-specific triggers: an undeclared Hebrew font (M14), a fetched transcript (M20). | measured on 0.8.138 (`check` exit 1, `0/0 text checks`); `packages/cli/src/commands/check.ts:411` |
| M25 | Asset paths are root-relative everywhere, sub-compositions included; `../` is the lint error `invalid_parent_traversal_in_asset_path`. `crossorigin` on `<video>`/`<audio>` is the lint error `media_crossorigin_breaks_preview`. A timed `<video>` needs `muted` or `data-has-audio="true"` (`video_missing_muted`). | `packages/lint/src/rules/composition.ts:639-703`; `packages/lint/src/rules/media.ts:514-545, 745-770`; `skills/hyperframes-core/references/variables-and-media.md:69` |
| M26 | Portrait scaffolding: `init --resolution portrait` sets html, body, viewport and root together; editing only `data-width`/`data-height` leaves a 1920x1080 body that clips the frame, and lint only warns (`root_dimensions_mismatch`). Directional transitions written in landscape pixels must use `xPercent`/`yPercent` in portrait. | `packages/cli/src/commands/init.ts:747-750`; `packages/lint/src/rules/core.ts:511-545` |
| M27 | Fonts are declared per composition file: lint checks each `compositions/*.html` alone and a sub-composition's `<head>` is discarded, so a sub-composition naming a Hebrew family needs an `@import` inside its `<template>` `<style>` (measured on 0.8.138). | `packages/lint/src/project.ts:222-229`; `skills/hyperframes-core/references/sub-compositions.md:26-35` |
| M28 | Half-open visibility window `[start, start+duration)`: final tweens must end slightly before `data-duration`. Determinism lint errors also cover `new Date()`, `performance.now()`, `gsap.utils.random()` and `requestAnimationFrame`. | `skills/hyperframes-core/references/data-attributes.md:41`; `packages/lint/src/rules/core.ts:903-951`; `packages/lint/src/rules/composition.ts:1040` |

---

## 2. Should cover (advanced)

| # | Item | Source |
|---|---|---|
| S1 | Text measurement: `window.__hyperframes.fitTextFontSize(text, {maxWidth, baseFontSize, minFontSize, fontWeight, fontFamily, step})` returns `{fontSize, fits}`. For Hebrew the `fontFamily` passed **must be the Hebrew face actually rendering**, or the measurement is taken against Latin metrics and the fit is wrong. | `determinism-rules.md` layout section |
| S2 | Registry: `npx hyperframes add <name>` installs blocks (`compositions/<name>.html`) and components (`compositions/components/<name>.html`); `npx hyperframes catalog` (with `--type`, `--tag`, `--json`) discovers them. **Names and tags are English, so search in English even for a Hebrew video.** | `registry/registry.json` (164 blocks, 222 components, 8 examples at `d94708e`); `packages/cli/src/commands/{add,catalog}.ts` |
| S3 | Preview + Studio: `npx hyperframes preview` (`--port 3002`, `--background`, `--status`, `--stop`) serves the Studio editor. Upstream's CLI workflow expects a preview URL handed to the user before render. | `packages/cli/src/commands/preview.ts`; `docs/studio/index.mdx:22` |
| S4 | Non-GSAP seek-safe runtimes (CSS keyframes, WAAPI, Anime.js, Lottie, Three.js, TypeGPU) and their per-runtime duration inference; Three.js is not inferable and forces `data-duration`. | `skills/hyperframes-animation/adapters/*.md`; `determinism-rules.md` § "Duration Contract For Non-GSAP Runtimes" |
| S5 | Shader transitions are declared in **JS**, `init({bgColor, accentColor, scenes, transitions, timeline})` from `@hyperframes/shader-transitions`, not by an attribute or component. 13 shaders in the registry; graceful non-WebGL fallback. | `packages/shader-transitions/{index.ts,shaders/registry.ts}`; `docs/packages/shader-transitions.mdx` |
| S6 | Audio mixing: group only the voice clips (`data-audio-group`), then generate the bed's carve with Studio or upstream `skills/hyperframes-audio/scripts/carve.mjs`; a hand-written `data-fx-carve` is never read at playback, only the `data-fx-chain` / `data-automation` it writes play. Fallback: a `data-automation` volume lane on the bed. `normalize-audio --target <element-id> --lufs <LUFS> --write` (`--lufs` default -16). | `skills/hyperframes-audio/SKILL.md:117-119, 222-275`; `packages/cli/src/commands/normalize-audio.ts:249-263` |
| S7 | Remaining clip attributes an author will meet: `data-media-start`, `data-volume` (max 3.98 ≈ +12 dB), `data-playback-rate` (0.1-5, constant), `data-hidden`, `data-has-audio`, `data-no-timeline`, and the layout escape hatches `data-layout-allow-overflow` / `-ignore` / `-bleed` / `-allow-caption-zone`. | `skills/hyperframes-core/references/data-attributes.md` |
| S8 | Composition variables: `data-composition-variables` on `<html>`, `data-variable-values` / `data-var-src` / `data-var-text` on sub-composition hosts; `render --variables` / `--variables-file` / `--strict-variables` / `--batch`. Relevant for HE/EN dual-cut renders from one composition. | `data-attributes.md`; `packages/cli/src/commands/render.ts` |
| S9 | Caption gates: `check --caption-zone "x0=..;y0=..;x1=..;y1=..;severity=error;seek=.."` raises `caption_zone_collision` for NON-caption text in the band (content under `[data-composition-id="captions"]`, `.caption-layer`, `#caption-stage` is exempt) and checks only the last frame unless `seek` lists more; `data-layout-allow-caption-zone` exempts intentional lower-thirds; `data-track-kind="captions"` marks the caption track (`caption_track_kind_missing`). Captions' own clearance from platform UI is checked by eye. | `packages/cli/src/commands/check.ts:113-117`; `packages/cli/src/commands/layout-audit.browser.js:1777`; `packages/cli/src/utils/checkPipeline.ts:149-151`; `packages/lint/src/rules/structure.ts:148-158` |
| S10 | Hebrew typographic detail at video scale: negative tracking is hostile to Hebrew (no ascender/descender rhythm to absorb it; `ר`/`ד`, `ב`/`כ`, `ה`/`ח` collide); weights 100-200 disintegrate at caption sizes; nikud, when present, needs extra `line-height` or it clips against the line above. | Typographic property of the Hebrew script; no upstream guidance exists (see §1 grep table) |
| S11 | Custom/local Hebrew fonts (a licensed foundry face, e.g. for brand work) are supported by authoring your own `@font-face` with a local or hosted file, `@font-face`-scoped declarations are deliberately skipped by the font normalizer, plus `fontLocalize.ts` for publishable bundles. | `packages/core/src/fonts/deterministicFonts.ts:136` (`isFontFaceDeclaration`); `packages/cli/src/fontLocalize.ts` |
| S12 | `hyperframes doctor --json` **always exits 0**, gate on the `.ok` field in the payload, not the exit code. | `packages/cli/src/commands/doctor.ts` |
| S13 | Distributed / hosted rendering: `hyperframes lambda` (`packages/aws-lambda`, Step Functions + CDK), `hyperframes cloudrun` (`packages/gcp-cloud-run`, Workflows + Terraform), `hyperframes cloud` (HeyGen-hosted). `--docker` for byte-deterministic renders. | `docs/deploy/{overview,aws-lambda,gcp-cloud-run,cloud}.mdx` |
| S14 | Caption placement for portrait Hebrew social: bottom-band positioning, one group visible at a time, a deterministic `tl.set` kill at `group.end`, and `overflow: visible` so scaled emphasis words are not clipped. | `skills/embedded-captions/references/rail.md`; `packages/lint/src/rules/captions.ts` |

---

S4 (non-GSAP runtimes) and S13 (distributed rendering) stay checklist-only as of 2026-10-07: neither is needed for a single Hebrew Reel, and the upstream adapters and `packages/aws-lambda` / `packages/gcp-cloud-run` docs are the authority. S8 is covered for the Hebrew/English dual cut in references/hebrew-rtl.md. Distributed renders matter for fonts only in that the implicit Google-font fetch is fail-closed there (M14), which the per-file declaration rule (M27) already avoids.

## 3. Out of scope (explicit)

Named so a reviewer does not score their absence as a gap.

| Item | Why out |
|---|---|
| Remotion / any React-based video | The skill's own description routes there to `remotion-best-practices`. Upstream `skills/remotion-to-hyperframes/` is a one-way migration aid, not this skill's job |
| FFmpeg-level editing, libass/`subtitles=` burn-in, SRT/ASS styling | HyperFrames has **no** burn-in path; captions are DOM elements composited by the normal render. Belongs to `video-use-best-practices` |
| Talking-head recut, matte occlusion, 35-identity caption catalog | Whole separate upstream skill, `skills/embedded-captions/` (138 files) + `skills/talking-head-recut/` |
| Sourcing media (BGM, SFX, stock, logos, background removal) | `skills/media-use/` (152 files), the "Agent Media OS" |
| Authoring new registry blocks/components upstream | `skills/hyperframes-registry/`; contributing upstream is not an adaptation-layer concern |
| Arabic, Persian, Urdu RTL | Hebrew has no cursive joining and no contextual shaping; Arabic-script shaping is a materially different problem and claiming coverage would be worse than declining it |
| Hebrew NLP (nikud restoration, morphological analysis, ktiv male normalization) | Text-preparation concern upstream of the composition; not video |
| Lambda/Cloud Run infrastructure provisioning | `packages/aws-lambda`, `packages/gcp-cloud-run` ship their own CDK/Terraform and docs |
| Kokoro voice tuning beyond "it has no Hebrew" | Once M21 establishes Hebrew is absent, Kokoro voice/speed selection is an English-narration concern |

---

## 4. Authoritative sources

**Upstream repo**, `github.com/heygen-com/hyperframes` @ `d94708e`, release **v0.8.138**.

| What | Path |
|---|---|
| Composition + `data-*` contract | `skills/hyperframes-core/references/data-attributes.md` |
| Determinism, duration contract, layout rules | `skills/hyperframes-core/references/determinism-rules.md` |
| **The RTL footgun** | `packages/lint/src/rules/composition.ts:1138-1168` (`html_dir_attribute_breaks_render`, severity `error`) |
| Repeat-count rule | `packages/lint/src/rules/gsap.ts:1563-1583` (`gsap_repeat_ceil_overshoot`) |
| All 98 lint codes | `packages/lint/src/rules/{core,composition,media,gsap,fonts,captions,adapters,slideshow,textures}.ts` |
| Font resolution + embedding + subset cache | `packages/core/src/fonts/deterministicFonts.ts` (moved from `packages/producer/src/services/` in `b3d2b82fe`, 2026-10-05) |
| Canonical font bytes | `packages/core/src/fonts/fontData.generated.ts` |
| CLI command registry (40 commands) | `packages/cli/src/cli.ts:120-162` |
| Render flags + resolution presets | `packages/cli/src/commands/render.ts`, `render/plan.ts`, `utils/renderArgs.ts` |
| `check` flags | `packages/cli/src/commands/check.ts:41-126` |
| Transcript / word-timestamp schema | `packages/cli/src/whisper/normalize.ts:4-12` |
| Animation adapters + CSS transition families | `skills/hyperframes-animation/` |
| Shader transitions API | `packages/shader-transitions/index.ts`, `shaders/registry.ts` |
| Audio attributes | `skills/hyperframes-audio/references/attributes.md` |
| Registry + config schema | `registry/registry.json`, `docs/schema/hyperframes.json` |
| HTML schema reference | `docs/reference/html-schema.mdx` |
| Node / browser requirements | `packages/cli/package.json:76`, `packages/producer/package.json:119`, `packages/cli/src/browser/manager.ts` |

**External (nothing upstream covers these):**

| What | Source |
|---|---|
| Bidirectional algorithm, isolates, mirroring | UAX #9, `https://www.unicode.org/reports/tr9/` |
| `<bdi>`, `unicode-bidi`, `dir` | MDN, `https://developer.mozilla.org/en-US/docs/Web/CSS/unicode-bidi` |
| Hebrew-subset font availability | `https://fonts.google.com/?subset=hebrew` and the machine-readable `https://fonts.google.com/metadata/fonts` (`subsets[]` contains `"hebrew"`) |
| Hebrew block is caseless | Unicode Character Database, `UnicodeData.txt`, U+05D0-U+05EA general category `Lo` |
| WCAG 2.1 contrast thresholds (4.5:1 / 3:1) | `https://www.w3.org/TR/WCAG21/#contrast-minimum` |
| External Hebrew TTS voices | ElevenLabs multilingual; Google Cloud `he-IL-Wavenet-*` / `he-IL-Standard-*`; OpenAI `tts-1` |
