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
| Pre-training ל-LLM עברי | קורפוס טקסט עברי גדול | קורפוסי Dicta, `allenai/MADLAD-400` עברית, `oscar-corpus/OSCAR-2301` עברית, חתך עברית של `uonlp/CulturaX`, פילטר `heb_Hebr` של `HuggingFaceFW/fineweb-2`, mC4 (החתך העברי באיכות נמוכה אבל לא מנוטרל), ויקיפדיה עברית, מליאות הכנסת |
| Instruction tuning ל-LLM | זוגות prompt-response בעברית | דאטהסטי instruction של Dicta, Alpaca מתורגם, מותאם |
| הבנת הנקרא / QA | טקסט + שאלות-תשובות | HeQ (`Etelis/HeQ_v1` כמראה ב-HF; קנוני ב-`github.com/NNLP-IL/Hebrew-Question-Answering-Dataset`); `omrikeren/ParaShoot` (~3K דוגמאות few-shot) |
| סיווג סנטימנט | טקסט עברי + תוויות | HebrewSentiment (`HebArabNlpProject/HebrewSentiment`) |
| NLI | זוגות premise-hypothesis | HebNLI (`HebArabNlpProject/HebNLI`) |
| NER | טקסט עברי + תגיות ישויות | דאטהסטי NER של Dicta, גרסאות היסטוריות של NNLP-IL |
| ניתוח מורפולוגי | טקסט עברי + תגיות מורפו | דאטהסטי morph של Dicta |
| ניקוד | טקסט מנוקד ולא מנוקד | דאטהסטי ניקוד של Dicta |
| זיהוי פרפראזות | זוגות טקסט עברי | Hebrew paraphrase dataset של NNLP-IL (9,750 זוגות) |
| סיכום | מאמר עברי + סיכום | `biunlp/HeSum` (10K זוגות מאמר-סיכום מחדשות עבריות, BIU NLP), `HebArabNlpProject/HebSummaries` |
| בנצ'מרק ידע כללי | שאלות אמריקאיות + תשובות | HEBREW-MMLU (תרגום עברי של MMLU; אמתו את ה-HF mirror הפעיל, יש מספר תרגומים קהילתיים) |
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

מודלים מרכזיים (אומתו ב-huggingface.co/dicta-il):
- `dicta-il/DictaLM-3.0-24B-Base`, LLM בסיס עברי דגלי (24B, מבוסס Mistral)
- `dicta-il/DictaLM-3.0-24B-Thinking`, וריאנט reasoning של ה-24B
- `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct`, instruction-tuned בגודל בינוני (12B, מבוסס Nemotron)
- `dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF`, מודל reasoning קטן שרץ על חומרה צרכנית
- וריאנטים מקוונטים לפרודקשן: `*-FP8`, `*-W4A16`, `*-GGUF` (לדוגמה `DictaLM-3.0-Nemotron-12B-Instruct-FP8`)
- `dicta-il/dictalm2.0-instruct`, הדור הקודם, 7B מבוסס Mistral-7B, instruct fine-tuned (לפי מתכון Zephyr). קיים גם ב-`dictalm2.0-instruct-GGUF`, `-AWQ`, `-GPTQ`
- `dicta-il/dictabert`, BERT עברי בסיסי
- `dicta-il/dictabert-sentiment`, סיווג סנטימנט עברי
- `dicta-il/dictabert-heq`, מכוון ל-QA עברי

#### התכנית הלאומית ל-NLP (HebArabNlpProject)

יוזמה לאומית לתשתיות NLP עברי-ערבי, ממומנת על ידי משרד הביטחון ונתמכת על ידי Dicta ו-Webiks.

מאגרים מרכזיים:
- `HebArabNlpProject/HebrewSentiment`, דוגמאות סנטימנט מתויגות בעברית בחלוקה לסטים של train/validation/test. בדקו את ה-dataset card לרישיון העדכני ולספירת הדוגמאות לפני שימוש מסחרי
- `HebArabNlpProject/HebNLI`, NLI עברי
- `HebArabNlpProject/HebSummaries`, סיכום עברי

#### קורפוסים רב-לשוניים בקנה-מידה web עם חתכי עברית

השתמשו באלה ל-pre-training של LLM כשאתם צריכים קנה-מידה ששום קורפוס עברי לבדו לא מספק. תמיד סננו לחתך הסקריפט העברי וגם dedupe מחדש מול נתוני הדומיין שלכם.

- `uonlp/CulturaX`, 6.3T טוקנים על פני 167 שפות, משלב mC4 v3.1.0 עם הוצאות OSCAR עד 2023-01. ניקוי ודה-דופ כבדים. מושכים את החתך העברי לפי קוד שפה. Apache 2.0 (אבל מותנה ברישיונות mC4/OSCAR שמתחת, בדקו לפני אימון מסחרי).
- `HuggingFaceFW/fineweb-2`, ~20TB על פני 1,868 צמדי שפה-סקריפט. עברית זמינה כ-`heb_Hebr`. סינון איכותי יותר מ-CulturaX. מקור: CommonCrawl 2013 עד אפריל 2024.
- `allenai/MADLAD-400`, קורפוס רב-לשוני ברמת מסמך על פני 419 שפות. שתי גרסאות: noisy (LangID בלבד) ו-clean (מסונן). עברית כלולה.
- `oscar-corpus/OSCAR-2301`, קורפוס רב-לשוני שמקורו ב-CommonCrawl, חתך עברי זמין. שימו לב ש-`OSCAR-2301` תחת gating ב-HuggingFace, בקשו גישה בדף הדאטהסט לפני שימוש.
- mC4 (חתך עברי), לא מנוטרל אבל החלק העברי שלו ספג ביקורת על טקסט רועש וסינון חלש יותר מקורפוסים חדשים. העדיפו FineWeb-2 או CulturaX איפה שאפשר.

תמיד עשו טוקניזציה מחדש ו-dedupe כשמשלבים קורפוסים; CulturaX כבר מכיל mC4 + OSCAR עד 2023, אז שכבת אותם שוב יוצרת כפילות משמעותית.

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

### שלב 7: בנצ'מרקים חסרים בעברית

לאקוסיסטם NLP העברי יש פערים. שווה לציין שהשחרור של DictaLM 3.0 (פברואר 2026) הביא עמו חבילת בנצ'מרקים שמכסה תרגום, תמצות, סכמות בסגנון Winograd, טריוויה ישראלית וניקוד עברי, ובכך מצמצמת את הפער במשימות האלה. הרשימה למטה היא מה שעדיין חסר נכון למאי 2026: אם המשימה שלכם נמצאת בה, צפו לבנות נתוני הערכה בעצמכם או לשלב את הבנצ'מרק הקרוב ביותר עם הערכה אנושית ספציפית לדומיין.

- **הערכות בטיחות / red-team עבריים**, אין עמית ציבורי ל-ToxicChat או HarmBench. בנו prompts פנימיים.
- **יצירת קוד בעברית**, אין בנצ'מרק docstring או הערה בעברית. השתמשו ב-HumanEval/MBPP באנגלית והכירו במחיר.
- **הערכות long-context בעברית**, אין Needle-in-a-Haystack או LongBench בעברית. בנו פנימי מתוך ויקיפדיה עברית או תמלילי הכנסת.
- **שימוש בכלים / function-calling בעברית**, אין בנצ'מרק ציבורי. תרגמו prompts מ-BFCL לעברית.
- **נתוני preference / RLHF בעברית**, נדירים. רוב אות ה-preference המיושרת לעברית פרטית (Dicta, AI21, Hebrew-Mistral).
- **הערכות דיאלוג מדובר בעברית**, ivrit.ai מכסה ASR אבל אין בנצ'מרק איכות-דיאלוג ציבורי. בנו הערכה פנימית משיחות אמיתיות.
- **רב-מודאלי בעברית (vision-language)**, כמעט שום דבר ציבורי. הבנת מסמכים עבריים מכוסה ברובה רק על ידי OCR מסחרי + צנרות תרגום.

ידוע שקיים אבל מוגבל:
- **HEBREW-MMLU**, תרגום עברי של MMLU שמופיע באקוסיסטם של ה-Open Hebrew LLM Leaderboard; מספר תרגומים קהילתיים באיכויות שונות. אמתו את ה-mirror הפעיל לפני פרסום מספרים בני-השוואה. `openai/MMMLU` מכסה 14 שפות אבל עברית לא בקבוצה הרשמית הזאת.
- **Hebrew Winograd**, פורט קהילתי של Winograd Schema Challenge, פחות מ-300 פריטים. שונות גבוהה בריצה בודדת.

### שלב 8: משאבי NLP אקדמיים בישראל

מעבר ל-ivrit.ai, Dicta והתכנית הלאומית, כמה מעבדות אוניברסיטאיות מפרסמות עבודות NLP עבריות שכדאי לעקוב אחריהן:

- **מעבדת NLP של אוניברסיטת בר-אילן (BIU NLP)**, הקבוצה שמאחורי HeSum (`biunlp/HeSum`), ה-AlephBERT המקורי, ובנצ'מרקי תיוג עבריים. פרסומים ב-`nlp.biu.ac.il`.
- **האוניברסיטה הפתוחה**, קורפוסים עבריים וטקסטים היסטוריים (לדוגמה קורפוסי הכנסת לפני שחרור ivrit.ai).
- **טכניון / מעבדת NLPH**, מאמרי NLP עברי, מחקר על טוקניזציה ומורפולוגיה עברית.
- **האוניברסיטה העברית בירושלים (HUJI)**, שיתופי פעולה עם האוניברסיטה הפתוחה על תחביר, מורפולוגיה ועברית היסטורית. הפורט המקורי של Winograd-HE (vshwartz) יוצא משם.
- **אוניברסיטת רייכמן / IDC NLP**, פרסומי בנצ'מרק עבריים מזדמנים שקשורים לשיתופי פעולה עם תעשייה.

אסטרטגיית מעקב: הירשמו ל-`NNLP-IL/Hebrew-Resources` ל-curation קהילתי; לפרסומים ראשוניים עקבו אחרי דפי המעבדות וה-authors ב-Hugging Face.

## דוגמאות

### דוגמה 1: סיווג סנטימנט לתמיכה עברית

המשתמש אומר: "צריך לסווג סנטימנט בהודעות תמיכת לקוחות עברית למוצר SaaS מסחרי."

פעולות:
1. משימה: סיווג סנטימנט על עברית דיבורית
2. בדקו `HebArabNlpProject/HebrewSentiment`, דוגמאות סנטימנט עבריות עם train/validation/test, כולל דיבור מסוים. ודאו את הרישיון העדכני ב-dataset card לפני שימוש מסחרי.
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
| ארגון Dicta ב-HuggingFace | https://huggingface.co/dicta-il | משפחת DictaLM 3.0 (24B-Base, Nemotron-12B-Instruct, 1.7B-Thinking-GGUF, 24B-Thinking), DictaLM 2.0, DictaBERT |
| אתר Dicta | https://dicta.org.il | פרסומים, דוח טכני DictaLM 3.0 |
| התכנית הלאומית ל-NLP | https://huggingface.co/HebArabNlpProject | HebrewSentiment, HebNLI, HebSummaries ובנצ'מרקים נוספים |
| NNLP-IL Hebrew Resources | https://github.com/NNLP-IL/Hebrew-Resources | רשימה מקיפה |
| HeQ GitHub | https://github.com/NNLP-IL/Hebrew-Question-Answering-Dataset | מקור HeQ |
| HeQ ב-HuggingFace (מראה) | https://huggingface.co/datasets/Etelis/HeQ_v1 | מראה ל-HeQ ל-loading ישיר |
| HeSum | https://huggingface.co/datasets/biunlp/HeSum | סיכום אבסטרקטיבי עברי, 10K זוגות מאמר-סיכום (BIU NLP) |
| ParaShoot | https://github.com/omrikeren/ParaShoot | QA עברית בסגנון SQuAD, ~3K דוגמאות few-shot |
| CulturaX | https://huggingface.co/datasets/uonlp/CulturaX | קורפוס pre-training רב-לשוני, חתך עברית לפי קוד שפה |
| FineWeb-2 | https://huggingface.co/datasets/HuggingFaceFW/fineweb-2 | קורפוס web רב-לשוני, עברית ב-`heb_Hebr` |
| MADLAD-400 | https://huggingface.co/datasets/allenai/MADLAD-400 | קורפוס רב-לשוני ברמת מסמך, תמיכה בעברית |
| OSCAR-2301 | https://huggingface.co/datasets/oscar-corpus/OSCAR-2301 | קורפוס מבוסס-CommonCrawl, חתך עברי (gated, צריך לבקש גישה) |
| Open Hebrew LLM Leaderboard (space חי) | https://huggingface.co/spaces/hebrew-llm-leaderboard/leaderboard | דירוגים חיים, ציוני בנצ'מרק עדכניים |
| Open Hebrew LLM Leaderboard (הכרזה) | https://huggingface.co/blog/leaderboard-hebrew | מתודולוגיית בנצ'מרקים |
| BIU NLP Lab | https://nlp.biu.ac.il | פרסומי NLP אקדמיים מבר-אילן (HeSum, מקורות AlephBERT) |

## מלכודות נפוצות

- "דאטהסט עברי" הוא לא דבר יחיד. הרגיסטר (מודרני, דתי, דיבורי, אקדמי) משנה יותר מהגודל הכולל. קורפוס חדשות של 10GB הוא חסר תועלת למוצר של טקסטים דתיים.
- ivrit.ai משתמשת ברישיון מתיר בהתאמה אישית שמתיר שימוש מסחרי במפורש. סוכנים רבים מצטטים CC-BY-NC כברירת מחדל מתוך הרגל. קראו את ה-dataset card הספציפי.
- DictaLM 3.0 בא במספר גדלים שנגזרים ממודלי בסיס שונים (Mistral, Nemotron, Qwen). הרישיונות של ה-upstream שונים. אל תניחו שרישיון אחד חל על כל ה-DictaLM.
- המטריקה הראשית של HeQ צריכה להיות F1, לא Exact Match. המורפולוגיה העברית ותופעת הסופיות הופכות את EM לשביר.
- יידיש ועברית חולקות אלפבית אך הן שפות שונות עם מודלים שונים. אל תאמנו מודל עברי על יידיש או להיפך בלי תכנון מפורש של העברת שפה.
- מראות HuggingFace של HeQ (`pig4431/HeQ_v1`, `Etelis/HeQ_v1`) הם תחזוקה-קהילתית. המקור הקנוני הוא `NNLP-IL/Hebrew-Question-Answering-Dataset` ב-GitHub. אמתו versioning עדכני לפני פרסום תוצאות בנצ'מרק.
- שכבת CulturaX מעל mC4 + OSCAR-2301 יוצרת כפילות כבדה. CulturaX כבר מכיל את mC4 v3.1.0 ו-OSCAR עד 2023-01. בחרו קורפוס אחד או עשו dedupe מפורש (sha256 של טקסט מנורמל) לפני אימון.
- mC4 לא מנוטרל, אבל החתך העברי שלו עם סינון חלש יותר מ-FineWeb-2 או CulturaX. אם אתם צריכים web עברי לפני 2024, העדיפו CulturaX על mC4 גולמי.
- ל-HEBREW-MMLU יש מספר תרגומים קהילתיים ופורקים. אמתו את ה-dataset ID הפעיל לפני פרסום תוצאות בנצ'מרק; מספרים מתרגומים שונים לא בני-השוואה ישירה. `openai/MMMLU` מכסה 14 שפות אבל עברית לא נכללת בקבוצה הרשמית הזאת.
- שמות וריאנטים של DictaLM 3.0 כוללים גם משפחות base/thinking/instruct וגם וריאנטים מקוונטים (FP8, W4A16, GGUF). כשמצטטים תוצאות בנצ'מרק, לוגגו את ה-model ID המדויק מדף ה-HF כולל סיומת קוונטיזציה; מספרים לא עוברים בין קוונטיזציות.
- `oscar-corpus/OSCAR-2301` תחת gating ב-HuggingFace. תכננו לאישור גישה לפני pipelines אימון שתלויים בו.

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
