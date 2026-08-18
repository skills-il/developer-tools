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

  for family_url in \
      "Heebo|https://fonts.google.com/download?family=Heebo" \
      "Rubik|https://fonts.google.com/download?family=Rubik" \
      "Assistant|https://fonts.google.com/download?family=Assistant"; do
    local family="${family_url%%|*}"
    local url="${family_url#*|}"
    if fc-list :lang=he 2>/dev/null | grep -qi "$family"; then
      log "  $family already present."
      continue
    fi
    log "  downloading $family..."
    local tmp_zip
    tmp_zip=$(mktemp -t "${family}.XXXXXX.zip")
    if curl -fsSL -o "$tmp_zip" "$url"; then
      unzip -qo "$tmp_zip" -d "$fonts_dir/$family" || log "  WARN: unzip failed for $family"
      rm -f "$tmp_zip"
    else
      log "  WARN: download failed for $family (Google Fonts may require an alternate URL). Skipping."
      rm -f "$tmp_zip"
    fi
  done

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
