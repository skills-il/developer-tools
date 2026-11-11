#!/usr/bin/env bash
# captions-only.sh
#
# For non-technical users: take a video, transcribe Hebrew, burn captions, done.
# No cuts. No editing. No agent orchestration loop. Just captions on the original.
#
# Usage:
#   captions-only.sh <video.mp4> [options]
#
# Options:
#   --strip-fillers       Remove ALWAYS-FILLER tokens (אה, אממ, אהמ...) by
#                         omitting them from the SRT. Speech timing preserved
#                         (no audio cuts, just words you don't see).
#   --output PATH         Output path (default: <video>.captioned.<ext>)
#   --font NAME           Caption font (default and only accepted value: Heebo)
#   --font-size N         Font size in output pixels. Default "auto": scaled
#                         from the video height by burn-hebrew-captions.sh.
#   --margin-v N          Bottom margin in output pixels. Default "auto", same.
#   --fontsdir PATH       Font directory passed to libass. Default is per-platform
#                         (~/Library/Fonts on macOS, ~/.local/share/fonts elsewhere).
#   --ffmpeg PATH         Path to ffmpeg with libass (default: ffmpeg on PATH).
#                         macOS: /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
#   --audio-track N       Zero-based audio stream to transcribe (default 0).
#                         OBS recordings often put the mic on track 1.
#   --max-gap-calls N     Cap on extra billed gap-recovery calls (default 10)
#   --keep-work           Don't delete temp work directory after success
#   --yes                 Skip the cost confirmation prompt. Without a terminal
#                         (an agent's shell, CI) the script prints the estimate
#                         and stops with exit code 3 unless --yes is given, so an
#                         agent shows the user the price and re-runs with --yes
#                         only after the user agrees.
#
# Side outputs (alongside the captioned video, named after the OUTPUT):
#   <output>.he.srt       The generated SRT file (useful for YouTube/Vimeo upload
#                         if you want soft captions there instead of burned-in),
#                         e.g. lecture.captioned.he.srt
#
# There is no transcript cache: every run transcribes again and is billed again.
#
# Why this exists: the full video-use workflow is designed for "raw footage -> curated cut"
# and costs $25-300 in Claude API tokens on long videos because the agent re-reads the
# transcript across turns. If you just want captions on the whole video and not an edit,
# this script does it for ~$1-3 in tokens regardless of video length, because there is
# no agent loop at all, just Scribe transcription + the burn-in script.
#
# Requires:
#   - ELEVENLABS_API_KEY exported in the environment (video-use's own setup keeps
#     it in its .env file; export it from there in your shell)
#   - ffmpeg with libass + fontconfig (see references/macos-ffmpeg-setup.md)
#   - python3 with python-bidi (python3 -m pip install --user python-bidi)
#   - Hebrew fonts (run scripts/install-hebrew-fonts.sh once if missing)

set -euo pipefail

VIDEO=""
OUTPUT=""
STRIP_FILLERS=0
FONT="Heebo"
# "auto" hands the decision to burn-hebrew-captions.sh, which derives font size
# and bottom margin as ratios of the probed frame height. Do NOT restore a fixed
# default here: passing an absolute --font-size unconditionally is what silently
# defeated the ratio scaling and left portrait captions at 2.7% of frame height.
FONTSIZE="auto"
MARGINV="auto"
FONTSDIR=""      # empty = let burn-hebrew-captions.sh pick the per-platform default
FFMPEG="ffmpeg"
KEEP_WORK=0
ASSUME_YES=0
AUDIO_TRACK=0
MAX_GAP_CALLS=10

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strip-fillers) STRIP_FILLERS=1; shift ;;
    --font) FONT="$2"; shift 2 ;;
    --font-size) FONTSIZE="$2"; shift 2 ;;
    --margin-v) MARGINV="$2"; shift 2 ;;
    --fontsdir) FONTSDIR="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --ffmpeg) FFMPEG="$2"; shift 2 ;;
    --keep-work) KEEP_WORK=1; shift ;;
    --audio-track) AUDIO_TRACK="$2"; shift 2 ;;
    --max-gap-calls) MAX_GAP_CALLS="$2"; shift 2 ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    -h|--help) sed -n '2,46p' "$0"; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *) [[ -z "$VIDEO" ]] && VIDEO="$1" || { echo "Multiple inputs not supported: $1" >&2; exit 1; }; shift ;;
  esac
done

[[ -z "$VIDEO" ]] && { echo "Usage: $0 <video.mp4> [options]. Try --help" >&2; exit 1; }
[[ ! -f "$VIDEO" ]] && { echo "Video file not found: $VIDEO" >&2; exit 1; }
[[ "$AUDIO_TRACK" =~ ^[0-9]+$ ]] || { echo "--audio-track must be a whole number" >&2; exit 1; }
[[ "$MAX_GAP_CALLS" =~ ^[0-9]+$ ]] || { echo "--max-gap-calls must be a whole number" >&2; exit 1; }

if [[ -z "$OUTPUT" ]]; then
  VIDEO_DIR=$(dirname "$VIDEO")
  VIDEO_BASE=$(basename "$VIDEO")
  VIDEO_EXT="${VIDEO_BASE##*.}"
  VIDEO_NAME="${VIDEO_BASE%.*}"
  OUTPUT="${VIDEO_DIR}/${VIDEO_NAME}.captioned.${VIDEO_EXT}"
fi

WORKDIR=$(mktemp -d -t "captions-only.XXXXXX")
log() { printf '[captions-only] %s\n' "$*"; }
cleanup() {
  rm -f "${WORKDIR}/.scribe-header"   # never leave the API key on disk, even with --keep-work
  if [[ $KEEP_WORK -eq 0 ]] && [[ -d "$WORKDIR" ]]; then
    rm -rf "$WORKDIR"
  else
    log "Work dir kept: $WORKDIR"
  fi
}
trap cleanup EXIT

log "Source video:  $VIDEO"
log "Output:        $OUTPUT"
log "Work dir:      $WORKDIR"
log "Font:          $FONT @ ${FONTSIZE} (auto = scaled from video height)"
log "Strip fillers: $([[ $STRIP_FILLERS -eq 1 ]] && echo "yes (ALWAYS-FILLER tokens dropped from SRT)" || echo "no")"


# The key is read from the environment only. It is sent nowhere except the
# pinned ElevenLabs host below, and it goes to curl through a 0600 header file,
# not on the command line where other local users could see it in `ps`.
readonly SCRIBE_URL="https://api.elevenlabs.io/v1/speech-to-text"
if [[ -z "${ELEVENLABS_API_KEY:-}" ]]; then
  log "ERROR: ELEVENLABS_API_KEY is not set in this shell."
  log "       Create one at https://elevenlabs.io/app/settings/api-keys and export it."
  exit 1
fi
HDR="${WORKDIR}/.scribe-header"
( umask 077; printf 'xi-api-key: %s\n' "$ELEVENLABS_API_KEY" > "$HDR" )


SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BURN_SCRIPT="${SCRIPT_DIR}/burn-hebrew-captions.sh"
[[ ! -f "$BURN_SCRIPT" ]] && { log "ERROR: burn-hebrew-captions.sh not found alongside this script at $BURN_SCRIPT"; exit 1; }

# Check that the burn step CAN run (libass filter, font, python-bidi) before
# anything is billed. Otherwise a stock Homebrew ffmpeg pays for the whole
# transcription and only then fails at the burn.
PRE_ARGS=(--preflight-only --font "$FONT" --ffmpeg "$FFMPEG")
if [[ -n "$FONTSDIR" ]]; then PRE_ARGS+=(--fontsdir "$FONTSDIR"); fi
if ! bash "$BURN_SCRIPT" "${PRE_ARGS[@]}"; then
  log "ERROR: the caption burn step cannot run on this machine (see above). Nothing was sent or billed."
  exit 1
fi

# FFPROBE must be assigned unconditionally: it is used again at Step 4, and
# leaving it unset made the script die under `set -u` AFTER the paid Scribe
# call had already gone out. Without a duration we also cannot price the run,
# and silently skipping the billing confirmation is not acceptable, so abort.
DURATION_SEC=0
FFPROBE="${FFMPEG%ffmpeg}ffprobe"
[[ -x "$FFPROBE" ]] || FFPROBE="ffprobe"
if command -v "$FFPROBE" >/dev/null 2>&1; then
  DURATION_SEC=$("$FFPROBE" -v error -show_entries format=duration -of csv=p=0 "$VIDEO" 2>/dev/null | cut -d. -f1)
fi
if [[ -z "$DURATION_SEC" || "$DURATION_SEC" -le 0 ]]; then
  log "ERROR: could not determine video duration (ffprobe missing or unreadable input)."
  log "       Refusing to bill your ElevenLabs account without showing you the cost first."
  log "       Install ffprobe (see references/macos-ffmpeg-setup.md) or pass --ffmpeg <path>."
  exit 1
fi
if [[ "$DURATION_SEC" -gt 0 ]]; then
  MIN=$((DURATION_SEC / 60))
  # 20 = ElevenLabs Scribe v2 list price in cents per hour of audio (API rate
  # card, re-checked 2026-11-11). Keep in sync with SKILL.md and pricing.md.
  COST_CENTS=$(( DURATION_SEC * 20 / 3600 ))
  COST_STR="\$0.$(printf '%02d' $COST_CENTS)"
  [[ $COST_CENTS -gt 99 ]] && COST_STR="\$$(($COST_CENTS / 100)).$(printf '%02d' $((COST_CENTS % 100)))"
  # Quote BOTH rails. A free/Starter user is metered in credits, not dollars, so
  # "~$0.03" reads as free while actually consuming a third of their month.
  CREDITS=$(( DURATION_SEC * 330 / 60 ))
  FREE_PCT=$(( CREDITS * 100 / 10000 ))
  log "Duration: ${MIN} minutes. Estimated Scribe cost: ~${COST_STR} on the API rate,"
  log "  or ~${CREDITS} credits (~${FREE_PCT}% of the 10,000-credit free monthly allowance) on a subscription."
  log "  Gap recovery may add further billed calls (at most ${MAX_GAP_CALLS}); in the worst case,"
  log "  Scribe dropping most of the file, that roughly doubles this estimate."

  # Cost confirmation gate (skipped with --yes)
  if [[ $ASSUME_YES -eq 0 ]]; then
    if [[ ! -t 0 ]]; then
      # No terminal to answer on (an agent's shell, CI). `read` would hit EOF
      # and, under set -e, kill the script with no message. Stop cleanly.
      log "No terminal for the confirmation prompt. Nothing was sent or billed."
      log "Show the estimate above to the user; once they agree, re-run with --yes."
      exit 3
    fi
    printf '[captions-only] Proceed and bill your ElevenLabs account ~%s (or ~%s credits)? [y/N] ' "${COST_STR}" "${CREDITS}"
    CONFIRM=""
    read -r CONFIRM || true
    case "$CONFIRM" in
      y|Y|yes|YES) ;;
      *) log "Aborted by user."; exit 0 ;;
    esac
  fi
fi

# One Scribe request. Every call goes to the pinned SCRIBE_URL; an earlier
# version of the gap-recovery call had no URL at all, so curl failed and
# `set -e` killed the run AFTER the paid main transcription.
scribe_call() {  # $1 = audio file, $2 = output json; prints the HTTP status
  curl -sS -o "$2" -w '%{http_code}' \
    -H @"$HDR" \
    -F "model_id=scribe_v2" \
    -F "language_code=heb" \
    -F "tag_audio_events=false" \
    -F "diarize=false" \
    -F "timestamps_granularity=word" \
    -F "file=@$1" \
    "$SCRIBE_URL" || true   # on a transport failure curl still prints 000
}

# Upload audio, not the video. A 3-hour 1080p lecture is several GB as MP4 and
# well under 200 MB as 64 kbps mono AAC, and Scribe only needs the sound.
log "Step 0: Extracting audio track ${AUDIO_TRACK} (mono AAC) for upload"
AUDIO="${WORKDIR}/audio.m4a"
if ! "$FFMPEG" -y -loglevel error -i "$VIDEO" -map "0:a:${AUDIO_TRACK}" -vn -ac 1 -ar 16000 -c:a aac -b:a 64k "$AUDIO"; then
  log "ERROR: could not extract audio track ${AUDIO_TRACK} from $VIDEO (does it have that many audio tracks?)."
  exit 1
fi
# Refuse to pay for silence (wrong track, muted recording).
PEAK=$("$FFMPEG" -hide_banner -nostats -i "$AUDIO" -af volumedetect -f null - 2>&1 | sed -nE 's/.*max_volume: (-?[0-9.]+|-inf) dB.*/\1/p' | tail -1)
if [[ "$PEAK" == "-inf" ]] || awk -v p="${PEAK:-0}" 'BEGIN{exit !(p < -60)}'; then
  log "ERROR: audio track ${AUDIO_TRACK} is silent (peak ${PEAK} dB). Not uploading. Try --audio-track 1."
  exit 1
fi

log "Step 1: Transcribing with ElevenLabs Scribe (no_verbatim=false, language_code=heb)"
HTTP_CODE=$(scribe_call "$AUDIO" "${WORKDIR}/scribe.json")

if [[ "$HTTP_CODE" != "200" ]]; then
  log "ERROR: Scribe returned HTTP $HTTP_CODE"
  log "Response body:"
  head -c 2000 "${WORKDIR}/scribe.json" 2>/dev/null; echo
  exit 1
fi
SCRIBE_SIZE=$(wc -c < "${WORKDIR}/scribe.json" | tr -d ' ')
log "  Transcript received: ${SCRIBE_SIZE} bytes"
GAP_FAILED=0

log "Step 1.5: Scanning for Scribe gaps (drops occasionally dropped 30s+ chunks)"
# Scribe sometimes silently fails to transcribe a section of audio. Detect:
#   (a) MID-FILE GAP: any gap > 30s between consecutive transcribed words
#   (b) TAIL GAP: if the last transcribed word ends > 10s before video end
# For each such gap, re-transcribe just that audio segment (Scribe usually
# succeeds when given an isolated short segment) and merge the recovered
# words into the main transcript.

GAP_THRESHOLD=30   # mid-file: consecutive words >30s apart = suspect
TAIL_THRESHOLD=10  # tail: last word ends >10s before video end = suspect

# Get video duration in seconds
VIDEO_DUR=$("$FFPROBE" -v error -show_entries format=duration -of csv=p=0 "$VIDEO" 2>/dev/null | cut -d. -f1)
[[ -z "$VIDEO_DUR" ]] && VIDEO_DUR=0

# Find gap windows to re-transcribe
GAPS_FILE="${WORKDIR}/gaps.txt"
WORKDIR="$WORKDIR" GAP_THRESHOLD="$GAP_THRESHOLD" TAIL_THRESHOLD="$TAIL_THRESHOLD" VIDEO_DUR="$VIDEO_DUR" \
python3 - <<'PYEOF' > "$GAPS_FILE"
import json, os
E = os.environ
gap_th, tail_th, dur = float(E['GAP_THRESHOLD']), float(E['TAIL_THRESHOLD']), float(E['VIDEO_DUR'])
data = json.load(open(os.path.join(E['WORKDIR'], 'scribe.json')))
words = [w for w in data.get('words', []) if w.get('type') == 'word']
gaps = []
for i in range(len(words) - 1):
    gap = words[i+1]['start'] - words[i]['end']
    if gap > gap_th:
        gaps.append((words[i]['end'], words[i+1]['start']))
# Tail gap
if words and words[-1]['end'] < dur - tail_th:
    gaps.append((words[-1]['end'], dur))
for start, end in gaps:
    print(f"{start:.2f} {end:.2f}")
PYEOF

GAP_COUNT=$(wc -l < "$GAPS_FILE" | tr -d ' ')
if [[ "$GAP_COUNT" -eq 0 ]]; then
  log "  No gaps detected. Transcript covers the full video."
else
  GAP_SECS=$(awk '{s += $2 - $1} END {printf "%d", s}' "$GAPS_FILE")
  log "  Detected ${GAP_COUNT} gap(s), ${GAP_SECS}s of audio. Each recovery is an extra billed call"
  log "  (~${GAP_SECS}s more Scribe time). At most ${MAX_GAP_CALLS} will be made (--max-gap-calls)."
  GAP_IDX=0
  while IFS=' ' read -r gap_start gap_end; do
    GAP_IDX=$((GAP_IDX + 1))
    if [[ $GAP_IDX -gt $MAX_GAP_CALLS ]]; then
      log "  Gap ${GAP_IDX}+: cap of ${MAX_GAP_CALLS} recovery calls reached, leaving the rest uncaptioned."
      GAP_FAILED=$((GAP_FAILED + 1))
      break
    fi
    DUR=$(awk -v a="$gap_start" -v b="$gap_end" 'BEGIN{printf "%.2f", b - a}')
    log "  Gap ${GAP_IDX}: ${gap_start}s -> ${gap_end}s (${DUR}s window)"
    GAP_AUDIO="${WORKDIR}/gap_${GAP_IDX}.m4a"
    GAP_JSON="${WORKDIR}/gap_${GAP_IDX}.json"
    if ! "$FFMPEG" -y -loglevel error -ss "$gap_start" -i "$AUDIO" -t "$DUR" -vn -c:a aac "$GAP_AUDIO" 2>/dev/null; then
      log "    WARN: could not cut gap audio, skipping"; GAP_FAILED=$((GAP_FAILED + 1)); continue
    fi
    # A real pause or a quiet screen-recording stretch is not a dropped chunk.
    # Measure the MEAN level, not the peak (one keyboard click would defeat a
    # peak test), and skip 0.5s at each edge so the tail of the last word and
    # the onset of the next one do not count. Speech averages far above -50 dB.
    MDUR=$(awk -v d="$DUR" 'BEGIN{x = d - 1; if (x < 0.2) x = d; printf "%.2f", x}')
    MOFF=$(awk -v d="$DUR" 'BEGIN{printf "%.2f", (d > 1.2) ? 0.5 : 0}')
    GMEAN=$("$FFMPEG" -hide_banner -nostats -ss "$MOFF" -t "$MDUR" -i "$GAP_AUDIO" -af volumedetect -f null - 2>&1 | sed -nE 's/.*mean_volume: (-?[0-9.]+|-inf) dB.*/\1/p' | tail -1)
    if [[ "$GMEAN" == "-inf" ]] || awk -v p="${GMEAN:-0}" 'BEGIN{exit !(p < -50)}'; then
      log "    Window is near-silent (mean ${GMEAN} dB), not a dropped chunk. Skipped, not billed."
      continue
    fi
    HTTP=$(scribe_call "$GAP_AUDIO" "$GAP_JSON")
    if [[ "$HTTP" = "200" ]]; then
      NEW_WORDS=$(python3 -c "
import json,sys
try:
    d=json.load(open(sys.argv[1])); print(len([w for w in d.get('words',[]) if w.get('type')=='word']))
except Exception:
    print('unreadable')" "$GAP_JSON")
      log "    Recovered ${NEW_WORDS} word(s) from gap"
    else
      log "    WARN: gap re-transcribe returned HTTP $HTTP, skipping"
      rm -f "$GAP_JSON"
      GAP_FAILED=$((GAP_FAILED + 1))
    fi
  done < "$GAPS_FILE"

  # Merge all recovered gap words back into the main transcript
  log "  Merging ${GAP_COUNT} recovered gap(s) into main transcript"
  WORKDIR=$WORKDIR GAP_COUNT=$GAP_COUNT python3 <<'PYEOF'
import json, os, glob
workdir = os.environ['WORKDIR']
gap_count = int(os.environ['GAP_COUNT'])

main = json.load(open(f"{workdir}/scribe.json"))
main_words = [w for w in main.get('words', []) if w.get('type') == 'word']
gaps_file = open(f"{workdir}/gaps.txt").readlines()
gap_windows = []
for i, line in enumerate(gaps_file, 1):
    parts = line.strip().split()
    if len(parts) == 2:
        gap_windows.append((float(parts[0]), float(parts[1]), i))

recovered_total = 0
for gap_start, gap_end, idx in gap_windows:
    gap_json_path = f"{workdir}/gap_{idx}.json"
    if not os.path.exists(gap_json_path): continue
    try:
        gap_data = json.load(open(gap_json_path))
    except Exception:
        print(f"  WARN: gap {idx} response unreadable, skipped")
        continue
    gap_words = [w for w in gap_data.get('words', []) if w.get('type') == 'word']
    # Shift timestamps to video time
    for w in gap_words:
        w['start'] += gap_start
        w['end'] += gap_start
    main_words += gap_words
    recovered_total += len(gap_words)

# Sort by start time
main_words.sort(key=lambda w: w['start'])
main['words'] = main_words
json.dump(main, open(f"{workdir}/scribe.json", 'w'), ensure_ascii=False)
print(f"  Merged {recovered_total} recovered words. Transcript now has {len(main_words)} total words.")
PYEOF
fi

if [[ $GAP_FAILED -gt 0 ]]; then
  log "  WARN: ${GAP_FAILED} gap window(s) could not be recovered and stay UNCAPTIONED."
  log "        See Troubleshooting in SKILL.md; re-running the script re-bills the whole file."
fi
rm -f "${WORKDIR}/.scribe-header"

log "Step 2: Building SRT (5-7 word chunks, break on silence >=250ms or sentence end)"
STRIP_FILLERS=$STRIP_FILLERS WORKDIR=$WORKDIR python3 <<'PYEOF'
import json, os, re

workdir = os.environ['WORKDIR']
strip_fillers = os.environ['STRIP_FILLERS'] == '1'

with open(f"{workdir}/scribe.json") as f:
    data = json.load(f)

words = [w for w in data.get("words", []) if w.get("type") == "word"]
if not words:
    raise SystemExit("ERROR: Scribe returned no word-type entries. Check the transcript JSON.")

# Sanitize pathologically long word durations. Scribe occasionally assigns an
# 80+ second end-timestamp to a single word that brackets a long silence gap,
# which would chain a whole chunk across the silence and cause "stuck" or
# "missing" captions downstream. Clip any single-word duration above 2s to 2s.
# A word genuinely taking >2s to pronounce is implausible for any natural speech.
MAX_WORD_DUR = 2.0
clipped = 0
for w in words:
    if w["end"] - w["start"] > MAX_WORD_DUR:
        w["end"] = w["start"] + MAX_WORD_DUR
        clipped += 1
if clipped > 0:
    print(f"  Clipped {clipped} pathologically long word duration(s) at {MAX_WORD_DUR}s (Scribe artifact)")

# NOTE: do NOT add bare "אם" here, it is the everyday word "if/whether", not a hesitation.
# The "umm" hesitation is the separate forms אממ / אמממ (plus pointed spellings).
# Pointed forms are written as escapes (\u05b6 is the segol vowel mark) so the
# file carries no invisible combining characters: "\u05d0\u05b6\u05d4" and
# "\u05d0\u05b6\u05de" are the pointed spellings of the two hesitations.
ALWAYS_FILLER = {"\u05d0\u05b6\u05d4","אה","\u05d0\u05b6\u05de","אממ","אמממ","אהמ","המ","ממ"}

chunks = []
current = []
filtered_count = 0
for i, w in enumerate(words):
    if strip_fillers:
        normalized = re.sub(r"[.,!?]", "", w["text"]).strip()
        if normalized in ALWAYS_FILLER:
            filtered_count += 1
            continue
    current.append(w)
    flush = False
    if len(current) >= 7:
        flush = True
    elif i + 1 < len(words):
        gap = words[i+1]["start"] - w["end"]
        if gap >= 0.25:
            flush = True
    if w["text"].rstrip().endswith((".", "?", "!")):
        flush = True
    if flush:
        chunks.append(current)
        current = []
if current:
    chunks.append(current)

def fmt(t):
    # Work in whole milliseconds: float truncation turned 1.2s into 00:00:01,199.
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

# Cap caption max display duration as a belt-and-suspenders safety. With
# word-level clipping above, chunks should naturally stay short, but this
# guards against any remaining edge case.
MAX_DISPLAY_SEC = 7.0
capped = 0
with open(f"{workdir}/captions.srt", "w", encoding="utf-8") as f:
    f.write("\ufeff")
    for i, ch in enumerate(chunks, 1):
        start = ch[0]["start"]
        end = ch[-1]["end"]
        if end - start > MAX_DISPLAY_SEC:
            end = start + MAX_DISPLAY_SEC
            capped += 1
        text = " ".join(w["text"] for w in ch)
        f.write(f"{i}\n{fmt(start)} --> {fmt(end)}\n{text}\n\n")
if capped > 0:
    print(f"  Capped display duration on {capped} cue(s) at {MAX_DISPLAY_SEC}s")

print(f"  Wrote {len(chunks)} caption cues to captions.srt")
if strip_fillers:
    print(f"  Stripped {filtered_count} ALWAYS-FILLER words from the captions")
PYEOF

# Step 3a: Export the SRT alongside the (future) output BEFORE the burn step,
# so the user has soft captions even if the burn or verify steps fail.
SRT_OUT="${OUTPUT%.*}.he.srt"
cp "${WORKDIR}/captions.srt" "$SRT_OUT"
log "Step 3a: Exported soft-caption SRT to $SRT_OUT"

log "Step 3b: Burning captions onto ${VIDEO}"
# Only forward --font-size / --margin-v when the user actually set them.
# Forwarding "auto" values would override the burn script's height-based ratios.
BURN_ARGS=(--base "$VIDEO" --srt "${WORKDIR}/captions.srt" --out "$OUTPUT" --font "$FONT" --ffmpeg "$FFMPEG")
# Use `if`, not `[[ ]] && ...`: under `set -e` a false test is a non-zero
# compound and would abort the script right before the burn step.
if [[ "$FONTSIZE" != "auto" ]]; then BURN_ARGS+=(--font-size "$FONTSIZE"); fi
if [[ "$MARGINV"  != "auto" ]]; then BURN_ARGS+=(--margin-v  "$MARGINV");  fi
if [[ -n "$FONTSDIR"          ]]; then BURN_ARGS+=(--fontsdir  "$FONTSDIR"); fi
if ! bash "$BURN_SCRIPT" "${BURN_ARGS[@]}"; then
  log "ERROR: the burn step failed. The soft-caption SRT above is complete: after fixing the cause,"
  log "       burn it with burn-hebrew-captions.sh --srt <that file> instead of re-running (which re-bills)."
  exit 1
fi

log ""
log "Done."
log "  Captioned video: $OUTPUT"
log "  Side SRT:        $SRT_OUT"
log ""
log "Open verify frames (from the burn script) with:"
log "  open \"$(dirname "$OUTPUT")\"/verify_*"
