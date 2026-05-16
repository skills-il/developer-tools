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
#   --strip-fillers       Remove ALWAYS-FILLER tokens (אה, אהה, אם, אממ...) by
#                         omitting them from the SRT. Speech timing preserved
#                         (no audio cuts, just words you don't see).
#   --output PATH         Output path (default: <video>.captioned.<ext>)
#   --font NAME           Caption font (default: Heebo)
#   --font-size N         Font size in ASS PlayRes units (default: 52)
#   --ffmpeg PATH         Path to ffmpeg with libass (default: ffmpeg on PATH)
#   --keep-work           Don't delete temp work directory after success
#   --yes                 Skip the cost confirmation prompt (for unattended/CI runs)
#
# Side outputs (alongside the captioned video):
#   <video>.he.srt        The generated SRT file (useful for YouTube/Vimeo upload
#                         if you want soft captions there instead of burned-in)
#
# Why this exists: the full video-use workflow is designed for "raw footage -> curated cut"
# and costs $25-300 in Claude API tokens on long videos because the agent re-reads the
# transcript across turns. If you just want captions on the whole video and not an edit,
# this script does it for ~$1-3 in tokens regardless of video length, because there is
# no agent loop at all, just Scribe transcription + the burn-in script.
#
# Requires:
#   - ELEVENLABS_API_KEY in env, or in ~/Developer/video-use/.env (auto-detected)
#   - ffmpeg with libass + fontconfig (see references/macos-ffmpeg-setup.md)
#   - python3 with python-bidi (auto-installed if missing)
#   - Hebrew fonts (run scripts/install-hebrew-fonts.sh once if missing)

set -euo pipefail

VIDEO=""
OUTPUT=""
STRIP_FILLERS=0
FONT="Heebo"
# Default FontSize is in absolute pixels (good for 720p); bump for higher resolutions.
FONTSIZE=52
FFMPEG="ffmpeg"
KEEP_WORK=0
ASSUME_YES=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strip-fillers) STRIP_FILLERS=1; shift ;;
    --font) FONT="$2"; shift 2 ;;
    --font-size) FONTSIZE="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --ffmpeg) FFMPEG="$2"; shift 2 ;;
    --keep-work) KEEP_WORK=1; shift ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    -h|--help) sed -n '2,35p' "$0"; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *) [[ -z "$VIDEO" ]] && VIDEO="$1" || { echo "Multiple inputs not supported: $1" >&2; exit 1; }; shift ;;
  esac
done

[[ -z "$VIDEO" ]] && { echo "Usage: $0 <video.mp4> [options]. Try --help" >&2; exit 1; }
[[ ! -f "$VIDEO" ]] && { echo "Video file not found: $VIDEO" >&2; exit 1; }

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
log "Font:          $FONT @ ${FONTSIZE}pt"
log "Strip fillers: $([[ $STRIP_FILLERS -eq 1 ]] && echo "yes (ALWAYS-FILLER tokens dropped from SRT)" || echo "no")"

EL_KEY="${ELEVENLABS_API_KEY:-}"
if [[ -z "$EL_KEY" ]] && [[ -f "$HOME/Developer/video-use/.env" ]]; then
  EL_KEY=$(sed -n 's/^ELEVENLABS_API_KEY=//p' "$HOME/Developer/video-use/.env" | tr -d '\n')
fi
if [[ -z "$EL_KEY" ]]; then
  log "ERROR: ELEVENLABS_API_KEY not found in environment or ~/Developer/video-use/.env"
  log "Get a key at https://elevenlabs.io/app/settings/api-keys and either:"
  log "  export ELEVENLABS_API_KEY=sk_..."
  log "  echo 'ELEVENLABS_API_KEY=sk_...' > ~/Developer/video-use/.env"
  exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BURN_SCRIPT="${SCRIPT_DIR}/burn-hebrew-captions.sh"
[[ ! -f "$BURN_SCRIPT" ]] && { log "ERROR: burn-hebrew-captions.sh not found alongside this script at $BURN_SCRIPT"; exit 1; }

DURATION_SEC=0
if command -v ffprobe >/dev/null 2>&1 || [[ -x "${FFMPEG%ffmpeg}ffprobe" ]]; then
  FFPROBE="${FFMPEG%ffmpeg}ffprobe"
  [[ ! -x "$FFPROBE" ]] && FFPROBE="ffprobe"
  DURATION_SEC=$("$FFPROBE" -v error -show_entries format=duration -of csv=p=0 "$VIDEO" 2>/dev/null | cut -d. -f1)
fi
if [[ -n "$DURATION_SEC" ]] && [[ "$DURATION_SEC" -gt 0 ]]; then
  MIN=$((DURATION_SEC / 60))
  COST_CENTS=$(( DURATION_SEC * 40 / 3600 ))
  COST_STR="\$0.$(printf '%02d' $COST_CENTS)"
  [[ $COST_CENTS -gt 99 ]] && COST_STR="\$$(($COST_CENTS / 100)).$(printf '%02d' $((COST_CENTS % 100)))"
  log "Duration: ${MIN} minutes. Estimated Scribe cost: ~${COST_STR}"

  # Cost confirmation gate (skipped with --yes)
  if [[ $ASSUME_YES -eq 0 ]]; then
    printf '[captions-only] Proceed and bill your ElevenLabs account ~%s? [y/N] ' "${COST_STR}"
    read -r CONFIRM
    case "$CONFIRM" in
      y|Y|yes|YES) ;;
      *) log "Aborted by user."; exit 0 ;;
    esac
  fi
fi

log "Step 1: Transcribing with ElevenLabs Scribe (no_verbatim=false, language_code=heb)"
HTTP_CODE=$(curl -sS -o "${WORKDIR}/scribe.json" -w '%{http_code}' \
  -H "xi-api-key: $EL_KEY" \
  -F "model_id=scribe_v1" \
  -F "language_code=heb" \
  -F "tag_audio_events=false" \
  -F "diarize=false" \
  -F "timestamps_granularity=word" \
  -F "file=@${VIDEO}" \
  https://api.elevenlabs.io/v1/speech-to-text)

if [[ "$HTTP_CODE" != "200" ]]; then
  log "ERROR: Scribe returned HTTP $HTTP_CODE"
  log "Response body:"
  cat "${WORKDIR}/scribe.json" | head -20
  exit 1
fi
SCRIBE_SIZE=$(wc -c < "${WORKDIR}/scribe.json" | tr -d ' ')
log "  Transcript received: ${SCRIBE_SIZE} bytes"

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
python3 << PYEOF > "$GAPS_FILE"
import json
data = json.load(open("${WORKDIR}/scribe.json"))
words = [w for w in data.get('words', []) if w.get('type') == 'word']
gaps = []
for i in range(len(words) - 1):
    gap = words[i+1]['start'] - words[i]['end']
    if gap > $GAP_THRESHOLD:
        gaps.append((words[i]['end'], words[i+1]['start']))
# Tail gap
if words and words[-1]['end'] < $VIDEO_DUR - $TAIL_THRESHOLD:
    gaps.append((words[-1]['end'], $VIDEO_DUR))
for start, end in gaps:
    print(f"{start:.2f} {end:.2f}")
PYEOF

GAP_COUNT=$(wc -l < "$GAPS_FILE" | tr -d ' ')
if [[ "$GAP_COUNT" -eq 0 ]]; then
  log "  No gaps detected. Transcript covers the full video."
else
  log "  Detected ${GAP_COUNT} gap(s). Re-transcribing each with scribe_v2."
  GAP_IDX=0
  while IFS=' ' read -r gap_start gap_end; do
    GAP_IDX=$((GAP_IDX + 1))
    DUR=$(echo "$gap_end - $gap_start" | bc)
    log "  Gap ${GAP_IDX}: ${gap_start}s -> ${gap_end}s (${DUR}s window)"
    GAP_AUDIO="${WORKDIR}/gap_${GAP_IDX}.m4a"
    GAP_JSON="${WORKDIR}/gap_${GAP_IDX}.json"
    "$FFMPEG" -y -loglevel error -ss "$gap_start" -i "$VIDEO" -t "$DUR" -vn -c:a aac "$GAP_AUDIO" 2>/dev/null
    HTTP=$(curl -sS -o "$GAP_JSON" -w '%{http_code}' \
      -H "xi-api-key: $EL_KEY" \
      -F "model_id=scribe_v2" \
      -F "language_code=heb" \
      -F "tag_audio_events=false" \
      -F "diarize=false" \
      -F "timestamps_granularity=word" \
      -F "file=@${GAP_AUDIO}")
    if [[ "$HTTP" = "200" ]]; then
      NEW_WORDS=$(python3 -c "import json; d=json.load(open('$GAP_JSON')); print(len([w for w in d.get('words',[]) if w.get('type')=='word']))")
      log "    Recovered ${NEW_WORDS} word(s) from gap"
    else
      log "    WARN: gap re-transcribe returned HTTP $HTTP, skipping"
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
    gap_data = json.load(open(gap_json_path))
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

ALWAYS_FILLER = {"אֶה","אה","אם","אֶמ","אממ","אמממ","אהמ","המ","ממ"}

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
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"

# Cap caption max display duration as a belt-and-suspenders safety. With
# word-level clipping above, chunks should naturally stay short, but this
# guards against any remaining edge case.
MAX_DISPLAY_SEC = 7.0
capped = 0
with open(f"{workdir}/captions.srt", "w", encoding="utf-8") as f:
    f.write("﻿")
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
bash "$BURN_SCRIPT" \
  --base "$VIDEO" \
  --srt "${WORKDIR}/captions.srt" \
  --out "$OUTPUT" \
  --font "$FONT" \
  --font-size "$FONTSIZE" \
  --ffmpeg "$FFMPEG"

log ""
log "Done."
log "  Captioned video: $OUTPUT"
log "  Side SRT:        $SRT_OUT"
log ""
log "Open verify frames (from the burn script) with:"
log "  open \"$(dirname "$OUTPUT")\"/verify_*"
