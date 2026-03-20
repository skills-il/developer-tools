---
name: hebrew-voice-bot-builder
description: >-
  Build Hebrew voice bots and IVR (Interactive Voice Response) systems with
  speech-to-text, text-to-speech, and telephony integration for Israeli
  businesses. Use when user asks to "build a Hebrew voice bot", "create an IVR
  in Hebrew", "Hebrew speech-to-text", "binui bot koli b'ivrit", "maarechet
  maane koli", "zihui dibur b'ivrit", or "Twilio Israel". Covers OpenAI
  Whisper Hebrew, Google Cloud STT/TTS he-IL, Azure Speech Services, Amazon
  Polly Hebrew, IVR menu design for Sunday-Thursday business hours, voicemail
  transcription, Hebrew accent handling, and +972 phone integration via Twilio
  and Vonage. Do NOT use for text-based chatbots (use hebrew-chatbot-builder),
  Hebrew NLP without voice (use hebrew-nlp-toolkit), or SMS messaging (use
  israeli-sms-gateway).
license: MIT
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
---

# בונה בוטים קוליים בעברית

בניית בוטים קוליים ומערכות מענה קולי (IVR) ברמת פרודקשן לעסקים ישראליים. הסקיל מכסה את כל צינור הקול: זיהוי דיבור (STT), סינתזת דיבור (TTS), עיצוב תפריטי IVR, אינטגרציה טלפונית, ואתגרים ייחודיים לעברית כמו מבטאים שונים ודיבור מעורב עברית-אנגלית.

## הוראות

### שלב 1: בחירת ארכיטקטורה

לפני הבנייה, צריך להחליט על הארכיטקטורה בהתאם לתרחיש:

| ארכיטקטורה | מתאים ל | רכיבים |
|------------|---------|--------|
| IVR (מקלדת) | ניווט תפריטים, קווי תשלום, קביעת תורים | TTS + DTMF + טלפוניה |
| בוט קולי (שיחתי) | שירות לקוחות, מצב הזמנה, שאלות נפוצות | STT + LLM + TTS + טלפוניה |
| תמלול הודעות קוליות | טיפול בשיחות שלא נענו, ניתוב הודעות | STT + צינור התראות |
| היברידי | תהליכים מורכבים עם קלט קולי וגם מקלדת | STT + TTS + DTMF + טלפוניה |

**החלטות מרכזיות:**
- **ספק STT**: OpenAI Whisper (הדיוק הכי טוב לעברית), Google Cloud STT (זמן תגובה נמוך), Azure Speech (פיצ'רים ארגוניים)
- **ספק TTS**: Google Cloud TTS (קולות טבעיים), Amazon Polly Hebrew (משתלם מבחינת עלות), Azure Neural TTS (האיכות הגבוהה ביותר)
- **טלפוניה**: Twilio (מלאי המספרים הישראלי הגדול ביותר), Vonage (תמחור תחרותי לישראל)
- **אירוח**: פונקציות ענן לנפח נמוך, שרתים ייעודיים לנפח גבוה

### שלב 2: זיהוי דיבור בעברית (STT)

#### OpenAI Whisper (מומלץ לדיוק)

Whisper מספק את הדיוק הטוב ביותר בתמלול עברית, במיוחד לדיבור מעורב עברית-אנגלית שנפוץ בסביבות הייטק ישראליות.

```python
import openai

client = openai.OpenAI()

def transcribe_hebrew(audio_file_path: str) -> str:
    """תמלול קובץ אודיו בעברית באמצעות Whisper."""
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="he",  # כפיית זיהוי עברית
            response_format="text",
        )
    return transcript
```

**טיפים ל-Whisper בעברית:**
- להגדיר `language="he"` במפורש כדי למנוע זיהוי שגוי כערבית
- לדיבור מעורב עברית-אנגלית, לא להגדיר שפה ולתת ל-Whisper לזהות אוטומטית
- Whisper מתמודד היטב עם טקסט ללא ניקוד (סטנדרטי בעברית מודרנית)
- איכות אודיו חשובה: קצב דגימה 16kHz+, ערוץ מונו, פורמט WAV או FLAC עדיף
- גודל קובץ מקסימלי: 25MB. להקלטות ארוכות, לחלק לסגמנטים

#### Google Cloud Speech-to-Text

זמן תגובה נמוך יותר מ-Whisper, מתאים לבוטים קוליים בזמן אמת.

```python
from google.cloud import speech_v1

def transcribe_hebrew_google(audio_content: bytes) -> str:
    """תמלול עברית באמצעות Google Cloud STT."""
    client = speech_v1.SpeechClient()

    audio = speech_v1.RecognitionAudio(content=audio_content)
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="he-IL",
        enable_automatic_punctuation=True,
        model="phone_call",  # מודל מותאם לשיחות טלפון
    )

    response = client.recognize(config=config, audio=audio)
    return " ".join(r.alternatives[0].transcript for r in response.results)
```

#### Azure Speech Services

ברמה ארגונית עם אפשרות לאימון מודלים מותאמים לאוצר מילים ספציפי.

```python
import azure.cognitiveservices.speech as speechsdk

def transcribe_hebrew_azure(audio_file_path: str) -> str:
    """תמלול עברית באמצעות Azure Speech."""
    speech_config = speechsdk.SpeechConfig(
        subscription="YOUR_AZURE_KEY",
        region="westeurope",  # האזור הקרוב ביותר לישראל
    )
    speech_config.speech_recognition_language = "he-IL"

    audio_config = speechsdk.AudioConfig(filename=audio_file_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    result = recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    return ""
```

לטבלת השוואה מפורטת של ספקי STT, ראו `references/hebrew-stt-models.md`.

### שלב 3: סינתזת דיבור בעברית (TTS)

#### Google Cloud TTS (מומלץ לצליל טבעי)

```python
from google.cloud import texttospeech

def synthesize_hebrew(text: str, output_path: str, voice_gender: str = "female") -> None:
    """המרת טקסט עברי לדיבור באמצעות Google Cloud TTS."""
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # קולות זמינים בעברית
    voice_map = {
        "female": "he-IL-Wavenet-A",    # נקבה, איכות גבוהה
        "male": "he-IL-Wavenet-B",      # זכר, איכות גבוהה
        "female_standard": "he-IL-Standard-A",  # נקבה, עלות נמוכה
        "male_standard": "he-IL-Standard-B",    # זכר, עלות נמוכה
    }

    voice = texttospeech.VoiceSelectionParams(
        language_code="he-IL",
        name=voice_map.get(voice_gender, "he-IL-Wavenet-A"),
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)
```

#### Amazon Polly Hebrew

משתלם מבחינת עלות לנפחי TTS גבוהים.

```python
import boto3

def synthesize_hebrew_polly(text: str, output_path: str) -> None:
    """המרת טקסט עברי לדיבור באמצעות Amazon Polly."""
    polly = boto3.client("polly", region_name="eu-west-1")

    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId="Avri",   # קול גברי עברי סטנדרטי (אין קול neural בעברית)
        Engine="standard",  # מנוע סטנדרטי (neural לא זמין לעברית)
        LanguageCode="he-IL",
    )

    with open(output_path, "wb") as out:
        out.write(response["AudioStream"].read())
```

#### Azure Neural TTS

הקולות העבריים באיכות הגבוהה ביותר, עם תמיכה ב-SSML לשליטה עדינה.

```python
import azure.cognitiveservices.speech as speechsdk

def synthesize_hebrew_azure(text: str, output_path: str) -> None:
    """המרת טקסט עברי לדיבור באמצעות Azure Neural TTS."""
    speech_config = speechsdk.SpeechConfig(
        subscription="YOUR_AZURE_KEY",
        region="westeurope",
    )
    # קולות עבריים: HilaNeural (נקבה), AvriNeural (זכר)
    speech_config.speech_synthesis_voice_name = "he-IL-HilaNeural"

    audio_config = speechsdk.AudioConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    result = synthesizer.speak_text(text)
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(f"סינתזה נכשלה: {result.reason}")
```

### שלב 4: עיצוב תפריט IVR לעסקים ישראליים

למערכות IVR ישראליות יש מוסכמות ספציפיות ששונות מהדפוס האמריקאי/האירופי.

#### ניתוב לפי שעות פעילות

שבוע העבודה בישראל הוא ראשון עד חמישי. מערכת ה-IVR חייבת להתחשב בזה:

```python
from datetime import datetime
import pytz

ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")

def get_business_status() -> dict:
    """קביעת סטטוס העסק לניתוב IVR."""
    now = datetime.now(ISRAEL_TZ)
    day = now.weekday()  # 0=שני, 6=ראשון
    hour = now.hour

    if day == 5:  # שבת
        return {
            "status": "closed",
            "message_he": "שלום, אנחנו סגורים בשבת. נחזור אליכם ביום ראשון.",
        }
    elif day == 4:  # שישי
        if 9 <= hour < 13:
            return {"status": "open", "message_he": "שלום, איך אפשר לעזור?"}
        else:
            return {"status": "closed", "message_he": "סגורים. שעות פעילות ביום שישי: 9:00-13:00."}
    elif day == 6 or day <= 3:  # ראשון עד חמישי
        if 9 <= hour < 17:
            return {"status": "open", "message_he": "שלום, איך אפשר לעזור?"}
        else:
            return {"status": "after_hours", "message_he": "שעות הפעילות: א'-ה' 9:00-17:00."}
    return {"status": "closed", "message_he": "כרגע אנחנו סגורים."}
```

#### מבנה תפריט IVR ישראלי סטנדרטי

```python
IVR_MENU = {
    "welcome": {
        "prompt_he": "שלום, הגעתם ל{company_name}.",
        "prompt_en": "For English, press 9.",
    },
    "main_menu": {
        "prompt_he": (
            "לשירות לקוחות, הקישו 1. "
            "למכירות, הקישו 2. "
            "לתמיכה טכנית, הקישו 3. "
            "למצב הזמנה, הקישו 4. "
            "לשמוע שוב, הקישו כוכבית."
        ),
        "timeout_seconds": 8,
        "max_retries": 3,
    },
}
```

#### עקרונות לפרומפטים קוליים בעברית

| כלל | דוגמה | למה |
|-----|--------|-----|
| שימוש בגוף שני רבים | "הקישו 1" ולא "תקיש 1" | טון מקצועי, נמנע ממגדר |
| פרומפטים עד 15 שניות | 3-4 אפשרויות מקסימום ברמה | מתקשרים מאבדים סבלנות |
| הכרזת שעות לפני הודעת סגור | "שעות הפעילות: א'-ה' 9-17" | מפחית ניסיונות חוזרים |
| אפשרות באנגלית | "For English, press 9" | 20% מהשיחות עשויות להעדיף אנגלית |
| "כוכבית" לכפתור * | "לחזרה, הקישו כוכבית" | מונח סטנדרטי בעברית |
| "סולמית" לכפתור # | "לאישור, הקישו סולמית" | מונח סטנדרטי בעברית |
| חזרה על התפריט ב-timeout | אחרי 8 שניות ללא קלט | מתקשרים צריכים זמן להקשיב |
| הודעה קולית מחוץ לשעות | "להשאיר הודעה, הקישו 1" | לוכד לידים מחוץ לשעות |

### שלב 5: צינור תמלול הודעות קוליות

```python
def process_voicemail(audio_path: str, caller_number: str) -> dict:
    """
    עיבוד הקלטת הודעה קולית: תמלול, סיווג וניתוב.
    """
    # שלב 1: תמלול באמצעות Whisper (הדיוק הטוב ביותר לעברית)
    transcript = transcribe_hebrew(audio_path)

    # שלב 2: זיהוי שפה (עברית, אנגלית, או מעורב)
    language = detect_voicemail_language(transcript)

    # שלב 3: סיווג כוונה
    intent = classify_voicemail_intent(transcript)

    # שלב 4: חילוץ ישויות (מספרי טלפון, מספרי הזמנה, שמות)
    entities = extract_voicemail_entities(transcript)

    # שלב 5: ניתוב לפי כוונה
    routing = route_voicemail(intent, entities)

    return {
        "caller": caller_number,
        "transcript": transcript,
        "language": language,
        "intent": intent,
        "entities": entities,
        "routing": routing,
    }

# כוונות נפוצות בהודעות קוליות בעברית
VOICEMAIL_INTENTS = {
    "callback_request": ["תתקשרו", "תחזרו", "חזרו אליי"],
    "order_inquiry": ["הזמנה", "משלוח", "חבילה", "מעקב"],
    "complaint": ["תלונה", "בעיה", "לא מרוצה"],
    "appointment": ["תור", "פגישה", "לקבוע", "לתאם"],
}
```

### שלב 6: טיפול בדיבור מעורב עברית-אנגלית

אנשי הייטק ישראלים עוברים תדיר בין עברית לאנגלית באמצע משפט (code-switching). הבוט חייב לטפל בזה בצורה חלקה.

```python
def handle_mixed_speech(audio_path: str) -> dict:
    """
    טיפול בדיבור מעורב עברית-אנגלית, נפוץ בהייטק הישראלי.
    אסטרטגיה: שימוש ב-Whisper ללא הגדרת שפה לזיהוי אוטומטי.
    """
    client = openai.OpenAI()

    with open(audio_path, "rb") as f:
        # בלי פרמטר language כדי ש-Whisper יטפל ב-code-switching
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
        )

    return {
        "full_transcript": transcript.text,
        "segments": transcript.segments,
    }

# מילים נפוצות בהייטק שנאמרות בעברית עם מבטא אנגלי
TECH_TERMS = {
    "דיפלוי": "deploy",
    "פושׁ": "push",
    "קומיט": "commit",
    "סרבר": "server",
    "באג": "bug",
    "פיצ'ר": "feature",
}
```

### שלב 7: אינטגרציה טלפונית (Twilio)

#### הגדרת Twilio עם מספרים ישראליים (+972)

```python
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from flask import Flask, request

app = Flask(__name__)

@app.route("/voice/incoming", methods=["POST"])
def handle_incoming_call():
    """טיפול בשיחה נכנסת עם תפריט IVR בעברית."""
    response = VoiceResponse()

    response.say(
        "שלום, הגעתם לשירות הלקוחות.",
        language="he-IL",
        voice="Google.he-IL-Wavenet-A",
    )

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
    response.redirect("/voice/incoming")

    return str(response)

@app.route("/voice/voicemail", methods=["POST"])
def handle_voicemail():
    """הקלטת הודעה קולית עם הנחיות בעברית."""
    response = VoiceResponse()

    response.say(
        "אנחנו כרגע לא זמינים. השאירו הודעה אחרי הצפצוף ונחזור אליכם בהקדם.",
        language="he-IL",
        voice="Google.he-IL-Wavenet-A",
    )

    response.record(max_length=120, play_beep=True)
    return str(response)
```

### שלב 8: טיפול במבטאים בעברית

לדוברי עברית בישראל רקע מגוון של מבטאים שמשפיע על דיוק זיהוי הדיבור.

| סוג מבטא | מאפיינים | השפעה על STT |
|----------|----------|-------------|
| ישראלי סטנדרטי | הגייה ישראלית מודרנית, מיזוג א/ע, ללא הבחנה ח/כ | דיוק בסיסי, כל המודלים מתמודדים היטב |
| מבטא רוסי | "ר" קשה (גרונית לשיניית), סיבילנטים רכים | עלול להפחית דיוק ב-5-10%. להוסיף רוסית כשפה חלופית |
| מבטא ערבי | שמירת צלילים לועיים (ע, ח), עיצורים אמפטיים | בדרך כלל מטופל היטב במודלים מאומנים על נתונים ישראליים |
| מבטא אתיופי | דפוסי תנועות שונים, הטעמה שונה | עשוי לדרוש אימון מודל מותאם לדיוק גבוה |
| מבטא אנגלי | תנועות אנגליות/אמריקאיות על עברית, "ר" שונה | תוצאות מעורבות. Whisper מתמודד הכי טוב |

**שיפור דיוק למבטאים לא סטנדרטיים:**
- Whisper כספק ראשי (מאומן על מבטאים מגוונים)
- ל-Google/Azure, לשקול מודלים מותאמים אישית עם נתוני אימון ספציפיים למבטא
- סף ביטחון: אם הביטחון של ה-STT מתחת ל-0.7, לבקש מהמתקשר לחזור
- להוסיף אוצר מילים ספציפי לתחום לשיפור זיהוי מונחים מקצועיים

להרצת סקריפט הדגמה לבדיקת STT בעברית:
```bash
python scripts/hebrew-stt-demo.py --help
```

## דוגמאות

### דוגמה 1: בניית IVR להזמנת מקומות במסעדה

המשתמש אומר: "צריך מערכת IVR למסעדה בתל אביב. מתקשרים צריכים להזמין מקום, לבדוק שעות, ולשמוע את התפריט."

פעולות:
1. עיצוב תפריט ראשי עם 3 אפשרויות: הזמנות (1), שעות/מיקום (2), תפריט (3)
2. הגדרת ניתוב לפי שעות: ראשון-חמישי 11:00-23:00, שישי 11:00-15:00, שבת סגור
3. הגדרת TTS בעברית עם קולות Google Wavenet
4. בניית תהליך הזמנה: איסוף תאריך, מספר סועדים, שם, אישור טלפוני
5. הגדרת הודעה קולית מחוץ לשעות עם צינור תמלול
6. אינטגרציה עם Twilio ומספר ישראלי +972

תוצאה: מערכת IVR מלאה עם פרומפטים בעברית, ניתוב מותאם לשעות פעילות, ותמלול הודעות.

### דוגמה 2: בוט קולי לשירות לקוחות

המשתמש אומר: "צריך בוט קולי שיחתי לחנות האונליין שלנו. שיטפל במצב הזמנה, החזרות, ויעביר לנציג."

פעולות:
1. הגדרת Twilio webhook לשיחות נכנסות
2. הגדרת Google Cloud STT לתמלול בזמן אמת (he-IL, מודל phone_call)
3. עיבוד טקסט מתומלל דרך LLM לזיהוי כוונה ויצירת תשובה
4. שימוש ב-Azure Neural TTS (he-IL-HilaNeural) לתגובות עבריות טבעיות
5. חיפוש הזמנה לפי מספר (DTMF או ספרות מדוברות)
6. העברה לנציג אנושי עם ניהול תור

תוצאה: בוט קולי שמבין עברית מדוברת, מספק מידע על הזמנות, ומעביר לנציג בצורה חלקה.

### דוגמה 3: שירות תמלול הודעות קוליות

המשתמש אומר: "רוצה לתמלל הודעות קוליות שנשארות על הקו העסקי ולשלוח אותן כטקסט למחלקה הרלוונטית."

פעולות:
1. הגדרת Twilio recording webhook ללכידת אודיו
2. הקמת צינור תמלול מבוסס Whisper לעברית
3. סיווג כוונת ההודעה (בקשת חזרה, תלונה, שאלה על הזמנה)
4. חילוץ ישויות (מספרי טלפון, מספרי הזמנה, שמות)
5. ניתוב הטקסט המתומלל ב-SMS/WhatsApp למחלקה הרלוונטית

תוצאה: צינור אוטומטי מהודעה קולית לטקסט שמתמלל הודעות בעברית ומנתב לפי כוונה.

## משאבים מצורפים

### סקריפטים
- `scripts/hebrew-stt-demo.py` -- סקריפט הדגמה לזיהוי דיבור בעברית באמצעות OpenAI Whisper. מייצר קובץ אודיו לדוגמה ומתמלל אותו בחזרה לטקסט. הרצה: `python scripts/hebrew-stt-demo.py --help`

### חומרי עזר
- `references/hebrew-stt-models.md` -- טבלת השוואה של מודלים לזיהוי דיבור בעברית (Whisper, Google Cloud STT, Azure Speech) עם בנצ'מרקים של דיוק, זמן תגובה, תמחור והמלצות לפי תרחיש. יש לעיין בו בעת בחירת ספק STT.
- `references/ivr-design-patterns.md` -- תבניות נפוצות של תהליכי IVR לעסקים ישראליים, כולל מסעדות, מרפאות, שירות לקוחות ומשרדי ממשלה. יש לעיין בו בעת עיצוב מבנה תפריט IVR.

## מלכודות נפוצות

- מנועי זיהוי דיבור בעברית מתקשים עם סלנג ישראלי ("יאללה", "סבבה", "בלאגן") ומילות שאלה מערבית, רוסית ואמהרית. סוכנים עלולים לא להתחשב בקלט רב-לשוני בבוטים קוליים.
- מערכות IVR טלפוניות ישראליות חייבות להציע עברית כשפת ברירת מחדל, ואנגלית כמשנית. סוכנים עלולים לבנות בוטים קוליים עם אנגלית כברירת מחדל, מה שמתסכל מתקשרים דוברי עברית.
- המרת טקסט לדיבור (TTS) בעברית דורשת ניקוד נכון לביטוי תקין. ללא ניקוד, מילים דו-משמעיות כמו "דבר" עלולות להיקרא "דָּבָר" (thing) או "דַּבֵּר" (speak).
- מספרי טלפון ישראליים באורך משתנה ב-IVR: קווים נייחים 9 ספרות (0X-XXXXXXX), נייד 10 ספרות (05X-XXXXXXX). בוטים קוליים חייבים לקבל את שני הפורמטים.
- רמות רעשי רקע בסביבות ישראליות טיפוסיות (בתי קפה, משרדים פתוחים, תחבורה ציבורית) גבוהות מהממוצע העולמי. סף הביטחון בבוטים קוליים צריך להיות נמוך יותר כדי להימנע מחזרות מרובות.

## פתרון בעיות

### בעיה: "תמלול עברי מחזיר טקסט בערבית"
סיבה: מודל ה-STT מזהה בטעות עברית כערבית עקב טווחי תווים משותפים או פונמות דומות.
פתרון: להגדיר במפורש את השפה ל-"he-IL" (Google/Azure) או `language="he"` (Whisper). ב-Whisper, הוספת רמז בעברית גם עוזרת: `prompt="שלום, ברוכים הבאים"`.

### בעיה: "קול ה-TTS נשמע רובוטי בעברית"
סיבה: שימוש בקולות Standard ולא Neural/Wavenet.
פתרון: לעבור לקולות neural: Google Wavenet (he-IL-Wavenet-A/B) או Azure Neural (he-IL-HilaNeural). Amazon Polly Hebrew מציע רק קול סטנדרטי (Avri, גברי) ללא אפשרות neural. קולות neural יקרים יותר אבל טבעיים בהרבה.

### בעיה: "תפריט IVR עושה timeout לפני שהמתקשר מגיב"
סיבה: timeout קצר מדי, במיוחד למתקשרים מבוגרים או פרומפטים ארוכים בעברית.
פתרון: להגדיל timeout ל-8-10 שניות. להוסיף אפשרות "לשמוע שוב, הקישו כוכבית". לקחת בחשבון שפרומפטים בעברית עלולים להיות ארוכים יותר מאנגלית.

### בעיה: "Twilio לא מוצא מספרים ישראליים"
סיבה: הזמינות של מספרים ישראליים משתנה. ל-Twilio מלאי מוגבל של +972 בהשוואה למספרים אמריקאיים.
פתרון: לחפש מספרים מקומיים וגם חינמיים. לשקול Vonage כחלופה עם זמינות טובה יותר למספרים ישראליים. לנפחים גבוהים, ליצור קשר עם Twilio sales. אפשר גם לנייד מספרים ישראליים קיימים ל-Twilio.
