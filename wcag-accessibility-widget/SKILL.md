---
name: wcag-accessibility-widget
description: 'Not legal advice. Build a self-hosted accessibility preferences widget for Israeli React or Next.js websites (high contrast, font size, keyboard focus highlighting, readable font, heading and link markers, stop animations) and the הצהרת נגישות statement page, framed correctly against the Israeli legal floor (ת"י 5568 at level AA, based on WCAG 2.0). Use when building an accessibility widget or toolbar, adding the accessibility statement page, making the toggles work in RTL, or debugging position:fixed elements that break under CSS filter. The widget is a comfort tool and does not by itself make a site compliant. Do NOT use for third-party overlay services (UserWay, AccessiBe), non-Israeli WCAG audits, or exemption, enforcement and full-site compliance questions (use israeli-accessibility-compliance).'
license: MIT
compatibility: Works with React 18+ and Next.js 13+ (App Router). No external API or service required, fully self-hosted with localStorage. Compatible with Tailwind CSS projects. RTL/Hebrew layout aware.
---

# WCAG Accessibility Widget

## Legal notice

This skill explains the Israeli web accessibility rules in general terms and helps you build a preferences widget and a statement page. It is not legal advice and not an accessibility audit. A widget does not by itself make a site meet ת"י 5568: the obligation is on the site's own content and markup. Whether a particular site is obliged, exempt, or conforms is a question for a מורשה לנגישות השירות or a lawyer who has examined that site.

## Overview

A self-hosted floating accessibility widget: a fixed button that opens a panel of preference toggles. Settings are persisted in `localStorage` and applied as CSS classes on `<html>`. No third-party service needed.

**Build the site right first, then add the widget.** The regulation requires the content itself to conform. A toolbar does not add missing labels, fix focus order, caption a video, or tag a PDF. In April 2025 the US FTC approved a final order requiring accessiBe to pay $1 million over claims that its widget could make any website WCAG-compliant. Never describe the widget to a client as the compliance solution.

## The Israeli Legal Floor

| Topic | What the rules say |
|-------|-------------------|
| Standard | Regulation 35א(א): web services must meet the "תקן נגישות אינטרנט", defined in regulation 35 as ת"י 5568, **at level AA**. |
| WCAG version | The May 2021 edition of ת"י 5568 Part 1 replaced the March 2013 edition and still adopts **WCAG 2.0** (December 2008) with Israeli changes. WCAG 2.1 and 2.2 AA are supersets; W3C states that content conforming to 2.2 also conforms to 2.0 and 2.1. Target 2.1 or 2.2 AA, but do not write "WCAG 2.1 = ת"י 5568". |
| Documents | A document such as a PDF prepared from 26 October 2017 and uploaded to the site must be accessible (35א(ג)). |
| Video | Captions for prerecorded video (SC 1.2.2) are required of public authorities and of businesses whose average turnover exceeds 5 million NIS that edit or produce recorded video (35ד). |
| Exemptions | An עוסק פטור, or a business whose average annual turnover does not exceed 100,000 NIS, is exempt from the web chapter (35ו(ז)). Other exemptions exist (35ו). Do not decide exemption for a client; point them to the regulation and a professional. |
| Notice and cure | A deviation is not treated as a breach unless the owner received notice and did not fix it within a reasonable time, no later than 60 days (35א(ד)). |
| Exposure | A court may award compensation of up to 50,000 NIS without proof of damage for a breach of the accessibility provisions (Equal Rights law, s.19נא(ב)); the figure is index-linked. |

## WCAG AA Checklist: What to Build

Audit these before touching the widget:

| Item | What to check / implement |
|------|--------------------------|
| **Skip link** | `<a href="#main-content">` in layout, visually hidden, visible on focus. Target `<main id="main-content" tabIndex={-1}>` (one per page) |
| **Alt text** | Every `<img>` has descriptive `alt`. Decorative images get `alt=""` |
| **Color contrast** | Normal text 4.5:1, large text 3:1. Tailwind `text-gray-500` fails on dark backgrounds (3.67:1 on `gray-900`, 3.04:1 on `gray-800`); `text-gray-400` passes (6.99:1 on `gray-900`). Measure your actual pair |
| **Keyboard and focus** | Everything reachable and operable by Tab, Enter and Space; a visible focus indicator on every control |
| **Forms** | Every input has a programmatic label; errors are identified in text, not by color alone |
| **ARIA** | `aria-label` on icon-only buttons, `aria-expanded` on disclosure buttons, `aria-label` on each `<nav>` when there are several |
| **Lang + dir** | `<html lang="he" dir="rtl">` (or your locale) on the root element |
| **Resize and zoom** | Text readable at 200% browser zoom without lost content; the widget's font toggle does not replace this |
| **Motion** | Honour `prefers-reduced-motion` by default, not only through a toggle |
| **Media and documents** | Captions where 35ד applies; accessible PDFs from 2017 on |
| **Accessibility statement** | Required by regulation 35ה, see below |

## Widget Architecture

The component is a client component. Put `"use client";` at the top of the file.

### 1. Settings, defaults, class map

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

### 2. Restore, then apply and persist

Restore must finish before anything is written. If the persist effect runs first on mount, it writes the defaults over the saved settings and the user's choices never survive a reload.

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

### 3. Trigger button and panel

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

### 4. Focus in, Escape out, focus back

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

### 5. Toggle switch (RTL-safe)

`translateX()` is physical, so it only stays RTL-safe if the thumb's starting point is physical too. An absolutely positioned element with no `left`/`right` sits at its static position, which in an RTL container is the RIGHT edge; `translateX` then pushes it out of the track. Anchor it with `left-0` (physical `left: 0`), not `start-0`.

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

Track is 44 by 24px and the thumb 18px with 3px clearance: off = 3px, on = 44 - 18 - 3 = 23px. Keep those in px, not `w-11 h-6`: the font-size modes change the root size, so rem-based track widths drift away from the fixed pixel offsets (at 88% the thumb overhangs the track, at 115% it stops short). For font size use three buttons with `aria-pressed`, setting `fontScale`.

## CSS Modes (globals.css)

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

Define `--a11y-mark` yourself; contrast mode overrides it with a lighter red that clears 3:1 on black. An outline that references an undefined custom property is invalid at computed-value time, so the focus outline silently disappears. Pausing autoplaying `<video>` and animated GIFs needs JavaScript; CSS alone does not stop them.

## Critical Bug: CSS filter + position:fixed

**Symptom:** The floating widget button (or a fixed header) "jumps to the bottom of the page" when a mode is activated.

**Root cause:** `filter`, `transform` and `perspective` (any value other than `none`) on an **ancestor** make that ancestor the containing block for its `position:fixed` descendants. The fixed element is then positioned relative to that ancestor, not the viewport, so on a long page `bottom: 1.5rem` means 1.5rem from the bottom of the page.

```css
/* Breaks every fixed descendant */
body     { filter: contrast(160%); }
#wrapper { filter: contrast(160%); }

/* Safe: filter only on elements that contain no fixed element you care about */
html.a11y-contrast #main-content { filter: contrast(160%); } /* widget is a sibling */

/* Best: no filter at all, recolour with CSS as in the contrast mode above */
```

**Rule:** Never apply `filter`, `transform` or `perspective` to an ancestor of a `position:fixed` element you care about.

## Widget Placement

`layout.tsx` is a server component; import the client widget and render it **after** `{children}`, never inside page content. To avoid a flash of default styles before React hydrates, apply the saved classes with a small inline script in `<head>`:

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

`suppressHydrationWarning` is needed because the script changes the `class` attribute of `<html>` before React hydrates. Keep the class map in the script and in the component identical.

z-index guide: header `z-50`, widget button and panel `z-[200]`, skip link `z-[9999]`. Portalled dialogs from UI libraries may need a higher value than the widget.

## Accessibility Statement Page

Regulation 35ה requires a statement **in a prominent place** on the site (and in any app), following the standard's guidance on accessibility statements, that includes:

- information about the accessibility adaptations the owner made
- the accessibility coordinator's details and how to contact them, **only if the owner must appoint one** (the law requires a coordinator from 25 employees, s.19מב)
- contact details for reporting a missing adaptation or requesting one (this applies to everyone)
- where an exemption under 35ו was granted, the exemption and the alternative adaptations (35ו(ג))

Good practice beyond the text of 35ה: the standard the site targets and whether conformance is full or partial, known limitations with alternatives, and the date of the last review. `references/accessibility-statement.md` has a template to adapt. Never state that the site "meets" a level unless an audit found it does; "partial conformance" with a list of known gaps is the honest default. Linking the statement from the footer is a common way to make it prominent.

## Examples

### Example 1: Widget for a Hebrew Next.js site
User says: "Add an accessibility widget to my Next.js site, it's in Hebrew"
Actions:
1. Run the WCAG AA checklist first and report what the site itself fails (skip link, labels, contrast)
2. Create the client component with restore-then-persist effects, `role="switch"` toggles anchored with `left-0`, and focus management
3. Add the CSS modes with `--a11y-mark` defined, and the `<head>` bootstrap script in `layout.tsx`
4. Tell the user plainly that the widget is a comfort tool, not compliance
Result: A widget whose settings survive reloads, renders correctly in RTL, and does not claim to make the site compliant.

### Example 2: Accessibility statement for a small business
User says: "Write me a הצהרת נגישות page"
Actions:
1. Ask whether they employ 25 or more people (coordinator section) and whether they hold an exemption
2. Ask which audit was done and what is known not to work
3. Fill the template in `references/accessibility-statement.md`, with partial conformance unless an audit says otherwise, and a contact route for reporting problems
4. Suggest a מורשה לנגישות השירות review before publishing
Result: A statement page that covers the items 35ה requires and makes no conformance claim the site cannot back.

## Bundled Resources

### References
- `references/accessibility-statement.md` -- Hebrew statement page template (TSX) with required and good-practice sections, placeholders, and a partial-conformance default. Use when building the /accessibility page.
- `references/README.md` -- sources for the Israeli rules, WCAG and testing tools.

## Gotchas

| Mistake | Fix |
|---------|-----|
| Telling a client the widget makes the site compliant | The content must conform; the widget is a preferences tool |
| Writing "WCAG 2.1 AA / ת"י 5568" as if they were the same | ת"י 5568 is WCAG 2.0-based at AA; 2.1/2.2 AA is a stricter target |
| Persist effect declared before restore | Restore first and skip writes until restored, or saved settings are wiped on every load |
| `filter` on body for contrast mode | Recolour with CSS instead |
| Toggle thumb with no physical anchor | `left-0` plus `translateX()`; `translateX` alone is not RTL-safe |
| Two booleans for large and small text | One `fontScale` value |
| `var(--red)` or another undefined variable in an outline | Define the variable, or the outline is dropped |
| `aria-hidden` on an element with focusable children | Put `aria-hidden` only on purely decorative wrappers |
| Statement listing a coordinator for a 5-person business | The coordinator section applies from 25 employees |
| Toggle sized in rem (`w-11`) while the widget scales the root font | Size the track and thumb in px so the offsets stay correct in every font mode |
| Contrast mode that also blacks out the widget's own switches | Re-assert a visible palette for `[role="switch"]` inside the contrast rules |
| Widget inside page content | Render after `{children}` in the layout |

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Service accessibility regulations (Hebrew text) | https://he.wikisource.org/wiki/%D7%AA%D7%A7%D7%A0%D7%95%D7%AA_%D7%A9%D7%95%D7%95%D7%99%D7%95%D7%9F_%D7%96%D7%9B%D7%95%D7%99%D7%95%D7%AA_%D7%9C%D7%90%D7%A0%D7%A9%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9E%D7%95%D7%92%D7%91%D7%9C%D7%95%D7%AA_%28%D7%94%D7%AA%D7%90%D7%9E%D7%95%D7%AA_%D7%A0%D7%92%D7%99%D7%A9%D7%95%D7%AA_%D7%9C%D7%A9%D7%99%D7%A8%D7%95%D7%AA%29 | Regulations 35 to 35ו: level AA, statement, exemptions, captions, documents |
| Equal Rights for Persons with Disabilities Law (Hebrew text) | https://he.wikisource.org/wiki/%D7%97%D7%95%D7%A7_%D7%A9%D7%95%D7%95%D7%99%D7%95%D7%9F_%D7%96%D7%9B%D7%95%D7%99%D7%95%D7%AA_%D7%9C%D7%90%D7%A0%D7%A9%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9E%D7%95%D7%92%D7%91%D7%9C%D7%95%D7%AA | s.19מב coordinator, s.19נא compensation |
| ת"י 5568 Part 1 (May 2021) | https://www.isoc.org.il/files/docs/5568.pdf | Which WCAG version the standard adopts |
| WCAG 2.2 | https://www.w3.org/TR/WCAG22/ | Current W3C Recommendation and backward compatibility |
| MDN position | https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position | Containing block of fixed elements under filter or transform |
| FTC order against accessiBe | https://www.ftc.gov/news-events/news/press-releases/2025/04/ftc-approves-final-order-requiring-accessibe-pay-1-million | Why a widget is not a compliance claim |

## Troubleshooting

### Error: settings reset after every reload
Cause: the persist effect ran on mount with the default state before the restore effect read storage, or storage is blocked.
Solution: restore first, gate the write on a `loaded` flag, and wrap both reads and writes in try/catch.

### Error: widget button jumps to the bottom of the page
Cause: a `filter`, `transform` or `perspective` on an ancestor of the fixed button.
Solution: remove it from the ancestor, or apply the effect to a sibling container such as `#main-content`.

### Error: toggle thumb sits outside the track in Hebrew
Cause: the thumb has no physical `left`, so in RTL it starts at the right edge before `translateX` moves it further right.
Solution: add `left-0` and use offsets of 3px (off) and 23px (on) for a 44px track.

### Error: page flashes unstyled before the saved mode applies
Cause: classes are applied only after hydration.
Solution: add the `<head>` bootstrap script and `suppressHydrationWarning` on `<html>`.
