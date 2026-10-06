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
- **ספק STT**: ב-OpenAI, `gpt-transcribe` לאודיו מוקלט ו-`gpt-live-transcribe` לסטרימינג (רק בסשנים של Realtime transcription, לא ב-endpoint של קבצים). ב-26.08.2026 OpenAI הוציאו משימוש את `whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe` ו-`gpt-4o-transcribe-diarize`, וכולם נכבים ב-26.02.2027, אז לא מתחילים עליהם פיתוח חדש. `whisper-large-v3-turbo` ל-self-host, וריאציות מותאמות-עברית של ivrit-ai (`ivrit-ai/whisper-large-v3-turbo-ct2`) כמודל פתוח שאומן במיוחד על עברית, Google Cloud STT (עברית רצה על Chirp בלבד, בקוד `iw-IL`), Azure Speech (תכונות ארגוניות), ו-ElevenLabs Scribe v2 שמציין עברית (heb) ברמת "Good (מעל 10% ועד 20% WER)" עם וריאנט זמן אמת של בערך 150ms. כדאי לקרוא את רמת ה-WER בכנות: עברית שם שתי דרגות מתחת לאנגלית, אז מדדו על אודיו השיחות שלכם ולא לפי הכותרת השיווקית.
- **ספק TTS, פיצול לפי תרחיש שימוש**:
  - **זמן אמת / streaming (סוכן קולי, IVR, שיחה חיה)**: OpenAI Realtime API, speech-to-speech רב-לשוני שתומך בעברית באופן טבעי דרך WebRTC/WebSocket/SIP, ברירת המחדל של 2026 ל-turn-taking של פחות מ-500ms. מודל ה-GA הנוכחי הוא `gpt-realtime-2.1` (ו-`gpt-realtime-2.1-mini` לשכבה הקטנה). שני שמות מודל שכדאי להימנע מהם: `gpt-realtime` הוצא משימוש ב-20.07.2026 עם כיבוי סופי ב-20.01.2027 (המחליף הוא `gpt-realtime-2.1`), והגרסה `gpt-4o-realtime-preview` הוסרה מה-API ב-07.05.2026. המודל `gpt-realtime-1.5` עדיין חי. אפשרויות נוספות לזמן אמת: ElevenLabs `eleven_v4_turbo` (בערך 100ms, ועברית ברשימת השפות של v4; את `eleven_v3_conversational` ElevenLabs מגדירים עכשיו דור קודם), Inworld `inworld-tts-2` ו-`inworld-tts-2-flash` (עברית `he` רשומה כשפת Tier 1; מודלי 1.5 הוצאו משימוש), והחברה הישראלית Deepdub (מזהה המודל ב-API הוא `dd-etts-3.0`, ועברית `he-IL` מופיעה בטבלת השפות של ה-API). אין ללכת ל-ElevenLabs `eleven_flash_v2_5` בשביל עברית: רשימת השפות שלו היא 29 השפות של Multilingual v2 בתוספת הונגרית, נורווגית ווייטנאמית, כלומר עברית חסרה שם לגמרי ולא רק חלשה.
  - **Offline / איכות מקסימלית (אודיובוקים, השמעת הודעות, יצירה בבאטץ׳)**: ElevenLabs `eleven_v4` (עברית ברשימת 90+ השפות שלו; `eleven_v3` מוגדר עכשיו דור קודם). v3 ו-v4 לא נתמכים ב-WebSocket של Text to Speech (`stream-input`); v4 מוגש דרך Text to Dialogue API, ונתיב ה-WebSocket שלהם הוא ה-WebSocket של Text to Dialogue (`wss://api.elevenlabs.io/v1/text-to-dialogue/stream-input`). גם Deepdub משרתת את המסלול הזה עם שליטה ברגש.
  - **חלופות וגיבוי**: Azure Neural TTS (`he-IL-HilaNeural`, `he-IL-AvriNeural`), Google Cloud TTS Wavenet (`he-IL-Wavenet-A/B`). **Amazon Polly אינו תומך בעברית** (אין locale בשם he-IL, אין קול עברי מכל מנוע, הקול "Avri" שייך ל-Azure ולא ל-Polly), לכן אין לנתב עברית דרך Polly. ElevenLabs Multilingual v2 אינו כולל עברית: 29 השפות המתועדות שלו הן en, ja, zh, de, hi, fr, ko, pt, it, es, id, nl, tr, fil, pl, sv, bg, ro, ar, cs, el, fi, hr, ms, sk, da, ta, uk ו-ru. עברית מופיעה ברשימות השפות של Eleven v3 ו-v4, אז נתבו עברית ל-v4 או ל-v3 (או ל-Azure/Google שלמעלה) ולא ל-Multilingual v2.
- **טלפוניה**: גם Twilio וגם Vonage מוכרים מספרים ישראליים. Twilio מפרסם תמחור שיחות לישראל (מספר מקומי, סלולרי וחינם), ואילו Vonage לא מפרסם תיעוד מקביל למספרים ישראליים, אז כדאי להשוות הצעות מחיר בעצמכם ולא לסמוך על דירוג. ניידות מספרים קיימת בשוק הישראלי, אבל כדאי לוודא מול המפעיל שהמספר הספציפי שלכם ניתן להעברה לספק שבחרתם לפני שמתחייבים.
- **הקלטת שיחות וחתימת קול (voiceprint)**: להשמיע "השיחה מוקלטת" בתחילת השיחה. זו פרקטיקה מקובלת, לא חובה סטטוטורית מצוטטת. [חוק האזנת סתר](https://he.wikisource.org/wiki/חוק_האזנת_סתר) מגדיר "האזנת סתר" כ"האזנה ללא הסכמה של אף אחד מבעלי השיחה". חתימת קול היא לא אותו נכס כמו קובץ ההקלטה: כדאי לשמור אותה בטבלה נפרדת, עם מפתח מחיקה לכל מתקשר, כך שאפשר למחוק אותה לבד בלי לגעת באודיו ובתמלול. לוודא מול איש מקצוע מוסמך אילו חובות חלות על העסק לפני עלייה לאוויר.
- **אירוח**: פונקציות ענן לנפח נמוך, שרתים ייעודיים לנפח גבוה

### שלב 2: זיהוי דיבור בעברית (STT)

#### OpenAI (ברירת המחדל המומלצת)

OpenAI מתמודד היטב עם דיבור מעורב עברית-אנגלית שנפוץ בסביבות הייטק ישראליות.

```python
import openai

client = openai.OpenAI()

def transcribe_hebrew(audio_file_path: str) -> str:
    """תמלול קובץ אודיו בעברית עם gpt-transcribe."""
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-transcribe",
            file=audio_file,
            # gpt-transcribe מקבל `languages` (רשימה) ולא `language` ביחיד;
            # אסור לשלוח את שניהם. extra_body הוא הדרך שבה הדוגמה הרשמית
            # בפייתון מעבירה אותו.
            extra_body={"languages": ["he"]},
        )
    return transcript.text


def transcribe_hebrew_with_timestamps(audio_file_path: str) -> dict:
    """חותמות זמן ברמת מילה. timestamp_granularities נתמך רק ב-whisper-1,
    שנכבה ב-26.02.2027: תכננו חלופה (למשל ElevenLabs Scribe v2, שמחזיר
    חותמות זמן ברמת מילה)."""
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

**טיפים ל-OpenAI בעברית:**
- להעביר עברית במפורש (`languages=["he"]` ב-gpt-transcribe, `language="he"` ב-whisper-1) כדי למנוע זיהוי שגוי כערבית
- לדיבור מעורב עברית-אנגלית ב-gpt-transcribe, להעביר את שתי השפות: `languages=["he", "en"]`, ועוד `keywords` לשמות מוצרים
- Whisper מתמודד היטב עם טקסט ללא ניקוד (סטנדרטי בעברית מודרנית)
- איכות אודיו חשובה: קצב דגימה 16kHz+, ערוץ מונו, פורמט WAV. אין להקליט ל-FLAC או ל-OGG אם היעד הוא OpenAI: ה-API לתמלול מקבל רק mp3, mp4, mpeg, mpga, m4a, wav ו-webm, ודוחה את הקובץ אחרי ההעלאה
- גודל קובץ מקסימלי: 25MB. להקלטות ארוכות, לחלק לסגמנטים

#### Google Cloud Speech-to-Text

זיהוי דיבור בעברית בגוגל רץ על מודלי Chirp בלבד, באזורים מוגדרים, דרך V2 API.

```python
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
import os

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]

# עברית ב-Google STT קיימת רק על משפחת Chirp והיא אזורית, ו-Chirp 2 מתועד כזמין
# אך ורק ב-Speech-to-Text API V2. לכן עברית חייבת לעבור דרך speech_v2 מול נקודת
# קצה אזורית, ולא דרך הלקוח הגלובלי speech_v1. בטבלת השפות הנתמכות iw-IL מופיע
# על chirp ו-chirp_2 ב-europe-west4, ב-asia-southeast1 וב-us-central1, ועל chirp_3 במולטי-אזורים
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
ש-`Speech.StreamingRecognize` שלו מקבל, ועברית לא נמצאת ברשימה (יש בה 16 לוקאלים:
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
        region="westeurope",  # אירופה; uaenorth או qatarcentral קרובים יותר, אבל מחוץ לאיחוד האירופי
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

קודם מנרמלים את טקסט ההודעה. ב-`references/hebrew-tts-normalization.md` יש פונקציית עזר בדוקה למספרי טלפון ות"ז (ספרה אחר ספרה), לסכומים בשקלים ולראשי תיבות עם גרשיים; תאריכים ושעות צריך להוסיף בעצמכם. ב-Chirp 3 HD תגיות ההשהיה `[pause]` מסומנות כלא זמינות ל-`he-il`, ולכן יוצרים השהיות בעזרת סימני פיסוק.

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

**הקוד הזה לא מכיר חגים**: ביום כיפור הוא עונה "פתוח". הפונקציה `is_open()` ב-`references/twilio-call-flow.md` מוסיפה את לוח החגים של Hebcal לישראל: סגור ביום טוב וביום העצמאות (ש-Hebcal מחזיר רק עם `mod=on`), נסגר ב-13:00 ביום שלפני יום טוב (אבל לא בערב פורים ובערב תשעה באב, שהם ימי עבודה רגילים), ושומר טבלת חגים מראש בקובץ עם ברירת מחדל ניתנת להגדרה, כך שתקלה ב-Hebcal לא תגרום לבוט לענות "פתוח" בחג.

#### מבנה תפריט IVR ישראלי סטנדרטי

מילון `IVR_MENU` מלא (ברכת פתיחה, תפריט ראשי עם 4 אפשרויות, תת-תפריט שירות לקוחות ותור לנציג עם הודעות המתנה תקופתיות בעברית) נמצא ב-`references/ivr-design-patterns.md` בסעיף "Reference IVR_MENU structure". כדאי 3-4 אפשרויות לכל רמה, כוכבית לתפריט הקודם וסולמית לתפריט הראשי, timeout של 8 שניות ו-3 ניסיונות.

#### עקרונות לפרומפטים קוליים בעברית

| כלל | דוגמה | למה |
|-----|--------|-----|
| שימוש בגוף שני רבים | "הקישו 1" ולא "תקיש 1" | טון מקצועי, נמנע ממגדר |
| פרומפטים עד 15 שניות | 3-4 אפשרויות מקסימום ברמה | מתקשרים מאבדים סבלנות |
| הכרזת שעות לפני הודעת סגור | "שעות הפעילות: א'-ה' 9-17" | מפחית ניסיונות חוזרים |
| אפשרות באנגלית | "For English, press 9" | חלק מהמתקשרים יעדיפו אנגלית; מדדו את שיעור הבחירה בקו שלכם לפני שמתכננים את הענף |
| "כוכבית" לכפתור * | "לחזרה, הקישו כוכבית" | מונח סטנדרטי בעברית |
| "סולמית" לכפתור # | "לתפריט הראשי, הקישו סולמית" | מונח סטנדרטי בעברית |
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
    # שלב 1: תמלול עם gpt-transcribe (transcribe_hebrew משלב 2)
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
    פלט לפי סגמנטים דורש verbose_json, שרק whisper-1 מחזיר, ו-whisper-1
    נכבה ב-26.02.2027. בלי סגמנטים, השתמשו ב-gpt-transcribe עם
    languages=["he", "en"] וקראו את שדה `languages` שהוא מחזיר.
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

client = Client("YOUR_SID", "YOUR_TOKEN")


def purchase_israeli_number(bundle_sid=None, address_sid=None):
    """רכישת מספר ישראלי ב-Twilio.

    לפי Twilio, באזורים מסוימים נדרשים Bundle או Address כדי לעמוד ברגולציה
    המקומית, ו-Regulation מוגדר לפי IsoCountry, NumberType ו-EndUserType.
    בדקו את ה-Regulation של IL לסוג המספר (ב-Console או דרך Regulatory
    Compliance API) ואת address_requirements של כל מועמד לפני הרכישה.
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

#### תהליך השיחה

תהליך השיחה המלא והבדוק ב-Flask נמצא ב-`references/twilio-call-flow.md`. עדיף להעתיק משם ולא לכתוב לבד מהקטעים שלמטה, כי כל אחד מהם הוא דרך שבה תהליך שנכתב ביד נשבר על קו אמיתי:

- לכל `<Gather>` ו-`<Record>` צריך `action` שמפנה לנתיב קיים. `<Record>` בלי `action` מבקש שוב את ה-URL הנוכחי, משמיע שוב את ההודעה ומקליט שוב, בלולאה.
- מעבירים את מספר הניסיון ב-URL ושולחים לנציג אחרי 3 ניסיונות; `<Redirect>` חשוף בחזרה לתפריט נתקע בלולאה כשהמתקשר שותק.
- מאמתים `X-Twilio-Signature` בכל webhook.
- מורידים את ההודעה הקולית מ-`recordingStatusCallback` ולא מה-action של `<Record>`: ייתכן שההקלטה עדיין לא זמינה כשה-action נשלח.
- ב-`<Say>` משתמשים בקולות `he-IL`: ב-Twilio יש `Google.he-IL-Standard-A` עד `D` ו-`Google.he-IL-Wavenet-A` עד `D`, ואין קול he-IL Chirp3-HD, למרות שבגוגל עצמה יש.
- קלט מדובר ב-`<Gather>`: השורה העברית היחידה של Twilio לגוגל (`iw-IL`) נמצאת בטבלה שמסומנת deprecated. בדקו `speechModel="deepgram_nova-3"` עם `language="he"` (Deepgram מציגה עברית ב-Nova-3) והשאירו DTMF כגיבוי.
- ב-webhook של TwiML אין אודיו. בוט שיחתי צריך Media Streams (`<Connect><Stream>`, תמיד mu-law ב-8kHz) או OpenAI Realtime דרך SIP; קובץ העזר מכסה את שניהם.

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

### דוגמה 2: בוט קולי לשירות לקוחות

המשתמש אומר: "צריך בוט קולי שיחתי לחנות האונליין שלנו. שיטפל במצב הזמנה, החזרות, ויעביר לנציג."

פעולות:
1. חיבור האודיו של השיחה עם Twilio Media Streams (mu-law ב-8kHz) או OpenAI Realtime דרך SIP; ב-webhook רגיל של TwiML אין אודיו
2. הגדרת Google Cloud STT V2 לתמלול בזמן אמת. עברית היא `iw-IL`, וסטרימינג בעברית דורש `chirp_3` במולטי-אזור `eu` או `us` (Preview): ב-`chirp_2` עברית לא מופיעה ברשימת StreamingRecognize. אין מודל ייעודי לשיחות טלפון בעברית
3. עיבוד טקסט מתומלל דרך LLM לזיהוי כוונה ויצירת תשובה
4. שימוש ב-Azure Neural TTS (he-IL-HilaNeural) לתגובות עבריות טבעיות
5. חיפוש הזמנה לפי מספר (DTMF או ספרות מדוברות)
6. העברה לנציג אנושי עם ניהול תור

### דוגמה 3: שירות תמלול הודעות קוליות

המשתמש אומר: "רוצה לתמלל הודעות קוליות שנשארות על הקו העסקי ולשלוח אותן כטקסט למחלקה הרלוונטית."

פעולות:
1. הגדרת Twilio recording webhook ללכידת אודיו
2. הקמת צינור תמלול מבוסס `gpt-transcribe` לעברית
3. סיווג כוונת ההודעה (בקשת חזרה, תלונה, שאלה על הזמנה)
4. חילוץ ישויות (מספרי טלפון, מספרי הזמנה, שמות)
5. ניתוב הטקסט המתומלל ב-SMS/WhatsApp למחלקה הרלוונטית

### דוגמה 4: טיפול בדיבור מעורב עברית-אנגלית

המשתמש אומר: "המתקשרים שלנו מערבבים לעיתים קרובות עברית ואנגלית, במיוחד מונחים טכניים. איך מטפלים בזה?"

פעולות:
1. להעביר ל-gpt-transcribe את שתי השפות (`languages=["he", "en"]`) במקום לכפות עברית בלבד
2. לממש עיבוד-לאחר לנרמול מונחים טכניים באנגלית במבטא עברי
3. לבנות אוצר מילים מותאם של מונחי טכנולוגיה עברית-אנגלית (deploy, push, server, bug)
4. לבדוק עם אודיו מעורב לדוגמה באמצעות סקריפט הדמו
5. להגדיר ספי ביטחון ולבקש מהמתקשר לחזור על עצמו כשהביטחון נמוך

## משאבים מצורפים

### סקריפטים
- `scripts/hebrew-stt-demo.py` -- סקריפט הדגמה לזיהוי דיבור בעברית דרך OpenAI (`gpt-transcribe` כברירת מחדל, `whisper-1` רק לחותמות הזמן של `--verbose`). מייצר קובץ אודיו לדוגמה ומתמלל אותו בחזרה לטקסט. הרצה: `python scripts/hebrew-stt-demo.py --help`

### חומרי עזר
- `references/hebrew-stt-models.md` -- טבלת השוואה של מודלים לזיהוי דיבור בעברית (Whisper, Google Cloud STT, Azure Speech) עם הבדלים מבניים (אף ספק לא מפרסם WER לעברית לפי תנאי שיחה כמו טלפון, רעש או מבטא, ולכן אין דירוג), תמחור והמלצות לפי תרחיש. עיינו בו בעת בחירת ספק STT.
- `references/twilio-call-flow.md` -- תהליך שיחה מלא ובדוק ב-Flask ל-Twilio: אימות חתימות, חגים וערבי חג מ-Hebcal, הגבלת ניסיונות, תא קולי בלי לולאה והורדת ההקלטה, וגם Media Streams ו-OpenAI Realtime דרך SIP לבוט שיחתי. עיינו בו לפני שכותבים webhooks.
- `references/hebrew-tts-normalization.md` -- נרמול טקסט עברי לפני TTS (טלפונים, ת"ז, שקלים, ראשי תיבות) עם פונקציית עזר בדוקה וסקריפט הבדיקות שלה.
- `references/ivr-design-patterns.md` -- תבניות נפוצות של תהליכי IVR לעסקים ישראליים, כולל מסעדות, מרפאות, שירות לקוחות ומשרדי ממשלה. עיינו בו בעת עיצוב מבנה תפריט IVR.

## מלכודות נפוצות

- מנועי זיהוי דיבור בעברית מתקשים עם סלנג ישראלי ("יאללה", "סבבה", "בלאגן") ומילות שאלה מערבית, רוסית ואמהרית. סוכנים עלולים לא להתחשב בקלט רב-לשוני בבוטים קוליים.
- מערכות IVR טלפוניות ישראליות חייבות להציע עברית כשפת ברירת מחדל, ואנגלית כמשנית. סוכנים עלולים לבנות בוטים קוליים עם אנגלית כברירת מחדל, מה שמתסכל מתקשרים דוברי עברית.
- TTS בעברית לא דורש ניקוד, וכל מחרוזת עברית בסקיל הזה כתובה בכוונה בלי ניקוד: הקולות הנוירליים he-IL של גוגל ושל Azure מנקדים בעצמם, ולכן קלט לא מנוקד הוא המצב הרגיל. מה שהניקוד כן נותן זה פירוק דו-משמעות בהומוגרפים. המילה "דבר" יכולה להיקרא `דָּבָר` או `דַּבֵּר`, אז אם הומוגרף נופל על מילה שמשנה את משמעות האפשרות בתפריט, מנקדים רק את המילה הזאת או כותבים את המשפט מחדש. תמיד להאזין לפלט לפני עלייה לאוויר במקום להניח התנהגות כזאת או אחרת.
- מספרי טלפון ישראליים באורך משתנה ב-IVR: קווים נייחים 9 ספרות (0X-XXXXXXX); נייד (05X) ומספרי 07X הם 10 ספרות (05X-XXXXXXX, 07X-XXXXXXX). בוטים קוליים חייבים לקבל את שני הפורמטים.
- אל תעתיקו סף ביטחון ממדריך, כולל מגרסאות קודמות של הסקיל הזה שטענו שרעש הרקע בישראל גבוה מהממוצע העולמי. אין לנו מקור להשוואה הזאת. קבעו את הסף לפי מדידות על הקו שלכם: הקליטו שיחות אמיתיות מהסביבות שהמתקשרים שלכם באמת נמצאים בהן (בתי קפה, משרדים פתוחים ותחבורה ציבורית הם המקרים הקשים הנפוצים כאן) וכוונו מול אוסף ההקלטות הזה.
- **ב-ElevenLabs, v3 ו-v4 לא נתמכים ב-WebSocket של Text to Speech (`stream-input`).** ה-endpoint הזה לא תומך ב-`eleven_v3` או ב-`eleven_v4_turbo`, ו-`eleven_flash_v2_5` מהדוגמה של הספק עצמו לא תומך בעברית בכלל ולכן אינו תחליף. ל-v3/v4 משתמשים ב-WebSocket של Text to Dialogue (ב-`eleven_v4_turbo` מותר בדיוק קול רשום אחד לחיבור).
- **כל מודלי התמלול של OpenAI שהסקיל השתמש בהם לפני 2026-09 נכבים ב-26.02.2027** (`whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `gpt-4o-transcribe-diarize`). סוכנים ימשיכו לפלוט `whisper-1` מנתוני האימון. ברירת המחדל היא `gpt-transcribe`, וזכרו שהוא מקבל `languages` (רשימה) במקום `language` ביחיד, ואסור לשלוח את שניהם. רק `whisper-1` מחזיר חותמות זמן ברמת מילה, אז פיצ'ר של חותמות זמן שנבנה היום צריך תוכנית מעבר.
- נוף הקול בעברית משתנה במהירות (במהלך 2026 ElevenLabs השיקו את v4, Inworld הוסיפו עברית כשפת Tier 1 והוציאו משימוש את מודלי 1.5, ו-OpenAI החליפו את כל קו התמלול). אמתו בזמן הבנייה, ובדקו את רשימת השפות המפורטת של הספק ולא מספר כולל בכותרת.


## קישורי עזר

| מקור | כתובת | מה לבדוק |
|------|-------|----------|
| OpenAI Whisper (זיהוי דיבור עברית) | https://github.com/openai/whisper | המרת דיבור לטקסט רב-לשונית כולל עברית, גדלי מודלים, דיוק |
| Google Cloud Speech-to-Text | https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages | תמיכה בעברית (מופיעה כ-`iw-IL`), זיהוי סטרימינג, תמחור |
| Azure AI Speech (עברית) | https://learn.microsoft.com/he-il/azure/ai-services/speech-service/language-support | קולות STT/TTS בעברית, רשימת קולות נוירליים |
| הוצאות משימוש ב-OpenAI | https://developers.openai.com/api/docs/deprecations | תאריכי כיבוי ומחליפים למודלי realtime ותמלול |
| ivrit.ai (קורפוס דיבור בעברית) | https://www.ivrit.ai | קורפוס דיבור עברי פתוח, מודלי ASR מאומנים מראש |
| מודלים של ElevenLabs | https://elevenlabs.io/docs/overview/models | רשימות שפות לכל מודל (עברית ב-v3/v4, חסרה ב-Multilingual v2 וב-Flash v2.5) ובאיזה WebSocket כל מודל משתמש |
| ה-API של Deepdub (ישראלי) | https://docs.deepdub.ai/api-reference/tts/generate-and-stream-tts-audio | שפות נתמכות (עברית `he-IL`), מזהה המודל הנוכחי |
| שפות ב-Inworld TTS | https://docs.inworld.ai/tts/capabilities/multilingual | דרגת העברית (`he`), מזהי המודלים הנוכחיים |

## פתרון בעיות

### בעיה: "תמלול עברי מחזיר טקסט בערבית"
סיבה: מודל ה-STT מזהה בטעות עברית כערבית עקב טווחי תווים משותפים או פונמות דומות.
פתרון: להגדיר את השפה במפורש. ה-STT של גוגל רוצה `iw-IL` (ולא `he-IL`, שלא מופיע בכלל בטבלת השפות הנתמכות שלו); ה-TTS של גוגל ו-Azure רוצים `he-IL`; ב-OpenAI מעבירים `languages=["he"]` ב-gpt-transcribe ו-`language="he"` ב-whisper-1. הוספת רמז בעברית גם עוזרת: `prompt="שלום, ברוכים הבאים"`.

### בעיה: "קול ה-TTS נשמע רובוטי בעברית"
סיבה: שימוש בקולות Standard ולא Neural/Wavenet.
פתרון: לעבור לקולות neural: Google Wavenet (he-IL-Wavenet-A/B) או Azure Neural (he-IL-HilaNeural). (Amazon Polly אינו תומך בעברית כלל, ולכן אינו אפשרות.) קולות neural יקרים יותר אבל טבעיים בהרבה.

### בעיה: "תפריט IVR עושה timeout לפני שהמתקשר מגיב"
סיבה: timeout קצר מדי, במיוחד למתקשרים מבוגרים או פרומפטים ארוכים בעברית.
פתרון: להגדיל timeout ל-8-10 שניות. להוסיף מקש ממוספר לחזרה (למשל "לשמוע שוב, הקישו 7"; לא מקש שכבר משמש לבחירת שפה), ולהשאיר את הכוכבית לתפריט הקודם. לקחת בחשבון שפרומפטים בעברית עלולים להיות ארוכים יותר מאנגלית.

### בעיה: "Twilio לא מוצא מספרים ישראליים"
סיבה: הזמינות של מספרים ישראליים משתנה. ל-Twilio מלאי מוגבל של +972 בהשוואה למספרים אמריקאיים.
פתרון: לחפש מספרים מקומיים וגם חינמיים, ולבדוק לכל מועמד את `address_requirements` ואת ה-Regulation של IL לסוג המספר: רכישה יכולה להיכשל בגלל Bundle או Address חסרים ולא בגלל מלאי. שווה לבקש הצעת מחיר גם מ-Vonage, אבל אף אחד מהספקים לא מפרסם מלאי מספרים ישראלי להשוואה, אז כדאי לבדוק זמינות בפועל בעצמכם ולא לסמוך על דירוג. לנפחים גבוהים, ליצור קשר עם Twilio sales. אפשר גם לנייד מספרים ישראליים קיימים ל-Twilio.
