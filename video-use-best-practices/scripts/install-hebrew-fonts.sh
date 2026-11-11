#!/usr/bin/env bash
# install-hebrew-fonts.sh
# Idempotent, user-level installer for the four Hebrew fonts video-use captions use:
# Heebo, Rubik, Assistant and Noto Sans Hebrew.
#
# - No root, no package manager. Fonts go into the per-user font directory:
#     macOS:  ~/Library/Fonts
#     Linux:  ~/.local/share/fonts   (override either with FONTS_DIR=/path)
# - Every file is fetched from the official google/fonts GitHub repository at a
#   PINNED commit and checked against a SHA-256 recorded below. A mismatch aborts
#   before anything is written to the font directory.
# - Fonts are data files, not executables. Nothing downloaded here is run.
#
# After running, verify with: fc-list :lang=he | head

set -euo pipefail

# google/fonts commit the URLs and checksums below were taken from (2026-11-08).
# To update: pick a newer commit, re-download, and re-record every checksum.
readonly GF_COMMIT="5bb28733cec313b63fbd415b574b5ae35c8aa8b8"
readonly GF_BASE="https://raw.githubusercontent.com/google/fonts/${GF_COMMIT}/ofl"

# family | path under ofl/ | local file name | sha256
readonly FONT_TABLE=(
  "Heebo|heebo/Heebo%5Bwght%5D.ttf|Heebo[wght].ttf|18f930b583fa8fe6b40b2f8263b7ac6afbac07adc91a12467874e7467d3ace30"
  "Rubik|rubik/Rubik%5Bwght%5D.ttf|Rubik[wght].ttf|1b3a7437ba2af80e465e773ed60c5036d1ba6ace492d89046dbcf18fb31e4e88"
  "Assistant|assistant/Assistant%5Bwght%5D.ttf|Assistant[wght].ttf|1c3b393884f8fb133a1b17f41d26178adae1050a4f86d7a429d1b5658c314fa3"
  "Noto Sans Hebrew|notosanshebrew/NotoSansHebrew%5Bwdth,wght%5D.ttf|NotoSansHebrew[wdth,wght].ttf|7ef36a2c3593758cdb622e1bdef4f84523e92fbc3ccc667438dd80ff54c2de88"
)

log() { printf '[install-hebrew-fonts] %s\n' "$*"; }

if [[ "$(id -u)" -eq 0 ]]; then
  log "ERROR: run this as your normal user. It installs into your own user font directory."
  exit 1
fi

case "$(uname -s)" in
  Darwin) DEFAULT_DIR="$HOME/Library/Fonts" ;;
  Linux)  DEFAULT_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/fonts" ;;
  *) log "ERROR: unsupported OS $(uname -s). Copy the four TTFs into your user font directory by hand."; exit 1 ;;
esac
FONTS_DIR="${FONTS_DIR:-$DEFAULT_DIR}"

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -c1-64
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -c1-64
  else log "ERROR: need sha256sum or shasum to verify downloads."; exit 1
  fi
}

command -v curl >/dev/null 2>&1 || { log "ERROR: curl is required."; exit 1; }
mkdir -p "$FONTS_DIR"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

failed=0
installed=0
for row in "${FONT_TABLE[@]}"; do
  IFS='|' read -r family path fname want <<<"$row"
  dest="$FONTS_DIR/$fname"
  if [[ -f "$dest" ]] && [[ "$(sha256_of "$dest")" == "$want" ]]; then
    log "  $family already installed at $dest"
    continue
  fi
  log "  downloading $family ..."
  tmp="$TMP_DIR/$fname"
  if ! curl -fsSL --proto '=https' -o "$tmp" "$GF_BASE/$path"; then
    log "  ERROR: download failed for $family"; failed=1; continue
  fi
  got=$(sha256_of "$tmp")
  if [[ "$got" != "$want" ]]; then
    log "  ERROR: checksum mismatch for $family (got $got, expected $want). Not installed."
    failed=1; continue
  fi
  mv "$tmp" "$dest"
  installed=$((installed + 1))
  log "  installed $family -> $dest"
done

if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$FONTS_DIR" >/dev/null 2>&1 || true
fi

if command -v fc-list >/dev/null 2>&1; then
  log "fontconfig now reports:"
  fc-list :lang=he family | grep -iE 'heebo|rubik|assistant|noto sans hebrew' | sort -u | head -10 || true
else
  log "NOTE: fc-list is not installed, so fontconfig cannot be queried. burn-hebrew-captions.sh"
  log "      checks fonts with fc-list; on macOS install it with: brew install fontconfig"
fi

if [[ $failed -ne 0 ]]; then
  log "ERROR: one or more fonts were not installed. Captions in a missing font render as boxes."
  exit 1
fi
log "Done (${installed} newly installed). Font directory: $FONTS_DIR"
log "Pass this directory to the subtitles filter as fontsdir= (burn-hebrew-captions.sh --fontsdir)."
