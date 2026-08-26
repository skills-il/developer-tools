#!/usr/bin/env bash
# install-hebrew-fonts.sh
# Idempotent installer for Hebrew fonts required by video-use's libass + fontconfig
# subtitle rendering. Covers macOS (Homebrew cask) and Debian/Ubuntu (apt + manual fallback).
#
# After running, verify with: fc-list :lang=he | head

set -euo pipefail

readonly FONTS=("Heebo" "Rubik" "Assistant" "Noto Sans Hebrew")

log() { printf '[install-hebrew-fonts] %s\n' "$*"; }

check_already_installed() {
  if command -v fc-list >/dev/null 2>&1; then
    local count
    count=$(fc-list :lang=he 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -ge 4 ]; then
      log "fontconfig already reports $count Hebrew-capable fonts. Verifying canonical set."
      local missing=()
      for f in "${FONTS[@]}"; do
        if ! fc-list :lang=he | grep -qi "$f"; then
          missing+=("$f")
        fi
      done
      if [ ${#missing[@]} -eq 0 ]; then
        log "All canonical fonts present. Nothing to do."
        return 0
      fi
      log "Missing: ${missing[*]}. Continuing install."
      return 1
    fi
  fi
  return 1
}

install_macos() {
  if ! command -v brew >/dev/null 2>&1; then
    log "ERROR: Homebrew not installed. Install from https://brew.sh, then re-run."
    exit 1
  fi

  log "Installing fonts via Homebrew Cask."
  for cask in font-heebo font-rubik font-assistant font-noto-sans-hebrew; do
    if brew list --cask "$cask" >/dev/null 2>&1; then
      log "  $cask already installed."
    else
      log "  installing $cask..."
      brew install --cask "$cask" || log "  WARN: $cask install failed (may be unavailable in your tap). Continuing."
    fi
  done

  # Ensure fontconfig is present (libass uses it on macOS too if available).
  if ! command -v fc-list >/dev/null 2>&1; then
    log "Installing fontconfig (needed for fc-list/fc-cache)."
    brew install fontconfig
  fi
}

install_debian() {
  log "Installing fonts via apt where available, manual download fallback for the rest."

  if [ "$(id -u)" -ne 0 ] && ! command -v sudo >/dev/null 2>&1; then
    log "ERROR: Need root or sudo for apt install. Re-run with sudo or as root."
    exit 1
  fi

  local SUDO=""
  [ "$(id -u)" -ne 0 ] && SUDO="sudo"

  $SUDO apt-get update -qq
  # fonts-noto-hebrew packages Noto Sans Hebrew.
  $SUDO apt-get install -y -qq fonts-noto-hebrew fontconfig || true

  # Heebo, Rubik, Assistant are not in Debian/Ubuntu apt repos as of 2026-05; install from Google Fonts.
  local fonts_dir="$HOME/.local/share/fonts"
  mkdir -p "$fonts_dir"

  # Do NOT use https://fonts.google.com/download?family=X here. That endpoint
  # returns HTTP 200 with the Google Fonts SPA shell (content-type text/html,
  # ~190KB), so `curl -f` succeeds, `unzip` fails, the failure was swallowed by
  # a WARN, and the script printed "Done." having installed nothing. Verified
  # 2026-08-26. Fetch the variable font directly from the google/fonts repo
  # instead, and hard-fail on anything that is not actually a font file.
  local ok=1
  for family_url in \
      "Heebo|https://github.com/google/fonts/raw/main/ofl/heebo/Heebo%5Bwght%5D.ttf" \
      "Rubik|https://github.com/google/fonts/raw/main/ofl/rubik/Rubik%5Bwght%5D.ttf" \
      "Assistant|https://github.com/google/fonts/raw/main/ofl/assistant/Assistant%5Bwght%5D.ttf"; do
    local family="${family_url%%|*}"
    local url="${family_url#*|}"
    if fc-list :lang=he 2>/dev/null | grep -qi "$family"; then
      log "  $family already present."
      continue
    fi
    log "  downloading $family..."
    local tmp_ttf
    tmp_ttf=$(mktemp -t "${family}.XXXXXX.ttf")
    if ! curl -fsSL -o "$tmp_ttf" "$url"; then
      log "  ERROR: download failed for $family ($url)."
      rm -f "$tmp_ttf"; ok=0; continue
    fi
    # Magic-byte check. Do NOT use grep for this: BRE/ERE does not expand \xNN,
    # so a `grep -qE '^\x00\x01\x00\x00'` never matches a real TTF and the whole
    # guard silently falls through to file(1), which slim images do not ship.
    # Hex-dump the first four bytes instead. Real sfnt files start 00010000,
    # "true" (74727565), "ttcf" (74746366) or "OTTO" (4f54544f); an HTML error
    # page starts "<" (3c).
    local magic
    magic=$(head -c 4 "$tmp_ttf" | od -An -tx1 | tr -d ' \n')
    case "$magic" in
      00010000|74727565|74746366|4f54544f) : ;;
      *)
        log "  ERROR: $url did not return a font file (first 4 bytes: $magic)."
        rm -f "$tmp_ttf"; ok=0; continue ;;
    esac
    mkdir -p "$fonts_dir/$family"
    mv "$tmp_ttf" "$fonts_dir/$family/${family}.ttf"
    log "  installed $family."
  done
  if [[ $ok -eq 0 ]]; then
    log "ERROR: one or more Hebrew fonts failed to install. Captions will render as boxes."
    log "       Install them manually into $fonts_dir and re-run 'fc-cache -f'."
    return 1
  fi

  log "Refreshing fontconfig cache."
  fc-cache -f "$fonts_dir"
}

main() {
  if check_already_installed; then
    log "Done. Verify: fc-list :lang=he | head"
    exit 0
  fi

  local os
  os=$(uname -s)
  case "$os" in
    Darwin)
      install_macos
      ;;
    Linux)
      if [ -f /etc/debian_version ]; then
        install_debian
      else
        log "ERROR: Linux distro is not Debian/Ubuntu. Install Heebo/Rubik/Assistant/Noto-Sans-Hebrew manually:"
        log "  1. Download from https://fonts.google.com/"
        log "  2. Copy .ttf files to ~/.local/share/fonts/ (user) or /usr/local/share/fonts/ (system)"
        log "  3. Run: fc-cache -f -v"
        exit 1
      fi
      ;;
    *)
      log "ERROR: Unsupported OS: $os. Install Hebrew fonts manually."
      exit 1
      ;;
  esac

  log "Verifying installation."
  if ! command -v fc-list >/dev/null 2>&1; then
    log "WARN: fc-list not on PATH. Cannot verify. libass may still find the fonts if they are in standard locations."
  else
    fc-list :lang=he | head -10
    local count
    count=$(fc-list :lang=he 2>/dev/null | wc -l | tr -d ' ')
    log "fontconfig reports $count Hebrew-capable font entries."
  fi
  log "Done."
}

main "$@"
