# Remotion Best-Practices Coverage Checklist

Canonical coverage contract for a Remotion best-practices skill, with a Hebrew/RTL
differentiator layer. Each item cites the authoritative remotion.dev page to verify
against. Used as the gate for review and future updates.

## Must cover

- **Frame-driven motion, never CSS animation.** All motion comes from
  `useCurrentFrame()`; `@keyframes`, `transition-*`, `animate-*`, Tailwind animation
  classes are forbidden (do not render deterministically on export).
  https://www.remotion.dev/docs/the-fundamentals
- **`useCurrentFrame()` + `interpolate()` + `spring()`.** Write timing in seconds and
  multiply by `fps` from `useVideoConfig()`; clamp with `extrapolateLeft/Right`; offer
  `Easing.bezier` (CSS cubic-bezier parity) and `spring()` as the physics option.
  https://www.remotion.dev/docs/interpolate , https://www.remotion.dev/docs/spring
- **Sequencing: `<Sequence>` + `<Series>`.** `from`, `durationInFrames`, `layout="none"`,
  local-frame reset inside a Sequence, negative-`from` trimming, nesting.
  https://www.remotion.dev/docs/sequence , https://www.remotion.dev/docs/series
- **Premounting.** `premountFor` to load a Sequence before it plays (fonts/assets ready).
  https://www.remotion.dev/docs/player/premounting
- **`@remotion/media` `<Video>` / `<Audio>` and `<OffthreadVideo>`.** Use new
  `@remotion/media` `<Video>` (frame-exact, off-thread via Mediabunny) as the current
  default; explain that the legacy "prefer `<OffthreadVideo>` over `<Video>`" advice
  refers only to the legacy `<Video>` from the `remotion` package. `trimBefore` +
  `durationInFrames` in FRAMES (`trimAfter` deprecated as of 4.0.533), `objectFit` as a PROP
  (it overrides `style.objectFit`, default `contain`), volume callbacks, playbackRate, loop,
  toneFrequency.
  https://www.remotion.dev/docs/media/video , https://www.remotion.dev/docs/offthreadvideo
- **`<Img>` over native `<img>`.** Native `<img>`/`<video>` cause blank frames; always use
  `<Img>` from remotion. https://www.remotion.dev/docs/img
- **`calculateMetadata` laziness.** Dynamic duration/dimensions/props; keep it cheap and
  lazy since it runs before every render; `abortSignal` for stale Studio requests.
  https://www.remotion.dev/docs/calculate-metadata
- **Compositions / Stills / parametrization.** `<Composition>`, `<Still>`, `defaultProps`,
  Zod `schema`, `zColor`. https://www.remotion.dev/docs/composition ,
  https://www.remotion.dev/docs/parametrized-rendering
- **Fonts: `@remotion/google-fonts` + `@remotion/fonts`.** Type-safe loadFont, weights,
  subsets, `waitUntilDone()`, local fonts. https://www.remotion.dev/docs/fonts
- **Rendering + Lambda/Cloud Run.** `npx remotion render`, `--codec` (incl. `h264-mkv`, `h264-ts`, `gif`; `png` is
  NOT a codec, use `--sequence` + `--image-format=png`), `--concurrency`, `--scale`, `--frames`; `@remotion/lambda`
  (recommended) and `@remotion/cloudrun` (frozen: critical fixes only). https://www.remotion.dev/docs/cli/render ,
  https://www.remotion.dev/docs/lambda
- **whisper.cpp captions.** `@remotion/install-whisper-cpp` `installWhisperCpp` +
  `downloadWhisperModel` + `transcribe` (`whisperCppVersion`, `tokenLevelTimestamps`) +
  `toCaptions`; pin a current whisper.cpp version; multilingual `medium` (not `medium.en`)
  for non-English. https://www.remotion.dev/docs/install-whisper-cpp/transcribe
- **WebGPU captions.** `@remotion/whisper-webgpu` (browser, and Node.js since 4.0.528) needs a
  GPU (`canUseWhisperWebGpu()`); `language` is REQUIRED for multilingual models (no
  auto-detect), so Hebrew needs `language: "he"` with `small` / `medium` / `large-v3-turbo`.
  https://www.remotion.dev/docs/whisper-webgpu/transcribe
- **Mediabunny sources.** `UrlSource` (URL), `BlobSource` (browser `File`), `FilePathSource`
  (Node path, then `input.dispose()`); there is no `FileSource`. `getImageDimensions()` is in
  `@remotion/media-utils`, not `remotion`.
- **Captions display.** `Caption` type, `@remotion/captions`, `createTikTokStyleCaptions`,
  word highlighting via tokens, `useDelayRender()` for fetching caption JSON, `parseSrt`.
  https://www.remotion.dev/docs/captions
- **Licensing gate.** Remotion is free for individuals / non-profits / orgs with <=3
  employees; 4+ employees need a paid Company License (applies to all use, not a feature).
  https://www.remotion.dev/docs/license

### Hebrew / RTL differentiators (the skill's reason to exist)

- **Bidi isolates** for mixed Hebrew/Latin/numbers: `\u2066` (LRI), `\u2067` (RLI),
  `\u2069` (PDI); container `direction: "rtl"`. https://www.remotion.dev/docs/
- **RTL flex semantics**: in an RTL flex container `flex-start` = RIGHT, `flex-end` = LEFT;
  do NOT use `flexDirection: "row-reverse"` (double-reverses). First DOM child renders right.
- **Hebrew font width**: no fixed Hebrew-to-English width ratio (varies by font and wording);
  size display titles with `fitText()` from `@remotion/layout-utils` after the font loads;
  `flexWrap: "nowrap"` / `whiteSpace: "nowrap"` to avoid mid-phrase wrap.
  https://www.remotion.dev/docs/layout-utils/fit-text
- **Hebrew fonts with `subsets: ["hebrew", "latin"]`** (Heebo, Rubik, Assistant, Noto Sans Hebrew); the
  `hebrew` unicode-range has no space, digits or ASCII punctuation.
  https://www.remotion.dev/docs/google-fonts
- **Hebrew RTL captions / typewriter**: caption container `direction: "rtl"`,
  `whiteSpace: "pre"`; typewriter reveals with `slice(0, n)` (logical order, which RTL paints
  right-to-left), never from the end of the string. Hebrew transcription pins `language: "he"`.
  Mapbox has no Hebrew basemap localization, so Hebrew map labels are Remotion overlays.
- **Natural Israeli Hebrew copy** (not literal translation) for on-screen text/captions.

## Should cover

- Transitions: `<TransitionSeries>`, `Transition` vs `Overlay`, timing helpers,
  duration math. https://www.remotion.dev/docs/transitions
- Audio visualization: `useWindowedAudioData`, `visualizeAudio`, waveform helpers.
  https://www.remotion.dev/docs/visualize-audio
- 3D: `@remotion/three` `<ThreeCanvas>`, ban `useFrame()` from r3f.
  https://www.remotion.dev/docs/three
- Charts, text animations, GIFs (`<AnimatedImage>`, `@remotion/gif`), Lottie, Tailwind, light leaks
  (`lightLeak()` from `@remotion/effects`; `@remotion/light-leaks` is deprecated), maps,
  transparent video, measuring text/DOM, `getVideoDuration/Dimensions`, FFmpeg helpers,
  silence detection.
- Voiceover (ElevenLabs `eleven_v3` for Hebrew via Text to Speech; the v4 family also lists
  Hebrew but its release note routes `eleven_v4` through Text to Dialogue; `eleven_multilingual_v2`
  and `eleven_flash_v2_5` have no Hebrew),
  Israeli map coordinates.
- One-frame `npx remotion still` sanity check; Studio is preview-only.

## Out of scope

(Re-checked 2026-10-07: none of these is a question an ordinary user of a Remotion skill would
expect it to answer, and none became capturable since the last cycle.)

- Non-Remotion video editing (raw FFmpeg pipelines without Remotion, DaVinci, Premiere).
- General React app development; static image generation outside Remotion.
- Live/realtime TTS conversational audio (voiceover here is pre-rendered).
- Deep r3f/Three.js tutorials beyond the Remotion integration rules.

## Authoritative sources

- Remotion docs index: https://www.remotion.dev/docs
- CLI render: https://www.remotion.dev/docs/cli/render
- Lambda: https://www.remotion.dev/docs/lambda
- @remotion/media: https://www.remotion.dev/docs/media/video
- @remotion/captions: https://www.remotion.dev/docs/captions
- install-whisper-cpp: https://www.remotion.dev/docs/install-whisper-cpp
- @remotion/google-fonts: https://www.remotion.dev/docs/google-fonts
- License: https://www.remotion.dev/docs/license
- GitHub (versions/releases): https://github.com/remotion-dev/remotion
- whisper.cpp releases: https://github.com/ggml-org/whisper.cpp/releases
- ElevenLabs models: https://elevenlabs.io/docs
