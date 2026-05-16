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

video-use is a free open-source skill, but the underlying services it calls are paid. **The price depends entirely on which mode you use.** Read this before you transcribe your first file.

### Two modes, very different prices

| Mode | What it does | Best for | Cost on 1-hour video |
|------|--------------|----------|----------------------|
| **A. Captions-only** (`scripts/captions-only.sh`) | Transcribes the video, burns Hebrew captions on the original. No cuts, no edit, no agent loop. | Lectures, webinars, full talks, podcast videos. Anyone who wants captions on a full video without editing. | **~$1-3 total** (~$0.40 Scribe + ~$1-2 Claude orchestration) |
| **B. Full cut workflow** (the default video-use flow) | Inventory → strategy → cut decisions → render → self-eval. Produces a curated edit from raw footage. | Cutting a long recording into a short teaser. Multi-take selection. Creative edit work. | **~$25-60** on a 1-hour source; **$120-300** on a 3-hour source. Scales super-linearly with duration because the agent re-reads the transcript across turns. |

| Service | Provider | Per-unit cost |
|---------|----------|---------------|
| Speech-to-text | ElevenLabs Scribe | ~$0.40 / hour of audio. Free tier covers ~10 hours/month. Cached per source file, so re-runs cost nothing. |
| Agent orchestration | Anthropic Claude | Depends on mode (see table above). Caption-only ≈ flat $1-3. Full cut scales with transcript length. |
| Local rendering | Your machine | $0. All FFmpeg + libass + Heebo work happens locally. |

**Real numbers from a validated test run** (May 2026, 11:29 Hebrew source → 75s teaser via Full cut mode):
- Scribe: ~$0.08 (one transcription)
- Claude API: $2.34 (strategy) + $7.16 (cut + self-eval + 1 re-render) = $9.50
- Total: **~$9.60** for first pass, ~$1-3 per follow-up iteration

### Pick the mode that matches your goal

**If you have a long video and just want captions on it** (the most common non-technical request), use captions-only. It's 20-100x cheaper than the full workflow and produces the same caption quality. Skip the rest of this skill and jump to Step 9.

**If you have raw footage and want a curated edit** (talking-head highlights, multi-take montage, teaser cut), use the full workflow. That's what the rest of the steps below cover.

### Budget tips

1. **Always start with captions-only mode if you're not sure.** If the captioned full video is enough, you saved ~$50. If you decide to cut later, the Scribe transcript is cached.
2. **For the full cut workflow, start with a transcribe-and-propose run only** (no cuts). Costs ~$2 and tells you whether the agent's strategy matches what you wanted before committing.
3. **Use `claude -p` headless mode for long mechanical phases.** Interactive sessions cost more per turn.

**One pricing trap to avoid:** `no_verbatim=true` on Scribe sounds like it saves money by dropping fillers, but it's destructive, your editor agent loses the ability to make per-instance keep/cut decisions, which usually leads to a re-transcription later. Keep `no_verbatim=false` (the default) and run the Hebrew lexicon post-pass instead.

## Instructions

This skill is an **overlay** on top of video-use's upstream SKILL.md. Read the upstream SKILL.md first for the 12 Hard Rules, the EDL JSON schema, `takes_packed.md`, `render.py`, and the parallel-animation pattern. Then apply the Hebrew deltas below.

### Step 0 (MANDATORY FIRST QUESTION): Ask the user which mode they want

Before transcribing, before checking env, before anything else, ask the user this question in plain Hebrew (or English if they wrote in English). Do NOT assume the answer based on file length or filename, ask explicitly. Most users who land here want option A and don't know about option B; some users want B and would waste $50 finding out captions-only would have done it.

> *"איזה משני המסלולים אתה רוצה?*
>
> *(א) כתוביות בלבד על כל הסרטון, בלי חיתוך, בלי עריכה. עולה כ-$1 עד $3 לכל סרטון בכל אורך. מתאים להרצאה, וובינר, פודקאסט, או כל סרטון שאתה רוצה לצרוב עליו כתוביות בעברית בלי לערוך אותו.*
>
> *(ב) חיתוך וערוך לטיזר/קליפ קצר, עם כתוביות. עולה כ-$10 עד $300 תלוי באורך המקור. מתאים אם אתה רוצה להפיק קליפ קצר מחומר גלם ארוך, לבחור best takes, או לסדר ביטים מחדש."*

Or in English: *"Which path do you want? (A) Just captions on the full video, no cuts (~$1-3 any length) or (B) Cut + edit into a teaser with captions (~$10-300 depending on source length)?"*

Route based on answer:
- **A → captions-only**: skip to Step 8 (captions-only mode). Steps 1-7 are not needed for this path.
- **B → full cut workflow**: continue with Step 1 onward.
- **Unsure / "do both"**: recommend A first. If the captioned full video isn't enough, the Scribe transcript is already cached and the B path becomes ~$0.08 cheaper.

This question replaces the upstream's "Converse" step 3 framing for the first turn. After they pick, you can still ask the upstream's content-shaped questions (target length, aspect, must-keep moments) within whichever path they chose.

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

This is the proven recipe for getting Hebrew captions burned in correctly with RTL ordering, proper font, and adequate spacing. The bundled `scripts/burn-hebrew-captions.sh` does all of this in one command, but understand the four moves so you can debug:

1. **Pre-shape the SRT with python-bidi.** Convert each Hebrew caption line from logical order (the order you wrote / Scribe transcribed) to display order (the order pixels need to be drawn LTR to produce a correct RTL visual). This bypasses libass's broken BiDi entirely.
   ```python
   from bidi.algorithm import get_display
   display_text = get_display(logical_text)   # "ספריית הסקילז AI שבניתי." → ".יתינבש AI זליקסה תיירפס"
   ```
   The pre-shaped text looks "scrambled" when you read it, but that's the point: libass draws it character-by-character LTR, and the result looks RTL-correct on screen.

2. **Convert pre-shaped SRT to ASS with `ffmpeg -i master_bidi.srt master_bidi.ass`.** ASS gives libass explicit style metadata.

3. **Patch the ASS file:**
   - `PlayResX/PlayResY` to match output resolution (ffmpeg defaults to 384x288, which renders fonts comically small at 1280x720)
   - Replace the `Default` style line with Heebo at the right size, with `Spacing=2` for letter tracking and `Encoding=1` per the libass rule

4. **Burn with explicit `fontsdir=`:** `subtitles=master_bidi.ass:fontsdir=$HOME/Library/Fonts`. The `fontsdir` parameter is more reliable than fontconfig discovery in static FFmpeg builds.

One-line invocation via the bundled script:

```bash
bash scripts/burn-hebrew-captions.sh \
  --base   edit/base.mp4 \
  --srt    edit/master.srt \
  --out    edit/final.mp4 \
  --ffmpeg /tmp/ffmpeg
```

After it runs, open the PNGs in the `verify_*/` directory it creates and apply the Step 6 checks.

### Step 8: Long video, captions-only mode (cheap path for non-editors)

**Use this when:** the user has a full lecture, webinar, podcast video, or talking-head recording, and just wants Hebrew captions burned in on the whole thing. No cuts. No editing. No multi-take selection. This is by far the most common request from non-technical users, and the full Steps 1-7 workflow is overkill (and 20-100x more expensive) for it.

The bundled `scripts/captions-only.sh` collapses the full workflow into one command:

```bash
# Basic: just add captions
bash scripts/captions-only.sh ~/Movies/my-lecture.mp4

# Add captions AND remove "אה / אהה / אם" filler words from the on-screen text
# (audio stays untouched, words just won't appear in captions):
bash scripts/captions-only.sh ~/Movies/my-lecture.mp4 --strip-fillers

# With custom output path and a static ffmpeg
bash scripts/captions-only.sh ~/Movies/my-lecture.mp4 \
  --output ~/Movies/my-lecture-with-captions.mp4 \
  --ffmpeg /tmp/ffmpeg
```

What it does, end-to-end:
1. Auto-detects `ELEVENLABS_API_KEY` from env or `~/Developer/video-use/.env`
2. Probes the video duration and prints the estimated Scribe cost
3. Transcribes the full video via Scribe with `language_code=heb` and `timestamps_granularity=word`
4. Builds an SRT chunking 5-7 words per caption, breaking on silence ≥250ms or sentence-end punctuation
5. (Optional) strips ALWAYS-FILLER tokens from the SRT if `--strip-fillers` is passed
6. Invokes `burn-hebrew-captions.sh` which does the python-bidi pre-shape + libass burn with Heebo + verify frames

Output lands at `<input>.captioned.<ext>` next to the source (or wherever `--output` says). Verify frames land in a `verify_*/` directory you can open with `open`.

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

### Example 1: 30-minute Hebrew talking-head to 5-minute edited cut with captions

User says: *"ערוך את הקבצים האלה לסרטון השקה. תוסיף כתוביות בעברית."*

Actions:
1. **Environment check (Step 1).** Verify libass+fontconfig in ffmpeg, Hebrew fonts installed, python-bidi installed. Install whatever's missing.
2. **Inventory.** `ffprobe` all sources, `transcribe_batch.py` against the directory (Scribe handles Hebrew automatically, no language flag needed), `pack_transcripts.py`.
3. **Pre-scan.** Read `takes_packed.md`. Note Hebrew slips. Do NOT rely on Scribe filler tags (it has none).
4. **Hebrew filler post-pass.** Apply the list from Step 3 to Scribe JSON. Add filler timestamps to the cut-candidate set.
5. **Converse + propose strategy** in Hebrew. Confirm target length, vertical or horizontal, Heebo as default.
6. **Execute.** Editor sub-agent produces `edl.json` with word-boundary cuts (Hard Rule 6) snapped via Scribe timestamps.
7. **Render base video** with `render.py` (without captions yet). Produces `base.mp4`.
8. **Burn captions** via `scripts/burn-hebrew-captions.sh` (Step 7 recipe). Produces `final.mp4` with correct RTL Hebrew.
9. **Self-eval (Step 6).** Open the auto-sampled verify PNGs, check glyph rendering AND pixel RTL order.
10. **Persist** to `project.md` in Hebrew or English (user choice, video-use is locale-blind for memory).

Result: 5-minute Hebrew video with Heebo-rendered RTL captions in correct visual order, fillers cut, 30ms fades at every boundary.

### Example 2: Mixed Hebrew/English tech tutorial with code-switching

User says: *"ערוך את ההקלטה של המדריך React הזה."*

Actions:
1. Same environment + inventory + transcribe pipeline.
2. `takes_packed.md` shows phrases like `[045.12-049.87] S0 התקנתי React אבל הוא לא טוען`. Do not normalize.
3. Cut decisions on word boundaries, the boundary between "React" and "אבל" is in Scribe JSON regardless of script change.
4. **Critical:** the SRT contains the mixed line in logical order. python-bidi `get_display()` correctly handles the embedded LTR run for "React" , preserves "React" as "React" (not "tcaeR") while reversing the surrounding Hebrew. Verify in Step 6 self-eval that "React" appears as `React` LTR within the RTL flow.

Result: Tutorial video where Hebrew narration reads RTL and English code/library names render LTR inline.

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

## Gotchas

- **Scribe occasionally drops non-Hebrew Unicode characters into Hebrew transcripts.** Most commonly Devanagari (`्` U+094D, `स` U+0938) at the end of words where the speaker's soft `-s` or `-m` ending sounded ambiguous. The classic failure mode: "סקילים" (skills, plural) transcribed as "סקיל्स" with two Devanagari characters instead of `ים`. These chars then render as boxes or wrong shapes in the burned-in caption. Always scan the SRT for non-Hebrew/Latin characters before burning. `burn-hebrew-captions.sh` does this automatically in its Step 0 sanitization pass with auto-fixes for common Scribe failure modes (extend the `auto_fixes` dict as you encounter more). To scan manually: `python3 -c "import re; bad=[(ln,line,[(c,hex(ord(c))) for c in line if not re.match(r'[֐-׿a-zA-Z0-9 .,!?\\\"\\'():;\\-]', c)]) for ln,line in enumerate(open('master.srt').read().split('\\n'),1) if '-->' not in line]; bad=[x for x in bad if x[2]]; [print(b) for b in bad]"`.
- **Helvetica is the most common mistake.** The bundled `SUB_FORCE_STYLE` in `render.py` uses `FontName=Helvetica`. Helvetica's Hebrew glyphs do NOT exist in the macOS or Linux Helvetica builds (Apple's "Helvetica" font is Latin-only; Linux usually maps it to a metric-equivalent). libass silently falls back to a tofu box. Always override `FontName` to a known Hebrew font before invoking the caption-burn step.
- **libass + SRT BiDi is silently broken on macOS.** Even with `--enable-libass --enable-fontconfig --enable-libharfbuzz` all present in the ffmpeg build, the SRT path frequently does NOT apply BiDi character reordering. Captions appear with characters in source byte order (period on the right, first word on the left). The "convert SRT to ASS" workaround alone does NOT fix this. The reliable fix is to pre-shape the text with python-bidi BEFORE converting to ASS. The bundled `burn-hebrew-captions.sh` does this automatically.
- **Homebrew's default ffmpeg lacks libass and fontconfig.** As of 2026-05, a fresh `brew install ffmpeg` produces a binary that cannot burn captions at all. See `references/macos-ffmpeg-setup.md` for the static-build or homebrew-tap fixes.
- **2-word UPPERCASE chunks do not translate to Hebrew.** Hebrew has no uppercase. Do not try to fake it with `\fnHeebo Bold`, the result looks the same as regular Heebo. The Hebrew kinetic-typography equivalent is bold weight + larger size + tighter line breaks (4-6 Hebrew words per chunk, since Hebrew words are shorter than English on average).
- **`fontsdir=` is more reliable than fontconfig.** Even when `fc-match Heebo` resolves correctly, the `subtitles` filter sometimes ignores fontconfig and falls back to libass's built-in font, producing the wrong typeface in the burned-in output. Always pass `subtitles=foo.ass:fontsdir=$HOME/Library/Fonts` (or wherever Heebo lives per `fc-list :family=Heebo file`).
- **`loudnorm` fails on freeze frames with silent audio.** If your edit ends with a freeze frame that has no audio (or has dead air longer than ~1.5s), `loudnorm` returns `I=-inf` and aborts. Workarounds: layer 2 seconds of room tone over the freeze before rendering, or skip loudnorm entirely with `--no-loudnorm` (audio stays at original levels, no normalization applied).
- **`drawtext` may be missing in static ffmpeg builds** even when other filters work. If you need text overlays outside of subtitles (e.g., a CTA freeze frame caption), test with `ffmpeg -h filter=drawtext` first. If unavailable, generate the overlay via PIL (with `layout_engine=ImageFont.Layout.RAQM` for Hebrew) and composite with ffmpeg's `overlay` filter.
- **Do not pre-translate code-switched English brands.** Users typing "תוסיף ראקט" (transliteration of "React") instead of "React" causes Scribe to transcribe phonetically wrong. Tell the user during the conversation phase: code-switched English stays English in the transcript and in the burned-in caption, Hebrew speakers expect this.
- **`yt-dlp` Hebrew filenames.** When pulling Hebrew sources from URLs, `yt-dlp` writes filenames with Hebrew chars. Subsequent FFmpeg + libass passes work fine on macOS but can break on Linux filesystems with non-UTF-8 locales (`LC_ALL=C` is the common culprit). Set `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8` in the install.md `.env` if you see "No such file" errors on visibly-present files.

## Troubleshooting

### One word in the caption renders as a weird non-Hebrew character (Greek/Devanagari/Tamil look)

Cause: Scribe transcribed a Hebrew word with a non-Hebrew Unicode character mixed in. Most common: Devanagari `्स` instead of `ים` at the end of a word with a soft `-s` sound (e.g., the colloquial pronunciation of "סקילים").

Solution: scan the SRT for non-Hebrew/Latin characters and fix them. `burn-hebrew-captions.sh` does this in its Step 0 sanitization pass; if you find a new pattern that auto-fix misses, add it to the `auto_fixes` dict in the script and submit a PR. For ad-hoc one-offs: `sed -i '' 's/סקיל्स/סקילים/g' master.srt` then re-run the burn script.

### Captions render as `□□□` boxes in the final video

Cause: libass cannot find a Hebrew-capable font, OR the ffmpeg build is missing libass entirely.
Solution (in order):
1. Run `ffmpeg -version | grep enable-libass` , if empty, you have the Homebrew-without-libass problem. Fix via `references/macos-ffmpeg-setup.md`.
2. Run `fc-list :lang=he` , if empty, `bash scripts/install-hebrew-fonts.sh`, then `fc-cache -f -v`.
3. Pass `fontsdir=` explicitly to the `subtitles` filter, not just relying on fontconfig: `subtitles=master.ass:fontsdir=$HOME/Library/Fonts`.
4. Re-render and re-check via Step 6 frame sampling.

### Hebrew captions render in correctly-shaped letters but words/letters are in wrong visual positions

Cause: libass did not apply BiDi reordering. This is the #1 Hebrew failure on macOS. Symptoms: period appears on the right side instead of the left; first word of the sentence appears on the visual left instead of the visual right; the entire line reads "English-style" left-to-right with Hebrew shapes.

Solution: pre-shape the SRT with python-bidi BEFORE rendering. The bundled `scripts/burn-hebrew-captions.sh` does this automatically. Manual version:

```python
from bidi.algorithm import get_display
# For each caption line in your SRT, replace:
new_line = get_display(original_hebrew_line)
```

Then convert the pre-shaped SRT to ASS, patch with Heebo style + Spacing=2 + correct PlayRes, and burn with `fontsdir=`. See Step 7 for the full recipe.

Note: converting SRT to ASS alone (`ffmpeg -i master.srt master.ass`) is NOT sufficient. libass still skips BiDi in the ASS path on macOS. The pre-shape step is non-optional.

### Captions appear with wrong font (visibly different from Heebo) even though Heebo is installed

Cause: libass fallback to its built-in font because fontconfig integration in the running ffmpeg is unreliable.
Solution: pass `fontsdir=` parameter explicitly to the `subtitles` filter. Find the directory with `dirname "$(fc-list :family=Heebo file | head -1 | sed 's/: $//')"`.

### Captions render at tiny size (4-6 pixels tall) on a 1280x720 output

Cause: ffmpeg's auto-conversion of SRT to ASS defaults to `PlayResX: 384, PlayResY: 288`. libass scales font size relative to PlayResY, so `Fontsize=22` at PlayResY=288 means ~7.6% of frame height, which at 1280x720 output looks like ~55 pixels. But if you didn't bump PlayResY to 720, font sizes you tune for 720p look right in preview but render at 288p scale on output.
Solution: in the ASS file, set `PlayResX` and `PlayResY` to match your output resolution. `burn-hebrew-captions.sh` does this automatically by probing the base video.

### Filler removal cut English fillers but left Hebrew fillers

Cause: ElevenLabs Scribe does not tag fillers in any language; you skipped the Hebrew lexicon post-pass.
Solution: Apply the `references/hebrew-filler-words.md` list to Scribe word timestamps before computing cut candidates. Re-run the editor sub-agent.

### Self-eval Step 6 passes locally but cloud render shows boxes

Cause: Local has Hebrew fonts via fontconfig; cloud renderer (Linux container without fonts) does not.
Solution: Add `scripts/install-hebrew-fonts.sh` to the container build step. Or bundle `Heebo[wght].ttf` into `<edit>/fonts/` and pass `subtitles=master.ass:fontsdir=<edit>/fonts` to the burn step.

### `loudnorm` errors out with `I=-inf`

Cause: The video ends with silence (most commonly a freeze frame with no audio).
Solution: layer 2 seconds of room tone over the silent portion before running loudnorm, OR pass `--no-loudnorm` to `render.py` to skip normalization (your audio stays at original mixed levels). For a polished release, the room-tone approach is preferred.
