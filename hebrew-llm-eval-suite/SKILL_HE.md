---
name: hebrew-llm-eval-suite
description: "Benchmark and compare LLMs on Hebrew reasoning, comprehension, sentiment, translation, and Israeli cultural knowledge. Wraps HuggingFace Open Hebrew LLM Leaderboard tasks and DictaLM 3.0 benchmarks into a reproducible evaluation harness."
license: MIT
---

# חבילת הערכת LLM בעברית

## בעיה

צוותי מוצר ישראליים בוחרים LLM-ים בעיוורון. אין בנצ'מרק עברי סטנדרטי שאפשר להריץ בשעתיים כדי להשוות Claude מול GPT מול DictaLM מול AI21 Jamba על מקרה שימוש אמיתי. ה-Open Hebrew LLM Leaderboard של HuggingFace בנוי למודלי בסיס ול-few-shot, לא למודלי צ'אט הסטד. DictaLM מפרסמת תוצאות אבל רק על החבילה שלה. הצוותים מנחשים, בודקים באופן לא פורמלי, או סומכים על הצהרות שיווקיות. התוצאה: החלפות מודל יקרות אחרי השקה, או הוצאת מוצרים עבריים על מודלים שנכשלים בשקט אצל דוברי עברית מלידה.

## הוראות

### שלב 1: בחרו את חבילת הבנצ'מרקים הנכונה

בנצ'מרקים שונים בודקים דברים שונים. בחרו את הסט הקטן ביותר שמכסה את מקרה השימוש שלכם.

| בנצ'מרק | HuggingFace ID | מה בודק | מתי להשתמש |
|---------|----------------|---------|-------------|
| HeQ | `Etelis/HeQ_v1` (מראה ב-HF); המקור הקנוני: `github.com/NNLP-IL/Hebrew-Question-Answering-Dataset` | הבנת הנקרא, QA חילוץ על ויקיפדיה וגיקטיים. 30,147 שאלות | מוצרים שעונים על שאלות מעל טקסט בעברית: חיפוש, RAG, תמיכה |
| HebrewSentiment | `HebArabNlpProject/HebrewSentiment` | סיווג סנטימנט (חיובי, שלילי, ניטרלי). 41,305 דוגמאות | ניתוח רשתות חברתיות, ביקורות |
| Hebrew Winograd | Winograd Schema בעברית (`cs.ubc.ca/~vshwartz/resources/winograd_he.jsonl`) | פתרון כינויי גוף שדורש ידע עולם | מוצרים שצריכים הבנה עברית מעמיקה |
| NeuLabs-TedTalks | תת-קבוצה של OPUS NeuLab-TedTalks en-he | איכות תרגום אנגלית-עברית לשני הכיוונים | מוצרי תרגום, אפליקציות רב-לשוניות |
| HebNLI | `HebArabNlpProject/HebNLI` | Natural Language Inference בעברית | סיווג, מודרציה, היגיון לוגי |
| HEBREW-MMLU (ידע כללי) | תרגום עברי של MMLU שבשימוש האקוסיסטם של ה-Open Hebrew LLM Leaderboard (אמתו את ה-ID העדכני ב-HF לפני הרצה; `openai/MMMLU` מכסה 14 שפות אבל עברית לא ברשימה הרשמית) | דיוק ידע כללי על 14 תחומים; התאמה עברית של MMLU | מוצרי צ'אט/RAG כלליים שצריכים ידע עולם רחב בעברית |
| DictaLM סיכום | חבילת Dicta (ראו דוח טכני DictaLM 3.0) | סיכום אבסטרקטיבי של חדשות עבריות | כלי סיכום, תחקירים |
| DictaLM ניקוד | חבילת Dicta | הוספת ניקוד לטקסט לא מנוקד | כלי חינוך, TTS |
| DictaLM טריוויה ישראלית | חבילת Dicta | ידע על תרבות, גיאוגרפיה, היסטוריה ופוליטיקה בישראל | מוצרי צריכה עם צורך בהקשר תרבותי |

כלל אצבע: התחילו מ-HeQ (הבנה) ועוד משימה אחת שמתאימה למוצר שלכם. למוצרים שצריכים ידע עולם רחב, הוסיפו HEBREW-MMLU.

#### פריימוורקים מומלצים

עטפו את הבנצ'מרקים שלמעלה בפריימוורק מבוסס במקום לבנות runner מאפס:

- **`lm-evaluation-harness` (EleutherAI)**: הסטנדרט להערכה משחזרת של מודלי בסיס, בשימוש ב-Open LLM Leaderboard של HuggingFace. משימות עברית כמו HeQ, HebrewSentiment ו-HebNLI לא מגיעות כמשימות native (נכון לאפריל 2026); הוסיפו אותן כקבצי YAML מותאמים אישית שמצביעים על ה-HF dataset IDs שלמעלה. מתאים להשוואה בין מודלי open-weight עם prompting עקבי של few-shot.
- **`inspect_ai` (UK AI Security Institute)**: פריימוורק עם פרימיטיבים של dataset, Task, Solver ו-Scorer, פלוס flows סוכנים מרובי-תורות ו-log viewer. אומץ על ידי Anthropic, DeepMind ועוד לאורך 2024-25. מתאים להערכת מודלי צ'אט וגם graded scoring. הריפו `UKGovernmentBEIS/inspect_evals` מספק יותר מ-200 הערכות מוכנות; משימות עברית לא בערכת ברירת המחדל אבל ההרחבה פשוטה.

בחרו ב-`lm-evaluation-harness` להתאמה ללידרבורד של מודלי בסיס, ב-`inspect_ai` להערכת צ'אטים וסוכנים.

### שלב 2: בחרו את המודלים להשוואה

ברירת מחדל סבירה לצוותי מוצר ישראליים:

| ספק | מודל | קריאה דרך |
|-----|------|------------|
| Anthropic | claude-opus-4-7 (1M context), claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | Anthropic SDK |
| OpenAI | משפחת gpt-5 | OpenAI SDK |
| Google | משפחת gemini-3 (gemini-3-pro, gemini-3-flash), gemini-2.5-pro | Google GenAI SDK |
| AI21 (ישראלי) | jamba-1.6-large, jamba-1.6-mini, jamba-reasoning-3b (משקלים פתוחים), legacy jamba-1.5-large, jamba-1.5-mini | AI21 SDK או Amazon Bedrock |
| Dicta (ישראלי, open-weight) | `dicta-il/DictaLM-3.0-24B-Base`, `dicta-il/DictaLM-3.0-Nemotron-12B-Instruct`, `dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF`, `dicta-il/DictaLM-3.0-24B-Thinking`, וגם `dicta-il/dictalm2.0-instruct` (DictaLM 2.0 על בסיס Mistral 7B) | transformers של HuggingFace או vLLM |
| Cohere (רב-לשוני, תמיכה בעברית) | `CohereLabs/aya-expanse-8b`, `CohereLabs/aya-expanse-32b`, `CohereLabs/aya-23-8B`, `CohereLabs/aya-23-35B` | transformers של HuggingFace או Cohere API |
| מודלים קהילתיים שעברו fine-tune לעברית | `yam-peleg/Hebrew-Mistral-7B`, `yam-peleg/Hebrew-Gemma-11B-Instruct`, `yam-peleg/Hebrew-Mixtral-8x22B` | transformers של HuggingFace |
| Meta | Llama-3.x-70B-Instruct | transformers של HuggingFace |
| Mistral | Mistral-Large-Instruct | transformers של HuggingFace |

AI21 מציגה את Jamba 1.5 כתומכת בעברית כ"שפת ליבה". DictaLM היא האפשרות ה-open-weight החזקה ביותר לעברית. ה-Aya-23 וה-Aya Expanse של Cohere מציגות עברית בין 23 שפות הנתמכות שלהן. המודלים הקהילתיים של Yam Peleg הם המשך-pretraining מ-Mistral, Gemma ו-Mixtral עם טוקנייזרים מורחבים לעברית. תמיד כללו לפחות מודל אחד שילידי-עברית כ-baseline.

### שלב 3: הרימו את ה-harness

השתמשו ב-`scripts/run_eval.py` כ-runner. הוא טוען בנצ'מרקים מ-HuggingFace, קורא ל-API של המודלים, וכותב תוצאות לדיסק.

```bash
pip install datasets transformers anthropic openai google-genai ai21

export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
export AI21_API_KEY=...

python scripts/run_eval.py --benchmark heq --model claude-sonnet-4-6 --limit 100
python scripts/run_eval.py --suite hebrew-core --models claude-sonnet-4-6,gpt-5,jamba-1.5-large
```

### שלב 4: ציון ואגרגציה

| בנצ'מרק | מטריקה ראשית | משנית |
|---------|--------------|--------|
| HeQ | F1, Exact Match | דיוק unanswerable |
| HebrewSentiment | דיוק | Macro-F1 |
| Hebrew Winograd | דיוק | אין |
| תרגום | BLEU, chrF | העדפה אנושית |
| HebNLI | דיוק | Macro-F1 |
| סיכום | ROUGE-L, BERTScore-HE | העדפה אנושית |
| ניקוד | דיוק מילה | דיוק תו |
| טריוויה | דיוק | פירוט לפי קטגוריה |

השתמשו ב-`scripts/score_results.py` שמטפל בנרמול עברי (צורות סופית, ניקוד, רווחים).

### שלב 5: הפיקו scorecard

השתמשו ב-`scripts/make_scorecard.py` להפקת דוח השוואה: JSON לשימוש תכנותי, markdown עם טבלת מודלים-נגד-בנצ'מרק, ניתוח פער לכל בנצ'מרק, והמלצה משוקללת.

### שלב 6: שלטו ברעש סטטיסטי

- הריצו כל מודל לפחות 3 פעמים ודווחו ממוצע וסטיית תקן
- לפחות 500 דוגמאות לכל בנצ'מרק (רצוי 1000+)
- קבעו פרמטרי דגימה זהים לכל המודלים
- לוגגו seeds היכן שרלוונטי
- לתרגום השתמשו ב-BLEU ו-chrF יחד

### שלב 7: טפלו במודלי מקור סגור

API-ים משתנים בשקט. לוגגו את גרסת המודל המדויקת מכל תגובה. ל-Claude, השתמשו ב-model ID מתוארך (לדוגמה `claude-opus-4-7-20260415`) ולוגגו את שדה `model` שמוחזר ב-response. ל-OpenAI, לוגגו את שדה `model` מה-response ואת `system_fingerprint` כשהוא זמין. ל-Gemini, לוגגו את `modelVersion` מה-metadata של ה-response. זה מה שהופך את ה-scorecards ההיסטוריים לבני-שחזור.

### שלב 8: התחשבו בהוגנות הטוקנייזר

הבדלים בין טוקנייזרים משפיעים מהותית על עלות, השהייה ואפילו דיוק בהערכות עבריות:

- **טוקנייזרים BPE** (GPT-4, Llama-3, Mistral) מתייחסים לעברית כשפת long-tail. הפריון (טוקנים למילה עברית) הוא בדרך כלל פי 3-5 מאשר באנגלית. prompt של 1,000 מילים בעברית יכול להתנפח ל-4,000-5,000 טוקנים.
- **טוקנייזרים SentencePiece עם הרחבות עברית** (DictaLM 2.0/3.0, Hebrew-Mistral-7B, Hebrew-Gemma-11B) מזריקים טוקנים ייעודיים לעברית. DictaLM 2.0 מדווחת על דחיסה של 2.76 טוקנים למילה עברית לעומת 5.78 של Mistral-7B.
- **טוקנייזרים של Aya/Cohere** מכוונים ל-23 שפות הנתמכות כולל עברית, עם פריון קרוב יותר למודלים native מאשר ל-BPE רגיל.

השלכות:
- תמיד לוגגו tokens-in ו-tokens-out לכל בנצ'מרק, לא רק את ספירת הדגימות, בהשוואת עלות או השהייה
- מודל עם F1 גרוע יותר אבל פריון טוקנייזר טוב פי 3 עשוי להיות הבחירה הנכונה למוצר רגיש לעלות
- מודלים עם פריון גבוה מגיעים מהר יותר למגבלת הקונטקסט; חתכו בהוגנות לאורך כל המודלים בהשוואה

דווחו "טבלת פריון" לצד ה-scorecard: מודל, ממוצע טוקנים למילה עברית על אותו פסקת ייחוס (אנחנו משתמשים ב-1,000 המילים הראשונות של ה-test set של HeQ כדגימה קבועה). `scripts/measure_fertility.py` מחשב זאת.

### שלב 9: נרמלו טקסט עברי לפני ניקוד

ניקוד HeQ כבר קורא לנרמול תואם-Dicta. גם הערכות סנטימנט, NLI ותרגום צריכות נרמול אחרת תראו הפסדים מלאכותיים:

- **הסירו ניקוד** לפני השוואת מחרוזות. תוויות הייחוס ותפוקות המודל יכולות להיבדל רק בנוכחות הניקוד. השתמשו בטווח Unicode U+05B0-U+05BC, U+05BD, U+05BF, U+05C1-U+05C2, U+05C7 פלוס סימני הטעמים U+0591-U+05AF.
- **נרמלו צורות סופיות** ל-EM של HeQ ולכל scorer מבוסס-מחרוזת: כ/ך, מ/ם, נ/ן, פ/ף, צ/ץ. החליפו את הצורה הסופית בצורת הבסיס בשני הצדדים.
- **כווצו רווחים** כולל non-breaking space (U+00A0), zero-width joiner (U+200D), וגרש/גרשיים עבריים (U+05F3-U+05F4) בהשוואת מחרוזות.
- **המירו רישיות לטינית לאות קטנה** בתפוקות תרגום, אבל אל תיגעו בעברית (אין רישיות בעברית).
- **לסנטימנט ו-NLI**, תפוקת המודל יכולה להיות מילת תווית מנוקדת או עם ה' הידיעה. הסירו ניקוד והפרידו את התחילית ה־ לפני מיפוי לאוצר התוויות.

`scripts/score_results.py --normalize hebrew-strict` מפעיל את כל אלה. `--normalize hebrew-loose` מדלג על נרמול סופיות והסרת תחיליות בהערכות תרגום, איפה שהם היו משנים את המשמעות.

### שלב 10: זהירויות LLM-as-judge לעברית

ל-graded scoring (סיכום, תרגום, QA פתוח), LLM judge נוח אבל יש לו כשלים ספציפיים לעברית:

- **הטיה לסגנון תשובה אנגלי.** רוב מודלי השיפוט אומנו על שיפוטים בעיקר באנגלית. הם נוטים לתת ציון גבוה לתשובות עבריות שמחקות סגנון אנגלי (ארוך, מסויג, מסויג עוד) על פני סגנון ישראלי native (ישיר, תכליתי, אידיומטי). זה מעניש באופן שיטתי מודלים native לעברית.
- **חיובי-שגוי על ערבוב סקריפטים.** judge יכול לתת ציון גבוה יותר לתשובה עברית עם מונחים טכניים באנגלית מאשר לאותה תשובה בעברית טהורה, כי תשובות מעורבות סקריפט נראות "אינפורמטיביות" יותר למודל שאומן על אנגלית.
- **בלבול בניקוד וסופיות.** חלק ממודלי השיפוט מענישים עברית נכונה שמשתמשת או משמיטה ניקוד בצורה שונה מהתפלגות האימון שלהם.
- **פערים בהיכרות תרבותית.** מודלי שיפוט שאומנו בעיקר על נתונים באנגלית מפספסים הקשר ישראלי דק (סלנג, ראשי תיבות צבאיים, חגים) ועלולים לסמן תשובות מדויקות כשגויות.

הפחתות:
- השתמשו לפחות בשני מודלי שיפוט מספקים שונים ודווחו הסכמה; סמנו אי-הסכמות לבדיקה אנושית
- כיילו את ה-judge עם 30-50 דוגמאות מדורגות אנושית ודווחו הסכמת judge-vs-human לפני שאתם סומכים בקנה מידה
- העדיפו judges ילידיי-עברית או רב-לשוניים חזקים (משפחת Claude, Gemini 2.x, Aya Expanse) על פני judges שמתמחים באנגלית
- לסנטימנט, NLI ו-HeQ העדיפו מטריקות מבוססות-ייחוס (דיוק, F1) על פני LLM-as-judge לחלוטין

## דוגמאות

### דוגמה 1: בחירת מודל סיכום למוצר חדשות עברי

המשתמש אומר: "אנחנו בונים פיצ'ר סיכום חדשות ואנחנו צריכים לבחור בין Claude, GPT, ו-DictaLM."

פעולות:
1. בחרו בנצ'מרקים: HeQ, DictaLM סיכום, Hebrew Winograd
2. הריצו `python scripts/run_eval.py --suite hebrew-summary --models claude-sonnet-4-6,gpt-5,DictaLM-3.0-24B-Base --samples 1000 --runs 3`
3. סקרו את ה-scorecard
4. אמתו שני המובילים על דגימה של כתבות אמיתיות עם מעריכים אנושיים
5. בחרו לפי ציון משוקלל פלוס עלות והשהייה

תוצאה: בחירת מודל מבוססת נתונים.

### דוגמה 2: מעקב אחרי רגרסיה עברית אחרי שדרוג ספק

המשתמש אומר: "Anthropic שחררה גרסה חדשה. האיכות בעברית השתפרה או ירדה?"

פעולות:
1. הריצו את החבילה הסטנדרטית מול הגרסה החדשה והקודמת
2. השוו scorecards עם `scripts/diff_scorecards.py prev.json new.json`
3. סמנו כל בנצ'מרק עם ירידה של יותר מ-2 נקודות כרגרסיה
4. קבלו החלטה

תוצאה: החלטת שדרוג מבוססת.

## משאבים מצורפים

### סקריפטים
- `scripts/run_eval.py` -- ה-harness הראשי. טוען בנצ'מרקים, קורא ל-API-ים, כותב תוצאות.
- `scripts/score_results.py` -- מחשב מטריקות עם נרמול עברי.
- `scripts/make_scorecard.py` -- מייצר scorecard ב-JSON ו-markdown עם המלצה משוקללת.

### מסמכי עזר
- `references/benchmark-catalog.md` -- קטלוג מלא של בנצ'מרקים עבריים.
- `references/prompt-templates.md` -- תבניות prompt zero-shot, few-shot, ו-CoT בעברית ובאנגלית.

## שרתי MCP מומלצים

אין צורך ב-MCP להרצת הערכות.

## קישורי עזר

| מקור | URL | מה לבדוק |
|------|-----|---------|
| Open Hebrew LLM Leaderboard (space חי) | https://huggingface.co/spaces/hebrew-llm-leaderboard/leaderboard | דירוגים חיים, הגשות מודלים, ציוני בנצ'מרק עדכניים |
| Open Hebrew LLM Leaderboard (בלוג ההכרזה) | https://huggingface.co/blog/leaderboard-hebrew | מתודולוגיה, מקורות בנצ'מרקים |
| דאטהסט HeQ (מראה ב-HF) | https://huggingface.co/datasets/Etelis/HeQ_v1 | כרטיס, פורמט. מקור קנוני: github.com/NNLP-IL/Hebrew-Question-Answering-Dataset |
| דאטהסט HebrewSentiment | https://huggingface.co/datasets/HebArabNlpProject/HebrewSentiment | רישיון, splits |
| דאטהסט HebNLI | https://huggingface.co/datasets/HebArabNlpProject/HebNLI | רישיון, splits, מבנה premise-hypothesis |
| דוח טכני DictaLM 3.0 | https://dicta.org.il/publications/DictaLM_3_0___Techincal_Report.pdf | חבילת הבנצ'מרקים של Dicta (לב: שם הקובץ "Techincal" ולא "Technical") |
| Dicta ב-HuggingFace | https://huggingface.co/dicta-il | DictaLM 3.0 (24B-Base, Nemotron-12B-Instruct, 1.7B-Thinking-GGUF, 24B-Thinking) ו-DictaBERT |
| ארגון Cohere Aya | https://huggingface.co/CohereLabs | Aya-23 (8B/35B) ו-Aya Expanse (8B/32B) רב-לשוניים עם תמיכה בעברית |
| מודלי עברית של Yam Peleg | https://huggingface.co/yam-peleg | Hebrew-Mistral-7B, Hebrew-Gemma-11B-Instruct, Hebrew-Mixtral-8x22B |
| הכרזת AI21 Jamba | https://www.ai21.com/blog/announcing-jamba-model-family/ | תמיכה בעברית |
| EleutherAI lm-evaluation-harness | https://github.com/EleutherAI/lm-evaluation-harness | פריימוורק סטנדרטי להערכת מודלי בסיס; משימות עברית מתווספות כ-YAML מותאם |
| UK AISI Inspect AI | https://github.com/UKGovernmentBEIS/inspect_ai | פריימוורק להערכת צ'אטים עם פרימיטיבי סוכן ו-graded scoring |
| אינדקס משאבי NLP עברי | https://github.com/NNLP-IL/Hebrew-Resources | רשימה מקיפה |

## מלכודות נפוצות

- גרסאות של LLM-ים סגורים משתנות בשקט. scorecard מלפני שישה חודשים אולי לא משקף את ההתנהגות הנוכחית. תמיד לוגגו את גרסת המודל המדויקת שמוחזרת מה-API ועשו ריצה מחדש לפני שאתם סומכים על מספרים היסטוריים.
- HeQ Exact Match שביר לעברית בגלל צורות סופית, ניקוד ושונויות רווחים שגורמות ל-false negatives. השתמשו ב-F1 כמטריקה ראשית ודווחו EM רק עם נרמול תואם-Dicta מפורש. סוכנים שמדווחים EM גולמי מורידים את הביצועים של כל מודל.
- Hebrew Winograd עם פחות מ-300 פריטים יש שונות גבוהה בריצה בודדת. דווחו תוצאות רק עם מספר ריצות וסטיות תקן. סוכנים שמריצים פעם ומחשיבים את התוצאה כסופית יחליפו דירוגי מודלים בין ריצות.
- AI21 Jamba משתמש ב-API ייעודי (ai21.com או Amazon Bedrock). אל תניחו ש-OpenAI SDK עובד איתו. השתמשו ב-AI21 Python SDK או Bedrock runtime.
- BLEU על עברית פחות אמין מ-BLEU על שפות אירופיות בגלל המורפולוגיה. דווחו chrF לצד BLEU ובדקו ידנית דגימה של תפוקות עם ציון נמוך. סוכנים שסומכים רק על BLEU מפספסים את אות האיכות האמיתי.
- מודלי DictaLM הבסיסיים אינם chat-tuned כברירת מחדל. השוואה zero-shot שלהם מול מודלי צ'אט כמו Claude לא הוגנת. השתמשו בגרסאות ה-instruct של Dicta (Nemotron-12B-Instruct, dictalm2.0-instruct) או ב-few-shot prompting עם דוגמאות משימה מפורשות.
- פריון טוקנייזר מטה השוואות עלות והשהייה. מודל BPE רגיל יכול להשתמש בפי 3-5 טוקנים למילה עברית מאשר טוקנייזר SentencePiece מכוון-עברית. תמיד לוגגו tokens-in/tokens-out לכל בנצ'מרק, לא רק את ספירת הדגימות.
- LLM-as-judge לעברית מוטה לסגנון תשובה אנגלי (ארוך, מסויג) על פני סגנון ישראלי native (ישיר, תכליתי). השתמשו בלפחות שני judges מספקים שונים, כיילו מול 30-50 דירוגים אנושיים, והעדיפו מטריקות מבוססות-ייחוס איפה שהן קיימות.
- ל-HEBREW-MMLU יש מספר תרגומים קהילתיים ופורקים. אמתו את ה-dataset ID הפעיל לפני פרסום בנצ'מרק; מספרים מתרגומים שונים אינם בני-השוואה.

## פתרון בעיות

### שגיאה: "הספק חסם בגלל יותר מדי בקשות"
סיבה: יותר מדי קריאות מקביליות.
פתרון: הקטינו את `--parallel` ב-`run_eval.py`.

### שגיאה: "ציון HeQ EM קרוב לאפס לכל המודלים"
סיבה: נרמול EM לא מופעל.
פתרון: השתמשו ב-F1 או הפעילו `scripts/score_results.py --normalize hebrew`.

### שגיאה: "BLEU בתרגום סותר את המעריכים האנושיים"
סיבה: BLEU לא אמין על עברית.
פתרון: דווחו גם chrF ובדקו ידנית דגימה של התוצאות הנמוכות.
