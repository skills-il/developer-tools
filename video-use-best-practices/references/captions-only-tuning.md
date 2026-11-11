# captions-only.sh tuning reference

Constants you can edit in `scripts/captions-only.sh` to change behavior. `GAP_THRESHOLD` and `TAIL_THRESHOLD` are shell variables in the Step 1.5 block; `MAX_WORD_DUR` and `MAX_DISPLAY_SEC` live inside the Step 2 Python heredoc, mid-file, not at the top. All defaults are conservative for a typical Hebrew talking-head / lecture / podcast video.

## Thresholds

| Constant | Default | What it controls | When to change |
|---|---|---|---|
| `MAX_WORD_DUR` | `2.0`s | Single-word duration cap | Scribe occasionally emits a single "word" with an 80s duration (Scribe bug, usually on a stuttered or hummed syllable). Without clipping, that one cue freezes on screen for 80s. Raise to 5-10s if your source has legitimately long-held vocals or names; lower to 1.5s for fast speech. |
| `GAP_THRESHOLD` | `30`s | Mid-file silence width that triggers gap recovery | Scribe sometimes silently drops 30s-2min of speech in long Hebrew files. A gap wider than this between two consecutive transcribed words triggers an isolated re-transcribe of that window with `scribe_v2`. Lower (e.g. 20s) = more aggressive recovery + more re-transcribe cost. Raise (e.g. 60s) for talks with long deliberate pauses or Q&A sections where silence is real. |
| `TAIL_THRESHOLD` | `10`s | Untranscribed tail width that triggers tail recovery | If the last transcribed word ends more than this before the video duration, treat the tail as a dropped chunk and re-transcribe it. Set to a high number (e.g. 600) to disable tail recovery if your source genuinely ends in silence (closing music, credits). |
| `MAX_DISPLAY_SEC` | `7.0`s | Per-cue display cap | Prevents a single cue from lingering after speech ends. Raise to 10s for slower readers or accessibility audiences; lower to 5s for tighter visual rhythm. |

## Scribe model

**There is no longer a choice.** ElevenLabs deprecated `scribe_v1` and announced its removal for 9 July 2026; its models page lists it under Deprecated models with `scribe_v2` as the replacement. Both the main pass and each gap-recovery call send `scribe_v2`.

Earlier versions of this file recommended `scribe_v1` for the main pass. Do not restore that. If a future cycle sees a v1/v2 split anywhere in this skill, it is stale: check https://elevenlabs.io/docs/api-reference/speech-to-text/convert for the current `model_id` enum before restoring it.

Scribe v2 is billed at $0.20 per hour of audio on the API rate card (see [pricing.md](pricing.md)). ElevenLabs now lists `scribe_v3` as its successor at the same price; switching `model_id` in `scribe_call()` is untested here, so verify a short clip first.

## Punctuation stripping (Step 0 of `burn-hebrew-captions.sh`)

By default, sentence-end `.` `?` `!` are stripped from any caption line containing Hebrew before the python-bidi pre-shape step. This is the BBC/Netflix caption style guide recommendation: line breaks and timing already signal end-of-thought, so punctuation adds visual noise without information.

The implementation reason matters too: the python-bidi + libass double-reversal recipe is BiDi-stable for letters but punctuation positioning becomes unpredictable depending on script mix (pure Hebrew lines vs Hebrew + English-token lines render the period in different positions). Stripping ends that whole class of failure modes.

**To keep punctuation**, comment out the `SENTENCE_END` block inside the Step 0 Python heredoc in `scripts/burn-hebrew-captions.sh`. Characters and words stay correct either way; you may see the period drift left/right depending on the line.

## Side outputs

Every successful run writes two artifacts:

- `<output>.mp4` , the burned-in captioned video.
- `<output>.he.srt` , the merged final SRT (post-Scribe-recovery, post-chunking, pre-burn). Upload this as a sidecar caption track to YouTube/Vimeo when you want the captions as user-toggleable text instead of burned pixels. 

There is no transcript cache. Every run calls Scribe again and is billed again; to fix captions without re-transcribing, edit `<output>.he.srt` and burn it with `burn-hebrew-captions.sh --srt`.

## Flags

| Flag | Effect |
|---|---|
| `--strip-fillers` | Remove ALWAYS-FILLER Hebrew tokens from caption text. Audio is untouched. The set is exactly `אֶה, אה, אֶמ, אממ, אמממ, אהמ, המ, ממ` (see `hebrew-filler-words.md`). **`אם` is deliberately NOT in it**, it means "if/whether" and auto-cutting it silently changes meaning; `וואלה` is context-dependent and is not auto-cut either. Do not add either one back. |
| `--yes` | Skip the cost-confirmation prompt. Without a terminal (an agent's shell, CI) and without `--yes`, the script prints the estimate and exits with code 3 before sending anything; show the user the estimate and re-run with `--yes` once they agree. |
| `--output PATH` | Override the default `<input>.captioned.<ext>` output path. |
| `--ffmpeg PATH` | Override the `ffmpeg` binary, e.g. `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` on macOS, where the default Homebrew ffmpeg has no libass. |
| `--audio-track N` | Zero-based audio stream to transcribe (default 0). OBS recordings often carry the mic on track 1. A silent track is refused before upload. |
| `--max-gap-calls N` | Cap on extra billed gap-recovery calls (default 10). Gaps beyond the cap stay uncaptioned and are logged. |
| `--font NAME`, `--fontsdir PATH` | Caption font (only Heebo is accepted: line widths are measured on it) and the font directory passed to libass. |
| `--font-size N`, `--margin-v N` | Absolute pixels. Default `auto` lets `burn-hebrew-captions.sh` scale both from the frame height. |
| `--keep-work` | Keep the temp work directory (Scribe JSON, extracted audio) for debugging. |

## Uploading the side-export SRT to YouTube/Vimeo

The `<output>.he.srt` written alongside the MP4 is a standard SRT in source-byte order (NOT the pre-shaped form fed to libass). Suitable for sidecar caption upload to any platform that consumes SRT.

- **YouTube**: Studio > select video > Subtitles > Add language > Hebrew > Upload file > pick the `.he.srt`. Choose "With timing" since the file has timestamps.
- **Vimeo**: video Settings > Distribution > Subtitles > Add new file > Language: Hebrew > Upload.
- **Self-hosted / Plyr / Video.js**: browsers' `<track>` element needs WebVTT, not SRT. Convert first (`ffmpeg -i x.he.srt x.he.vtt`), then reference the `.vtt` as `<track kind="captions" srclang="he" src="...">` inside the `<video>` element.

The advantage over burned-in pixels: users can toggle captions off, accessibility tools can read them, and search engines can index the text.
