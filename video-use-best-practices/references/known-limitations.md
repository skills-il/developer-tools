# Known limitations, video-use-best-practices

Moved out of SKILL.md at v1.3.1 to stay under the 5,000-word body cap.
Read this before promising a behaviour the skill has not actually validated.

Gaps we know about so users don't burn cycles on unsupported workflows. Log new symptoms in the skill's GitHub issues.

- **`captions-only.sh` validated up to ~12-min video.** It uploads extracted 64 kbps mono AAC (about 29 MB per hour), far under Scribe's documented file-size limit ("less than 5.0GB"), so long files are not blocked by size; long-file behaviour beyond the gap recovery is still unmeasured.
- **`vertical-social-he` 1080x1920 not validated against a real render.** MarginV=120 (41.7% of frame height at PlayResY=288) is theoretical; spot-check against current Instagram/TikTok UI.
- **Heebo alternatives (Rubik/Assistant/Noto Sans Hebrew) listed but not tested as `FontName=`.** Verify with Step 6.
- **Multi-speaker interviews not handled.** `captions-only.sh` hardcodes `diarize=false`, no speaker labels. Use upstream `helpers/transcribe.py --num-speakers N` for interview content.
- **No SDH / accessibility tags** (`[music]`, `[laughter]`). `tag_audio_events=false` is hardcoded. Inject manually for full IS 5568 / ADA compliance.
- **No detection of pre-existing burned-in captions** , double-burns silently. Inspect source first.
- **The side `.he.srt` keeps Scribe garbage characters.** The auto-fix runs inside the burn step, after the sidecar copy, so the burned captions are fixed but the sidecar is not. Run the same fix on the sidecar before uploading it.
- **Burned captions are Heebo only.** `burn-hebrew-captions.sh` refuses any other `--font`: its line-width estimate is measured on Heebo, and auto-wrap is disabled to protect line order, so an unmeasured wider font (e.g. Arial Hebrew) could run off the frame.
- **The transcribed track is not made the default.** All audio tracks are copied; a player that picks track 0 may play the game/desktop track of an OBS recording.
- **Linux libass behaviour is unmeasured.** The pre-shape is validated on macOS only; the script warns on other systems. Check the first verification frame before a long render.
- **Scribe garbage-char auto-fix covers 2 patterns.** Add new ones to `auto_fixes` in `burn-hebrew-captions.sh` Step 0.
- **1-3hr cost claim is extrapolated** , agent re-reading the transcript may push upper bound higher.
