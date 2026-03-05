---
name: skills-il-skill-creator
description: >-
  Interactive workflow for creating new skills for the skills-il organization --
  guides through category selection, use case definition, folder scaffolding,
  YAML frontmatter generation with bilingual metadata, instruction writing, Hebrew
  companion creation, and validation. Use when user asks to "create a new skill",
  "scaffold a skill for skills-il", "write a SKILL.md", "contribute a skill",
  "new skill template", or "liztor skill chadash". Enforces skills-il conventions:
  kebab-case naming, Hebrew transliterations, bilingual display_name/display_description,
  progressive disclosure, and validate-skill.sh compliance. Do NOT use for editing
  existing skills, creating skills for non-skills-il platforms, or generic markdown
  file creation.
license: MIT
allowed-tools: 'Bash(python:*) Bash(./scripts/*) WebFetch'
compatibility: >-
  No network required for scaffolding. WebFetch optional for pulling latest
  conventions. Works with Claude Code, Claude.ai, Cursor.
metadata:
  author: skills-il
  version: 1.2.0
  category: developer-tools
  tags:
    he:
      - יוצר-סקילים
      - פיגומים
      - תבנית
      - מפתחים
      - תהליך-עבודה
      - ישראל
    en:
      - skill-creator
      - scaffolding
      - template
      - developer
      - workflow
      - israel
  display_name:
    he: יוצר סקילים skills-il
    en: Skills-IL Skill Creator
  display_description:
    he: >-
      תהליך אינטראקטיבי ליצירת סקילים חדשים לארגון skills-il -- הנחיה לבחירת
      קטגוריה, הגדרת מקרי שימוש, יצירת תיקייה, כתיבת frontmatter דו-לשוני,
      הוראות, קובץ עברי נלווה ואימות. השתמש כשמשתמש מבקש "ליצור skill חדש",
      "תבנית skill", "לתרום skill" או "scaffold skill".
    en: >-
      Interactive workflow for creating new skills for the skills-il organization --
      guides through category selection, use case definition, folder scaffolding,
      YAML frontmatter generation with bilingual metadata, instruction writing, Hebrew
      companion creation, and validation. Use when user asks to "create a new skill",
      "scaffold a skill for skills-il", "write a SKILL.md", "contribute a skill",
      "new skill template", or "liztor skill chadash". Do NOT use for editing
      existing skills or creating skills for non-skills-il platforms.
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
    - openclaw
---

# יוצר סקילים skills-il

## סקירה

סקיל זה מנחה אותך בתהליך יצירת סקיל חדש ואיכותי לארגון skills-il. הוא עוקב אחר המדריך המלא של Anthropic ליצירת סקילים ואוכף את כל המוסכמות של הארגון.

כל סקיל שתיצור יכלול: SKILL.md עם frontmatter מאומת, מטאדאטה דו-לשונית (עברית + אנגלית), הוראות שלב-אחר-שלב עם טבלאות ודוגמאות קוד, קובץ עברי נלווה (SKILL_HE.md), ויעבור את כל בדיקות האימות.

## הוראות

### שלב 1: בחירת קטגוריה

שאל את המשתמש לאיזה ריפוזיטורי הסקיל שייך:

| קטגוריה | ריפו | תחום |
|----------|------|------|
| מס ופיננסים | tax-and-finance | חשבוניות, שכר, מע"מ, תשלומים, פנסיה |
| שירותי ממשלה | government-services | data.gov.il, ביטוח לאומי, רשם, תחבורה |
| אבטחה וציות | security-compliance | חוק הגנת הפרטיות, סייבר, מחקר משפטי |
| לוקליזציה | localization | RTL, עיבוד שפה עברית, OCR, תזמון שבת |
| כלי פיתוח | developer-tools | אימות ת.ז., המרת תאריכים, פורמט טלפון |
| תקשורת | communication | SMS, וואטסאפ, Monday.com, שוק העבודה |
| אוכל ומסעדות | food-and-dining | מסעדות, מתכונים, כשרות, משלוחים |
| טכנולוגיה משפטית | legal-tech | חוזים, מחקר משפטי, ציות |
| שיווק וצמיחה | marketing-growth | SEO, רשתות חברתיות, פרסום, קמפיינים, ASO |
| חינוך | education | פלטפורמות למידה, שיעורים פרטיים, כלים אקדמיים |
| שירותי בריאות | health-services | קופות חולים, בתי מרקחת, רשומות רפואיות, תורים |

אם הסקיל לא מתאים לאף קטגוריה, דון עם המשתמש אם הוא שייך לקטגוריה קיימת או מצדיק ריפו חדש.

### שלב 2: איסוף פרטי היוצר (חובה)

לפני שממשיכים, חובה לשאול את המשתמש על פרטי היוצר שלו. הפרטים נדרשים להגשת הסקיל לספריית Skills IL.

שאל את המשתמש:

> "מה השם שלך? השם יוצג כיוצר הסקיל בספריית Skills IL. שם המשתמש שלך ב-GitHub גם מתאים."

חכה לתשובת המשתמש ושמור כ-`creator_name`.

לאחר מכן שאל:

> "מה כתובת האימייל שלך? זה נדרש כדי שנוכל לעדכן אותך כשהסקיל מתפרסם, מקבל המלצה, או אם צריך ליצור איתך קשר לגבי עדכונים. הכתובת לא תוצג באופן ציבורי."

חכה לתשובת המשתמש ושמור כ-`creator_email`.

**כללים:**
- `creator_name` הוא שדה חובה. ברירת מחדל: שם משתמש GitHub אם המשתמש מעדיף לא לתת שם מלא.
- `creator_email` הוא שדה **חובה** וחייב להיות כתובת אימייל תקינה. אסור להמשיך בלעדיו.
- שמור את שני הערכים -- הם ישמשו בשדה `metadata.author` ובהגשה לספרייה.
- אם המשתמש מסרב לתת אימייל, הסבר שזה חובה לתהליך ההגשה ולא יקבל התראות על הסקיל בלעדיו.

### שלב 3: הגדרת מקרי שימוש

חשוב: לפני כתיבת קוד, הגדר 2-3 מקרי שימוש קונקרטיים.

לכל מקרה שימוש, תעד:
- **טריגר**: מה המשתמש יאמר (באנגלית ובעברית)
- **שלבים**: איזה תהליך רב-שלבי נדרש
- **כלים**: אילו כלים נחוצים (מובנים או MCP)
- **תוצאה**: איך נראית הצלחה

דוגמה:
```
מקרה שימוש: אימות חשבונית אלקטרונית
טריגר: "לאמת חשבונית אלקטרונית" או "validate e-invoice"
שלבים:
1. ניתוח שדות החשבונית
2. אימות מספר הקצאה
3. בדיקה מול כללי שע"מ
תוצאה: חשבונית מאומתת עם דוח עבר/נכשל
```

### שלב 4: בדיקת עובדות של מידע תחומי

לפני כתיבת תוכן כלשהו, אמת את העובדות המרכזיות שהסקיל שלך יפנה אליהן. זה חשוב במיוחד לסקילים שעוסקים בחוקים ישראליים, רגולציה, שירותי ממשלה, כללים פיננסיים או מדיניות בריאות, כי אלה משתנים לעיתים קרובות.

**מה לאמת:**
- ספי חוק וגבולות (למשל: תקרת תביעות קטנות, מדרגות מס, הגבלות גיל)
- תהליכים ממשלתיים וטפסים (למשל: הליכי הגשה, מסמכים נדרשים)
- שמות מוסדות ופרטי קשר (למשל: מספרי טלפון, אתרים, כתובות)
- תמחור ועמלות (למשל: השתתפות עצמית, אגרות הגשה, עלויות שירות)
- שינויי חקיקה אחרונים שנכנסו לתוקף השנה

**איך לאמת:**
- חפש במקורות ממשלתיים רשמיים (gov.il, כנסת, ביטוח לאומי)
- בדוק תאריכים של השנה הנוכחית בחיפושים שלך (חוקים וספים משתנים מדי שנה)
- הצלב לפחות 2 מקורות לעובדות קריטיות כמו סכומי כסף או דרישות חוקיות
- רשום תאריך אימות כדי שניתן יהיה לעדכן את הסקיל כשעובדות משתנות

**מה לרשום:**
לכל עובדה מרכזית, ציין: העובדה, המקור, ותאריך האימות. כלול אלה כהפניות בתוך הוראות ה-SKILL.md (למשל: "38,900 ש"ח נכון לינואר 2025").

אסור לדלג על שלב זה. סקיל עם עובדות מיושנות או שגויות (שיעור מס לא נכון, חוק שפג תוקף, מספר טלפון שגוי) גרוע יותר מאשר בלי סקיל בכלל.

### שלב 5: יצירת מבנה תיקייה

הרץ את סקריפט ה-scaffolding:

```bash
python scripts/scaffold-skill.py --name <skill-name> --category <category-repo>
```

הסקריפט יוצר:
```
<skill-name>/
├── SKILL.md          # תבנית עם שלד frontmatter
├── SKILL_HE.md       # שלד קובץ עברי
├── scripts/          # לסקריפטים
└── references/       # לתיעוד עזר
```

בדוק את הפלט:
- שם תיקייה ב-kebab-case
- ללא רווחים, קו תחתון או אותיות גדולות
- השם לא מכיל "claude" או "anthropic"
- אין README.md בתוך התיקייה

### שלב 6: כתיבת YAML Frontmatter

צור את ה-frontmatter לפי המבנה המדויק. השתמש ב-`creator_name` שנאסף בשלב 2 בשדה `author`:

```yaml
---
name: <skill-name>
description: >-
  [מה הסקיל עושה]. Use when user asks to [triggers],
  "[תעתיק עברי]", or [scenarios]. [יכולות מרכזיות].
  Do NOT use for [אנטי-טריגרים].
license: MIT
allowed-tools: '<כלים אם נדרש>'
compatibility: >-
  [דרישות רשת/מערכת]. Works with Claude Code, Claude.ai, Cursor.
metadata:
  author: <creator_name משלב 2>
  version: 1.0.0
  category: <category>
  tags:
    he:
      - <tag1-he>
      - <tag2-he>
      - ישראל
    en:
      - <tag1>
      - <tag2>
      - israel
  display_name:
    he: "<שם בעברית>"
    en: <English Name>
  display_description:
    he: "<תיאור בעברית>"
    en: >-
      <English description>
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
    # - openclaw          # הוסף רק אם הסקיל מאומת כתואם OpenClaw
---
```

**סוכנים נתמכים:** כלול את כל הסוכנים הסטנדרטיים (claude-code עד codex) כברירת מחדל. אם הסקיל תלוי בתכונות ספציפיות לסוכן (למשל כלי MCP זמינים רק ב-Claude Code), הסר סוכנים שלא יכולים לתמוך ותעד מדוע בשדה `compatibility`.

**תאימות OpenClaw (חובה לשאול):** לפני סיום ה-frontmatter, שאל את המשתמש:

> "האם הסקיל הזה תואם ל-OpenClaw? OpenClaw הוא סוכן קוד בקוד פתוח. סמן כתואם רק אם הסקיל לא תלוי בתכונות ספציפיות ל-Claude. האם להוסיף `openclaw` לרשימת הסוכנים?"

- אם המשתמש מאשר: הסר את ההערה מ-`openclaw`
- אם לא בטוח: השאר מוער
- אסור להניח תאימות -- תמיד שאל

**תגיות דו-לשוניות (חובה לשאול):** אחרי הגדרת התגיות באנגלית, שאל:

> "אנא ספק תרגום עברי לכל תגית. מערכי `he` ו-`en` חייבים להיות באותו אורך. מהם המקבילים בעברית?"

- שני המערכים `he` ו-`en` הם **חובה**
- חייבים להיות **באותו אורך**
- אין מחרוזות ריקות
- מונחים טכניים ללא מקבילה עברית יישארו באנגלית בשניהם

**כללי תיאור (קריטי):**
- נוסחה: `[מה עושה] + [מתי להשתמש] + [יכולות] + [מתי לא להשתמש]`
- מתחת ל-1024 תווים
- אין סוגריים משולשים (`<>`) ב-frontmatter
- כלול ביטויי טריגר שמשתמשים באמת יגידו
- כלול תעתיקים עבריים במירכאות
- סיים עם `Do NOT use for` + הפניה לסקילים קשורים

**תבניות allowed-tools:**
- ללא כלים: השמט את השדה
- סקריפטי Python: `'Bash(python:*)'`
- Python + רשת: `'Bash(python:*) WebFetch'`
- כלי CLI מרובים: `'Bash(python:*) Bash(curl:*) WebFetch'`
- התקנות pip: `'Bash(python:*) Bash(pip:*)'`

### שלב 7: כתיבת הוראות

כתוב את גוף ה-SKILL.md לפי מבנה זה:

```markdown
# <שם הסקיל>

## Instructions

### Step 1: <שלב ראשון>
<הסבר ברור עם טבלאות ודוגמאות קוד>

### Step N: <שלב הבא>
...

## Examples

### Example 1: <תרחיש נפוץ>
User says: "<בקשה טיפוסית>"
Actions:
1. ...
Result: <תוצאה>

## Bundled Resources

### Scripts
- `scripts/<name>.py` -- <מה עושה>. Run: `python scripts/<name>.py --help`

### References
- `references/<name>.md` -- <מה מכיל>. Consult when <מתי>.

## Troubleshooting

### Error: "<שגיאה>"
Cause: <סיבה>
Solution: <פתרון>
```

**כללי כתיבה:**
- היה ספציפי: `"הרץ python scripts/validate.py --input {filename}"` ולא "אמת את הנתונים"
- השתמש בטבלאות למטריצות החלטה, מיפוי שדות, נתוני השוואה
- כלול קוד inline לאלגוריתמים וקריאות API
- שמור על SKILL.md מתחת ל-5,000 מילים -- העבר תיעוד מפורט ל-`references/`
- הפנה למשאבים מצורפים עם הנחיית "Consult when..."
- כלול 2-4 דוגמאות למקרים נפוצים וקצה
- כלול 2-4 רשומות פתרון בעיות לשגיאות צפויות
- שלב מונחים עבריים inline: "תשלומים (tashlumim)"

**חשיפה הדרגתית:**
- SKILL.md = הוראות ליבה (מה שהסוכן צריך ברוב הזמן)
- `references/` = מפרטים מפורטים, תיעוד API מלא, מקרי קצה (נטענים לפי דרישה)
- `scripts/` = עוזרים ניתנים להרצה (מופעלים לפי צורך)

### שלב 8: יצירת מסמכי עזר וסקריפטים

כל סקיל צריך לכלול קבצי עזר וסקריפטים. אלה לא תוספות אופציונליות; הם ההבדל בין סקיל דק לבין סקיל באיכות ייצור.

**מסמכי עזר (תיקיית `references/`):**

צור 2-3 קבצי עזר שמכילים מידע מפורט מדי ל-SKILL.md. דפוסים נפוצים:

| דפוס | דוגמה | מתי להשתמש |
|-------|--------|-------------|
| ספרייה/רשימה | `hospital-directory.md`, `crisis-hotlines-directory.md` | הסקיל מכסה תחום עם מוסדות, שירותים או אנשי קשר רבים |
| מדריך מפורט | `fair-rental-law-summary.md`, `ivf-process-detailed.md` | תהליך או חוק דורש יותר פירוט ממה שנכנס להוראות |
| מילון מונחים | `hebrew-rental-glossary.md` | הסקיל משתמש במונחים מקצועיים עבריים (50+ מונחים) |
| רשימת בדיקה | `contract-checklist.md`, `evidence-guide.md` | משתמשים צריכים רשימת אימות או הכנה שלב-אחר-שלב |
| טבלת השוואה | `universities-comparison.md`, `city-rental-guide.md` | משתמשים צריכים להשוות אפשרויות על פני מספר מימדים |
| תבנית | `demand-letter-template.md` | משתמשים צריכים נקודת התחלה למסמך או טופס |

כל קובץ עזר צריך:
- להיות מתחת ל-3,000 מילים
- להשתמש ב-markdown עם כותרות וטבלאות ברורות
- לכלול מונחים עבריים בסוגריים
- להיות מקושר מ-SKILL.md עם הנחיית "Consult when..."

**סקריפטים (תיקיית `scripts/`):**

צור 1-2 סקריפטי Python לחישובים או חיפושי מידע. דפוסים נפוצים:

| דפוס | דוגמה | מתי להשתמש |
|-------|--------|-------------|
| מחשבון | `sekher-calculator.py`, `filing-fee-calculator.py` | הסקיל כולל נוסחאות, חישובי מס או הערכת עמלות |
| בודק זכאות | `fertility-coverage-checker.py` | הסקיל כולל כללי זכאות מבוססי קריטריונים מרובים |
| מעריך עלויות | `therapy-cost-estimator.py`, `rental-budget-calculator.py` | משתמשים צריכים להשוות עלויות בין אפשרויות |
| מדד/התאמה | `rent-index-calculator.py` | הסקיל כולל ערכים צמודי מדד או התאמות מבוססות זמן |

כל סקריפט צריך:
- להשתמש ב-`#!/usr/bin/env python3` shebang
- לכלול argparse עם `--help`
- להכיל docstring ברור שמסביר שימוש
- להשתמש רק ב-stdlib (ללא תלויות חיצוניות)
- לכלול אימות קלט עם הודעות שגיאה ברורות
- להדפיס תוצאות בפלט נקי ומעוצב

**עדכון SKILL.md:** הוסף חלק `## Bundled Resources` (לפני `## Troubleshooting`) שמפרט את כל המסמכים והסקריפטים עם הנחיית "Consult when...".

**עדכון SKILL_HE.md:** הוסף חלק תואם `## משאבים מצורפים` עם תיאורים בעברית.

### שלב 9: יצירת קובץ עברי נלווה (SKILL_HE.md)

צור SKILL_HE.md עם אותו מבנה בעברית:
- תרגם את ההוראות לעברית
- השאר בלוקי קוד, שמות שדות והפניות API באנגלית
- השתמש במונחים עבריים מקוריים (לא תעתיקים)
- שמור על מספור שלבים וחלקים זהה

קובץ העברית משתמש באותו frontmatter כמו SKILL.md (ה-frontmatter נשאר באנגלית).

### שלב 10: אימות והכנה להגשה

הרץ את סקריפט האימות:

```bash
./scripts/validate-skill.sh <skill-name>/SKILL.md
```

הסקריפט בודק 9 כללים:

| # | כלל | תיקון נפוץ |
|---|------|-----------|
| 1 | הקובץ בדיוק `SKILL.md` | שנה שם אם אותיות שגויות |
| 2 | מתחיל ב-`---` | הוסף frontmatter |
| 3 | `name` ב-kebab-case, תואם לתיקייה | תקן שם |
| 4 | אין "claude"/"anthropic" בשם | בחר שם אחר |
| 5 | תיאור: קיים, מתחת ל-1024, יש טריגר, אין `<>` | קצר או הוסף "Use when" |
| 6 | אין `<>` ב-frontmatter | הסר סוגריים משולשים |
| 7 | גוף מתחת ל-5,000 מילים | העבר תוכן ל-references/ |
| 8 | אין README.md בתיקיית הסקיל | מחק README.md |
| 9 | אין סודות מקודדים | הסר מפתחות API |

לאחר שהאימות עובר, בדוק מול רשימת האיכות:
- [ ] עובדות תחום אומתו מול מקורות רשמיים (שלב 4)
- [ ] התיאור כולל מה ומתי
- [ ] ההוראות ספציפיות ובנות ביצוע
- [ ] הדוגמאות מכסות 2+ תרחישים אמיתיים
- [ ] פתרון בעיות מכסה שגיאות צפויות
- [ ] קובץ עברי קיים ומבנה החלקים תואם ל-SKILL.md 1:1
- [ ] לפחות 2 קבצי עזר ב-`references/` עם הנחיית "Consult when..."
- [ ] לפחות סקריפט עזר 1 ב-`scripts/` עם argparse ו-`--help`
- [ ] אין בעיות אבטחה (סודות, וקטורי הזרקה)
- [ ] רשימת `supported_agents` מדויקת
- [ ] `metadata.tags` עם מערכי `he` ו-`en` באורך שווה ללא מחרוזות ריקות
- [ ] `creator_name` ו-`creator_email` נאספו מהמשתמש (שלב 2)

### שלב 11: הגשה או פריסה

לאחר שהאימות עובר, השלב הבא תלוי בתפקידך:

**לתורמים מהקהילה (רוב המשתמשים):**

הגש את הסקיל דרך האתר בכתובת https://agentskills.co.il/he/submit (אנגלית: /en/submit).

1. בחר סוג הגשה: "ריפוזיטורי קיים" (אם דחפת את הסקיל לריפו GitHub) או "הצעה" (אם אתה רוצה שצוות skills-il ייצור את הריפו)
2. מלא את הטופס עם: כתובת ריפו GitHub, שם יוצר ואימייל (משלב 2)
3. צוות skills-il יבדוק את ההגשה, יריץ ניתוח אבטחה ויפרסם אם עובר

**למנהלי ארגון skills-il:**

פרוס ישירות לריפו הקטגוריה ולמסד הנתונים:

1. שכפל את ריפו הקטגוריה: `gh repo clone skills-il/<category-repo>`
2. העתק את תיקיית הסקיל לתוך הריפו
3. בצע commit ודחוף ל-master:
   ```bash
   git add <skill-name>/
   git commit -m "feat: add <skill-name> skill"
   git push origin master
   ```
4. חכה שבדיקת האבטחה CI תעבור (בדוק עם `gh run list --repo skills-il/<category-repo> --limit 1`)
5. הכנס ל-Supabase דרך צינור הסנכרון או SQL ישיר
6. ודא שהסקיל מופיע באתר (מטמון ISR מתרענן תוך ~5 דקות)

ה-`github_url` במסד הנתונים חייב להצביע לתיקיית הסקיל, לא לשורש הריפו:
`https://github.com/skills-il/<category-repo>/tree/master/<skill-name>`

## דוגמאות

### דוגמה 1: יצירת סקיל לשירותי ממשלה

המשתמש אומר: "אני רוצה ליצור סקיל לחיפוש פסקי דין"

פעולות:
1. קטגוריה: government-services
2. פרטי יוצר: שאל שם ואימייל
3. מקרי שימוש: חיפוש לפי מספר תיק, חיפוש לפי שופט, חיפוש לפי נושא
4. בדיקת עובדות: אמת מבנה מערכת בתי המשפט, שיטות גישה לנבו, פורמטי ציטוט
5. Scaffold: `python scripts/scaffold-skill.py --name israeli-court-decisions --category government-services`
6. Frontmatter: טריגרים כוללים "פסקי דין", "בית משפט", "נבו"
7. הוראות: שלבים לסוגי חיפוש, ניתוח תוצאות, פורמט ציטוט
8. מסמכי עזר: `references/court-hierarchy.md`; סקריפטים: `scripts/case-lookup.py`
9. עברית: SKILL_HE.md עם מינוח משפטי
10. אימות: `./scripts/validate-skill.sh israeli-court-decisions/SKILL.md`
11. הגשה דרך https://agentskills.co.il/he/submit

תוצאה: סקיל מוכן לספריית Skills IL.

### דוגמה 2: יצירת כלי פיתוח

המשתמש אומר: "אני צריך סקיל שעוזר לפרמט כתובות ישראליות"

פעולות:
1. קטגוריה: developer-tools
2. פרטי יוצר: שאל שם ואימייל
3. מקרי שימוש: פורמט לדואר, אימות מיקוד, נרמול שמות ערים
4. בדיקת עובדות: אמת כללי פורמט מיקוד, זמינות API של דואר ישראל, מיפויי שמות ערים
5. Scaffold: `python scripts/scaffold-skill.py --name israeli-address-formatter --category developer-tools`
6. Frontmatter: טריגרים כוללים "פורמט כתובת", "מיקוד", "address normalization"
7. הוראות: כללי פורמט, חיפוש מיקוד, שמות ערים דו-לשוניים
8. מסמכי עזר: `references/mikud-format.md`; סקריפטים: `scripts/mikud-validator.py`
9. עברית: SKILL_HE.md
10. אימות: עובר את כל הבדיקות
11. הגשה דרך https://agentskills.co.il/he/submit

תוצאה: סקיל פורמט כתובות עם אימות ותמיכה בדואר.

### דוגמה 3: יצירת סקיל עם MCP

המשתמש אומר: "אני רוצה ליצור סקיל שמשתמש בשרת israeli-bank-mcp"

פעולות:
1. קטגוריה: tax-and-finance
2. פרטי יוצר: שאל שם ואימייל
3. מקרי שימוש: סיווג תנועות, זיהוי חיובים חוזרים, סיכום חודשי
4. בדיקת עובדות: אמת דפוסי API של בנקים ישראליים, תקני סיווג תנועות
5. Scaffold: `python scripts/scaffold-skill.py --name israeli-bank-analyzer --category tax-and-finance`
6. Frontmatter: הוסף `mcp-server: israeli-bank-mcp` למטאדאטה, טריגרים כוללים "ניתוח תנועות בנק"
7. הוראות: קריאות כלי MCP לשליפת תנועות, לוגיקת סיווג, יצירת סיכום
8. מסמכי עזר: `references/bank-api-reference.md`; סקריפטים: `scripts/transaction-categorizer.py`
9. עברית: SKILL_HE.md עם מינוח בנקאי
10. אימות: עובר את כל הבדיקות
11. הגשה דרך https://agentskills.co.il/he/submit

תוצאה: סקיל מועשר MCP שמוסיף אינטליגנציה על גבי גישה לנתוני בנק.

## משאבים מצורפים

### סקריפטים
- `scripts/scaffold-skill.py` -- יוצר את מבנה התיקייה המלא לסקיל חדש: תבנית SKILL.md עם שלד frontmatter, שלד SKILL_HE.md, תיקיות scripts/ ו-references/. מאמת פורמט שם ומונע דריסה. הרצה: `python scripts/scaffold-skill.py --help`

### מסמכי עזר
- `references/skill-spec.md` -- מפרט מלא של SKILL.md כולל כל שדות frontmatter (חובה ואופציונלי), נוסחת כתיבת תיאור עם דוגמאות טובות/רעות, 5 דפוסי סקילים מהמדריך של Anthropic, רשימת בדיקות איכות וכללי אימות. עיין כאשר כותב frontmatter או הוראות וצריך הנחיה מפורטת מעבר לשלבים לעיל.

## פתרון בעיות

### שגיאה: "האימות נכשל על התיאור"
סיבה: חסר ביטוי טריגר או מעל 1024 תווים
פתרון: וודא שהתיאור כולל אחד מ: "Use when", "Use for", "Use if", "When user", "When the user". בדוק שהאורך מתחת ל-1024 תווים. הסר סוגריים משולשים `<>`.

### שגיאה: "השם לא תואם לתיקייה"
סיבה: שדה `name` ב-SKILL.md שונה משם התיקייה
פתרון: שדה ה-`name` חייב להתאים בדיוק לשם התיקייה. שניהם חייבים להיות ב-kebab-case.

### שגיאה: "הגוף חורג מ-5,000 מילים"
סיבה: יותר מדי פרטים ב-SKILL.md
פתרון: העבר תיעוד מפורט לקבצי `references/`. שמור על SKILL.md ממוקד בהוראות ליבה. קשר למסמכי עזר עם "Consult `references/filename.md` for..." .

### שגיאה: "סקריפט ה-scaffold נכשל"
סיבה: תיקייה כבר קיימת או פורמט שם לא תקין
פתרון: בדוק אם תיקיית הסקיל כבר קיימת. וודא שהשם ב-kebab-case בלבד (אותיות קטנות, מספרים, מקפים). ללא רווחים, קו תחתון או אותיות גדולות.
