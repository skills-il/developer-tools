---
name: wcag-accessibility-widget
description: 'אינו ייעוץ משפטי. בניית ווידג''ט העדפות נגישות עצמאי לאתרי React או Next.js ישראליים (ניגודיות גבוהה, גודל גופן, הדגשת פוקוס מקלדת, גופן קריא, סימון כותרות וקישורים, עצירת אנימציות) ודף הצהרת נגישות, במסגור נכון מול הרף החוקי בישראל (ת"י 5568 ברמה AA, מבוסס WCAG 2.0). השתמשו כשבונים ווידג''ט או סרגל נגישות, מוסיפים דף הצהרת נגישות, מתקנים מתגים שנשברים ב-RTL, או מאבחנים אלמנטים position:fixed שנשברים תחת CSS filter. הווידג''ט הוא כלי נוחות ואינו הופך אתר לנגיש כדין בפני עצמו. אל תשתמשו עבור שירותי overlay של צד שלישי (UserWay, AccessiBe), ביקורות WCAG שאינן ישראליות, או שאלות של פטורים, אכיפה ובדיקת ציות מלאה של אתר (השתמשו ב-israeli-accessibility-compliance).'
license: MIT
compatibility: עובד עם React 18+ ו-Next.js 13+ (App Router). אין צורך ב-API או שירות חיצוני, עצמאי לחלוטין עם localStorage. תואם לפרויקטי Tailwind CSS. מודע לפריסת RTL/עברית.
---

# ווידג'ט נגישות WCAG

## הבהרה משפטית

הסקיל מסביר באופן כללי את כללי הנגישות לאתרי אינטרנט בישראל ועוזר לבנות ווידג'ט העדפות ודף הצהרה. הוא אינו ייעוץ משפטי ואינו בדיקת נגישות. ווידג'ט לבדו לא הופך אתר לעומד בת"י 5568: החובה חלה על התוכן והקוד של האתר עצמו. השאלה אם אתר מסוים חייב בהנגשה, פטור ממנה או עומד בה היא שאלה למורשה לנגישות השירות או לעורך דין שבדקו את האתר.

## סקירה כללית

ווידג'ט נגישות צף ועצמאי: כפתור קבוע שפותח פאנל של מתגי העדפות. ההגדרות נשמרות ב-`localStorage` ומוחלות כ-CSS class על `<html>`. אין צורך בשירות צד שלישי.

**קודם בונים את האתר נכון, ורק אחר כך מוסיפים ווידג'ט.** התקנה דורשת שהתוכן עצמו יעמוד בתקן. סרגל כלים לא מוסיף תוויות חסרות, לא מתקן סדר פוקוס, לא מוסיף כתוביות לסרטון ולא מנגיש PDF. באפריל 2025 אישרה ה-FTC האמריקאית צו סופי שחייב את accessiBe לשלם מיליון דולר בגלל טענות שהווידג'ט שלה יכול להפוך כל אתר לעומד ב-WCAG. אל תציגו ללקוח את הווידג'ט כפתרון הציות.

## הרף החוקי בישראל

| נושא | מה הכללים קובעים |
|------|------------------|
| תקן | תקנה 35א(א): שירות אינטרנט צריך לעמוד ב"תקן נגישות אינטרנט", שמוגדר בתקנה 35 כת"י 5568, **ברמה AA**. |
| גרסת WCAG | מהדורת מאי 2021 של ת"י 5568 חלק 1 באה במקום מהדורת מרס 2013 ועדיין מאמצת את **WCAG 2.0** (דצמבר 2008) עם שינויים ישראליים. WCAG 2.1 ו-2.2 ברמה AA מחמירים יותר; ה-W3C קובע שתוכן שעומד ב-2.2 עומד גם ב-2.0 וב-2.1. תכוונו ל-2.1 או 2.2 ברמה AA, אבל אל תכתבו "WCAG 2.1 = ת"י 5568". |
| מסמכים | מסמך כמו PDF שהוכן מ-26 באוקטובר 2017 והועלה לאתר חייב להיות נגיש (35א(ג)). |
| וידאו | כתוביות לווידאו מוקלט (1.2.2) נדרשות מרשות ציבורית ומעסק שמחזורו הממוצע עולה על 5 מיליון ש"ח ושעורך או מפיק תוכני וידאו מוקלטים (35ד). |
| פטורים | עוסק פטור, או עסק שמחזורו השנתי הממוצע אינו עולה על 100,000 ש"ח, פטור מפרק האינטרנט (35ו(ז)). יש פטורים נוספים (35ו). אל תכריעו בעצמכם אם לקוח פטור; תפנו אותו לתקנה ולאיש מקצוע. |
| הודעה ותיקון | סטייה לא נחשבת הפרה אלא אם נשלחה לבעל האתר הודעה והוא לא תיקן בתוך זמן סביר, ולא יאוחר מ-60 ימים (35א(ד)). |
| חשיפה | בית משפט רשאי לפסוק פיצוי של עד 50,000 ש"ח בלא הוכחת נזק בשל הפרת הוראות הנגישות (חוק השוויון, סעיף 19נא(ב)); הסכום צמוד למדד. |

## רשימת WCAG ברמה AA: מה לבנות

תבדקו את הסעיפים האלה לפני שנוגעים בווידג'ט:

| סעיף | מה לבדוק או ליישם |
|------|-------------------|
| **קישור דילוג** | `<a href="#main-content">` בלייאאוט, מוסתר ויזואלית וגלוי בפוקוס. יעד: `<main id="main-content" tabIndex={-1}>` (אחד בכל עמוד) |
| **טקסט חלופי** | לכל `<img>` יש `alt` תיאורי. תמונות דקורטיביות מקבלות `alt=""` |
| **ניגודיות צבעים** | טקסט רגיל 4.5:1, טקסט גדול 3:1. ב-Tailwind, ‏`text-gray-500` נכשל על רקע כהה (3.67:1 על `gray-900`, ‏3.04:1 על `gray-800`); ‏`text-gray-400` עובר (6.99:1 על `gray-900`). תמדדו את הצמד שלכם בפועל |
| **מקלדת ופוקוס** | כל רכיב נגיש ומופעל ב-Tab, ‏Enter ו-Space; סימון פוקוס גלוי על כל רכיב |
| **טפסים** | לכל שדה יש תווית תכנותית; שגיאות מזוהות בטקסט ולא רק בצבע |
| **ARIA** | `aria-label` לכפתורים עם אייקון בלבד, `aria-expanded` לכפתורי פתיחה, `aria-label` לכל `<nav>` כשיש כמה |
| **שפה וכיוון** | `<html lang="he" dir="rtl">` (או השפה שלכם) על אלמנט השורש |
| **הגדלה וזום** | טקסט קריא בזום 200% בדפדפן בלי אובדן תוכן; כפתור הגופן בווידג'ט לא מחליף את זה |
| **תנועה** | לכבד את `prefers-reduced-motion` כברירת מחדל, לא רק דרך מתג |
| **מדיה ומסמכים** | כתוביות כשתקנה 35ד חלה; מסמכי PDF נגישים מ-2017 והלאה |
| **הצהרת נגישות** | נדרשת לפי תקנה 35ה, ראו בהמשך |

## ארכיטקטורת הווידג'ט

הקומפוננטה היא client component. שימו `"use client";` בראש הקובץ.

### 1. הגדרות, ברירות מחדל, מפת class

```ts
type FontScale = "sm" | "md" | "lg";
type Settings = {
  keyboardNav: boolean;
  noAnimations: boolean;
  highContrast: boolean;
  fontScale: FontScale; // one value, so small and large can never both be on
  readableFont: boolean;
  markHeadings: boolean;
  markLinks: boolean;
};

const DEFAULTS: Settings = {
  keyboardNav: false, noAnimations: false, highContrast: false,
  fontScale: "md", readableFont: false, markHeadings: false, markLinks: false,
};
const STORAGE_KEY = "a11y";
const FLAG_CLASSES = {
  keyboardNav: "a11y-keyboard", noAnimations: "a11y-no-anim",
  highContrast: "a11y-contrast", readableFont: "a11y-readable",
  markHeadings: "a11y-headings", markLinks: "a11y-links",
} as const;
const FONT_CLASSES = { sm: "a11y-font-sm", md: "", lg: "a11y-font-lg" } as const;

function readSaved(): Settings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const saved = raw ? JSON.parse(raw) : null;
    if (!saved || typeof saved !== "object" || Array.isArray(saved)) return DEFAULTS;
    // migrate the pre-1.1.0 shape, which had two booleans instead of fontScale
    const fontScale: FontScale =
      saved.fontScale || (saved.textLarge ? "lg" : saved.textSmall ? "sm" : "md");
    const { textLarge, textSmall, ...rest } = saved;
    return { ...DEFAULTS, ...rest, fontScale };
  } catch {
    return DEFAULTS; // storage blocked or corrupt
  }
}
```

### 2. קודם שחזור, אחר כך החלה ושמירה

השחזור חייב להסתיים לפני שכותבים משהו. אם אפקט השמירה רץ ראשון בטעינה, הוא כותב את ברירות המחדל מעל ההגדרות השמורות, והבחירות של המשתמש לא שורדות רענון.

```ts
const [settings, setSettings] = useState<Settings>(DEFAULTS);
const [loaded, setLoaded] = useState(false);

useEffect(() => {
  setSettings(readSaved());
  setLoaded(true);
}, []);

useEffect(() => {
  if (!loaded) return; // never persist the pre-restore defaults
  const html = document.documentElement;
  Object.entries(FLAG_CLASSES).forEach(([key, cls]) =>
    html.classList.toggle(cls, settings[key as keyof typeof FLAG_CLASSES]));
  html.classList.remove("a11y-font-sm", "a11y-font-lg");
  if (FONT_CLASSES[settings.fontScale]) html.classList.add(FONT_CLASSES[settings.fontScale]);
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(settings)); } catch { /* blocked */ }
}, [settings, loaded]);
```

### 3. כפתור הפתיחה והפאנל

```tsx
<button
  ref={btnRef} id="a11y-btn" type="button"
  aria-expanded={isOpen} aria-controls="a11y-panel" aria-label="הגדרות נגישות"
  onClick={() => setIsOpen((o) => !o)}
  className="fixed bottom-6 start-6 z-[200] ..."
>
  {/* icon, aria-hidden="true" */}
</button>
{isOpen && (
  <div ref={panelRef} id="a11y-panel" role="region" aria-labelledby="a11y-title"
       className="fixed bottom-24 start-6 z-[200] ...">
    <h2 id="a11y-title">הגדרות נגישות</h2>
    {/* toggles */}
  </div>
)}
```

### 4. פוקוס פנימה, Escape החוצה, פוקוס חזרה

```ts
useEffect(() => {
  if (!isOpen) return;
  panelRef.current?.querySelector<HTMLElement>("button")?.focus(); // move focus into the panel
  const close = () => { setIsOpen(false); btnRef.current?.focus(); };
  const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") close(); };
  const onMouse = (e: MouseEvent) => {
    if (!panelRef.current?.contains(e.target as Node) &&
        !btnRef.current?.contains(e.target as Node)) {
      // try to hand focus back; mousedown precedes the browser's own focus
      // move, so this only holds when the click lands on inert content
      if (panelRef.current?.contains(document.activeElement)) close();
      else setIsOpen(false);
    }
  };
  document.addEventListener("keydown", onKey);
  document.addEventListener("mousedown", onMouse);
  return () => {
    document.removeEventListener("keydown", onKey);
    document.removeEventListener("mousedown", onMouse);
  };
}, [isOpen]);
```

### 5. מתג בטוח ל-RTL

הפונקציה `translateX()` פיזית, ולכן היא בטוחה ל-RTL רק אם גם נקודת ההתחלה של הכפתור פיזית. אלמנט עם מיקום אבסולוטי בלי `left` או `right` יושב במיקום הסטטי שלו, ובמכל RTL זה הקצה הימני; ‏`translateX` דוחף אותו אז אל מחוץ למסילה. תעגנו אותו עם `left-0` (‏`left: 0` פיזי), ולא עם `start-0`.

```tsx
function Toggle({ label, checked, onChange }:
  { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button type="button" role="switch" aria-checked={checked}
            onClick={() => onChange(!checked)}
            className="flex w-full items-center justify-between gap-3 py-2">
      <span>{label}</span>
      {/* px, not rem: the font-size modes change the root size and would
          otherwise resize the track while the thumb offsets stay fixed */}
      <span aria-hidden="true"
            className={`relative h-[24px] w-[44px] shrink-0 rounded-full ${checked ? "bg-blue-700" : "bg-gray-500"}`}>
        <span className="absolute left-0 top-[3px] h-[18px] w-[18px] rounded-full bg-white shadow-sm transition-transform duration-200"
              style={{ transform: `translateX(${checked ? "23px" : "3px"})` }} />
      </span>
    </button>
  );
}
```

המסילה היא 44 על 24 פיקסלים והכפתור 18 פיקסלים עם מרווח של 3: כבוי = 3px, דלוק = 44 - 18 - 3 = 23px. תשמרו על הערכים האלה בפיקסלים ולא ב-`w-11 h-6`: מצבי גודל הגופן משנים את גודל השורש, ולכן רוחב מסילה ביחידות rem מתרחק מההיסטים הקבועים (ב-88% הכפתור חורג מהמסילה, וב-115% הוא עוצר לפני הסוף). לגודל הגופן תשתמשו בשלושה כפתורים עם `aria-pressed` שמגדירים את `fontScale`.

## מצבי CSS (globals.css)

```css
:root { --a11y-mark: #c00000; }

/* Keyboard focus highlight */
html.a11y-keyboard *:focus,
html.a11y-keyboard *:focus-visible {
  outline: 3px solid var(--a11y-mark) !important;
  outline-offset: 3px !important;
}

/* No animations: the toggle, and the OS setting by default */
html.a11y-no-anim *, html.a11y-no-anim *::before, html.a11y-no-anim *::after {
  animation-duration: 0.001ms !important; animation-iteration-count: 1 !important;
  animation-delay: 0s !important;
  transition-duration: 0.001ms !important; transition-delay: 0s !important;
}
html.a11y-no-anim { scroll-behavior: auto !important; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important; animation-iteration-count: 1 !important;
    animation-delay: 0s !important;
    transition-duration: 0.001ms !important; transition-delay: 0s !important;
  }
  html { scroll-behavior: auto !important; }
}

/* High contrast: recolour the page, never use filter (see below).
   Only simple selectors inside :not(), so the rule still parses in older browsers. */
html.a11y-contrast body,
html.a11y-contrast body *:not(img):not(video):not(picture):not(svg) {
  background-color: #000 !important;
  color: #fff !important;
}
html.a11y-contrast a { color: #ff0 !important; }
/* border-color alone does nothing where border-style is none */
html.a11y-contrast input, html.a11y-contrast textarea,
html.a11y-contrast select, html.a11y-contrast button {
  border: 1px solid #fff !important;
}
html.a11y-contrast ::placeholder { color: #d9d9d9 !important; opacity: 1; }
/* The widget must stay readable in its own mode: keep the switch visible.
   State is carried by thumb position and aria-checked, not by colour alone. */
html.a11y-contrast { --a11y-mark: #ff5252; background-color: #000 !important; }
html.a11y-contrast [role="switch"] > span[aria-hidden="true"] {
  /* box-shadow, not border: a border would be drawn inside the 44x24 track
     under box-sizing: border-box and shift the thumb */
  background-color: #000 !important; box-shadow: 0 0 0 1px #fff !important;
}
html.a11y-contrast [role="switch"] > span[aria-hidden="true"] > span {
  background-color: #fff !important;
}

/* Font size: scale the root so rem-based sizes follow */
html.a11y-font-lg { font-size: 115%; }
html.a11y-font-sm { font-size: 88%; }

/* Readable font: leave icon fonts and bare <code> / <pre> text alone.
   Simple selectors only inside :not(). A complex argument such as
   :not(svg *) invalidates the WHOLE rule on an older engine without
   Selectors 4 support, and the mode then silently does nothing, which is
   worse than the thing it guards against. Two consequences to know:
   text inside an <svg> gets the readable font (SVG <text> is real content,
   and a chart that sets its own font is overridden), and the spans inside a
   highlighted code block are matched even though <code> and <pre> are not,
   so a syntax-highlighted block renders mixed. */
html.a11y-readable body *:not(i):not(svg):not(code):not(pre):not([class*="icon"]) {
  font-family: Arial, Helvetica, sans-serif !important;
  letter-spacing: 0.015em;
}

/* Mark headings */
html.a11y-headings h1, html.a11y-headings h2,
html.a11y-headings h3, html.a11y-headings h4 {
  outline: 2px dashed var(--a11y-mark) !important;
  outline-offset: 6px;
}

/* Mark links and buttons, except the widget's own controls */
html.a11y-links a,
html.a11y-links button:not([role="switch"]):not(#a11y-btn) {
  outline: 2px solid #3b82f6 !important;
  text-decoration: underline !important;
}
```

תגדירו את `--a11y-mark` בעצמכם; מצב הניגודיות דורס אותו באדום בהיר יותר שעובר 3:1 על שחור. קו מתאר שמפנה למשתנה CSS לא מוגדר אינו תקף בזמן החישוב, וסימון הפוקוס פשוט נעלם. עצירת `<video>` שמתנגן אוטומטית וקובצי GIF מונפשים דורשת JavaScript; ‏CSS לבד לא עוצר אותם.

## באג קריטי: CSS filter + position:fixed

**התסמין:** כפתור הווידג'ט הצף (או כותרת קבועה) "קופץ לתחתית העמוד" כשמפעילים מצב.

**הסיבה:** ‏`filter`, ‏`transform` ו-`perspective` (בכל ערך שאינו `none`) על **אב קדמון** הופכים אותו ל-containing block של צאצאי ה-`position:fixed` שלו. האלמנט הקבוע ממוקם אז ביחס לאב הקדמון ולא ל-viewport, ובעמוד ארוך `bottom: 1.5rem` פירושו 1.5rem מתחתית העמוד.

```css
/* Breaks every fixed descendant */
body     { filter: contrast(160%); }
#wrapper { filter: contrast(160%); }

/* Safe: filter only on elements that contain no fixed element you care about */
html.a11y-contrast #main-content { filter: contrast(160%); } /* widget is a sibling */

/* Best: no filter at all, recolour with CSS as in the contrast mode above */
```

**הכלל:** לעולם אל תחילו `filter`, ‏`transform` או `perspective` על אב קדמון של אלמנט `position:fixed` שחשוב לכם.

## מיקום הווידג'ט

הקובץ `layout.tsx` הוא server component; תייבאו אליו את הווידג'ט (client) ותרנדרו אותו **אחרי** `{children}`, אף פעם לא בתוך תוכן העמוד. כדי למנוע הבהוב של עיצוב ברירת המחדל לפני ש-React נטען, תחילו את ה-class השמורים עם סקריפט קטן בתוך `<head>`:

```tsx
const A11Y_BOOTSTRAP = `try{var s=JSON.parse(localStorage.getItem("a11y")||"{}"),h=document.documentElement,
m={keyboardNav:"a11y-keyboard",noAnimations:"a11y-no-anim",highContrast:"a11y-contrast",
readableFont:"a11y-readable",markHeadings:"a11y-headings",markLinks:"a11y-links"};
for(var k in m)if(s[k])h.classList.add(m[k]);
var f=s.fontScale||(s.textLarge?"lg":s.textSmall?"sm":"md");
if(f==="lg")h.classList.add("a11y-font-lg");if(f==="sm")h.classList.add("a11y-font-sm")}catch(e){}`;

<html lang="he" dir="rtl" suppressHydrationWarning>
  <head><script dangerouslySetInnerHTML={{ __html: A11Y_BOOTSTRAP }} /></head>
  <body>
    <a href="#main-content" className="sr-only focus:not-sr-only ...">דלג לתוכן הראשי</a>
    <main id="main-content" tabIndex={-1}>{children}</main>
    <AccessibilityWidget />
  </body>
</html>
```

צריך `suppressHydrationWarning` כי הסקריפט משנה את מאפיין ה-`class` של `<html>` לפני ש-React מבצע hydration. תשמרו על מפת ה-class בסקריפט ובקומפוננטה זהות.

מדריך z-index: כותרת `z-50`, כפתור ופאנל הווידג'ט `z-[200]`, קישור הדילוג `z-[9999]`. דיאלוגים מספריות UI שמרונדרים ב-portal עשויים להצטרך ערך גבוה מהווידג'ט.

## דף הצהרת נגישות

תקנה 35ה מחייבת הצהרה **במקום בולט** באתר (ובכל יישום), לפי הנחיות התקן לעניין הצהרת נגישות, שכוללת:

- מידע על התאמות הנגישות שבעל האתר ביצע
- פרטי רכז הנגישות ודרכי ההתקשרות איתו, **רק אם בעל האתר חייב למנות רכז** (החוק מחייב רכז ממעסיק של 25 עובדים, סעיף 19מב)
- פרטים ליצירת קשר לצורך הודעה על היעדר התאמה או בקשה להנגשה (חל על כולם)
- אם ניתן פטור לפי 35ו, את הפטור ואת ההתאמות החלופיות (35ו(ג))

פרקטיקה טובה מעבר לנוסח 35ה: התקן שהאתר מכוון אליו והאם ההתאמה מלאה או חלקית, מגבלות ידועות עם חלופות, ותאריך הבדיקה האחרונה. בקובץ `references/accessibility-statement.md` יש תבנית להתאמה. לעולם אל תכתבו שהאתר "עומד" ברמה מסוימת אלא אם בדיקה מצאה שכן; "התאמה חלקית" עם רשימת הפערים הידועים היא ברירת המחדל הכנה. קישור להצהרה מהפוטר הוא דרך מקובלת להציב אותה במקום בולט.

## דוגמאות

### דוגמה 1: ווידג'ט לאתר Next.js בעברית
המשתמש אומר: "תוסיף ווידג'ט נגישות לאתר ה-Next.js שלי, הוא בעברית"
פעולות:
1. להריץ קודם את רשימת WCAG ברמה AA ולדווח במה האתר עצמו נכשל (קישור דילוג, תוויות, ניגודיות)
2. ליצור את קומפוננטת ה-client עם אפקטים של שחזור ואז שמירה, מתגי `role="switch"` מעוגנים עם `left-0`, וניהול פוקוס
3. להוסיף את מצבי ה-CSS עם `--a11y-mark` מוגדר, ואת סקריפט האתחול ב-`<head>` של `layout.tsx`
4. לומר למשתמש במפורש שהווידג'ט הוא כלי נוחות ולא ציות
תוצאה: ווידג'ט שההגדרות שלו שורדות רענון, מוצג נכון ב-RTL, ולא טוען שהוא הופך את האתר לנגיש כדין.

### דוגמה 2: הצהרת נגישות לעסק קטן
המשתמש אומר: "תכתוב לי דף הצהרת נגישות"
פעולות:
1. לשאול אם הם מעסיקים 25 עובדים או יותר (סעיף הרכז) והאם יש להם פטור
2. לשאול איזו בדיקה נעשתה ומה ידוע שעדיין לא עובד
3. למלא את התבנית ב-`references/accessibility-statement.md`, עם התאמה חלקית אלא אם בדיקה קבעה אחרת, ועם דרך ליצור קשר לדיווח על בעיות
4. להציע בדיקה של מורשה לנגישות השירות לפני פרסום
תוצאה: דף הצהרה שמכסה את מה ש-35ה דורשת ולא טוען לעמידה שהאתר לא יכול לגבות.

## משאבים מצורפים

### קובצי עזר
- `references/accessibility-statement.md` -- תבנית דף הצהרה בעברית (TSX) עם סעיפי חובה וסעיפי פרקטיקה טובה, מקומות למילוי, וברירת מחדל של התאמה חלקית. להשתמש בה כשבונים את דף /accessibility.
- `references/README.md` -- מקורות לכללים הישראליים, ל-WCAG ולכלי הבדיקה.

## מלכודות נפוצות

| טעות | תיקון |
|------|-------|
| לומר ללקוח שהווידג'ט הופך את האתר לעומד בחוק | התוכן צריך לעמוד בתקן; הווידג'ט הוא כלי העדפות |
| לכתוב "WCAG 2.1 AA / ת"י 5568" כאילו הם זהים | ת"י 5568 מבוסס WCAG 2.0 ברמה AA; ‏2.1/2.2 AA הוא יעד מחמיר יותר |
| אפקט השמירה מוצהר לפני אפקט השחזור | קודם שחזור, ולא לכתוב עד שהשחזור הסתיים, אחרת ההגדרות נמחקות בכל טעינה |
| `filter` על body למצב ניגודיות | לצבוע מחדש עם CSS |
| כפתור מתג בלי עוגן פיזי | ‏`left-0` יחד עם `translateX()`; ‏`translateX` לבדו לא בטוח ל-RTL |
| שני משתנים בוליאניים לטקסט גדול וקטן | ערך `fontScale` אחד |
| ‏`var(--red)` או משתנה לא מוגדר אחר בקו מתאר | להגדיר את המשתנה, אחרת קו המתאר נעלם |
| ‏`aria-hidden` על אלמנט עם ילדים שמקבלים פוקוס | לשים `aria-hidden` רק על עטיפות דקורטיביות |
| הצהרה עם רכז נגישות לעסק של 5 אנשים | סעיף הרכז חל מ-25 עובדים |
| מתג במידות rem (`w-11`) כשהווידג'ט משנה את גופן השורש | לקבוע את המסילה והכפתור בפיקסלים כדי שההיסטים יישארו נכונים בכל מצב גופן |
| מצב ניגודיות שמשחיר גם את המתגים של הווידג'ט עצמו | להחזיר פלטה גלויה ל-`[role="switch"]` בתוך כללי הניגודיות |
| ווידג'ט בתוך תוכן העמוד | לרנדר אחרי `{children}` בלייאאוט |

## קישורי עזר

| מקור | קישור | מה לבדוק |
|------|-------|----------|
| תקנות הנגישות לשירות (נוסח עברי) | https://he.wikisource.org/wiki/%D7%AA%D7%A7%D7%A0%D7%95%D7%AA_%D7%A9%D7%95%D7%95%D7%99%D7%95%D7%9F_%D7%96%D7%9B%D7%95%D7%99%D7%95%D7%AA_%D7%9C%D7%90%D7%A0%D7%A9%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9E%D7%95%D7%92%D7%91%D7%9C%D7%95%D7%AA_%28%D7%94%D7%AA%D7%90%D7%9E%D7%95%D7%AA_%D7%A0%D7%92%D7%99%D7%A9%D7%95%D7%AA_%D7%9C%D7%A9%D7%99%D7%A8%D7%95%D7%AA%29 | תקנות 35 עד 35ו: רמה AA, הצהרה, פטורים, כתוביות, מסמכים |
| חוק שוויון זכויות לאנשים עם מוגבלות (נוסח עברי) | https://he.wikisource.org/wiki/%D7%97%D7%95%D7%A7_%D7%A9%D7%95%D7%95%D7%99%D7%95%D7%9F_%D7%96%D7%9B%D7%95%D7%99%D7%95%D7%AA_%D7%9C%D7%90%D7%A0%D7%A9%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9E%D7%95%D7%92%D7%91%D7%9C%D7%95%D7%AA | סעיף 19מב רכז, סעיף 19נא פיצוי |
| ת"י 5568 חלק 1 (מאי 2021) | https://www.isoc.org.il/files/docs/5568.pdf | איזו גרסת WCAG התקן מאמץ |
| WCAG 2.2 | https://www.w3.org/TR/WCAG22/ | ההמלצה הנוכחית של W3C ותאימות לאחור |
| MDN position | https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position | ה-containing block של אלמנטים קבועים תחת filter או transform |
| צו ה-FTC נגד accessiBe | https://www.ftc.gov/news-events/news/press-releases/2025/04/ftc-approves-final-order-requiring-accessibe-pay-1-million | למה ווידג'ט אינו טענת ציות |

## פתרון בעיות

### שגיאה: ההגדרות מתאפסות אחרי כל רענון
סיבה: אפקט השמירה רץ בטעינה עם ברירות המחדל לפני שאפקט השחזור קרא את האחסון, או שהאחסון חסום.
פתרון: קודם שחזור, להתנות את הכתיבה בדגל `loaded`, ולעטוף גם קריאה וגם כתיבה ב-try/catch.

### שגיאה: כפתור הווידג'ט קופץ לתחתית העמוד
סיבה: ‏`filter`, ‏`transform` או `perspective` על אב קדמון של הכפתור הקבוע.
פתרון: להסיר מהאב הקדמון, או להחיל את האפקט על מכל אח כמו `#main-content`.

### שגיאה: כפתור המתג יושב מחוץ למסילה בעברית
סיבה: לכפתור אין `left` פיזי, ולכן ב-RTL הוא מתחיל בקצה הימני לפני ש-`translateX` מזיז אותו עוד ימינה.
פתרון: להוסיף `left-0` ולהשתמש בהיסטים של 3px (כבוי) ו-23px (דלוק) למסילה של 44px.

### שגיאה: העמוד מהבהב בלי עיצוב לפני שהמצב השמור מוחל
סיבה: ה-class מוחלים רק אחרי hydration.
פתרון: להוסיף את סקריפט האתחול ב-`<head>` ואת `suppressHydrationWarning` על `<html>`.
