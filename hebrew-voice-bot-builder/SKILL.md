---
name: hebrew-voice-bot-builder
description: Build Hebrew voice bots and IVR (Interactive Voice Response) systems with speech-to-text, text-to-speech, and telephony integration for Israeli businesses. Use when user asks to "build a Hebrew voice bot", "create an IVR in Hebrew", "Hebrew speech-to-text", "binui bot koli b'ivrit", "maarechet maane koli", "zihui dibur b'ivrit", or "Twilio Israel". Covers OpenAI Whisper Hebrew, Google Cloud STT/TTS he-IL, Azure Speech Services, IVR menu design for Sunday-Thursday business hours, voicemail transcription, Hebrew accent handling, and +972 phone integration via Twilio and Vonage. Do NOT use for text-based chatbots (use hebrew-chatbot-builder), Hebrew NLP without voice (use hebrew-nlp-toolkit), or SMS messaging (use israeli-sms-gateway).
license: MIT
allowed-tools: Bash(python:*)
compatibility: Requires API keys for speech services (OpenAI, Google Cloud, Azure, or AWS). Requires Twilio or Vonage account for telephony. Works with Claude Code, Cursor, Windsurf.
---

# Hebrew Voice Bot Builder

Build production-ready Hebrew voice bots and IVR systems for Israeli businesses. This skill covers the full voice pipeline: speech-to-text (STT), text-to-speech (TTS), IVR flow design, telephony integration, and Hebrew-specific challenges like accent handling and mixed Hebrew-English speech.

## Instructions

> **Language code: Google STT uses `iw-IL`, Google TTS uses `he-IL`.** Google's
> Speech-to-Text supported-languages table lists Hebrew as `iw-IL` (the legacy
> ISO code for Hebrew), while the Text-to-Speech voice list uses `he-IL`
> (`he-IL-Wavenet-A`, `he-IL-Chirp3-HD-*`). Pass the documented code for each
> side rather than assuming one code works for both.

### Step 1: Choose Your Architecture

Before building, decide on the voice bot architecture based on the use case:

| Architecture | Best For | Components |
|-------------|----------|------------|
| IVR (keypad) | Simple menu navigation, payment lines, appointment scheduling | TTS + DTMF + telephony |
| Voice bot (conversational) | Customer service, order status, FAQ handling | STT + LLM + TTS + telephony |
| Voicemail transcription | Missed call handling, message routing | STT + notification pipeline |
| Hybrid | Complex flows with both speech and keypad input | STT + TTS + DTMF + telephony |

**Key decisions:**
- **STT provider**: OpenAI `gpt-transcribe` for recorded audio and `gpt-live-transcribe` for streaming (Realtime transcription sessions only, not the file endpoint). On 2026-08-26 OpenAI deprecated `whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe` and `gpt-4o-transcribe-diarize`, all shutting down on 2027-02-26, so do not start new work on them. `whisper-large-v3-turbo` for self-host, ivrit-ai's Hebrew-tuned variants (`ivrit-ai/whisper-large-v3-turbo-ct2`) for an open model trained specifically on Hebrew, Google Cloud STT (low latency; Hebrew runs on Chirp, `iw-IL`), Azure Speech (enterprise features), and ElevenLabs Scribe v2, which lists Hebrew (heb) in the "Good (>10% to <=20% WER)" band with a realtime variant at roughly 150ms. Note the WER band honestly: Hebrew is two tiers below English there, so benchmark on your own call audio rather than picking on the marketing claim.
- **TTS provider, split by use case**:
  - **Real-time / streaming (voice agents, IVR, live conversation)**: OpenAI Realtime API, native multilingual speech-to-speech including Hebrew over WebRTC/WebSocket/SIP, the 2026 default for sub-500ms turn-taking. The current GA model is `gpt-realtime-2.1` (`gpt-realtime-2.1-mini` for the smaller tier). Two model names to avoid: `gpt-realtime` was deprecated on 2026-07-20 with a hard shutdown on 2027-01-20 (replacement `gpt-realtime-2.1`), and `gpt-4o-realtime-preview` was removed from the API on 2026-05-07. `gpt-realtime-1.5` is still live. Other realtime options: ElevenLabs `eleven_v4_turbo` (~100ms, Hebrew is in the v4 language list; ElevenLabs now labels `eleven_v3_conversational` previous generation), Inworld `inworld-tts-2` and `inworld-tts-2-flash` (Hebrew `he` is listed as a Tier 1 language; the 1.5 models are deprecated), and the Israeli vendor Deepdub (API model id `dd-etts-3.0`, Hebrew `he-IL` in its API language table). Do NOT reach for ElevenLabs `eleven_flash_v2_5` for Hebrew: its language list is Multilingual v2's 29 languages plus Hungarian, Norwegian and Vietnamese, so Hebrew is absent entirely rather than merely weak.
  - **Offline / max quality (audiobooks, voicemail playback, batch generation)**: ElevenLabs `eleven_v4` (Hebrew is in its 90+ language list; `eleven_v3` is now previous generation). v3 and v4 are NOT on the Text to Speech `stream-input` WebSocket; v4 is served through the Text to Dialogue API, and their WebSocket route is the Text to Dialogue WebSocket (`wss://api.elevenlabs.io/v1/text-to-dialogue/stream-input`). Deepdub also serves this track with emotional control.
  - **Fallbacks**: Azure Neural TTS (`he-IL-HilaNeural`, `he-IL-AvriNeural`), Google Cloud TTS Wavenet (`he-IL-Wavenet-A/B`). **Amazon Polly does NOT support Hebrew** (no he-IL locale, no Hebrew voice of any engine, the "Avri" voice belongs to Azure, not Polly), so do not route Hebrew through Polly. ElevenLabs Multilingual v2 does NOT list Hebrew: its documented 29 languages are en, ja, zh, de, hi, fr, ko, pt, it, es, id, nl, tr, fil, pl, sv, bg, ro, ar, cs, el, fi, hr, ms, sk, da, ta, uk and ru. Hebrew appears in the Eleven v3 and v4 language lists, so route Hebrew to v4 or v3 (or to Azure/Google above) and not to Multilingual v2.
- **Telephony**: Twilio and Vonage both sell Israeli numbers. Twilio publishes Israeli voice pricing (local, mobile and toll-free tiers); Vonage does not publish comparable Israeli number documentation, so compare quotes yourself rather than trusting a ranking. Number portability exists in the Israeli market, but confirm with the carrier that your specific number can be ported to your chosen provider before committing.
- **Hosting**: Cloud functions for low-volume, dedicated servers for high-volume.
- **Call recording and voiceprints**: play a recording announcement (`השיחה מוקלטת`) at the start of the call. It is standard practice, not a cited statutory duty. The Wiretap Law ([חוק האזנת סתר](https://he.wikisource.org/wiki/חוק_האזנת_סתר)) defines "האזנת סתר" as "האזנה ללא הסכמה של אף אחד מבעלי השיחה". Treat a voiceprint as a different artifact from the recording: store it in its own table, keyed for per-caller deletion, so it can be erased independently of the audio and of the transcript. Have the operator confirm which obligations apply to their business with a qualified professional before launch.

### Step 2: Hebrew Speech-to-Text (STT)

#### OpenAI (recommended as the default)

OpenAI handles mixed Hebrew-English speech well, which is common in Israeli tech environments.

```python
import openai

client = openai.OpenAI()

def transcribe_hebrew(audio_file_path: str) -> str:
    """Transcribe Hebrew audio with gpt-transcribe."""
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-transcribe",
            file=audio_file,
            # gpt-transcribe takes `languages` (a list), NOT the singular
            # `language`; do not send both. extra_body is how the
            # official Python example passes it.
            extra_body={"languages": ["he"]},
        )
    return transcript.text


def transcribe_hebrew_with_timestamps(audio_file_path: str) -> dict:
    """Word-level timestamps. timestamp_granularities is supported ONLY on
    whisper-1, which shuts down on 2027-02-26: plan a replacement (for
    example ElevenLabs Scribe v2, which returns word-level timestamps)."""
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="he",
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )
    return transcript
```

**OpenAI Hebrew tips:**
- Pass Hebrew explicitly (`languages=["he"]` on gpt-transcribe, `language="he"` on whisper-1) to avoid misdetecting Hebrew as Arabic
- For mixed Hebrew-English on gpt-transcribe, pass both: `languages=["he", "en"]`, plus `keywords` for product names
- Whisper handles niqqud-free text well (standard for modern Hebrew)
- Audio quality matters: 16kHz+ sample rate, mono channel, WAV. Do NOT capture to FLAC or OGG if OpenAI is the target: its transcription API accepts only mp3, mp4, mpeg, mpga, m4a, wav and webm, and rejects the file after upload
- Maximum file size: 25MB. For longer recordings, split into segments

#### Google Cloud Speech-to-Text

Google's Hebrew STT runs on Chirp models only, regionally, through the V2 API.

```python
import os
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]

# Hebrew on Google STT is Chirp-only and REGIONAL, and Chirp 2 is documented as
# "exclusively available within the Speech-to-Text API V2". So Hebrew must go
# through speech_v2 against a regional endpoint, not the global speech_v1
# client. The supported-languages table lists iw-IL on: chirp and chirp_2 in
# europe-west4, asia-southeast1 and us-central1, and chirp_3 in the eu and us
# multi-regions.
# There is no phone_call or telephony model for Hebrew, so do not expect a
# phone-audio-tuned accuracy gain; benchmark on your own 8kHz call audio.
LOCATION = "europe-west4"
MODEL = "chirp_2"


def transcribe_hebrew_google(audio_content: bytes) -> str:
    """Transcribe Hebrew audio using Google Cloud STT V2 (Chirp)."""
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint=f"{LOCATION}-speech.googleapis.com",
        )
    )

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["iw-IL"],  # Google STT documents Hebrew as iw-IL, not he-IL
        model=MODEL,
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/_",
        config=config,
        content=audio_content,
    )

    response = client.recognize(request=request)
    return " ".join(
        result.alternatives[0].transcript for result in response.results
    )
```

**Streaming Hebrew needs a different model from the one above.** Chirp 2 enumerates the
languages its `Speech.StreamingRecognize` accepts, and Hebrew is NOT on that list (it
covers 16 locales: the Chinese, English, French, German, Italian, Japanese, Korean,
Portuguese and Spanish variants). Chirp 2's `Recognize` and `BatchRecognize` are fine for
Hebrew, which is what the code above uses. For STREAMING Hebrew use **`chirp_3` in the
`eu` or `us` multi-region**: Chirp 3 lists StreamingRecognize as Supported and its locale
table includes `Hebrew (Israel) iw-IL` at **Preview** maturity. Two consequences: set
`LOCATION = "us"` (or `"eu"`) and `MODEL = "chirp_3"` for the streaming path, and treat
Preview as Preview, meaning pin your behaviour with tests and have a fallback. If you do
not want a Preview dependency, run the call through short `Recognize` requests on
utterance boundaries, or use a provider whose Hebrew streaming you have tested (OpenAI
Realtime, or ElevenLabs Scribe v2 Realtime).

#### Azure Speech Services

Enterprise-grade with custom model training for domain-specific Hebrew vocabulary.

```python
import azure.cognitiveservices.speech as speechsdk

def transcribe_hebrew_azure(audio_file_path: str) -> str:
    """Transcribe Hebrew audio using Azure Speech Services."""
    speech_config = speechsdk.SpeechConfig(
        subscription="YOUR_AZURE_KEY",
        region="westeurope",  # EU; uaenorth or qatarcentral are closer, but outside the EU
    )
    speech_config.speech_recognition_language = "he-IL"

    audio_config = speechsdk.AudioConfig(filename=audio_file_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return ""
    else:
        raise RuntimeError(f"Speech recognition failed: {result.reason}")
```

Consult `references/hebrew-stt-models.md` for a comparison of STT providers.

### Step 3: Hebrew Text-to-Speech (TTS)

Normalize prompt text first with the tested helper in `references/hebrew-tts-normalization.md` (phones, IDs, shekels, acronyms; add dates and times yourself). Chirp 3 HD `[pause]` tags are unavailable for `he-il`; use punctuation.

#### Google Cloud TTS (Recommended for Natural Sound)

```python
from google.cloud import texttospeech

def synthesize_hebrew(text: str, output_path: str, voice_gender: str = "female") -> None:
    """Convert Hebrew text to speech using Google Cloud TTS."""
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Available Hebrew voices
    voice_name_map = {
        # Chirp3-HD is the newer he-IL voice tier (Achernar, Aoede, Charon,
        # Kore, Puck, Zephyr and more). Wavenet below is the older tier and is
        # still live; A/B them on your own prompts before choosing.
        "female": "he-IL-Wavenet-A",  # Female, high quality
        "male": "he-IL-Wavenet-B",    # Male, high quality
        "female_standard": "he-IL-Standard-A",  # Female, lower cost
        "male_standard": "he-IL-Standard-B",    # Male, lower cost
    }

    voice = texttospeech.VoiceSelectionParams(
        language_code="he-IL",
        name=voice_name_map.get(voice_gender, "he-IL-Wavenet-A"),
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,   # 0.5 to 2.0, adjust for clarity
        pitch=0.0,           # -20.0 to 20.0 semitones
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)
```

#### Amazon Polly Hebrew: NOT available

Amazon Polly does **not** support Hebrew. There is no `he-IL` locale in Polly's supported-languages list and no Hebrew voice of any engine (standard or neural). The "Avri" voice some guides attribute to Polly is actually the **Azure** voice `he-IL-AvriNeural`, not a Polly voice. For a low-cost cloud TTS fallback in Hebrew, use Google Cloud TTS (`he-IL-Wavenet-A/B`) or Azure Neural TTS below instead of Polly.

#### Azure Neural TTS

Highest quality Hebrew voices with SSML support for fine-grained control.

```python
import azure.cognitiveservices.speech as speechsdk

def synthesize_hebrew_azure(text: str, output_path: str) -> None:
    """Convert Hebrew text to speech using Azure Neural TTS."""
    speech_config = speechsdk.SpeechConfig(
        subscription="YOUR_AZURE_KEY",
        region="westeurope",
    )
    # Hebrew neural voices
    speech_config.speech_synthesis_voice_name = "he-IL-HilaNeural"  # Female
    # Alternative: "he-IL-AvriNeural" for male voice

    audio_config = speechsdk.AudioConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = synthesizer.speak_text(text)

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(f"Speech synthesis failed: {result.reason}")


def synthesize_hebrew_ssml(ssml: str, output_path: str) -> None:
    """
    Synthesize Hebrew speech with SSML for fine control.

    Example SSML for IVR prompt:
    <speak version="1.0" xml:lang="he-IL">
        <voice name="he-IL-HilaNeural">
            <prosody rate="0.9">
                ברוכים הבאים לשירות הלקוחות.
            </prosody>
            <break time="500ms"/>
            לתמיכה טכנית, הקישו 1.
            <break time="300ms"/>
            למכירות, הקישו 2.
        </voice>
    </speak>
    """
    speech_config = speechsdk.SpeechConfig(
        subscription="YOUR_AZURE_KEY",
        region="westeurope",
    )
    audio_config = speechsdk.AudioConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = synthesizer.speak_ssml(ssml)
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(f"SSML synthesis failed: {result.reason}")
```

### Step 4: IVR Menu Design for Israeli Businesses

Israeli IVR systems have specific conventions that differ from US/European patterns.

#### Business Hours Routing

Israeli business week is Sunday through Thursday. IVR systems must account for this:

```python
from datetime import datetime
import pytz

ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")

def get_business_status() -> dict:
    """Determine current business status for IVR routing."""
    now = datetime.now(ISRAEL_TZ)
    day = now.weekday()  # 0=Monday, 6=Sunday
    hour = now.hour

    # Israeli business days: Sunday (6) through Thursday (3)
    # Friday (4): half day until ~13:00
    # Saturday (5): closed (Shabbat)

    if day == 5:  # Saturday (Shabbat)
        return {
            "status": "closed",
            "reason": "shabbat",
            "message_he": "שלום, אנחנו סגורים בשבת. נחזור אליכם ביום ראשון.",
            "next_open": "Sunday 9:00",
        }
    elif day == 4:  # Friday
        if hour < 9:
            return {"status": "before_hours", "message_he": "שעות הפעילות ביום שישי: 9:00 עד 13:00."}
        elif hour < 13:
            return {"status": "open", "message_he": "שלום, איך אפשר לעזור?"}
        else:
            return {
                "status": "closed",
                "reason": "friday_afternoon",
                "message_he": "סגורים בשישי אחה\"צ. נחזור ביום ראשון.",
                "next_open": "Sunday 9:00",
            }
    elif day == 6 or day <= 3:  # Sunday through Thursday
        if 9 <= hour < 17:
            return {"status": "open", "message_he": "שלום, איך אפשר לעזור?"}
        else:
            return {
                "status": "after_hours",
                "message_he": "שעות הפעילות שלנו: א'-ה' 9:00-17:00, ו' 9:00-13:00.",
            }
    else:  # Should not happen but handle gracefully
        return {"status": "closed", "message_he": "כרגע אנחנו סגורים."}
```

**This sketch is holiday-blind**: on Yom Kippur it answers "open". `is_open()` in `references/twilio-call-flow.md` uses Hebcal's Israel schedule: closed on yom tov and Yom HaAtzma'ut, early close before a yom tov (not Erev Purim), and a cached table with a configurable outage fallback.

#### Standard Israeli IVR Menu Structure

A complete `IVR_MENU` dictionary (welcome, a 4-option main menu, a customer-service submenu, and an agent queue with periodic Hebrew hold messages) lives in `references/ivr-design-patterns.md` under "Reference IVR_MENU structure". Keep 3-4 options per level, `*` = previous menu and `#` = main menu, an 8-second timeout and 3 retries.

#### Hebrew IVR Prompt Best Practices

| Rule | Example | Why |
|------|---------|-----|
| Use formal register (second person plural) | "הקישו 1" not "תקיש 1" | Professional tone, avoids gender |
| Keep prompts under 15 seconds | 3-4 options max per menu level | Callers lose patience quickly |
| Announce hours before after-hours message | "שעות הפעילות: א'-ה' 9-17" | Reduces callback attempts |
| Offer English option | "For English, press 9" | Some callers will prefer English; measure the take-up on your own line before sizing the branch |
| Use "כוכבית" for star key | "לחזרה, הקישו כוכבית" | Standard Hebrew term for * |
| Use "סולמית" for hash/pound key | "לתפריט הראשי, הקישו סולמית" | Standard Hebrew term for # |
| Repeat the menu on timeout | After 8 seconds of no input | Callers may need time to listen |
| Provide voicemail option after hours | "להשאיר הודעה, הקישו 1" | Captures leads outside business hours |

### Step 5: Voicemail-to-Text Transcription Pipeline

```python
import os
import json
from datetime import datetime

# NOTE: this block is a pipeline SKELETON, not a runnable module.
# detect_voicemail_language() and classify_voicemail_intent() are defined below.
# extract_voicemail_entities(), get_audio_duration() and route_voicemail() are
# YOUR business logic and are intentionally not implemented here: entity
# extraction and routing depend on your CRM and your queue names. Stub them
# before running, or the first call raises NameError.
def process_voicemail(audio_path: str, caller_number: str) -> dict:
    """
    Process a voicemail recording: transcribe, classify, and route.

    Args:
        audio_path: Path to the voicemail audio file
        caller_number: Caller's phone number (+972...)

    Returns:
        Processed voicemail with transcript and routing info
    """
    # Step 1: Transcribe with gpt-transcribe (transcribe_hebrew in Step 2)
    transcript = transcribe_hebrew(audio_path)

    # Step 2: Detect language (Hebrew, English, or mixed)
    language = detect_voicemail_language(transcript)

    # Step 3: Classify intent
    intent = classify_voicemail_intent(transcript)

    # Step 4: Extract key entities
    entities = extract_voicemail_entities(transcript)

    result = {
        "caller": caller_number,
        "timestamp": datetime.now().isoformat(),
        "transcript": transcript,
        "language": language,
        "intent": intent,
        "entities": entities,
        "audio_path": audio_path,
        "duration_seconds": get_audio_duration(audio_path),
    }

    # Step 5: Route based on intent
    result["routing"] = route_voicemail(intent, entities)

    return result


def detect_voicemail_language(text: str) -> str:
    """Detect whether voicemail is Hebrew, English, or mixed."""
    hebrew_chars = sum(1 for c in text if "\u0590" <= c <= "\u05FF")
    latin_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    total = hebrew_chars + latin_chars

    if total == 0:
        return "unknown"

    hebrew_ratio = hebrew_chars / total

    if hebrew_ratio > 0.7:
        return "hebrew"
    elif hebrew_ratio < 0.3:
        return "english"
    else:
        return "mixed"


VOICEMAIL_INTENTS = {
    "callback_request": ["תתקשרו", "תחזרו", "חזרו אליי", "תתקשר"],
    "order_inquiry": ["הזמנה", "משלוח", "חבילה", "מעקב"],
    "complaint": ["תלונה", "בעיה", "לא מרוצה", "לא עובד"],
    "appointment": ["תור", "פגישה", "לקבוע", "לתאם"],
    "general": [],
}


def classify_voicemail_intent(transcript: str) -> str:
    """Classify voicemail intent based on Hebrew keywords."""
    for intent, keywords in VOICEMAIL_INTENTS.items():
        if any(keyword in transcript for keyword in keywords):
            return intent
    return "general"
```

### Step 6: Mixed Language Handling (Hebrew-English)

Israeli tech professionals frequently switch between Hebrew and English mid-sentence (code-switching). Voice bots must handle this gracefully.

```python
def detect_segment_language(text: str) -> str:
    """Label a segment by script: Hebrew block U+0590-U+05FF vs Latin."""
    hebrew = sum(1 for ch in text if "\u0590" <= ch <= "\u05FF")
    latin = sum(1 for ch in text if ch.isascii() and ch.isalpha())
    if hebrew and latin:
        return "mixed"
    return "he" if hebrew else ("en" if latin else "unknown")


def handle_mixed_speech(audio_path: str) -> dict:
    """
    Handle mixed Hebrew-English speech common in Israeli tech.

    Strategy: Use Whisper without language hint for auto-detection,
    then post-process to normalize mixed output. Per-segment output needs
    verbose_json, which only whisper-1 returns, and whisper-1 shuts down on
    2027-02-26. Without segments, use gpt-transcribe with
    languages=["he", "en"] and read the detected `languages` it returns.
    """
    client = openai.OpenAI()

    with open(audio_path, "rb") as f:
        # Omit language parameter to let Whisper handle code-switching
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
        )

    segments = []
    # transcript.segments holds TranscriptionSegment pydantic models, not dicts.
    # segment["text"] raises TypeError and segment.get("text") raises
    # AttributeError on every current openai SDK. Read the attributes.
    for segment in transcript.segments:
        text = segment.text
        lang = detect_segment_language(text)
        segments.append({
            "text": text,
            "language": lang,
            "start": segment.start,
            "end": segment.end,
        })

    return {
        "full_transcript": transcript.text,
        "segments": segments,
        "detected_languages": list(set(s["language"] for s in segments)),
    }


# Common Hebrew-English tech phrases that Whisper may mishandle
HEBREW_ENGLISH_CORRECTIONS = {
    "דיפלוי": "deploy",     # Hebrew-accented English
    "פוש": "push",
    "קומיט": "commit",
    "סרבר": "server",
    "באג": "bug",
    "פיצ'ר": "feature",
    "אפליקציה": "application",
    "דאטהבייס": "database",
}
```

### Step 7: Phone Integration (Twilio)

#### Setting Up Twilio with Israeli Numbers (+972)

```python
from twilio.rest import Client

TWILIO_ACCOUNT_SID = "YOUR_SID"
TWILIO_AUTH_TOKEN = "YOUR_TOKEN"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def purchase_israeli_number(bundle_sid=None, address_sid=None):
    """Purchase an Israeli phone number from Twilio.

    Twilio documents that "some regions require a Bundle" or an Address to
    meet local regulations, and a Regulation is unique per IsoCountry,
    NumberType and EndUserType. Check the IL Regulation for your number type
    (Console purchase flow or the Regulatory Compliance API) and each
    candidate's `address_requirements` BEFORE buying, then pass the SIDs.
    """
    numbers = client.available_phone_numbers("IL").local.list(limit=5)
    if not numbers:
        return None
    kwargs = {}
    if bundle_sid:
        kwargs["bundle_sid"] = bundle_sid
    if address_sid:
        kwargs["address_sid"] = address_sid
    purchased = client.incoming_phone_numbers.create(
        phone_number=numbers[0].phone_number,
        voice_url="https://your-server.com/voice/incoming",
        voice_method="POST",
        **kwargs,
    )
    return purchased.phone_number
```

#### The call flow

The complete, tested Flask call flow lives in `references/twilio-call-flow.md`. Copy it from there rather than writing one from the fragments below, because each of these is a way a hand-written flow breaks on a real line:

- Every `<Gather>` and `<Record>` needs an `action` route that exists. A `<Record>` without `action` re-requests the current URL, replays the prompt and records again in a loop.
- Carry the attempt count in the URL and send the caller to an agent after 3 tries; a bare `<Redirect>` back to the menu loops forever on silence.
- Validate `X-Twilio-Signature` on every webhook.
- Fetch the voicemail from `recordingStatusCallback`, not from the `<Record>` action: the recording may not be accessible yet when the action fires.
- `<Say>` uses `he-IL` voices: Twilio offers `Google.he-IL-Standard-A` to `D` and `Google.he-IL-Wavenet-A` to `D`, and NO he-IL Chirp3-HD voice, although Google itself has one.
- Spoken input in `<Gather>`: Twilio's only Google Hebrew row (`iw-IL`) sits in a table it marks deprecated. Test `speechModel="deepgram_nova-3"` with `language="he"` (Deepgram lists Hebrew for Nova-3) and keep DTMF as the fallback.
- A TwiML webhook carries no audio. A conversational bot needs Media Streams (`<Connect><Stream>`, always 8 kHz mu-law) or OpenAI Realtime over SIP; the reference covers both.

### Step 8: Hebrew Accent Handling

Hebrew speakers in Israel have diverse accent backgrounds that affect speech recognition accuracy.

| Accent Type | Characteristics | What to test for |
|-------------|----------------|------------------|
| Standard Israeli | Modern Israeli pronunciation, merged alef/ayin, no distinction between chet/chaf | Your baseline set |
| Russian-accented | Hard "r" (guttural to alveolar), softer sibilants, vowel shifts | Whether a Russian language hint helps or hurts on your audio |
| Arabic-accented | Preserved pharyngeal sounds (ayin, chet), emphatic consonants | Whether pharyngeals are dropped or substituted in the transcript |
| Ethiopian-accented | Distinct vowel patterns, different stress patterns | Whether word boundaries survive the different stress pattern |
| English-accented | American/British vowel sounds applied to Hebrew, different "r" | Whether the model code-switches mid-word |

**No vendor publishes accent-conditioned Hebrew WER, so this table deliberately ranks nothing.** Earlier versions asserted which accents degrade and which model handles them best; those rankings had no source. Collect 20-30 utterances per accent group from your own callers and measure with the bundled demo script before choosing a provider.

**Improving accuracy for non-standard accents:**
- Measure before choosing a primary provider; a model trained on diverse accents is a reason to test it, not a result
- For Google/Azure, consider custom speech models with accent-specific training data
- Implement a confidence threshold and re-prompt below it, but derive the number from your own recordings rather than copying one (see the Gotcha on thresholds). A threshold that is right for a quiet office is wrong for a bus
- Add domain-specific vocabulary to improve recognition of industry terms

Run the demo script to test Hebrew STT with sample audio:
```bash
python scripts/hebrew-stt-demo.py --help
```

## Examples

### Example 1: Build a Restaurant Reservation IVR

User says: "I need an IVR system for a restaurant in Tel Aviv. Callers should be able to make reservations, check hours, and hear the menu."

Actions:
1. Design a 3-option main menu: reservations (1), hours/location (2), menu (3)
2. Set up business hours routing: Sunday-Thursday 11:00-23:00, Friday 11:00-15:00, Saturday closed
3. Configure Hebrew TTS for all prompts using Google Cloud Wavenet voices
4. Implement reservation flow: gather date, party size, name, phone confirmation
5. Set up after-hours voicemail with transcription pipeline
6. Integrate with Twilio using an Israeli +972 number

### Example 2: Customer Service Voice Bot

User says: "Build a conversational voice bot for our e-commerce site. It should handle order status, returns, and escalate to a human agent."

Actions:
1. Connect the call audio with Twilio Media Streams (8 kHz mu-law) or OpenAI Realtime over SIP; a plain TwiML webhook carries no audio
2. Configure Google Cloud STT V2 for real-time streaming transcription. Hebrew is `iw-IL`, and streaming Hebrew requires `chirp_3` in the `eu` or `us` multi-region (Preview): `chirp_2` does not list Hebrew for StreamingRecognize. There is no telephony-tuned Hebrew model
3. Process transcribed text through an LLM for intent detection and response generation
4. Use Azure Neural TTS (he-IL-HilaNeural) for natural Hebrew responses
5. Implement order lookup by order number (DTMF or spoken digits)
6. Add human agent escalation with queue management
7. Handle mixed Hebrew-English input for product names

### Example 3: Voicemail Transcription Service

User says: "I want to transcribe voicemails left on our business line and send them as text messages to the relevant department."

Actions:
1. Configure Twilio recording webhook to capture voicemail audio
2. Set up a `gpt-transcribe` transcription pipeline for Hebrew
3. Classify voicemail intent (callback request, complaint, order inquiry)
4. Extract entities (phone numbers, order numbers, names)
5. Route transcribed text via SMS/WhatsApp to the relevant department
6. Store transcripts with audio links for reference

### Example 4: Handling Mixed Hebrew-English Speech

User says: "Our callers frequently mix Hebrew and English, especially tech terms. How do I handle this?"

Actions:
1. Pass both languages to gpt-transcribe (`languages=["he", "en"]`) rather than forcing Hebrew alone
2. Implement post-processing to normalize Hebrew-accented English tech terms
3. Build a custom vocabulary of Hebrew-English tech terms (deploy, push, server, bug)
4. Test with sample mixed-language audio using the demo script
5. Set confidence thresholds and fallback to asking the caller to repeat if low

## Bundled Resources

### Scripts
- `scripts/hebrew-stt-demo.py` -- Demo script for Hebrew speech-to-text using OpenAI (`gpt-transcribe` by default, `whisper-1` only for `--verbose` timestamps). Generates a sample Hebrew audio file using TTS and transcribes it back to text. Tests basic Hebrew STT accuracy. Run: `python scripts/hebrew-stt-demo.py --help`

### References
- `references/hebrew-stt-models.md` -- Comparison table of Hebrew speech-to-text models (Whisper, Google Cloud STT, Azure Speech) with structural differences (no vendor publishes Hebrew WER per condition such as phone, noise or accent, so none is ranked), pricing, and recommendations by use case. Consult when choosing an STT provider.
- `references/twilio-call-flow.md` -- Complete, tested Flask call flow for Twilio: signature validation, Hebcal holiday and erev-chag hours, bounded retries, loop-free voicemail and recording fetch, plus Media Streams and OpenAI Realtime SIP for conversational bots. Consult before writing webhooks.
- `references/hebrew-tts-normalization.md` -- Hebrew text normalization before TTS (phones, IDs, shekels, acronyms) with a tested helper and its test script.
- `references/ivr-design-patterns.md` -- Common IVR flow patterns for Israeli businesses including restaurant, clinic, customer service, and government office templates. Consult when designing IVR menu structures.

## Gotchas

- Hebrew speech-to-text engines struggle with Israeli slang ("yalla", "sababa", "balagan") and loan words from Arabic, Russian, and Amharic. Agents may not account for multilingual input in Hebrew voice bots.
- Israeli phone IVR systems must offer Hebrew as the default language, with English as secondary. Agents may build voice bots with English as the default, frustrating Hebrew-speaking callers.
- Hebrew TTS does NOT require nikud, and every Hebrew string in this skill is deliberately unvocalized: Google and Azure he-IL neural voices run their own diacritization, which is why unvocalized input is the normal case. What nikud buys you is disambiguation of homographs. "דבר" can be read `davar` (thing) or `daber` (speak), so if a homograph lands on a word that changes the meaning of a menu option, either add nikud on that word alone or reword the prompt. Listen to the output before shipping rather than assuming either behaviour.
- Israeli phone numbers have varying IVR input lengths: landlines are 9 digits (0X-XXXXXXX); mobile (05X) and 07X numbers are 10 digits (05X-XXXXXXX, 07X-XXXXXXX). Voice bots must accept both formats.
- Do not copy a confidence threshold from a tutorial, including from earlier versions of this skill, which asserted that Israeli ambient noise runs above a global average. We have no source for that comparison. Set the threshold from measurements on your own line: record real calls from the environments your callers are actually in (cafes, open offices, public transit are the common hard cases here) and tune against that recording set.
- **ElevenLabs v3 and v4 are NOT on the Text to Speech `stream-input` WebSocket.** That endpoint does not support `eleven_v3` or `eleven_v4_turbo`, and the Hebrew-free `eleven_flash_v2_5` in the vendor's own WebSocket example is not a substitute. Use the Text to Dialogue WebSocket for v3/v4 instead (`eleven_v4_turbo` allows exactly one registered voice per connection).
- **Every OpenAI transcription model this skill used before 2026-09 shuts down on 2027-02-26** (`whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `gpt-4o-transcribe-diarize`). Agents will keep emitting `whisper-1` from training data. Default to `gpt-transcribe`, and remember it takes `languages` (a list) in place of the singular `language`; do not send both. Only `whisper-1` returns word timestamps, so a timestamp feature built today needs a migration plan.
- The Hebrew voice landscape moves fast (ElevenLabs shipped v4, Inworld added Hebrew as a Tier 1 language and deprecated its 1.5 models, OpenAI replaced its whole transcription line, all during 2026). Re-verify at build time, and check the vendor's enumerated LANGUAGE LIST rather than a headline language count.


## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| OpenAI Whisper (Hebrew STT) | https://github.com/openai/whisper | Multilingual speech-to-text including Hebrew, model sizes, accuracy benchmarks |
| Google Cloud Speech-to-Text | https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages | Hebrew support (listed as `iw-IL`), streaming recognition, pricing |
| Azure AI Speech (Hebrew) | https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support | Hebrew STT/TTS voices, neural voice list |
| OpenAI deprecations | https://developers.openai.com/api/docs/deprecations | Shutdown dates and replacements for realtime and transcription models |
| ivrit.ai (Hebrew voice corpus) | https://www.ivrit.ai | Open-source Hebrew speech corpus, pre-trained ASR models |
| ElevenLabs models | https://elevenlabs.io/docs/overview/models | Per-model language lists (Hebrew in v3/v4, absent from Multilingual v2 and Flash v2.5) and which WebSocket each model uses |
| Deepdub API (Israeli) | https://docs.deepdub.ai/api-reference/tts/generate-and-stream-tts-audio | Supported languages (Hebrew `he-IL`), current model id |
| Inworld TTS languages | https://docs.inworld.ai/tts/capabilities/multilingual | Hebrew `he` tier, current model ids |

## Troubleshooting

### Error: "Hebrew transcription returns Arabic text"
Cause: STT model misidentifies Hebrew as Arabic due to shared character ranges or similar phonemes.
Solution: Explicitly set the language. Google STT wants `iw-IL` (NOT `he-IL`, which does not appear on its supported-languages table at all); Google TTS and Azure want `he-IL`; OpenAI wants `languages=["he"]` on gpt-transcribe and `language="he"` on whisper-1. Adding a Hebrew prompt hint also helps: `prompt="שלום, ברוכים הבאים"`.

### Error: "TTS voice sounds robotic for Hebrew"
Cause: Using Standard-tier voices instead of Neural/Wavenet voices.
Solution: Switch to neural voices: Google Wavenet (he-IL-Wavenet-A/B) or Azure Neural (he-IL-HilaNeural). (Amazon Polly does not support Hebrew at all, so it is not an option.) Neural voices are more expensive but significantly more natural.

### Error: "IVR menu times out before caller responds"
Cause: Timeout too short, especially for elderly callers or long Hebrew prompts.
Solution: Increase gather timeout to 8-10 seconds. Add a numbered "repeat" key (for example "לשמוע שוב, הקישו 7"; never a key already used for a language option); keep `*` for the previous menu. Hebrew prompts often run longer than English.

### Error: "Twilio cannot find Israeli numbers"
Cause: Israeli number availability varies. Twilio has limited +972 inventory compared to US numbers.
Solution: Search for both local and toll-free numbers, and check each candidate's `address_requirements` and the IL Regulation for that number type: a purchase can fail for a missing Bundle or Address rather than for inventory. Vonage is worth a quote as an alternative, but neither vendor publishes a comparable Israeli number inventory, so compare actual availability yourself rather than trusting a ranking. For high-volume needs, contact Twilio sales for dedicated number blocks. You can also port existing Israeli numbers to Twilio.
