# macOS FFmpeg setup for Hebrew captions

video-use renders Hebrew captions via `libass`, which FFmpeg only gets when it is built with `--enable-libass`. On macOS, **Homebrew's default `ffmpeg` formula ships without it**: re-checked 2026-11-11 on the core `ffmpeg` 9.0.2 bottle, whose filter list has no `subtitles`, `ass` or `drawtext`. A fresh `brew install ffmpeg` therefore cannot burn captions at all.

This is the most common silent failure for Hebrew video editing on macOS.

## Check whether your FFmpeg is usable

Test for the filter, not for configure flags. Builds spell the fontconfig flag differently (`--enable-libfontconfig` in Homebrew's `ffmpeg-full`, `--enable-fontconfig` in some static builds), so a grep for one spelling gives false alarms.

```bash
ffmpeg -hide_banner -filters 2>/dev/null | grep -E ' (subtitles|ass) '
```

Two lines (`ass` and `subtitles`) means libass is in. No output means captions will either error out or never render.

## Fix option A: Homebrew `ffmpeg-full` (recommended)

Homebrew core carries a second, bottled formula, `ffmpeg-full`, that depends on libass, fontconfig, freetype and harfbuzz. It is keg-only, so it does not replace or shadow the default `ffmpeg`:

```bash
brew install ffmpeg-full
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -hide_banner -filters | grep ' subtitles '
```

Point the scripts at it explicitly (Intel Macs use `/usr/local/opt/ffmpeg-full/bin/ffmpeg`):

```bash
scripts/burn-hebrew-captions.sh --ffmpeg /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg \
  --base base.mp4 --srt master.srt --out final.mp4
# For video-use's own helpers, put it first on PATH for that one command:
PATH="/opt/homebrew/opt/ffmpeg-full/bin:$PATH" python3 helpers/render.py edl.json -o final.mp4
```

Installing it can upgrade shared libraries that the default `ffmpeg` links against. If `ffmpeg` then fails with `Library not loaded`, run `brew upgrade ffmpeg` to bring it in line.

## Fix option B: Third-party Homebrew tap

The `homebrew-ffmpeg/ffmpeg` tap builds FFmpeg with libass and fontconfig included:

```bash
brew tap homebrew-ffmpeg/ffmpeg
brew install homebrew-ffmpeg/ffmpeg/ffmpeg
```

This replaces the default formula's `ffmpeg` on PATH. Slower to install than option A (it compiles from source).

## Known gotchas after install

Even with a properly-built ffmpeg:

1. **`drawtext` may still be missing** in some static builds (no `libfreetype` at runtime even when configured). If you need text overlays outside of subtitles (e.g., CTA freeze frames), test with `ffmpeg -h filter=drawtext`. If unavailable, render the overlay with PIL (`layout_engine=ImageFont.Layout.RAQM` for Hebrew) and composite it with ffmpeg's `overlay` filter.

2. **libass + SRT BiDi is unreliable on macOS** even with proper libass build. The cause is opaque (some combination of libfribidi linkage, libass version, and how the SRT-to-libass-internal-event conversion handles direction). The reliable fix is to pre-shape the Hebrew text with `python-bidi` (`get_display(line, base_dir='R')`) before rendering, so libass receives display-order characters and just draws them LTR , which it does correctly. The bundled `scripts/burn-hebrew-captions.sh` does this automatically.

`base_dir='R'` is not optional. Without it python-bidi infers paragraph direction from the first strong character, so a caption beginning with a Latin token is treated as LTR and comes out in reversed word order.

**The `subtitles` filter's `shaping` option does not substitute for the pre-shape.** FFmpeg documents `shaping=complex` as "Required for correct rendering of complex scripts such as Arabic, Hebrew, Devanagari and Thai", which makes it look like the supported fix. It is not: shaping is glyph substitution and positioning, not bidirectional reordering. Tested 2026-08-26 on a HarfBuzz-enabled static build, `shaping=auto` and `shaping=complex` produced byte-identical frames, and an un-pre-shaped Hebrew line still rendered in source byte order under both.

3. **`fontsdir=` parameter is more reliable than fontconfig.** Even when `fc-match Heebo` finds your installed Heebo, the `subtitles` filter sometimes ignores fontconfig and falls back to libass's built-in font. Passing `subtitles=master.ass:fontsdir=$HOME/Library/Fonts` gives libass an explicit directory to search. FFmpeg documents `fontsdir` as additive rather than as a precedence override: "These fonts will be used **in addition to** whatever the font provider uses." In practice it is what makes Heebo resolve reliably, but it does not guarantee priority over fontconfig, so keep the font correctly installed as well.

## What this skill assumes

Throughout SKILL.md and the bundled scripts, when we say "ffmpeg" we assume option A or option B above. If you are on a stock Homebrew ffmpeg without libass, you will see misleading errors (e.g., "subtitles filter not found" or boxes-in-final-output with no error at all). Fix the install before debugging caption rendering.
