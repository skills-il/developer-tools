---
name: israeli-id-validator
description: Validate and format Israeli identification numbers including Teudat Zehut (personal ID), company numbers, amuta (non-profit) numbers, and partnership numbers. Use when user asks to validate Israeli ID, "teudat zehut", "mispar zehut", company number validation, or needs to implement Israeli ID validation in code. Includes check digit algorithm and test ID generation. Do NOT use for non-Israeli identification systems.
license: MIT
allowed-tools: Bash(python:*)
compatibility: No network required. Works with Claude Code, Claude.ai, Cursor.
version: 1.0.1
---

# מאמת תעודת זהות ישראלית

## הוראות

### שלב 1: זיהוי סוג המספר
| סוג | קידומת | אורך | דוגמה |
|-----|--------|------|-------|
| תעודת זהות | כלשהי | 9 ספרות | 123456782 |
| חברה (בע"מ) | 51 | 9 ספרות | 51-530820-1 |
| עמותה | 58 | 9 ספרות | 58-012345-6 |
| שותפות | 55 | 9 ספרות | 55-012345-6 |

### שלב 2: אימות באמצעות אלגוריתם ספרת ביקורת
אלגוריתם ספרת הביקורת של מספר זהות ישראלי (חל על כל הסוגים):

```python
def validate_israeli_id(id_number: str) -> bool:
    """Validate Israeli ID number (TZ, company, amuta, etc.)"""
    # Remove dashes and spaces, pad to 9 digits
    id_str = id_number.replace('-', '').replace(' ', '').zfill(9)

    if len(id_str) != 9 or not id_str.isdigit():
        return False

    total = 0
    for i, digit in enumerate(id_str):
        # Position counting from left: odd positions (0,2,4,6,8) multiply by 1
        # Even positions (1,3,5,7) multiply by 2
        weight = 1 if i % 2 == 0 else 2
        val = int(digit) * weight
        if val > 9:
            val = val // 10 + val % 10     # Sum digits if > 9
        total += val

    return total % 10 == 0
```

### שלב 3: מתן תוצאה
למספרים תקינים: אישור תקינות, זיהוי סוג לפי קידומת
למספרים לא תקינים: דיווח על אי-תקינות, הצגת הבדיקה שנכשלה, הצעת שגיאות נפוצות:
- ספרות מוחלפות
- ספרה חסרה/עודפת
- ספרת ביקורת שגויה

### שלב 4: יצירת מספרים לבדיקה (לשימוש בפיתוח)
לצורכי פיתוח ובדיקות, ניתן ליצור מספרי זיהוי תקינים:

```python
def generate_test_id(prefix: str = "") -> str:
    """Generate a valid Israeli ID number for testing."""
    import random
    base = prefix + ''.join([str(random.randint(0, 9)) for _ in range(8 - len(prefix))])
    # Calculate check digit
    total = 0
    for i, digit in enumerate(base):
        weight = 1 if i % 2 == 0 else 2
        val = int(digit) * weight
        if val > 9:
            val = val // 10 + val % 10
        total += val
    check = (10 - (total % 10)) % 10
    return base + str(check)
```

הערה חשובה: מספרים שנוצרו מיועדים לבדיקות בלבד. לעולם אל תשתמשו במספרים אקראיים כזיהוי אמיתי.

## דוגמאות

### דוגמה 1: אימות תעודת זהות
המשתמש אומר: "האם 123456782 הוא מספר תעודת זהות תקין?"
תוצאה: הרצת האלגוריתם, דיווח תקין/לא תקין עם הסבר.

### דוגמה 2: מימוש בקוד
המשתמש אומר: "אני צריך אימות תעודת זהות ישראלית ב-JavaScript"
תוצאה: מתן אלגוריתם מקביל ב-JavaScript.

### דוגמה 3: יצירת נתוני בדיקה
המשתמש אומר: "אני צריך 10 מספרי חברה תקינים לבדיקה"
תוצאה: יצירת 10 מספרים תקינים עם קידומת 51- לבדיקה.

## משאבים מצורפים

### סקריפטים
- `scripts/validate_id.py` — מאמת, מזהה, מעצב ומייצר מספרי זיהוי ישראליים (תעודת זהות, חברה, עמותה, שותפות). תומך במצב מפורט המציג חישוב ספרת ביקורת שלב אחר שלב, יצירת מספרי בדיקה באצווה עם בקרת קידומת, וזיהוי סוג מכל מספר. הרצה: `python scripts/validate_id.py --help`

### חומרי עזר
- `references/id-formats.md` — מפרט כל פורמטי מספרי הזיהוי הישראליים כולל תעודת זהות, חברה (קידומת 51), עמותה (קידומת 58), שותפות (קידומת 55), ואגודה שיתופית (קידומת 57) עם רשויות מנפיקות, תבניות פורמט, אלגוריתם ספרת ביקורת מסוג Luhn עם דוגמה מפורטת, ושגיאות אימות נפוצות. עיינו בו בעת מימוש לוגיקת אימות או דיבוג כשלים בספרת ביקורת.

## מלכודות נפוצות

- מספרי תעודת זהות ישראליים הם בדיוק 9 ספרות עם ספרת ביקורת מסוג Luhn-variant. סוכנים עלולים ליצור מספרים אקראיים בני 9 ספרות שנכשלים בבדיקת ספרת הביקורת.
- מספרי תעודת זהות עם פחות מ-9 ספרות חייבים להיות מרופדים באפסים משמאל. מספר כמו "12345678" הוא בעצם "012345678". סוכנים עלולים למחוק אפסים מובילים ולשבור ולידציה.
- מספר אישי צבאי משתמש בפורמט שונה מתעודת זהות אזרחית ולא צריך להיבדק עם אותו אלגוריתם.
- תעודות זהות של תושבים זמניים מתחילות בדפוסי ספרות ספציפיים. סוכנים עלולים לדחות תעודות זמניות תקינות כי הן לא תואמות דפוסי תעודות קבועות.
- אלגוריתם ספרת הביקורת הישראלי מכפיל ספרות לסירוגין ב-1 וב-2 (לא 2 ו-1 כמו ב-Luhn הסטנדרטי). סוכנים שמממשים Luhn סטנדרטי יאשרו מספרים שגויים.

## פתרון בעיות

### שגיאה: "המספר נראה תקין אך לא מזוהה"
סיבה: ספרת הביקורת עוברת אך המספר לא הונפק בפועל
פתרון: האלגוריתם מאמת רק את הפורמט, לא את הקיום בפועל. אימות האם מספר הונפק בפועל דורש גישה למערכות רשות המסים או משרד הפנים.