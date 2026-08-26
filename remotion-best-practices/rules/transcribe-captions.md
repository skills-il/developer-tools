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

// whisper.cpp 1.5.5 is the documented minimum; pin to a current release.
// As of 2026-08 the whisper.cpp project is on the 1.9.x line (latest v1.9.3).
// Check https://github.com/ggml-org/whisper.cpp/releases for the latest tag.
const WHISPER_CPP_VERSION = "1.9.3";
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

## Browser-side transcription without whisper.cpp

Remotion 4.0.518 added `@remotion/whisper-webgpu`, which runs Whisper in the browser over
WebGPU with no local whisper.cpp install and no model download step in your build. It is the
lighter path when you only need captions inside Studio or a Player, and it avoids the
platform-specific whisper.cpp build entirely. Check support first with `canUseWhisperWebGpu()`,
which needs WebGPU, a usable adapter, and a secure context. The `installWhisperCpp` route above
remains the right choice for CI and headless renders. See https://www.remotion.dev/docs/whisper-webgpu.
