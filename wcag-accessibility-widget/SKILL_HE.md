---
name: wcag-accessibility-widget
description: בנה ווידג'ט נגישות צף ועצמאי לאתרי אינטרנט ישראליים — כפתורי WCAG 2.1 AA / ת"י 5568 (ניגודיות גבוהה, גודל גופן, ניווט מקלדת, גופן קריא, סימון כותרות/קישורים), הגדרות שמורות ב-localStorage, מוחלות כ-CSS class על <html>. השתמשו כשבונים ווידג'ט נגישות, מיישמים דרישות חוק שוויון זכויות לאנשים עם מוגבלות, יוצרים דף הצהרת נגישות, או מאבחנים אלמנטים position:fixed שנשברים בעת שימוש ב-CSS filter. מכסה ארכיטקטורת קומפוננטה ב-React/Next.js, כפתורי toggle בטוחים ל-RTL, אסטרטגיית CSS class, ותוכן דף הצהרת הנגישות הנדרש. אל תשתמשו עבור שירותי accessibility overlay צד שלישי (UserWay, AccessiBe) או ביקורות WCAG שאינן ישראליות.
license: MIT
compatibility: עובד עם React 18+ ו-Next.js 13+ (App Router). אין צורך ב-API או שירות חיצוני — עצמאי לחלוטין עם localStorage. תואם לפרויקטי Tailwind CSS. מודע לפריסת RTL/עברית.
---

# ווידג'ט נגישות WCAG

## סקירה כללית

ווידג'ט נגישות עצמאי: כפתור קבוע שפותח פנל עם כפתורי toggle לתכונות WCAG 2.1 AA נפוצות. ההגדרות שמורות ב-`localStorage` ומוחלות כ-CSS class על `<html>`. אין צורך בשירות צד שלישי.

---

## רשימת WCAG 2.1 AA — מה לבנות

לפני כל שינוי בקומפוננטה, בדקו תחילה את הפריטים הבאים:

| פריט | מה לבדוק / ליישם |
|------|-----------------|
| **קישור דילוג** | `<a href="#main-content">` בפריסה, מוסתר ויזואלית, גלוי בפוקוס. יעד: `<main id="main-content" tabIndex={-1}>` |
| **תיאור תמונות** | לכל `<img>` יש `alt` תיאורי. תמונות דקורטיביות מקבלות `alt=""` + `aria-hidden="true"` |
| **ניגודיות צבע** | טקסט רגיל ≥ 4.5:1, טקסט גדול ≥ 3:1. כשל נפוץ: `text-gray-500` על רקע כהה (~3.9:1) → השתמשו ב-`text-gray-400` |
| **ניווט מקלדת** | כל האלמנטים האינטראקטיביים נגישים ב-Tab. בדקו עם מקלדת בלבד |
| **תוויות ARIA** | `aria-label` על כפתורים עם סמל בלבד, `aria-expanded` על toggles, `aria-label` על `<nav>` כשיש מספר navs |
| **אלמנטים דקורטיביים** | אמוג'י, span קו תחתי, אייקוני SVG עם טקסט סמוך → `aria-hidden="true"` |
| **שפה וכיוון** | `<html lang="he" dir="rtl">` (או השפה שלכם) על אלמנט השורש |
| **רספונסיביות מובייל** | האתר שמיש במובייל ללא גלילה אופקית |
| **הצהרת נגישות** | נדרשת לפי חוק שוויון זכויות לאנשים עם מוגבלות — עמוד בכתובת `/accessibility` |
| **מדיניות פרטיות** | `/privacy-policy` עם רשימה של כל הנתונים שהטופס אוסף |

---

## ארכיטקטורת הווידג'ט

### 1. טיפוס ההגדרות + מפת CSS class

```ts
type Settings = {
  keyboardNav: boolean;
  noAnimations: boolean;
  highContrast: boolean;
  textLarge: boolean;    // בלעדי עם textSmall
  textSmall: boolean;
  readableFont: boolean;
  markHeadings: boolean;
  markLinks: boolean;
};

const CLASS_MAP: Record<keyof Settings, string> = {
  keyboardNav:  "a11y-keyboard",
  noAnimations: "a11y-no-anim",
  highContrast: "a11y-contrast",
  textLarge:    "a11y-font-lg",
  textSmall:    "a11y-font-sm",
  readableFont: "a11y-readable",
  markHeadings: "a11y-headings",
  markLinks:    "a11y-links",
};
```

### 2. החלת class על `<html>` + שמירה

```ts
useEffect(() => {
  const html = document.documentElement;
  (Object.keys(settings) as (keyof Settings)[]).forEach((key) => {
    html.classList.toggle(CLASS_MAP[key], settings[key]);
  });
  localStorage.setItem("a11y", JSON.stringify(settings));
}, [settings]);
```

### 3. שחזור בעת טעינה

```ts
useEffect(() => {
  try {
    const saved = localStorage.getItem("a11y");
    if (saved) setSettings(JSON.parse(saved));
  } catch { /* ignore */ }
}, []);
```

### 4. סגירה ב-Escape + לחיצה מחוץ

```ts
useEffect(() => {
  if (!isOpen) return;
  const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setIsOpen(false); };
  const onMouse = (e: MouseEvent) => {
    if (!panelRef.current?.contains(e.target as Node) &&
        !btnRef.current?.contains(e.target as Node)) setIsOpen(false);
  };
  document.addEventListener("keydown", onKey);
  document.addEventListener("mousedown", onMouse);
  return () => {
    document.removeEventListener("keydown", onKey);
    document.removeEventListener("mousedown", onMouse);
  };
}, [isOpen]);
```

### 5. כפתור toggle בטוח ל-RTL

השתמשו ב-`transform: translateX()` — CSS transforms הם תמיד פיזיים (לא מתהפכים ב-RTL):

```tsx
<span
  aria-hidden="true"
  className="absolute top-[3px] h-[18px] w-[18px] rounded-full bg-white shadow-sm transition-transform duration-200"
  style={{ transform: `translateX(${active ? "21px" : "3px"})` }}
/>
```

מסלול: `w-11 h-6` (44×24px). אגודל: 18×18px עם ריפוד 3px מכל צד → פועל=21px, כבוי=3px.

---

## מצבי CSS (globals.css)

```css
/* ניווט מקלדת */
html.a11y-keyboard *:focus,
html.a11y-keyboard *:focus-visible {
  outline: 3px solid var(--red) !important;
  outline-offset: 3px !important;
}

/* ללא אנימציות */
html.a11y-no-anim *, html.a11y-no-anim *::before, html.a11y-no-anim *::after {
  animation-duration: 0.001ms !important;
  transition-duration: 0.001ms !important;
}
html.a11y-no-anim { scroll-behavior: auto !important; }

/* ניגודיות גבוהה — ראו באג קריטי למטה, אל תשתמשו ב-filter על body/html */
html.a11y-contrast { --bg: #000; --bg2: #000; --muted: #e8e8e8; }
html.a11y-contrast body { background-color: #000 !important; }
html.a11y-contrast .text-gray-400 { color: #ebebeb !important; }
html.a11y-contrast .text-gray-500 { color: #e0e0e0 !important; }

/* גדלי גופן — משנה rem שורש כך שכל יחידות rem מתרחבות */
html.a11y-font-lg { font-size: 115%; }
html.a11y-font-sm { font-size: 88%; }

/* גופן קריא */
html.a11y-readable, html.a11y-readable * {
  font-family: Arial, Helvetica, sans-serif !important;
  letter-spacing: 0.015em;
}

/* סימון כותרות */
html.a11y-headings h1, html.a11y-headings h2,
html.a11y-headings h3, html.a11y-headings h4 {
  outline: 2px dashed var(--red) !important;
  outline-offset: 6px;
}

/* סימון קישורים / כפתורים (לא כולל toggles של הווידג'ט) */
html.a11y-links a,
html.a11y-links button:not([role="switch"]):not(#a11y-btn) {
  outline: 2px solid #3b82f6 !important;
  text-decoration: underline !important;
}
```

---

## באג קריטי: CSS filter + position:fixed

**תסמין:** כפתור הווידג'ט הצף (או header דביק) "קופץ לתחתית העמוד" בעת הפעלת מצב.

**סיבת שורש:** CSS `filter` (וכן `transform`, `perspective`) על כל **אב** של אלמנט `position:fixed` גורם לאלמנט לקבל מיקום יחסית לאב המסונן במקום ה-viewport. בעמוד ארוך, `bottom: 1.5rem` הופך ל-1.5rem מתחתית העמוד, לא מה-viewport.

**מה שובר:**
```css
/* ❌ כל אחד מאלה על אב של אלמנט fixed */
body    { filter: contrast(160%); }   /* שובר את כל הצאצאים fixed */
#wrapper { filter: contrast(160%); }  /* שובר צאצאי fixed */
```

**גישות בטוחות:**
```css
/* ✅ מיקוד רק על אלמנטים שאינם אבות */
html.a11y-contrast header { filter: contrast(160%); }  /* header הוא fixed אבל filter עליו, לא על אב */
html.a11y-contrast #main-content { filter: contrast(160%); }  /* הווידג'ט הוא sibling, לא צאצא */

/* ✅ עדיף: הימנעות מ-filter לחלוטין — שימוש בדריסת משתני CSS */
html.a11y-contrast { --bg: #000; --muted: #e0e0e0; }
html.a11y-contrast body { background-color: #000 !important; }
```

**כלל:** לעולם אל תחיל `filter`, `transform`, או `perspective` על אלמנט שהוא אב של `position:fixed` שאכפת לכם ממנו.

---

## מיקום הווידג'ט

מקמו את הווידג'ט ב-`layout.tsx` body, **אחרי** `{children}` — לעולם לא בתוך תוכן הדף:

```tsx
<body>
  <a href="#main-content" className="sr-only focus:not-sr-only ...">דלג לתוכן הראשי</a>
  {children}                  {/* תוכן הדף — Header (fixed) + main */}
  <AccessibilityWidget />     {/* כפתור + פנל fixed, sibling של children */}
</body>
```

מדריך z-index:
- Header: `z-50`
- כפתור + פנל הווידג'ט: `z-[200]`
- קישור דילוג: `z-[9999]`

---

## דף הצהרת נגישות (חוק ישראלי)

נדרש לפי חוק שוויון זכויות לאנשים עם מוגבלות. חייב לכלול:

- הצהרה על רמת ההתאמה (WCAG 2.1 AA / ת"י 5568)
- רשימת ההתאמות שבוצעו
- מגבלות ידועות
- פרטי רכז הנגישות (שם + טלפון)
- תאריך סקירה אחרונה
- הפנייה לנציב שוויון זכויות לתלונות שלא נפתרו

קשרו מהתחתית לצד מדיניות הפרטיות.

### תבנית דף הצהרת נגישות

```tsx
// app/accessibility/page.tsx
export default function AccessibilityPage() {
  return (
    <main id="main-content" tabIndex={-1} dir="rtl" lang="he">
      <h1>הצהרת נגישות</h1>

      <section>
        <h2>מחויבות לנגישות</h2>
        <p>
          [שם האתר] פועל לאפשר שימוש נגיש לכלל המשתמשים, לרבות אנשים עם מוגבלות,
          בהתאם לחוק שוויון זכויות לאנשים עם מוגבלות (התשנ"ח-1998) ותקנות הנגישות.
        </p>
        <p>
          האתר עומד ברמת תאימות <strong>WCAG 2.1 AA</strong> (ת"י 5568).
        </p>
      </section>

      <section>
        <h2>התאמות נגישות שבוצעו</h2>
        <ul>
          <li>ניגודיות צבעים גבוהה</li>
          <li>הגדלה והקטנה של גודל הגופן</li>
          <li>הדגשת ניווט מקלדת</li>
          <li>גופן קריאה נוח (Arial)</li>
          <li>הדגשת כותרות וקישורים</li>
          <li>עצירת אנימציות</li>
          <li>קישור דילוג לתוכן הראשי</li>
          <li>תגיות alt לתמונות</li>
          <li>תוויות ARIA לאלמנטים אינטראקטיביים</li>
        </ul>
      </section>

      <section>
        <h2>מגבלות ידועות</h2>
        <p>אנו עובדים באופן שוטף לשיפור הנגישות. אם נתקלתם בבעיה — פנו אלינו.</p>
      </section>

      <section>
        <h2>רכז נגישות</h2>
        <p>שם: [שם רכז הנגישות]</p>
        <p>טלפון: [מספר טלפון]</p>
        <p>דוא"ל: [כתובת דוא"ל]</p>
      </section>

      <section>
        <h2>תאריך סקירה אחרונה</h2>
        <p>[תאריך]</p>
      </section>

      <section>
        <h2>פניות ותלונות</h2>
        <p>
          במידה ונתקלתם בבעיית נגישות שלא נפתרה, תוכלו לפנות ל
          <a href="https://www.justice.gov.il/Units/NetzivutShivionZchuyot/Pages/default.aspx">
            נציב שוויון זכויות לאנשים עם מוגבלות
          </a>.
        </p>
      </section>
    </main>
  );
}
```

---

## שגיאות נפוצות

| שגיאה | תיקון |
|-------|-------|
| `filter` על body למצב ניגודיות | השתמשו בדריסת משתני CSS במקום |
| `aria-hidden` על אלמנט עם צאצאים שניתן לפוקוס | העבירו `aria-hidden` לעטיפה דקורטיבית בלבד |
| שני אלמנטי `<nav>` ללא תוויות | הוסיפו `aria-label` לכל nav |
| `text-gray-500` על רקע כהה | נכשל ב-4.5:1 — השתמשו ב-`text-gray-400` לכל הפחות |
| גודל גופן דרך דריסות `px` | השתמשו ב-`font-size: %` על `<html>` כך שכל יחידות `rem` מתרחבות |
| אגודל toggle עם מיקום מודע ל-RTL | השתמשו ב-`translateX()` — הוא תמיד פיזי, לא מתהפך ב-RTL |
| ווידג'ט בתוך תוכן הדף | מקמו אחרי `{children}` בפריסה, לעולם לא בתוך main |
