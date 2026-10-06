# Hebrew Speech-to-Text Models Comparison

Comparison of STT providers for Hebrew voice applications, with accuracy benchmarks, latency, pricing, and use case recommendations.

## Model Comparison

| Feature | OpenAI Whisper | Google Cloud STT | Azure Speech Services |
|---------|---------------|-------------------|----------------------|
| Hebrew Language Code | `he` (`languages=["he"]` on gpt-transcribe) | `iw-IL` | `he-IL` |
| Best Model | gpt-transcribe (files) / gpt-live-transcribe (streaming). whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe and gpt-4o-transcribe-diarize shut down 2027-02-26 | chirp_2 / chirp_3 (Hebrew is Chirp-only; there is no phone_call or telephony model for iw-IL) | Standard |
| Accuracy (clean audio) | see note below | see note below | see note below |
| Accuracy (phone audio) | see note below | see note below | see note below |
| Accuracy (noisy) | see note below | see note below | see note below |
| Mixed Hebrew-English | All three document multilingual handling; none publishes a code-switching benchmark. Measure it. | | |
| Streaming Support | Yes via gpt-live-transcribe in Realtime transcription sessions (not supported on `v1/audio/transcriptions`) | Yes, but for Hebrew only on chirp_3 (Preview) | Yes |
| Custom Vocabulary | `prompt` plus `keywords` (gpt-transcribe) | Phrase hints | Custom Speech models |
| Speaker Diarization | gpt-4o-transcribe-diarize only, which shuts down 2027-02-26 | Not for Hebrew: no iw-IL row lists speaker diarization | Yes |
| Word Timestamps | whisper-1 only (shuts down 2027-02-26) | Yes | Yes |
| Punctuation | Auto (good) | Auto (good) | Auto (moderate) |

### A note on accuracy

Earlier versions of this table carried per-provider Hebrew accuracy percentages
for clean, phone and noisy audio. Those numbers had no source behind them and
have been removed rather than re-cited: none of these three vendors publishes a
Hebrew word error rate broken down by phone, noise or accent condition (ElevenLabs,
not in this table, publishes a single Hebrew WER band for Scribe v2), and the Whisper paper reports Hebrew only as
part of its multilingual evaluation, not as a per-condition breakdown.

Treat provider choice as something to measure on your own audio. A short
benchmark on 20-30 real recordings from the line you are actually deploying to
will tell you more than any published figure, because Hebrew WER moves sharply
with telephony codec, speaker accent and the amount of English mixed in.

What can be said from the vendor documentation is structural rather than
numeric, and the rest of this table covers it: OpenAI streams through the Realtime
API rather than the file-upload endpoint, Google streams Hebrew only on chirp_3 at
Preview maturity, Azure streams, and OpenAI's diarization model
(gpt-4o-transcribe-diarize) is on the 2027-02-26 shutdown list, while Google does
not list diarization for any Hebrew row.

## Pricing (as of 2026)

| Provider | Model | Price per Minute | Notes |
|----------|-------|-----------------|-------|
| OpenAI | gpt-transcribe | $0.0045/min | Recommended file model; whisper-1 is deprecated |
| Google Cloud STT | chirp (V2 only) | See Google's pricing page | Google bills chirp under its Standard models; volume tiers apply |
| Azure Speech | Standard / Custom | See Azure's pricing page | Prices render client-side; read them in a browser |

**Note:** Prices may vary. Check each provider's current pricing page for the latest rates.

## Hebrew-Specific Accuracy Notes

### Whisper Strengths
- Handles Hebrew written without niqqud, which is standard modern Hebrew text
- Handles code-switching between Hebrew and English in the same utterance (Hebrew-English transitions)
- Trained on multilingual data covering a range of accents due to multilingual training data
- Transcribes Hebrew numbers and dates
- Recognizes common Hebrew abbreviations and acronyms

### Whisper Weaknesses
- The file-upload transcription endpoint is batch-only; streaming comes from gpt-live-transcribe in Realtime transcription sessions, a separate product
- Can occasionally hallucinate content for very short or silent audio segments
- No custom model training (vocabulary help is `prompt` and, on gpt-transcribe, `keywords`)
- File size limit of 25MB requires splitting long recordings

### Google Cloud STT Strengths
- Real-time streaming support (essential for live voice bots)
- Streaming recognition with interim results, but for Hebrew only on chirp_3 (eu/us, Preview); chirp_2 streaming does not list Hebrew. There is NO Hebrew phone_call or telephony model, so expect no phone-audio-tuned gain
- Phrase hints for domain-specific Hebrew terms
- Speaker diarization for multi-speaker scenarios, but NOT for Hebrew: no iw-IL row lists it
- Robust silence detection and endpoint detection

### Google Cloud STT Weaknesses
- Relative Hebrew accuracy versus Whisper is not published by either vendor; benchmark on your own call audio rather than trusting a ranking
- Code-switching behaviour between Hebrew and English is not benchmarked by the vendor; test it on your own mixed-language utterances
- Hebrew punctuation sometimes inconsistent

### Azure Speech Strengths
- Custom Speech models allow training on domain-specific Hebrew data
- Enterprise features (private endpoints, compliance certifications)
- Good integration with Azure ecosystem
- Pronunciation assessment capability
- Continuous recognition for long-form audio

### Azure Speech Weaknesses
- Baseline Hebrew accuracy versus the other two is not published by any vendor; benchmark it yourself
- Custom model training requires significant labeled data
- No Israel region for Speech; `uaenorth` and `qatarcentral` are geographically closer than `westeurope`, which keeps data in the EU
- Hebrew voice list more limited than English

## Recommendations by Use Case

| Use Case | Recommended Provider | Why |
|----------|---------------------|-----|
| Voicemail transcription (batch) | OpenAI gpt-transcribe | Simplest to set up, cost-effective for batch |
| Live IVR voice bot | Google Cloud STT V2 (chirp_3, eu/us) or OpenAI Realtime | Hebrew streaming is documented on chirp_3 only, at Preview maturity; chirp_2 does not list Hebrew for StreamingRecognize |
| Enterprise call center | Azure Speech | Custom models, compliance, enterprise support |
| Mixed Hebrew-English tech calls | OpenAI | Documents code-switching handling; verify on your own audio |
| High-volume transcription | Google Cloud STT | Free tier + competitive pricing at scale |
| Domain-specific (medical, legal) | Azure Speech (custom) | Custom model training for specialized vocab |
| Prototype / MVP | OpenAI | Simplest API, no cloud project or regional endpoint to configure |

## Audio Format Recommendations

| Scenario | Format | Sample Rate | Channels | Notes |
|----------|--------|-------------|----------|-------|
| Phone calls (Twilio) | MULAW | 8000 Hz | Mono | Standard telephony format |
| VoIP calls | PCM/WAV | 16000 Hz | Mono | Better quality than MULAW |
| Pre-recorded audio | WAV | 16000+ Hz | Mono | Lossless preferred. FLAC only if your target API accepts it |
| OpenAI upload | mp3/mp4/mpeg/mpga/m4a/wav/webm | 16000+ Hz | Mono | Max 25MB. FLAC and OGG are NOT accepted |
| Streaming (Google) | LINEAR16 | 16000 Hz | Mono | Raw PCM for streaming |

## Hebrew-Specific Configuration Tips

### Whisper
```python
# Recommended for Hebrew (gpt-transcribe takes `languages`, a list; it
# replaces the singular `language`; do not send both)
transcript = client.audio.transcriptions.create(
    model="gpt-transcribe",
    file=audio_file,
    prompt="שלום, ברוכים הבאים",      # Hebrew prompt hint
    extra_body={"languages": ["he"]},  # Prevent Arabic misdetection
)
# Timestamps: only whisper-1 supports timestamp_granularities, and it shuts
# down on 2027-02-26.
```

### Google Cloud STT
```python
# Hebrew on Google STT is Chirp-only, regional, and V2-only. Chirp 2 is documented
# as "exclusively available within the Speech-to-Text API V2", so a speech_v1 client
# asking for chirp_2 will not work, and the v1 encoding / speech_contexts fields do
# not exist on the v2 config. See SKILL.md Step 2 for the full working call.
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

# Batch / short Recognize for Hebrew: chirp_2 in europe-west4 or asia-southeast1.
# STREAMING Hebrew: chirp_3 in the eu or us multi-region (Preview). Hebrew is NOT
# on Chirp 2's StreamingRecognize language list.
LOCATION, MODEL = "europe-west4", "chirp_2"

client = SpeechClient(
    client_options=ClientOptions(api_endpoint=f"{LOCATION}-speech.googleapis.com")
)

config = cloud_speech.RecognitionConfig(
    auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
    language_codes=["iw-IL"],  # Google STT documents Hebrew as iw-IL, NOT he-IL
    model=MODEL,
)
```

### Azure Speech
```python
# Best settings for Hebrew
speech_config = speechsdk.SpeechConfig(
    subscription=key,
    region="westeurope",
)
speech_config.speech_recognition_language = "he-IL"
speech_config.set_property(
    speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs,
    "5000",
)
speech_config.set_property(
    speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
    "2000",
)
```
