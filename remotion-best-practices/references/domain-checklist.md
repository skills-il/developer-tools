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
  https://www.remotion.dev/docs/premount
- **`@remotion/media` `<Video>` / `<Audio>` and `<OffthreadVideo>`.** Use new
  `@remotion/media` `<Video>` (frame-exact, off-thread via Mediabunny) as the current
  default; explain that the legacy "prefer `<OffthreadVideo>` over `<Video>`" advice
  refers only to the legacy `<Video>` from the `remotion` package. `trimBefore`/`trimAfter`
  in FRAMES, volume callbacks, playbackRate, loop, toneFrequency.
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
- **Rendering + Lambda/Cloud Run.** `npx remotion render`, `--codec` (incl. `h264-mkv`,
  `png` image-sequence), `--concurrency`, `--scale`, `--frames`; `@remotion/lambda`
  (recommended) and `@remotion/cloudrun` (alpha). https://www.remotion.dev/docs/cli/render ,
  https://www.remotion.dev/docs/lambda
- **whisper.cpp captions.** `@remotion/install-whisper-cpp` `installWhisperCpp` +
  `downloadWhisperModel` + `transcribe` (`whisperCppVersion`, `tokenLevelTimestamps`) +
  `toCaptions`; pin a current whisper.cpp version; multilingual `medium` (not `medium.en`)
  for non-English. https://www.remotion.dev/docs/install-whisper-cpp/transcribe
- **Captions display.** `Caption` type, `@remotion/captions`, `createTikTokStyleCaptions`,
  word highlighting via tokens, `useDelayRender()` for fetching caption JSON, `parseSrt`.
  https://www.remotion.dev/docs/captions
- **Licensing gate.** Remotion is free for individuals / non-profits / orgs with <=3
  employees; 4+ employees need a paid Company License (applies to all use, not a feature).
  https://www.remotion.dev/docs/license

### Hebrew / RTL differentiators (the skill's reason to exist)

- **Bidi isolates** for mixed Hebrew/Latin/numbers: `⁦` (LRI), `⁧` (RLI),
  `⁩` (PDI); container `direction: "rtl"`. https://www.remotion.dev/docs/
- **RTL flex semantics**: in an RTL flex container `flex-start` = RIGHT, `flex-end` = LEFT;
  do NOT use `flexDirection: "row-reverse"` (double-reverses). First DOM child renders right.
- **Hebrew font width**: Hebrew display weights render ~20-30% wider than English; drop the
  font size ~2 steps; `flexWrap: "nowrap"` / `whiteSpace: "nowrap"` to avoid mid-phrase wrap.
- **Hebrew fonts with `subsets: ["hebrew"]`** (Heebo, Rubik, Assistant, Noto Sans Hebrew).
  https://www.remotion.dev/docs/google-fonts
- **Hebrew RTL captions / typewriter**: caption container `direction: "rtl"`,
  `whiteSpace: "pre"`; typewriter reveals from the end of the string.
- **Natural Israeli Hebrew copy** (not literal translation) for on-screen text/captions.

## Should cover

- Transitions: `<TransitionSeries>`, `Transition` vs `Overlay`, timing helpers,
  duration math. https://www.remotion.dev/docs/transitions
- Audio visualization: `useWindowedAudioData`, `visualizeAudio`, waveform helpers.
  https://www.remotion.dev/docs/visualize-audio
- 3D: `@remotion/three` `<ThreeCanvas>`, ban `useFrame()` from r3f.
  https://www.remotion.dev/docs/three
- Charts, text animations, GIFs (`@remotion/gif`), Lottie, Tailwind, light leaks, maps,
  transparent video, measuring text/DOM, `getVideoDuration/Dimensions`, FFmpeg helpers,
  silence detection.
- Voiceover (ElevenLabs `eleven_multilingual_v2` default; `eleven_v3` for broader langs),
  Israeli map coordinates.
- One-frame `npx remotion still` sanity check; Studio is preview-only.

## Out of scope

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
