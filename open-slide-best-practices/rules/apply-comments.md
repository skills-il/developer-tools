# apply-comments (open-slide reference)

> Adapted from [open-slide/open-slide MIT, packages/core/skills/apply-comments/SKILL.md](https://raw.githubusercontent.com/open-slide/open-slide/f4d840ed1282cb4e2db1280f4a6454113a495383/packages/core/skills/apply-comments/SKILL.md). Mirrored from `@open-slide/core@2.3.1`. Hebrew/RTL pointers added by skills-il. Links are pinned to the 2.3.1 release commit, not `main`, so they cannot drift ahead of the published package.

# Apply slide comments

The open-slide editor has a comment mode that lets the user click a rendered page element, or drag across a region of the page, and attach a textual comment (e.g. *"make this red"*, *"change to 'Open Slide Rocks'"*). Each comment is persisted as an in-source JSX marker inside `slides/<slideId>/index.tsx`.

Your job: read those markers, perform the described edits, and delete the markers.

> **Before making any page edit**, consult the [./slide-authoring.md](./slide-authoring.md) reference, it is the technical reference for how `slides/<id>/index.tsx` is structured (canvas, type scale, palette, assets, file contract). A comment like *"make this bigger"* or *"change the accent colour"* should be applied in a way that stays consistent with those rules.

## Marker format

```
{/* @slide-comment id="c-<8hex>" ts="<ISO>" text="<base64url(JSON)>" */}
```

- Sits as the **first child inside** the JSX element it refers to (i.e. between that element's opening `>` and its other children). The marker is dropped *into* its target, not floated above it. Newly written markers get a line of their own; older ones may share a line with the content that follows them.
- `text` is base64url-encoded JSON: `{"note": "...", "hint"?: "...", "rect"?: {"x", "y", "w", "h"}, "page"?: n}`.
  - `rect` is present when the comment was left on a dragged region rather than on an element. Values are pixels on the 1920×1080 page canvas, measured from the page's top-left corner. The marker still sits inside the deepest element that contains the region, but the note refers to what is *inside* that region, possibly several children, or only part of the enclosing element.
  - `page` is the 0-based index (into the default export array) of the page the comment was left on.
- Detection regex (authoritative, use exactly this):

  ```
  /\{\/\*\s*@slide-comment\s+id="(c-[a-f0-9]+)"\s+ts="([^"]+)"\s+text="([A-Za-z0-9_\-]+={0,2})"\s*\*\/\}/g
  ```

## Procedure

1. **Identify the target slide(s).**
   - If the user names one (`getting-started`, `q2-roadmap`, etc.), work on that single `slides/<slideId>/index.tsx`.
   - If they say "all" or don't specify, scan every `slides/*/index.tsx`. Process each slide one at a time.

2. **Read the file and find all markers.**
   - Run the regex above against the whole file.
   - For each match, base64url-decode `text` and `JSON.parse` it to get `{ note, hint?, rect?, page? }`.
   - Record each hit as `{ id, lineIndex (0-based), note, hint, rect, page }`.
   - If there are no markers, tell the user and stop.

3. **Understand each comment in context.**
   - The targeted JSX element is the **enclosing** element of the marker, i.e. read upward from the marker line until you reach the unclosed JSX opening tag whose body the marker lives in. That element is the target. (For self-closing elements like `<img />`, the inspector hoists the marker to the nearest non-self-closing ancestor; in that case the comment usually refers to a child of the enclosing element rather than the enclosing element itself, use the `note` text to disambiguate.)
   - Read enough surrounding code (parent element, sibling elements, inline styles) to apply the change faithfully. A comment inside a `<div>` with an inline `background` style usually refers to that element's styling, for example.
   - When the payload has a `rect`, work out which children of the enclosing element fall inside that region (compare their positions and sizes against the rect on the 1920×1080 canvas) and apply the note to those, not to the whole enclosing element.
   - If the `note` is ambiguous, do the smallest reasonable interpretation and mention the assumption in your summary.

4. **Apply edits in reverse line order.**
   - Sort markers by descending `lineIndex` and process one at a time, using the `Edit` tool.
   - Processing top-down would invalidate line numbers for later markers as the file shrinks/grows.

5. **Remove each marker after applying its edit.**
   - Delete the marker token. If nothing else is left on that line, delete the whole line including its trailing `\n`; if content shares the line, keep that content.
   - Never leave a marker behind for an edit you applied, that signals a failure. Markers deliberately skipped per the edge cases below stay in place.

6. **Verify.**
   - After all edits, re-read the file and confirm the only remaining markers are ones you reported as skipped.
   - Confirm the edited JSX is well-formed (balanced tags, no dangling attributes). If the project's `package.json` has typecheck/lint scripts, run them with the project's package manager; scaffolded projects ship neither TypeScript nor a linter, there, rely on the running dev server (or the `build` script) to surface compile errors. Fix any errors you introduced.
   - If the dev server is running, screenshot each edited page via `/s/<id>/preview?p=N` to confirm the change looks right, see **Previewing a page visually** in [./slide-authoring.md](./slide-authoring.md).

7. **Report.**
   - Summarise: `N applied, M skipped` plus a one-line description of each change (including the slide id).

## base64url decoding helper

```js
function decode(s) {
  const pad = s.length % 4 === 0 ? '' : '='.repeat(4 - (s.length % 4));
  return Buffer.from(s.replace(/-/g, '+').replace(/_/g, '/') + pad, 'base64').toString('utf8');
}
```

You can run this inline via `node -e '...'` if you need to inspect a payload; otherwise just reason about the decoded string.

## Edge cases

- **Marker with no enclosing JSX element** (shouldn't happen, the inspector won't write one, but if you find one): delete it and note as orphan.
- **Multiple markers stacked on consecutive lines inside the same element**: they all refer to that enclosing element. Read their notes in source order to understand the combined intent, then apply and delete them bottom-up per step 4.
- **Comment asks for something outside the target element's scope** (e.g. "add a new page"): do the closest-reasonable edit and mention the scope expansion in your summary.
- **Can't resolve the comment** (e.g. truly ambiguous, or the file changed shape such that the target element doesn't exist): leave the marker in place and report it as skipped. Don't guess.

## Do not

- Do not touch `package.json`, `open-slide.config.ts`, or files outside `slides/`.
- Do not add dependencies.
- Do not re-introduce markers or leave `TODO` breadcrumbs, the user already has a record in git.

## Hebrew and RTL note

Comments may be in Hebrew (e.g. `text` field decoded to "תגדיל את הכותרת" / "make the heading bigger"). The marker format is unaffected, `text` is base64url-encoded JSON and base64url is byte-safe for any Unicode payload. Decode normally; the Hebrew renders fine in your reasoning. When applying the edit, follow the rules in [./slide-authoring.md](./slide-authoring.md) and [./hebrew-rtl.md](./hebrew-rtl.md), e.g. a "make this heading bigger" comment in a Hebrew slide should re-check the new size in the preview route (see [./hebrew-rtl.md](./hebrew-rtl.md) section 4) and recompute the vertical budget.

A `rect` is measured from the page's top-left corner in physical pixels even on an RTL page. Compare it against where children actually render (in an RTL row the first child in source sits on the right), not against their source order.
