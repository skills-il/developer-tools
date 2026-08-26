# Changelog

## 1.2.1 - 2026-08-26

Citation corrections in `references/domain-checklist.md`, found by the Independent Judge re-verifying every cited path and line against upstream @ 4f00336.

### Fixed

- Row M12 listed `inspect` among the commands deprecated in favour of `check`. `validate.ts` and `layout.ts` do carry `deprecated: true`; `inspect.ts` carries no deprecation marker and `inspect` is a live command. Corrected.
- Row S2 cited `registry.json` as 154 blocks and 219 components. It parses to 154 blocks, 218 components and 9 examples.
- Row M11 cited `browser/manager.ts:191` for the chrome-headless-shell auto-download; line 191 is a type export. The substantive line is 45 (`PUPPETEER_CACHE_DIR`).

## 1.2.0 - 2026-08-26

Validated against upstream heygen-com/hyperframes @ 4f00336 (release v0.8.15, 2026-08-26).

### Fixed

- `hyperframes validate` is deprecated upstream in favour of `hyperframes check`, which runs lint, runtime, layout, motion and the WCAG contrast pass in one browser session. Updated the Output Checklist, the Contrast section and both Troubleshooting entries in EN and HE. `lint` is not deprecated and stays.
- The animation-map invocation pointed at `skills/hyperframes/scripts/animation-map.mjs`, a path that does not exist upstream (it is `skills/hyperframes-animation/scripts/`). Corrected in SKILL.md and in both bundled scripts' own usage headers.
- Kokoro was described as supporting "8 languages" while listing nine. Upstream's `SUPPORTED_LANGS` tuple holds nine locales. Corrected in six places across SKILL.md, SKILL_HE.md, references/tts.md and references/hebrew-rtl.md.
- `data-track-index` was documented as "same-track clips cannot overlap". It is a Studio display lane; upstream's linter states that neither it nor `data-layer` is read by the render. Removed the false constraint.
- The claim that `$ELEVENLABS_API_KEY` makes `hyperframes tts` route to ElevenLabs is wrong: the command is local-only and has no provider argument. The HeyGen Starfish, then ElevenLabs, then Kokoro order belongs to the media-use audio path. Rewritten in EN and HE.
- Kokoro TTS reference link 404'd (`skills/hyperframes-media/...`); the file lives at `skills/media-use/audio/references/tts.md`.
- `references/tts.md` claimed `tts --list` shows "54 voices (8 languages)". The CLI bundles 12 voices covering 6 of the 9 locales.
- GSAP pin moved 3.15.0 to 3.14.2 to match the version upstream scaffolds into `templates/blank/index.html`, so a composition does not end up loading two GSAP builds.
- `fitTextFontSize` returns `{ fontSize, fits }`, not a number.

### Added

- `## Bundled Scripts` (EN + HE): both scripts import `@hyperframes/producer`, which Node resolves relative to the script file, so they must be copied into the project before they run. Verified by executing both end to end against a 1080x1920 Hebrew RTL composition. `contrast-report.mjs` was previously undocumented.
- Gotcha: `animation-map.mjs` describes motion in screen space, so a correct Hebrew entrance (`x: 80`, entering from the right) is reported as "moves left". Measured, not inferred.
- Gotcha: audio groups (`data-audio-group`), the summed FX bus (`data-fx-chain`) and `hyperframes normalize-audio` for layering Hebrew narration over a music bed.
- `hyperframes transcribe --engine` (auto/parakeet/whisper) noted alongside the existing `.en`-model warning.

## 1.1.2 - 2026-08-19

### Fixed

- Translated section headings that had been left in English in SKILL_HE.md, where they rendered as-is on the Hebrew page. Hebrew is the site's default locale, and the skill validator never checked the Hebrew file, so these went unnoticed.

