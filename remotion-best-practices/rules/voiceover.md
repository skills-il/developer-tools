---
name: voiceover
description: Adding AI-generated voiceover to Remotion compositions using TTS
metadata:
  tags: voiceover, audio, elevenlabs, tts, speech, calculateMetadata, dynamic duration
---

# Adding AI voiceover to a Remotion composition

Use ElevenLabs TTS to generate speech audio per scene, then use [`calculateMetadata`](./calculate-metadata) to dynamically size the composition to match the audio.

## Prerequisites

By default this guide uses **ElevenLabs** as the TTS provider (`ELEVENLABS_API_KEY` environment variable). Users may substitute any TTS service that can produce an audio file.

If the user has not specified a TTS provider, recommend ElevenLabs and ask for their API key.

**For Hebrew, never use `eleven_multilingual_v2` or `eleven_flash_v2_5`.** `eleven_multilingual_v2` covers 29 languages and Hebrew is NOT among them (nor is it in `eleven_flash_v2_5`, which is v2's list plus Hungarian, Norwegian and Vietnamese). Hebrew (heb) is in the language lists of the v3 family (`eleven_v3`, 70+ languages) and of the newer v4 family (`eleven_v4` and `eleven_v4_turbo`, 90+ languages, released September 28, 2026).

The example below uses `eleven_v3`, which ElevenLabs documents as usable with the Text to Speech API that this script calls. ElevenLabs now calls v3 its previous generation and recommends v4, but its v4 release note routes `eleven_v4` through the Text to Dialogue API. Before swapping `eleven_v4` into this Text to Speech call, check that `GET /v1/models` reports `can_do_text_to_speech` for it, and drop `style` from `voice_settings`, because the Style setting is not available in Eleven v4. `eleven_multilingual_v2` remains a reasonable default for the 29 languages it does cover.

Ensure the environment variable is available when running the generation script:

```bash
node --strip-types generate-voiceover.ts
```

## Generating audio with ElevenLabs

Create a script that reads the config, calls the ElevenLabs API for each scene, and writes MP3 files to the `public/` directory so Remotion can access them via `staticFile()`.

The core API call for a single scene:

```ts title="generate-voiceover.ts"
const response = await fetch(
  `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
  {
    method: "POST",
    headers: {
      "xi-api-key": process.env.ELEVENLABS_API_KEY!,
      "Content-Type": "application/json",
      Accept: "audio/mpeg",
    },
    body: JSON.stringify({
      text: "Welcome to the show.",
      model_id: "eleven_v3", // v3 for Hebrew; multilingual_v2 has no Hebrew
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75,
        style: 0.3,
      },
    }),
  },
);

if (!response.ok) {
  // Without this check a 401/422 error body gets written to disk as an "MP3".
  throw new Error(`ElevenLabs ${response.status}: ${await response.text()}`);
}

const audioBuffer = Buffer.from(await response.arrayBuffer());
writeFileSync(`public/voiceover/${compositionId}/${scene.id}.mp3`, audioBuffer);
```

## Dynamic composition duration with calculateMetadata

Use [`calculateMetadata`](./calculate-metadata.md) to measure the [audio durations](./get-audio-duration.md) and set the composition length accordingly.

```tsx
import { CalculateMetadataFunction, staticFile } from "remotion";
import { getAudioDuration } from "./get-audio-duration";

const FPS = 30;

const SCENE_AUDIO_FILES = [
  "voiceover/my-comp/scene-01-intro.mp3",
  "voiceover/my-comp/scene-02-main.mp3",
  "voiceover/my-comp/scene-03-outro.mp3",
];

export const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
}) => {
  const durations = await Promise.all(
    SCENE_AUDIO_FILES.map((file) => getAudioDuration(staticFile(file))),
  );

  const sceneDurations = durations.map((durationInSeconds) => {
    return durationInSeconds * FPS;
  });

  return {
    durationInFrames: Math.ceil(sceneDurations.reduce((sum, d) => sum + d, 0)),
  };
};
```

The computed `sceneDurations` are passed into the component via a `voiceover` prop so the component knows how long each scene should be.

If the composition uses [`<TransitionSeries>`](./transitions.md), subtract the overlap from total duration: [./transitions.md#calculating-total-composition-duration](./transitions.md#calculating-total-composition-duration)

## Rendering audio in the component

See [audio.md](./audio.md) for more information on how to render audio in the component.

## Delaying audio start

See [audio.md#delaying](./audio.md#delaying) for more information on how to delay the audio start.
