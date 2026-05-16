#!/usr/bin/env bash
# burn-hebrew-captions.sh
# End-to-end Hebrew caption burn-in for video-use output (and any base.mp4 + master.srt pair).
#
# IMPORTANT CORRECTION (v1.2.3): the original v1.1.0 approach assumed libass + SRT was
# silently broken for Hebrew BiDi on macOS, and pre-shaped the text with python-bidi
# before rendering. End-to-end testing on a real video proved that diagnosis WRONG:
# libass + SRT actually handles Hebrew BiDi correctly when the SRT is fed DIRECTLY
# to the subtitles filter. The python-bidi pre-shape + SRT->ASS chain was double-
# reversing the text back to source byte order. The CORRECT recipe is to skip
# pre-shape and ASS conversion entirely, and let libass do its job with the source SRT.
#
# What this script now does:
#   0. Sanitize Scribe garbage characters (Devanagari `्स` etc.) from the SRT
#   1. Burn captions onto the base video with libass + explicit fontsdir + force_style
#   2. Sample verification frames (1 per minute, capped at 30)
#
# Usage:
#   burn-hebrew-captions.sh \
#     --base <path/to/base.mp4> \
#     --srt  <path/to/master.srt> \
#     --out  <path/to/final.mp4> \
#     [--font Heebo] \
#     [--fontsdir $HOME/Library/Fonts] \
#     [--font-size 52] \
#     [--spacing 2] \
#     [--margin-v 80] \
#     [--ffmpeg /tmp/ffmpeg]   # static evermeet build path (default: ffmpeg on PATH)
#
# Requires: ffmpeg with libass + fontconfig (Homebrew ffmpeg often lacks these on macOS;
# see references/macos-ffmpeg-setup.md for a fix), python3 with python-bidi.

set -euo pipefail

FONT="Heebo"
FONTSDIR="$HOME/Library/Fonts"
# Note: FontSize is in absolute pixels for libass+SRT (no PlayResY scaling).
# 26 is good for 720p; bump to 36-42 for 1080p, 56-72 for 4K.
FONTSIZE="26"
SPACING="2"
MARGINV="35"
FFMPEG="ffmpeg"

BASE=""
SRT=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base) BASE="$2"; shift 2 ;;
    --srt)  SRT="$2";  shift 2 ;;
    --out)  OUT="$2";  shift 2 ;;
    --font) FONT="$2"; shift 2 ;;
    --fontsdir) FONTSDIR="$2"; shift 2 ;;
    --font-size) FONTSIZE="$2"; shift 2 ;;
    --spacing) SPACING="$2"; shift 2 ;;
    --margin-v) MARGINV="$2"; shift 2 ;;
    --ffmpeg) FFMPEG="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$BASE" || -z "$SRT" || -z "$OUT" ]] && { echo "Required: --base BASE.mp4 --srt MASTER.srt --out OUT.mp4" >&2; exit 1; }
[[ ! -f "$BASE" ]] && { echo "Base video not found: $BASE" >&2; exit 1; }
[[ ! -f "$SRT" ]] && { echo "SRT not found: $SRT" >&2; exit 1; }

log() { printf '[burn-hebrew-captions] %s\n' "$*"; }

# Pre-flight checks
log "Pre-flight: verifying ffmpeg has libass + fontconfig"
if ! "$FFMPEG" -version 2>/dev/null | grep -q 'enable-libass'; then
  log "ERROR: $FFMPEG was not built with --enable-libass. See references/macos-ffmpeg-setup.md."
  log "       Quick fix on macOS: curl -L https://evermeet.cx/ffmpeg/getrelease/zip -o /tmp/ff.zip && unzip /tmp/ff.zip -d /tmp/ && /tmp/ffmpeg -version | head -1"
  exit 1
fi

log "Pre-flight: verifying Hebrew fonts are available"
if ! fc-list :lang=he 2>/dev/null | grep -qi "$FONT"; then
  log "ERROR: $FONT not found by fontconfig. Run scripts/install-hebrew-fonts.sh first."
  exit 1
fi

log "Pre-flight: verifying python3 (for SRT sanitization)"
command -v python3 >/dev/null 2>&1 || { log "ERROR: python3 not found"; exit 1; }

# Probe base for resolution so we can size the ASS PlayResX/Y to match
# Use ffprobe if next to ffmpeg, else fall back to ffmpeg with verbose output
FFPROBE="${FFMPEG%ffmpeg}ffprobe"
[[ ! -x "$FFPROBE" ]] && FFPROBE="ffprobe"
if command -v "$FFPROBE" >/dev/null 2>&1; then
  BASE_W=$("$FFPROBE" -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$BASE")
  BASE_H=$("$FFPROBE" -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$BASE")
else
  # Fallback: parse from ffmpeg stderr (without -v error which silences stream info)
  PROBE=$("$FFMPEG" -hide_banner -i "$BASE" 2>&1 | grep -E 'Stream.*Video' | head -1)
  BASE_W=$(echo "$PROBE" | sed -nE 's/.* ([0-9]+)x([0-9]+).*/\1/p')
  BASE_H=$(echo "$PROBE" | sed -nE 's/.* ([0-9]+)x([0-9]+).*/\2/p')
fi
[[ -z "$BASE_W" || -z "$BASE_H" ]] && { log "ERROR: could not probe base resolution"; exit 1; }
log "Base resolution: ${BASE_W}x${BASE_H}"

WORKDIR=$(dirname "$OUT")

# Step 0: Scribe sanitization , strip non-Hebrew/Latin "garbage" characters
# Scribe occasionally drops Devanagari, Tamil, Cyrillic, or CJK characters into
# Hebrew transcripts when a word ending sounds ambiguous (e.g., the soft `-s` of
# colloquial "סקילים" can be transcribed as Devanagari `्स`).
log "Step 0: Scanning for non-Hebrew/Latin garbage characters in SRT"
python3 <<PYEOF
import re
content = open('${SRT}', encoding='utf-8-sig').read()
auto_fixes = {
    'סקיל्स': 'סקילים',          # Devanagari ्स → Hebrew ים (final-mem plural)
    'סקילז्': 'סקילז',                 # Devanagari virama after Hebrew → drop virama
}
fixed_count = 0
for bad, good in auto_fixes.items():
    if bad in content:
        content = content.replace(bad, good)
        fixed_count += 1
        print(f'  Auto-fixed: {repr(bad)} -> {repr(good)}')

allowed = re.compile(r'[֐-׿a-zA-Z0-9\s.,!?\'"()\\[\\]:;\\-–,’>﻿]')
suspicious = []
for ln_num, line in enumerate(content.split('\n'), 1):
    if '-->' in line or re.match(r'^\d+\$', line.strip()): continue
    bad = [(c, f'U+{ord(c):04X}') for c in line if not allowed.match(c) and c != '\n']
    if bad:
        suspicious.append((ln_num, line, bad))

if suspicious:
    print(f'  WARN: {len(suspicious)} caption line(s) contain non-Hebrew/Latin characters after auto-fix:')
    for ln, txt, bad in suspicious[:5]:
        print(f'    Line {ln}: {txt}')
        for c, code in bad: print(f'      -> {repr(c)} ({code})')
    print('  These may render as boxes or wrong shapes. Fix manually before re-running.')
else:
    print(f'  Clean. {fixed_count} auto-fix(es) applied.')

# Write sanitized SRT back (with BOM for libass compatibility)
with open('${SRT}', 'w', encoding='utf-8') as f:
    f.write('﻿' + content.lstrip('﻿'))
PYEOF

# Step 1: Burn captions directly from SRT via libass
# libass + SRT handles Hebrew BiDi correctly without ASS conversion or pre-shape.
# Style is passed inline via force_style (commas in force_style values are escaped \,).
log "Step 1: Burning captions onto ${BASE} -> ${OUT}"
log "  Style: Font=${FONT} ${FONTSIZE}pt Bold, Spacing=${SPACING}, MarginV=${MARGINV}"

# Escape SRT path for ffmpeg subtitles filter (colons need escaping)
ESCAPED_SRT=$(printf '%s' "$SRT" | sed 's/\\/\\\\\\\\/g; s/:/\\:/g')

# Build force_style with commas escaped (filter argument separator is comma, so style
# field separators have to be escaped). PrimaryColour white, OutlineColour black,
# BorderStyle=1 outline, Outline=2px, Alignment=2 (bottom-center), Encoding=1.
FORCE_STYLE="FontName=${FONT}\\,FontSize=${FONTSIZE}\\,Bold=1\\,PrimaryColour=&H00FFFFFF\\,OutlineColour=&H00000000\\,BorderStyle=1\\,Outline=2\\,Shadow=0\\,Alignment=2\\,Spacing=${SPACING}\\,MarginV=${MARGINV}\\,Encoding=1"

"$FFMPEG" -y -loglevel warning \
  -i "$BASE" \
  -vf "subtitles=${ESCAPED_SRT}:fontsdir=${FONTSDIR}:force_style=${FORCE_STYLE}" \
  -c:a copy \
  -c:v libx264 -preset medium -crf 18 \
  "$OUT"

# Step 2: Sample verification frames (one per minute, capped at 30)
log "Step 2: Sampling frames for visual verification"
# Probe duration via ffprobe (more reliable than parsing ffmpeg stderr, which is silenced by -v error)
if command -v "$FFPROBE" >/dev/null 2>&1; then
  DURATION_FLOAT=$("$FFPROBE" -v error -show_entries format=duration -of csv=p=0 "$OUT" 2>/dev/null)
  DURATION=$(printf '%.0f' "${DURATION_FLOAT:-60}" 2>/dev/null || echo 60)
else
  DURATION=$("$FFMPEG" -hide_banner -i "$OUT" 2>&1 | sed -nE 's/.*Duration: ([0-9]+):([0-9]+):([0-9]+).*/\1*3600+\2*60+\3/p' | head -1 | bc)
fi
[[ -z "$DURATION" ]] || [[ "$DURATION" -le 0 ]] && DURATION=60

VERIFY_DIR="${WORKDIR}/verify_$(date +%s)"
mkdir -p "$VERIFY_DIR"

# Sample density: ~1 frame per minute, but at least 3 frames, at most 30
NUM_FRAMES=$(( DURATION / 60 ))
[[ $NUM_FRAMES -lt 3 ]] && NUM_FRAMES=3
[[ $NUM_FRAMES -gt 30 ]] && NUM_FRAMES=30
STEP=$(( DURATION / NUM_FRAMES ))
[[ $STEP -lt 1 ]] && STEP=1

log "  Sampling ${NUM_FRAMES} frames (every ~${STEP}s across ${DURATION}s output)"
# Frame sampling is best-effort: if a single frame fails (e.g. ss past EOF), keep going.
# Do not let this kill the parent script via set -e since the captioned video is already done.
set +e
for ((i=0; i<NUM_FRAMES; i++)); do
  t=$(( STEP * i + STEP / 2 ))
  [[ $t -lt 1 ]] && t=1
  [[ $t -ge $DURATION ]] && t=$((DURATION - 1))
  "$FFMPEG" -y -loglevel error -ss "$t" -i "$OUT" -frames:v 1 \
    -vf "crop=iw:200:0:ih-220" "${VERIFY_DIR}/t$(printf '%04d' $t)s.png" 2>/dev/null
done
set -e
FRAME_COUNT=$(ls "${VERIFY_DIR}"/*.png 2>/dev/null | wc -l | tr -d ' ')
log "  ${VERIFY_DIR}/ contains ${FRAME_COUNT} verification frames"

# Final summary
log ""
log "Done."
log "  Output:        ${OUT}"
log "  Verify frames: ${VERIFY_DIR}/"
log ""
log "MANDATORY VISUAL CHECK (per video-use-best-practices Step 6):"
log "  1. Open each verify_*/t*s.png and confirm:"
log "     a. Captions render in ${FONT} (no tofu boxes, no fallback font)"
log "     b. Hebrew READS correctly (right-to-left)"
log "        Verification: pick any visible caption and confirm Hebrew words read"
log "        naturally from RIGHT to LEFT, periods/question marks at the left end"
log "        of the line (the visual end of the RTL flow)."
log "     c. For mixed-script lines (e.g., 'התקנתי React'), the English token"
log "        stays LTR inline within the RTL flow (React, not tcaeR)."
log "  2. If captions look broken, check: ffmpeg has libass+fontconfig"
log "     (\`ffmpeg -version | grep enable-libass\`), Heebo is installed"
log "     (\`fc-list :family=Heebo\`), and you ran THIS ffmpeg not a different one."
