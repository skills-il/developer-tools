# macOS FFmpeg setup for Hebrew captions

video-use renders Hebrew captions via `libass`, which depends on `--enable-libass` and `--enable-fontconfig` in FFmpeg's build configuration. On macOS, **Homebrew's default `ffmpeg` formula ships without either** as of 2026-05, so a fresh `brew install ffmpeg` produces an FFmpeg that cannot burn captions at all.

This is the most common silent failure for Hebrew video editing on macOS.

## Check whether your FFmpeg is usable

```bash
ffmpeg -version 2>&1 | grep -oE 'enable-(libass|fontconfig|libharfbuzz|libfreetype)' | sort -u
```

You need to see at least these four lines:

```
enable-fontconfig
enable-libass
enable-libfreetype
enable-libharfbuzz
```

If any of these are missing, captions will either error out (`No such filter: subtitles`) or render incorrectly (boxes, wrong font, no BiDi).

## Fix option A: Tessus static build (recommended, no recompile)

Tessus at evermeet.cx publishes static `ffmpeg` binaries built with the full feature set:

```bash
curl -L https://evermeet.cx/ffmpeg/getrelease/zip -o /tmp/ff.zip
unzip /tmp/ff.zip -d /tmp/
chmod +x /tmp/ffmpeg
/tmp/ffmpeg -version | head -1   # verify
```

The static binary at `/tmp/ffmpeg` has libass, fontconfig, libfreetype, libharfbuzz, x264, x265, aom, and dozens of other codecs. No dynamic linking, no dependency hell.

Use it explicitly when invoking video-use's helpers or `burn-hebrew-captions.sh`:

```bash
PATH=/tmp:$PATH python3 helpers/render.py edl.json -o final.mp4
# OR
scripts/burn-hebrew-captions.sh --ffmpeg /tmp/ffmpeg --base base.mp4 --srt master.srt --out final.mp4
```

For a permanent install, move it to a stable location:

```bash
sudo mv /tmp/ffmpeg /usr/local/bin/ffmpeg-static
ln -sf /usr/local/bin/ffmpeg-static /usr/local/bin/ffmpeg
```

## Fix option B: Third-party Homebrew tap

Homebrew removed feature flags from the main `ffmpeg` formula years ago (no `brew install ffmpeg --with-libass`). The `homebrew-ffmpeg/ffmpeg` tap re-introduces them:

```bash
brew tap homebrew-ffmpeg/ffmpeg
brew install homebrew-ffmpeg/ffmpeg/ffmpeg --with-libass --with-fontconfig --with-libharfbuzz
```

This installs to `/opt/homebrew/bin/ffmpeg` (Apple Silicon) or `/usr/local/bin/ffmpeg` (Intel) and shadows the default formula. Slower to install than option A (compiles from source), but the binary is dynamically linked and updates with Homebrew's normal cadence.

## Known gotchas after install

Even with a properly-built ffmpeg:

1. **`drawtext` may still be missing** in some static builds (no `libfreetype` at runtime even when configured). If you need text overlays outside of subtitles (e.g., CTA freeze frames), test with `ffmpeg -h filter=drawtext`. If unavailable, use the PIL approach the `cta_freeze.mp4` builder uses.

2. **`loudnorm` fails on silent segments.** If your edit ends with a freeze frame that has no audio (or has dead air longer than ~1.5s), `loudnorm` returns `I=-inf` and aborts. Workarounds: (a) layer 2 seconds of room tone over the freeze before rendering, (b) skip loudnorm with `--no-loudnorm`, (c) split into pre-freeze and freeze segments and concat after loudnorm runs only on the speech portion.

3. **libass + SRT BiDi is unreliable on macOS** even with proper libass build. The cause is opaque (some combination of libfribidi linkage, libass version, and how the SRT-to-libass-internal-event conversion handles direction). The reliable fix is to pre-shape the Hebrew text with `python-bidi` (`get_display()`) before rendering, so libass receives display-order characters and just draws them LTR , which it does correctly. The bundled `scripts/burn-hebrew-captions.sh` does this automatically.

4. **`fontsdir=` parameter is more reliable than fontconfig.** Even when `fc-match Heebo` finds your installed Heebo, the `subtitles` filter sometimes ignores fontconfig and falls back to libass's built-in font. Passing `subtitles=master.ass:fontsdir=$HOME/Library/Fonts` forces libass to look in the explicit directory first.

## What this skill assumes

Throughout SKILL.md and the bundled scripts, when we say "ffmpeg" we assume one of options A, B, or C above. If you are on a stock Homebrew ffmpeg without libass, you will see misleading errors (e.g., "subtitles filter not found" or boxes-in-final-output with no error at all). Fix the install before debugging caption rendering.
