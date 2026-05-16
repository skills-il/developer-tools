---
name: video-use-best-practices
description: "Best practices for using browser-use/video-use to edit Hebrew videos end-to-end with Claude Code. Covers the Hebrew-specific deltas to video-use's 12 Hard Rules: SUB_FORCE_STYLE override (Helvetica has no Hebrew glyphs), Hebrew filler-word post-pass on Scribe word timestamps, libass + fontconfig font discovery for Heebo, takes_packed.md handling for Hebrew with sofit/nikud/code-switching, and animation slot guidance that defers to hyperframes-best-practices and remotion-best-practices. Use when editing Hebrew talking-head video, podcast clips, tutorials, or marketing video with video-use. Do NOT use for non-Hebrew video-use sessions (read upstream SKILL.md directly), Hebrew podcast audio-only post-production (use hebrew-podcast-postproduction), or generic FFmpeg work without video-use orchestration."
license: MIT
allowed-tools: Bash Read Write Edit
compatibility: "Requires video-use installed (see upstream install.md). Hebrew fonts (Heebo) need to be installed on the host. Works with Claude Code (primary), Cursor, Codex. Designed to be read alongside the upstream video-use SKILL.md, not as a replacement."
---

# video-use Best Practices (Hebrew)

## Problem

video-use ships with a strong English-first default: the bundled `SUB_FORCE_STYLE` uses Helvetica (no Hebrew glyphs, renders as boxes), 2-word UPPERCASE chunks (Hebrew has no uppercase), and the filler-removal step assumes an English filler lexicon while Scribe itself doesn't tag fillers per-word in any language. Hebrew creators using video-use hit the same three walls every time: missing-glyph boxes burned into the final video, captions that look wrong because UPPERCASE doesn't exist in Hebrew, and a "filler removal" step that leaves "אֶה", "כאילו", "יעני", and friends in. This skill is the Hebrew-specific override layer on top of video-use's 12 Hard Rules, none of the rules change, only the style values, font fallback chain, and filler list.

## Instructions

This skill is an **overlay** on top of video-use's upstream SKILL.md. Read the upstream SKILL.md first for the 12 Hard Rules, the EDL JSON schema, `takes_packed.md`, `render.py`, and the parallel-animation pattern. Then apply the Hebrew deltas below.

### Step 1: Verify Hebrew fonts are installed before the first render

Hard Rule 1 (subtitles applied LAST in filter chain) plus libass font resolution means a missing Hebrew font produces a silent failure: the SRT renders as `□□□` boxes burned into the final video. Verify before you cut.

Run:

```bash
fc-list :lang=he | head -5
```

If empty, install Heebo (the canonical choice, see References section for why):

```bash
bash scripts/install-hebrew-fonts.sh
```

Re-run `fc-list :lang=he` and confirm Heebo, Rubik, Assistant, and Noto Sans Hebrew all appear. libass uses fontconfig to resolve font names; if fontconfig cannot find a Hebrew font, libass falls back to its built-in glyph (usually a box).

### Step 2: Override `SUB_FORCE_STYLE` for Hebrew

The bundled `bold-overlay` style in `render.py` is `FontName=Helvetica,FontSize=18,Bold=1,...,MarginV=35`. For Hebrew, override before invoking `render.py --build-subtitles`:

```python
# Hebrew override for video-use SUB_FORCE_STYLE.
# Applied via render.py monkeypatch OR by setting the env var the helper reads.
SUB_FORCE_STYLE_HE = (
    "FontName=Heebo,"
    "FontSize=22,"           # Hebrew x-height runs taller than Helvetica at the same point size; 22 keeps optical weight balanced
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H00000000,"
    "BorderStyle=1,Outline=2,Shadow=0,"
    "Alignment=2,"
    "MarginV=50"             # Hebrew descenders + diacritics need more bottom clearance than Latin
)
```

The full ready-to-use override file is at `references/sub-force-style-hebrew.md` with three variants: `bold-overlay-he` (kinetic typography, 4-6 word chunks since UPPERCASE does not exist in Hebrew), `natural-sentence-he` (documentary/tutorial), and `vertical-social-he` (1080x1920 with `MarginV=120` to clear platform UI).

### Step 3: Add a Hebrew filler-word post-pass

**Important correction to a common assumption:** ElevenLabs Scribe does NOT tag fillers per word in ANY language. The Scribe word object exposes `type` values of `'word'`, `'spacing'`, or `'audio_event'` only, there is no `'filler'` or `'is_filler'` field. The only filler-related control is the request-level boolean `no_verbatim` (scribe_v2 only), which is **destructive**: it removes filler words, false starts, and disfluencies from the output entirely instead of marking them for review. `tag_audio_events` tags non-speech audio like `(laughter)` and `(applause)`, not verbal hesitations.

What that means in practice: call Scribe with `no_verbatim=false` (the default, keeps fillers in the word stream verbatim), then run your own lexicon match over `words[].text` to mark filler candidates. Cutting based on a lexicon you control beats `no_verbatim=true` because it preserves the editor sub-agent's ability to keep meaning-bearing instances.

Apply the Hebrew filler lexicon at `references/hebrew-filler-words.md`. The full list there has ~30 entries split into ALWAYS-FILLER (safe to auto-cut) and CONTEXT-DEPENDENT (flag for the editor sub-agent, these words have real meaning in some contexts). The core entries:

```
ALWAYS-FILLER:
אֶה, אה, אם, אֶמ, אממ, אמממ, אהמ, המ, ממ

CONTEXT-DEPENDENT (flag, don't auto-cut):
כאילו, יעני, אז, אז ככה, בעצם, טוב, טוב נו, אוקיי, סבבה,
נו, האמת, בסדר, וואלה, כזה, ככה, נכון, פשוט, ממש,
סוג של, בקיצור, כנראה, לדעתי,
את יודע, את יודעת, אתה יודע, אתה מבין, את מבינה, הבנת,
תראה, תראי, שמע, שמעי, בוא, בואי
```

Apply the same rule as upstream: do not strip mid-phrase. Treat detected ALWAYS-FILLER tokens as silence-equivalent cut candidates with the same 30-200ms padding window (Hard Rule 7) and the same word-boundary snap (Hard Rule 6). For CONTEXT-DEPENDENT tokens, surface them to the editor sub-agent with a flag rather than auto-cutting.

**Editorial nuance:** the CONTEXT-DEPENDENT entries each have a literal sense and a filler sense. "כאילו" is filler in "זה כאילו לא עבד" but a literal "as if" in "התנהגה כאילו לא קרה כלום". "תראה / שמע / בוא" function as turn-starters far more often than as the literal verb in spoken Hebrew, but they ARE sometimes literal. Per upstream's "Unavoidable slips are kept if no better take exists" rule, prefer leaving them in over multiple cuts in tight succession. A small number per minute tends to read as natural Israeli speech.

### Step 4: `takes_packed.md` with Hebrew transcripts

`pack_transcripts.py` works unchanged on Hebrew Scribe JSON, it is locale-blind, breaks on silence >=0.5s, and produces phrase-level lines. Three Hebrew-specific things to watch:

1. **Code-switching is common.** Tech tutorials say "התקנתי React" (mid-sentence English). The phrase boundary stays on silence, not on script change. Do not try to "fix" this in the packed transcript, let the editor sub-agent see the mixed line as a single phrase. Hard Rule 6 (snap cuts to word boundaries) still applies; the boundary is in the Scribe JSON regardless of script.
2. **Nikud (vowel marks) is usually absent in Scribe output.** Do not add it. The Scribe transcript is for cut decisions, not for end-user reading. Burn-in subtitles use the same un-nikud-ed text.
3. **Sofit forms (ם ן ץ ף ך) appear correctly in Scribe output** when used at end-of-word. If you see middle-of-word sofit forms, that is a Scribe error, flag in pre-scan (upstream step 2) but do not silently rewrite.

### Step 5: Animation slots, defer to existing Hebrew skills

video-use's upstream SKILL.md says: *"Do not default to Remotion just because the animation is web-adjacent."* For Hebrew animation slots, the priority is the same, and we have a dedicated skill per engine:

| Slot type | Engine | Skill to load into the sub-agent prompt |
|-----------|--------|------------------------------------------|
| Kinetic typography, callout cards, product UI motion | HyperFrames | `hyperframes-best-practices` (covers Heebo via Google Fonts auto-fetch, `dir="rtl"`, `<bdi>` for mixed scripts) |
| Component-state compositions, existing Remotion brand system | Remotion | `remotion-best-practices` (covers Hebrew Google Fonts, bidi text animations) |
| Diagrams, equation derivations | Manim | (no Hebrew skill yet, Manim's Hebrew support is limited; pre-render Hebrew labels as PNG and import as `ImageMobject`) |
| Simple counters, typewriter, single bar reveals | PIL | Use `Pillow.ImageFont.truetype("Heebo-Bold.ttf", size, layout_engine=ImageFont.Layout.RAQM)` to enable HarfBuzz-based BiDi. Without `RAQM`, Pillow draws glyphs in input order and Hebrew comes out backwards |

When spawning a parallel sub-agent for a Hebrew animation slot, include in the prompt: *"This is a Hebrew animation. Load `hyperframes-best-practices` (or `remotion-best-practices`) before writing any composition code. Use Heebo as the default font."* The 10-point sub-agent brief from upstream SKILL.md applies unchanged.

### Step 6: Self-eval, extend step 7 for Hebrew

Upstream's self-eval (step 7 of "The process") runs `timeline_view` on the rendered output at every cut boundary and checks four things. For Hebrew, add two checks:

5. **Glyph fallback boxes.** Scan the subtitle row of each sampled frame. If you see `□`, `?`, or visibly different fonts mid-line, libass picked a fallback font, abort and re-check Step 1 (fontconfig found no Hebrew font).
6. **Mixed-script line direction.** For frames with code-switched lines like "התקנתי React", verify the Hebrew portion reads right-to-left and the English brand stays left-to-right within the right-to-left flow. If "React" appears mirrored or the whole line flipped LTR, the SRT file is missing the UTF-8 BOM or libass is misreading the file encoding.

Keep the 3-pass cap from upstream. If the boxes persist after 3 passes, flag to the user, the issue is environmental (font install), not editorial.

### Step 7: Sample Hebrew prompts to drive the conversation phase

video-use's "Converse" step (step 3 of "The process") asks questions shaped by the material. Sample Hebrew prompts users send:

| Hebrew user message | What it maps to in the upstream workflow |
|---------------------|------------------------------------------|
| "ערוך את הקבצים האלה לסרטון השקה" | "edit these into a launch video", full inventory then strategy then execute |
| "תנקה את השתיקות ואת המילים המיותרות" | Filler removal + dead-space cuts only |
| "תוסיף כתוביות בעברית במרכז התחתון" | Subtitle generation with Hebrew SUB_FORCE_STYLE override |
| "תוסיף גרידינג חם" | `grade.py --filter` with `warm_cinematic` preset (works language-agnostic) |
| "תפצל למקטעים של 30 שניות לאינסטה" | Vertical 1080x1920 reformat with `vertical-social-he` style |
| "תבדוק שאין שגיאות בכתוביות בעברית" | Trigger self-eval Step 6 (glyph fallback + direction) |

## Examples

### Example 1: 30-minute Hebrew talking-head to 5-minute edited cut with captions

User says: *"ערוך את הקבצים האלה לסרטון השקה. תוסיף כתוביות בעברית."*

Actions:
1. **Inventory.** `ffprobe` all sources, `transcribe_batch.py` against the directory (Scribe handles Hebrew automatically, no language flag needed), `pack_transcripts.py`.
2. **Pre-scan.** Read `takes_packed.md`. Note Hebrew slips AND English filler tags from Scribe.
3. **Hebrew filler post-pass.** Apply the list from Step 3 to Scribe JSON. Add filler timestamps to the cut-candidate set.
4. **Converse + propose strategy** in Hebrew. Confirm the user wants Heebo for captions, target 5 minutes, vertical or horizontal.
5. **Execute.** Editor sub-agent produces `edl.json` with word-boundary cuts (Hard Rule 6) snapped via Scribe timestamps.
6. **Render** with `SUB_FORCE_STYLE_HE`. `render.py --build-subtitles` produces `master.srt` with output-timeline offsets (Hard Rule 5).
7. **Self-eval.** Run upstream's 4 checks + the 2 Hebrew checks from Step 6.
8. **Persist** to `project.md` in Hebrew or English (user choice, video-use is locale-blind for memory).

Result: 5-minute Hebrew video with Heebo-rendered RTL captions, fillers cut, 30ms fades at every boundary.

### Example 2: Mixed Hebrew/English tech tutorial with code-switching

User says: *"ערוך את ההקלטה של המדריך React הזה."*

Actions:
1. Same inventory + transcribe pipeline.
2. `takes_packed.md` shows phrases like `[045.12-049.87] S0 התקנתי React אבל הוא לא טוען`. Do not normalize.
3. Cut decisions on word boundaries, the boundary between "React" and "אבל" is in Scribe JSON regardless of script change.
4. Render with `SUB_FORCE_STYLE_HE`. The SRT contains the mixed line as a single subtitle entry; libass + BiDi handles direction at render time **only if the SRT is saved as UTF-8 with BOM**.
5. Self-eval Step 6 explicitly verifies "React" appears LTR within the RTL flow.

Result: Tutorial video where Hebrew narration reads RTL and English code/library names render LTR inline, no manual `<bdi>` markup needed.

## Recommended MCP Servers

video-use is a standalone Claude Code skill and does not require any MCP server. If your Hebrew editing workflow needs live data (for example, fetching trending Hebrew tweets to caption over, or pulling Bituach Leumi PSA copy), check the skills-il MCP directory at https://agentskills.co.il/mcp.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| video-use upstream | https://github.com/browser-use/video-use | SKILL.md (12 Hard Rules), install.md, helpers/ |
| libass ASS format guide | https://github.com/libass/libass/wiki/ASS-File-Format-Guide | UTF-8 BOM requirement, Encoding field rules |
| FFmpeg subtitles filter | https://ffmpeg.org/ffmpeg-filters.html | `subtitles=` filter syntax, libass dependency |
| Heebo on Google Fonts | https://fonts.google.com/specimen/Heebo | License, weights, character coverage |
| Noto Sans Hebrew | https://fonts.google.com/noto/specimen/Noto+Sans+Hebrew | Hebrew script coverage |
| Unicode BiDi algorithm | https://www.unicode.org/reports/tr9/ | UAX #9, directional isolation rules for mixed Hebrew+Latin |
| ElevenLabs Scribe | https://elevenlabs.io/blog/meet-scribe | Multi-language transcription (Hebrew supported via 99-language model) |

## Bundled Resources

### Scripts

- `scripts/install-hebrew-fonts.sh`, Idempotent installer for Heebo, Rubik, Assistant, Noto Sans Hebrew. macOS (Homebrew cask) and Debian/Ubuntu (apt + manual fallback) paths. Re-runs `fc-cache` and verifies via `fc-list :lang=he`.

### References

- `references/sub-force-style-hebrew.md`, Three ready-to-use `SUB_FORCE_STYLE` overrides for Hebrew (`bold-overlay-he`, `natural-sentence-he`, `vertical-social-he`). Documents why each value differs from the upstream Latin defaults.
- `references/hebrew-filler-words.md`, Annotated Hebrew filler list with editorial guidance (which are always-fillers vs. sometimes-load-bearing). Drop-in for the Step 3 post-pass.

## Gotchas

- **Helvetica is the most common mistake.** The bundled `SUB_FORCE_STYLE` in `render.py` uses `FontName=Helvetica`. Helvetica's Hebrew glyphs do NOT exist in the macOS or Linux Helvetica builds (Apple's "Helvetica" font is Latin-only; Linux usually maps it to a metric-equivalent). libass silently falls back to a tofu box. Always override `FontName` to a known Hebrew font before invoking `render.py --build-subtitles`. The override is invisible in the rendered preview's lower-third UI but obvious once you sample frames.
- **2-word UPPERCASE chunks do not translate to Hebrew.** Hebrew has no uppercase. Do not try to fake it with `\fnHeebo Bold`, the result looks the same as regular Heebo. The Hebrew kinetic-typography equivalent is bold weight + larger size + tighter line breaks (4-6 Hebrew words per chunk, since Hebrew words are shorter than English on average).
- **SRT vs ASS for Hebrew.** video-use's `render.py --build-subtitles` produces SRT (not ASS). SRT + libass + BiDi handles Hebrew correctly **only when the file is saved UTF-8 with BOM** per the libass file-format guide. The `helpers/render.py` `build_subtitles()` function writes UTF-8 without BOM. If your captions render LTR or mirrored, the canonical fix is to prepend the BOM (`﻿`) when writing the file. If that doesn't resolve it, convert the SRT to ASS (`ffmpeg -i master.srt master.ass`) which gives you explicit `Encoding=1` per the libass rule, then point the `subtitles=` filter at the ASS file.
- **Do not pre-translate code-switched English brands.** Users typing "תוסיף ראקט" (transliteration of "React") instead of "React" causes Scribe to transcribe phonetically wrong. Tell the user during the conversation phase: code-switched English stays English in the transcript and in the burned-in caption, Hebrew speakers expect this.
- **`yt-dlp` Hebrew filenames.** When pulling Hebrew sources from URLs, `yt-dlp` writes filenames with Hebrew chars. Subsequent FFmpeg + libass passes work fine on macOS but can break on Linux filesystems with non-UTF-8 locales (`LC_ALL=C` is the common culprit). Set `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8` in the install.md `.env` if you see "No such file" errors on visibly-present files.

## Troubleshooting

### Captions render as `□□□` boxes in the final video

Cause: libass cannot find a Hebrew-capable font via fontconfig.
Solution: Run `fc-list :lang=he`, if empty, `bash scripts/install-hebrew-fonts.sh`, then `fc-cache -f -v`. Re-render. If still empty after install, check `fc-cache` permissions (may need `sudo` on Linux for system font dirs).

### Hebrew captions appear LTR or with words in reverse order

Cause: SRT file written without UTF-8 BOM, libass misreads encoding.
Solution: Either (a) re-save the SRT with BOM prefix `﻿`, or (b) convert to ASS via `ffmpeg -i master.srt master.ass` so libass gets the default `Encoding=1` per its file-format guide. Re-render.

### Filler removal cut English fillers but left Hebrew fillers

Cause: ElevenLabs Scribe tags English fillers only; Hebrew filler post-pass (Step 3) was skipped.
Solution: Apply the `references/hebrew-filler-words.md` list to Scribe word timestamps before computing cut candidates. Re-run the editor sub-agent.

### Self-eval Step 6 passes locally but cloud render shows boxes

Cause: Local has Hebrew fonts via fontconfig; cloud renderer (Linux container without fonts) does not.
Solution: Add `scripts/install-hebrew-fonts.sh` to the container build step. Or bundle Heebo `.ttf` into `<edit>/fonts/` and point the FFmpeg `subtitles` filter at it inline: `subtitles=master.srt:fontsdir=<edit>/fonts`. (Note: `--enable-libass` is a configure-time FFmpeg build flag, not a runtime CLI flag; the runtime equivalent is the `fontsdir=` parameter on the `subtitles` filter, or setting `FC_CONFIG_DIR` env var to a fontconfig dir that includes Hebrew fonts.)
