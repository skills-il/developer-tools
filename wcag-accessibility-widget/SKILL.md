---
name: wcag-accessibility-widget
description: Build a self-hosted floating accessibility widget for Israeli websites — WCAG 2.1 AA / ת"י 5568 toggles (high contrast, font size, keyboard nav, readable font, heading/link markers), settings persisted in localStorage, applied as CSS classes on <html>. Use when building an accessibility widget, implementing Israeli accessibility law compliance (חוק שוויון זכויות לאנשים עם מוגבלות), creating an הצהרת נגישות page, or debugging position:fixed elements that break under CSS filter. Covers React/Next.js component architecture, RTL-safe toggle switches, CSS class strategy, and required accessibility declaration page content. Do NOT use for third-party accessibility overlay services (UserWay, AccessiBe) or non-Israeli WCAG audits.
license: MIT
compatibility: Works with React 18+ and Next.js 13+ (App Router). No external API or service required — fully self-hosted with localStorage. Compatible with Tailwind CSS projects. RTL/Hebrew layout aware.
---

# WCAG Accessibility Widget

## Overview

A self-hosted floating accessibility widget: a fixed button that opens a panel with toggles for common WCAG 2.1 AA features. Settings are persisted in `localStorage` and applied as CSS classes on `<html>`. No third-party service needed.

---

## WCAG 2.1 AA Checklist — What to Build

Before touching any component, audit these items first:

| Item | What to check / implement |
|------|--------------------------|
| **Skip link** | `<a href="#main-content">` in layout, visually hidden, visible on focus. Target `<main id="main-content" tabIndex={-1}>` |
| **Alt text** | Every `<img>` has descriptive `alt`. Decorative images get `alt=""` + `aria-hidden="true"` |
| **Color contrast** | Normal text ≥ 4.5:1, large text ≥ 3:1. Common fail: `text-gray-500` on dark bg (~3.9:1) → use `text-gray-400` |
| **Keyboard navigation** | All interactive elements reachable by Tab. Test with keyboard only |
| **ARIA labels** | `aria-label` on icon-only buttons, `aria-expanded` on toggles, `aria-label` on `<nav>` when multiple navs exist |
| **Decorative elements** | Emoji, underline spans, SVG icons with adjacent text → `aria-hidden="true"` |
| **Lang + dir** | `<html lang="he" dir="rtl">` (or your locale) on the root element |
| **Mobile responsive** | Site usable on mobile without horizontal scroll |
| **Accessibility declaration** | Required by Israeli law (חוק שוויון זכויות) — page at `/accessibility` |
| **Privacy policy** | `/privacy-policy` listing exactly what data the form collects |

---

## Widget Architecture

### 1. Settings type + CSS class map

```ts
type Settings = {
  keyboardNav: boolean;
  noAnimations: boolean;
  highContrast: boolean;
  textLarge: boolean;    // mutually exclusive with textSmall
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

### 2. Apply classes to `<html>` + persist

```ts
useEffect(() => {
  const html = document.documentElement;
  (Object.keys(settings) as (keyof Settings)[]).forEach((key) => {
    html.classList.toggle(CLASS_MAP[key], settings[key]);
  });
  localStorage.setItem("a11y", JSON.stringify(settings));
}, [settings]);
```

### 3. Restore on mount

```ts
useEffect(() => {
  try {
    const saved = localStorage.getItem("a11y");
    if (saved) setSettings(JSON.parse(saved));
  } catch { /* ignore */ }
}, []);
```

### 4. Close on Escape + outside click

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

### 5. Toggle switch component (RTL-safe)

Use `transform: translateX()` — CSS transforms are always physical (not RTL-flipped):

```tsx
<span
  aria-hidden="true"
  className="absolute top-[3px] h-[18px] w-[18px] rounded-full bg-white shadow-sm transition-transform duration-200"
  style={{ transform: `translateX(${active ? "21px" : "3px"})` }}
/>
```

Track: `w-11 h-6` (44×24px). Thumb: 18×18px with 3px padding each side → on=21px, off=3px.

---

## CSS Modes (globals.css)

```css
/* Keyboard nav */
html.a11y-keyboard *:focus,
html.a11y-keyboard *:focus-visible {
  outline: 3px solid var(--red) !important;
  outline-offset: 3px !important;
}

/* No animations */
html.a11y-no-anim *, html.a11y-no-anim *::before, html.a11y-no-anim *::after {
  animation-duration: 0.001ms !important;
  transition-duration: 0.001ms !important;
}
html.a11y-no-anim { scroll-behavior: auto !important; }

/* High contrast — see critical bug below, DO NOT use filter on body/html */
html.a11y-contrast { --bg: #000; --bg2: #000; --muted: #e8e8e8; }
html.a11y-contrast body { background-color: #000 !important; }
html.a11y-contrast .text-gray-400 { color: #ebebeb !important; }
html.a11y-contrast .text-gray-500 { color: #e0e0e0 !important; }

/* Font sizes — scale root rem so all rem-based units scale */
html.a11y-font-lg { font-size: 115%; }
html.a11y-font-sm { font-size: 88%; }

/* Readable font */
html.a11y-readable, html.a11y-readable * {
  font-family: Arial, Helvetica, sans-serif !important;
  letter-spacing: 0.015em;
}

/* Mark headings */
html.a11y-headings h1, html.a11y-headings h2,
html.a11y-headings h3, html.a11y-headings h4 {
  outline: 2px dashed var(--red) !important;
  outline-offset: 6px;
}

/* Mark links / buttons (exclude widget's own toggles) */
html.a11y-links a,
html.a11y-links button:not([role="switch"]):not(#a11y-btn) {
  outline: 2px solid #3b82f6 !important;
  text-decoration: underline !important;
}
```

---

## Critical Bug: CSS filter + position:fixed

**Symptom:** Floating widget button (or sticky header) "jumps to the bottom of the page" when a mode is activated.

**Root cause:** CSS `filter` (and `transform`, `perspective`) on any **ancestor** of a `position:fixed` element makes that element position relative to the filtered ancestor instead of the viewport. On a long page, `bottom: 1.5rem` becomes 1.5rem from the bottom of the page, not the viewport.

**What breaks it:**
```css
/* ❌ Any of these on an ancestor of a fixed element */
body    { filter: contrast(160%); }   /* breaks ALL fixed descendants */
#wrapper { filter: contrast(160%); }  /* breaks fixed descendants */
```

**Safe approaches:**
```css
/* ✅ Target only non-ancestor elements */
/* Apply filter to the element itself (not its ancestor) */
html.a11y-contrast header { filter: contrast(160%); }  /* header is fixed but filter is ON it, not ancestor */
html.a11y-contrast #main-content { filter: contrast(160%); }  /* widget is sibling, not descendant */

/* ✅ Best: avoid filter entirely — use CSS variable overrides */
html.a11y-contrast { --bg: #000; --muted: #e0e0e0; }
html.a11y-contrast body { background-color: #000 !important; }
```

**Rule:** Never apply `filter`, `transform`, or `perspective` to any element that is an ancestor of a `position:fixed` element you care about.

---

## Widget Placement

Place widget in `layout.tsx` body, **after** `{children}` — never inside page content:

```tsx
<body>
  <a href="#main-content" className="sr-only focus:not-sr-only ...">דלג לתוכן הראשי</a>
  {children}          {/* page content — Header (fixed) + main */}
  <AccessibilityWidget />   {/* fixed button + panel, sibling of children */}
</body>
```

z-index guide:
- Header: `z-50`
- Widget button + panel: `z-[200]`
- Skip link: `z-[9999]`

---

## Accessibility Declaration Page (Israeli Law)

Required by חוק שוויון זכויות לאנשים עם מוגבלות. Must include:

- Statement of conformance level (WCAG 2.1 AA / ת"י 5568)
- List of adaptations made
- Known limitations
- Accessibility coordinator contact (name + phone)
- Date of last review
- Reference to נציב שוויון זכויות for unresolved complaints

Link from footer alongside privacy policy.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `filter` on body for contrast mode | Use CSS variable overrides instead |
| `aria-hidden` on element with focusable children | Move `aria-hidden` to purely decorative wrapper |
| Two `<nav>` elements without labels | Add `aria-label` to each nav |
| `text-gray-500` on dark bg | Fails 4.5:1 — use `text-gray-400` minimum |
| Font size via `px` overrides | Use `font-size: %` on `<html>` so all `rem` units scale |
| Toggle thumb using RTL-aware positioning | Use `translateX()` — it's always physical, not RTL-flipped |
| Widget inside page content | Place after `{children}` in layout, never inside main |
