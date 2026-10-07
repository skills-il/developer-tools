---
name: transcribe-captions
description: Transcribing audio to generate captions in Remotion
metadata:
  tags: captions, transcribe, whisper, audio, speech-to-text
---

# Transcribing audio

To transcribe audio to generate captions in Remotion, you can use the [`transcribe()`](https://www.remotion.dev/docs/install-whisper-cpp/transcribe) function from the [`@remotion/install-whisper-cpp`](https://www.remotion.dev/docs/install-whisper-cpp) package.

## Prerequisites

First, the @remotion/install-whisper-cpp package needs to be installed.
If it is not installed, use the following command:

```bash
npx remotion add @remotion/install-whisper-cpp
```

## Transcribing

Make a Node.js script to download Whisper.cpp and a model, and transcribe the audio.

```ts
import path from "path";
import {
  downloadWhisperModel,
  installWhisperCpp,
  transcribe,
  toCaptions,
} from "@remotion/install-whisper-cpp";
import fs from "fs";

const to = path.join(process.cwd(), "whisper.cpp");

// whisper.cpp 1.5.5 is the documented minimum; pin to a current STABLE release.
// As of 2026-10 the latest stable releases are v1.9.5 and v1.9.4. Skip tags GitHub marks
// "Pre-release" (v1.9.3 is one). Pinned to 1.9.4 rather than 1.9.5 only because 1.9.5
// was one day old at the time of writing. Check https://github.com/ggml-org/whisper.cpp/releases
const WHISPER_CPP_VERSION = "1.9.4";
// Windows caveat: only official release tags are accepted there, prebuilt binaries stop at
// 1.6.0, and from 1.7.3 a source build is required, which needs cmake on PATH.

await installWhisperCpp({
  to,
  version: WHISPER_CPP_VERSION,
});

// Use "medium" (multilingual) for Hebrew or any non-English audio.
// "medium.en" is ENGLISH-ONLY and produces garbage for Hebrew (see SKILL.md Gotcha #3).
// "large-v3-turbo" is also multilingual and is the better Hebrew default when you can
// afford the download (~1.62 GB vs ~1.53 GB for "medium"): faster inference and higher
// multilingual accuracy. Both are in the supported model list of @remotion/install-whisper-cpp.
await downloadWhisperModel({
  model: "medium",
  folder: to,
});

// transcribe() REQUIRES a 16-bit 16kHz WAV. ElevenLabs and most TTS providers emit MP3,
// so this conversion is a mandatory step in the Hebrew pipeline, not an optional one.
import {execSync} from 'child_process';
execSync('npx remotion ffmpeg -i /path/to/voiceover.mp3 -ar 16000 -ac 1 /path/to/audio123.wav -y');

const whisperCppOutput = await transcribe({
  model: "medium",
  whisperPath: to,
  whisperCppVersion: WHISPER_CPP_VERSION,
  inputPath: "/path/to/audio123.wav",
  // ALWAYS pin the language for Hebrew. Without it whisper.cpp auto-detects, and on short
  // or noisy Hebrew audio it routinely picks Arabic, Yiddish or English, or emits Latin
  // transliteration, which poisons every caption downstream however correct the RTL
  // container is. "he" is a valid value of the Language type.
  language: "he",
  tokenLevelTimestamps: true,
});

// Optional: Apply our recommended postprocessing
const { captions } = toCaptions({
  whisperCppOutput,
});

// Write it to the public/ folder so it can be fetched from Remotion
fs.writeFileSync("captions123.json", JSON.stringify(captions, null, 2));
```

Transcribe each clip individually and create multiple JSON files.

See [Displaying captions](display-captions.md) for how to display the captions in Remotion.

## GPU transcription without whisper.cpp: `@remotion/whisper-webgpu`

Remotion 4.0.518 added `@remotion/whisper-webgpu`, which runs timestamped Whisper models over
WebGPU through Transformers.js and converts the result to `@remotion/captions`. It needs no
whisper.cpp build. It runs in the browser (Studio, Player), and since 4.0.528 the docs also
cover Node.js (with `@mediabunny/server` to decode the file to a 16kHz waveform). Either way it
needs a GPU: call `canUseWhisperWebGpu()` first and fall back to the whisper.cpp route above if
`supported` is false, which is the usual case on GPU-less CI runners.

Install it together with its Transformers.js peer dependency:

```bash
npx remotion add @remotion/whisper-webgpu @huggingface/transformers
```

The example below runs in the browser: `resampleTo16Khz()` decodes and resamples browser audio, so it is not the Node.js path. In Node.js, also install `mediabunny` and `@mediabunny/server` and follow the Node.js page linked at the end of this section to build the 16kHz waveform.

**Hebrew rule for this package:** automatic language detection is not supported. With a
multilingual model the `language` option of `transcribe()` is required, so pass `language: "he"`
and pick a multilingual model (`small` is the documented default; `medium` and `large-v3-turbo`
are also available). Never use a `.en` model for Hebrew audio.

```ts
import {
  canUseWhisperWebGpu,
  downloadWhisperModel,
  resampleTo16Khz,
  toCaptions,
  transcribe,
} from "@remotion/whisper-webgpu";

export const transcribeHebrewFile = async (file: File) => {
  const support = await canUseWhisperWebGpu();
  if (!support.supported) {
    throw new Error(support.detailedReason);
  }
  await downloadWhisperModel({ model: "small" });
  const channelWaveform = await resampleTo16Khz({ file });
  const transcription = await transcribe({
    channelWaveform,
    model: "small",
    language: "he",
  });
  const { captions } = toCaptions({ whisperWebGpuOutput: transcription });
  return captions;
};
```

See https://www.remotion.dev/docs/whisper-webgpu and, for Node.js, https://www.remotion.dev/docs/whisper-webgpu/node.
