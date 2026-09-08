# Domain checklist: open-slide-best-practices

Scope: authoring open-slide decks, with Hebrew and RTL as the differentiator. Mirrors the five
skills bundled with `@open-slide/core`, pinned to **1.19.1**.

## Must cover (core)

| Item | Why it is core | Status |
| --- | --- | --- |
| `slides/<id>/index.tsx` file contract | The only file a slide author writes | Covered, `rules/slide-authoring.md` |
| Fixed 1920x1080 canvas and the vertical budget | Overflow is silently cropped, the top cause of broken decks | Covered, SKILL.md + slide-authoring |
| ASCII-only slide folder ids (`SLIDE_ID_RE`) | Hebrew folder names are dropped at discovery with exit 0 | Covered, re-verified on 1.19.1 |
| `DesignSystem` const and `var(--osd-*)` tokens | Runtime theming surface | Covered |
| Themes as a **two-file bundle** (`<id>.md` + `<id>.demo.tsx`) | The Themes panel renders the demo; markdown alone gives a dead preview | Covered, `rules/create-theme.md` |
| `meta.theme` back-link | Links slide to theme, chip + `/themes/<id>` listing | Covered, `rules/create-slide.md` |
| Speaker notes (`notes` export) | Built into the runtime; agents otherwise write a `script.md` the runtime never reads | Covered, SKILL.md + slide-authoring |
| `@slide-comment` inspector markers | The apply-comments workflow | Covered |
| `current.json` deictic resolution | "this page" resolution | Covered |
| Hebrew Google Fonts via module-level, slide-keyed head injection | Hebrew renders in fallback fonts otherwise. Note `&subset=` is a v1 parameter the `css2` endpoint ignores | Covered, `rules/hebrew-rtl.md` |
| CSS logical properties over physical | Physical properties fight RTL reading order | Covered |
| `<bdi>` for mixed Hebrew + Latin | Bidi reordering corrupts mixed runs | Covered |
| Hebrew type-scale calibration | Hebrew is ~10-15% wider per character | Covered, runtime default is 168/36 |
| Node engine requirement | `commander@15` declares `node >=22.12.0` and `chalk@6` declares `node >=22`; both warn on Node 20 | Covered |
| Version landscape: 1.19.x stable vs 2.0.0-beta | Prevents accidental beta adoption; carries the stale-`vite` upgrade trap | Covered as of 1.4.0 |

## Should cover (advanced)

| Item | Status |
| --- | --- |
| `<Steps>` / `SlideTransition` / `MorphElement` | Deferred to pinned upstream reference files |
| Assets and `<ImagePlaceholder>` | Covered in slide-authoring |
| `useSlidePageNumber()` with `<bdi>` digits in an RTL footer | Covered |
| Dev-server surfaces (notes drawer, command menu, presenter deck switching, `allowedHosts`) | Covered as of 1.4.0 |

## Out of scope (explicit)

- **A `## Examples` section in SKILL.md.** *Accepted structural exception, decided 2026-09-08.*
  This is a reference-style skill: SKILL.md is a router into `rules/*.md`, and the worked
  examples legitimately live in `rules/hebrew-rtl.md` and `rules/slide-authoring.md` next to the
  rules they illustrate. Duplicating them into SKILL.md would add maintenance surface and push
  toward the 5,000-word cap without helping an agent that already loads the rules file. This was
  deferred in 1.2.0 and 1.3.0; it is now settled rather than re-deferred each cycle.
- **v2.0.0-beta API documentation.** The skill carries a version advisory and the upgrade trap,
  but documents no v2-specific API. The beta shipped twice in the week before 1.4.0, and upstream
  states v1 slide source needs no changes, so per-API v2 coverage would go stale without helping.
  Revisit when v2 reaches GA.
- Video generation. Belongs to `remotion-best-practices` / `hyperframes-best-practices`.
- Generic Hebrew presentations outside open-slide. Belongs to `presentation-generator`.

## Authoritative sources

Every factual claim in this skill is pinned in `evidence.json` to the `@open-slide/core` 1.19.1
release commit `7fbd1ea84cf1ee7cd701cc9fe59bff3e4e0148c5`, not to `main` (which now serves
2.0.0-beta). The sources used, each with per-file URLs recorded in `evidence.json`:

- Upstream repo `1weiho/open-slide`, read at the pinned release commit: the runtime source under
  `packages/core/src/` and the five bundled skills under `packages/core/skills/`.
- The upstream docs site, including its v1-to-v2 migration guide.
- The npm registry metadata for `@open-slide/core` and `@open-slide/cli`, cross-checked against
  each package's `package.json` at the pinned commit.
- Google Fonts stylesheet endpoints for the Hebrew subset, and MDN for logical properties and
  the `bdi` element.

When bumping the pinned version, update the URLs in `evidence.json` and the upstream links inside
`SKILL.md`, `SKILL_HE.md` and `rules/*.md` together, then re-run the verifier with
`--check-sources`.
