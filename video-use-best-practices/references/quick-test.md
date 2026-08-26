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
5. Frame check: open the MP4 at t=5s. The caption should show "שלום זאת בדיקה" (or similar) with **the pixel left-to-right order REVERSED relative to source byte order**: the first source word sits at the visual RIGHT, the last at the visual LEFT. No period at the end of the line.

   **Pixel order matching source byte order is the failure, not the success.** That is the exact symptom of BiDi not being applied, which is the bug this whole skill exists to work around (see SKILL.md Step 6). Earlier versions of this file described the failure as the acceptance criterion.

   If your test line starts with a Latin token, also confirm that token lands on the visual RIGHT. If it lands on the left, the pre-shape ran without `base_dir='R'`.

If any of those fail, see Troubleshooting in the main SKILL.md.

## Why use this instead of real footage

The ElevenLabs free tier is 10,000 credits/month, and Speech-to-Text costs ~330 credits per minute of audio (so roughly 30 minutes of transcription per month). A 10-minute Hebrew talking-head uses ~3,300 credits (about a third of the month). A 10-second synthetic clip costs ~55 credits, ~0.5% of the monthly quota. Use this for pipeline-correctness validation; save the real-footage quota for production runs.
