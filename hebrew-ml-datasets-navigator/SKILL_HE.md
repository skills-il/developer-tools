---
name: hebrew-ml-datasets-navigator
description: "Navigate the fragmented landscape of Hebrew and Yiddish ML datasets and models. Covers ivrit.ai, Dicta, the Israeli National NLP Program, and Knesset Plenums. Helps pick the right dataset by task, license, and register."
license: MIT
---

# ניווט במאגרי ML עבריים

## בעיה

קהילת ה-ML הישראלית חזקה לגודלה, אבל המאגרים והמודלים מפוזרים. ivrit.ai מפרסמת קורפוסי דיבור עברי ברמה עולמית בארגון HuggingFace אחד, Dicta מפרסמת מודלי LLM ו-BERT עבריים בארגון אחר, התכנית הלאומית ל-NLP מתחזקת בנצ'מרקים תחת `HebArabNlpProject`, ומשאבים קלאסיים כמו AlephBERT נמצאים במקום אחר. הרישיונות משתנים מידידותי-מסחרי-מלא עד מחקר-בלבד. כיסוי הרגיסטר בעברית משתנה דרמטית: חלק מהקורפוסים הם כולם עברית סטנדרטית מודרנית, אחרים חצי טקסטים דתיים, אחרים דיבור חי. חוקר שמנסה לבחור את השילוב הנכון ל-"פיין-טיונינג של סיווג סנטימנט על צ'אט תמיכה עברי למוצר מסחרי" צריך לחפש בחמישה ארגונים ולקרוא כל dataset card כדי להבין מה באמת מותר לו להשתמש בו.

## הוראות

### שלב 1: זהו את המשימה

משימות ML עבריות שונות זקוקות לדאטהסטים שונים. התאימו את המשימה למשפחת הדאטהסטים לפני חיפוש.

| משימה | סוג מידע | משפחות דאטהסט לבדיקה ראשונה |
|------|----------|-------------------------------|
| זיהוי דיבור עברי (ASR) | אודיו + תמלול | ivrit.ai (crowd-transcribe, crowd-recital, audio-v2) |
| סינתזת דיבור עברי (TTS) | טקסט + אודיו סטודיו | אודיו ברישוי פתוח (מוגבל, בדרך כלל דורש הקלטות משלכם) |
| Pre-training ל-LLM עברי | קורפוס טקסט עברי גדול | קורפוסי Dicta, תת-קבוצה עברית של MADLAD-400, OSCAR Hebrew, ויקיפדיה עברית, מליאות הכנסת |
| Instruction tuning ל-LLM | זוגות prompt-response בעברית | דאטהסטי instruction של Dicta, Alpaca מתורגם, מותאם |
| הבנת הנקרא / QA | טקסט + שאלות-תשובות | HeQ (`pig4431/HeQ_v1`) |
| סיווג סנטימנט | טקסט עברי + תוויות | HebrewSentiment (`HebArabNlpProject/HebrewSentiment`) |
| NLI | זוגות premise-hypothesis | HebNLI (`HebArabNlpProject/HebNLI`) |
| NER | טקסט עברי + תגיות ישויות | דאטהסטי NER של Dicta, גרסאות היסטוריות של NNLP-IL |
| ניתוח מורפולוגי | טקסט עברי + תגיות מורפו | דאטהסטי morph של Dicta |
| ניקוד | טקסט מנוקד ולא מנוקד | דאטהסטי ניקוד של Dicta |
| זיהוי פרפראזות | זוגות טקסט עברי | Hebrew paraphrase dataset של NNLP-IL (9,750 זוגות) |
| תרגום עברית-אנגלית | קורפוסים מקבילים | NeuLabs-TedTalks, תת-קבוצות OPUS |
| ASR יידיש | אודיו + תמלול יידיש | ivrit.ai Yiddish (yi-whisper) |
| טקסט יידיש | קורפוסי יידיש | ivrit.ai crowd-whatsapp-yi, crowd-recital-yi |

### שלב 2: ארגונים מרכזיים

שמרו את הארגונים האלה כמקורות סמכותיים לעדכונים:

#### ivrit.ai

ארגון ללא מטרות רווח שמתמקד במשאבי דיבור עבריים. נכון ל-2025-2026 מארח את קורפוס האודיו העברי הגדול בעולם (יותר מ-22,000 שעות) תחת רישיון שמתיר שימוש מסחרי במפורש.

מודלים וקורפוסים מרכזיים:
- `ivrit-ai/crowd-transcribe-v5`, דאטהסט ASR עברי מקראוד-סורסינג
- `ivrit-ai/whisper-large-v3-turbo-ct2`, גרסה הכי מהירה להשקה בפרודקשן
- `ivrit-ai/pyannote-speaker-diarization-3.1`, diarization עברי
- `ivrit-ai/yi-whisper-large-v3`, ASR יידיש

#### Dicta

ארגון ה-LLM וה-BERT העברי המוביל בישראל.

מודלים מרכזיים:
- `dicta-il/DictaLM-3.0-24B-Base`, LLM בסיס עברי דגלי
- `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct`, instruction-tuned בגודל בינוני
- `dicta-il/dictabert`, BERT עברי בסיסי
- `dicta-il/dictabert-sentiment`, סיווג סנטימנט עברי
- `dicta-il/dictabert-heq`, מכוון ל-QA עברי

#### התכנית הלאומית ל-NLP (HebArabNlpProject)

יוזמה לאומית לתשתיות NLP עברי-ערבי, ממומנת על ידי משרד הביטחון ונתמכת על ידי Dicta ו-Webiks.

מאגרים מרכזיים:
- `HebArabNlpProject/HebrewSentiment`, 41,305 דוגמאות מתויגות, CC-BY-4.0
- `HebArabNlpProject/HebNLI`, NLI עברי

### שלב 3: תאימות רישיון לפי שימוש

| המוצר שלך | רישיונות שאפשר להשתמש בהם | להימנע |
|------------|-----------------------------|---------|
| SaaS מסחרי / מוצר | CC-BY-4.0, MIT, Apache 2.0, רישיון ivrit.ai, רישיונות Dicta המסחריים | CC-BY-NC, GPL (אלא אם המוצר שלכם GPL), "מחקר בלבד" |
| פרסום מחקרי | כל רישיון שמתיר הפצה למחקר | דאטהסטים תחת NDA |
| אב-טיפוס פנימי | הכי מתירים, "מחקר מותר" מכסה רוב הצרכים | בדקו היטב אם האב-טיפוס נהפך למוצר |

תמיד קראו את ה-dataset card הספציפי. רישיונות משתנים.

### שלב 4: כיסוי רגיסטר דמוגרפי

"דאטהסט עברי" הוא לא הומוגני.

| רגיסטר | מקורות טיפוסיים | מתי זה משנה |
|---------|------------------|-------------|
| כתוב סטנדרטי מודרני | ויקיפדיה, חדשות, גיקטיים | LLM כללי, חיפוש, סיכום |
| דיבור / קולוקוויאלי | פודקאסטים, יוטיוב, WhatsApp | צ'אטבוטים, ממשקי קול, תמיכה |
| אקדמי / פורמלי | קורפוסים אקדמיים, משפטיים | משפט, מדע, ממשל |
| דתי / קלאסי | תנ"ך, תלמוד, טקסטים רבניים | כלי דת, עיבוד טקסטים היסטוריים |
| נאומי מליאת הכנסת | רישומים פרלמנטריים (דרך ivrit.ai) | NLP פוליטי, civic tech |
| מעורב עברית-אנגלית | דיונים טכנולוגיים | מוצרי סטארט-אפ, כלי מפתחים |

### שלב 5: התאמת דאטהסטים למודלים

| משימה | מודל התחלתי | Fine-tune על | הערות |
|------|-------------|--------------|--------|
| סנטימנט | `dicta-il/dictabert` | `HebArabNlpProject/HebrewSentiment` | בדיוק הרצפט של Dicta |
| QA | `dicta-il/dictabert` | `pig4431/HeQ_v1` | בדיוק הרצפט של Dicta |
| ASR עברי | `ivrit-ai/whisper-large-v3` | אודיו דומיין ספציפי שלכם | השתמשו ב-turbo-ct2 לפרודקשן |
| ASR יידיש | `ivrit-ai/yi-whisper-large-v3` | אודיו יידיש שלכם | תת-משימה תחומה |
| LLM עברי instruction | `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct` | זוגות instruction שלכם | השתמשו ב-LoRA |
| Embeddings | `dicta-il/neodictabert-bilingual-embed` | זוגות שלכם | baseline דו-לשוני חזק |

### שלב 6: אמתו לפני אימון

1. אשרו שהדאטהסט קיים ב-HuggingFace ID
2. קראו את ה-dataset card במלואו
3. בדקו sample count ו-splits
4. לאודיו, האזינו לכמה דוגמאות
5. לטקסט, קראו כמה דוגמאות
6. בדקו תאימות רישיון לשימוש המסחרי הספציפי
7. תעדו דרישות ייחוס

## דוגמאות

### דוגמה 1: סיווג סנטימנט לתמיכה עברית

המשתמש אומר: "צריך לסווג סנטימנט בהודעות תמיכת לקוחות עברית למוצר SaaS מסחרי."

פעולות:
1. משימה: סיווג סנטימנט על עברית דיבורית
2. בדקו `HebArabNlpProject/HebrewSentiment`, 41,305 דוגמאות, CC-BY-4.0, כולל דיבור מסוים. מסחרי OK עם ייחוס.
3. בדקו `dicta-il/dictabert-sentiment` כ-baseline מוכן
4. התחילו עם מודל Dicta והעריכו על צ'אטים אמיתיים מוחזקים
5. אם הבסיס לא מספיק, עשו fine-tune של `dicta-il/dictabert` על HebrewSentiment + הנתונים שלכם
6. תעדו ייחוס במוצר

תוצאה: בחירת מודל מבוססת נתונים עם ייחוס תקין.

### דוגמה 2: מוצר תמלול פודקאסט עברי

המשתמש אומר: "אנחנו רוצים לתמלל פודקאסטים עבריים למוצר חדש. באיזה מודל ASR להתחיל?"

פעולות:
1. משימה: דיבור לטקסט עברי על אודיו שיחתי
2. בדקו מודלי ivrit.ai, משפחת whisper-large-v3 היא SOTA לעברית
3. להשהייה בפרודקשן, השתמשו ב-`whisper-large-v3-turbo-ct2`
4. לפודקאסטים מרובי דוברים, שלבו עם `pyannote-speaker-diarization-3.1`
5. אשרו שהרישיון של ivrit.ai מתיר שימוש מסחרי
6. תכננו ייחוס לפי ה-dataset card
7. שקלו fine-tuning על דוגמת פודקאסטים משלכם אם יש אי-התאמת דומיין

תוצאה: סטאק ASR מוכן להשקה.

## משאבים מצורפים

### סקריפטים
- `scripts/find_dataset.py` -- מחפש דאטהסטים אינטראקטיבית. מסנן לפי משימה, רישיון, רגיסטר, ועברית/יידיש/מעורב.

### מסמכי עזר
- `references/dataset-catalog.md` -- קטלוג מקיף של דאטהסטים עבריים ויידיים.
- `references/model-catalog.md` -- קטלוג מקיף של מודלים עבריים ויידיים.
- `references/license-quick-guide.md` -- מדריך תאימות רישיונות.

## שרתי MCP מומלצים

אין צורך ב-MCP לניווט.

## קישורי עזר

| מקור | URL | מה לבדוק |
|------|-----|---------|
| ארגון ivrit.ai ב-HuggingFace | https://huggingface.co/ivrit-ai | מודלי ASR, דאטהסטים, diarization |
| אתר ivrit.ai | https://www.ivrit.ai/en/ivrit-ai-2/ | משימה, רישוי |
| ארגון Dicta ב-HuggingFace | https://huggingface.co/dicta-il | משפחת DictaLM 3.0, DictaBERT |
| אתר Dicta | https://dicta.org.il | פרסומים, דוח טכני DictaLM |
| התכנית הלאומית ל-NLP | https://huggingface.co/HebArabNlpProject | בנצ'מרקים עברית-ערבית |
| NNLP-IL Hebrew Resources | https://github.com/NNLP-IL/Hebrew-Resources | רשימה מקיפה |
| HeQ GitHub | https://github.com/NNLP-IL/Hebrew-Question-Answering-Dataset | מקור HeQ |
| Open Hebrew LLM Leaderboard | https://huggingface.co/blog/leaderboard-hebrew | מתודולוגיית בנצ'מרקים |

## מלכודות נפוצות

- "דאטהסט עברי" הוא לא דבר יחיד. הרגיסטר (מודרני, דתי, דיבורי, אקדמי) משנה יותר מהגודל הכולל. קורפוס חדשות של 10GB הוא חסר תועלת למוצר של טקסטים דתיים.
- ivrit.ai משתמשת ברישיון מתיר בהתאמה אישית שמתיר שימוש מסחרי במפורש. סוכנים רבים מצטטים CC-BY-NC כברירת מחדל מתוך הרגל. קראו את ה-dataset card הספציפי.
- DictaLM 3.0 בא במספר גדלים שנגזרים ממודלי בסיס שונים (Mistral, Nemotron, Qwen). הרישיונות של ה-upstream שונים. אל תניחו שרישיון אחד חל על כל ה-DictaLM.
- המטריקה הראשית של HeQ צריכה להיות F1, לא Exact Match. המורפולוגיה העברית ותופעת הסופיות הופכות את EM לשביר.
- יידיש ועברית חולקות אלפבית אך הן שפות שונות עם מודלים שונים. אל תאמנו מודל עברי על יידיש או להיפך בלי תכנון מפורש של העברת שפה.
- הדאטהסט `pig4431/HeQ_v1` הוא מראה תחזוקה-קהילתית של HuggingFace. המקור הקנוני הוא `NNLP-IL/Hebrew-Question-Answering-Dataset` ב-GitHub.

## פתרון בעיות

### שגיאה: "רישיון הדאטהסט לא ברור או השתנה"
סיבה: dataset cards ב-HuggingFace יכולים להתעדכן.
פתרון: השתמשו ב-dataset card הנוכחי כמקור סמכותי. כשיש ספק, שלחו מייל לבעלי הדאטהסט.

### שגיאה: "מודל שעשינו לו fine-tune על HeQ נכשל על עברית מהעולם האמיתי"
סיבה: פסקאות HeQ מגיעות מויקיפדיה וגיקטיים, שנוטות לפורמלי.
פתרון: הוסיפו נתוני אימון ספציפיים לדומיין.

### שגיאה: "דרישות הייחוס לא ברורות"
סיבה: דאטהסטים שונים יש להם סעיפי ייחוס שונים.
פתרון: קראו את קובץ LICENSE ו-CITATION בדאטהסט.
