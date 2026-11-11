# Hebrew animation slots: which engine and which skill

Moved out of SKILL.md Step 5 at v1.4.0 to stay under the 5,000-word body cap.

video-use's upstream SKILL.md says: *"Do not default to Remotion just because the animation is web-adjacent."* For Hebrew animation slots the priority is the same, and there is a dedicated skill per engine:

| Slot type | Engine | Skill to load into the sub-agent prompt |
|-----------|--------|------------------------------------------|
| Kinetic typography, callout cards, product UI motion | HyperFrames | `hyperframes-best-practices` (covers Heebo via Google Fonts auto-fetch, `dir="rtl"`, `<bdi>` for mixed scripts) |
| Component-state compositions, existing Remotion brand system | Remotion | `remotion-best-practices` (covers Hebrew Google Fonts, bidi text animations) |
| Diagrams, equation derivations | Manim | (no Hebrew skill yet, Manim's Hebrew support is limited; pre-render Hebrew labels as PNG and import as `ImageMobject`) |
| Simple counters, typewriter, single bar reveals | PIL | Use `Pillow.ImageFont.truetype("Heebo-Bold.ttf", size, layout_engine=ImageFont.Layout.RAQM)` to enable HarfBuzz-based BiDi. Without `RAQM`, Pillow draws glyphs in input order and Hebrew comes out backwards |

Upstream also warns that fonts fail silently: a web font that did not load renders in a fallback face with no error. For Hebrew that fallback is usually a face with no Hebrew glyphs at all, so assert the font loaded (HyperFrames/Remotion: `document.fonts.check(...)`; PIL: pass an explicit font path) before rendering.
