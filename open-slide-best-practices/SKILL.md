---
name: open-slide-best-practices
description: "Best practices for authoring presentations with open-slide, the React slide framework with a fixed 1920×1080 canvas, with full Hebrew and RTL support. Covers the slides/[id]/index.tsx file contract, type scale, DesignSystem tokens, themes/ system, @slide-comment inspector markers, current.json deictic resolution, Hebrew Google Fonts (Heebo, Rubik, Assistant, Noto Sans Hebrew), CSS logical properties, bidirectional Hebrew+English text with the bdi element, and Hebrew-aware type scale tuning. Use when authoring or editing slides under slides/[id]/ in an open-slide project, or when building Hebrew or bilingual decks on the framework. Do NOT use for video creation (use remotion-best-practices or hyperframes-best-practices), or for generic Hebrew presentations outside open-slide (use presentation-generator)."
license: MIT
---

# open-slide Best Practices for Israeli Developers

> Adapted from [open-slide/open-slide](https://github.com/open-slide/open-slide) (MIT, formerly `1weiho/open-slide`). Hebrew and RTL adaptations by [skills-il](https://agentskills.co.il).

## Problem

open-slide ships an opinionated authoring system: a fixed 1920×1080 React canvas, a typed `DesignSystem` const, a themes folder, an inspector that drops `@slide-comment` markers in source, and five built-in skills (`slide-authoring`, `create-slide`, `create-theme`, `apply-comments`, `current-slide`). None of those touch Hebrew or RTL. Out of the box, a deck written by a coding agent comes out left-aligned, system-font only, with `paddingLeft` that fights the Hebrew reading order, and no guidance for mixed Hebrew+English text. Israeli developers waste hours retrofitting RTL, loading Hebrew Google Fonts, and discovering that type sizes tuned against English copy do not transfer reliably to Hebrew.

## Instructions

### When to use

Use this skill whenever you are writing or editing code under `slides/<id>/` in an open-slide project, creating a theme under `themes/`, or processing inspector comments, especially when any of that content is in Hebrew or bilingual.

### New project setup

When in an empty folder or workspace with no existing open-slide project, scaffold one using:

```bash
npx @open-slide/cli init my-slide
cd my-slide
npm run dev
```

Replace `my-slide` with a suitable project name. The scaffolder installs dependencies, runs `git init` with a first commit, and prints `npm run dev` as the next step. `init` takes `--use-pnpm` / `--use-yarn` / `--use-bun` / `--use-npm` to pick the package manager, and `--no-install` / `--no-git` to skip those steps.

**Node version.** Core 2.x declares `"node": "^20.19.0 || >=22.12.0"`, but the CLI depends on `commander@15`, which declares `">=22.12.0"`, and on `chalk@6` (`">=22"`). On Node 20.19 the scaffold still completes but npm prints `EBADENGINE Unsupported engine` for both. Use Node 22.12 or newer.

**Vocabulary trap.** In open-slide a "slide" is a whole deck (one folder) and its "pages" are what a user calls slides. "A 10-slide deck" / "מצגת של 10 שקפים" means ten pages in ONE `slides/<id>/index.tsx`, not ten folders.

What the scaffold gives you:

| Path | What it is |
| --- | --- |
| `slides/<id>/index.tsx` | One folder per deck. See the id rule below. |
| `themes/` | Theme bundles (`<id>.md` + `<id>.demo.tsx`) |
| `assets/` | Global assets shared across decks, imported via `@assets/...` |
| `open-slide.config.ts` | Typed `OpenSlideConfig` export, empty by default. Options: `base`, `slidesDir`, `themesDir`, `assetsDir`, `port`, `allowedHosts`, `build`, `agent`, and a deprecated `locale`. |
| `.agents/skills/` and `.claude/skills/` | The five upstream skills, copied in at init time |
| `AGENTS.md` / `CLAUDE.md` | Short routing rules telling a coding agent which bundled skill to use |
| `npm run sync:skills` | Re-copies the bundled skills out of `@open-slide/core` after a core upgrade |

Run `npm run sync:skills` after upgrading `@open-slide/core`, otherwise the agent keeps reading the skill copies from the version you scaffolded with.

### Which version you are on

Target **`@open-slide/core` 2.x**. v2 went GA on 2026-09-26, npm's `latest` tag resolves to it, and `npx @open-slide/cli init` scaffolds it. Everything in this skill is verified against **2.3.1**, by scaffolding a project and running its build and exports.

**Upgrading a v1 workspace.** Slide source needs no changes; the upstream migration guide confines the move to `package.json`, your Node version and your deploy config. Bump `@open-slide/core` to `^2.0.0` and `react` / `react-dom` to `^19.2.8`, reinstall, then run `npm run sync:skills`.

**The one thing that breaks on upgrade.** A v1 scaffold puts `vite` in your `devDependencies`; core 2.x ships its own Vite 8. Leave the old entry in place and `dev`, `build` and `preview` all refuse to start:

```
✖ Remove vite from your package.json
  devDependencies in package.json still lists vite, a leftover from v1.
  It shadows the vite@8.3.5 bundled with open-slide: @tailwindcss/vite
  is loading vite@5.4.21 from node_modules/vite instead.
    $ npm uninstall vite
```

Run the printed uninstall command (it matches your package manager). Fresh v2 scaffolds omit `vite` and ship `vercel.json` / `netlify.toml` so hosts still know how to build. Migration guide: <https://open-slide.dev/docs/migrate-to-v2>.

### Slide folder ids must be ASCII (Hebrew folder names are silently dropped)

**Do not name a slide folder in Hebrew.** Discovery filters every folder under `slides/` through `SLIDE_ID_RE = /^[a-z0-9_-]+$/i` and skips the rest, so a folder like `slides/פתיחה/` never reaches the sidebar, the browser, or the build. Re-verified on `@open-slide/core@2.3.1` by scaffolding a project and running `npm run build`:

```
[plugin open-slide] Ignoring slide folder "פתיחה": slide ids must match
/^[a-z0-9_-]+$/i (lowercase/uppercase letters, digits, "-", "_"). Rename the folder under
"slides/" to a kebab-case id so it appears in the browser and can be moved into folders.
```

It is only a warning, so `npm run build` exits 0. Use a Latin kebab-case id (`peticha`, `cover`, `q2-roadmap`) and put the Hebrew in `meta.title` and in the page content, where it belongs.

**Do not over-apply this rule.** It is specific to slide folder ids. Verified as NOT affected:

| Surface | Hebrew allowed? | Why |
| --- | --- | --- |
| `slides/<id>/` folder name | No | Filtered by `SLIDE_ID_RE` at discovery |
| `meta.title` | Yes | Free text, never used as an id |
| `themes/<id>.md` file name | Yes | The theme id is `path.basename(file, '.md')` with no ASCII filter, and theme routes are built with `encodeURIComponent(id)` |
| Theme frontmatter values (`name:`, `description:`) | Yes | Only the frontmatter KEY is matched against `/^([A-Za-z0-9_-]+)\s*:/`; the value is free text |
| Slide body copy | Yes | It is just JSX text |

### Hebrew and RTL

For any Hebrew or bilingual deck, load [./rules/hebrew-rtl.md](./rules/hebrew-rtl.md) first. It covers:

- Hebrew Google Fonts (Heebo, Rubik, Assistant, Noto Sans Hebrew) loaded by head injection
- The `<html dir="rtl">` set-up vs per-page `dir` attribute (the canvas root is the page component, not the document)
- CSS logical properties (`paddingInlineStart`, `marginInlineStart`, `insetInlineStart`) instead of `paddingLeft`/`marginLeft`/`left`
- `flexDirection: 'row-reverse'` vs setting `dir` on the flex container
- Bidirectional isolation with `<span dir="ltr">` or `<bdi>` for mixed Hebrew + Latin (brand names, code, URLs)
- Hebrew-aware type scale tuning (English sizes are not a reliable guide; preview and adjust)
- Hebrew `DesignSystem.fonts` choices and RTL-aware theme markdown
- Hebrew typography pitfalls: nikkud rendering, sofit letter spacing, hyphen vs maqaf

### Slide authoring (file contract, canvas, type scale, themes, design tokens)

For the technical reference on what goes inside `slides/<id>/index.tsx`, load [./rules/slide-authoring.md](./rules/slide-authoring.md). It mirrors the upstream `slide-authoring` skill (file contract, canvas math, type scale, themes, `DesignSystem` tokens, starter template, assets, previewing a page) with Hebrew/RTL pointers inline.

Upstream has since split its own `slide-authoring` skill into per-primitive reference files. Three of them cover primitives this skill does not restate, so read them upstream rather than reimplementing by hand:

| Upstream reference | Primitive | Why it matters in a Hebrew deck |
| --- | --- | --- |
| [`references/steps.md`](https://raw.githubusercontent.com/open-slide/open-slide/f4d840ed1282cb4e2db1280f4a6454113a495383/packages/core/skills/slide-authoring/references/steps.md) | `<Steps>` / `<Step>` stepped reveals | Staged reveals let you keep each Hebrew beat short instead of overflowing one dense page |
| [`references/page-numbers.md`](https://raw.githubusercontent.com/open-slide/open-slide/f4d840ed1282cb4e2db1280f4a6454113a495383/packages/core/skills/slide-authoring/references/page-numbers.md) | `useSlidePageNumber()` | Read `{ current, total }` from the hook instead of hardcoding a footer counter; wrap the whole `current / total` run in one `<span dir="ltr">` inside an RTL footer (per-number wrapping still reverses it) |
| [`references/morph.md`](https://raw.githubusercontent.com/open-slide/open-slide/f4d840ed1282cb4e2db1280f4a6454113a495383/packages/core/skills/slide-authoring/references/morph.md) | `MorphElement` shared-element ("magic move") transitions | Morph interpolates position and size across the cut, so an element that moves between an LTR and an RTL page needs the same `id` on both |

### Drafting a new deck

When the user asks for "make slides about X" / "create a presentation" / "draft a deck", load [./rules/create-slide.md](./rules/create-slide.md) for the workflow: theme picker, the four scoping questions (aesthetic direction, page count, text density, motion), slide id selection, structure planning, visual commitment, write, self-review, hand off.

### Creating a theme

When the user asks to "create a theme" / "make a theme called X" / "extract a theme from this slide", load [./rules/create-theme.md](./rules/create-theme.md). A theme is a **two-file bundle**: `themes/<id>.md` (Palette / Typography / Layout / Fixed components / Motion / Aesthetic) plus a paired demo module `themes/<id>.demo.tsx` (`.jsx`, `.ts` and `.js` are also accepted), a runnable 2-3 page mini-slide that the dev UI's Themes panel renders as the live preview. Writing only the markdown leaves the theme with a dead preview card.

### Applying inspector comments

When the user left comments in the dev server's comment mode and asks to "apply comments", load [./rules/apply-comments.md](./rules/apply-comments.md): marker format, detection regex, decoded payload (including dragged-region `rect`), and the reverse-line-order procedure.

### Resolving deictic references ("this page", "the slide I'm on")

When the user references the current slide without naming it, load [./rules/current-slide.md](./rules/current-slide.md) **first**. It reads the live cursor at `node_modules/.open-slide/current.json`. **Re-read it on every deictic turn**; a value you read earlier is almost certainly stale.

### Speaker notes go in the `notes` export, never in a markdown file

Asked for a talk track, agents routinely write a `script.md` the runtime never reads, and the presenter view stays empty.

Notes are an optional `notes` export in `slides/<id>/index.tsx`, **index-aligned** with the default page array. `SlideModule` declares it as `notes?: (string | undefined)[]`. Use `undefined` to skip a page rather than shifting the array:

```tsx
const Cover: Page = () => <div dir="rtl">שלום</div>;
const Agenda: Page = () => <div dir="rtl">סדר היום</div>;
const Pillars: Page = () => <div dir="rtl">שלושה עמודי תווך</div>;

export const notes: (string | undefined)[] = [
  'פתחו בציטוט של הלקוח, ואז הציגו את עצמכם.',
  undefined,
  `שלושה עמודי תווך, פסקה לכל אחד.
עצרו לשאלות לפני המעבר.`,
];

export default [Cover, Agenda, Pillars];
```

Rules:

- One entry per page, in the same order as the default export. A missing entry silently misaligns every note after it.
- Multi-line notes work; use a template literal.
- **`notes` must be a hand-written ARRAY LITERAL, one plain element per page, with no `satisfies` or `as const` after it.** The dev server writes drawer edits back into your source (`PUT /__notes`). A computed array, an imported constant or a `.map()` returns `422 \`notes\` export is not an array literal` and breaks drawer editing. A spread INSIDE a literal (`[...intro, 'x']`) is worse: it passes the check, counts as one element, and a drawer edit then lands on the wrong page silently.
- **The presenter view renders a small Markdown subset** (bold, italic, inline code, `#` headings, lists) since 2.0.0; the notes drawer edits the raw text. Upstream's own `slide-authoring` skill still says markdown is not rendered, which no longer matches the code. Any note line starting with `- `, `* `, `1. ` or `1) ` becomes a list.
- **Hebrew notes render LTR-aligned and you cannot fix it from the slide.** The drawer and presenter set no `dir`, and presenter lists indent with a physical left padding, so Hebrew bullets sit on the left. Prefer short plain paragraphs over Markdown lists in Hebrew notes.
- Never deliver a speech script as a separate file. If the user asks for "תסריט" / "a script" / "speaker notes", it goes in this export.

Upstream documents this export since 2.0.0; the Hebrew behaviour above and the export behaviour below are documented nowhere upstream.

### Exporting a Hebrew deck (read before "export it for the board")

The toolbar's Download menu has four exports. Verified on 2.3.1 by exporting a Hebrew test deck and reading the produced files:

| Export | Hebrew result | Notes included? |
| --- | --- | --- |
| **Export as PPTX** (editable) | **Broken for Hebrew. Do not use.** Any Hebrew paragraph that wraps, or that mixes Hebrew with a Latin run, is split into one text run per character with a line break after each, so PowerPoint shows a vertical column of single letters. English exports cleanly; the defect is RTL-specific. Paragraphs also carry no `rtl` attribute and `text-align: start` maps to left. | Yes |
| **Export as image PPTX** | Safe. Each page becomes one PNG on a PowerPoint slide, so text is not editable. | Yes, as raw text: `lang="en-US"`, no `rtl`, and Markdown markers (`**`) stay literal |
| **Export as PDF** | Safe, vector text via the browser's print pipeline. Not supported in Safari (shows an error); use Chrome or Edge. The print frame is white: CSS gradient layers and `box-shadow` are stripped from every element, so a gradient-only page background prints white. Put a solid `background-color` under any gradient, and check the PDF. | No |
| **Export as HTML** | A static snapshot that keeps the page markup (`dir`, text, styles), but a Google Fonts `<link>` stays an external URL, so the file needs internet to show Heebo; offline it falls back to a system Hebrew face and re-wraps. | No |

So: for a board pack, export **PDF from Chrome or Edge**. If the board needs speaker notes inside the file, export **image PPTX** and fix the notes' direction in PowerPoint (or keep notes as plain short paragraphs). The PDF and PPTX exports wait for `document.fonts.ready` before capturing.

**The agent cannot produce the file.** Exports run in the browser; the CLI has no export command, and PDF opens the system print dialog. Hand the user the steps: start the dev server, open the deck in Chrome or Edge, Download, Export as PDF, then choose "Save as PDF" as the destination (page size is already set). Never claim `npm run build` produced the board file.

The upstream docs' Export page still says native editable PPTX "is not available yet", which no longer matches the shipped menu.

### Dev-server surfaces worth knowing

These are viewer features, not authoring APIs, but users ask about them and an agent that knows they exist avoids rebuilding them by hand:

| Surface | What it does |
| --- | --- |
| Notes drawer / presenter view | Renders the `notes` export above. Present mode shows notes beside the timer. |
| Preview route | `/s/<id>/preview?p=N` (1-based, dev only) renders one page with no editor chrome; the server URL is in `node_modules/.open-slide/server.json`. Screenshot it at 1920×1080 to check a Hebrew page. Steps in `slide-authoring.md`. |
| Comment mode | Toolbar mode: click an element or drag across a region, type a note. Pending comments become `@slide-comment` markers; see `apply-comments.md`. |
| Inline text and visual editing | Double-click text to edit it in place, with a floating Format toolbar; elements can be moved and resized. Edits are written back into `index.tsx`. See Gotchas 14 and 15 for the Hebrew traps. |
| Agent panel | Press `A` to drive a locally installed Claude Code or Codex from the browser. Its system prompt routes only to the RTL-unaware upstream skills, so for Hebrew decks add a line to the project's `CLAUDE.md` / `AGENTS.md` pointing at this skill. `agent: { enabled: false }` hides it. |
| Command menu | `⌘K` palette for searching decks, jumping to pages and running slide actions. |
| Presenter-window deck switching | The presenter window can switch decks without dropping the presenter session. |
| Themes panel | Renders each theme's `<id>.demo.tsx`. A theme with no demo file shows an empty card. |
| `allowedHosts` | `open-slide.config.ts` accepts `allowedHosts?: string[] \| true`, needed when serving the dev server through a tunnel or a non-localhost host. |

### Vertical budget reminder (the #1 source of broken slides)

Anything below 1080px on the canvas is silently cropped. Before writing any page, sum:

```
(font_size × line_height × number_of_lines) + gaps + (2 × padding) ≤ 1080
```

If you're tight, **split into two pages**. Never use `overflow: auto/scroll/hidden`, negative margins, or transforms to hide overflow. The canvas does not scroll; cropped content is gone. See [./rules/slide-authoring.md](./rules/slide-authoring.md) section "Vertical budget" for the full worked example.

For Hebrew text, do not trust sizes borrowed from an English layout: a heading that fits on one line in English may wrap to two in Heebo. Drop the size or shorten the copy, and confirm in the preview route. See `hebrew-rtl.md` section 4.

## Reference Links

| Source | URL | What to Check |
| --- | --- | --- |
| open-slide upstream repo | https://github.com/open-slide/open-slide | Latest API, breaking changes, version, `packages/core/CHANGELOG.md` |
| open-slide docs / homepage | https://open-slide.dev | Install, demos |
| open-slide v1 to v2 migration guide | https://open-slide.dev/docs/migrate-to-v2 | Upgrade steps, Node requirement, the `vite` devDependency trap |
| @open-slide/cli on npm (latest package.json via unpkg) | https://unpkg.com/@open-slide/cli/package.json | `version` = the CLI that `npx` runs today |
| @open-slide/core on npm (latest package.json via unpkg) | https://unpkg.com/@open-slide/core/package.json | `version` and `engines` of the runtime `latest` resolves to |
| MDN: CSS logical properties | https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values | RTL-aware CSS, `inset-inline-start`, `padding-inline` |
| MDN: `<bdi>` element | https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdi | Bidi isolation for mixed Hebrew+Latin |
| Google Fonts metadata for Heebo | https://raw.githubusercontent.com/google/fonts/2fe1e8c6b137fb13041a7cfca6fdcd8a910ea4dc/ofl/heebo/METADATA.pb | `subsets: "hebrew"` (same file exists per family under `ofl/<family>/`) |
| Upstream slide-id regex (`slide-ops.ts`) | https://raw.githubusercontent.com/open-slide/open-slide/f4d840ed1282cb4e2db1280f4a6454113a495383/packages/core/src/editing/slide-ops.ts | `SLIDE_ID_RE`, whether non-ASCII slide folder ids are still filtered out |
| Upstream webfont loading rules | https://raw.githubusercontent.com/open-slide/open-slide/f4d840ed1282cb4e2db1280f4a6454113a495383/packages/core/skills/slide-authoring/references/webfonts.md | The supported way to load a webfont (head injection, slide-keyed id) |

## Recommended MCP Servers

None directly, since open-slide has no API surface. The skill is purely client-side authoring guidance.

## Gotchas

These are the failure modes a coding agent hits when authoring an open-slide deck in Hebrew without this skill. They are NOT user errors.

1. **Using `paddingLeft` and `marginLeft` everywhere.** In LTR these read as "from the start of the line". In RTL they're literally on the wrong side of the canvas. Use `paddingInlineStart` / `paddingInlineEnd` (or shorthand `paddingInline`) so the layout flips automatically when `dir="rtl"` is set on the canvas root. The same applies to `left` / `right` (use `insetInlineStart` / `insetInlineEnd`) and `text-align: left/right` (use `text-align: start/end`).

2. **Setting `direction: 'rtl'` on `<html>` or globally.** open-slide's canvas root is the page component, not the HTML document. The dev server chrome (file rail, navigation arrows) is upstream UI in English; flipping the document direction breaks it. Set `dir="rtl"` on the page component's root `<div>` only. The Inspector and presenter mode keep their LTR layout; only your slide content flips. There is no Hebrew option to switch them to either: `OpenSlideConfig.locale` is deprecated in favour of the slide UI's language switcher, and the shipped UI locales are `en`, `zh-TW`, `zh-CN`, `ja` and `es` only. Tell the user the authoring chrome stays English; only the deck is Hebrew.

3. **Naming the slide folder in Hebrew.** It is the natural thing to do on a Hebrew deck and it silently loses the slide: discovery filters folder names through `/^[a-z0-9_-]+$/i` and only warns. Latin kebab-case id, Hebrew in `meta.title`. See "Slide folder ids must be ASCII" above.

4. **Loading the Hebrew webfont from inside the page component.** A `<style>@import ...</style>` or a `<link>` rendered inside a `Page` re-registers the whole `@font-face` set once per mounted page, and the home page, the thumbnail rail, the overview grid and the PDF print root all mount every page at the same time. Upstream's rule is to inject the stylesheet once into `<head>` from module top level of `index.tsx`, with an element id keyed to the slide (`osd-webfont-<slide-id>`) so one slide's fonts cannot suppress another's. See `hebrew-rtl.md` section 3.

5. **The default display font is a serif with no Hebrew glyphs.** `defaultDesign.fonts.display` is `Georgia, "Times New Roman", serif` and `fonts.body` is `-apple-system, BlinkMacSystemFont, "Inter", system-ui, sans-serif`. Georgia carries no Hebrew, so an unstyled Hebrew hero silently falls back to whatever system serif the OS picks (David / Times-like). That, not the body stack, is the real cause of the "my Hebrew deck renders in a dated serif" symptom. For decks that ship beyond a dev machine, load Heebo or Rubik via Google Fonts (`css2`, no `subset` parameter, it is ignored) and put them first in the stack with the system stack as fallback. See `hebrew-rtl.md`.

6. **Reusing the English type scale unchecked.** Sizes tuned against English copy do not transfer: Hebrew lines set to a different width and a translated line has a different length. Preview each Hebrew page. If the hero reads small, the +10-15% bump in `hebrew-rtl.md` section 4 is an editorial starting point, but recompute the vertical budget after any bump, since bumping can cause the wrapping it is meant to prevent.

7. **Mixing Hebrew and English without `<bdi>`.** A bullet like "השתמשו ב-React Router" with mixed Hebrew + Latin tokens often renders the punctuation in the wrong place because the browser's bidi algorithm doesn't always isolate the Latin span. Isolate mixed runs with `<span dir="ltr">` (preferred in 2.x, see Gotcha 14) or `<bdi>`: `השתמשו ב-<span dir="ltr">React Router</span>`. Critical for code identifiers, brand names, and URLs inside Hebrew copy.

8. **`array.map` for visually repeated cards.** The upstream rule (one component instantiated per item, NOT `map` over a data array) applies in Hebrew too. The reason is the inspector: `map` shares one source location per item, so editing one Hebrew label changes all rendered cards. Define `<Card />` once, instantiate it three times explicitly. See `slide-authoring.md`.

9. **Ignoring `node_modules/.open-slide/current.json`.** When the user says "תקן את הכותרת בעמוד הזה" ("fix the heading on this page"), the deictic "הזה" maps exactly the same way the English "this" does, you must read `current.json` to find which slide they're on. Re-read it on every turn. See `current-slide.md`.

10. **Same vertical budget at the bumped Hebrew type scale.** A cover that fits a 3-line LTR hero at 200px (3 × 200 × 0.95 = 570px) will overflow if you keep 3 lines AND bump to 232px for Hebrew (3 × 232 × 0.95 = 661px), once padding and subtitle are added you blow past 1080. Either stay at 1-2 lines for the Hebrew hero, or recompute the full budget with the bumped values before committing. Splitting is always the right answer.

11. **Mis-translated technical terms inside the slide copy.** Agents render dev terminology into Hebrew that means something else ("themes" as "ערכאות", a legal term; "resolution" as "רזולוציה"). Use the glossary in `hebrew-rtl.md` section 6.5 and verify terms with a native speaker before shipping.

12. **Gradients between brand colors.** A gradient between two distant brand hues blends through an off-brand intermediate (blue to magenta passes through purple). Hold primary brand colors solid; see `hebrew-rtl.md` section 7.5. Remember too that PDF export strips CSS gradients.

13. **Audit your own copy for bidi traps. Recursively.** A skill that warns about missing `<bdi>` will frequently MISS its own `<bdi>` calls inside Hebrew sentences ("השתמשו ב-RTL" needs `<bdi>RTL</bdi>`). When writing prose, slides, or examples, manually scan every Latin token embedded in Hebrew runs and isolate it (`<span dir="ltr">` or `<bdi>`). Code identifiers, brand names, version numbers, file extensions, all need isolation. The author writing the rule is not exempt from the rule.

14. **`<bdi>` turns off inline text editing for its whole line.** In 2.x, double-click editing only treats an element as editable text when every child is text, `<br>`, or one of `b code del em i ins mark s small span strong sub sup u`. `bdi` is not on that list, so `<p>השתמשו ב-<bdi>React Router</bdi></p>` can no longer be edited in place. When the user wants to keep editing in the browser, use `<span dir="ltr">React Router</span>` instead: the HTML rendering rules give any element with a `dir` attribute `unicode-bidi: isolate`, and `dir="ltr"` also sets the run's direction, which together match what `<bdi>` does for a Latin run (a bare `unicode-bidi: isolate` without `dir` does NOT: it still renders `-5` as `5-`), and `span` stays editable. Use `<span dir="ltr">` for signed numbers too.

15. **The Format and Design panels undo Hebrew rules.** The Format panel's align buttons write physical `textAlign: 'right'` and treat "left" as "remove the property"; the Design panel's Shuffle swaps the `design` const for a Latin-only preset, dropping Heebo and your type scale. After a user touches either panel, re-check `textAlign`, `fonts.display` and `typeScale` in source. Details in `hebrew-rtl.md` sections 2 and 3.

16. **Choosing "Export as PPTX" for a Hebrew deck.** The editable PPTX export shreds wrapped or mixed Hebrew into one character per line. Use "Export as image PPTX" or PDF instead; see "Exporting a Hebrew deck" above.

17. **Self-hosting a Hebrew font through the Assets panel's Google Fonts search.** Its download fetches a single TTF without the Hebrew subset; for Heebo that file has 0 of the 27 Hebrew letters, while the search preview shows Hebrew correctly. Load Hebrew families by head injection (`hebrew-rtl.md` section 3) or self-host a file you checked for Hebrew glyphs.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Hebrew text renders left-aligned | Page root is missing `dir="rtl"` | Add `dir="rtl"` to the page's outer `<div>`, or set `direction: 'rtl'` in its inline style |
| Hebrew heading renders in a serif when you wanted sans | Verified cause: `defaultDesign.fonts.display` is `Georgia, "Times New Roman", serif`, and Georgia has no Hebrew glyphs, so the OS substitutes a system Hebrew serif | Set `fonts.display` (not just `fonts.body`) to a Hebrew family and load it via head injection |
| Editing a note from the drawer fails, or the drawer stops saving | The `notes` export is not an array literal, so the dev server's write-back returns `422 \`notes\` export is not an array literal`. A computed array, an import or a `.map()` trigger it | Write `notes` out as a plain array literal |
| A drawer edit to one page's note lands on a different page | A spread inside the `notes` literal (`[...intro, 'x']`) passes the check but counts as one element | Replace the spread with one written-out entry per page |
| The exported PPTX shows Hebrew as a vertical column of single letters | "Export as PPTX" (editable) splits wrapping or mixed RTL text per character; verified on 2.3.1, English is unaffected | Export as image PPTX or PDF |
| A Hebrew sentence cannot be double-click edited in the browser | It contains a `<bdi>`, which the inline editor does not treat as inline text | Swap the `<bdi>` for `<span dir="ltr">` |
| `✖ Remove vite from your package.json` on `dev` / `build` | A v1 workspace still lists `vite` in `devDependencies`, shadowing core's Vite 8 | Run the printed uninstall command and reinstall |
| Hebrew speaker notes are left-aligned in the presenter pane | The notes drawer and presenter set no `dir`, so notes inherit the viewer chrome's direction. There is no author-side fix | Keep notes short and hard-wrap them; this is viewer behaviour, not a bug in your slide |
| A signed number reads backwards on a Hebrew slide (`-5` shows as `5-`) | The sign has no digit on its other side, so UAX#9 W4 cannot fold it into the number; it stays a neutral and jumps to the far side | Wrap the signed number in `<bdi>` (or `<span dir="ltr">` to keep it inline-editable). Negative KPIs are the usual miss, they look like a single number |
| Brand name like "skills-il" appears with hyphen on the wrong side | Mixed Hebrew+Latin without bidi isolation | Wrap the Latin run in `<span dir="ltr">` or `<bdi>` |
| Hero heading wraps to a second line in Hebrew but not English | The size was tuned against English copy, which sets to a different width and length | Shorten the title or drop the size, then re-check in the preview route |
| A footer page counter reads `12 / 3` on a Hebrew page | The `current / total` run is not isolated, or each number is isolated separately | Wrap the whole run in one `<span dir="ltr">` |
| `paddingLeft: 160` puts content against the right edge of an RTL slide | Physical CSS in an RTL container | Replace with `paddingInline: 160` or `paddingInlineStart: 160` |
| Inspector arrows / file rail flipped | You set `direction: 'rtl'` globally on `<html>` | Move `dir="rtl"` to the page component's root only |
| A slide you created never appears in the sidebar or the build, but nothing errors | The folder id under `slides/` is not ASCII (a Hebrew name), so discovery skipped it with a warning only | Rename the folder to Latin kebab-case; keep the Hebrew in `meta.title`. Grep the dev/build output for `Ignoring slide folder` |
| Hebrew webfont loads but the deck feels heavy on the home page or PDF export | The `@font-face` set is registered once per mounted page because the stylesheet is injected inside a `Page` component | Inject it once into `<head>` from module top level with an id keyed to the slide (`osd-webfont-<slide-id>`) |
| `npm warn EBADENGINE Unsupported engine` on `npx @open-slide/cli init` | Node older than 22.12.0 (`commander@15` requires `>=22.12.0`) | Upgrade Node to 22.12 or newer |
| `current.json` does not exist | Dev server has not been opened on a slide yet | Run `pnpm dev` and open any slide in the browser, then re-read |
| A marker is still in the file after applying, or content was deleted with it | Removed only the text, or removed a whole line that also held content (2.x markers can share a line) | Delete the marker token; delete the line only when nothing else is on it |
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

Load on demand. Start with `hebrew-rtl.md` for Hebrew or bilingual content.
