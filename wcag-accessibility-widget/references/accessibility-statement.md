# Accessibility Statement Template (הצהרת נגישות)

A template the site owner adapts. It is not legal advice and not an audit. Fill every bracket from real information; delete a section that does not apply rather than leaving a placeholder.

Regulation 35ה requires the statement to be in a prominent place on the site and in any app, and to include:

| Section | Required? |
|---------|-----------|
| Adaptations made | Required (35ה) |
| Contact for reporting a missing adaptation or requesting one | Required for everyone (35ה) |
| Accessibility coordinator name and contact | Required only if the owner must appoint one: an employer of 25 or more (law s.19מב) |
| Exemption granted under 35ו and the alternative adaptations | Required when an exemption was granted (35ו(ג)) |
| Standard targeted, full or partial conformance, known limitations, date of last review | Good practice |

Rules for filling it:
- Write "partial conformance" and list what does not work yet, unless an audit found full conformance. A false claim of full conformance is worse than an honest partial one.
- The standard is ת"י 5568 at level AA. If you also target WCAG 2.1 or 2.2 AA, say so separately; do not present them as the same thing.
- List real adaptations of the site itself first. The widget belongs at the end of the list, as an addition.

```tsx
// app/accessibility/page.tsx
// The layout already renders <main id="main-content">, so this page renders
// a <div>, not a second <main>.
export default function AccessibilityPage() {
  return (
    <div dir="rtl" lang="he">
      <h1>הצהרת נגישות</h1>

      <section>
        <h2>מחויבות לנגישות</h2>
        <p>
          [שם האתר] פועל להנגיש את האתר לכלל המשתמשים, לרבות אנשים עם מוגבלות,
          לפי חוק שוויון זכויות לאנשים עם מוגבלות, התשנ"ח-1998, והתקנות שהותקנו מכוחו.
        </p>
      </section>

      <section>
        <h2>רמת ההנגשה</h2>
        <p>
          האתר הונגש בהתאמה [חלקית / מלאה] לתקן הישראלי ת"י 5568 ברמה AA,
          [ובנוסף ל-WCAG 2.1 ברמה AA]. הבדיקה האחרונה נערכה ב-[תאריך] על ידי [מי בדק].
        </p>
      </section>

      <section>
        <h2>התאמות נגישות שבוצעו</h2>
        <ul>
          <li>[למשל: תיאור טקסטואלי לתמונות]</li>
          <li>[למשל: ניווט מלא במקלדת וסימון פוקוס]</li>
          <li>[למשל: תוויות לשדות בטפסים והודעות שגיאה בטקסט]</li>
          <li>[למשל: ניגודיות צבעים לפי התקן]</li>
          <li>[למשל: רכיב הגדרות נגישות: ניגודיות, גודל גופן, עצירת אנימציות]</li>
        </ul>
      </section>

      <section>
        <h2>חלקים שעדיין אינם נגישים</h2>
        <p>[מה עדיין לא נגיש, ואיזו חלופה קיימת בינתיים. אם אין ידוע כזה, מחקו את הסעיף.]</p>
      </section>

      {/* מחקו את הסעיף הזה אם אין חובה למנות רכז נגישות */}
      <section>
        <h2>רכז נגישות</h2>
        <p>שם: [שם]</p>
        <p>טלפון: [טלפון]</p>
        <p>דוא"ל: [דוא"ל]</p>
      </section>

      <section>
        <h2>דיווח על בעיית נגישות</h2>
        <p>
          נתקלתם בחלק באתר שאינו נגיש, או שאתם צריכים התאמה? אפשר לפנות אלינו
          ב-[דוא"ל] או ב-[טלפון], ונחזור אליכם.
        </p>
      </section>

      <section>
        <h2>תאריך עדכון ההצהרה</h2>
        <p>[תאריך]</p>
      </section>
    </div>
  );
}
```
