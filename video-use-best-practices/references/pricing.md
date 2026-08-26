# Pricing (video-use Hebrew workflows)

Verified against https://elevenlabs.io/pricing and https://elevenlabs.io/pricing/api on 2026-08-26.

video-use is free; underlying services are paid. Mode determines cost.

| Mode | What | Best for | Cost / 1hr video |
|------|------|----------|------------------|
| **A. Captions-only** (`scripts/captions-only.sh`) | Transcribe + burn Hebrew captions on original. No cuts. | Lectures, webinars, podcast videos. | **~$1-3 total** |
| **B. Full cut** (default video-use flow) | Inventory → strategy → cut → render → self-eval. | Teaser from raw footage; multi-take selection. | **~$25-60** (1hr); **$120-300** (3hr). Scales super-linearly. |

Per-unit: Scribe v2 is **$0.22 per hour** of audio on the API rate card (Scribe v2 Realtime is $0.39). `scribe_v1` was removed on 9 July 2026, so `scribe_v2` is the only model the scripts may send. Claude tokens depend on mode. Local FFmpeg/libass rendering is $0.

**Two rate cards, do not mix them.** $0.22/hr is the pay-as-you-go **API** rate. On a subscription you spend **credits**: STT bills ~330 credits/minute, so an hour of audio is 19,800 credits, two thirds of Starter's 30,000. Dollar figures here assume the API rate; the free-tier warning below assumes credits.

**Free-tier reality check (the "$1-3" assumes the API rate; Starter is $6/mo for 30,000 credits).** ElevenLabs free tier is **10,000 credits/month**, and Speech-to-Text bills ~330 credits/minute (the per-character figure is for text-to-speech, not STT), so it covers only **~30 minutes of transcription/month**. A 10-minute Hebrew talking-head uses ~3,300 credits; gap-recovery (Step 8) re-transcribes dropped windows, counting again. So free tier yields **two or three short videos/month** before the quota wall. Warn non-technical users upfront.

**Validated test (May 2026, 11:29 source → 75s teaser via Full cut):** Scribe $0.08 + Claude $9.50 = **~$9.60 first pass**, ~$1-3 per iteration.

**Pick the cheap one if unsure.** Captions-only is 20-100x cheaper than Full cut for long videos and produces the same caption quality. If you decide to cut later, the Scribe transcript is already cached.

**Pricing trap:** `no_verbatim=true` on Scribe sounds like it saves money by dropping fillers but is destructive (agent loses the ability to make per-instance keep/cut decisions, usually leads to a re-transcription). Keep `no_verbatim=false` (default) and run the Hebrew lexicon post-pass instead.

**Offline fallback (no Scribe budget):** Whisper Large v3 transcribes Hebrew locally for free. WER is ~33% for Whisper Large v3 (32.9% on FLEURS in ElevenLabs' own Hebrew benchmark table, where Scribe v1 is listed at 15.2%). ElevenLabs' current Hebrew page headline claims a 3.1% Hebrew WER on FLEURS for Scribe without naming a version, so treat 15.2% as the last version-attributed figure and 3.1% as the current marketing one. Either way, local Whisper captions are noticeably less accurate, but the fallback works when ElevenLabs is unavailable or you want zero cost.

**Burn-in only. Never route a Whisper transcript into the Mode B cut workflow**, because upstream's anti-patterns forbid phrase-level SRT ("loses sub-second gap data, always word-level verbatim") and `--output_format srt` destroys the word timestamps the filler post-pass and Hard Rules 5 and 6 need. Use `--word_timestamps True --output_format json`, derive the SRT yourself, feed that to `burn-hebrew-captions.sh`, and skip `captions-only.sh`.

## Rate-card cheat sheet

| Item | Value | Source |
|---|---|---|
| Scribe v2, API pay-as-you-go | $0.22 per hour of audio | elevenlabs.io/pricing/api |
| Scribe v2 Realtime, API | $0.39 per hour of audio | elevenlabs.io/pricing/api |
| Speech-to-text, credit rate | ~330 credits per minute (19,800/hour) | elevenlabs.io/pricing |
| Free plan | $0, 10,000 credits/month (~30 min of STT) | elevenlabs.io/pricing |
| Starter | $6/month, 30,000 credits | elevenlabs.io/pricing |
| Creator | $22/month, 121,000 credits | elevenlabs.io/pricing |
| `scribe_v1` | Removed 9 July 2026. Migrate to `scribe_v2` or `scribe_v2_realtime`. | elevenlabs.io/docs/changelog/2026/6/8 |

Re-check this page whenever a cycle touches cost text. ElevenLabs has changed Scribe pricing twice in 2026.
