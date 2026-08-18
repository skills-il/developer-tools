# IVR Design Patterns for Israeli Businesses

Common IVR flow patterns for different Israeli business types. All prompts use formal Hebrew register (second person plural) to avoid gendered language.

## General Principles

### Israeli-Specific Conventions

| Convention | Detail |
|-----------|--------|
| Business days | Sunday (yom rishon) through Thursday (yom chamishi) |
| Friday | Half day, typically 9:00-13:00 |
| Saturday (Shabbat) | Closed. Do not offer callbacks on Saturday |
| Time format | 24-hour clock (14:30, not 2:30 PM) |
| Star key | "כוכבית" (kokhavit) |
| Hash/pound key | "סולמית" (sulamit) |
| "Press" | "הקישו" (hakishu, plural imperative) |
| Agent | "נציג" (natzig) or "נציג/ה" (natzig/a) |
| Hold message | Repeat every 60 seconds |
| Language option | English on key 9 (standard placement) |

### Menu Depth Guidelines

| Menu Level | Max Options | Timeout |
|-----------|-------------|---------|
| Welcome | 1 message + language choice | N/A |
| Main menu | 4-5 options | 8 seconds |
| Sub-menu | 3-4 options | 6 seconds |
| Data entry | 1 input field | 10 seconds |

Do not exceed 3 menu levels. If you need more depth, redesign the flow.

## Pattern 1: Restaurant / Cafe

```
[Welcome]
"שלום, הגעתם למסעדת {name}."

[Business Hours Check]
  IF open:
    -> [Main Menu]
  IF Friday afternoon / Shabbat:
    "אנחנו סגורים כעת. שעות פעילות: א'-ה' {hours}, ו' {fri_hours}."
    "להשאיר הודעה, הקישו 1. לשמוע שוב, הקישו כוכבית."

[Main Menu]
"להזמנת מקום, הקישו 1.
 לשעות פעילות ומיקום, הקישו 2.
 לשמוע את תפריט היום, הקישו 3.
 לנציג, הקישו 0."

[1 - Reservations]
"לאיזה תאריך תרצו להזמין מקום?"
  -> Gather date (DTMF or speech)
"כמה סועדים?"
  -> Gather number (1-20)
"על איזה שם ההזמנה?"
  -> Record name (speech)
"לאישור ההזמנה ל-{date}, {count} סועדים, על שם {name}, הקישו 1.
 לביטול, הקישו 2."

[2 - Hours & Location]
"שעות פעילות: א'-ה' {hours}, ו' {fri_hours}, שבת סגור.
 הכתובת: {address}.
 לחזרה לתפריט, הקישו כוכבית."

[3 - Daily Menu]
"תפריט היום: {menu_items}.
 להזמנת מקום, הקישו 1.
 לחזרה, הקישו כוכבית."
```

## Pattern 2: Medical Clinic / Dentist

```
[Welcome]
"שלום, הגעתם למרפאת {name}."

[Emergency Check]
"במקרה חירום רפואי, התקשרו למד"א 101 או פנו לחדר מיון הקרוב."

[Main Menu]
"לקביעת תור, הקישו 1.
 לביטול או שינוי תור, הקישו 2.
 לתוצאות בדיקות, הקישו 3.
 לחידוש מרשם, הקישו 4.
 לנציג, הקישו 0."

[1 - Schedule Appointment]
"לאיזה רופא תרצו לקבוע תור?"
  "לד"ר {name1}, הקישו 1.
   לד"ר {name2}, הקישו 2.
   לד"ר {name3}, הקישו 3."
  -> [Date Selection]
"התורים הפנויים הקרובים:
 {date1} בשעה {time1}, הקישו 1.
 {date2} בשעה {time2}, הקישו 2."
"לאישור תור ב-{date} בשעה {time}, הקישו 1."
"התור נקבע. תקבלו SMS עם אישור. תודה ויום טוב."

[2 - Cancel/Reschedule]
"הקישו את מספר תעודת הזהות שלכם."
  -> Validate TZ (9 digits)
"נמצא תור ב-{date} בשעה {time} אצל ד"ר {doctor}.
 לביטול, הקישו 1.
 לשינוי מועד, הקישו 2."

[4 - Prescription Renewal]
"הקישו את מספר תעודת הזהות שלכם."
  -> Validate TZ
"לחידוש מרשם, השאירו הודעה עם שם התרופה. הרופא יחזור אליכם תוך 24 שעות."
  -> Record message
```

## Pattern 3: E-Commerce / Customer Service

```
[Welcome]
"שלום, הגעתם לשירות הלקוחות של {company}."
"For English, press 9."

[Main Menu]
"למעקב אחר הזמנה, הקישו 1.
 להחזרות והחלפות, הקישו 2.
 לתמיכה טכנית, הקישו 3.
 לחשבונות וחיובים, הקישו 4.
 לנציג, הקישו 0."

[1 - Order Tracking]
"הקישו את מספר ההזמנה (6 ספרות)."
  -> Validate order number
"הזמנה מספר {order_id}:
 סטטוס: {status}.
 תאריך משלוח משוער: {delivery_date}.
 לפרטים נוספים, הקישו 1.
 לנציג, הקישו 0.
 לתפריט ראשי, הקישו כוכבית."

[2 - Returns]
"מדיניות ההחזרות שלנו: ניתן להחזיר מוצרים עד 14 יום מהרכישה.
 להתחלת תהליך החזרה, הקישו 1.
 לבדיקת סטטוס החזרה, הקישו 2."

[2.1 - Start Return]
"הקישו את מספר ההזמנה."
  -> Validate
"מהי סיבת ההחזרה?
 מוצר פגום, הקישו 1.
 לא מתאים, הקישו 2.
 שונה מהתמונה, הקישו 3.
 סיבה אחרת, הקישו 4."
  -> Generate return label
"פתחנו בקשת החזרה. תקבלו מדבקת משלוח ב-SMS. תודה."

[Agent Queue]
"ממתינים לנציג הפנוי הבא.
 מספרכם בתור: {position}.
 זמן המתנה משוער: {wait} דקות."
  -> Hold music (Israeli/neutral)
  -> Every 60s: "תודה שאתם ממתינים. שיחתכם חשובה לנו."
```

## Pattern 4: Government Office / Municipality

```
[Welcome]
"שלום, הגעתם ל{office_name}."
"For English, press 9."
"לשירות בערבית, הקישו 8."

[Main Menu]
"לקביעת תור, הקישו 1.
 לבירור סטטוס בקשה, הקישו 2.
 למידע כללי, הקישו 3.
 לנציג, הקישו 0."

[After Hours]
"שעות קבלת קהל: א'-ה' {hours}.
 לשירות עצמי באתר האינטרנט: {website}.
 להשאיר הודעה, הקישו 1."

[1 - Schedule Appointment]
"לאיזה שירות תרצו לקבוע תור?
 רישום, הקישו 1.
 רישוי, הקישו 2.
 ארנונה, הקישו 3.
 שירות אחר, הקישו 4."
"הקישו את מספר תעודת הזהות שלכם."
  -> Validate TZ
"התור הפנוי הקרוב: {date} בשעה {time}.
 לאישור, הקישו 1.
 לתאריך אחר, הקישו 2."
"התור נקבע. מספר אישור: {confirmation}.
 אנא הגיעו עם תעודת זהות ומסמכים רלוונטיים."

[2 - Application Status]
"הקישו את מספר האסמכתא (Reference number)."
  -> Validate
"בקשה מספר {ref}: סטטוס {status}.
 עדכון אחרון: {last_update}.
 למידע נוסף, הקישו 1.
 לנציג, הקישו 0."
```

## Pattern 5: Service Provider (ISP, Telecom, Insurance)

```
[Welcome]
"שלום, הגעתם ל{company}.
 שיחה זו מוקלטת לצורכי שירות."

[Existing Customer Check]
"אם אתם לקוחות קיימים, הקישו 1.
 אם אתם מעוניינים להצטרף, הקישו 2."

[1 - Existing Customers]
"הקישו את מספר תעודת הזהות שלכם."
  -> Identify customer
"שלום {customer_name}.
 לתקלות ותמיכה טכנית, הקישו 1.
 לבירור חשבון, הקישו 2.
 לשדרוג או שינוי חבילה, הקישו 3.
 לביטול שירות, הקישו 4.
 לנציג, הקישו 0."

[1.1 - Technical Support]
"האם יש לכם תקלה כרגע?
 אינטרנט לא עובד, הקישו 1.
 אינטרנט איטי, הקישו 2.
 בעיה אחרת, הקישו 3."

[1.1.1 - Internet Down]
"מבצעים בדיקה אוטומטית של הקו שלכם...
 [pause 5 seconds]
 זיהינו תקלה באזור שלכם. הצוות הטכני עובד על תיקון.
 זמן תיקון משוער: {eta}.
 לעדכונים, תקבלו SMS.
 לנציג, הקישו 0."

[2 - New Customers]
"תודה על העניין!
 לפרטים על החבילות שלנו, הקישו 1.
 לשיחה עם יועץ מכירות, הקישו 2."
```

## Flow Control Best Practices

### Error Handling
```
[Invalid Input]
"בחירה לא תקינה."
  -> Repeat menu (up to 3 times)

[No Input Timeout]
"לא קיבלנו בחירה."
  -> Repeat menu (up to 2 times)

[Max Retries Exceeded]
"מעבירים אתכם לנציג."
  -> Transfer to agent queue

[System Error]
"מצטערים, המערכת אינה זמינה כרגע. אנא נסו שוב מאוחר יותר."
  -> Log error, optionally offer voicemail
```

### Navigation Controls (Include in Every Sub-menu)
```
"לחזרה לתפריט הקודם, הקישו 9.
 לתפריט הראשי, הקישו כוכבית.
 לנציג, הקישו 0."
```

### Hold Music Guidelines
- Use neutral instrumental music (avoid songs with lyrics)
- Volume lower than voice prompts
- Interrupt every 60 seconds with position/wait update
- Offer callback option after 3 minutes: "אם תרצו שנחזור אליכם, הקישו 1"
