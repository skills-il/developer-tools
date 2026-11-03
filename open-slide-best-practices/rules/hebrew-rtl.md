# hebrew-rtl: Hebrew and RTL adaptation for open-slide

This file is the central Hebrew/RTL reference for open-slide. The upstream framework has zero Hebrew or RTL coverage in its own skill files; this file fills that gap. Read it before authoring any Hebrew or bilingual deck.

## TL;DR

For a Hebrew or bilingual `slides/<id>/index.tsx`:

1. Set `dir="rtl"` on the **page component's root `<div>`** only (never on `<html>`, that breaks the dev server chrome).
2. Use **logical CSS** everywhere: `paddingInline`, `paddingInlineStart`, `marginInlineStart`, `insetInlineStart`, `text-align: 'start'`. Never physical (`paddingLeft`, `marginLeft`, `left`, `text-align: 'left'`) inside the page root.
3. Load **Hebrew Google Fonts** (Heebo, Rubik, Assistant, Noto Sans Hebrew, Frank Ruhl Libre, Suez One) by injecting the stylesheet **once into `<head>` from module top level**, with an element id keyed to the slide. Never from inside the page component. List the family first in `DesignSystem.fonts.display` / `fonts.body`, with the system stack as fallback.
4. **Re-check every size for Hebrew instead of reusing the English one.** Hebrew and English copy do not set to the same width at the same px size, so preview each page. This skill's +10-15% hero bump (section 4) is an editorial starting point, not a framework rule or a measured constant.
5. Isolate any Latin or signed-number run inside Hebrew copy to prevent bidi glitches. In core 2.x prefer `<span dir="ltr">` (keeps the line inline-editable); `<bdi>` isolates just as well but turns off inline editing for that line. Example: `השתמשו ב-<span dir="ltr">React Router</span>`.
6. The 1080px **vertical budget rule still applies**, but recompute it for Hebrew at whatever heading sizes you settled on in step 4.
7. **Export as PDF or image PPTX, never the editable "Export as PPTX"**, which shreds wrapped Hebrew into one character per line (verified on core 2.3.1). See section 3.

And one rule that is not about styling at all: **name the slide folder in ASCII.** `slides/<id>` ids must match `/^[a-z0-9_-]+$/i`. A Hebrew folder name is silently skipped at discovery, the slide never appears in the browser or the build, and the build still exits 0. Hebrew belongs in `meta.title` and in the page content, not in the folder name.

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

**The browser editing panels do not follow this rule.** In core 2.x the Format panel and the inline-text toolbar write physical `textAlign: 'right'` / `'center'` / `'justify'` into source, and their "left" button removes the property instead (on an RTL page that leaves the text right-aligned). They also report anything other than center/right/justify, including `start` and `end`, as "left". If a user aligned text from a panel, expect physical values in source and decide whether to convert them.

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

The runtime default `DesignSystem.fonts.display` is `Georgia, "Times New Roman", serif` (no Hebrew glyphs, so the OS substitutes a system Hebrew serif) and `fonts.body` is a system sans stack. For decks that ship beyond a dev machine, use a Hebrew Google Font for both.

### Recommended families (Hebrew subset)

| Family                | Style              | Weights commonly available | Use for                          |
| --------------------- | ------------------ | -------------------------- | -------------------------------- |
| **Heebo**             | Geometric sans     | 100-900                    | General workhorse, body + display |
| **Rubik**             | Friendly geometric | 300-900                    | Decks with playful or warm tone   |
| **Assistant**         | Humanist sans      | 200-800                    | Body copy where Heebo feels cold  |
| **Noto Sans Hebrew**  | Neutral sans       | 100-900                    | Maximum compatibility, multilingual decks |
| **Frank Ruhl Libre**  | Serif (editorial)  | 300-900                    | Editorial/Q-deck headings; classy |
| **Suez One**          | Slab display       | 400 only                   | Hero-only, single weight          |

Avoid: David Libre (system-y, looks dated at large sizes), VarelaRound (cute but the round terminals fight large hero sizes).

### Loading them

Upstream documents exactly one supported mechanism, in `slide-authoring/references/webfonts.md`, and it is a hard rule:

> **Load the stylesheet once, in `<head>` (never inside a per-page component).**

The reason is specific to this framework: every page of a slide is mounted live at the same time (the thumbnail rail, the overview grid, and the PDF print root all render them together), so a `<style>@import ...</style>` or a `<link>` returned from a `Page` component registers the whole `@font-face` set once *per page*. Upstream also requires the injected element's id to be **keyed to the slide**, because the home page mounts pages from every slide at once, so a shared id like `osd-webfont` would let the first slide's fonts suppress every other slide's.

**Option A (recommended): idempotent head injection at module top level of `slides/<id>/index.tsx`.**

```tsx
const FONT_HREF =
  'https://fonts.googleapis.com/css2?family=Heebo:wght@400;700;900&display=swap';
const FONT_LINK_ID = 'osd-webfont-hebrew-cover'; // suffix = this slide's folder id

if (typeof document !== 'undefined') {
  let link = document.getElementById(FONT_LINK_ID) as HTMLLinkElement | null;
  if (!link) {
    link = document.createElement('link');
    link.id = FONT_LINK_ID;
    link.rel = 'stylesheet';
    document.head.appendChild(link);
  }
  if (link.href !== FONT_HREF) link.href = FONT_HREF;
}

const Cover: Page = () => (
  <div dir="rtl" style={{ /* ... */ fontFamily: 'Heebo, system-ui, sans-serif' }}>
    ...
  </div>
);
```

Top-level statements, not inside a component and not inside an effect. The `typeof document !== 'undefined'` guard keeps it safe during the static build.

**Create-or-update, never create-if-missing.** HMR re-runs the module but leaves the previous `<link>` in the document, so an `if (!document.getElementById(id))` guard skips the new URL and a font change does not show until a full reload. Upstream's webfonts reference switched to this shape in 2.x; the same pattern applies to any `<style>` you inject for `@keyframes`.

**List only the weights you actually use.** Each extra weight multiplies the number of `@font-face` rules.

**Do not add `&subset=hebrew` to a `css2` URL.** It is a v1-API parameter and the `css2` endpoint ignores it: the response is byte-identical with and without it. You do not need it anyway, because `css2` already splits the family into `unicode-range`-scoped `@font-face` blocks, one of which is Hebrew (`U+0307-0308, U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F`), and the browser downloads only the ranges the page actually uses. The real subsetting lever is `&text=<unique chars>`, which works well for Hebrew when a hero uses only a handful of characters. Only subset once the copy is frozen: in 2.x the text is edited live (inline editing, the agent panel), and any letter outside the subset silently renders in the fallback face.

**The old `<style>@import</style>`-inside-the-page pattern is no longer correct.** Earlier versions of this skill recommended it; it still renders, but it re-registers the font set per mounted page and upstream now explicitly forbids it.

**Option B: Reference in `DesignSystem.fonts` (so the Design panel can tweak it):**

```tsx
export const design: DesignSystem = {
  palette: { bg: '#0f172a', text: '#f8fafc', accent: '#fbbf24' },
  fonts: {
    display: 'Heebo, system-ui, -apple-system, sans-serif',
    body: 'Heebo, system-ui, -apple-system, sans-serif',
  },
  typeScale: { hero: 200, body: 40 },   // example values above the runtime default 168/36; settle them by previewing
  radius: 12,
};
```

Pair this with the head injection from Option A, since `DesignSystem.fonts` only declares the CSS `font-family` value, it does NOT load the font file. (The Design panel reads `DesignSystem.fonts` to render its preview; it does not own font loading.)

**There is no project `index.html` to put a `<link>` in.** A scaffolded project ships no `index.html` (the HTML shell lives inside `@open-slide/core`), so head injection from the slide module is the only route. Earlier versions of this skill described a project-level `index.html` option; it never applied to a scaffolded project.

**Do not self-host a Hebrew font through the Assets panel's Google Fonts search.** Its download (core 2.x) fetches one TTF from the legacy `fonts.googleapis.com/css` endpoint without a subset parameter, and for Heebo that file has no Hebrew letters at all (0 of 27, measured with fontTools), while the search preview, which loads `css2`, shows Hebrew correctly. If you need an offline font file, fetch it with `&subset=hebrew` on that legacy endpoint (measured: all 27 letters) or from a package such as Fontsource, and check its Hebrew coverage before relying on it.

**The Design panel's Shuffle overwrites Hebrew fonts.** Shuffle replaces the whole `design` const with a random preset, and every preset font stack is Latin-only (Georgia, Times, Helvetica, Inter, SF Mono). Saving writes it back to source, silently dropping Heebo from `fonts.display` and your Hebrew type scale. After a user shuffles, restore the Hebrew `fonts` and `typeScale`.

### Exporting a Hebrew deck (PDF, PPTX, HTML)

Core 2.x has four exports, and they behave very differently for Hebrew. Verified on 2.3.1 by exporting a Hebrew test deck and reading the produced files:

- **Export as PPTX (editable): do not use for Hebrew.** It rebuilds each page as native PowerPoint text boxes from the browser's measured line boxes. Its line grouper assumes text advances left to right, so a Hebrew text node that wraps, or that sits next to a Latin run, is split into one run per character with a line break after each: a 4-line Hebrew paragraph came out with 99 line breaks, while the same English paragraph came out with 3. Paragraphs carry no `rtl="1"`, and `text-align: start` / default alignment maps to left.
- **Export as image PPTX: safe.** Each page is rasterised with `html-to-image` into one PNG per slide. Text is not editable. Speaker notes are copied into the PowerPoint notes pane as raw text, `lang="en-US"` with no `rtl`, Markdown markers included.
- **Export as PDF: safe, and the best board deliverable.** The print frame is white with black text: CSS gradient layers are removed from every element, so a page whose background is only a gradient prints white and light text on it can vanish. Give any gradient page a solid color underneath, in React `style={{ backgroundColor: '#0f172a', backgroundImage: 'linear-gradient(...)' }}` (the color survives the strip), and check the PDF. It mounts every page into a print root and calls the browser's print, so text stays vector and selectable. Not supported in Safari (the app shows an error); use Chrome or Edge. `box-shadow` is stripped too, and a gradient-filled heading (`background-clip: text`) loses its fill. No notes.
- **Export as HTML.** A static snapshot that keeps `dir` and the page markup, but cross-origin stylesheets such as the Google Fonts `<link>` stay external URLs, so the file needs internet to show the Hebrew webfont. No notes.

The PDF and both PPTX pipelines already wait for `document.fonts.ready` (and `data-waitfor` targets) before capturing, so you no longer need to "let the font settle" by hand. What still bites is a font that never loads, or a self-hosted file without Hebrew glyphs.

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

Hebrew and Latin do not set to the same width at the same `font-size`, and a translated line is usually a different number of characters, so an English layout's sizes are not a reliable guide. Effects to watch for:

- A hero title that fits on one line in English may wrap to two in Heebo at the same size, or may fit with room to spare.
- Bullets sized against English copy can wrap in Hebrew.
- Padding-inline still works fine; what changes is how much **content** fits in the line.

There is no fixed conversion factor. Preview the actual page (preview route, section 9) and adjust.

### Recommended adjustments

Editorial starting points (skills-il calibration, not measured constants). Use them only when a preview shows the Hebrew hero reading small or wrapping badly:

| Element          | Upstream (Latin) | Hebrew suggestion |
| ---------------- | ---------------- | ----------------- |
| Hero title       | 140-200px        | 160-220px (+10-15%) |
| Section heading  | 80-120px         | 88-132px (+10%)     |
| Page heading     | 56-80px          | 60-88px (+8%)       |
| Body text        | 32-44px          | 32-44px (unchanged) |
| Caption / label  | 22-28px          | 22-28px (unchanged) |

Body and caption sizes are left unchanged as an editorial choice: long lines absorb small differences, while at hero and section sizes line-wrapping is binary (1 line vs 2), so that is where a preview most often calls for an adjustment.

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

Bumping a heading always eats budget: in the 840px worked example from `slide-authoring.md`, an 80px heading at line-height 1.2 costs 96px and an 88px heading costs 105.6px (total 825.6px, still under). A bigger bump, or a heading that now wraps to two lines, can push the page over. **Always recompute the budget after bumping the scale.**

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
  <span dir="ltr" style={{ color: PALETTE.brand }}>open-slide</span>
  <br />
  בעברית.
</h1>
```

2 lines × 240 × 0.95 = 456px. Same visual punch, fits the canvas. **A 3-line Hebrew hero almost always overflows. Default to 1-2 lines on covers and section dividers.**

### Line-height for Hebrew

Starting points for Hebrew line-height (editorial, adjust after previewing; the worked examples above use a tighter 0.95-0.98 for multi-line heroes, which is fine when every line is short):

- Hero (160-220px): `lineHeight: 1.1` (upstream default 1.05, a touch too tight)
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
- Plain unsigned integers and decimals in Hebrew copy (`1,500`, `1.5 מיליון`). **Signed** numbers are the exception, see the rule directly below. Currency signs, percents and units are covered by the scope note below, which makes no claim either way: preview them.
- Logos as `<img>` (they're not text, no bidi to worry about)

CSS caution: a bare `unicode-bidi: isolate` on a `<span>` is NOT equivalent. `<bdi>` is isolation plus automatic direction; a bare isolate keeps the inherited RTL direction, and measured in Chromium it still renders `-5` as `5-`. Use `<span dir="ltr">` (isolation plus an explicit LTR direction) or `<bdi>`.

**`<bdi>` costs you inline editing in core 2.x, so prefer `<span dir="ltr">`.** Double-click text editing only treats an element as one editable text run when every child is text, `<br>`, or one of `b code del em i ins mark s small span strong sub sup u`. `bdi` is not on that list, so a sentence containing a `<bdi>` cannot be edited in place. `<span dir="ltr">` gets the same result: the HTML rendering rules give any element with a `dir` attribute `unicode-bidi: isolate`, and the attribute also sets the run's direction to LTR. Measured in Chromium inside `dir="rtl"`: `<span dir="ltr">-5</span>` and `<bdi>-5</bdi>` both keep `-5`. Everything below that says "wrap in `<bdi>`" accepts `<span dir="ltr">` as well, and `span` is the better default for a deck the user will keep editing in the browser.

```tsx
<p>השתמשו בספריית <span dir="ltr">React Router</span> לניתוב.</p>
```

### Signed numbers reorder in Hebrew text

A **sign attached to a number** (`-5`, `5+`, a negative delta on a stats slide) does not stay where you
put it. Measured in Chromium with `dir="rtl"`, the sign moves to the opposite side of the digits:

| Source | Renders as |
| --- | --- |
| `ירידה של -5 נקודות` | the minus lands after the digit (`5-`) |
| `טווח 5+ שנים` | the plus lands before the digit (`+5`) |

**Why:** a separator only fuses into a number when it sits *between two digits* (UAX#9 W4). A leading
`-` or a trailing `+` has no digit on its other side, so it stays a neutral, resolves to the
surrounding RTL direction, and jumps to the far side of the number.

**Fix:** wrap the signed number in `<bdi>`.

```jsx
// ❌ the minus ends up on the wrong side
<p>ירידה של -5 נקודות ברבעון</p>

// ✅
<p>ירידה של <bdi>-5</bdi> נקודות ברבעון</p>
```

This is the most commonly missed case on a Hebrew stats slide, because a negative KPI looks like a
single number and nothing errors.

> **Scope note, read before extending this section.** Only the signed-number case above is asserted
> here, because it is the only one that reproduced identically under every method tried (`fribidi`,
> and two independent Chromium geometry measurements). Ranges (`2020 - 2024`, `2020-2024`), time
> ranges, slashes, spaced and unspaced percent signs, and `₪` on either side of a figure gave
> **inconsistent** results across those methods, so this skill deliberately makes no claim about
> them. If you need to settle one, measure it in a real browser by comparing the client-rect
> geometry of the two tokens, and be aware that reading `fribidi`'s visual output by eye is not a
> reliable substitute: it reports display order, not reading order, and it is easy to mistake one
> for the other in both directions.

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
  <span>{current} / {total}</span>
</div>

// Hebrew Footer (const { current, total } = useSlidePageNumber()):
<div style={{
  position: 'absolute',
  insetInline: 120,        // was: left: 120, right: 120
  bottom: 60,
  display: 'flex',
  justifyContent: 'space-between',
  fontSize: 24, color: '#94a3b8',
}}>
  <span>סקילס-אי-אל · 2026</span>
  <span dir="ltr">{current} / {total}</span>   {/* ONE isolate around the whole run */}
</div>
```

**Isolate the whole counter, not each number.** Measured in Chromium inside `dir="rtl"`: a bare `3 / 12` renders as `12 / 3`, and wrapping each number separately (`<bdi>3</bdi> / <bdi>12</bdi>`) still renders `12 / 3`. One `<span dir="ltr">` (or one `<bdi>`) around `current / total` renders `3 / 12`. Read the numbers from `useSlidePageNumber()`, never hardcode them.

`insetInline: 120` is shorthand for `insetInlineStart: 120; insetInlineEnd: 120`, pinning to both edges with logical-property naming. The brand and page-counter swap visual sides automatically when the surrounding `dir="rtl"` is on the page root.

If you want an explicit visual order (e.g. logo always on the visual left, page counter always on the visual right, regardless of `dir`), use `flexDirection: 'row-reverse'` inside an RTL container, or position absolutely with `insetInlineStart` / `insetInlineEnd` separately.

### Timelines, roadmaps and charts

A flex row inside `dir="rtl"` runs right to left, so a quarter-by-quarter roadmap built as a row puts Q1 on the right. That may be what you want, but decide it explicitly and tell the user which way time runs. To keep a time axis left to right on a Hebrew page, set `dir="ltr"` on the row container only and keep `dir="rtl"` on the Hebrew labels inside each cell. Wrap Latin quarter and year labels (`Q3 2026`) in `<span dir="ltr">`. This skill makes no claim about how a date range such as `2026-2027` or `יולי-ספטמבר` orders (see the scope note in section 5): check every timeline page in the preview route before shipping.

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

Mark placement varies between fonts and sizes. If a slide uses nikkud, test a real sample in the font and size you chose (preview route) before shipping, especially at body size.

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
- Display: Heebo, weight 800-900
- Body: Heebo, weight 400-500
- Hero: 200px (בעברית, מוגדל מברירת המחדל של הרנטיים, 168px)
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
- [ ] Hebrew fonts loaded by **module-level, slide-keyed head injection** (the mechanism section 3 requires), NOT by a `<style>@import</style>` or a `<link>` returned from a `Page` component, which re-registers the whole `@font-face` set once per mounted page. `DesignSystem.fonts.display` and `fonts.body` start with the Hebrew family.
- [ ] Hero/section size chosen **deliberately** after previewing, and the vertical budget recomputed at that value. The +10-15% bump in section 4 is an optional editorial starting point, not a framework rule; bumping reflexively can cause the very wrapping it is meant to prevent.
- [ ] Vertical budget recomputed at the bumped sizes; every page sums under 1080px.
- [ ] Hero on covers/section dividers fits 1-2 lines (3 lines at the bumped Hebrew scale almost always overflows).
- [ ] Latin runs inside Hebrew copy isolated with `<span dir="ltr">` (preferred in 2.x, stays inline-editable) or `<bdi>` (brand names, code, URLs, version numbers, file extensions). **Audit your own prose recursively**, a skill author writing about `<bdi>` will miss it in their own examples.
- [ ] Embedded code blocks: `<pre dir="ltr">` with `textAlign: 'start'`. Verified the code reads LTR while the surrounding slide stays RTL.
- [ ] No mis-translated technical terms (themes ≠ ערכאות; resolution ≠ רזולוציית; authoring ≠ אוטרינג).
- [ ] Hebrew tone is direct/Israeli, not government-formal (avoid `ניתן ל...` / `יש לבדוק` / `במידה ו` patterns).
- [ ] No nikkud quality issues at the chosen font + size (test with a real sample if you used nikkud).
- [ ] Numbers are Latin digits (`1, 2, 3`), currency uses `₪` or `ש״ח`.
- [ ] **Signed numbers audited.** A leading `-` or trailing `+` on a number reorders inside Hebrew text (`-5` renders as `5-`). Grep the page for a `-` or `+` immediately before or after a digit and wrap each in `<span dir="ltr">` or `<bdi>`. Negative KPIs are the usual miss.
- [ ] Footer / page-counter / breadcrumb chrome flips correctly in `dir="rtl"` (use `insetInline` shorthand, `flexDirection: 'row'` with `justifyContent: 'space-between'` flips automatically, don't double-flip with `row-reverse`).
- [ ] If the deck follows a brand palette: no invented gradients between non-adjacent brand colors (e.g., Israeli Blue → Magenta blends through purple, which is off-brand).
- [ ] If the dev server is running, every Hebrew page was screenshotted at 1920×1080 through `/s/<id>/preview?p=N` and looked at.
- [ ] Page counter: ONE `<span dir="ltr">` around the whole `current / total` run, numbers from `useSlidePageNumber()`.
- [ ] Any gradient page background has a solid `backgroundColor` under it, so the PDF does not print it white.
- [ ] Export plan: PDF from Chrome or Edge, or image PPTX when notes must travel with the file. Never the editable "Export as PPTX" for Hebrew.

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
