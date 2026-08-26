# Domain checklist: Hebrew/RTL adaptation layer over HyperFrames

**Scope.** This skill is an adaptation layer, not a fork. It sits over
`heygen-com/hyperframes` (anchored at `4f00336`, release **v0.8.15**) and its job is (a) to carry
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
| M1 | **`<html dir="rtl">` (or `dir="auto"`) must NEVER be set.** It previews and snapshots correctly but renders a fully blank/black MP4, with the undersized output file as the only tell. Keep `lang`, scope `direction: rtl` / `dir="rtl"` to text-containing elements. | `packages/lint/src/rules/composition.ts:838-871`, rule `html_dir_attribute_breaks_render`, **severity `error`**, "a confirmed, silent failure". Tests `composition.test.ts:1332-1384` |
| M2 | Composition anatomy: root `data-composition-id` + `data-width`/`data-height`; `data-start` is what makes an element a clip; visibility window is half-open `[start, start+duration)`. | `skills/hyperframes-core/references/data-attributes.md` |
| M3 | `class="clip"` on visible timed elements, a convention the runtime ignores but the scaffold's shared `.clip { position:absolute; inset:0 }` rule depends on for a full-frame scene box, and lint warns without it. Omit on `<video>`/`<audio>`. | `skills/hyperframes-core/references/data-attributes.md:25`; lint code `timed_element_missing_clip_class` |
| M4 | `data-track-index` is a Studio display lane only; the render never reads it, and neither it nor legacy `data-layer` constrains timing or z-order. | `skills/hyperframes-core/references/data-attributes.md`; lint `deprecated_data_layer` |
| M5 | GSAP timeline contract: one `gsap.timeline({paused:true})` per composition, registered at `window.__timelines[compositionId]`, never `tl.play()`, duration from `data-duration`. | `skills/hyperframes-core/references/determinism-rules.md`; lint `gsap_timeline_registered_before_async_build` |
| M6 | Determinism ban list: `Date.now()`, `performance.now()`, unseeded `Math.random()`, `requestAnimationFrame`, render-time network fetches for required assets, hover/scroll/pointer state. | `determinism-rules.md`; lint `non_deterministic_code`, `requestanimationframe_in_composition`, `base64_media_prohibited` |
| M7 | **Finite repeats computed with `Math.floor`, not `Math.ceil`**: `repeat: Math.max(0, Math.floor(total / cycle) - 1)`. `Math.ceil(x) - 1` overshoots the composition duration and is itself a lint finding. | `packages/lint/src/rules/gsap.ts:1563-1583`, rule `gsap_repeat_ceil_overshoot`, fixHint spells out floor; and `gsap_infinite_repeat` for `repeat: -1` |
| M8 | Standalone `index.html` must NOT wrap the composition in `<template>`; only `data-composition-src` sub-compositions do. | lint `standalone_composition_wrapped_in_template` |
| M9 | Video is `muted playsinline` + a separate `<audio>` element; never nest video in a timed element; framework owns playback. | lint `video_nested_in_timed_element`, `media_missing_data_start`, `media_crossorigin_breaks_preview` |
| M10 | Root duration source: `data-duration` is read **once at compile time** and cannot be changed by script or `--variables`. There is no `--duration` render flag. Required outright for Three.js / infinite-CSS / no-animation-signal roots. | `packages/cli/src/commands/render/plan.ts`; lint `root_composition_missing_duration_source` |
| M11 | Host toolchain: **Node >= 22**, FFmpeg on PATH, and a **Puppeteer-managed `chrome-headless-shell`** that the CLI auto-downloads into its cache. Everything the skill instructs is a shell command. | `packages/cli/package.json:76`, `packages/producer/package.json:119`, `packages/cli/src/browser/manager.ts:45` (`PUPPETEER_CACHE_DIR`) |
| M12 | `check` is the gate (`lint` + runtime + layout + motion + WCAG contrast in one browser session, `--samples` default **9**); `validate` and `layout` are marked deprecated in favour of `check`; `inspect` and `lint` are NOT deprecated and remain live commands. | `packages/cli/src/commands/check.ts:41-126`; `validate.ts` and `layout.ts` carry `deprecated: true`, `inspect.ts` carries no deprecation marker; `packages/cli/src/cli.ts:120-162` |
| M13 | `render` output surface: `--format mp4\|webm\|mov\|gif\|png-sequence`, `--resolution` presets (`portrait` 1080x1920, `landscape` 1920x1080, `square`, 4k variants), `--quality draft\|standard\|high`, `--crf` XOR `--video-bitrate`, `--fps` resolving explicit → root `data-fps` → **default 30**. | `packages/cli/src/commands/render.ts:120-282`, `utils/renderArgs.ts:258-275`, `render/plan.ts:184-222` |
| M14 | Font resolution: 18 canonical `@fontsource` families are pre-embedded; anything else goes to `fetchGoogleFont()` → Google CSS2 API with a Chrome UA → woff2 → base64 `@font-face` data URI, cached at `~/.cache/hyperframes/fonts/<slug>/<weight>-<style>-<subset>.woff2`. A 4xx (family absent from Google's catalog) silently falls back to the CSS stack. Never add `<link>` or `@import`. | `packages/producer/src/services/deterministicFonts.ts:335-408, 727-736, 1065-1140`; lint `font_family_without_font_face`, `system_font_will_alias` |

### 1.2 Hebrew / RTL

| # | Item | Source that makes it core |
|---|---|---|
| M15 | **Hebrew glyph coverage is a hard font-selection constraint.** Not one of the 18 canonical fonts has a Hebrew subset. Any font-picking guidance in this skill must filter on the Google Fonts `hebrew` subset, not the `latin` subset, or the composition renders tofu/fallback. | `deterministicFonts.ts:335-408` (`CANONICAL_FONTS`); Google Fonts metadata `subsets[]` at `https://fonts.google.com/metadata/fonts` |
| M16 | Per-subset `unicode-range` is preserved and the disk cache is keyed by `subsetToken(weight x style x unicode-range)`. A Google family with a Hebrew subset gets that subset fetched and injected automatically, this is *why* declaring `font-family: 'Heebo'` works at all, and it is incidental, not designed. | `deterministicFonts.ts:487-489, 757-768` |
| M17 | Scoping direction the sanctioned way: `dir="rtl"` on the composition root `<div>` and on individual text containers, never on `<html>`. Sub-compositions loaded via `data-composition-src` establish their own direction context and do not inherit. | M1's fixHint; `skills/hyperframes-core/references/data-attributes.md` (sub-composition host attrs) |
| M18 | GSAP `x`/`xPercent`/`translateX` do not mirror for RTL. Hebrew entrances use positive `x` (from the right); exits mirror too. Applies equally to wipe/push transitions and to caption sweeps. | No upstream mirroring exists, `registry/blocks/weight-wave`'s `ltr\|rtl` variable is the only direction switch in the tree, and it reverses a sweep index, not text |
| M19 | Bidi isolation for mixed runs: `<bdi>` / `unicode-bidi: isolate` around Latin brand names, URLs, and any digit adjacent to a symbol/range (`15%`, `₪199`, `10-20`). Bare integers need no wrapper. Mirrored characters (`()[]""`) must be left to the browser, never hand-swapped. | UAX #9 (Unicode Bidirectional Algorithm), rules X5a-c and BD16; MDN `unicode-bidi`. Upstream contributes nothing (2 comment hits) |
| M20 | Hebrew captions must use a **multilingual** Whisper/Parakeet model with `--language he`. `.en` variants translate rather than transcribe. Word-level timestamps are the `{id, text, start, end}` shape in `transcript.json`. | `packages/cli/src/commands/transcribe.ts`; `packages/cli/src/whisper/normalize.ts:4-12` |
| M21 | **Hebrew TTS does not exist in the toolchain.** `hyperframes tts` is local-only Kokoro-82M with no provider argument; 9 phonemizer locales, none Hebrew; the CLI bundles 12 voices across 6 of them. Hebrew narration must be produced externally and imported as an `<audio>` clip. | `packages/cli/src/commands/tts.ts` (args: `input, --text-file, --output, --voice, --speed, --lang, --list, --json`); `skills/media-use/audio/references/tts.md` |
| M22 | Hebrew has no hyphenation and no case. Line-breaking must be word-boundary-only via `max-width`; `<br>` is banned by the layout rules; and any rule phrased as "ALL CAPS", `.toUpperCase()`, or small-caps is a **no-op** on Hebrew and must not be presented as a Hebrew emphasis mechanism. | Unicode: Hebrew block U+05D0-U+05EA is caseless (no `Lu`/`Ll` pairs); `determinism-rules.md` layout section bans `<br>` |
| M23 | Host-executability statement. Every gate in this skill (`check`, `render`, `transcribe`, `normalize-audio`, `node scripts/*.mjs`) is a shell invocation against a local Node 22 + FFmpeg + Chromium install. On `chatgpt`, `claude-ai`, `claude-desktop`, and `manus` there is no shell, so the skill's happy path terminates at "author the HTML" and every verification step is unreachable. This must be stated, not implied. | M11's toolchain requirements + the declared `supported_agents` list in `metadata.json` |

---

## 2. Should cover (advanced)

| # | Item | Source |
|---|---|---|
| S1 | Text measurement: `window.__hyperframes.fitTextFontSize(text, {maxWidth, baseFontSize, minFontSize, fontWeight, fontFamily, step})` returns `{fontSize, fits}`. For Hebrew the `fontFamily` passed **must be the Hebrew face actually rendering**, or the measurement is taken against Latin metrics and the fit is wrong. | `determinism-rules.md` layout section |
| S2 | Registry: `npx hyperframes add <name>` installs blocks (`compositions/<name>.html`) and components (`compositions/components/<name>.html`); `npx hyperframes catalog --query "<english>"` discovers them. **The catalog index is English-only, query in English even for a Hebrew video.** | `registry/registry.json` (154 blocks, 218 components, 9 examples); `packages/cli/src/commands/{add,catalog}.ts`; `docs/schema/hyperframes.json` |
| S3 | Preview + Studio: `npx hyperframes preview` (`--port 3002`, `--background`, `--status`, `--stop`) serves the Studio editor. Upstream's CLI workflow expects a preview URL handed to the user before render. | `packages/cli/src/commands/preview.ts`; `docs/studio/index.mdx:22` |
| S4 | Non-GSAP seek-safe runtimes (CSS keyframes, WAAPI, Anime.js, Lottie, Three.js, TypeGPU) and their per-runtime duration inference; Three.js is not inferable and forces `data-duration`. | `skills/hyperframes-animation/adapters/*.md`; `determinism-rules.md` § "Duration Contract For Non-GSAP Runtimes" |
| S5 | Shader transitions are declared in **JS**, `init({bgColor, accentColor, scenes, transitions, timeline})` from `@hyperframes/shader-transitions`, not by an attribute or component. 13 shaders in the registry; graceful non-WebGL fallback. | `packages/shader-transitions/{index.ts,shaders/registry.ts}`; `docs/packages/shader-transitions.mdx` |
| S6 | Audio mixing surface: `data-audio-group` (audio clips only, ignored on `<video>`), `data-fx-chain` JSON node graph, `data-automation` lanes, `<hf-audio-group>` busses, `hyperframes normalize-audio --reference --target --tolerance`. Attribute JSON must be `&quot;`-escaped. | `skills/hyperframes-audio/references/attributes.md`; `packages/cli/src/commands/normalize-audio.ts` |
| S7 | Remaining clip attributes an author will meet: `data-media-start`, `data-volume` (max 3.98 ≈ +12 dB), `data-playback-rate` (0.1-5, constant), `data-hidden`, `data-has-audio`, `data-no-timeline`, and the layout escape hatches `data-layout-allow-overflow` / `-ignore` / `-bleed` / `-allow-caption-zone`. | `skills/hyperframes-core/references/data-attributes.md` |
| S8 | Composition variables: `data-composition-variables` on `<html>`, `data-variable-values` / `data-var-src` / `data-var-text` on sub-composition hosts; `render --variables` / `--variables-file` / `--strict-variables` / `--batch`. Relevant for HE/EN dual-cut renders from one composition. | `data-attributes.md`; `packages/cli/src/commands/render.ts` |
| S9 | `check --caption-zone` and the `captions.ts` lint family (overflow/fit/exit) as the caption-specific gate. | `packages/lint/src/rules/captions.ts`; `check.ts:41-126` |
| S10 | Hebrew typographic detail at video scale: negative tracking is hostile to Hebrew (no ascender/descender rhythm to absorb it; `ר`/`ד`, `ב`/`כ`, `ה`/`ח` collide); weights 100-200 disintegrate at caption sizes; nikud, when present, needs extra `line-height` or it clips against the line above. | Typographic property of the Hebrew script; no upstream guidance exists (see §1 grep table) |
| S11 | Custom/local Hebrew fonts (a licensed foundry face, e.g. for brand work) are supported by authoring your own `@font-face` with a local or hosted file, `@font-face`-scoped declarations are deliberately skipped by the font normalizer, plus `fontLocalize.ts` for publishable bundles. | `deterministicFonts.ts:106-110` (`isFontFaceDeclaration`), `:710` (error hint); `packages/cli/src/fontLocalize.ts` |
| S12 | `hyperframes doctor --json` **always exits 0**, gate on the `.ok` field in the payload, not the exit code. | `packages/cli/src/commands/doctor.ts` |
| S13 | Distributed / hosted rendering: `hyperframes lambda` (`packages/aws-lambda`, Step Functions + CDK), `hyperframes cloudrun` (`packages/gcp-cloud-run`, Workflows + Terraform), `hyperframes cloud` (HeyGen-hosted). `--docker` for byte-deterministic renders. | `docs/deploy/{overview,aws-lambda,gcp-cloud-run,cloud}.mdx` |
| S14 | Caption placement for portrait Hebrew social: bottom-band positioning, one group visible at a time, a deterministic `tl.set` kill at `group.end`, and `overflow: visible` so scaled emphasis words are not clipped. | `skills/embedded-captions/references/rail.md`; `packages/lint/src/rules/captions.ts` |

---

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

**Upstream repo**, `github.com/heygen-com/hyperframes` @ `4f00336`, release **v0.8.15**.

| What | Path |
|---|---|
| Composition + `data-*` contract | `skills/hyperframes-core/references/data-attributes.md` |
| Determinism, duration contract, layout rules | `skills/hyperframes-core/references/determinism-rules.md` |
| **The RTL footgun** | `packages/lint/src/rules/composition.ts:838-871` (`html_dir_attribute_breaks_render`, severity `error`) |
| Repeat-count rule | `packages/lint/src/rules/gsap.ts:1563-1583` (`gsap_repeat_ceil_overshoot`) |
| All 98 lint codes | `packages/lint/src/rules/{core,composition,media,gsap,fonts,captions,adapters,slideshow,textures}.ts` |
| Font resolution + embedding + subset cache | `packages/producer/src/services/deterministicFonts.ts` |
| Canonical font bytes | `packages/producer/src/services/fontData.generated.ts` |
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
