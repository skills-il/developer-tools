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
| HeQ | `pig4431/HeQ_v1` | הבנת הנקרא, QA חילוץ על ויקיפדיה וגיקטיים. 30,147 שאלות | מוצרים שעונים על שאלות מעל טקסט בעברית: חיפוש, RAG, תמיכה |
| HebrewSentiment | `HebArabNlpProject/HebrewSentiment` | סיווג סנטימנט (חיובי, שלילי, ניטרלי). 41,305 דוגמאות | ניתוח רשתות חברתיות, ביקורות |
| Hebrew Winograd | Winograd Schema בעברית | פתרון כינויי גוף שדורש ידע עולם | מוצרים שצריכים הבנה עברית מעמיקה |
| NeuLabs-TedTalks | Leaderboard subset | איכות תרגום אנגלית-עברית לשני הכיוונים | מוצרי תרגום, אפליקציות רב-לשוניות |
| HebNLI | `HebArabNlpProject/HebNLI` | Natural Language Inference בעברית | סיווג, מודרציה, היגיון לוגי |
| DictaLM סיכום | חבילת Dicta | סיכום אבסטרקטיבי של חדשות עבריות | כלי סיכום, תחקירים |
| DictaLM ניקוד | חבילת Dicta | הוספת ניקוד לטקסט לא מנוקד | כלי חינוך, TTS |
| DictaLM טריוויה ישראלית | חבילת Dicta | ידע על תרבות, גיאוגרפיה, היסטוריה ופוליטיקה בישראל | מוצרי צריכה עם צורך בהקשר תרבותי |

כלל אצבע: התחילו מ-HeQ (הבנה) ועוד משימה אחת שמתאימה למוצר שלכם.

### שלב 2: בחרו את המודלים להשוואה

ברירת מחדל סבירה לצוותי מוצר ישראליים:

| ספק | מודל | קריאה דרך |
|-----|------|------------|
| Anthropic | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | Anthropic SDK |
| OpenAI | משפחת gpt-5 | OpenAI SDK |
| Google | gemini-2.x | Google GenAI SDK |
| AI21 (ישראלי) | jamba-1.5-large, jamba-1.5-mini | AI21 SDK או Amazon Bedrock |
| Dicta (ישראלי, open-weight) | DictaLM-3.0-24B-Base, DictaLM-3.0-Nemotron-12B-Instruct, DictaLM-3.0-1.7B | transformers של HuggingFace או vLLM |
| Meta | Llama-3.x-70B-Instruct | transformers של HuggingFace |
| Mistral | Mistral-Large-Instruct | transformers של HuggingFace |

AI21 מציגה את Jamba 1.5 כתומכת בעברית כ"שפת ליבה". DictaLM היא האפשרות ה-open-weight החזקה ביותר לעברית. תמיד כללו לפחות מודל אחד שילידי-עברית כ-baseline.

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
| Hebrew Winograd | דיוק | — |
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

API-ים משתנים בשקט. לוגגו את גרסת המודל המדויקת מכל תגובה.

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
| Open Hebrew LLM Leaderboard | https://huggingface.co/blog/leaderboard-hebrew | מתודולוגיה, מקורות בנצ'מרקים |
| דאטהסט HeQ | https://huggingface.co/datasets/pig4431/HeQ_v1 | כרטיס, רישיון, פורמט |
| דאטהסט HebrewSentiment | https://huggingface.co/datasets/HebArabNlpProject/HebrewSentiment | רישיון, splits |
| דוח טכני DictaLM 3.0 | https://dicta.org.il/publications/DictaLM_3_0___Techincal_Report.pdf | חבילת הבנצ'מרקים של Dicta |
| Dicta ב-HuggingFace | https://huggingface.co/dicta-il | מודלים עדכניים |
| הכרזת AI21 Jamba | https://www.ai21.com/blog/announcing-jamba-model-family/ | תמיכה בעברית |
| אינדקס משאבי NLP עברי | https://github.com/NNLP-IL/Hebrew-Resources | רשימה מקיפה |

## מלכודות נפוצות

- גרסאות של LLM-ים סגורים משתנות בשקט. תמיד לוגגו את גרסת המודל המדויקת.
- HeQ Exact Match שביר לעברית בגלל צורות סופית וניקוד. השתמשו ב-F1 כמטריקה ראשית.
- Hebrew Winograd עם פחות מ-300 פריטים יש שונות גבוהה בריצה בודדת. דווחו מספר ריצות וסטיות תקן.
- AI21 Jamba משתמש ב-API ייעודי (ai21.com או Amazon Bedrock). אל תניחו ש-OpenAI SDK עובד איתו.
- BLEU על עברית פחות אמין בגלל המורפולוגיה. דווחו גם chrF.
- מודלי DictaLM הבסיסיים אינם chat-tuned. השוואה zero-shot שלהם מול מודלי צ'אט לא הוגנת. השתמשו בגרסאות ה-instruct.

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
