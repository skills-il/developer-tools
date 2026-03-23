---
name: hebrew-voice-bot-builder
description: Build Hebrew voice bots and IVR (Interactive Voice Response) systems with speech-to-text, text-to-speech, and telephony integration for Israeli businesses. Use when user asks to "build a Hebrew voice bot", "create an IVR in Hebrew", "Hebrew speech-to-text", "binui bot koli b'ivrit", "maarechet maane koli", "zihui dibur b'ivrit", or "Twilio Israel". Covers OpenAI Whisper Hebrew, Google Cloud STT/TTS he-IL, Azure Speech Services, Amazon Polly Hebrew, IVR menu design for Sunday-Thursday business hours, voicemail transcription, Hebrew accent handling, and +972 phone integration via Twilio and Vonage. Do NOT use for text-based chatbots (use hebrew-chatbot-builder), Hebrew NLP without voice (use hebrew-nlp-toolkit), or SMS messaging (use israeli-sms-gateway).
license: MIT
allowed-tools: Bash(python:*)
compatibility: Requires API keys for speech services (OpenAI, Google Cloud, Azure, or AWS). Requires Twilio or Vonage account for telephony. Works with Claude Code, Cursor, Windsurf.
---

# Hebrew Voice Bot Builder

Build production-ready Hebrew voice bots and IVR systems for Israeli businesses. This skill covers the full voice pipeline: speech-to-text (STT), text-to-speech (TTS), IVR flow design, telephony integration, and Hebrew-specific challenges like accent handling and mixed Hebrew-English speech.

## Instructions

### Step 1: Choose Your Architecture

Before building, decide on the voice bot architecture based on the use case:

| Architecture | Best For | Components |
|-------------|----------|------------|
| IVR (keypad) | Simple menu navigation, payment lines, appointment scheduling | TTS + DTMF + telephony |
| Voice bot (conversational) | Customer service, order status, FAQ handling | STT + LLM + TTS + telephony |
| Voicemail transcription | Missed call handling, message routing | STT + notification pipeline |
| Hybrid | Complex flows with both speech and keypad input | STT + TTS + DTMF + telephony |

**Key decisions:**
- **STT provider**: OpenAI Whisper (best accuracy for Hebrew), Google Cloud STT (low latency), Azure Speech (enterprise features)
- **TTS provider**: Google Cloud TTS (natural voices), Amazon Polly Hebrew (cost-effective), Azure Neural TTS (highest quality)
- **Telephony**: Twilio (largest Israeli number inventory), Vonage (competitive pricing for Israel)
- **Hosting**: Cloud functions for low-volume, dedicated servers for high-volume

### Step 2: Hebrew Speech-to-Text (STT)

#### OpenAI Whisper (Recommended for Accuracy)

Whisper provides the best Hebrew transcription accuracy, especially for mixed Hebrew-English speech common in Israeli tech environments.

```python
import openai

client = openai.OpenAI()

def transcribe_hebrew(audio_file_path: str) -> str:
    """Transcribe Hebrew audio using OpenAI Whisper."""
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="he",  # Force Hebrew language detection
            response_format="text",
        )
    return transcript


def transcribe_hebrew_with_timestamps(audio_file_path: str) -> dict:
    """Transcribe with word-level timestamps for subtitle generation."""
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

**Whisper Hebrew tips:**
- Set `language="he"` explicitly to avoid misdetecting Hebrew as Arabic
- For mixed Hebrew-English, let Whisper auto-detect (omit the language parameter) and post-process
- Whisper handles niqqud-free text well (standard for modern Hebrew)
- Audio quality matters: 16kHz+ sample rate, mono channel, WAV or FLAC preferred
- Maximum file size: 25MB. For longer recordings, split into segments

#### Google Cloud Speech-to-Text

Lower latency than Whisper, suitable for real-time voice bots.

```python
from google.cloud import speech_v1

def transcribe_hebrew_google(audio_content: bytes) -> str:
    """Transcribe Hebrew audio using Google Cloud STT."""
    client = speech_v1.SpeechClient()

    audio = speech_v1.RecognitionAudio(content=audio_content)
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="he-IL",
        # Enable automatic punctuation for Hebrew
        enable_automatic_punctuation=True,
        # Model optimized for phone calls
        model="phone_call",
        # Enable word-level confidence scores
        enable_word_confidence=True,
    )

    response = client.recognize(config=config, audio=audio)

    results = []
    for result in response.results:
        results.append(result.alternatives[0].transcript)

    return " ".join(results)


def stream_transcribe_hebrew(audio_generator):
    """Real-time streaming transcription for live phone calls."""
    client = speech_v1.SpeechClient()

    config = speech_v1.StreamingRecognitionConfig(
        config=speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.MULAW,
            sample_rate_hertz=8000,  # Standard phone audio
            language_code="he-IL",
            model="phone_call",
            enable_automatic_punctuation=True,
        ),
        interim_results=True,  # Get partial results for faster response
    )

    streaming_config = speech_v1.StreamingRecognizeRequest(
        streaming_config=config
    )

    def request_generator():
        yield streaming_config
        for chunk in audio_generator:
            yield speech_v1.StreamingRecognizeRequest(audio_content=chunk)

    responses = client.streaming_recognize(requests=request_generator())

    for response in responses:
        for result in response.results:
            if result.is_final:
                yield result.alternatives[0].transcript
```

#### Azure Speech Services

Enterprise-grade with custom model training for domain-specific Hebrew vocabulary.

```python
import azure.cognitiveservices.speech as speechsdk

def transcribe_hebrew_azure(audio_file_path: str) -> str:
    """Transcribe Hebrew audio using Azure Speech Services."""
    speech_config = speechsdk.SpeechConfig(
        subscription="YOUR_AZURE_KEY",
        region="westeurope",  # Closest region to Israel
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

Consult `references/hebrew-stt-models.md` for a detailed comparison of STT providers with accuracy benchmarks.

### Step 3: Hebrew Text-to-Speech (TTS)

#### Google Cloud TTS (Recommended for Natural Sound)

```python
from google.cloud import texttospeech

def synthesize_hebrew(text: str, output_path: str, voice_gender: str = "female") -> None:
    """Convert Hebrew text to speech using Google Cloud TTS."""
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Available Hebrew voices
    voice_name_map = {
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

#### Amazon Polly Hebrew

Cost-effective for high-volume TTS needs.

```python
import boto3

def synthesize_hebrew_polly(text: str, output_path: str) -> None:
    """Convert Hebrew text to speech using Amazon Polly."""
    polly = boto3.client("polly", region_name="eu-west-1")

    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId="Avri",  # Hebrew male standard voice (no neural Hebrew voice exists)
        Engine="standard",   # Standard engine (neural not available for Hebrew)
        LanguageCode="he-IL",
    )

    with open(output_path, "wb") as out:
        out.write(response["AudioStream"].read())
```

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

#### Standard Israeli IVR Menu Structure

```python
IVR_MENU = {
    "welcome": {
        "prompt_he": "שלום, הגעתם ל{company_name}.",
        "prompt_en": "Hello, you've reached {company_name}. For English, press 9.",
    },
    "main_menu": {
        "prompt_he": (
            "לשירות לקוחות, הקישו 1. "
            "למכירות, הקישו 2. "
            "לתמיכה טכנית, הקישו 3. "
            "למצב הזמנה, הקישו 4. "
            "לשמוע שוב, הקישו כוכבית."
        ),
        "options": {
            "1": "customer_service",
            "2": "sales",
            "3": "tech_support",
            "4": "order_status",
            "9": "english_menu",
            "*": "main_menu",  # Repeat
        },
        "timeout_seconds": 8,
        "no_input_prompt_he": "לא קיבלנו בחירה. בבקשה הקישו מספר מ-1 עד 4.",
        "invalid_prompt_he": "בחירה לא תקינה. נסו שוב.",
        "max_retries": 3,
    },
    "customer_service": {
        "prompt_he": (
            "לבירור חשבון, הקישו 1. "
            "לתלונה, הקישו 2. "
            "לנציג, הקישו 0. "
            "לחזרה לתפריט הראשי, הקישו כוכבית."
        ),
        "options": {
            "1": "account_inquiry",
            "2": "complaint",
            "0": "agent_queue",
            "*": "main_menu",
        },
    },
    "agent_queue": {
        "prompt_he": "ממתינים לנציג הפנוי הבא. זמן המתנה משוער: {wait_time} דקות.",
        "hold_music": "hold_music_hebrew.mp3",
        "periodic_message_he": "תודה שאתם ממתינים. שיחתכם חשובה לנו.",
        "periodic_interval_seconds": 60,
    },
}
```

#### Hebrew IVR Prompt Best Practices

| Rule | Example | Why |
|------|---------|-----|
| Use formal register (second person plural) | "הקישו 1" not "תקיש 1" | Professional tone, avoids gender |
| Keep prompts under 15 seconds | 3-4 options max per menu level | Callers lose patience quickly |
| Announce hours before after-hours message | "שעות הפעילות: א'-ה' 9-17" | Reduces callback attempts |
| Offer English option | "For English, press 9" | 20% of Israeli calls may prefer English |
| Use "כוכבית" for star key | "לחזרה, הקישו כוכבית" | Standard Hebrew term for * |
| Use "סולמית" for hash/pound key | "לאישור, הקישו סולמית" | Standard Hebrew term for # |
| Repeat the menu on timeout | After 8 seconds of no input | Callers may need time to listen |
| Provide voicemail option after hours | "להשאיר הודעה, הקישו 1" | Captures leads outside business hours |

### Step 5: Voicemail-to-Text Transcription Pipeline

```python
import os
import json
from datetime import datetime

def process_voicemail(audio_path: str, caller_number: str) -> dict:
    """
    Process a voicemail recording: transcribe, classify, and route.

    Args:
        audio_path: Path to the voicemail audio file
        caller_number: Caller's phone number (+972...)

    Returns:
        Processed voicemail with transcript and routing info
    """
    # Step 1: Transcribe using Whisper (best Hebrew accuracy)
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
def handle_mixed_speech(audio_path: str) -> dict:
    """
    Handle mixed Hebrew-English speech common in Israeli tech.

    Strategy: Use Whisper without language hint for auto-detection,
    then post-process to normalize mixed output.
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
    for segment in transcript.segments:
        text = segment["text"]
        lang = detect_segment_language(text)
        segments.append({
            "text": text,
            "language": lang,
            "start": segment["start"],
            "end": segment["end"],
        })

    return {
        "full_transcript": transcript.text,
        "segments": segments,
        "detected_languages": list(set(s["language"] for s in segments)),
    }


# Common Hebrew-English tech phrases that Whisper may mishandle
HEBREW_ENGLISH_CORRECTIONS = {
    "דיפלוי": "deploy",     # Hebrew-accented English
    "פושׁ": "push",
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
from twilio.twiml.voice_response import VoiceResponse, Gather

TWILIO_ACCOUNT_SID = "YOUR_SID"
TWILIO_AUTH_TOKEN = "YOUR_TOKEN"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def purchase_israeli_number():
    """Purchase an Israeli phone number from Twilio."""
    numbers = client.available_phone_numbers("IL").local.list(limit=5)
    if numbers:
        purchased = client.incoming_phone_numbers.create(
            phone_number=numbers[0].phone_number,
            voice_url="https://your-server.com/voice/incoming",
            voice_method="POST",
        )
        return purchased.phone_number
    return None


# Flask webhook handler for incoming calls
from flask import Flask, request

app = Flask(__name__)


@app.route("/voice/incoming", methods=["POST"])
def handle_incoming_call():
    """Handle incoming call with Hebrew IVR menu."""
    response = VoiceResponse()

    # Welcome message in Hebrew
    response.say(
        "שלום, הגעתם לשירות הלקוחות.",
        language="he-IL",
        voice="Google.he-IL-Wavenet-A",
    )

    # Gather DTMF input with Hebrew prompt
    gather = Gather(
        num_digits=1,
        action="/voice/menu-selection",
        timeout=8,
        language="he-IL",
    )
    gather.say(
        "לשירות לקוחות, הקישו 1. למכירות, הקישו 2. לתמיכה טכנית, הקישו 3.",
        language="he-IL",
        voice="Google.he-IL-Wavenet-A",
    )
    response.append(gather)

    # If no input, repeat
    response.redirect("/voice/incoming")

    return str(response)


@app.route("/voice/menu-selection", methods=["POST"])
def handle_menu_selection():
    """Route based on DTMF selection."""
    digit = request.form.get("Digits", "")
    response = VoiceResponse()

    routes = {
        "1": "/voice/customer-service",
        "2": "/voice/sales",
        "3": "/voice/tech-support",
    }

    if digit in routes:
        response.redirect(routes[digit])
    else:
        response.say(
            "בחירה לא תקינה. בבקשה נסו שוב.",
            language="he-IL",
            voice="Google.he-IL-Wavenet-A",
        )
        response.redirect("/voice/incoming")

    return str(response)


@app.route("/voice/voicemail", methods=["POST"])
def handle_voicemail():
    """Record a voicemail with Hebrew instructions."""
    response = VoiceResponse()

    response.say(
        "אנחנו כרגע לא זמינים. בבקשה השאירו הודעה אחרי הצפצוף ונחזור אליכם בהקדם.",
        language="he-IL",
        voice="Google.he-IL-Wavenet-A",
    )

    response.record(
        max_length=120,  # 2 minutes max
        action="/voice/voicemail-complete",
        transcribe=False,  # We handle transcription ourselves for better Hebrew
        play_beep=True,
    )

    return str(response)
```

### Step 8: Hebrew Accent Handling

Hebrew speakers in Israel have diverse accent backgrounds that affect speech recognition accuracy.

| Accent Type | Characteristics | STT Impact |
|-------------|----------------|------------|
| Standard Israeli | Modern Israeli pronunciation, merged alef/ayin, no distinction between chet/chaf | Baseline accuracy, all models handle well |
| Russian-accented | Hard "r" (guttural to alveolar), softer sibilants, vowel shifts | May reduce accuracy by 5-10%. Add Russian as alternate language hint |
| Arabic-accented | Preserved pharyngeal sounds (ayin, chet), emphatic consonants | Generally handled well by models trained on Israeli data |
| Ethiopian-accented | Distinct vowel patterns, different stress patterns | May need custom model training for high accuracy |
| English-accented | American/British vowel sounds applied to Hebrew, different "r" | Mixed results. Whisper handles best due to multilingual training |

**Improving accuracy for non-standard accents:**
- Use Whisper as primary (trained on diverse accents)
- For Google/Azure, consider custom speech models with accent-specific training data
- Implement a confidence threshold: if STT confidence is below 0.7, ask the caller to repeat
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

Result: Complete IVR system with Hebrew prompts, business-hours-aware routing, and voicemail transcription.

### Example 2: Customer Service Voice Bot

User says: "Build a conversational voice bot for our e-commerce site. It should handle order status, returns, and escalate to a human agent."

Actions:
1. Set up Twilio webhook for incoming calls
2. Configure Google Cloud STT for real-time streaming transcription (he-IL, phone_call model)
3. Process transcribed text through an LLM for intent detection and response generation
4. Use Azure Neural TTS (he-IL-HilaNeural) for natural Hebrew responses
5. Implement order lookup by order number (DTMF or spoken digits)
6. Add human agent escalation with queue management
7. Handle mixed Hebrew-English input for product names

Result: Conversational voice bot that understands Hebrew speech, provides order information, and seamlessly escalates to human agents.

### Example 3: Voicemail Transcription Service

User says: "I want to transcribe voicemails left on our business line and send them as text messages to the relevant department."

Actions:
1. Configure Twilio recording webhook to capture voicemail audio
2. Set up Whisper-based transcription pipeline for Hebrew
3. Classify voicemail intent (callback request, complaint, order inquiry)
4. Extract entities (phone numbers, order numbers, names)
5. Route transcribed text via SMS/WhatsApp to the relevant department
6. Store transcripts with audio links for reference

Result: Automated voicemail-to-text pipeline that transcribes Hebrew voicemails and routes them by intent.

### Example 4: Handling Mixed Hebrew-English Speech

User says: "Our callers frequently mix Hebrew and English, especially tech terms. How do I handle this?"

Actions:
1. Configure Whisper without a fixed language parameter (auto-detection handles code-switching)
2. Implement post-processing to normalize Hebrew-accented English tech terms
3. Build a custom vocabulary of Hebrew-English tech terms (deploy, push, server, bug)
4. Test with sample mixed-language audio using the demo script
5. Set confidence thresholds and fallback to asking the caller to repeat if low

Result: Voice bot that correctly transcribes mixed Hebrew-English speech common in Israeli tech environments.

## Bundled Resources

### Scripts
- `scripts/hebrew-stt-demo.py` -- Demo script for Hebrew speech-to-text using OpenAI Whisper. Generates a sample Hebrew audio file using TTS and transcribes it back to text. Tests basic Hebrew STT accuracy. Run: `python scripts/hebrew-stt-demo.py --help`

### References
- `references/hebrew-stt-models.md` -- Comparison table of Hebrew speech-to-text models (Whisper, Google Cloud STT, Azure Speech) with accuracy benchmarks, latency, pricing, and recommendations by use case. Consult when choosing an STT provider.
- `references/ivr-design-patterns.md` -- Common IVR flow patterns for Israeli businesses including restaurant, clinic, customer service, and government office templates. Consult when designing IVR menu structures.

## Gotchas

- Hebrew speech-to-text engines struggle with Israeli slang ("yalla", "sababa", "balagan") and loan words from Arabic, Russian, and Amharic. Agents may not account for multilingual input in Hebrew voice bots.
- Israeli phone IVR systems must offer Hebrew as the default language, with English as secondary. Agents may build voice bots with English as the default, frustrating Hebrew-speaking callers.
- Hebrew Text-to-Speech (TTS) requires correct nikud (vowel diacritics) placement for proper pronunciation. Without nikud, ambiguous words like "דבר" may be read as "davar" (thing) or "daber" (speak).
- Israeli phone numbers have varying IVR input lengths: landlines are 9 digits (0X-XXXXXXX), mobile are 10 digits (05X-XXXXXXX). Voice bots must accept both formats.
- Background noise levels in typical Israeli environments (cafes, open offices, public transit) are higher than global averages. Voice bot confidence thresholds should be set lower to avoid excessive re-prompts.

## Troubleshooting

### Error: "Hebrew transcription returns Arabic text"
Cause: STT model misidentifies Hebrew as Arabic due to shared character ranges or similar phonemes.
Solution: Explicitly set the language to "he-IL" (Google/Azure) or `language="he"` (Whisper). For Whisper, adding a Hebrew prompt hint also helps: `prompt="שלום, ברוכים הבאים"`.

### Error: "TTS voice sounds robotic for Hebrew"
Cause: Using Standard-tier voices instead of Neural/Wavenet voices.
Solution: Switch to neural voices: Google Wavenet (he-IL-Wavenet-A/B) or Azure Neural (he-IL-HilaNeural). Amazon Polly Hebrew only offers a standard voice (Avri, male) with no neural option. Neural voices are more expensive but significantly more natural.

### Error: "IVR menu times out before caller responds"
Cause: Timeout too short, especially for elderly callers or long Hebrew prompts.
Solution: Increase gather timeout to 8-10 seconds. Add a "repeat" option ("לשמוע שוב, הקישו כוכבית"). Consider that Hebrew prompts may take longer than English due to longer word counts for the same content.

### Error: "Twilio cannot find Israeli numbers"
Cause: Israeli number availability varies. Twilio has limited +972 inventory compared to US numbers.
Solution: Search for both local and toll-free numbers. Consider Vonage as an alternative with better Israeli number availability. For high-volume needs, contact Twilio sales for dedicated number blocks. You can also port existing Israeli numbers to Twilio.
