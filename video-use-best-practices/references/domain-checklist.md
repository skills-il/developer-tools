# Domain Coverage Checklist, video-use-best-practices

Generated: 2026-05-16. Last revised: 2026-11-11 (v1.4.0): upstream re-diffed to `43cfc56`, out-of-scope rows re-litigated, coverage pointers re-checked. Research sources: github.com/browser-use/video-use SKILL.md+install.md, github.com/libass/libass wiki, ffmpeg.org/ffmpeg-filters.html, www.unicode.org/reports/tr9/, fonts.google.com, hyperframes-best-practices and remotion-best-practices skills in skills-il directory.

## Must cover (core)

- [x] **SUB_FORCE_STYLE override for Helvetica** , source: upstream SKILL.md "Worked styles" + render.py SUB_FORCE_STYLE constant , why core: this is the single most-common Hebrew failure mode (boxes burned into the final video). Covered in Step 2 + references/sub-force-style-hebrew.md.
- [x] **Hebrew filler-word post-pass** , source: ElevenLabs Scribe does not tag fillers per word in any language (word `type` is word/spacing/audio_event only) , why core: upstream "filler removal" feature is the headline benefit, and it does not work for Hebrew speakers without this list. Covered in Step 3 + references/hebrew-filler-words.md.
- [x] **fontconfig + libass font discovery** , source: libass/libass wiki , why core: even with a correct SUB_FORCE_STYLE FontName, libass fails silently if fontconfig cannot resolve the name to an installed font. Covered in Step 1 + scripts/install-hebrew-fonts.sh.
- [x] **SRT UTF-8 BOM requirement** , source: libass ASS File Format Guide ("a UTF-8 BOM SHOULD be added at the start") , why core: render.py writes SRT without BOM. `burn-hebrew-captions.sh` writes its working SRT copies with a BOM. Direction itself is fixed by the pre-shape, not by the BOM.
- [x] **Animation engine routing to existing Hebrew skills** , source: hyperframes-best-practices and remotion-best-practices skills exist with Hebrew/RTL coverage , why core: video-use ships with HyperFrames + Remotion + Manim + PIL as overlay engines; skills-il already has dedicated Hebrew skills for the two web-based engines. Covered in Step 5 + references/animation-slots.md.
- [x] **Hard Rules deference** , source: upstream SKILL.md "Hard Rules (production correctness, non-negotiable)" , why core: this skill is an OVERLAY, not a replacement. Specializing rules 1, 3, 5, 6 for Hebrew without contradicting them is the whole point. Covered throughout, made explicit in Instructions preamble.

## Should cover (advanced / edge cases)

- [x] **Code-switching with English brand names** , source: common in Israeli tech tutorials , why important: mixed-script SRT rendering breaks differently than pure Hebrew (BiDi algorithm activates per-line). Covered in Step 4, Example 2, Self-eval Step 6.
- [x] **Sofit forms (ם ן ץ ף ך) and nikud in Scribe output** , source: Hebrew orthography , why important: Scribe occasionally produces middle-of-word sofit or surprise nikud; downstream display assumes the canonical form. Covered in Step 4 item 3.
- [x] **Self-eval checks for Hebrew (glyph fallback + direction)** , source: upstream self-eval step 7 , why important: upstream's 4 visual checks do not catch the two most common Hebrew render failures. Covered in Step 6 items 5+6.
- [x] **Vertical social (1080x1920) MarginV** , source: upstream `helpers/render.py` SUB_FORCE_STYLE, which ships `Alignment=2,MarginV=90` against libass default `PlayResY=288` (31.25% of frame height) with the comment "TikTok / IG Reels / Shorts UI ... covers roughly the bottom ~25-30% of a 1080x1920 frame ... Do not drop this below ~75 without a specific reason" , why important: `burn-hebrew-captions.sh` rewrites PlayResY to the real frame height, which changes the unit MarginV is expressed in, so a fixed MarginV=80 silently became 4.2% and buried the captions inside the platform UI band. Fixed in v1.3.0 by scaling font size and margin as ratios of frame height. **NOTE: upstream's own SKILL.md prose says `MarginV=35`; its shipped code says 90. The code is ground truth.** Covered in Step 7 + references/sub-force-style-hebrew.md.
- [x] **Hebrew prompts table for conversation phase** , source: upstream "Converse" step + common Hebrew creator workflows , why important: video-use's conversation phase is shaped by user prompts; non-Hebrew creators will not know what natural Hebrew requests map to the upstream workflow. Covered in references/conversation-prompts.md (moved out of SKILL.md at v1.4.0 for the word cap).
- [x] **Caption chunk size under upstream's new chunker** , source: upstream render.py `chunk_words()` with `CHUNK_WORDS=2`, `CHUNK_MAX_WORDS=3` (commit b877063) , why important: the Hebrew 4-6 word guidance cannot be applied through SUB_FORCE_STYLE. Covered in Step 2.
- [x] **Upstream Mode B transcription still sends scribe_v1** , source: upstream helpers/transcribe.py at 43cfc56 , why important: the full-cut path inherits a deprecated model. Covered in Step 1.

## Out of scope (explicit, with rationale)

- **ASS Encoding=177 historical Hebrew code page** , out: libass guide says Encoding MUST be 1 for modern UTF-8 workflows; the 177 value is legacy Windows-charset trivia that adds noise without helping. Stay on the canonical "UTF-8 with BOM + Encoding=1" path.
- **Whisper local transcription for the Mode B cut** , out (re-checked 2026-11-11): upstream's anti-patterns forbid phrase-level transcripts for cutting. A user could ask for a free path, so `references/pricing.md` documents Whisper as a burn-in-only fallback with word timestamps; the cut workflow stays Scribe-only.
- **Hebrew RSS / podcast distribution** , out: covered by sibling skill `hebrew-podcast-postproduction` for audio-only podcasts. video-use is video-first.
- **ASR for Yiddish, Aramaic, Ladino** , out: ElevenLabs Scribe does not currently advertise these. Hebrew only.
- **Cantillation marks (te'amim) in subtitles** , out (re-checked 2026-11-11): an ordinary caption user does not ask for them, and religious-text video has its own conventions. Nikud (vowel points) is different and IS handled: a pointed caption was rendered through the pre-shape on 2026-11-11 and the marks stayed on their base letters.
- **TTS Hebrew voiceover** , out: covered separately by `hyperframes-best-practices` and `remotion-best-practices` (both document Hebrew TTS via external providers since Kokoro does not support Hebrew). video-use does not have a TTS stage.
- **Right-to-left video orientation** , out: RTL is a text-direction concern, not a video-frame concern. Hebrew creators record left-to-right cameras like everyone else.

## Known failure modes (mitigated)

These are Scribe / libass failure modes discovered during real-use validation. Each has a programmatic mitigation in `scripts/captions-only.sh` or `scripts/burn-hebrew-captions.sh`. Listed here so the next `update-skill` run recognizes them as covered and doesn't re-discover them as "gaps".

- [x] **Scribe silently drops 30s+ chunks of speech mid-file or at the tail** , mitigation: `captions-only.sh` v1.2.7+ auto-detects gaps (>30s mid-file or >10s untranscribed tail) and re-transcribes each isolated window with `scribe_v2`, then merges the recovered words back into the main transcript. Documented in Step 8 and `references/captions-only-tuning.md`.
- [x] **Scribe occasionally emits a single "word" with 80+s duration** , mitigation: `captions-only.sh` clips any word with duration > `MAX_WORD_DUR` (default 2.0s). Without clipping, a single freak cue would freeze on screen for the full duration. Tunable in `references/captions-only-tuning.md`.
- [x] **Punctuation positioning unstable under python-bidi + libass double-reversal** , mitigation: `burn-hebrew-captions.sh` Step 0 strips trailing `.`/`?`/`!` from Hebrew lines by default (BBC/Netflix style). Disable rationale + how-to in `references/captions-only-tuning.md`. Troubleshooting entry: "Captions have no periods or question marks".
- [x] **ElevenLabs free-tier limit is credit-based (10,000 credits/month), not per-hour or per-character** , mitigation: pricing section states STT costs ~330 credits/min (~30 minutes of transcription/month) so non-technical users understand they get only a couple of short videos a month. Quick-test recipe in `references/quick-test.md` lets users validate the pipeline without burning the quota.
- [x] **libass wraps pre-shaped lines in the wrong order** , mitigation: `burn-hebrew-captions.sh` v1.4.0 splits long lines in logical order BEFORE the pre-shape. Without it, a wrapped cue put the end of the sentence on the top line (measured on a 1080x1920 render).
- [x] **Agent shells have no terminal for the cost prompt** , mitigation: `captions-only.sh` v1.4.0 exits 3 with the estimate instead of dying silently in `read`; the agent relays the estimate and re-runs with `--yes`.
- [x] **Gap recovery sent no URL** , mitigation: fixed in v1.4.0. Before it, any detected gap aborted the run after the paid main transcription (`curl: (2) no URL specified` under `set -e`). Recovery calls are now capped (`--max-gap-calls`).
- [x] **Pre-shape recipe is deliberate, not an accident** , mitigation: the Gotchas and Troubleshooting entries both flag the double reversal as DELIBERATE, and say the pre-shape is mandatory. There is deliberately NO canonical-BiDi escape hatch: on macOS libass does not reorder, so feeding a raw SRT renders reversed. FFmpeg's documented `shaping=complex` was tested on 2026-08-26 and does not substitute for the pre-shape (shaping is glyph substitution, not reordering). Prevents future maintainers from "fixing" the working render.

## Authoritative sources

- https://github.com/browser-use/video-use , upstream SKILL.md, install.md, helpers/. **Pin by HEAD SHA, not by version:** the repo has no tags, no releases and no published package, so "re-check on a minor version bump" is an inert trigger. Last validated against `43cfc56` (2026-10-08). Changes since `92c2b34` that this skill tracks: source frame rate preserved by default plus `--fps` (0c40770), rotation-aware portrait detection (b5352cf), `--audio-track` and silent-track refusal in transcribe.py (9575612), phrase-aware `chunk_words()` and a hard exit on a missing subtitles file (b877063). `helpers/transcribe.py` still sends the deprecated `scribe_v1`, so this skill overrides upstream there.
- https://elevenlabs.io/pricing and https://elevenlabs.io/pricing/api , Scribe rate card and credit rates. Re-check on EVERY cycle that touches cost text; pricing changed twice in 2026.
- https://elevenlabs.io/docs/api-reference/speech-to-text/convert , current `model_id` enum. `scribe_v1` deprecated, removal scheduled for 2026-07-09 per the ElevenLabs changelog.
- https://github.com/libass/libass/wiki/ASS-File-Format-Guide , UTF-8 BOM rule, Encoding=1 rule, alignment numpad layout.
- https://ffmpeg.org/ffmpeg-filters.html , `subtitles=` filter syntax, libass build dependency.
- https://www.unicode.org/reports/tr9/ , UAX #9 BiDi algorithm, directional isolation for mixed-script text.
- https://fonts.google.com/specimen/Heebo , license, weights, character coverage.
- https://fonts.google.com/noto/specimen/Noto+Sans+Hebrew , maximum-coverage fallback.
- https://elevenlabs.io/blog/introducing-scribe-v2 , Scribe v2 announcement.
- https://github.com/google/fonts , source of the pinned, checksummed TTFs `install-hebrew-fonts.sh` installs.
- https://formulae.brew.sh/formula/ffmpeg-full , the libass-enabled Homebrew formula.

## Update triggers

- video-use cuts a release that adds, removes, or renames any of: render.py, SUB_FORCE_STYLE, helpers/transcribe.py, helpers/pack_transcripts.py, helpers/timeline_view.py, helpers/grade.py, project.md format, EDL JSON schema.
- ElevenLabs Scribe ships native Hebrew filler tagging (would make Step 3 redundant).
- libass cuts a release that changes the BOM requirement or default Encoding behavior.
- A new Hebrew Google Font appears that is better-suited than Heebo for the kinetic-typography use case.
