# hebrew-rtl: Hebrew and RTL adaptation for open-slide

This file is the central Hebrew/RTL reference for open-slide. The upstream framework has zero Hebrew or RTL coverage in its own skill files; this file fills that gap. Read it before authoring any Hebrew or bilingual deck.

## TL;DR

For a Hebrew or bilingual `slides/<id>/index.tsx`:

1. Set `dir="rtl"` on the **page component's root `<div>`** only (never on `<html>`, that breaks the dev server chrome).
2. Use **logical CSS** everywhere: `paddingInline`, `paddingInlineStart`, `marginInlineStart`, `insetInlineStart`, `text-align: 'start'`. Never physical (`paddingLeft`, `marginLeft`, `left`, `text-align: 'left'`) inside the page root.
3. Load **Hebrew Google Fonts** (Heebo, Rubik, Assistant, Noto Sans Hebrew, Frank Ruhl Libre, Suez One) via the global stylesheet OR `@import` in a `<style>` block at the top of the page. List them first in `DesignSystem.fonts.display` / `fonts.body`, with the system stack as fallback.
4. **Bump the type scale by ~10–15%** for Hebrew (Hebrew renders wider per character at the same px size).
5. Wrap any Latin run inside Hebrew copy in `<bdi>` to prevent bidi punctuation glitches: `השתמשו ב-<bdi>React Router</bdi>`.
6. The 1080px **vertical budget rule still applies**, but recompute it for Hebrew at the larger heading sizes you picked in step 4.

The remaining sections explain each of these in depth.

## 1. The `dir` attribute: page root, not document

The upstream `slide-authoring` reference is silent on `dir`. The default is whatever `<html>` carries, which is `ltr` in the upstream scaffolder. Resist the urge to flip it globally:

```tsx
// ❌ WRONG, flips the upstream dev server chrome (file rail, navigation arrows, inspector)
document.documentElement.setAttribute('dir', 'rtl');
```

```tsx
// ✅ RIGHT, flip on the page root only. The canvas content goes RTL; the chrome stays LTR.
const Cover: Page = () => (
  <div
    dir="rtl"
    style={{ width: '100%', height: '100%', /* ... */ }}
  >
    ...
  </div>
);
```

If every page in the deck is Hebrew, repeat `dir="rtl"` on each page root. There is no project-level "this slide is RTL" config, open-slide treats each page as an independent React component.

For a bilingual deck where some pages are English and others Hebrew, set `dir` per page accordingly. Mixing is fine.

## 2. Logical CSS properties (the most-violated rule)

Inside any container with `dir="rtl"`, **physical CSS properties read backwards**: `paddingLeft: 160` puts the padding on the *visual right* (since "left" in document order is the right edge in RTL). This is the single most common bug when adapting an upstream open-slide template to Hebrew.

| Physical (avoid in `dir="rtl"`) | Logical (RTL-safe)              |
| ------------------------------- | ------------------------------- |
| `paddingLeft`                   | `paddingInlineStart`            |
| `paddingRight`                  | `paddingInlineEnd`              |
| `marginLeft`                    | `marginInlineStart`             |
| `marginRight`                   | `marginInlineEnd`               |
| `left` (in `position: absolute`) | `insetInlineStart`              |
| `right` (in `position: absolute`) | `insetInlineEnd`              |
| `borderLeft`                    | `borderInlineStart`             |
| `borderRight`                   | `borderInlineEnd`               |
| `text-align: 'left'`            | `text-align: 'start'`           |
| `text-align: 'right'`           | `text-align: 'end'`             |
| `padding: '0 160px'` (symmetric) | `paddingInline: 160` (same effect, name-correct) |
| `padding: '120px 160px'`        | `padding: '120px 160px'` (vertical/horizontal block-axis is unchanged; safe) |

The block-axis properties (`paddingTop`, `paddingBottom`, `marginTop`, `marginBottom`, `top`, `bottom`) are **not** affected by `dir`, those map to writing-mode, which open-slide doesn't tilt. Leave them as physical.

### Worked example (the upstream starter, Hebrew-adapted)

```tsx
// upstream (LTR):
const Cover: Page = () => (
  <div style={{
    width: '100%', height: '100%',
    background: 'var(--osd-bg)', color: 'var(--osd-text)',
    display: 'flex', flexDirection: 'column', justifyContent: 'center',
    padding: '0 160px',
  }}>
    <div style={{ fontSize: 28, color: 'var(--osd-accent)', letterSpacing: '0.2em' }}>
      CHAPTER 01
    </div>
    <h1 style={{ fontSize: 'var(--osd-size-hero)', fontWeight: 900, margin: '32px 0' }}>
      The Big Idea
    </h1>
  </div>
);

// Hebrew-adapted (RTL):
const Cover: Page = () => (
  <div
    dir="rtl"
    style={{
      width: '100%', height: '100%',
      background: 'var(--osd-bg)', color: 'var(--osd-text)',
      display: 'flex', flexDirection: 'column', justifyContent: 'center',
      paddingInline: 160,           // was: padding: '0 160px'
      textAlign: 'start',            // explicit; default with dir="rtl" is right-aligned
      fontFamily: 'var(--osd-font-body)',
    }}
  >
    <div style={{ fontSize: 28, color: 'var(--osd-accent)', letterSpacing: '0.2em' }}>
      פרק 01
    </div>
    <h1 style={{ fontSize: 'var(--osd-size-hero)', fontWeight: 900, margin: '32px 0', lineHeight: 1.1 }}>
      הרעיון הגדול
    </h1>
  </div>
);
```

Note: `letterSpacing` is direction-agnostic in CSS, but in Hebrew, **wide letter-spacing on body copy reduces legibility** because Hebrew letters depend on visual proximity for word boundaries (no spaces between letters in some ligatures). Reserve `letterSpacing: '0.2em'` for short ALL-CAPS-equivalent labels in English ("CHAPTER 01") or Hebrew labels under 4 characters; otherwise drop it to `0` or `0.02em`.

## 3. Hebrew Google Fonts

The upstream `DesignSystem.fonts` defaults to system stacks. macOS resolves Hebrew to Helvetica or Arial Hebrew, which is acceptable for body text but looks weak at the upstream hero scale (140–200px). For decks that ship beyond a dev machine, use Google Fonts.

### Recommended families (Hebrew subset)

| Family                | Style              | Weights commonly available | Use for                          |
| --------------------- | ------------------ | -------------------------- | -------------------------------- |
| **Heebo**             | Geometric sans     | 100–900                    | General workhorse, body + display |
| **Rubik**             | Friendly geometric | 300–900                    | Decks with playful or warm tone   |
| **Assistant**         | Humanist sans      | 200–800                    | Body copy where Heebo feels cold  |
| **Noto Sans Hebrew**  | Neutral sans       | 100–900                    | Maximum compatibility, multilingual decks |
| **Frank Ruhl Libre**  | Serif (editorial)  | 300–900                    | Editorial/Q-deck headings; classy |
| **Suez One**          | Slab display       | 400 only                   | Hero-only, single weight          |

Avoid: David Libre (system-y, looks dated at large sizes), VarelaRound (cute but the round terminals fight large hero sizes).

### Loading them

There are three options. The first is recommended because it works without modifying anything outside `slides/<id>/`.

**Option A: `@import` inside the page (simplest, slide-scoped):**

```tsx
const Cover: Page = () => (
  <>
    <style>{`
      @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700;900&display=swap&subset=hebrew');
    `}</style>
    <div dir="rtl" style={{ /* ... */ fontFamily: 'Heebo, system-ui, sans-serif' }}>
      ...
    </div>
  </>
);
```

The `subset=hebrew` URL parameter ships only the Hebrew glyph subset (smaller payload). Drop it if the deck mixes Latin and you want the same font for both.

**Option B: Reference in `DesignSystem.fonts` (so the Design panel can tweak it):**

```tsx
export const design: DesignSystem = {
  palette: { bg: '#0f172a', text: '#f8fafc', accent: '#fbbf24' },
  fonts: {
    display: 'Heebo, system-ui, -apple-system, sans-serif',
    body: 'Heebo, system-ui, -apple-system, sans-serif',
  },
  typeScale: { hero: 200, body: 40 },   // bumped from upstream 180/36 for Hebrew
  radius: 12,
};
```

Pair this with the `@import` in a `<style>` block at the page top, since `DesignSystem.fonts` only declares the CSS `font-family` value, it does NOT load the font file. (The Design panel reads `DesignSystem.fonts` to render its preview; it does not own font loading.)

**Option C: Project-level injection.** If you control the project (not just `slides/`), add `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;700;900&family=Rubik:wght@400;700;900&display=swap&subset=hebrew">` to the project's `index.html` template once. Per-slide work then just references the family name. The upstream "do not touch package.json or open-slide.config.ts" rule does NOT cover `index.html`, but when in doubt, prefer Option A (slide-scoped), it keeps the slide self-contained.

### Exporting to PDF / PPTX

Recent open-slide builds stopped force-loading every registered font into the export root and subset webfonts instead, so an export only embeds the glyphs a deck actually uses. For Hebrew decks this matters: keep the `&subset=hebrew` parameter on the Google Fonts URL (Option A/C above) so the PDF/PPTX export embeds the Hebrew glyph set cleanly rather than falling back to a system Hebrew face (David / Times) in the exported file. If a hero uses only a handful of Hebrew characters, the tighter `&text=...` parameter subsets even further. Verify the exported PDF renders Hebrew in the intended webfont, not a fallback serif, before sharing it.

## 3.5. Code blocks inside Hebrew slides

A common pattern is showing English code samples inside an otherwise Hebrew page (Before/After comparisons, install commands, API examples). The `<pre>` element needs three things:

```tsx
<pre
  dir="ltr"
  style={{
    fontFamily: '"JetBrains Mono", ui-monospace, monospace',
    fontSize: 22,
    lineHeight: 1.6,
    color: PALETTE.cream,
    margin: 0,
    whiteSpace: 'pre-wrap',
    textAlign: 'start',  // critical: 'start' inside dir="ltr" = left, regardless of outer RTL
  }}
>
  {code}
</pre>
```

- **`dir="ltr"`**: makes the code itself flow LTR (so `const x = 1` reads naturally), even though the surrounding slide is RTL.
- **`textAlign: 'start'`**: without this, the `<pre>` may inherit `textAlign: 'right'` or `'end'` from the RTL parent, pushing the code to the visual right edge of the box. `'start'` is logical-property aware: in a `dir="ltr"` element it resolves to `left`. Don't use `'left'` directly, same outcome here, but breaks if you ever wrap the code block in another RTL container.
- **`whiteSpace: 'pre-wrap'`**: preserves indentation but allows wrapping if the code line exceeds the box width.

Card labels above code blocks (e.g., "אחרי · RTL מלא, פונט עברי") stay in the outer RTL flow. Only the `<pre>` flips. The mixed-direction layout works because each container declares its own direction explicitly.

## 4. Hebrew-aware type scale

Hebrew letters at the same `font-size` render approximately 10–15% wider per character than Latin in the same family (because Hebrew has no ascenders/descenders pulling it taller, the design space is mostly horizontal). Effects:

- A hero title that fits on one line in English at 140px may wrap to two in Heebo at the same size.
- A bullet that fits on one line at 40px in English wraps in Hebrew if the copy length is matched.
- Padding-inline still works fine; it's the **content width** that's tighter.

### Recommended adjustments

Take the upstream type scale and apply a Hebrew tax:

| Element          | Upstream (Latin) | Hebrew suggestion |
| ---------------- | ---------------- | ----------------- |
| Hero title       | 140–200px        | 160–220px (+10–15%) |
| Section heading  | 80–120px         | 88–132px (+10%)     |
| Page heading     | 56–80px          | 60–88px (+8%)       |
| Body text        | 32–44px          | 32–44px (unchanged) |
| Caption / label  | 22–28px          | 22–28px (unchanged) |

Body and caption sizes are unchanged because at small sizes the per-character width difference is negligible relative to the line being long anyway. The bump is concentrated at hero / section sizes where line-wrapping is binary (1 line vs 2).

### Vertical budget reminder

The 1080px vertical-budget math from upstream still applies. Recompute it with the bumped Hebrew sizes:

```
Heading (Hebrew hero): 200px × 1.1 line-height × 1 line = 220px
Gap:                                                       64px
Body paragraph (Hebrew): 40px × 1.6 × 3 lines           = 192px
Gap:                                                       48px
5 bullets (Hebrew): 40px × 1.6 × 1 line each            = 320px
4 gaps between bullets: 24px each                       =  96px
TOTAL                                                     940px
+ 2 × 120px padding                                      = 1180px

→ 1180 > 1080 → split the page.
```

The same content that fits in English at 80px hero will overflow in Hebrew at the +10% bumped 88px. **Always recompute the budget after bumping the scale.**

### Worked-example failure: the cover that didn't fit

A real failure observed while building a Hebrew open-slide deck:

```tsx
// This LTR-style cover fit in English:
<h1 style={{ fontSize: 232, lineHeight: 0.98 }}>
  מצגות
  <br />
  ב-open-slide
  <br />
  בעברית.
</h1>
```

Hebrew cover budget at 232px × 0.98 line-height × 3 lines = 682px. Add eyebrow (50px) + margin (64px) + 3-line subtitle at 44px × 1.45 = 191px + bottom padding (120px) + 80px footer + top padding (120px). **Total: 1307px**. Overflowed by 227px and the subtitle visibly collided with the footer.

**Fix:** drop to 2 lines AND tighten the layout:

```tsx
<h1 style={{ fontSize: 240, lineHeight: 0.95 }}>
  <bdi style={{ color: PALETTE.brand }}>open-slide</bdi>
  <br />
  בעברית.
</h1>
```

2 lines × 240 × 0.95 = 456px. Same visual punch, fits the canvas. **A 3-line Hebrew hero almost always overflows. Default to 1–2 lines on covers and section dividers.**

### Line-height for Hebrew

Hebrew benefits from slightly tighter line-height than the upstream defaults at hero sizes (Hebrew has no ascenders/descenders so the optical line gap looks larger than Latin):

- Hero (160–220px): `lineHeight: 1.1` (upstream default 1.05, a touch too tight)
- Section heading: `lineHeight: 1.15`
- Page heading: `lineHeight: 1.2` (unchanged)
- Body: `lineHeight: 1.5` (a touch tighter than upstream's 1.6, feels right in Hebrew)
- Caption: `lineHeight: 1.4`

## 5. Bidirectional text: `<bdi>` for mixed Hebrew + Latin

Hebrew copy frequently embeds Latin tokens: brand names, code identifiers, URLs, version numbers. The browser's bidi (Unicode Bidirectional) algorithm tries to figure out where each run goes, but it gets edge cases wrong, especially around:

- Punctuation between Hebrew and Latin: `קוד-React` may render the hyphen on the wrong side.
- Numbers near brand names: `React 18` inside Hebrew can flip to `18 React` visually.
- Trailing parens: `(npm)` after a Hebrew word can land in the wrong place.

The fix is `<bdi>` (Bidirectional Isolate). It tells the bidi algorithm: "treat this span as a self-contained unit, don't merge its direction with the surrounding text."

```tsx
// ❌ Without isolation, punctuation may render in surprising places
<p>השתמשו בספריית React Router לניתוב.</p>

// ✅ Wrap the Latin run
<p>השתמשו בספריית <bdi>React Router</bdi> לניתוב.</p>
```

Use `<bdi>` for:
- Brand names (`<bdi>Vercel</bdi>`, `<bdi>Supabase</bdi>`)
- Code identifiers in prose (`<bdi>useEffect</bdi>`)
- URLs in body text (`<bdi>agentskills.co.il</bdi>`)
- Version numbers attached to a Latin name (`<bdi>React 18.3</bdi>`)
- Email addresses, file paths, anything that mixes Hebrew + Latin + punctuation

**You do NOT need `<bdi>` for:**
- Pure Latin runs (English-only paragraphs)
- Pure Hebrew runs (Hebrew-only paragraphs)
- Numbers in Hebrew financial copy (e.g. "₪1,500" or "1,500 ש״ח", the bidi algorithm handles these correctly)
- Logos as `<img>` (they're not text, no bidi to worry about)

CSS alternative: `unicode-bidi: isolate` on a `<span>` does the same thing. `<bdi>` is the semantic shortcut.

## 6. RTL flexbox layouts

CSS Flexbox respects `dir`. In a `dir="rtl"` container:

| flex property                | LTR behavior | RTL behavior |
| ---------------------------- | ------------ | ------------ |
| `flexDirection: 'row'`       | left → right | right → left (flips automatically) |
| `flexDirection: 'row-reverse'` | right → left | left → right (flips automatically) |
| `flexDirection: 'column'`    | top → bottom (unchanged) | top → bottom (unchanged) |
| `justifyContent: 'flex-start'` | left edge | right edge (flips automatically) |
| `justifyContent: 'space-between'` | spreads horizontally (unchanged direction-wise) | same |

So for a horizontal layout like a footer with brand-on-the-left, page-counter-on-the-right (upstream pattern):

```tsx
// Upstream Footer:
<div style={{
  position: 'absolute', left: 120, right: 120, bottom: 60,
  display: 'flex', justifyContent: 'space-between',
  fontSize: 24, color: '#94a3b8',
}}>
  <span>EDITORIAL NOIR · 2026</span>
  <span>{pageNum} / {total}</span>
</div>

// Hebrew Footer:
<div style={{
  position: 'absolute',
  insetInline: 120,        // was: left: 120, right: 120
  bottom: 60,
  display: 'flex',
  justifyContent: 'space-between',
  fontSize: 24, color: '#94a3b8',
}}>
  <span>סקילס-אי-אל · 2026</span>
  <span>{pageNum} / {total}</span>
</div>
```

`insetInline: 120` is shorthand for `insetInlineStart: 120; insetInlineEnd: 120`, pinning to both edges with logical-property naming. The brand and page-counter swap visual sides automatically when the surrounding `dir="rtl"` is on the page root.

If you want an explicit visual order (e.g. logo always on the visual left, page counter always on the visual right, regardless of `dir`), use `flexDirection: 'row-reverse'` inside an RTL container, or position absolutely with `insetInlineStart` / `insetInlineEnd` separately.

## 6.5. Hebrew technical-translation traps

Translation tools and well-meaning agents render English dev terminology into Hebrew that means something else. These are the most-frequent traps observed when adapting upstream LTR English content for Hebrew users. Always verify with a native speaker:

| English term | Wrong translation | What it actually means in Hebrew | Use instead |
| --- | --- | --- | --- |
| themes (visual) | ערכאות | court instances (legal) | **ערכות נושא** or **תמות** |
| resolution (of a reference) | רזולוציית | screen / image resolution | **פיענוח**, **זיהוי**, **פתרון** |
| authoring | אוטרינג | English transliteration; sounds techy and wrong | **כתיבה**, **יצירה**, **חיבור** |
| tuned scale | סקאלה מכוונת | literal but robotic | **סקאלה מותאמת** |
| upstream | אופסטרים / אוטופסטרים | English transliteration | **קוד מקור (של X)**, **המקור** |
| install | התקנה ✓ | correct, but imperative form is more native | **להתקנה** (heading) or **תתקינו** (CTA) |
| best practices | שיטות עבודה מומלצות ✓ | correct | same |
| design tokens | טוקני עיצוב ✓ | correct (transliteration acceptable in tech context) | same |

When unsure: ship the term in English (Latin script) instead of inventing a Hebrew transliteration. `DesignSystem`, `themes`, `bidi`, `RTL` all stay in English even in Hebrew prose, and look natural when wrapped in `<bdi>`.

### Tone in Israeli Hebrew

Israeli technical Hebrew is direct, slightly informal, and avoids the formal/passive register of government Hebrew. Common substitutions:

| Translated-sounding | Natural Israeli |
| --- | --- |
| ניתן להשתמש (one can use) | אפשר להשתמש / השתמשו |
| מומלץ לבצע (it is recommended to perform) | כדאי לעשות / עשו |
| יש לבדוק (it is necessary to check) | תבדקו / חשוב לבדוק |
| הסקיל מספק (the skill provides) | הסקיל נותן / יש בסקיל |
| בכדי (in order to) | כדי |
| במידה ו (in case that) | אם |
| במהלך (during), overused | תוך כדי / כש |

If a sentence reads like a legal document, rewrite it. Israeli devs expect warm, direct Hebrew, even in technical reference material.

## 7. Hebrew typography pitfalls

These are the small things that make a Hebrew deck look amateur if missed.

### Nikkud (vowel marks)

If your deck quotes biblical text, poetry, or children's content, you may have vowel marks attached to consonants:

```
שָׁלוֹם
```

Most Hebrew Google Fonts render nikkud, but quality varies. **Heebo, Frank Ruhl Libre, and Noto Sans Hebrew handle nikkud well.** Rubik and Assistant are weaker, the marks may collide with consonants at small sizes.

If you're using nikkud at body size (40px), test with a real sample. At hero size (160–220px) all listed fonts handle nikkud cleanly.

### Sofit letters

Hebrew has 5 letters with a different "final" form when at the end of a word: ם, ן, ץ, ף, ך. These render correctly in any modern font; **never** treat them as ASCII transliterations or substitute the regular form. Your text input from the user should already have the correct sofit forms.

### Maqaf vs hyphen-minus

The standard Unicode hyphen-minus (`-`, U+002D) is fine in Hebrew copy. The proper Hebrew typographic hyphen, **maqaf** (`־`, U+05BE), is rarely used in modern Hebrew web typography. Stick with `-` unless the deck is for a typography-conscious editorial audience.

### Apostrophe in transliterations

Words like "ChatGPT-ה" use a regular hyphen between the Latin word and the Hebrew prefix/suffix. Don't substitute curly quotes (`'` or `'`), they break in monospace fonts and look wrong at hero sizes.

### Numbers: keep Latin

Use `1, 2, 3` not `١, ٢, ٣` (Arabic-Indic digits, used in Arabic but not modern Hebrew). And not the Hebrew numeric letter system (`א, ב, ג`) unless the deck is explicitly traditional. Modern Hebrew uses Latin digits.

### Currency

Israeli Shekel: `₪1,500` (symbol-first) or `1,500 ש״ח` (suffix). Both work. The symbol `₪` (U+20AA) renders in all listed Google Fonts. Don't write `NIS 1,500` for a Hebrew audience, they'll read it but it feels foreign.

## 7.5. Brand-palette discipline (when the slide has a brand to follow)

Hebrew RTL adaptation often coincides with brand alignment, adapting an open-slide deck to a specific Israeli company's visual identity. A common LTR-template instinct is to gradient between primary brand colors for visual punch ("the hero number is a gradient from brand blue to brand magenta"). **This frequently produces an off-brand intermediate hue.**

Concrete example: agentskills.co.il publishes Israeli Blue (`#003286`) and YooTech Magenta (`#bc46a2`) as separate palette entries. A linear gradient `Israeli Blue → Magenta` blends through saturated purple, which is **not** in the published palette. The site uses each color solid; magenta as accent, Israeli Blue as the dominant brand mark.

**Rules of thumb when adapting to a brand:**

1. **Hold solid bold marks for primary brand colors.** A confident solid `#003286` "0%" beats a contrived gradient.
2. **Only gradient between adjacent hues.** `Israeli Blue → Israeli Blue Light` (same family, lower saturation) is safe. `Brand Blue → Brand Yellow` blends through green and almost certainly invents a non-brand color.
3. **Or fade to neutral.** A brand-blue → cream gradient is fine; a brand-blue → brand-magenta gradient usually isn't.
4. **Audit each combination by checking the midpoint.** Drop a color picker on the visual midpoint of the gradient and ask: is this color in the published palette?

When in doubt, write down the project's hex values, place them next to each other, and resist combining them. The site that issued the palette doesn't gradient-blend its own colors; your slide shouldn't either.

## 8. Themes for Hebrew decks

A `themes/<id>.md` file can be Hebrew-first. Author the markdown's prose sections in Hebrew, but **keep the code snippets logical-CSS-first** so they work for any direction:

```markdown
---
name: עורכי-עמוקים
description: זהות חזותית ל-pitch deck ישראלי, פלטה כהה, גופנים עבריים מודרניים
mode: dark
---

## פלטה
| תפקיד | ערך | הערות |
| --- | --- | --- |
| bg | `#0f172a` | רקע כהה |
| text | `#f8fafc` | טקסט ראשי |
| accent | `#fbbf24` | הדגשות, eyebrow, מספרים מרכזיים |
| muted | `#94a3b8` | טקסט משני, קווים מפרידים |

## טיפוגרפיה
- Display: Heebo, weight 800–900
- Body: Heebo, weight 400–500
- Hero: 200px (ב-Hebrew, מוגדל מהדיפולט של 180px)
- Body: 40px

## רכיבים קבועים
### Title (paste-ready, RTL-safe)
```tsx
const Title = ({ children }: { children: React.ReactNode }) => (
  <h1 style={{
    fontSize: 200, fontWeight: 900, lineHeight: 1.1,
    margin: 0, color: 'var(--osd-text)',
    fontFamily: 'Heebo, system-ui, sans-serif',
  }}>
    {children}
  </h1>
);
```
```

The Footer's `position: 'absolute'` should use `insetInline: 120` (logical), not `left: 120; right: 120` (physical). The visible result is identical for symmetric edges, but logical naming documents intent.

## 9. Self-review for Hebrew slides

Add these to the upstream "Self-review before finishing" checklist:

- [ ] Page root carries `dir="rtl"` (every page that renders Hebrew).
- [ ] No physical-axis CSS inside the page root: `paddingLeft`, `paddingRight`, `marginLeft`, `marginRight`, `left`, `right`, `borderLeft`, `borderRight`, `text-align: 'left'`, `text-align: 'right'` are absent (or only used in symmetric-equivalent shorthand like `padding: '120px 160px'` where the H/V split is unambiguous).
- [ ] Hebrew fonts loaded via `@import` or project-level `<link>`. `DesignSystem.fonts.display` and `fonts.body` start with the Hebrew family.
- [ ] Type scale bumped 10–15% at hero/section sizes vs the upstream defaults.
- [ ] Vertical budget recomputed at the bumped sizes; every page sums under 1080px.
- [ ] Hero on covers/section dividers fits 1–2 lines (3 lines at the bumped Hebrew scale almost always overflows).
- [ ] Latin runs inside Hebrew copy wrapped in `<bdi>` (brand names, code, URLs, version numbers, file extensions). **Audit your own prose recursively**, a skill author writing about `<bdi>` will miss it in their own examples.
- [ ] Embedded code blocks: `<pre dir="ltr">` with `textAlign: 'start'`. Verified the code reads LTR while the surrounding slide stays RTL.
- [ ] No mis-translated technical terms (themes ≠ ערכאות; resolution ≠ רזולוציית; authoring ≠ אוטרינג).
- [ ] Hebrew tone is direct/Israeli, not government-formal (avoid `ניתן ל...` / `יש לבדוק` / `במידה ו` patterns).
- [ ] No nikkud quality issues at the chosen font + size (test with a real sample if you used nikkud).
- [ ] Numbers are Latin digits (`1, 2, 3`), currency uses `₪` or `ש״ח`.
- [ ] Footer / page-counter / breadcrumb chrome flips correctly in `dir="rtl"` (use `insetInline` shorthand, `flexDirection: 'row'` with `justifyContent: 'space-between'` flips automatically, don't double-flip with `row-reverse`).
- [ ] If the deck follows a brand palette: no invented gradients between non-adjacent brand colors (e.g., Israeli Blue → Magenta blends through purple, which is off-brand).

## 10. Bilingual decks (some pages Hebrew, some English)

For decks that mix Hebrew and English pages:

- Set `dir="rtl"` per page (Hebrew pages) or omit it (English pages, default ltr from `<html>`).
- Define the Hebrew font family in `DesignSystem.fonts` even for English pages, Hebrew fonts in this list (Heebo, Rubik, Noto Sans Hebrew) all render Latin glyphs cleanly, so a single shared `font-family` works for both directions. The English page renders Latin glyphs from the same Hebrew family; visual coherence stays intact.
- Title and section-heading sizes can stay at the bumped Hebrew values for English pages too (English at 200px hero is fine, generous, not cramped). Or use two different `typeScale` values per page if you want tight English vs roomy Hebrew. Latter requires per-page DesignSystem overrides; not currently supported by the Design panel cleanly. Pragmatic answer: pick one bumped value, apply to both.
- Keep navigation chrome (page numbers, footer brand) consistent across pages, switching between LTR and RTL chrome page-to-page is jarring. Either always-LTR or always-RTL, regardless of content direction. Pick one.

Cover example:

```tsx
// Cover page in Hebrew
const HebrewCover: Page = () => (
  <div dir="rtl" style={{ width: '100%', height: '100%', paddingInline: 160, /* ... */ }}>
    <h1 style={{ fontSize: 200, fontFamily: 'Heebo, sans-serif' }}>
      הרעיון הגדול
    </h1>
  </div>
);

// Detail page in English
const EnglishDetail: Page = () => (
  <div style={{ width: '100%', height: '100%', paddingInline: 160, /* ... */ }}>
    <h2 style={{ fontSize: 132, fontFamily: 'Heebo, sans-serif' }}>
      Section heading
    </h2>
  </div>
);

export default [HebrewCover, EnglishDetail] satisfies Page[];
```

The `dir="rtl"` is missing on the second component, so it inherits `ltr` from `<html>`, correct for English. Both share the Hebrew font family for consistency.
