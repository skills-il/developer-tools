# Hebrew SUB_FORCE_STYLE overrides for video-use

Three drop-in replacements for the `SUB_FORCE_STYLE` constant in `helpers/render.py`. Use whichever matches the delivery format.

## Why these values differ from the upstream Latin defaults

The upstream `bold-overlay` style in `render.py` is designed for English short-form social video and uses Helvetica at **FontSize=18, MarginV=90**, against libass's default `PlayResY: 288`.

> **Correction (2026-08-26).** Earlier revisions of this file said upstream uses `MarginV=35`. That number appears in upstream's own SKILL.md prose, but its shipped `SUB_FORCE_STYLE` in `helpers/render.py` is `Alignment=2,MarginV=90`, with a comment explaining the choice: "MarginV is NOT taste, it is a platform safe-zone rule. TikTok / IG Reels / Shorts UI ... covers roughly the bottom ~25-30% of a 1080x1920 frame ... libass auto-scales the render canvas relative to PlayResY=288, so MarginV=90 lands the caption baseline roughly 30% up from the bottom on any aspect. Do not drop this below ~75 without a specific reason." The code is ground truth.

**Everything below is expressed against PlayResY=288, so the numbers are fractions of frame height, not output pixels.** This matters because `scripts/burn-hebrew-captions.sh` rewrites `PlayResY` to the real video height. Once it does, an absolute MarginV means something completely different: measured on a 1080x1920 render, the old fixed `MARGINV=80` put the caption baseline 89px from the bottom, **4.6% of frame height**, inside the very UI band upstream's 31.25% exists to clear. Font size collapsed the same way, 52/1920 = 2.7% against upstream's 18/288 = 6.25%. As of skill v1.3.0 the script derives both from frame height: portrait uses upstream's ratios (6.25% font, 31.25% margin), landscape keeps the script's previously shipping ratios (4.81% font, 7.41% margin), because upstream's stated rationale is vertical-platform UI and a 31% margin would float captions into the middle of a landscape lecture. `--font-size` and `--margin-v` still accept absolute pixels and override the ratio.

Three Hebrew-specific adjustments:

1. **FontName**: Helvetica has no Hebrew glyphs on macOS or Linux. libass falls back to a tofu box. Heebo is the closest Hebrew design match (rationale below).
2. **FontSize**: Hebrew x-height is taller than Latin Helvetica at the same point size. Bumping to 22 keeps the optical weight balanced; using the Latin size makes Hebrew captions look oversized next to where users expect.
3. **MarginV**: Hebrew has more vertical ink below the baseline than Latin (sofit forms like ך, ץ, ף descend) plus the occasional dot below for nikud, so it needs a little more clearance than the Latin equivalent. The variant values below (50 horizontal, 70 documentary, 120 vertical social) are in PlayResY=288 units. **Note the 120 vertical-social value is 41.7% of frame height, deliberately above upstream's 31.25%; the 50 used for the horizontal variant is 17.4%, deliberately below it, because a landscape lecture has no bottom action rail.** Adjust if your platform's safe zone has changed.

## Why Heebo as the canonical font

Among the Hebrew Google Fonts (Heebo, Rubik, Assistant, Noto Sans Hebrew), Heebo is the closest geometric match to Helvetica, which is what the upstream `bold-overlay` style was tuned for. The selection rationale (informed, not definitive , confirm against your brand if you have one):

- Geometric / grotesque construction matching Helvetica's design family.
- Multiple weights available on Google Fonts for kinetic-typography work.
- Latin glyphs designed to harmonize with the Hebrew (relevant for code-switched lines like "התקנתי React").
- Free and open license via Google Fonts (verify the current license on the specimen page before commercial redistribution).

Alternatives are intentionally listed second:
- **Rubik**: slightly rounder, friendlier feel; good for casual content, less precise at small sizes.
- **Assistant**: thinner default weight; good for documentary subtitles when readability at lower contrast matters.
- **Noto Sans Hebrew**: maximum glyph coverage including rare cantillation marks; use when subtitles include biblical or liturgical text.

If the brand requires a specific Hebrew font not on this list, override `FontName` to that font's PostScript name and confirm via `fc-match "<FontName>:lang=he"` that fontconfig resolves to it (not to a fallback).

## Variant 1: `bold-overlay-he`, short-form social, kinetic typography

Drop-in replacement for the upstream `bold-overlay`. Use for TikTok/Reels/Shorts that need fast-paced kinetic typography.

```python
SUB_FORCE_STYLE_HE_BOLD = (
    "FontName=Heebo,"
    "FontSize=22,"
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H00000000,"
    "BorderStyle=1,Outline=2,Shadow=0,"
    "Alignment=2,"
    "MarginV=50"
)
```

**Chunking rules** (apply when generating SRT, not in the style):
- Hebrew has no UPPERCASE, so the upstream "2-word UPPERCASE" rule does not apply. Use 4-6 Hebrew words per caption line instead (Hebrew words average shorter than English, so the equivalent visual density is 4-6 not 2).
- Break on punctuation (`.`, `,`, `?`, `!`, `;`).
- Never break mid-construct-state (e.g., do not split "בית ספר" across lines).

## Variant 2: `natural-sentence-he`, documentary, tutorial, education

Sentence-case Hebrew (which is just Hebrew, since there is no case), longer chunks, larger font for readability.

```python
SUB_FORCE_STYLE_HE_NATURAL = (
    "FontName=Heebo,"
    "FontSize=28,"           # larger for sustained reading at 1x
    "Bold=0,"                # regular weight reads less aggressive over documentary footage
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H00000000,"
    "BorderStyle=1,Outline=2,Shadow=0,"
    "Alignment=2,"
    "MarginV=70"             # extra clearance for longer reading time at frame bottom
)
```

**Chunking rules:**
- 7-10 Hebrew words per line, two lines maximum.
- Break on natural pauses from Scribe word timestamps (gaps >=300ms).
- Prefer punctuation breaks over word-count breaks.

## Variant 3: `vertical-social-he`, 1080x1920 (Reels, Shorts, TikTok)

Vertical canvas with safe-zone margin to clear the platform UI overlays (likes, share, follow button, caption text).

```python
SUB_FORCE_STYLE_HE_VERTICAL = (
    "FontName=Heebo,"
    "FontSize=32,"           # larger absolute size to read on mobile
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H00000000,"
    "BorderStyle=1,Outline=3,Shadow=0,"
    "Alignment=2,"
    "MarginV=120"            # clears Instagram/TikTok bottom UI (caption row + audio attribution)
)
```

**Chunking rules:**
- 3-5 Hebrew words per line (narrower visual width).
- Single line preferred; two lines max.
- Position above platform UI varies by year and platform; 120 (41.7% of frame height at PlayResY=288) is a conservative MarginV that works across all three as of 2026, and sits above upstream's 31.25% floor. Verify against the current Instagram/TikTok safe-zone before final delivery , platforms change UI layouts.

## Wiring into video-use

Easiest path: monkeypatch in your project's prelude before invoking `render.py`. Example:

```python
import helpers.render as render
render.SUB_FORCE_STYLE = SUB_FORCE_STYLE_HE_BOLD
```

Cleaner path: fork `render.py` locally and add a `--style hebrew-bold|hebrew-natural|hebrew-vertical` CLI flag that switches the constant. The upstream rules (subtitles LAST, output-timeline offsets) remain unchanged.

## Verification

After overriding, render a 5-second test clip and `timeline_view` it. The Hebrew text should:

- Render in Heebo's distinct geometric shapes (not Helvetica fallback or libass tofu).
- Sit cleanly above the bottom edge with the MarginV margin visible.
- Read right-to-left with no glyph reordering.
- For mixed-script lines: Hebrew portion RTL, English brands LTR inline.

If any check fails, the issue is in Step 1 (fontconfig) or Step 2 (style override applied AFTER style is locked in by render.py), not in this file.
