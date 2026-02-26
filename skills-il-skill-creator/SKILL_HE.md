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
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
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

### שלב 2: הגדרת מקרי שימוש

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

### שלב 3: יצירת מבנה תיקייה

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

### שלב 4: כתיבת YAML Frontmatter

צור את ה-frontmatter לפי המבנה המדויק:

```yaml
---
name: <skill-name>
description: >-
  [מה הסקיל עושה]. Use when user asks to [triggers],
  "[תעתיק עברי]", or [scenarios]. [יכולות מרכזיות].
  Do NOT use for [אנטי-טריגרים].
license: MIT
metadata:
  author: skills-il
  version: 1.0.0
  category: <category>
  tags:
    - <tag1>
    - israel
  display_name:
    he: "<שם בעברית>"
    en: <English Name>
  display_description:
    he: "<תיאור בעברית>"
    en: >-
      <English description>
---
```

**כללי תיאור (קריטי):**
- נוסחה: `[מה עושה] + [מתי להשתמש] + [יכולות] + [מתי לא להשתמש]`
- מתחת ל-1024 תווים
- אין סוגריים משולשים (`<>`) ב-frontmatter
- כלול ביטויי טריגר שמשתמשים באמת יגידו
- כלול תעתיקים עבריים במירכאות
- סיים עם `Do NOT use for` + הפניה לסקילים קשורים

### שלב 5: כתיבת הוראות

כתוב את גוף ה-SKILL.md לפי מבנה זה:

```markdown
# <שם הסקיל>

## Instructions

### Step 1: <שלב ראשון>
<הסבר ברור עם טבלאות ודוגמאות קוד>

## Examples

### Example 1: <תרחיש נפוץ>
User says: "<בקשה טיפוסית>"
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
- השתמש בטבלאות למטריצות החלטה
- שמור על SKILL.md מתחת ל-5,000 מילים
- העבר תיעוד מפורט ל-`references/`
- כלול 2-4 דוגמאות ו-2-4 פתרונות בעיות

### שלב 6: יצירת קובץ עברי נלווה (SKILL_HE.md)

צור SKILL_HE.md עם אותו מבנה בעברית:
- תרגם את ההוראות לעברית
- השאר בלוקי קוד, שמות שדות והפניות API באנגלית
- השתמש במונחים עבריים מקוריים (לא תעתיקים)
- שמור על מספור שלבים וחלקים זהה

### שלב 7: אימות והכנה ל-PR

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

## דוגמאות

### דוגמה 1: יצירת סקיל לשירותי ממשלה

המשתמש אומר: "אני רוצה ליצור סקיל לחיפוש פסקי דין"

פעולות:
1. קטגוריה: government-services
2. מקרי שימוש: חיפוש לפי מספר תיק, חיפוש לפי שופט, חיפוש לפי נושא
3. Scaffold: `python scripts/scaffold-skill.py --name israeli-court-decisions --category government-services`
4. Frontmatter: טריגרים כוללים "פסקי דין", "בית משפט", "נבו"
5. הוראות: שלבים לסוגי חיפוש, ניתוח תוצאות, פורמט ציטוט
6. עברית: SKILL_HE.md עם מינוח משפטי
7. אימות: `./scripts/validate-skill.sh israeli-court-decisions/SKILL.md`

תוצאה: סקיל מוכן ל-PR לריפו government-services.

### דוגמה 2: יצירת כלי פיתוח

המשתמש אומר: "אני צריך סקיל שעוזר לפרמט כתובות ישראליות"

פעולות:
1. קטגוריה: developer-tools
2. מקרי שימוש: פורמט לדואר, אימות מיקוד, נרמול שמות ערים
3. Scaffold: `python scripts/scaffold-skill.py --name israeli-address-formatter --category developer-tools`
4. Frontmatter: טריגרים כוללים "פורמט כתובת", "מיקוד", "address normalization"
5. הוראות: כללי פורמט, חיפוש מיקוד, שמות ערים דו-לשוניים
6. עברית: SKILL_HE.md
7. אימות: עובר את כל הבדיקות

תוצאה: סקיל פורמט כתובות עם אימות ותמיכה בדואר.

## משאבים מצורפים

### סקריפטים
- `scripts/scaffold-skill.py` -- יוצר את מבנה התיקייה המלא לסקיל חדש. הרצה: `python scripts/scaffold-skill.py --help`

### מסמכי עזר
- `references/skill-spec.md` -- מפרט מלא של SKILL.md כולל שדות frontmatter, נוסחת תיאור, 5 דפוסי סקילים, רשימת בדיקות איכות וכללי אימות. עיין כאשר כותב frontmatter או הוראות.

## פתרון בעיות

### שגיאה: "האימות נכשל על התיאור"
סיבה: חסר ביטוי טריגר או מעל 1024 תווים
פתרון: וודא שהתיאור כולל אחד מ: "Use when", "Use for", "Use if", "When user". בדוק שהאורך מתחת ל-1024 תווים. הסר סוגריים משולשים `<>`.

### שגיאה: "השם לא תואם לתיקייה"
סיבה: שדה `name` ב-SKILL.md שונה משם התיקייה
פתרון: שדה ה-`name` חייב להתאים בדיוק לשם התיקייה. שניהם חייבים להיות ב-kebab-case.

### שגיאה: "הגוף חורג מ-5,000 מילים"
סיבה: יותר מדי פרטים ב-SKILL.md
פתרון: העבר תיעוד מפורט לקבצי `references/`. שמור על SKILL.md ממוקד בהוראות ליבה.
