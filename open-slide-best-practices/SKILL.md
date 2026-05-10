---
name: open-slide-best-practices
description: "Best practices for authoring presentations with open-slide, the React slide framework with a fixed 1920×1080 canvas, with full Hebrew and RTL support. Covers the slides/[id]/index.tsx file contract, type scale, DesignSystem tokens, themes/ system, @slide-comment inspector markers, current.json deictic resolution, Hebrew Google Fonts (Heebo, Rubik, Assistant, Noto Sans Hebrew), CSS logical properties, bidirectional Hebrew+English text with the bdi element, and Hebrew-aware type scale tuning. Use when authoring or editing slides under slides/[id]/ in an open-slide project, or when building Hebrew or bilingual decks on the framework. Do NOT use for video creation (use remotion-best-practices or hyperframes-best-practices), or for generic Hebrew presentations outside open-slide (use presentation-generator)."
license: MIT
---

# open-slide Best Practices for Israeli Developers

> Adapted from [1weiho/open-slide](https://github.com/1weiho/open-slide) (MIT). Hebrew and RTL adaptations by [skills-il](https://agentskills.co.il).

## Problem

open-slide ships an opinionated authoring system: a fixed 1920×1080 React canvas, a typed `DesignSystem` const, a themes folder, an inspector that drops `@slide-comment` markers in source, and five built-in skills (`slide-authoring`, `create-slide`, `create-theme`, `apply-comments`, `current-slide`). None of those touch Hebrew or RTL. Out of the box, a deck written by a coding agent comes out left-aligned, system-font only, with `paddingLeft` that fights the Hebrew reading order, and no guidance for mixed Hebrew+English text. Israeli developers waste hours retrofitting RTL, loading Hebrew Google Fonts, and discovering that the type scale (140–200px hero) which works in Inter looks cramped in Heebo at the same weight.

## Instructions

### When to use

Use this skill whenever you are writing or editing code under `slides/<id>/` in an open-slide project, creating a theme under `themes/`, or processing inspector comments — especially when any of that content is in Hebrew or bilingual.

### New project setup

When in an empty folder or workspace with no existing open-slide project, scaffold one using:

```bash
npx @open-slide/cli init my-slide
cd my-slide
pnpm dev
```

Replace `my-slide` with a suitable project name. The scaffolder ships with the upstream agent skills preconfigured; this skill provides Hebrew and RTL adaptations on top.

### Hebrew and RTL

For any Hebrew or bilingual deck, load [./rules/hebrew-rtl.md](./rules/hebrew-rtl.md) first. It covers:

- Hebrew Google Fonts (Heebo, Rubik, Assistant, Noto Sans Hebrew) with `subset=hebrew`
- The `<html dir="rtl">` set-up vs per-page `dir` attribute (the canvas root is the page component, not the document)
- CSS logical properties (`paddingInlineStart`, `marginInlineStart`, `insetInlineStart`) instead of `paddingLeft`/`marginLeft`/`left`
- `flexDirection: 'row-reverse'` vs setting `dir` on the flex container
- Bidirectional text with `<bdi>` for mixed Hebrew + Latin (brand names, code, URLs)
- Hebrew-aware type scale tuning (Hebrew renders ~10–15% wider per character at the same px size)
- Hebrew `DesignSystem.fonts.display` and `fonts.body` choices that work at hero size
- RTL-aware theme markdown patterns under `themes/`
- Hebrew typography pitfalls: nikkud rendering, sofit letter spacing, hyphen vs maqaf

### Slide authoring (file contract, canvas, type scale, themes, design tokens)

For the technical reference on what goes inside `slides/<id>/index.tsx`, load [./rules/slide-authoring.md](./rules/slide-authoring.md). This is the same content the upstream `slide-authoring` skill exposes, with Hebrew/RTL pointers inline. It covers the file contract, the 1920×1080 canvas math, the type scale, spacing, visual direction, themes, the `DesignSystem` design-tokens object, the starter template, assets, image placeholders, and the repeated-elements rule.

### Drafting a new deck

When the user asks for "make slides about X" / "create a presentation" / "draft a deck", load [./rules/create-slide.md](./rules/create-slide.md) for the workflow: theme picker, the four scoping questions (aesthetic direction, page count, text density, motion), slide id selection, structure planning, visual commitment, write, self-review, hand off.

### Creating a theme

When the user asks to "create a theme" / "make a theme called X" / "extract a theme from this slide", load [./rules/create-theme.md](./rules/create-theme.md). Themes live as one markdown file under `themes/<id>.md` with Palette / Typography / Layout / Fixed components / Motion / Aesthetic sections.

### Applying inspector comments

When the user has clicked on a rendered page in the dev server and added comments (via the in-browser inspector tool), and asks to "apply comments" / "process slide comments", load [./rules/apply-comments.md](./rules/apply-comments.md). It covers the `{/* @slide-comment */}` marker format, the detection regex, the base64url-decoded payload, and the apply-in-reverse-line-order procedure.

### Resolving deictic references ("this page", "the slide I'm on")

When the user references the current slide without naming it, load [./rules/current-slide.md](./rules/current-slide.md) **first**. It explains how to read the live cursor at `node_modules/.open-slide/current.json`, what fields are in it, and the staleness rules. **Re-read it on every deictic turn** — the user navigates between turns, so a value you read earlier is almost certainly stale.

### Vertical budget reminder (the #1 source of broken slides)

Anything below 1080px on the canvas is silently cropped. Before writing any page, sum:

```
(font_size × line_height × number_of_lines) + gaps + (2 × padding) ≤ 1080
```

If you're tight, **split into two pages**. Never use `overflow: auto/scroll/hidden`, negative margins, or transforms to hide overflow. The canvas does not scroll; cropped content is gone. See [./rules/slide-authoring.md](./rules/slide-authoring.md) section "Vertical budget" for the full worked example.

For Hebrew text the budget is tighter than it looks: Hebrew renders ~10–15% wider per character than Latin at the same px size, so a heading that fits English on one line at 80px may wrap to two in Heebo. Either drop the size or shorten the copy. See `hebrew-rtl.md` for the calibration table.

## Reference Links

| Source | URL | What to Check |
| --- | --- | --- |
| open-slide upstream repo | https://github.com/1weiho/open-slide | Latest API, breaking changes, version |
| open-slide docs / homepage | https://open-slide.dev | Install, demos |
| @open-slide/cli on npm | https://www.npmjs.com/package/@open-slide/cli | Current CLI version |
| @open-slide/core on npm | https://www.npmjs.com/package/@open-slide/core | Current runtime version, exports |
| MDN: CSS logical properties | https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values | RTL-aware CSS, `inset-inline-start`, `padding-inline` |
| MDN: `<bdi>` element | https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdi | Bidi isolation for mixed Hebrew+Latin |
| Google Fonts (Hebrew subset) | https://fonts.google.com/?subset=hebrew | Hebrew web fonts: Heebo, Rubik, Assistant, Noto Sans Hebrew |

## Recommended MCP Servers

None directly, since open-slide has no API surface. The skill is purely client-side authoring guidance.

## Gotchas

These are the failure modes a coding agent hits when authoring an open-slide deck in Hebrew without this skill. They are NOT user errors.

1. **Using `paddingLeft` and `marginLeft` everywhere.** In LTR these read as "from the start of the line". In RTL they're literally on the wrong side of the canvas. Use `paddingInlineStart` / `paddingInlineEnd` (or shorthand `paddingInline`) so the layout flips automatically when `dir="rtl"` is set on the canvas root. The same applies to `left` / `right` (use `insetInlineStart` / `insetInlineEnd`) and `text-align: left/right` (use `text-align: start/end`).

2. **Setting `direction: 'rtl'` on `<html>` or globally.** open-slide's canvas root is the page component, not the HTML document. The dev server chrome (file rail, navigation arrows) is upstream UI in English; flipping the document direction breaks it. Set `dir="rtl"` on the page component's root `<div>` only. The Inspector and presenter mode keep their LTR layout; only your slide content flips.

3. **System font stack only.** The upstream starter uses `system-ui, -apple-system, sans-serif` for both `display` and `body`. On macOS that resolves to Helvetica / SF Pro for Hebrew, which is acceptable but not display-quality at 140–200px hero. For decks that ship beyond a dev machine, load Heebo or Rubik via Google Fonts (`?subset=hebrew`) and put them first in the stack with the system stack as fallback. See `hebrew-rtl.md`.

4. **Same type scale as English.** 140–200px hero in Inter looks tight at the lower bound (140) for Hebrew, because Hebrew uppercase-equivalent (Hebrew has no case) sits at the cap-height-equivalent of large-x-height Latin fonts. Hebrew at 140px reads like Latin at 120px. Either bump the hero to 160–220px for Hebrew, or drop the line count.

5. **Mixing Hebrew and English without `<bdi>`.** A bullet like "השתמשו ב-React Router" with mixed Hebrew + Latin tokens often renders the punctuation in the wrong place because the browser's bidi algorithm doesn't always isolate the Latin span. Wrap mixed runs in `<bdi>`: `השתמשו ב-<bdi>React Router</bdi>`. Critical for code identifiers, brand names, and URLs inside Hebrew copy.

6. **`array.map` for visually repeated cards.** The upstream rule (one component instantiated per item, NOT `map` over a data array) applies in Hebrew too. The reason is the inspector: `map` shares one source location per item, so editing one Hebrew label changes all rendered cards. Define `<Card />` once, instantiate it three times explicitly. See `slide-authoring.md`.

7. **Ignoring `node_modules/.open-slide/current.json`.** When the user says "תקן את הכותרת בעמוד הזה" ("fix the heading on this page"), the deictic "הזה" maps exactly the same way the English "this" does — you must read `current.json` to find which slide they're on. Re-read it on every turn. See `current-slide.md`.

8. **Same vertical budget at the bumped Hebrew type scale.** A cover that fits a 3-line LTR hero at 200px (3 × 200 × 0.95 = 570px) will overflow if you keep 3 lines AND bump to 232px for Hebrew (3 × 232 × 0.95 = 661px) — once padding and subtitle are added you blow past 1080. Either stay at 1–2 lines for the Hebrew hero, or recompute the full budget with the bumped values before committing. Splitting is always the right answer.

9. **Mis-translated technical terms inside the slide copy.** Translation services and well-meaning agents render English dev terminology into Hebrew that means something else. Common traps:
   - **"themes" → "ערכאות"** (literally "court instances" — a legal term). Correct: **"ערכות נושא"** (theme sets) or **"תמות"** (transliteration).
   - **"resolution" (as in "resolving a reference") → "רזולוציית"** (means screen/image resolution). Correct: **"פיענוח"** (decoding) or **"זיהוי"** (identification).
   - **"authoring" → "אוטרינג"** (English transliteration, sounds techy and wrong). Correct: **"כתיבה"** or **"יצירה"**.
   - **"tuned scale" → "סקאלה מכוונת"** (literal but robotic). Better: **"סקאלה מותאמת"** (adapted scale).
   Always verify Hebrew technical terms with a native speaker or a Hebrew dev community reference before shipping.

10. **Pairing brand colors as a gradient can produce an off-brand intermediate hue.** A linear gradient from Israeli Blue (`#003286`) to YooTech Magenta (`#bc46a2`) blends through saturated purple — which is NOT in the agentskills.co.il palette. If a project has a brand palette, audit each combination: hold solid bold marks for primary brand colors, and only gradient between adjacent hues (e.g., Israeli Blue → Israeli Blue Light) or fade to neutral (cream / navy). One confident solid usually beats a contrived gradient.

11. **Audit your own copy for bidi traps. Recursively.** A skill that warns about missing `<bdi>` will frequently MISS its own `<bdi>` calls inside Hebrew sentences ("השתמשו ב-RTL" needs `<bdi>RTL</bdi>`). When writing prose, slides, or examples, manually scan every Latin token embedded in Hebrew runs and wrap it. Code identifiers, brand names, version numbers, file extensions — all need isolation. The author writing the rule is not exempt from the rule.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Hebrew text renders left-aligned | Page root is missing `dir="rtl"` | Add `dir="rtl"` to the page's outer `<div>`, or set `direction: 'rtl'` in its inline style |
| Hebrew renders in a serif when you wanted sans | Browser fell back to a system Hebrew face (David, Times) | Load Heebo/Rubik/Assistant via Google Fonts and put them first in `fonts.body` / `fonts.display` |
| Brand name like "skills-il" appears with hyphen on the wrong side | Mixed Hebrew+Latin without bidi isolation | Wrap the Latin run in `<bdi>` |
| Hero heading wraps to a second line in Hebrew but not English | Hebrew is wider per character | Either bump hero size by ~15% or shorten the title |
| `paddingLeft: 160` puts content against the right edge of an RTL slide | Physical CSS in an RTL container | Replace with `paddingInline: 160` or `paddingInlineStart: 160` |
| Inspector arrows / file rail flipped | You set `direction: 'rtl'` globally on `<html>` | Move `dir="rtl"` to the page component's root only |
| `current.json` does not exist | Dev server has not been opened on a slide yet | Run `pnpm dev` and open any slide in the browser, then re-read |
| Comment markers missing after applying | Did not delete the marker line, only the text | Re-run the regex; remove the entire line including trailing `\n` |
| `@open-slide/cli init` fails with "package not found" | Network or registry issue | Verify `npm view @open-slide/cli version` returns a version; clear pnpm/npm cache |
| Type imports fail | Wrong package or stale install | Imports come from `@open-slide/core`: `import type { Page, SlideMeta, DesignSystem } from '@open-slide/core'` |

## Bundled Resources

```
rules/
├── slide-authoring.md     # File contract, canvas, type scale, themes, design tokens, assets
├── create-slide.md        # New-deck workflow: theme picker, scoping questions, structure
├── create-theme.md        # Theme markdown authoring under themes/<id>.md
├── apply-comments.md      # @slide-comment marker handling
├── current-slide.md       # Resolving "this page" via current.json
└── hebrew-rtl.md          # Hebrew fonts, bidi, logical CSS, RTL DesignSystem (the new content)
```

Load on demand based on the task. Always start with `hebrew-rtl.md` for Hebrew or bilingual content.
