---
name: video-use-best-practices
description: "Best practices for using browser-use/video-use to edit Hebrew videos end-to-end with Claude Code. Covers the Hebrew-specific deltas to video-use's 12 Hard Rules: SUB_FORCE_STYLE override (Helvetica has no Hebrew glyphs), the python-bidi pre-shape recipe for libass+SRT BiDi failures on macOS, Hebrew filler-word post-pass on Scribe word timestamps, fontsdir= parameter for reliable font discovery, takes_packed.md handling for Hebrew with sofit/nikud/code-switching, and animation slot guidance that defers to hyperframes-best-practices and remotion-best-practices. Use when editing Hebrew talking-head video, podcast clips, tutorials, or marketing video with video-use. Do NOT use for non-Hebrew video-use sessions (read upstream SKILL.md directly), Hebrew podcast audio-only post-production (use hebrew-podcast-postproduction), or generic FFmpeg work without video-use orchestration."
license: MIT
allowed-tools: Bash Read Write Edit
compatibility: "Claude Code only. video-use's Hard Rule 10 requires the Agent tool for parallel animation sub-agent dispatch, which is Claude Code's specific primitive. The upstream install.md mentions Codex as well, but the parallel-agent model differs and is not tested here. Also requires video-use installed (see upstream install.md), an ffmpeg with libass+fontconfig (see references/macos-ffmpeg-setup.md if on Homebrew), python-bidi installed, and Hebrew fonts (Heebo) on the host."
---

# video-use Best Practices (Hebrew)

## Problem

video-use ships with a strong English-first default: the bundled `SUB_FORCE_STYLE` uses Helvetica (no Hebrew glyphs, renders as boxes), 2-word UPPERCASE chunks (Hebrew has no uppercase), and the filler-removal step assumes an English filler lexicon while Scribe itself does not tag fillers per-word in any language. Hebrew creators using video-use hit the same three walls every time: missing-glyph boxes burned into the final video, captions that look wrong because UPPERCASE doesn't exist in Hebrew, and a "filler removal" step that leaves "אֶה", "כאילו", "יעני", and friends in. On macOS there's also a fourth wall: libass + SRT BiDi reordering is unreliable even with a fully-built libass, so Hebrew sentences render as characters drawn left-to-right in source byte order rather than in proper RTL visual order. This skill is the Hebrew-specific override layer on top of video-use's 12 Hard Rules. None of the upstream rules change, only the style values, font fallback chain, filler lexicon, caption-burn recipe, and self-eval frame checks.

## Pricing you should understand before you start

video-use is free; underlying services are paid. Mode determines cost.

| Mode | What | Best for | Cost / 1hr video |
|------|------|----------|------------------|
| **A. Captions-only** (`scripts/captions-only.sh`) | Transcribe + burn Hebrew captions on original. No cuts. | Lectures, webinars, podcast videos. | **~$1-3 total** |
| **B. Full cut** (default video-use flow) | Inventory → strategy → cut → render → self-eval. | Teaser from raw footage; multi-take selection. | **~$25-60** (1hr); **$120-300** (3hr). Scales super-linearly. |

Per-unit: Scribe ~$0.40/hr (paid). Claude tokens depend on mode (above). Local FFmpeg/libass rendering is $0.

**Free-tier reality check (the "$1-3" number assumes paid Starter, $5/mo).** ElevenLabs free tier is **10,000 characters/month**, not hours. A 10-minute Hebrew talking-head burns ~7,000-8,000 characters in one transcription. Gap-recovery (see Step 8) re-transcribes the dropped window, which counts again. So on free tier you realistically get **~1 long Hebrew video/month** before the quota wall. If the user is non-technical and "just wants captions on this one lecture", warn them upfront.

**Validated test (May 2026, 11:29 source → 75s teaser via Full cut):** Scribe $0.08 + Claude $9.50 = **~$9.60 first pass**, ~$1-3 per iteration.

**Pick the cheap one if unsure.** Captions-only is 20-100x cheaper than Full cut for long videos and produces the same caption quality. If you decide to cut later, the Scribe transcript is already cached.

**Pricing trap:** `no_verbatim=true` on Scribe sounds like it saves money by dropping fillers but is destructive (agent loses the ability to make per-instance keep/cut decisions, usually leads to a re-transcription). Keep `no_verbatim=false` (default) and run the Hebrew lexicon post-pass instead.

**Offline fallback (no Scribe budget):** Whisper Large v3 transcribes Hebrew locally for free. WER is ~33% (vs Scribe's 15%), so captions are noticeably less accurate, but it works when ElevenLabs is unavailable or you want zero cost. Run `whisper your-video.mp4 --language he --model large-v3 --output_format srt`, then feed the SRT to `burn-hebrew-captions.sh` directly (skip captions-only.sh which assumes Scribe).

## Instructions

This skill is an **overlay** on top of video-use's upstream SKILL.md. Read the upstream SKILL.md first for the 12 Hard Rules, the EDL JSON schema, `takes_packed.md`, `render.py`, and the parallel-animation pattern. Then apply the Hebrew deltas below.

### Step 0 (FIRST TURN ONLY): Price disclaimer + mode selection

On the **first turn of a new session** (not on follow-ups within the same session), state the price disclaimer AND ask which mode. Both in one message. Do NOT re-show this on subsequent turns once the user has picked.

> *"לפני שמתחילים, חשוב שתדע: השימוש בסקיל הזה צורך מ-ElevenLabs (כ-$0.40 לשעה של אודיו) ומ-Anthropic Claude (תלוי במסלול). העלות מצטברת אצלך, לא אצלי. שני מסלולים:*
>
> *(א) כתוביות בלבד על כל הסרטון, בלי חיתוך. כ-$1 עד $3 לכל סרטון. מתאים להרצאה, וובינר, פודקאסט.*
>
> *(ב) חיתוך לטיזר/קליפ קצר עם כתוביות. כ-$10 עד $300 לפי אורך המקור.*
>
> *מה אתה מעדיף?"*

English: *"Before we start, costs: ElevenLabs (~$0.40/hr) + Claude (depends on mode). Two paths: (A) captions-only ~$1-3, or (B) full cut ~$10-300. Which one?"*

Routing: **A → Step 8** (skip 1-7). **B → Step 1**. **Unsure → recommend A** (Scribe transcript caches, so adding B later only adds ~$0.08).

### Step 1: Verify the environment before the first render

Hard Rule 1 (subtitles applied LAST in filter chain) plus libass font resolution means a missing Hebrew font, a missing libass build, or a missing python-bidi install all produce silent failures: the SRT renders as `□□□` boxes burned into the final video, or as Hebrew with characters in the wrong positions. Verify all three before you cut.

```bash
# 1. ffmpeg has libass + fontconfig + libharfbuzz
ffmpeg -version 2>&1 | grep -oE 'enable-(libass|fontconfig|libharfbuzz|libfreetype)' | sort -u
# Expect: enable-fontconfig, enable-libass, enable-libfreetype, enable-libharfbuzz

# 2. Hebrew fonts are installed (Heebo, Rubik, Assistant, Noto Sans Hebrew)
fc-list :lang=he | head -5

# 3. python-bidi is installed (needed for the macOS BiDi workaround in Step 7)
python3 -c 'import bidi; print(bidi.__version__)'
```

If any check fails:
- Missing libass in ffmpeg → read `references/macos-ffmpeg-setup.md`, install the static evermeet build or use the homebrew-ffmpeg tap.
- Missing Hebrew fonts → `bash scripts/install-hebrew-fonts.sh` (idempotent installer for the canonical 4 fonts).
- Missing python-bidi → `pip3 install python-bidi`.

### Step 2: Override `SUB_FORCE_STYLE` for Hebrew

The bundled `bold-overlay` style in `render.py` is `FontName=Helvetica,FontSize=18,Bold=1,...,MarginV=35`. For Hebrew, override before invoking `render.py --build-subtitles`:

```python
# Hebrew override for video-use SUB_FORCE_STYLE.
# Applied via render.py monkeypatch OR by setting the env var the helper reads.
SUB_FORCE_STYLE_HE = (
    "FontName=Heebo,"
    "FontSize=22,"           # Hebrew x-height runs taller than Helvetica at the same point size
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H00000000,"
    "BorderStyle=1,Outline=2,Shadow=0,"
    "Alignment=2,"
    "Spacing=2,"             # default Hebrew tracking is cramped in libass
    "MarginV=50,"            # Hebrew descenders + diacritics need more bottom clearance than Latin
    "Encoding=1"             # libass rule: MUST always be 1
)
```

**Important:** overriding `SUB_FORCE_STYLE` is necessary but NOT sufficient on macOS. video-use's render.py path produces SRT files, and SRT + libass + BiDi is unreliable on macOS regardless of style settings. You must ALSO follow Step 7 (caption burn-in recipe) to get correct visual output. The override in this step ensures the right font and spacing for when libass eventually gets there.

The full ready-to-use override file is at `references/sub-force-style-hebrew.md` with three variants: `bold-overlay-he` (kinetic typography, 4-6 word chunks since UPPERCASE does not exist in Hebrew), `natural-sentence-he` (documentary/tutorial), and `vertical-social-he` (1080x1920 with `MarginV=120` to clear platform UI).

### Step 3: Add a Hebrew filler-word post-pass

**Important correction to a common assumption:** ElevenLabs Scribe does NOT tag fillers per word in ANY language. The Scribe word object exposes `type` values of `'word'`, `'spacing'`, or `'audio_event'` only, there is no `'filler'` or `'is_filler'` field. The only filler-related control is the request-level boolean `no_verbatim` (scribe_v2 only), which is **destructive**: it removes filler words, false starts, and disfluencies from the output entirely instead of marking them for review. `tag_audio_events` tags non-speech audio like `(laughter)` and `(applause)`, not verbal hesitations.

What that means in practice: call Scribe with `no_verbatim=false` (the default, keeps fillers in the word stream verbatim), then run your own lexicon match over `words[].text` to mark filler candidates. Cutting based on a lexicon you control beats `no_verbatim=true` because it preserves the editor sub-agent's ability to keep meaning-bearing instances.

Apply the Hebrew filler lexicon at `references/hebrew-filler-words.md`. The full list there has ~35 entries split into ALWAYS-FILLER (safe to auto-cut) and CONTEXT-DEPENDENT (flag for the editor sub-agent, these words have real meaning in some contexts). The core entries:

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

### Step 6: Frame-sampling self-eval (you must look at actual pixels)

Upstream's self-eval (step 7 of "The process") runs `timeline_view` on the rendered output at every cut boundary and checks four things. For Hebrew, you must **actually open and look at sampled frames** to verify two more checks. Do not just trust that libass succeeded; the failure modes are silent.

The mandatory protocol:

```bash
# Sample frames at evenly-spaced timestamps across the output, plus right after every cut
ffmpeg -y -ss <time> -i final.mp4 -frames:v 1 -vf "crop=iw:200:0:ih-220" /tmp/verify/t<time>s.png
```

Then **open each PNG and verify with your own eyes**:

5. **Glyph fallback boxes.** Scan the subtitle row. If you see `□`, `?`, or visibly different fonts mid-line, libass picked a fallback font. The most common cause: `fontsdir=` parameter was not passed to the `subtitles` filter (Step 7 handles this). Re-render with `fontsdir=$HOME/Library/Fonts` (macOS) or wherever `fc-list :family=Heebo file` reports.

6. **RTL visual order (the most-missed check).** For a known caption line, verify the pixel left-to-right order is the REVERSE of source byte order. Example: source SRT line `ספריית הסקילז AI שבניתי.` should render with pixel LTR order:
   ```
   ספריית [right]   הסקילז   AI   שבניתי   . [left]
   ```
   The first source word (`ספריית`) ends up on the visual RIGHT. The period (last source byte) ends up on the visual LEFT. `AI` is embedded LTR within the RTL flow.

   **If the pixel LTR order matches the source byte order instead of being reversed, BiDi was not applied.** Symptoms: words look correctly shaped but appear in "English-style" left-to-right positions, with period on the right. This is the most common Hebrew failure on macOS and the recipe in Step 7 fixes it.

Keep the 3-pass cap from upstream. After 3 failed renders, stop iterating and flag to the user, the problem is environmental (font install, ffmpeg build, missing python-bidi), not editorial.

**An honest example from the field:** during the first validated run of this skill (May 2026), self-eval initially passed because the agent only checked for "no boxes" and didn't compare pixel order to source byte order. The output had perfect Heebo rendering but every Hebrew line was visually reversed because libass skipped BiDi. The fix landed in Step 7 below.

### Step 7: Caption burn-in recipe (the one that actually works on macOS)

The bundled `scripts/burn-hebrew-captions.sh` does this in one command. The recipe is short:

1. **Sanitize the SRT** for Scribe garbage characters (Devanagari `्स` etc. that Scribe occasionally drops mid-Hebrew). Auto-fixes known patterns, warns on unknown ones.
2. **Feed the SRT directly to libass** via the FFmpeg `subtitles=` filter with explicit `fontsdir=` and `force_style=FontName=Heebo\,FontSize=26\,Bold=1\,Spacing=2\,Encoding=1\,...`. libass + SRT handles Hebrew BiDi correctly out of the box. Do NOT convert to ASS first; do NOT pre-shape with python-bidi (both interfere with libass's native BiDi).
3. **Sample verification frames** (1 per minute, capped at 30).

One-line invocation:

```bash
bash scripts/burn-hebrew-captions.sh \
  --base   edit/base.mp4 \
  --srt    edit/master.srt \
  --out    edit/final.mp4 \
  --ffmpeg /tmp/ffmpeg
```

**Important correction (v1.2.3):** earlier versions of this skill (v1.1.0 through v1.2.2) claimed libass+SRT was silently broken for Hebrew BiDi on macOS and recommended a python-bidi pre-shape + SRT→ASS chain to work around it. **That diagnosis was wrong.** libass+SRT actually handles BiDi correctly. The pre-shape chain was double-reversing back to source byte order, producing the exact symptom (period on right, first word on left) the workaround was meant to fix. Renders produced with v1.1.0-v1.2.2 that look broken will render correctly with v1.2.3+ unchanged.

**FontSize is in absolute pixels** when using libass+SRT directly (no PlayRes scaling). Defaults: 26 for 720p, 36-42 for 1080p, 56-72 for 4K.

### Step 8: Long video, captions-only mode (cheap path for non-editors)

**Use this when:** the user has a full lecture, webinar, podcast video, or talking-head recording, and just wants Hebrew captions burned in on the whole thing. No cuts. No editing. No multi-take selection. This is by far the most common request from non-technical users, and the full Steps 1-7 workflow is overkill (and 20-100x more expensive) for it.

The bundled `scripts/captions-only.sh` collapses the full workflow into one command:

```bash
# Basic: just add captions
bash scripts/captions-only.sh ~/Movies/my-lecture.mp4

# Add captions AND remove "אה / אהה / אם" filler words from the on-screen text
# (audio stays untouched, words just won't appear in captions):
bash scripts/captions-only.sh ~/Movies/my-lecture.mp4 --strip-fillers

# Non-interactive (skip the cost-confirmation prompt; useful in CI / batch runs)
bash scripts/captions-only.sh ~/Movies/my-lecture.mp4 --yes

# With custom output path and a static ffmpeg
bash scripts/captions-only.sh ~/Movies/my-lecture.mp4 \
  --output ~/Movies/my-lecture-with-captions.mp4 \
  --ffmpeg /tmp/ffmpeg
```

What it does, end-to-end:
1. Auto-detects `ELEVENLABS_API_KEY` from env or `~/Developer/video-use/.env`
2. Probes the video duration and prints the estimated Scribe cost (unless `--yes` is passed)
3. Transcribes the full video via Scribe v1 with `language_code=heb` and `timestamps_granularity=word`
4. **Auto-recovers Scribe gaps** (v1.2.7+): scans for any 30s+ mid-file silence between consecutive transcribed words OR a tail end where the last word finishes >10s before the video ends. For each detected window, re-transcribes that isolated segment with `scribe_v2` and merges the recovered words back into the main transcript. Scribe occasionally drops 30s+ chunks silently on long Hebrew files; this makes the failure self-healing instead of "users discover untranscribed sections weeks later".
5. Builds an SRT chunking 5-7 words per caption, breaking on silence ≥250ms or sentence-end punctuation
6. (Optional) strips ALWAYS-FILLER tokens from the SRT if `--strip-fillers` is passed
7. Invokes `burn-hebrew-captions.sh` which:
   - **Strips sentence-end `.`/`?`/`!` from Hebrew lines by default** (BBC/Netflix caption style). Why: the python-bidi + libass double-reversal recipe is BiDi-stable for letters but punctuation positioning becomes unpredictable depending on script mix. Stripping ends that whole class of failure modes. If you want punctuation back, comment out the `SENTENCE_END` block in Step 0 of `burn-hebrew-captions.sh` , characters and words stay correct either way.
   - Does the python-bidi pre-shape + libass burn with Heebo + verify frames

Output lands at `<input>.captioned.<ext>` next to the source (or wherever `--output` says). The merged SRT is also written next to the output as `<output>.he.srt` for sidecar upload to YouTube/Vimeo (full steps in `references/captions-only-tuning.md`). Verify frames land in a `verify_*/` directory you can open with `open`.

**Tuning:** thresholds (`MAX_WORD_DUR`, `GAP_THRESHOLD`, `TAIL_THRESHOLD`, `MAX_DISPLAY_SEC`), the Scribe v1 / v2 split, and how to disable punctuation-stripping are documented in `references/captions-only-tuning.md`.

**Cost on a real example:** a 1-hour Hebrew lecture costs ~$0.40 in Scribe + ~$1 in Claude tokens for the orchestration around the bash script = **~$1.40 total**. A 3-hour webinar: ~$1.20 + ~$2 = **~$3.20**. Compare to the full cut workflow on the same 3-hour source: **$120-300**.

**When NOT to use this:** if you need to cut the long video down to a short teaser, or pick the best take from multiple recordings of the same content, or rearrange beats for narrative flow, you need the full Steps 1-7 workflow. Captions-only just captions the original.

### Step 9: Sample Hebrew prompts to drive the conversation phase

video-use's "Converse" step (step 3 of "The process") asks questions shaped by the material. Sample Hebrew prompts users send:

| Hebrew user message | What it maps to in the upstream workflow |
|---------------------|------------------------------------------|
| "ערוך את הקבצים האלה לסרטון השקה" | "edit these into a launch video", full inventory then strategy then execute |
| "תנקה את השתיקות ואת המילים המיותרות" | Filler removal + dead-space cuts only |
| "תוסיף כתוביות בעברית במרכז התחתון" | Subtitle generation with Hebrew SUB_FORCE_STYLE override AND `burn-hebrew-captions.sh` |
| "תוסיף גרידינג חם" | `grade.py --filter` with `warm_cinematic` preset (works language-agnostic) |
| "תפצל למקטעים של 30 שניות לאינסטה" | Vertical 1080x1920 reformat with `vertical-social-he` style |
| "תבדוק שאין שגיאות בכתוביות בעברית" | Trigger Step 6 frame-sampling self-eval (glyph fallback + RTL pixel order) |

## Examples

### Example 1: Long lecture, captions-only (most common ask)

User says: *"תוסיף כתוביות לסרטון הזה."* (no editing requested)

Step 0 mode pick: A. Then: `bash scripts/captions-only.sh ~/Movies/lecture.mp4`. Done. Output `lecture.captioned.mp4` + side `lecture.he.srt` for YouTube. ~$1-3 total.

### Example 2: Raw footage to edited cut with captions

User says: *"ערוך את הקבצים האלה לסרטון השקה. תוסיף כתוביות בעברית."*

Step 0 mode pick: B. Then: env check (Step 1), inventory + transcribe + filler post-pass (Steps 2-3), converse + EDL (Steps 4-5), `render.py` produces `base.mp4`, `burn-hebrew-captions.sh` produces `final.mp4`, self-eval per Step 6.

### Example 3: Mixed Hebrew/English tech tutorial

Source phrases like `התקנתי React אבל הוא לא טוען`. Both modes work: `python-bidi.get_display()` preserves "React" as `React` (not `tcaeR`) while reversing the surrounding Hebrew. Verify in Step 6 that mixed-script lines render with English LTR inside RTL flow.

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
| python-bidi | https://github.com/MeirKriheli/python-bidi | `get_display()` for the macOS BiDi workaround |
| ElevenLabs Scribe | https://elevenlabs.io/blog/meet-scribe | Multi-language transcription (Hebrew supported via 99-language model) |
| ElevenLabs pricing | https://elevenlabs.io/pricing | Scribe per-hour cost and free tier limits |

## Bundled Resources

### Scripts

- `scripts/install-hebrew-fonts.sh`: Idempotent installer for Heebo, Rubik, Assistant, Noto Sans Hebrew. macOS (Homebrew cask) and Debian/Ubuntu (apt + manual fallback) paths. Re-runs `fc-cache` and verifies via `fc-list :lang=he`.
- `scripts/burn-hebrew-captions.sh`: The Step 7 caption burn-in recipe in one command. Pre-shapes SRT with python-bidi, converts to ASS, patches PlayRes/Style/Spacing, burns with explicit fontsdir, samples verification frames. Pre-flight checks that ffmpeg has libass and that Hebrew fonts exist before running. Step 0 of the script also sanitizes Scribe garbage characters (Devanagari etc.) with auto-fixes.
- `scripts/captions-only.sh`: The Step 8 cheap path for non-technical users. One command, full video in, captioned full video out. Transcribes via Scribe, builds SRT, optionally strips ALWAYS-FILLER tokens (`--strip-fillers`), then runs burn-hebrew-captions.sh. ~$1-3 total regardless of video length, vs. ~$25-300 for the full cut workflow.

### References

- `references/sub-force-style-hebrew.md`: Three ready-to-use `SUB_FORCE_STYLE` overrides for Hebrew (`bold-overlay-he`, `natural-sentence-he`, `vertical-social-he`). Documents why each value differs from the upstream Latin defaults, including PlayResX/Y and Spacing notes.
- `references/hebrew-filler-words.md`: Annotated Hebrew filler list with editorial guidance (which are always-fillers vs. sometimes-load-bearing). Drop-in for the Step 3 post-pass.
- `references/macos-ffmpeg-setup.md`: Fixes for the common Homebrew ffmpeg-without-libass trap and other macOS-specific gotchas (loudnorm on freeze frames, drawtext fallback to PIL, libass+SRT BiDi failure mode).
- `references/captions-only-tuning.md`: All `captions-only.sh` tunables in one place , thresholds (`MAX_WORD_DUR`, `GAP_THRESHOLD`, `TAIL_THRESHOLD`, `MAX_DISPLAY_SEC`), the Scribe v1 vs v2 split with rationale, the punctuation-stripping default + how to disable, side-output paths, and the full flags reference. Read this before changing any caption behavior.
- `references/quick-test.md`: 10-second synthetic Hebrew test video recipe (uses macOS `say -v Carmit` + ffmpeg). Costs ~$0.001 in Scribe and lets you validate the full pipeline end-to-end without burning your free-tier quota on real footage.

## Gotchas

- **Scribe occasionally drops non-Hebrew Unicode characters into Hebrew transcripts.** Most commonly Devanagari (`्` `स`) at the end of words where the speaker's soft `-s` or `-m` ending sounded ambiguous. Classic failure: "סקילים" transcribed as "סקיל्स". These chars render as boxes in the burn. `burn-hebrew-captions.sh` Step 0 auto-fixes the known patterns and warns on unknown ones; extend `auto_fixes` when you find more.
- **Helvetica is the most common mistake.** The bundled `SUB_FORCE_STYLE` in `render.py` uses `FontName=Helvetica`. Helvetica's Hebrew glyphs do NOT exist in the macOS or Linux Helvetica builds (Apple's "Helvetica" font is Latin-only; Linux usually maps it to a metric-equivalent). libass silently falls back to a tofu box. Always override `FontName` to a known Hebrew font before invoking the caption-burn step.
- **The python-bidi pre-shape + libass ASS-conversion double-reversal is DELIBERATE, not a bug to fix.** It produces a non-canonical layout where Hebrew characters within each word render in source byte order LTR while word order stays RTL (sometimes called the "VSFilter-era" look). This is the user-validated rendering for this skill, not a workaround for a temporary libass bug. If you read older notes that say "feed SRT directly, don't pre-shape" they describe a *different* rendering target (canonical Hebrew BiDi). Both are technically correct; this skill ships the pre-shape recipe because that's what real users preferred during field validation (May 2026). Do NOT "clean up" the python-bidi step or skip the SRT->ASS conversion , doing so silently flips the entire caption layout and will look broken to anyone who validated the current output.
- **Homebrew's default ffmpeg lacks libass and fontconfig.** As of 2026-05, a fresh `brew install ffmpeg` produces a binary that cannot burn captions at all. See `references/macos-ffmpeg-setup.md` for the static-build or homebrew-tap fixes.
- **2-word UPPERCASE chunks do not translate to Hebrew.** Hebrew has no uppercase. Do not try to fake it with `\fnHeebo Bold`, the result looks the same as regular Heebo. The Hebrew kinetic-typography equivalent is bold weight + larger size + tighter line breaks (4-6 Hebrew words per chunk, since Hebrew words are shorter than English on average).
- **`fontsdir=` is more reliable than fontconfig.** Even when `fc-match Heebo` resolves correctly, the `subtitles` filter sometimes ignores fontconfig and falls back to libass's built-in font, producing the wrong typeface in the burned-in output. Always pass `subtitles=foo.ass:fontsdir=$HOME/Library/Fonts` (or wherever Heebo lives per `fc-list :family=Heebo file`).
- **`loudnorm` fails on freeze frames with silent audio.** If your edit ends with a freeze frame that has no audio (or has dead air longer than ~1.5s), `loudnorm` returns `I=-inf` and aborts. Workarounds: layer 2 seconds of room tone over the freeze before rendering, or skip loudnorm entirely with `--no-loudnorm` (audio stays at original levels, no normalization applied).
- **`drawtext` may be missing in static ffmpeg builds** even when other filters work. If you need text overlays outside of subtitles (e.g., a CTA freeze frame caption), test with `ffmpeg -h filter=drawtext` first. If unavailable, generate the overlay via PIL (with `layout_engine=ImageFont.Layout.RAQM` for Hebrew) and composite with ffmpeg's `overlay` filter.
- **Do not pre-translate code-switched English brands.** Users typing "תוסיף ראקט" (transliteration of "React") instead of "React" causes Scribe to transcribe phonetically wrong. Tell the user during the conversation phase: code-switched English stays English in the transcript and in the burned-in caption, Hebrew speakers expect this.
- **`yt-dlp` Hebrew filenames.** When pulling Hebrew sources from URLs, `yt-dlp` writes filenames with Hebrew chars. Subsequent FFmpeg + libass passes work fine on macOS but can break on Linux filesystems with non-UTF-8 locales (`LC_ALL=C` is the common culprit). Set `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8` in the install.md `.env` if you see "No such file" errors on visibly-present files.

## Known Limitations

Gaps we know about so users don't burn cycles on unsupported workflows. Log new symptoms in the skill's GitHub issues.

- **`captions-only.sh` validated up to ~12-min video** (Scribe per-file limit is ~2GB/10hr). At 1hr+ split with `ffmpeg -t` and concat SRTs.
- **`vertical-social-he` 1080×1920 not validated against a real render.** MarginV=120 is theoretical; spot-check against current Instagram/TikTok UI.
- **Heebo alternatives (Rubik/Assistant/Noto Sans Hebrew) listed but not tested as `FontName=`.** Verify with Step 6.
- **Multi-speaker interviews not handled.** `captions-only.sh` hardcodes `diarize=false`, no speaker labels. Use upstream `helpers/transcribe.py --num-speakers N` for interview content.
- **No SDH / accessibility tags** (`[music]`, `[laughter]`). `tag_audio_events=false` is hardcoded. Inject manually for full IS 5568 / ADA compliance.
- **No detection of pre-existing burned-in captions** , double-burns silently. Inspect source first.
- **Scribe garbage-char auto-fix covers 2 patterns.** Add new ones to `auto_fixes` in `burn-hebrew-captions.sh` Step 0.
- **1-3hr cost claim is extrapolated** , agent re-reading the transcript may push upper bound higher.

## Troubleshooting

### One word in the caption renders as a weird non-Hebrew character (Greek/Devanagari/Tamil look)

Cause: Scribe transcribed a Hebrew word with a non-Hebrew Unicode character mixed in. Most common: Devanagari `्स` instead of `ים` at the end of a word with a soft `-s` sound (e.g., the colloquial pronunciation of "סקילים").

Solution: scan the SRT for non-Hebrew/Latin characters and fix them. `burn-hebrew-captions.sh` does this in its Step 0 sanitization pass; if you find a new pattern that auto-fix misses, add it to the `auto_fixes` dict in the script and submit a PR. For ad-hoc one-offs: `sed -i '' 's/סקיל्स/סקילים/g' master.srt` then re-run the burn script.

### Captions render as `□□□` boxes
Cause: libass cannot find a Hebrew font, or ffmpeg lacks libass. Fix: `ffmpeg -version | grep enable-libass` (if empty, see `references/macos-ffmpeg-setup.md`); `fc-list :lang=he` (if empty, run `install-hebrew-fonts.sh`); always pass `fontsdir=$HOME/Library/Fonts` explicitly.

### Captions look "different than expected" , chars within words read LTR not RTL
Deliberate (see the Gotchas double-reversal note). To switch to canonical Hebrew BiDi: skip the python-bidi pre-shape (Step 1 of `burn-hebrew-captions.sh`) AND skip the SRT->ASS conversion (Step 2), feeding the source SRT directly to `subtitles=`. Both layouts render valid Hebrew, pick by audience preference.

### Captions have no periods or question marks
Default behavior since v1.2.6: `burn-hebrew-captions.sh` Step 0 strips trailing `.`/`?`/`!` from any caption line containing Hebrew. BBC/Netflix caption style guides recommend this because line breaks and timing already signal end-of-thought. To restore punctuation, comment out the `SENTENCE_END` block in the Step 0 Python heredoc of `burn-hebrew-captions.sh`. Full rationale + alternatives in `references/captions-only-tuning.md`.

### Scribe gap-recovery itself returned an HTTP error
Symptom: `captions-only.sh` logs `WARN: gap re-transcribe returned HTTP <code>, skipping` and that window stays uncaptioned. Cause: Scribe v2 occasionally rate-limits, times out, or rejects very short or mid-word windows. Fix: (1) re-run the script , cached bulk transcript means only the failed gap retries, no extra base cost; (2) if it fails twice, extract a slightly wider window manually (`ffmpeg -ss <start-1> -t <dur+2>`), curl Scribe yourself, drop words into the cached `scribe.json`; (3) lower `GAP_THRESHOLD` to 20s so recovery splits long failing windows.

### Wrong font (not Heebo) despite Heebo installed
Cause: libass fell back to its built-in font because fontconfig integration is unreliable. Fix: pass `fontsdir=$HOME/Library/Fonts` explicitly to `subtitles=`.

### Captions render at tiny size on HD output
Cause: ffmpeg's SRT->ASS default is `PlayResX: 384, PlayResY: 288` and libass scales font size relative to PlayResY. Fix: set PlayResX/Y to match output. `burn-hebrew-captions.sh` does this automatically.

### Filler removal cut English but left Hebrew
Cause: Scribe doesn't tag fillers in any language; you skipped the Hebrew lexicon post-pass. Fix: apply `references/hebrew-filler-words.md` to Scribe word timestamps before computing cut candidates.

### Local renders fine but cloud render shows boxes
Cause: cloud container has no Hebrew fonts. Fix: add `install-hebrew-fonts.sh` to the container build step, or bundle Heebo into `<edit>/fonts/` and pass `fontsdir=<edit>/fonts`.

### `loudnorm` errors with `I=-inf`
Cause: video ends with silence (freeze frame with no audio). Fix: layer 2s of room tone over the silent portion, OR pass `--no-loudnorm` to `render.py`.
