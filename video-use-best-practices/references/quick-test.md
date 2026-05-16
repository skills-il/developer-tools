# Quick test recipe

A 10-second synthetic Hebrew test clip you can use to validate `captions-only.sh` end-to-end without burning real footage against your ElevenLabs quota.

## macOS (uses built-in `say` + Carmit Hebrew voice)

```bash
# 1. Generate Hebrew speech audio
say -v Carmit -o /tmp/test-he.aiff "שלום, זאת בדיקה של מערכת הכתוביות בעברית. אם אתה רואה את הטקסט הזה, הכל עובד."

# 2. Combine with a solid color video track
ffmpeg -y -f lavfi -i color=c=#1a1a2e:s=1280x720:d=10 -i /tmp/test-he.aiff \
  -c:v libx264 -preset ultrafast -c:a aac -shortest /tmp/test-he.mp4

# 3. Run the full pipeline
bash scripts/captions-only.sh /tmp/test-he.mp4 --yes --ffmpeg /tmp/ffmpeg
```

Expected: `/tmp/test-he.captioned.mp4` with Hebrew captions burned in over the dark background. Cost: ~$0.001 in Scribe (10 seconds of audio).

## Linux (uses espeak-ng if available, or download a CC-licensed Hebrew sample)

```bash
# Option A: espeak-ng (low quality but works for pipeline validation)
espeak-ng -v he "שלום, זאת בדיקה של הכתוביות" -w /tmp/test-he.wav
ffmpeg -y -f lavfi -i color=c=#1a1a2e:s=1280x720:d=10 -i /tmp/test-he.wav \
  -c:v libx264 -preset ultrafast -c:a aac -shortest /tmp/test-he.mp4

# Option B: any Hebrew CC-BY video clip from Wikimedia Commons works
```

## What success looks like

After running the pipeline you should see:
1. Console: `Detected 0 gap(s). Transcript covers the full video.` (no recovery needed on a 10s clip)
2. Console: `Stripped sentence-end punctuation (. ? !) from N Hebrew line(s) for clean caption display.`
3. File: `/tmp/test-he.captioned.mp4` exists and is ~1-2MB
4. File: `/tmp/test-he.captioned.he.srt` exists with 1-3 cues of Hebrew text
5. Frame check: open the MP4 at t=5s and the caption should show "שלום זאת בדיקה" (or similar) with Hebrew chars in source byte order LTR within each word, no period at the end of the line

If any of those fail, see Troubleshooting in the main SKILL.md.

## Why use this instead of real footage

The ElevenLabs free tier is 10,000 characters/month. A 10-minute Hebrew talking-head burns ~7-8K characters, so one real-video test eats nearly the whole month. A 10-second synthetic clip transcribes to ~30 characters, ~0.3% of the monthly quota. Use this for pipeline-correctness validation; save the real-footage quota for production runs.
