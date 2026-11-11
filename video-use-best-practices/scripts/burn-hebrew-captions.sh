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
#   5. Sample frames for visual self-verification (1/minute, min 3, max 30)
#
# Usage:
#   burn-hebrew-captions.sh \
#     --base <path/to/base.mp4> \
#     --srt  <path/to/master.srt> \
#     --out  <path/to/final.mp4> \
#     [--font Heebo] \
#     [--fontsdir $HOME/Library/Fonts] \
#     [--font-size N]     # default "auto": scaled from frame height
#     [--spacing 2] \
#     [--margin-v N]      # default "auto": scaled from frame height
#     [--ffmpeg PATH]     # an ffmpeg that has the libass "subtitles" filter (default: ffmpeg on PATH)
#                         # macOS: /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg after `brew install ffmpeg-full`
#
# Requires: ffmpeg with the libass "subtitles" filter (Homebrew's default ffmpeg formula
# lacks it; see references/macos-ffmpeg-setup.md), python3 with python-bidi.

set -euo pipefail

FONT="Heebo"
if [[ "$(uname -s)" == "Darwin" ]]; then
  FONTSDIR="$HOME/Library/Fonts"
else
  FONTSDIR="$HOME/.local/share/fonts"   # where install-hebrew-fonts.sh puts them on Debian
fi
# "auto" scales off the probed video height, see the ratio block after the probe.
# Pass an explicit number to --font-size / --margin-v to override.
FONTSIZE="auto"
SPACING="2"
MARGINV="auto"
FFMPEG="ffmpeg"

BASE=""
PREFLIGHT_ONLY=0
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
    --preflight-only) PREFLIGHT_ONLY=1; shift ;;
    -h|--help)
      sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ $PREFLIGHT_ONLY -eq 0 ]]; then
  [[ -z "$BASE" || -z "$SRT" || -z "$OUT" ]] && { echo "Required: --base BASE.mp4 --srt MASTER.srt --out OUT.mp4" >&2; exit 1; }
  [[ ! -f "$BASE" ]] && { echo "Base video not found: $BASE" >&2; exit 1; }
  [[ ! -f "$SRT" ]] && { echo "SRT not found: $SRT" >&2; exit 1; }
fi
# Numeric options feed shell arithmetic, so accept digits only (or "auto").
for pair in "font-size:$FONTSIZE" "margin-v:$MARGINV" "spacing:$SPACING"; do
  val="${pair#*:}"
  if [[ "$val" != "auto" && ! "$val" =~ ^[0-9]+$ ]]; then
    echo "--${pair%%:*} must be a whole number (got: $val)" >&2; exit 1
  fi
done
[[ "$SPACING" == "auto" ]] && { echo "--spacing must be a whole number" >&2; exit 1; }

log() { printf '[burn-hebrew-captions] %s\n' "$*"; }

# Pre-flight checks
log "Pre-flight: verifying ffmpeg has the libass subtitles filter"
# Test for the filter itself, not a configure flag: builds spell the fontconfig
# flag differently (--enable-libfontconfig vs --enable-fontconfig), but every
# libass build lists "subtitles" here.
# Capture first: `ffmpeg | grep -q` under pipefail fails at random when grep
# exits early and ffmpeg takes SIGPIPE.
FILTERS=$("$FFMPEG" -hide_banner -filters 2>/dev/null || true)
if ! grep -qE '^ *[A-Z.|]+ +subtitles ' <<<"$FILTERS"; then
  log "ERROR: $FFMPEG has no 'subtitles' filter (built without libass)."
  log "       macOS: brew install ffmpeg-full, then pass --ffmpeg /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
  log "       (the default Homebrew ffmpeg formula lacks libass). Other options: references/macos-ffmpeg-setup.md."
  exit 1
fi

log "Pre-flight: verifying Hebrew fonts are available"
HE_FONTS=$(fc-list :lang=he family 2>/dev/null || true)
if ! grep -qiF "$FONT" <<<"$HE_FONTS"; then
  log "ERROR: $FONT not found by fontconfig. Run scripts/install-hebrew-fonts.sh first."
  exit 1
fi

# The Step 1 line-width estimate is measured on Heebo Bold only, and auto-wrap
# is off (WrapStyle 2) to protect line order, so an unmeasured wider font could
# run off the frame. Refuse it rather than ship clipped captions.
if [[ "$FONT" != "Heebo" ]]; then
  log "ERROR: --font $FONT is not supported. Line widths are calibrated on Heebo only, and a wider"
  log "       font can run past the frame edge. Use Heebo (scripts/install-hebrew-fonts.sh)."
  exit 1
fi

log "Pre-flight: verifying python3 + python-bidi"
if ! python3 -c 'from bidi.algorithm import get_display' 2>/dev/null; then
  log "ERROR: python-bidi is not installed for $(command -v python3)."
  log "       Install it once with: python3 -m pip install --user python-bidi"
  log "       (or inside the virtualenv you run video-use from), then re-run."
  exit 1
fi
# --preflight-only lets captions-only.sh run these checks BEFORE it bills a
# Scribe call, instead of discovering a missing libass after paying.
if [[ $PREFLIGHT_ONLY -eq 1 ]]; then
  log "Pre-flight OK (ffmpeg subtitles filter, ${FONT}, python-bidi)."
  exit 0
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

# ---------------------------------------------------------------------------
# Font size and bottom margin are RATIOS of the frame height, not fixed pixels.
#
# Why this is not cosmetic. Step 3 below rewrites `PlayResY: 288` to the real
# video height, which changes the unit MarginV is expressed in. Upstream
# video-use ships `Alignment=2,MarginV=90` against libass default PlayResY=288,
# i.e. 31.25% of frame height, and helpers/render.py explains why: "TikTok /
# IG Reels / Shorts UI ... covers roughly the bottom ~25-30% of a 1080x1920
# frame ... Do not drop this below ~75 without a specific reason."
#
# Carrying a fixed MarginV=80 into 1920-tall coordinates silently turned that
# 31.25% into 4.2%. Measured on a 1080x1920 render: the caption baseline sat
# 89px from the bottom, 4.6% of frame height, i.e. buried inside the platform
# UI band that upstream value exists to clear. Font size collapsed the same
# way: 52/1920 is 2.7% against upstream 18/288 = 6.25%.
#
# A 9:16 source uses upstream's ratios directly, since upstream's stated
# rationale is the full-screen vertical player UI. Everything else (landscape,
# 4:5 feed posts, square) keeps this script's previously shipping effective
# ratios (52/1080 and 80/1080), because a lecture, webinar or feed post has no
# bottom action rail and a 31% margin would float the captions into the middle
# of the frame.
# ---------------------------------------------------------------------------
# Upstream's 31.25% safe zone is specifically about the full-screen 9:16 player
# UI. A 4:5 Instagram feed post (1080x1350) is taller than it is wide but has no
# in-frame action rail, and a 31% margin would float its captions into the middle
# third. Test for an aspect at least as tall as 9:16 rather than merely portrait.
if [[ $(( BASE_H * 9 )) -ge $(( BASE_W * 16 )) ]]; then
  ORIENTATION="portrait 9:16"
  FONT_RATIO_NUM=625;   FONT_RATIO_DEN=10000     # 18/288, upstream proven size
  MARGIN_RATIO_NUM=3125; MARGIN_RATIO_DEN=10000  # 90/288, upstream safe zone
else
  ORIENTATION="standard (not 9:16)"
  FONT_RATIO_NUM=481;   FONT_RATIO_DEN=10000     # 52/1080, previously shipped
  MARGIN_RATIO_NUM=741;  MARGIN_RATIO_DEN=10000  # 80/1080, previously shipped
fi
[[ "$FONTSIZE" == "auto" ]] && FONTSIZE=$(( BASE_H * FONT_RATIO_NUM / FONT_RATIO_DEN ))
[[ "$MARGINV"  == "auto" ]] && MARGINV=$(( BASE_H * MARGIN_RATIO_NUM / MARGIN_RATIO_DEN ))
# Outline, letter spacing and side margins live in the SAME rewritten coordinate
# space as FontSize, so leaving them at fixed pixels reintroduces the unit bug at
# a smaller scale: an Outline of 4px against a 120px font is a third of the
# relative stroke upstream ships (Outline=2 against FontSize=18, i.e. 11%).
OUTLINE_PX=$(( FONTSIZE * 11 / 100 ))
[[ $OUTLINE_PX -lt 1 ]] && OUTLINE_PX=1
# Round rather than truncate: integer division floored small frames to 0 spacing,
# which silently drops the Hebrew tracking this script exists to add.
SPACING_PX=$(( (FONTSIZE * SPACING + 26) / 52 ))
[[ $SPACING_PX -lt 1 ]] && SPACING_PX=1
MARGIN_H=$(( BASE_W * 37 / 1000 ))   # 40/1080, the side gutter this script has always shipped
log "Orientation: ${ORIENTATION}. Font ${FONTSIZE}px, bottom margin ${MARGINV}px, outline ${OUTLINE_PX}px, side margin ${MARGIN_H}px (frame ${BASE_W}x${BASE_H})."

WORKDIR=$(dirname "$OUT")
mkdir -p "$WORKDIR"
# Intermediates live in a private temp dir, not beside the user's video, and
# Step 0 sanitizes into a copy: it used to write back over the file passed to
# --srt, silently rewriting video-use's own master.srt (a paid Scribe artifact).
TMPW=$(mktemp -d)
trap 'rm -rf "$TMPW"' EXIT
CLEAN_SRT="${TMPW}/clean.srt"
BIDI_SRT="${TMPW}/bidi.srt"
RAW_ASS="${TMPW}/raw.ass"
PATCHED_ASS="${TMPW}/captions.ass"

# Step 0: Scribe sanitization , strip non-Hebrew/Latin "garbage" characters
# Scribe occasionally drops Devanagari, Tamil, Cyrillic, or CJK characters into
# Hebrew transcripts when a word ending sounds ambiguous (e.g., the soft `-s` of
# colloquial "סקילים" can be transcribed as Devanagari virama + sa, U+094D U+0938).
log "Step 0: Sanitizing SRT (Scribe garbage chars + Hebrew sentence-end punctuation position)"
SRT_IN="$SRT" CLEAN_SRT="$CLEAN_SRT" python3 - <<'PYEOF'
import os
import re, sys
content = open(os.environ['SRT_IN'], encoding='utf-8-sig').read()
# Auto-fixes for known Scribe Hebrew failure modes (extend as you find more)
auto_fixes = {
    'סקיל\u094d\u0938': 'סקילים',   # Devanagari virama+sa -> Hebrew ים (final-mem plural)
    'סקילז\u094d': 'סקילז',          # Devanagari virama after Hebrew -> drop virama
}
fixed_count = 0
for bad, good in auto_fixes.items():
    if bad in content:
        content = content.replace(bad, good)
        fixed_count += 1
        print(f'  Auto-fixed: {repr(bad)} -> {repr(good)}')

# STRIP trailing sentence-end punctuation from Hebrew lines (BBC/Netflix style).
# Why: the pre-shape gets the letters and words into correct RTL visual order,
# but sentence-end punctuation placement varies with the script mix (pure Hebrew
# vs Hebrew+English). Rather than fight the BiDi algorithm with positioning
# hacks, drop sentence-end punctuation from captions entirely. This matches BBC and Netflix caption style
# guides, which recommend minimal punctuation since line breaks and timing
# already signal end-of-thought.
HEBREW_RANGE = re.compile(r'[֐-׿]')
SENTENCE_END = re.compile(r'^(.*?)\s*[.?!]+\s*$')
punct_stripped = 0
new_lines = []
for line in content.split('\n'):
    # Only touch caption text lines (not cue numbers, not timestamps)
    if '-->' in line or re.match(r'^\d+$', line.strip()) or not line.strip():
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
# Percent, slash, plus, ampersand and friends are ordinary caption content
# (הנחה של 15%, dates like 3/4). They were absent from this class, so every
# price or date line produced a false "may render as boxes" warning.
allowed = re.compile(r'[֐-׿a-zA-Z0-9\s.,!?\'"()\[\]:;\-–,’>%/+=&#@*_₪\ufeff]')
suspicious = []
for ln_num, line in enumerate(content.split('\n'), 1):
    if '-->' in line or re.match(r'^\d+$', line.strip()): continue
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

# Write the sanitized version to a WORKDIR copy. NEVER write back over
# the --srt input: that is the caller's file and may be video-use's master transcript.
with open(os.environ['CLEAN_SRT'], 'w', encoding='utf-8') as f:
    f.write('\ufeff' + content.lstrip('\ufeff'))
PYEOF

# Step 1: Pre-shape SRT with python-bidi
# The pre-shape exists because libass on macOS does not apply BiDi reordering to
# SRT-derived events. It is validated on macOS only. On a libass build that DOES
# reorder, feeding it display-order text reverses it a second time and every
# Hebrew caption comes out backwards, with no error. Warn rather than guess, and
# tell the operator exactly what to look at.
if [[ "$(uname -s)" != "Darwin" ]]; then
  log "  NOTE: the python-bidi pre-shape is validated on macOS, where libass does not"
  log "        reorder SRT BiDi. This looks like $(uname -s). If your libass DOES reorder,"
  log "        the pre-shape double-reverses and captions render backwards."
  log "        Check the verification frames in Step 5 before rendering anything long:"
  log "        the FIRST word of each source line must appear at the visual RIGHT."
fi
log "Step 1: Pre-shaping Hebrew with python-bidi (logical -> display order), pre-wrapping long lines"
CLEAN_SRT="$CLEAN_SRT" BIDI_SRT="$BIDI_SRT" BASE_W="$BASE_W" MARGIN_H="$MARGIN_H" \
FONTSIZE="$FONTSIZE" SPACING_PX="$SPACING_PX" python3 - <<'PYEOF'
import math
import os
import re
from bidi.algorithm import get_display

E = os.environ
fs, sp = int(E['FONTSIZE']), int(E['SPACING_PX'])
avail = (int(E["BASE_W"]) - 2 * int(E["MARGIN_H"])) * 0.95

def est_width(s):
    # Estimate in FontSize units, as libass scales them: 0.45 per glyph, 0.25
    # per space, plus the letter spacing added to every character. Measured on
    # Heebo Bold renders (2026-11-11): about 0.33 per glyph on ordinary caption
    # text and 0.53 for a run of the widest letter (ש). Wider fonts than Heebo
    # can overflow; WrapStyle 2 (Step 3) makes that visible rather than reorder.
    glyphs = sum(1 for c in s if not c.isspace())
    return glyphs * 0.45 * fs + (len(s) - glyphs) * 0.25 * fs + len(s) * sp

def wrap_logical(line):
    """Split a too-wide line into balanced lines, in LOGICAL (reading) order.

    This must happen BEFORE the pre-shape. libass wraps display-order text
    left to right, so letting it wrap a pre-shaped line puts the END of the
    sentence on the top line. Measured on a 1080x1920 render: "React ... ועל
    זה נדבר" came out with "ועל זה נדבר" above "React הוא מעולה".
    """
    words = line.split()
    n = math.ceil(est_width(line) / avail)
    if n <= 1 or len(words) < 2:
        return [line]
    n = min(n, len(words))
    if n >= len(words):
        return words
    # Choose the n-1 break points that minimise the widest line (small DP:
    # captions are a handful of words), so the lines come out balanced.
    W = len(words)
    seg = lambda i, j: est_width(' '.join(words[i:j]))
    best = {}
    def solve(i, k):
        if (i, k) in best:
            return best[(i, k)]
        if k == 1:
            r = (seg(i, W), [W])
        else:
            r = min(((max(seg(i, j), solve(j, k - 1)[0]), [j] + solve(j, k - 1)[1])
                     for j in range(i + 1, W - k + 2)), key=lambda x: x[0])
        best[(i, k)] = r
        return r
    # The line count above is an estimate. If the widest balanced line still
    # does not fit, add a line rather than let libass wrap display-order text.
    while solve(0, n)[0] > avail and n < W:
        n += 1
    cuts = solve(0, n)[1]
    lines, start = [], 0
    for c in cuts:
        lines.append(' '.join(words[start:c])); start = c
    return lines

src = open(E['CLEAN_SRT'], encoding='utf-8-sig').read()  # sanitized copy, not the caller's file
out_lines = []
wrapped = 0
for line in src.split('\n'):
    if re.match(r'^\d+$', line.strip()) or '-->' in line or line.strip() == '':
        out_lines.append(line)
        continue
    parts = wrap_logical(line.strip())
    wrapped += len(parts) > 1
    has_hebrew = re.search(r'[\u0590-\u05ff]', line) is not None
    for part in parts:
        if not has_hebrew:
            # A Latin-only caption is an LTR paragraph. Forcing base_dir='R'
            # on it moves trailing punctuation to the wrong end ('.Thank you').
            out_lines.append(part)
            continue
        # base_dir='R' is load-bearing. Without it python-bidi infers the
        # paragraph direction from the first strong character, so any caption
        # that STARTS with a Latin token ("React הוא מעולה", "ChatGPT משנה...")
        # is treated as an LTR paragraph and comes out in reversed word order.
        # Measured: get_display("React הוא מעולה") puts React leftmost;
        # with base_dir='R' it is rightmost, which is correct for a Hebrew line.
        out_lines.append(get_display(part, base_dir='R'))
# Write WITH UTF-8 BOM for downstream libass compatibility
with open(E['BIDI_SRT'], 'w', encoding='utf-8') as f:
    f.write('\ufeff' + '\n'.join(out_lines))
print(f'Pre-shaped: {len([l for l in out_lines if l.strip() and not l.strip().isdigit() and "-->" not in l])} caption lines ({wrapped} pre-wrapped)')
PYEOF

# Step 2: Convert to ASS
log "Step 2: Converting pre-shaped SRT to ASS"
"$FFMPEG" -y -loglevel error -i "$BIDI_SRT" "$RAW_ASS"

# Step 3: Patch ASS - PlayRes to match output, Heebo style with Spacing
log "Step 3: Patching ASS (PlayRes=${BASE_W}x${BASE_H}, Font=${FONT} ${FONTSIZE}, Spacing=${SPACING}, MarginV=${MARGINV})"
RAW_ASS="$RAW_ASS" PATCHED_ASS="$PATCHED_ASS" FONT="$FONT" FONTSIZE="$FONTSIZE" BASE_W="$BASE_W" BASE_H="$BASE_H" SPACING_PX="$SPACING_PX" OUTLINE_PX="$OUTLINE_PX" MARGIN_H="$MARGIN_H" MARGINV="$MARGINV" python3 - <<'PYEOF'
import os
import sys
E = os.environ
W, H = E['BASE_W'], E['BASE_H']
src = open(E['RAW_ASS'], encoding='utf-8').read()
# The style values below are in OUTPUT-PIXEL units, which is only true once
# PlayRes has been rewritten to the real frame size. If ffmpeg ever emits a
# different default canvas, or omits PlayRes entirely (libass then assumes 288),
# the font size would be interpreted against 288 and the caption would render
# off-frame. Fail loudly instead of rendering garbage.
n_y = src.count('PlayResY: 288')
if n_y != 1:
    if 'PlayResY:' in src:
        sys.exit('ERROR: unexpected PlayResY in generated ASS; expected exactly one "PlayResY: 288". '
                 'Style values are in output-pixel units and would be misinterpreted. Aborting.')
    # No PlayRes header at all: insert one so libass does not fall back to 288.
    src = src.replace('[Script Info]', f'[Script Info]\nPlayResX: {W}\nPlayResY: {H}', 1)
    if f'PlayResY: {H}' not in src:
        sys.exit('ERROR: generated ASS has no [Script Info] section to add PlayRes to. Aborting.')
else:
    src = src.replace('PlayResX: 384', f'PlayResX: {W}')
    src = src.replace('PlayResY: 288', f'PlayResY: {H}')
# WrapStyle 2 = never auto-wrap. Lines were already split in reading order in
# Step 1; an automatic wrap of pre-shaped text would put the sentence END on
# the top line. A line that overflows the frame is visible in the verification
# frames, a silently reordered one is not.
import re as _re
if _re.search(r'^WrapStyle:.*$', src, flags=_re.M):
    src = _re.sub(r'^WrapStyle:.*$', 'WrapStyle: 2', src, count=1, flags=_re.M)
else:
    src = src.replace('[Script Info]', '[Script Info]\nWrapStyle: 2', 1)
# Build the V4+ Style line in canonical order:
# Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour,
# Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle,
# Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
new_style = (
    f"Style: Default,{E['FONT']},{E['FONTSIZE']},"
    '&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,'  # white text, black outline
    '-1,0,0,0,'                                     # Bold=true, no italic/underline/strikeout
    f"100,100,{E['SPACING_PX']},0,"                 # ScaleX/Y=100, Spacing, Angle=0
    f"1,{E['OUTLINE_PX']},0,"                       # BorderStyle=1 outline, Outline, Shadow=0
    f"2,{E['MARGIN_H']},{E['MARGIN_H']},{E['MARGINV']},"  # Alignment=bottom-center, MarginL/R, MarginV
    '1'                                             # Encoding=1 (libass: MUST always be 1)
)
out = [new_style if l.startswith('Style: Default,') else l for l in src.splitlines()]
open(os.environ['PATCHED_ASS'], 'w', encoding='utf-8').write('\n'.join(out) + '\n')
PYEOF

# Step 4: Burn captions
log "Step 4: Burning captions onto ${BASE} -> ${OUT}"
# Map every audio stream explicitly. Without -map, ffmpeg keeps ONE audio
# stream, the one with the most channels: on an OBS recording that is the
# desktop/game track, so the captioned file shipped without the mic.
# Escape paths for the subtitles filter. Two levels apply: the filter option
# value (backslash, quote, colon) and then the filtergraph (backslash, quote,
# brackets, comma, semicolon). Escaping only colons broke on any output folder
# containing an apostrophe, comma or bracket.
ff_escape() {
  python3 -c '
import sys
v = sys.argv[1]
v = "".join("\\" + c if c in "\\\x27:" else c for c in v)
v = "".join("\\" + c if c in "\\\x27[],;" else c for c in v)
print(v, end="")' "$1"
}
ESCAPED_ASS=$(ff_escape "$PATCHED_ASS")
ESCAPED_FONTSDIR=$(ff_escape "$FONTSDIR")
"$FFMPEG" -y -loglevel warning \
  -i "$BASE" \
  -map 0:v:0 -map '0:a?' \
  -vf "subtitles=${ESCAPED_ASS}:fontsdir=${ESCAPED_FONTSDIR}" \
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

# The crop MUST follow the caption band. It used to be a fixed 200px strip 20px
# above the bottom edge, which stopped containing the captions the moment the
# margin became a ratio: on a 1080x1920 portrait render the captions now sit
# ~600px up, so every verification frame was empty background while the script
# still printed "MANDATORY VISUAL CHECK". Derive the window from the values
# actually used, with generous padding for descenders and two-line cues.
# Anchor the window on the MARGIN and open it upward, rather than guessing a
# line count. Measured on a 9:16 render at 120px font: a 3-line cue spans ~450px
# and a 5-line cue spans 662px, so a FONTSIZE*5 window still clipped the top of
# the latter. FONTSIZE*7 upward from one line below the margin covers both, and
# an oversized PNG costs nothing. A cue taller than six lines will still clip;
# that is a caption-design problem, not a verification problem.
CROP_H=$(( FONTSIZE * 7 ))
CROP_Y=$(( BASE_H - MARGINV - FONTSIZE * 6 ))
[[ $CROP_Y -lt 0 ]] && CROP_Y=0
[[ $(( CROP_Y + CROP_H )) -gt $BASE_H ]] && CROP_H=$(( BASE_H - CROP_Y ))
log "  Sampling ${NUM_FRAMES} frames (every ~${STEP}s across ${DURATION}s output), crop ${CROP_H}px at y=${CROP_Y}"
# Frame sampling is best-effort: if a single frame fails (e.g. ss past EOF), keep going.
# Do not let this kill the parent script via set -e since the captioned video is already done.
set +e
for ((i=0; i<NUM_FRAMES; i++)); do
  t=$(( STEP * i + STEP / 2 ))
  [[ $t -lt 1 ]] && t=1
  [[ $t -ge $DURATION ]] && t=$((DURATION - 1))
  "$FFMPEG" -y -loglevel error -ss "$t" -i "$OUT" -frames:v 1 \
    -vf "crop=iw:${CROP_H}:0:${CROP_Y}" "${VERIFY_DIR}/t$(printf '%04d' $t)s.png" 2>/dev/null
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
log "        For 'ספריית הסקילז AI שבניתי' the FIRST source word (ספריית) must be"
log "        rightmost and the last (שבניתי) leftmost, with AI between them."
log "        A mid-line comma sits to the LEFT of the word it follows."
log "        On a multi-line cue, the TOP line holds the start of the sentence."
log "     c. For mixed-script lines (e.g., 'התקנתי React'), the English token"
log "        stays LTR inline within the RTL flow."
log "  2. If ANY check fails, the python-bidi pre-shape didn't run or the ffmpeg"
log "     used is not the one this script invoked. Re-check the pre-flight output."
