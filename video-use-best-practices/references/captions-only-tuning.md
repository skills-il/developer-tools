# captions-only.sh tuning reference

Constants you can edit at the top of `scripts/captions-only.sh` to change behavior. All defaults are conservative for a typical Hebrew talking-head / lecture / podcast video.

## Thresholds

| Constant | Default | What it controls | When to change |
|---|---|---|---|
| `MAX_WORD_DUR` | `2.0`s | Single-word duration cap | Scribe occasionally emits a single "word" with an 80s duration (Scribe bug, usually on a stuttered or hummed syllable). Without clipping, that one cue freezes on screen for 80s. Raise to 5-10s if your source has legitimately long-held vocals or names; lower to 1.5s for fast speech. |
| `GAP_THRESHOLD` | `30`s | Mid-file silence width that triggers gap recovery | Scribe sometimes silently drops 30s-2min of speech in long Hebrew files. A gap wider than this between two consecutive transcribed words triggers an isolated re-transcribe of that window with `scribe_v2`. Lower (e.g. 20s) = more aggressive recovery + more re-transcribe cost. Raise (e.g. 60s) for talks with long deliberate pauses or Q&A sections where silence is real. |
| `TAIL_THRESHOLD` | `10`s | Untranscribed tail width that triggers tail recovery | If the last transcribed word ends more than this before the video duration, treat the tail as a dropped chunk and re-transcribe it. Set to a high number (e.g. 600) to disable tail recovery if your source genuinely ends in silence (closing music, credits). |
| `MAX_DISPLAY_SEC` | `7.0`s | Per-cue display cap | Prevents a single cue from lingering after speech ends. Raise to 10s for slower readers or accessibility audiences; lower to 5s for tighter visual rhythm. |

## Scribe v1 vs v2 choice

- **Full-video pass**: `scribe_v1`. More stable on long files, slightly cheaper, more conservative chunking.
- **Each gap-recovery call**: `scribe_v2`. Better at isolated short segments where the speaker context is missing (no preceding words to anchor the language model).

Both are billed per second; v2 is not more expensive per ElevenLabs' May 2026 pricing. Don't swap them around without testing , the failure modes differ.

## Punctuation stripping (Step 0 of `burn-hebrew-captions.sh`)

By default, sentence-end `.` `?` `!` are stripped from any caption line containing Hebrew before the python-bidi pre-shape step. This is the BBC/Netflix caption style guide recommendation: line breaks and timing already signal end-of-thought, so punctuation adds visual noise without information.

The implementation reason matters too: the python-bidi + libass double-reversal recipe is BiDi-stable for letters but punctuation positioning becomes unpredictable depending on script mix (pure Hebrew lines vs Hebrew + English-token lines render the period in different positions). Stripping ends that whole class of failure modes.

**To keep punctuation**, comment out the `SENTENCE_END` block inside the Step 0 Python heredoc in `scripts/burn-hebrew-captions.sh`. Characters and words stay correct either way; you may see the period drift left/right depending on the line.

## Side outputs

Every successful run writes two artifacts:

- `<output>.mp4` , the burned-in captioned video.
- `<output>.he.srt` , the merged final SRT (post-Scribe-recovery, post-chunking, pre-burn). Upload this as a sidecar caption track to YouTube/Vimeo when you want the captions as user-toggleable text instead of burned pixels. Distinct from the raw Scribe output (which is in the temp `WORKDIR`).

## Flags

| Flag | Effect |
|---|---|
| `--strip-fillers` | Remove ALWAYS-FILLER Hebrew tokens (אה, אהה, אם, וואלה when standalone, etc.) from caption text. Audio is untouched. |
| `--yes` | Skip the cost-confirmation prompt. Useful in CI / batch / scripted runs. |
| `--output PATH` | Override the default `<input>.captioned.<ext>` output path. |
| `--ffmpeg PATH` | Override the `ffmpeg` binary (e.g. `/tmp/ffmpeg` for the static evermeet build on macOS, where Homebrew ffmpeg often lacks libass). |

## Uploading the side-export SRT to YouTube/Vimeo

The `<output>.he.srt` written alongside the MP4 is a standard SRT in source-byte order (NOT the pre-shaped form fed to libass). Suitable for sidecar caption upload to any platform that consumes SRT.

- **YouTube**: Studio > select video > Subtitles > Add language > Hebrew > Upload file > pick the `.he.srt`. Choose "With timing" since the file has timestamps.
- **Vimeo**: video Settings > Distribution > Subtitles > Add new file > Language: Hebrew > Upload.
- **Self-hosted / Plyr / Video.js**: reference the `.he.srt` as a `<track kind="captions" srclang="he" src="...">` child of the `<video>` element.

The advantage over burned-in pixels: users can toggle captions off, accessibility tools can read them, and search engines can index the text.
