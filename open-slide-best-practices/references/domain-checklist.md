# Domain checklist: open-slide-best-practices

Scope: authoring open-slide decks, with Hebrew and RTL as the differentiator. Mirrors the five
skills bundled with `@open-slide/core`, pinned to **2.3.1** (release commit `f4d840e`).

## Must cover (core)

| Item | Why it is core | Status |
| --- | --- | --- |
| `slides/<id>/index.tsx` file contract | The only file a slide author writes | Covered, `rules/slide-authoring.md` |
| Fixed 1920x1080 canvas and the vertical budget | Overflow is silently cropped, the top cause of broken decks | Covered, SKILL.md + slide-authoring |
| ASCII-only slide folder ids (`SLIDE_ID_RE`) | Hebrew folder names are dropped at discovery with exit 0 | Covered, re-verified on 2.3.1 by `npm run build` |
| `DesignSystem` const and `var(--osd-*)` tokens | Runtime theming surface | Covered |
| Themes as a **two-file bundle** (`<id>.md` + `<id>.demo.tsx`) | The Themes panel renders the demo; markdown alone gives a dead preview | Covered, `rules/create-theme.md` |
| `meta.theme` back-link | Links slide to theme, chip + `/themes/<id>` listing | Covered, `rules/create-slide.md` |
| Speaker notes (`notes` export) | Built into the runtime; agents otherwise write a `script.md` the runtime never reads | Covered, SKILL.md + slide-authoring |
| `@slide-comment` inspector markers | The apply-comments workflow | Covered |
| `current.json` deictic resolution | "this page" resolution | Covered |
| Hebrew Google Fonts via module-level, slide-keyed head injection | Hebrew renders in fallback fonts otherwise. Note `&subset=` is a v1 parameter the `css2` endpoint ignores | Covered, `rules/hebrew-rtl.md` |
| CSS logical properties over physical | Physical properties fight RTL reading order | Covered |
| `<bdi>` for mixed Hebrew + Latin | Bidi reordering corrupts mixed runs | Covered |
| Hebrew type-scale calibration | English sizes are not a reliable guide for Hebrew copy; the +10-15% bump is an editorial starting point, verified by previewing | Covered, runtime default is 168/36 |
| Page counters, timelines and charts in RTL | A per-number isolate still reverses `3 / 12`; a row-based roadmap runs right to left | Covered as of 2.0.0, hebrew-rtl section 6 |
| Node engine requirement | `commander@15` declares `node >=22.12.0` and `chalk@6` declares `node >=22`; both warn on Node 20 | Covered |
| Version landscape: v2 is GA and `latest`; v1 upgrade path | v1 workspaces carry the stale-`vite` trap that blocks dev/build | Covered as of 2.0.0 |
| Exporting a Hebrew deck (PDF / image PPTX / editable PPTX / HTML) | Editable PPTX shreds Hebrew per character (measured); PDF is not supported in Safari and strips gradients; only PPTX carries notes | Covered as of 2.0.0, SKILL.md + hebrew-rtl section 3 |
| Speaker notes: presenter Markdown subset, LTR rendering, spread pitfall, export behaviour | The notes export is what the user asks for in "with speaker notes" | Covered as of 2.0.0 |
| 2.x editing surfaces vs Hebrew (`<bdi>` blocks inline editing, Format panel physical align, Shuffle drops Hebrew fonts, Assets-panel Google Fonts download has no Hebrew glyphs) | Each silently undoes a Hebrew rule the skill teaches | Covered as of 2.0.0, Gotchas 14-17 + hebrew-rtl |
| Preview route and `server.json` for visual self-review | The only way an agent can look at a Hebrew page without driving the editor | Covered as of 2.0.0 |
| Agent panel routes to RTL-unaware upstream skills | Users drafting from the in-app panel bypass this skill unless `CLAUDE.md` points at it | Covered as of 2.0.0 |

## Should cover (advanced)

| Item | Status |
| --- | --- |
| `<Steps>` / `SlideTransition` / `MorphElement` | Deferred to pinned upstream reference files |
| Assets and `<ImagePlaceholder>` | Covered in slide-authoring |
| `useSlidePageNumber()` with `<bdi>` digits in an RTL footer | Covered |
| Dev-server surfaces (notes drawer, preview route, comment mode, inline/visual editing, agent panel, command menu, presenter deck switching, `allowedHosts`) | Covered as of 2.0.0 |
| `data-waitfor` on async content before export | Deferred (minor, 2.0.0 cycle) |
| `build.*` toggles for a public share link | Deferred (minor, 2.0.0 cycle) |
| Visual-editing resize writes fixed `height` on text boxes, later copy overflows | Deferred (minor, 2.0.0 cycle) |

## Out of scope (explicit)

- **A `## Examples` section in SKILL.md.** *Accepted structural exception, decided 2026-09-08, re-confirmed 2026-11-03* (the rationale below still holds).
  This is a reference-style skill: SKILL.md is a router into `rules/*.md`, and the worked
  examples legitimately live in `rules/hebrew-rtl.md` and `rules/slide-authoring.md` next to the
  rules they illustrate. Duplicating them into SKILL.md would add maintenance surface and push
  toward the 5,000-word cap without helping an agent that already loads the rules file. This was
  deferred in 1.2.0 and 1.3.0; it is now settled rather than re-deferred each cycle.
- **v2.0.0-beta API documentation.** *Re-opened and closed 2026-11-03.* v2 reached GA on
  2026-09-26 and is npm `latest`, so the row failed the "would a user ask" test. The skill now
  targets 2.x and is verified on 2.3.1. Nothing v2-specific remains out of scope.
- **Editable-PPTX internals and an upstream fix.** *Reviewed 2026-11-03.* Users will not ask how
  the line grouper works; they need "do not use it for Hebrew", which the skill says. Reporting the
  bug upstream is a maintainer action, not skill content.
- Video generation. Belongs to `remotion-best-practices` / `hyperframes-best-practices`.
- Generic Hebrew presentations outside open-slide. Belongs to `presentation-generator`.

## Authoritative sources

Every factual claim in this skill is pinned in `evidence.json` to the `@open-slide/core` 2.3.1
release commit `f4d840ed1282cb4e2db1280f4a6454113a495383`, not to `main`. The sources used, each
with per-file URLs recorded in `evidence.json`:

- Upstream repo `open-slide/open-slide` (formerly `1weiho/open-slide`), read at the pinned release
  commit: the runtime source under `packages/core/src/` and the five bundled skills under
  `packages/core/skills/`.
- The upstream docs site, including its v1-to-v2 migration guide and the Export and Agent pages.
- The npm `latest` package.json of `@open-slide/core` and `@open-slide/cli`, read through unpkg
  (npmjs.com itself is Cloudflare-gated and cannot serve as evidence).
- A 2.3.1 project scaffolded and exported locally (build output, PPTX/HTML export XML).
- Google Fonts stylesheet endpoints for the Hebrew subset, the HTML rendering spec, and MDN.

When bumping the pinned version, update the URLs in `evidence.json` and the upstream links inside
`SKILL.md`, `SKILL_HE.md` and `rules/*.md` together, then re-run the verifier with
`--check-sources`.
