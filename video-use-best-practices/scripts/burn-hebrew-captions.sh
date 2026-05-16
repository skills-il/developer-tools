#!/usr/bin/env bash
# burn-hebrew-captions.sh
# End-to-end Hebrew caption burn-in for video-use output (and any base.mp4 + master.srt pair).
#
# Why this script exists: libass on macOS with static-build FFmpeg silently skips BiDi
# reordering even when libfribidi is theoretically linked. The result is that Hebrew
# characters get drawn in source byte order (LTR), which looks like the words are in the
# wrong positions. Calling `ffmpeg -i master.srt master.ass` alone does NOT fix this.
# The reliable workaround is to pre-shape the text with python-bidi BEFORE rendering, so
# libass just draws what it sees and the result is RTL-correct on screen.
#
# This script does the full working recipe:
#   1. Pre-shape SRT with python-bidi (logical -> display order)
#   2. Convert pre-shaped SRT to ASS via ffmpeg
#   3. Patch ASS: PlayResX/Y to match output resolution, Heebo style with proper spacing
#   4. Burn captions onto the base video with explicit fontsdir
#   5. Sample 3 frames for visual self-verification
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
FONTSIZE="52"
SPACING="2"
MARGINV="80"
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

log "Pre-flight: verifying python3 + python-bidi"
if ! python3 -c 'import bidi' 2>/dev/null; then
  log "Installing python-bidi (one-time)."
  pip3 install --quiet python-bidi
fi

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
BIDI_SRT="${WORKDIR}/.bidi_$(basename "$SRT")"
RAW_ASS="${WORKDIR}/.raw_$(basename "${SRT%.srt}.ass")"
PATCHED_ASS="${WORKDIR}/$(basename "${SRT%.srt}.bidi.ass")"

# Step 0: Scribe sanitization , strip non-Hebrew/Latin "garbage" characters
# Scribe occasionally drops Devanagari, Tamil, Cyrillic, or CJK characters into
# Hebrew transcripts when a word ending sounds ambiguous (e.g., the soft `-s` of
# colloquial "סקילים" can be transcribed as Devanagari `्स`).
log "Step 0: Sanitizing SRT (Scribe garbage chars + Hebrew sentence-end punctuation position)"
python3 <<PYEOF
import re, sys
content = open('${SRT}', encoding='utf-8-sig').read()
# Auto-fixes for known Scribe Hebrew failure modes (extend as you find more)
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

# STRIP trailing sentence-end punctuation from Hebrew lines (BBC/Netflix style).
# Why: the python-bidi + libass double-reversal puts Hebrew chars in source-order
# LTR pixel positions (which the user wants), but punctuation positioning becomes
# unstable depending on script mix (pure Hebrew vs Hebrew+English). Rather than
# fight the BiDi algorithm with positioning hacks, just drop sentence-end
# punctuation from captions entirely. This matches BBC and Netflix caption style
# guides, which recommend minimal punctuation since line breaks and timing
# already signal end-of-thought.
HEBREW_RANGE = re.compile(r'[֐-׿]')
SENTENCE_END = re.compile(r'^(.*?)\s*[.?!]+\s*\$')
punct_stripped = 0
new_lines = []
for line in content.split('\n'):
    # Only touch caption text lines (not cue numbers, not timestamps)
    if '-->' in line or re.match(r'^\d+\$', line.strip()) or not line.strip():
        new_lines.append(line)
        continue
    # Only act if the line contains Hebrew
    if not HEBREW_RANGE.search(line):
        new_lines.append(line)
        continue
    m = SENTENCE_END.match(line)
    if m and m.group(1).strip():
        new_lines.append(m.group(1).rstrip())
        punct_stripped += 1
    else:
        new_lines.append(line)
content = '\n'.join(new_lines)
if punct_stripped > 0:
    print(f'  Stripped sentence-end punctuation (. ? !) from {punct_stripped} Hebrew line(s) for clean caption display.')

# Now scan for remaining suspicious characters
allowed = re.compile(r'[֐-׿a-zA-Z0-9\s.,!?\'"()\\[\\]:;\\-–,’>﻿]')
suspicious = []
for ln_num, line in enumerate(content.split('\n'), 1):
    if '-->' in line or re.match(r'^\d+\$', line.strip()): continue
    bad = [(c, f'U+{ord(c):04X}') for c in line if not allowed.match(c) and c != '\n']
    if bad:
        suspicious.append((ln_num, line, bad))

if suspicious:
    print(f'  WARN: {len(suspicious)} caption line(s) still contain non-Hebrew/Latin characters after auto-fix:')
    for ln, txt, bad in suspicious[:5]:
        print(f'    Line {ln}: {txt}')
        for c, code in bad:
            print(f'      -> {repr(c)} ({code})')
    print('  These may render as boxes or wrong shapes. Fix manually in the SRT before re-running.')
elif fixed_count == 0 and punct_stripped == 0:
    print(f'  Clean. No changes needed.')

# Write back the sanitized version
with open('${SRT}', 'w', encoding='utf-8') as f:
    f.write('﻿' + content.lstrip('﻿'))
PYEOF

# Step 1: Pre-shape SRT with python-bidi
log "Step 1: Pre-shaping Hebrew with python-bidi (logical -> display order)"
python3 <<PYEOF
import re
from bidi.algorithm import get_display

src = open('${SRT}', encoding='utf-8-sig').read()  # strip leading BOM if present
out_lines = []
for line in src.split('\n'):
    if re.match(r'^\d+$', line.strip()) or '-->' in line or line.strip() == '':
        out_lines.append(line)
    else:
        out_lines.append(get_display(line))
# Write WITH UTF-8 BOM for downstream libass compatibility
with open('${BIDI_SRT}', 'w', encoding='utf-8') as f:
    f.write('﻿' + '\n'.join(out_lines))
print(f'Pre-shaped: {len([l for l in out_lines if l.strip() and not l.strip().isdigit() and "-->" not in l])} caption lines')
PYEOF

# Step 2: Convert to ASS
log "Step 2: Converting pre-shaped SRT to ASS"
"$FFMPEG" -y -loglevel error -i "$BIDI_SRT" "$RAW_ASS"

# Step 3: Patch ASS - PlayRes to match output, Heebo style with Spacing
log "Step 3: Patching ASS (PlayRes=${BASE_W}x${BASE_H}, Font=${FONT} ${FONTSIZE}, Spacing=${SPACING}, MarginV=${MARGINV})"
python3 <<PYEOF
src = open('${RAW_ASS}').read()
src = src.replace('PlayResX: 384', 'PlayResX: ${BASE_W}')
src = src.replace('PlayResY: 288', 'PlayResY: ${BASE_H}')
# Build the V4+ Style line in canonical order:
# Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour,
# Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle,
# Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
new_style = (
    'Style: Default,${FONT},${FONTSIZE},'
    '&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,'  # white text, black outline
    '-1,0,0,0,'                                     # Bold=true, no italic/underline/strikeout
    '100,100,${SPACING},0,'                         # ScaleX/Y=100, Spacing, Angle=0
    '1,4,0,'                                        # BorderStyle=1 outline, Outline=4px, Shadow=0
    '2,40,40,${MARGINV},'                           # Alignment=bottom-center, MarginL/R=40, MarginV
    '1'                                             # Encoding=1 (libass: MUST always be 1)
)
out = [new_style if l.startswith('Style: Default,') else l for l in src.splitlines()]
open('${PATCHED_ASS}', 'w').write('\n'.join(out) + '\n')
PYEOF

# Step 4: Burn captions
log "Step 4: Burning captions onto ${BASE} -> ${OUT}"
# Escape the ASS path for ffmpeg subtitles filter (colons and backslashes)
ESCAPED_ASS=$(printf '%s' "$PATCHED_ASS" | sed 's/\\/\\\\\\\\/g; s/:/\\:/g')
"$FFMPEG" -y -loglevel warning \
  -i "$BASE" \
  -vf "subtitles=${ESCAPED_ASS}:fontsdir=${FONTSDIR}" \
  -c:a copy \
  -c:v libx264 -preset medium -crf 18 \
  "$OUT"

# Step 5: Sample verification frames (one per minute, capped at 30)
log "Step 5: Sampling frames for visual verification"
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
log "     b. Hebrew words appear in correct RTL visual order"
log "        For 'ספריית הסקילז AI שבניתי.' the pixel LTR order should read:"
log "        ספריית [right] הסקילז AI שבניתי [left] ."
log "        (period on LEFT, first source word on RIGHT)"
log "     c. For mixed-script lines (e.g., 'התקנתי React'), the English token"
log "        stays LTR inline within the RTL flow."
log "  2. If ANY check fails, the python-bidi pre-shape didn't run or the ffmpeg"
log "     used is not the one this script invoked. Re-check the pre-flight output."
