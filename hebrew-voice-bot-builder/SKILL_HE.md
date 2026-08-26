---
name: hebrew-voice-bot-builder
description: >-
  Build Hebrew voice bots and IVR (Interactive Voice Response) systems with
  speech-to-text, text-to-speech, and telephony integration for Israeli
  businesses. Use when user asks to "build a Hebrew voice bot", "create an IVR
  in Hebrew", "Hebrew speech-to-text", "binui bot koli b'ivrit", "maarechet
  maane koli", "zihui dibur b'ivrit", or "Twilio Israel". Covers OpenAI
  Whisper Hebrew, Google Cloud STT/TTS he-IL, Azure Speech Services,
  IVR menu design for Sunday-Thursday business hours, voicemail
  transcription, Hebrew accent handling, and +972 phone integration via Twilio
  and Vonage. Do NOT use for text-based chatbots (use hebrew-chatbot-builder),
  Hebrew NLP without voice (use hebrew-nlp-toolkit), or SMS messaging (use
  israeli-sms-gateway).
license: MIT
---

# בונה בוטים קוליים בעברית

בניית בוטים קוליים ומערכות מענה קולי (IVR) ברמת פרודקשן לעסקים ישראליים. הסקיל מכסה את כל צינור הקול: זיהוי דיבור (STT), סינתזת דיבור (TTS), עיצוב תפריטי IVR, אינטגרציה טלפונית, ואתגרים ייחודיים לעברית כמו מבטאים שונים ודיבור מעורב עברית-אנגלית.

## הוראות

> **קוד שפה: ב-STT של גוגל עברית היא `iw-IL`, וב-TTS היא `he-IL`.** טבלת השפות
> הנתמכות של Speech-to-Text מציגה עברית כ-`iw-IL` (קוד ISO הישן לעברית), בעוד
> שרשימת הקולות של Text-to-Speech משתמשת ב-`he-IL` (למשל `he-IL-Wavenet-A`).
> העבירו לכל צד את הקוד המתועד שלו, ואל תניחו שקוד אחד עובד לשניהם.

### שלב 1: בחירת ארכיטקטורה

לפני הבנייה, צריך להחליט על הארכיטקטורה בהתאם לתרחיש:

| ארכיטקטורה | מתאים ל | רכיבים |
|------------|---------|--------|
| IVR (מקלדת) | ניווט תפריטים, קווי תשלום, קביעת תורים | TTS + DTMF + טלפוניה |
| בוט קולי (שיחתי) | שירות לקוחות, מצב הזמנה, שאלות נפוצות | STT + LLM + TTS + טלפוניה |
| תמלול הודעות קוליות | טיפול בשיחות שלא נענו, ניתוב הודעות | STT + צינור התראות |
| היברידי | תהליכים מורכבים עם קלט קולי וגם מקלדת | STT + TTS + DTMF + טלפוניה |

**החלטות מרכזיות:**
- **ספק STT**: OpenAI `gpt-4o-transcribe` או `gpt-4o-mini-transcribe` (השהיה נמוכה יותר מ-`whisper-1`, זמין דרך OpenAI Realtime API לסטרימינג), `whisper-large-v3-turbo` ל-self-host, וריאציות מותאמות-עברית של ivrit-ai (`ivrit-ai/whisper-large-v3-turbo-ct2`) כמודל פתוח שאומן במיוחד על עברית, Google Cloud STT (השהיה נמוכה; עברית רצה על Chirp, בקוד `iw-IL`), Azure Speech (תכונות ארגוניות), ו-ElevenLabs Scribe v2 שמציין עברית (heb) ברמת "Good (מעל 10% ועד 20% WER)" עם וריאנט זמן אמת של בערך 150ms. כדאי לקרוא את רמת ה-WER בכנות: עברית שם שתי דרגות מתחת לאנגלית, אז מדדו על אודיו השיחות שלכם ולא לפי הכותרת השיווקית. ה-API הישן `whisper-1` עדיין נתמך אבל `gpt-4o-transcribe` הוא ברירת המחדל הנוכחית לעברית.
- **ספק TTS, פיצול לפי תרחיש שימוש**:
  - **זמן אמת / streaming (סוכן קולי, IVR, שיחה חיה)**: OpenAI Realtime API, speech-to-speech רב-לשוני שתומך בעברית באופן טבעי דרך WebRTC/WebSocket/SIP, ברירת המחדל של 2026 ל-turn-taking של פחות מ-500ms. מודל ה-GA הנוכחי הוא `gpt-realtime-2.1` (ו-`gpt-realtime-2.1-mini` לשכבה הקטנה). שני שמות מודל שכדאי להימנע מהם: `gpt-realtime` הוצא משימוש ב-20.07.2026 עם כיבוי סופי ב-20.01.2027 (המחליף הוא `gpt-realtime-2.1`), והגרסה `gpt-4o-realtime-preview` הוסרה מה-API ב-07.05.2026. המודל `gpt-realtime-1.5` עדיין חי. אפשרויות נוספות לזמן אמת: ElevenLabs `eleven_v3_conversational` (בערך 280ms, ועברית נמצאת ברשימת השפות של v3, כך שזה מסלול אמיתי לעברית בזמן אמת), Inworld Realtime TTS-2 ו-TTS-2 Flash (Inworld מפרסמים "200+ שפות" אבל לא מונים עברית בשום מקום בתיעוד, אז כדאי להתייחס לעברית שם כלא נבדקה ולאמת עם אודיו משלכם; השמות הישנים TTS-1 ו-TTS-1.5 כבר לא מופיעים), ו-Deepdub Phantom X 3.2 של החברה הישראלית Deepdub. אין ללכת ל-ElevenLabs `eleven_flash_v2_5` בשביל עברית: רשימת השפות שלו היא 29 השפות של Multilingual v2 בתוספת הונגרית, נורווגית ווייטנאמית, כלומר עברית חסרה שם לגמרי ולא רק חלשה.
  - **Offline / איכות מקסימלית (אודיובוקים, השמעת הודעות, יצירה בבאטץ׳)**: ElevenLabs `eleven_v3`, איכות העברית הכי טובה ש-ElevenLabs מציעה, תומך בעברית בין 70+ שפות, אבל **אין WebSocket / streaming API**, REST בלבד. Deepdub Phantom X 3.2 משרת גם את המסלול הזה עם שליטה ברגש.
  - **חלופות וגיבוי**: Azure Neural TTS (`he-IL-HilaNeural`, `he-IL-AvriNeural`), Google Cloud TTS Wavenet (`he-IL-Wavenet-A/B`). **Amazon Polly אינו תומך בעברית** (אין locale בשם he-IL, אין קול עברי מכל מנוע, הקול "Avri" שייך ל-Azure ולא ל-Polly), לכן אין לנתב עברית דרך Polly. ElevenLabs Multilingual v2 אינו כולל עברית: 29 השפות המתועדות שלו הן en, ja, zh, de, hi, fr, ko, pt, it, es, id, nl, tr, fil, pl, sv, bg, ro, ar, cs, el, fi, hr, ms, sk, da, ta, uk ו-ru. עברית מופיעה רק ברשימת השפות של Eleven v3, אז נתבו עברית ל-v3 (או ל-Azure/Google שלמעלה) ולא ל-Multilingual v2.
- **טלפוניה**: גם Twilio וגם Vonage מוכרים מספרים ישראליים. Twilio מפרסם תמחור שיחות לישראל (מספר מקומי, סלולרי וחינם), ואילו Vonage לא מפרסם תיעוד מקביל למספרים ישראליים, אז כדאי להשוות הצעות מחיר בעצמכם ולא לסמוך על דירוג. ניידות מספרים קיימת בשוק הישראלי, אבל כדאי לוודא מול המפעיל שהמספר הספציפי שלכם ניתן להעברה לספק שבחרתם לפני שמתחייבים.
- **הקלטת שיחות וחתימת קול (voiceprint)**: להשמיע "השיחה מוקלטת" בתחילת השיחה. זו פרקטיקה מקובלת בשיחות שירות בישראל, והסקיל הזה לא מציג אותה כחובה סטטוטורית מצוטטת (גרסה קודמת כן הציגה, והמקור לא החזיק). חתימת קול היא לא אותו נכס כמו קובץ ההקלטה: כדאי לשמור אותה בטבלה נפרדת, עם מפתח מחיקה לכל מתקשר, כך שאפשר למחוק אותה לבד בלי לגעת באודיו ובתמלול. לוודא מול איש מקצוע מוסמך אילו חובות חלות על העסק לפני עלייה לאוויר.
- **אירוח**: פונקציות ענן לנפח נמוך, שרתים ייעודיים לנפח גבוה

### שלב 2: זיהוי דיבור בעברית (STT)

#### OpenAI Whisper (כדאי לדיוק)

OpenAI מתמודד היטב עם דיבור מעורב עברית-אנגלית שנפוץ בסביבות הייטק ישראליות.

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
- איכות אודיו חשובה: קצב דגימה 16kHz+, ערוץ מונו, פורמט WAV. אין להקליט ל-FLAC או ל-OGG אם היעד הוא OpenAI: ה-API לתמלול מקבל רק mp3, mp4, mpeg, mpga, m4a, wav ו-webm, ודוחה את הקובץ אחרי ההעלאה
- גודל קובץ מקסימלי: 25MB. להקלטות ארוכות, לחלק לסגמנטים

#### Google Cloud Speech-to-Text

זמן תגובה נמוך יותר מ-Whisper, מתאים לבוטים קוליים בזמן אמת.

```python
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
import os

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]

# עברית ב-Google STT קיימת רק על משפחת Chirp והיא אזורית, ו-Chirp 2 מתועד כזמין
# אך ורק ב-Speech-to-Text API V2. לכן עברית חייבת לעבור דרך speech_v2 מול נקודת
# קצה אזורית, ולא דרך הלקוח הגלובלי speech_v1. בטבלת השפות הנתמכות iw-IL מופיע
# על chirp ו-chirp_2 ב-europe-west4 וב-asia-southeast1, ועל chirp_3 במולטי-אזורים
# eu ו-us. אין מודל phone_call או telephony לעברית, אז אין לצפות לשיפור דיוק
# שמותאם לאודיו טלפוני; צריך למדוד על אודיו שיחות אמיתי של 8kHz.
LOCATION = "europe-west4"
MODEL = "chirp_2"


def transcribe_hebrew_google(audio_content: bytes) -> str:
    """תמלול עברית באמצעות Google Cloud STT V2 (Chirp)."""
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint=f"{LOCATION}-speech.googleapis.com",
        )
    )

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["iw-IL"],  # גוגל מתעדת עברית ב-STT ככה, לא he-IL
        model=MODEL,
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/_",
        config=config,
        content=audio_content,
    )

    response = client.recognize(request=request)
    return " ".join(r.alternatives[0].transcript for r in response.results)
```

**לסטרימינג בעברית צריך מודל אחר מזה שלמעלה.** Chirp 2 מונה במפורש את השפות
ש-`Speech.StreamingRecognize` שלו מקבל, ועברית לא נמצאת ברשימה (יש בה 17 לוקאלים:
הווריאנטים של סינית, אנגלית, צרפתית, גרמנית, איטלקית, יפנית, קוריאנית, פורטוגזית
וספרדית). המתודות `Recognize` ו-`BatchRecognize` של Chirp 2 כן עובדות לעברית, וזה
מה שהקוד למעלה משתמש בו. לסטרימינג בעברית צריך **`chirp_3` במולטי-אזור `eu` או
`us`**: ב-Chirp 3 מתועד ש-StreamingRecognize נתמך, וטבלת הלוקאלים שלו כוללת את
`Hebrew (Israel) iw-IL` בבשלות **Preview**. שתי מסקנות: להגדיר `LOCATION = "us"`
(או `"eu"`) ו-`MODEL = "chirp_3"` לנתיב הסטרימינג, ולהתייחס ל-Preview כ-Preview,
כלומר לקבע התנהגות בבדיקות ולהחזיק נתיב גיבוי. מי שלא רוצה תלות ב-Preview יכול
להריץ את השיחה בבקשות `Recognize` קצרות על גבולות של משפטים, או לעבור לספק שבדקתם
שהסטרימינג העברי שלו עובד (OpenAI Realtime או ElevenLabs Scribe v2 Realtime).

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

#### Google Cloud TTS (כדאי לצליל טבעי)

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

#### Amazon Polly עברית: לא זמין

Amazon Polly **אינו** תומך בעברית. אין locale בשם `he-IL` ברשימת השפות הנתמכות של Polly ואין קול עברי מכל מנוע (סטנדרטי או neural). הקול "Avri" שחלק מהמדריכים מייחסים ל-Polly הוא למעשה הקול של **Azure** `he-IL-AvriNeural`, ולא קול של Polly. לגיבוי TTS ענני זול בעברית, השתמשו ב-Google Cloud TTS (`he-IL-Wavenet-A/B`) או ב-Azure Neural TTS למטה במקום Polly.

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
| אפשרות באנגלית | "For English, press 9" | חלק מהמתקשרים יעדיפו אנגלית; מדדו את שיעור הבחירה בקו שלכם לפני שמתכננים את הענף |
| "כוכבית" לכפתור * | "לחזרה, הקישו כוכבית" | מונח סטנדרטי בעברית |
| "סולמית" לכפתור # | "לאישור, הקישו סולמית" | מונח סטנדרטי בעברית |
| חזרה על התפריט ב-timeout | אחרי 8 שניות ללא קלט | מתקשרים צריכים זמן להקשיב |
| הודעה קולית מחוץ לשעות | "להשאיר הודעה, הקישו 1" | לוכד לידים מחוץ לשעות |

### שלב 5: צינור תמלול הודעות קוליות

```python
# הערה: הבלוק הזה הוא שלד של pipeline, לא מודול שרץ כמו שהוא.
# הפונקציות detect_voicemail_language(), classify_voicemail_intent(),
# extract_voicemail_entities() ו-route_voicemail() הן הלוגיקה העסקית שלכם והן
# בכוונה לא ממומשות כאן: חילוץ ישויות וניתוב תלויים ב-CRM ובשמות התורים שלכם.
# צריך לממש אותן לפני הרצה, אחרת הקריאה הראשונה תזרוק NameError.
# הגרסה האנגלית של הסקיל מכילה מימוש לדוגמה של שתי הראשונות.
def process_voicemail(audio_path: str, caller_number: str) -> dict:
    """
    עיבוד הקלטת הודעה קולית: תמלול, סיווג וניתוב.
    """
    # שלב 1: תמלול באמצעות Whisper
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
def detect_segment_language(text: str) -> str:
    """סיווג סגמנט לפי כתב: בלוק עברי U+0590-U+05FF מול לטיני."""
    hebrew = sum(1 for ch in text if "\u0590" <= ch <= "\u05FF")
    latin = sum(1 for ch in text if ch.isascii() and ch.isalpha())
    if hebrew and latin:
        return "mixed"
    return "he" if hebrew else ("en" if latin else "unknown")


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

    segments = []
    # transcript.segments מחזיק מודלים של pydantic מסוג TranscriptionSegment,
    # לא מילונים. הגישה segment["text"] זורקת TypeError ו-segment.get("text")
    # זורקת AttributeError בכל גרסת SDK עדכנית של openai, אז קוראים תכונות.
    # חשוב גם מפני שהרשימה הגולמית אינה ניתנת לסריאליזציה ל-JSON.
    for segment in transcript.segments:
        text = segment.text
        segments.append({
            "text": text,
            "language": detect_segment_language(text),
            "start": segment.start,
            "end": segment.end,
        })

    return {
        "full_transcript": transcript.text,
        "segments": segments,
    }

# מילים נפוצות בהייטק שנאמרות בעברית עם מבטא אנגלי
TECH_TERMS = {
    "דיפלוי": "deploy",
    "פוש": "push",
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
        # הפרמטר language מגדיר את מנוע זיהוי הדיבור של Twilio, ולכן ב-gather
        # של DTMF בלבד (num_digits, בלי input="speech") הוא לא עושה כלום. אם
        # עוברים ל-input="speech", התיעוד של <Gather> מתעד עברית כ-`iw-IL` ולא
        # כ-`he-IL`, ומציין שהיא לא נתמכת ב-v2 STT הגלובלי של גוגל. הקול
        # `Google.he-IL-Wavenet-A` למטה הוא קול של <Say> ותקין כמו שהוא:
        # ל-<Say> ול-<Gather> יש אוצר תגיות שונה.
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

| סוג מבטא | מאפיינים | מה לבדוק |
|----------|----------|----------|
| ישראלי סטנדרטי | הגייה ישראלית מודרנית, מיזוג א/ע, ללא הבחנה ח/כ | סט הבסיס שלכם |
| מבטא רוסי | "ר" קשה (גרונית לשיניית), סיבילנטים רכים | האם רמז שפה רוסית עוזר או מזיק על האודיו שלכם |
| מבטא ערבי | שמירת צלילים לועיים (ע, ח), עיצורים אמפטיים | האם הצלילים הלועיים נופלים או מוחלפים בתמלול |
| מבטא אתיופי | דפוסי תנועות שונים, הטעמה שונה | האם גבולות המילים שורדים את דפוס ההטעמה השונה |
| מבטא אנגלי | תנועות אנגליות/אמריקאיות על עברית, "ר" שונה | האם המודל עובר שפה באמצע מילה |

**אף ספק לא מפרסם WER בעברית לפי מבטא, ולכן הטבלה הזאת בכוונה לא מדרגת כלום.** גרסאות קודמות טענו אילו מבטאים נפגעים ואיזה מודל מתמודד הכי טוב; לטענות האלה לא היה מקור. אספו 20-30 אמירות לכל קבוצת מבטא מהמתקשרים שלכם ומדדו עם סקריפט הדמו המצורף לפני שבוחרים ספק.

**שיפור דיוק למבטאים לא סטנדרטיים:**
- למדוד לפני שבוחרים ספק ראשי; מודל שאומן על מבטאים מגוונים הוא סיבה לבדוק אותו, לא תוצאה
- ל-Google/Azure, לשקול מודלים מותאמים אישית עם נתוני אימון ספציפיים למבטא
- להגדיר סף ביטחון ולבקש חזרה מתחתיו, אבל לגזור את המספר מההקלטות שלכם ולא להעתיק אותו (ראו את המלכודת על ספים). סף שנכון למשרד שקט לא נכון לאוטובוס
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
2. הגדרת Google Cloud STT V2 לתמלול בזמן אמת. עברית היא `iw-IL`, וסטרימינג בעברית דורש `chirp_3` במולטי-אזור `eu` או `us` (Preview): ב-`chirp_2` עברית לא מופיעה ברשימת StreamingRecognize. אין מודל ייעודי לשיחות טלפון בעברית
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

### דוגמה 4: טיפול בדיבור מעורב עברית-אנגלית

המשתמש אומר: "המתקשרים שלנו מערבבים לעיתים קרובות עברית ואנגלית, במיוחד מונחים טכניים. איך מטפלים בזה?"

פעולות:
1. להגדיר את Whisper ללא פרמטר שפה קבוע (הזיהוי האוטומטי מטפל בהחלפת קוד)
2. לממש עיבוד-לאחר לנרמול מונחים טכניים באנגלית במבטא עברי
3. לבנות אוצר מילים מותאם של מונחי טכנולוגיה עברית-אנגלית (deploy, push, server, bug)
4. לבדוק עם אודיו מעורב לדוגמה באמצעות סקריפט הדמו
5. להגדיר ספי ביטחון ולבקש מהמתקשר לחזור על עצמו כשהביטחון נמוך

תוצאה: בוט קולי שמתמלל נכון דיבור מעורב עברית-אנגלית הנפוץ בסביבות הייטק בישראל.

## משאבים מצורפים

### סקריפטים
- `scripts/hebrew-stt-demo.py` -- סקריפט הדגמה לזיהוי דיבור בעברית דרך OpenAI Whisper. מייצר קובץ אודיו לדוגמה ומתמלל אותו בחזרה לטקסט. הרצה: `python scripts/hebrew-stt-demo.py --help`

### חומרי עזר
- `references/hebrew-stt-models.md` -- טבלת השוואה של מודלים לזיהוי דיבור בעברית (Whisper, Google Cloud STT, Azure Speech) עם בנצ'מרקים של דיוק, זמן תגובה, תמחור והמלצות לפי תרחיש. עיינו בו בעת בחירת ספק STT.
- `references/ivr-design-patterns.md` -- תבניות נפוצות של תהליכי IVR לעסקים ישראליים, כולל מסעדות, מרפאות, שירות לקוחות ומשרדי ממשלה. עיינו בו בעת עיצוב מבנה תפריט IVR.

## מלכודות נפוצות

- מנועי זיהוי דיבור בעברית מתקשים עם סלנג ישראלי ("יאללה", "סבבה", "בלאגן") ומילות שאלה מערבית, רוסית ואמהרית. סוכנים עלולים לא להתחשב בקלט רב-לשוני בבוטים קוליים.
- מערכות IVR טלפוניות ישראליות חייבות להציע עברית כשפת ברירת מחדל, ואנגלית כמשנית. סוכנים עלולים לבנות בוטים קוליים עם אנגלית כברירת מחדל, מה שמתסכל מתקשרים דוברי עברית.
- TTS בעברית לא דורש ניקוד, וכל מחרוזת עברית בסקיל הזה כתובה בכוונה בלי ניקוד: הקולות הנוירליים he-IL של גוגל ושל Azure מנקדים בעצמם, ולכן קלט לא מנוקד הוא המצב הרגיל. מה שהניקוד כן נותן זה פירוק דו-משמעות בהומוגרפים. המילה "דבר" יכולה להיקרא `דָּבָר` או `דַּבֵּר`, אז אם הומוגרף נופל על מילה שמשנה את משמעות האפשרות בתפריט, מנקדים רק את המילה הזאת או כותבים את המשפט מחדש. תמיד להאזין לפלט לפני עלייה לאוויר במקום להניח התנהגות כזאת או אחרת.
- מספרי טלפון ישראליים באורך משתנה ב-IVR: קווים נייחים 9 ספרות (0X-XXXXXXX), נייד 10 ספרות (05X-XXXXXXX). בוטים קוליים חייבים לקבל את שני הפורמטים.
- אל תעתיקו סף ביטחון ממדריך, כולל מגרסאות קודמות של הסקיל הזה שטענו שרעש הרקע בישראל גבוה מהממוצע העולמי. אין לנו מקור להשוואה הזאת. קבעו את הסף לפי מדידות על הקו שלכם: הקליטו שיחות אמיתיות מהסביבות שהמתקשרים שלכם באמת נמצאים בהן (בתי קפה, משרדים פתוחים ותחבורה ציבורית הם המקרים הקשים הנפוצים כאן) וכוונו מול אוסף ההקלטות הזה.
- **ElevenLabs `eleven_v3` עובד רק על REST**, אין WebSocket / streaming API נכון למאי 2026. סוכנים שיבחרו ב-v3 בגלל "איכות עברית הכי טובה" וינסו לחבר אותו לסוכן קולי חי ייתקלו בהשהיה לא קבילה. השתמשו ב-OpenAI Realtime API, Inworld Realtime TTS-2 או Deepdub Phantom X 3.2 לזמן אמת בעברית; שמרו את v3 לתרחישי offline / batch / השמעת תוכן מוקלט.
- נוף ה-TTS בעברית משתנה במהירות (Deepdub Phantom X יצא במרץ 2026; Inworld החליפו את קו TTS-1 ב-Realtime TTS-2 במהלך 2026 והשמות הישנים נעלמו מהתיעוד). אמתו תמיכה בעברית של כל ספק בזמן הבנייה, ובדקו את רשימת השפות המפורטת של הספק ולא מספר כולל בכותרת: הצהרה על "200+ שפות" שלא מזכירה עברית אינה ראיה לתמיכה בעברית.


## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| OpenAI Whisper (זיהוי דיבור עברית) | https://github.com/openai/whisper | המרת דיבור לטקסט רב-לשונית כולל עברית, גדלי מודלים, דיוק |
| Google Cloud Speech-to-Text | https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages | תמיכה בעברית (מופיעה כ-`iw-IL`), זיהוי סטרימינג, תמחור |
| Azure AI Speech (עברית) | https://learn.microsoft.com/he-il/azure/ai-services/speech-service/language-support | קולות STT/TTS בעברית, רשימת קולות נוירליים |
| מודלים בעברית ב-HuggingFace | https://huggingface.co/models?language=he | מודלים פתוחים לזיהוי דיבור/המרה לדיבור בעברית |
| ivrit.ai (קורפוס דיבור בעברית) | https://www.ivrit.ai | קורפוס דיבור עברי פתוח, מודלי ASR מאומנים מראש |
| תיעוד streaming / WebSocket של ElevenLabs | https://elevenlabs.io/docs/api-reference/streaming | אילו מודלים תומכים ב-streaming (v3 לא, Flash v2.5 כן) |
| Deepdub (ישראלי) | https://deepdub.ai | Phantom X 3.2, קול AI בזמן אמת עם תמיכה ילידית בעברית ו-eTTS רגשי |
| Inworld TTS | https://inworld.ai/tts | Realtime TTS-2 ו-TTS-2 Flash. Inworld מפרסמים 200+ שפות אבל לא מונים עברית; צריך לאמת עם אודיו משלכם. השמות TTS-1 ו-TTS-1.5 כבר לא מופיעים בתיעוד |

## פתרון בעיות

### בעיה: "תמלול עברי מחזיר טקסט בערבית"
סיבה: מודל ה-STT מזהה בטעות עברית כערבית עקב טווחי תווים משותפים או פונמות דומות.
פתרון: להגדיר את השפה במפורש. ה-STT של גוגל רוצה `iw-IL` (ולא `he-IL`, שלא מופיע בכלל בטבלת השפות הנתמכות שלו); ה-TTS של גוגל ו-Azure רוצים `he-IL`; ב-OpenAI מעבירים `language="he"`. ב-Whisper, הוספת רמז בעברית גם עוזרת: `prompt="שלום, ברוכים הבאים"`.

### בעיה: "קול ה-TTS נשמע רובוטי בעברית"
סיבה: שימוש בקולות Standard ולא Neural/Wavenet.
פתרון: לעבור לקולות neural: Google Wavenet (he-IL-Wavenet-A/B) או Azure Neural (he-IL-HilaNeural). (Amazon Polly אינו תומך בעברית כלל, ולכן אינו אפשרות.) קולות neural יקרים יותר אבל טבעיים בהרבה.

### בעיה: "תפריט IVR עושה timeout לפני שהמתקשר מגיב"
סיבה: timeout קצר מדי, במיוחד למתקשרים מבוגרים או פרומפטים ארוכים בעברית.
פתרון: להגדיל timeout ל-8-10 שניות. להוסיף אפשרות "לשמוע שוב, הקישו כוכבית". לקחת בחשבון שפרומפטים בעברית עלולים להיות ארוכים יותר מאנגלית.

### בעיה: "Twilio לא מוצא מספרים ישראליים"
סיבה: הזמינות של מספרים ישראליים משתנה. ל-Twilio מלאי מוגבל של +972 בהשוואה למספרים אמריקאיים.
פתרון: לחפש מספרים מקומיים וגם חינמיים. שווה לבקש הצעת מחיר גם מ-Vonage, אבל אף אחד מהספקים לא מפרסם מלאי מספרים ישראלי להשוואה, אז כדאי לבדוק זמינות בפועל בעצמכם ולא לסמוך על דירוג. לנפחים גבוהים, ליצור קשר עם Twilio sales. אפשר גם לנייד מספרים ישראליים קיימים ל-Twilio.
