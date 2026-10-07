# Hebrew and RTL

HyperFrames handles most of the HTML-to-video pipeline for English out of the box. Hebrew adds four concerns: font loading, text direction, animation mirroring, and the missing Hebrew TTS.

## Fonts

**Declare the Hebrew family with a Google Fonts `<link>` in `<head>`, naming the weights you use.**

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;800&display=swap" />
```

None of the 18 pre-bundled families (inter, roboto, montserrat, outfit, nunito, oswald, league-gothic, archivo-black, space-mono, ibm-plex-mono, jetbrains-mono, eb-garamond, playfair-display, source-code-pro, noto-sans-jp, open-sans, lato, poppins) covers Hebrew, so every Hebrew family goes through the Google Fonts path in `packages/core/src/fonts/deterministicFonts.ts`. Two ways in, measured on HyperFrames 0.8.138 with a 1080x1920 Hebrew composition:

| What you write | Lint / `check` | Render |
|---|---|---|
| `font-family: 'Heebo'` only | **Error** `font_family_without_font_face`, whose message says text "will fall back to a generic font". `check` then stops before its browser session, so contrast, layout and motion never run | A local render still fetches Heebo (9 faces) and embeds it. Upstream documents this implicit path as fail-closed in distributed/cloud renders: if Google is unreachable the render errors |
| A Google Fonts `<link>` (or `@import`) for the family | Clean | The compiler fetches exactly the linked weights (2 faces for `wght@400;800`), caches the WOFF2s under `~/.cache/hyperframes/fonts/heebo/`, and injects deterministic base64 `@font-face` rules that win over the stylesheet |

Either way the compiler fetches the font from Google at build time (`render` compiles first, so a cold cache needs network); the `<link>` adds no further dependency, because the deterministic faces win over the stylesheet. It is simply the declaration the compiler and the linter both read.

**Every composition file declares its own fonts.** Lint checks each `compositions/*.html` on its own, and a sub-composition's `<head>` is discarded when it is mounted. So a caption or scene sub-composition that names a Hebrew family carries an `@import` at the top of the `<style>` inside its `<template>`:

```html
<template>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Heebo:wght@400;800&display=swap");
    #root { position: absolute; inset: 0; font-family: "Heebo", sans-serif; }
  </style>
  ...
</template>
```

Measured on 0.8.138: without that `@import` the sub-composition raises `font_family_without_font_face` even when `index.html` has the `<link>`; with it lint is clean and the render embeds Heebo. The lint message's "will fall back" is wrong for a real Google family on a local render, but the error itself is real and it disables the rest of `check`. A licensed non-Google Hebrew face needs your own `@font-face` pointing at a file in the project.

### Hebrew Google Fonts that work

All resolve through the Google Fonts path once declared:

| Family | Character | When to reach for it |
|---|---|---|
| Heebo | Modern sans, widest weight range (100-900) | Default body + display in 2020s Israeli brand videos |
| Rubik | Geometric rounded sans | Product, fintech, startup copy |
| Assistant | Clean contemporary sans | Utility UI, dashboards, technical content |
| Alef | Condensed, high contrast | Editorial headlines, Hebrew-first publications |
| Frank Ruhl Libre | Modernized traditional serif | Long-form, editorial, prestige |
| Noto Sans Hebrew | Neutral pan-Unicode sans | Mixed-script, accessibility fallback |

First compile fetches the WOFF2s; subsequent runs hit the local cache.

### Weight contrast

Hebrew display letterforms carry less visual weight than equivalent Latin glyphs at the same `font-weight`. Where the upstream typography rules call for 300 vs 900 weight contrast, Hebrew benefits from 400 vs 900. Very light Hebrew (100-200) breaks up at video sizes, avoid it for anything smaller than a headline.

## Direction

Set `dir="rtl"` explicitly on Hebrew text containers. **Never set `dir` on the `<html>` element.** `<html dir="rtl">` and `<html dir="auto">` preview correctly and can render a fully blank black MP4; upstream flags it as the severity-`error` lint rule `html_dir_attribute_breaks_render`. Keep `lang="he"` there and scope direction downward. A sub-composition (loaded via `data-composition-src`) has its `<template>` contents cloned into the host DOM, so it inherits the host's direction in the full render; put `dir="rtl"` on its own root anyway, because a standalone render or snapshot of that file has no RTL ancestor.

```html
<div data-composition-id="hero" data-width="1920" data-height="1080" dir="rtl">
  <div class="scene-content">
    <h1 class="title">כותרת בעברית</h1>
    <p class="subtitle">תת-כותרת מסבירה</p>
  </div>
  <style>
    .scene-content {
      display: flex;
      flex-direction: column;
      justify-content: center;
      width: 100%;
      height: 100%;
      padding: 120px 160px;
      gap: 24px;
      box-sizing: border-box;
      font-family: 'Heebo', sans-serif;
    }
    .title { font-size: 120px; font-weight: 900; }
    .subtitle { font-size: 42px; font-weight: 400; }
  </style>
</div>
```

Apply `dir="rtl"` to each Hebrew text element when the composition also carries English runs, don't rely on the container. Caption tracks specifically need per-word `dir="rtl"` because word spans are injected dynamically.

## GSAP x-axis mirroring

GSAP tweens do not auto-mirror for RTL. A title animated with `gsap.from('.title', { x: -80, opacity: 0 })` enters from the left in both LTR and RTL layouts. For Hebrew, flip the sign so the entrance matches reading direction:

```js
// Latin (LTR): title enters from left
tl.from('.title', { x: -80, opacity: 0, duration: 0.6, ease: 'power3.out' }, 0);

// Hebrew (RTL): title enters from right
tl.from('.title-he', { x: 80, opacity: 0, duration: 0.6, ease: 'power3.out' }, 0);
```

Same rule for `xPercent`, `translateX` in keyframes, and wipe transitions. Exits mirror too: a Latin title that exits to the right with `x: 40` exits to the left for Hebrew with `x: -40`.

**Directional transitions.** The catalog's push, slide and cover transitions are written in landscape pixels (`x: 1920`, `y: 1080`). In a 1080x1920 Reel those literals are wrong: `x: 1920` overshoots and a vertical push from `y: 1080` starts the incoming scene already on screen. Rewrite them with `xPercent` / `yPercent` (100 or -100). For Hebrew, a horizontal push follows reading direction: the incoming scene enters from the left (`xPercent: -100` to 0) while the outgoing one leaves to the right, the mirror of the LTR template. This is a reading-direction convention, not an upstream rule; pick one direction and keep it for the whole video.

Rotation, scale, and y-axis tweens are direction-agnostic, leave them alone.

## Captions

Always pass `--language he`. With it, the CLI swaps an English-only `.en` model for its multilingual twin before downloading (`initialModelForLanguage`, so `--model small.en --language he` actually runs `small`), and `--engine auto` falls back to Whisper because Parakeet's language list has no Hebrew. Without `--language`, the default model `small.en` forces English and a Hebrew file comes back as English text.

```bash
# Default Hebrew caption pipeline (small is weak on Hebrew word boundaries)
npx hyperframes transcribe narration-he.wav --model medium --language he

# Noisy audio or a music bed
npx hyperframes transcribe narration-he.wav --model large-v3 --language he

# Scaffolding a new portrait project straight from the voiceover
npx hyperframes init promo --resolution portrait --audio narration-he.wav --language he --model medium
```

**Hebrew transcript QA before you inline it.** Whisper's Hebrew word boundaries feed every per-word effect directly, and upstream's fragment repair (`mergeFragments` in `packages/cli/src/whisper/normalize.ts`) only knows Latin patterns. If you have the script the voiceover was read from, diff the transcript words against it and fix spelling while keeping each word's `start`/`end`; check that prefix letters (ו, ה, ב, ל, מ, ש, כ) are not split off as separate words; and look for zero- or near-zero-duration words, which flash in karaoke captions.

`transcribe` writes `transcript.json`. The caption composition must carry that data inline as `var TRANSCRIPT = [...]`: a caption composition that `fetch()`es the file is a lint error (`caption_transcript_not_inline`), which also stops `check` before its browser session. Mark the caption element `data-track-kind="captions"`; lint flags caption-like rows without it (`caption_track_kind_missing`).

**Reels safe zones.** Instagram and TikTok draw their own UI over the bottom band (caption, username) and a vertical action rail on the right edge, and Hebrew text, which anchors to the right, runs into that rail first. The exact sizes change with the apps, so treat any fixed margin as a rule of thumb and check against a current screenshot of the target app. Give Hebrew text containers more inline-start (right) padding than left.

`--caption-zone` gates the OTHER text, not the captions. It reserves a band for captions and fails headlines, prices and CTAs that intrude into it; content inside `[data-composition-id="captions"]`, `.caption-layer` or `#caption-stage` is exempt (`packages/cli/src/commands/layout-audit.browser.js`). So use it to keep non-caption text out of the bottom band, and check the captions' own position against the platform UI by eye in `preview`:

```bash
npx hyperframes check --strict --caption-zone "x0=0;y0=.8;x1=1;y1=1;severity=error;seek=.05,.15,.25,.35,.45,.55,.65,.75,.85,.95"
```

The band (fractions of the frame) is an example; size it to the platform. The `seek` list (fractions of the duration) matters: by default the band is checked only at the last frame (`seek=1`). Measured on 0.8.138 with a 30-second composition: a headline visible from 1s to 4s inside the band passed without `seek` and failed at t=1.5s with it; the same text inside a composition with id `captions` was not checked at all. Add the midpoint of any short-lived element the spacing would miss, and mark an intentional lower-third with `data-layout-allow-caption-zone`.

For caption rendering, wrap the word span with `dir="rtl"` and choose a highlight animation that reads right-to-left. The upstream `references/captions.md` marker-sweep patterns work for Hebrew, mirror the GSAP sweep direction so the highlighter moves right-to-left across the word group.

```html
<div class="caption" dir="rtl">
  <span class="caption-word">שלום</span>
  <span class="caption-word">עולם</span>
</div>
```

```js
// Mirror the sweep direction for Hebrew
tl.fromTo('.caption-word.highlight', { '--sweep': '100%' }, { '--sweep': '0%', duration: 0.3 });
```

Word-level timestamps produce better Hebrew captions than phrase-level SRT/VTT, per-word animation effects (karaoke, slam, scatter) depend on accurate word boundaries.

## Voiceover

The built-in `npx hyperframes tts` command is local-only (no provider argument) and uses Kokoro-82M, which does not support Hebrew. `npx hyperframes doctor` checks only the local Kokoro dependencies, so it cannot tell you which cloud voice the media-use engine would pick. It also always exits 0; gate scripts on the `.ok` field of `doctor --json`. Kokoro's 9 phonemizer locales encode in the voice-ID first letter: `a`=American English, `b`=British English, `e`=Spanish, `f`=French, `h`=Hindi, `i`=Italian, `j`=Japanese, `p`=Brazilian Portuguese, `z`=Mandarin.

Two routes for Hebrew voiceover:

1. **The upstream media-use audio engine with Gemini.** Upstream added Gemini TTS on 2026-09-24 as an explicit provider (it is not in the automatic HeyGen, ElevenLabs, Kokoro order). Google's Gemini speech-generation language table lists Hebrew for both `gemini-3.8-flash-tts` and `gemini-3.8-flash-lite-tts`. Put `"provider": "gemini"` and `"lang": "he"` in `audio_request.json`; per upstream, Gemini infers the spoken language from the text and `lang` selects the transcription language for the word timings it writes to `audio_meta.json`. It needs `GEMINI_API_KEY` or `GOOGLE_API_KEY` (or a service account).
2. **Any external service**, with the file imported as a normal `<audio>` clip:

| Provider | Hebrew support | Notes |
|---|---|---|
| ElevenLabs | Multiple Hebrew voices (male/female) | Highest quality, cloud API with per-character pricing |
| OpenAI TTS | Hebrew via `tts-1` / `tts-1-hd` multilingual voices | Works but phonemization is uneven on rare words |
| Google Cloud TTS | `he-IL-Standard-*` and `he-IL-Wavenet-*` voices | Good baseline; check list for current voice names |

After generating the file, place it in the composition like any other audio asset:

```html
<audio
  id="narration-he"
  data-start="0"
  data-duration="30"
  data-track-index="2"
  src="narration-he.wav"
  data-volume="1"
></audio>
```

Then run `hyperframes transcribe` against the generated file to produce word-level timestamps for captions.

## Hebrew and English cuts from one composition

To ship a Hebrew and an English version of the same video, declare the swappable text as composition variables (`data-composition-variables` on `<html>`, bound with `data-var-text`) and render each cut with `render --variables` or `--variables-file`; see upstream `skills/hyperframes-core/references/variables-and-media.md`. Direction does not swap by itself: set `dir` on the text containers for each locale, and mirror the GSAP `x` values as described above.

## Bidirectional text

Hebrew copy frequently mixes in Latin-script brand names, URLs, product names, and numbers. Without isolation, the Unicode bidi algorithm reorders runs and can place punctuation on the wrong side of the Latin token.

Wrap Latin runs with `<bdi>` or apply `unicode-bidi: isolate` via CSS:

```html
<!-- Hebrew paragraph with an English brand name -->
<p dir="rtl">הצטרפו ל־<bdi>HyperFrames</bdi> עכשיו.</p>

<!-- Hebrew with mixed URL -->
<p dir="rtl">הקוד בכתובת <bdi>github.com/heygen-com/hyperframes</bdi>.</p>
```

```css
/* CSS alternative if you can't modify the markup */
.brand { unicode-bidi: isolate; }
```

A **bare** integer in Hebrew context is handled correctly by the bidi algorithm and displays left-to-right inside an RTL paragraph without any wrapper. A digit touching a symbol is not: a percent sign, a currency sign, a range dash or an adjacent Latin token can detach and land on the wrong side, so prices and percentages DO need isolation. Write `<bdi>₪199</bdi>`, `<bdi>15%</bdi>`, `<bdi>10-20</bdi>`.

**Line-breaking.** Hebrew does not hyphenate. Set `max-width` so a long headline wraps at word boundaries, which the browser already does for Hebrew (`word-break: keep-all` changes CJK breaking, not Hebrew). Never force breaks with `<br>`; for a deliberate one-word-per-line title, give each word its own element.

**Punctuation mirroring.** Parentheses, brackets and quotes are mirrored characters: `(` displays as `)` in an RTL run. Keep the text in a proper `dir="rtl"` container and let the browser mirror them; never hand-swap `(` and `)`. When a parenthetical holds LTR content (a brand, a URL, a number), wrap only that inner content in `<bdi>`.

## Quick checklist

Before rendering a Hebrew composition:

1. Root `<div data-composition-id>` has `dir="rtl"` (or the text containers do).
2. The Hebrew family is declared with a Google Fonts `<link>` (or `@import`) and `npx hyperframes lint` shows no `font_family_without_font_face`.
3. GSAP entrance x-values are positive (entering from the right) for Hebrew elements.
4. Mixed-script runs use `<bdi>` or `unicode-bidi: isolate`.
5. Audio narration file exists; it was generated externally (not via `hyperframes tts`).
6. Transcribe command passed `--language he` (and a multilingual `--model`, `medium` or larger), and the caption composition holds the transcript inline as `var TRANSCRIPT = [...]`.
7. Caption spans have `dir="rtl"` and any marker-sweep animation runs right-to-left.
