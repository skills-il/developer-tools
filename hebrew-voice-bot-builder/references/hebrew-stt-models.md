# Hebrew Speech-to-Text Models Comparison

Comparison of STT providers for Hebrew voice applications, with accuracy benchmarks, latency, pricing, and use case recommendations.

## Model Comparison

| Feature | OpenAI Whisper | Google Cloud STT | Azure Speech Services |
|---------|---------------|-------------------|----------------------|
| Hebrew Language Code | `he` | `he-IL` | `he-IL` |
| Best Model | whisper-1 | phone_call / latest_long | Standard |
| Accuracy (clean audio) | 92-95% | 88-92% | 87-91% |
| Accuracy (phone audio) | 88-92% | 85-90% | 84-89% |
| Accuracy (noisy) | 80-85% | 75-80% | 74-79% |
| Mixed Hebrew-English | Excellent | Good | Good |
| Streaming Support | No (batch only) | Yes | Yes |
| Real-time Factor | ~0.3x (batch) | ~1x (streaming) | ~1x (streaming) |
| Custom Vocabulary | Via prompt hint | Phrase hints | Custom Speech models |
| Speaker Diarization | No | Yes | Yes |
| Word Timestamps | Yes | Yes | Yes |
| Punctuation | Auto (good) | Auto (good) | Auto (moderate) |
| Max Audio Length | 25MB file | 480 min (async) | 10 min (sync), unlimited (batch) |

## Pricing (as of 2026)

| Provider | Model | Price per Minute | Notes |
|----------|-------|-----------------|-------|
| OpenAI Whisper | whisper-1 | ~$0.006/min | Batch only, no streaming |
| Google Cloud STT | Standard | $0.006/15s ($0.024/min) | First 60 min/month free |
| Google Cloud STT | Enhanced / phone_call | $0.009/15s ($0.036/min) | Higher accuracy for phone |
| Azure Speech | Standard | $1.00/hr ($0.0167/min) | First 5 hours/month free |
| Azure Speech | Custom | $1.40/hr ($0.0233/min) | Custom model training extra |

**Note:** Prices may vary. Check each provider's current pricing page for the latest rates.

## Hebrew-Specific Accuracy Notes

### Whisper Strengths
- Best at handling Hebrew without niqqud (standard modern Hebrew text)
- Excellent code-switching detection (Hebrew-English transitions)
- Handles diverse accents well due to multilingual training data
- Good at transcribing Hebrew numbers and dates
- Recognizes common Hebrew abbreviations and acronyms

### Whisper Weaknesses
- Batch-only processing (no real-time streaming)
- Can occasionally hallucinate content for very short or silent audio segments
- No custom vocabulary training (only prompt-based hints)
- File size limit of 25MB requires splitting long recordings

### Google Cloud STT Strengths
- Real-time streaming support (essential for live voice bots)
- Phone call model (optimized for 8kHz telephony audio)
- Phrase hints for domain-specific Hebrew terms
- Speaker diarization for multi-speaker scenarios
- Robust silence detection and endpoint detection

### Google Cloud STT Weaknesses
- Slightly lower accuracy than Whisper for Hebrew
- Mixed Hebrew-English handling less robust than Whisper
- Phrase hints limited to 5,000 entries
- Hebrew punctuation sometimes inconsistent

### Azure Speech Strengths
- Custom Speech models allow training on domain-specific Hebrew data
- Enterprise features (private endpoints, compliance certifications)
- Good integration with Azure ecosystem
- Pronunciation assessment capability
- Continuous recognition for long-form audio

### Azure Speech Weaknesses
- Lowest baseline Hebrew accuracy of the three
- Custom model training requires significant labeled data
- Closest region to Israel is West Europe (adds latency vs Middle East regions)
- Hebrew voice list more limited than English

## Recommendations by Use Case

| Use Case | Recommended Provider | Why |
|----------|---------------------|-----|
| Voicemail transcription (batch) | OpenAI Whisper | Best accuracy, cost-effective for batch |
| Live IVR voice bot | Google Cloud STT | Streaming support, phone_call model |
| Enterprise call center | Azure Speech | Custom models, compliance, enterprise support |
| Mixed Hebrew-English tech calls | OpenAI Whisper | Superior code-switching detection |
| High-volume transcription | Google Cloud STT | Free tier + competitive pricing at scale |
| Domain-specific (medical, legal) | Azure Speech (custom) | Custom model training for specialized vocab |
| Prototype / MVP | OpenAI Whisper | Simplest API, best out-of-box accuracy |

## Audio Format Recommendations

| Scenario | Format | Sample Rate | Channels | Notes |
|----------|--------|-------------|----------|-------|
| Phone calls (Twilio) | MULAW | 8000 Hz | Mono | Standard telephony format |
| VoIP calls | PCM/WAV | 16000 Hz | Mono | Better quality than MULAW |
| Pre-recorded audio | WAV/FLAC | 16000+ Hz | Mono | Lossless preferred |
| Whisper upload | MP3/WAV/FLAC | 16000+ Hz | Mono | Max 25MB file size |
| Streaming (Google) | LINEAR16 | 16000 Hz | Mono | Raw PCM for streaming |

## Hebrew-Specific Configuration Tips

### Whisper
```python
# Best settings for Hebrew
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="he",                    # Prevent Arabic misdetection
    prompt="שלום, ברוכים הבאים",      # Hebrew prompt hint
    response_format="verbose_json",   # Get timestamps and confidence
)
```

### Google Cloud STT
```python
# Best settings for Hebrew phone calls
config = speech_v1.RecognitionConfig(
    encoding=speech_v1.RecognitionConfig.AudioEncoding.MULAW,
    sample_rate_hertz=8000,
    language_code="he-IL",
    model="phone_call",
    enable_automatic_punctuation=True,
    speech_contexts=[
        speech_v1.SpeechContext(
            phrases=["שלום", "הזמנה", "תלונה", "נציג"],
            boost=10.0,
        )
    ],
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
