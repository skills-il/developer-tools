# Hebrew and RTL

HyperFrames handles most of the HTML-to-video pipeline for English out of the box. Hebrew adds four concerns: font loading, text direction, animation mirroring, and the missing Hebrew TTS.

## Fonts

**Do NOT add a Google Fonts `<link rel="stylesheet">` tag or a CSS `@import url(...)` statement for Hebrew fonts.**

The compiler already resolves non-canonical `font-family` values through `fetchGoogleFont()` in `packages/producer/src/services/deterministicFonts.ts`. When your composition CSS sets `font-family: 'Heebo'`, the compiler:

1. Checks its 18-font canonical list (no Hebrew fonts are bundled, inter, roboto, montserrat, outfit, nunito, oswald, league-gothic, archivo-black, space-mono, ibm-plex-mono, jetbrains-mono, eb-garamond, playfair-display, source-code-pro, noto-sans-jp, open-sans, lato, poppins).
2. Falls through to `fetchGoogleFont('Heebo')` which calls the Google Fonts CSS2 API with a Chrome 131 User-Agent (triggers WOFF2 responses including the Hebrew `unicode-range` block). The compiled URL follows the pattern `https://fonts.googleapis.com/css2?family=Heebo:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,700`.
3. Caches the WOFF2 files at `~/.cache/hyperframes/fonts/heebo/<weight>-<style>.woff2`.
4. Embeds each face as a base64 `data:font/woff2;base64,...` URI in the compiled HTML via an injected `@font-face` rule.

Adding a stylesheet link adds a runtime network dependency that breaks deterministic rendering and duplicates the font face. Just write `font-family` and let the compiler fetch + embed.

### Hebrew Google Fonts that work

All auto-resolve via the Google Fonts fallback:

| Family | Character | When to reach for it |
|---|---|---|
| Heebo | Modern sans, widest weight range (100-900) | Default body + display in 2020s Israeli brand videos |
| Rubik | Geometric rounded sans | Product, fintech, startup copy |
| Assistant | Clean contemporary sans | Utility UI, dashboards, technical content |
| Alef | Condensed, high contrast | Editorial headlines, Hebrew-first publications |
| Frank Ruhl Libre | Modernized traditional serif | Long-form, editorial, prestige |
| Noto Sans Hebrew | Neutral pan-Unicode sans | Mixed-script, accessibility fallback |

First compile fetches the WOFF2; subsequent runs hit the local cache. To pre-warm a fresh machine, run `npx hyperframes preview` once, it triggers the same font path as render.

### Weight contrast

Hebrew display letterforms carry less visual weight than equivalent Latin glyphs at the same `font-weight`. Where the upstream typography rules call for 300 vs 900 weight contrast, Hebrew benefits from 400 vs 900. Very light Hebrew (100-200) breaks up at video sizes, avoid it for anything smaller than a headline.

## Direction

Set `dir="rtl"` explicitly on Hebrew text containers. Composition roots inherit document direction by default, but HyperFrames sub-compositions (loaded via `data-composition-src`) set their own context and don't inherit from the parent.

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

Rotation, scale, and y-axis tweens are direction-agnostic, leave them alone.

## Captions

Transcribe Hebrew audio with a multilingual Whisper model and explicit language flag. **Never use `.en` models on Hebrew audio**, they TRANSLATE Hebrew into English instead of transcribing it.

```bash
# Default Hebrew caption pipeline
npx hyperframes transcribe narration-he.wav --model small --language he

# Higher accuracy for noisy audio or music backgrounds
npx hyperframes transcribe narration-he.wav --model medium --language he

# Production quality
npx hyperframes transcribe narration-he.wav --model large-v3 --language he
```

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

The built-in `npx hyperframes tts` command uses Kokoro-82M, which does not support Hebrew. The 8 supported Kokoro languages encode in the voice-ID first letter: `a`=American English, `b`=British English, `e`=Spanish, `f`=French, `h`=Hindi, `i`=Italian, `j`=Japanese, `p`=Brazilian Portuguese, `z`=Mandarin.

Generate Hebrew voiceover with an external service and import the audio file as a normal `<audio>` clip:

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

Numbers in Hebrew context (prices, statistics, dates) are already handled correctly by the bidi algorithm, they display left-to-right inside an RTL paragraph without any wrapper.

## Quick checklist

Before rendering a Hebrew composition:

1. Root `<div data-composition-id>` has `dir="rtl"` (or the text containers do).
2. `font-family` references a Google Fonts Hebrew family, no `@import`, no `<link>`.
3. GSAP entrance x-values are positive (entering from the right) for Hebrew elements.
4. Mixed-script runs use `<bdi>` or `unicode-bidi: isolate`.
5. Audio narration file exists; it was generated externally (not via `hyperframes tts`).
6. Transcribe command used `--model <size> --language he`, never `.en`.
7. Caption spans have `dir="rtl"` and any marker-sweep animation runs right-to-left.
