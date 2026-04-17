---
name: hebrew-rtl
description: Hebrew RTL text rendering, fonts, captions, and bidirectional text in Remotion
metadata:
  tags: hebrew, rtl, bidi, fonts, captions, israel
---

# Hebrew & RTL Video Production in Remotion

## Hebrew Google Fonts

Use `@remotion/google-fonts` with the `hebrew` subset. These fonts have excellent Hebrew support:

```tsx
// Heebo -- clean, modern, great for titles and body
import { loadFont } from "@remotion/google-fonts/Heebo";
const { fontFamily } = loadFont("normal", {
  weights: ["400", "700", "900"],
  subsets: ["hebrew"],
});

// Rubik -- rounded, friendly, works for marketing videos
import { loadFont as loadRubik } from "@remotion/google-fonts/Rubik";
const { fontFamily: rubikFamily } = loadRubik("normal", {
  weights: ["400", "600", "700"],
  subsets: ["hebrew"],
});

// Assistant -- geometric, minimal, good for tech content
import { loadFont as loadAssistant } from "@remotion/google-fonts/Assistant";
const { fontFamily: assistantFamily } = loadAssistant("normal", {
  weights: ["400", "600", "700"],
  subsets: ["hebrew"],
});

// Noto Sans Hebrew -- widest Unicode coverage, fallback font
import { loadFont as loadNoto } from "@remotion/google-fonts/NotoSansHebrew";
const { fontFamily: notoFamily } = loadNoto("normal", {
  weights: ["400", "700"],
  subsets: ["hebrew"],
});
```

Always specify `subsets: ["hebrew"]` to avoid downloading the full font file. For bilingual videos, add both subsets:

```tsx
const { fontFamily } = loadFont("normal", {
  weights: ["400", "700"],
  subsets: ["hebrew", "latin"],
});
```

## RTL Text Direction

Every Hebrew text container MUST have `direction: "rtl"` and `textAlign: "right"`. Without these, Hebrew text renders left-aligned and punctuation appears on the wrong side.

```tsx
const hebrewTextStyle: React.CSSProperties = {
  direction: "rtl",
  textAlign: "right",
  fontFamily, // Hebrew font loaded above
  fontSize: 48,
  color: "white",
};

export const HebrewTitle: React.FC<{ text: string }> = ({ text }) => {
  return (
    <div style={hebrewTextStyle}>
      {text}
    </div>
  );
};
```

For full-frame Hebrew layouts, set RTL on the AbsoluteFill:

```tsx
import { AbsoluteFill } from "remotion";

export const HebrewScene: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        direction: "rtl",
        padding: 60,
        justifyContent: "center",
        alignItems: "flex-start", // "flex-start" is the RIGHT side in RTL
      }}
    >
      <h1 style={{ fontFamily, fontSize: 72, color: "white" }}>
        כותרת ראשית
      </h1>
      <p style={{ fontFamily, fontSize: 36, color: "#ccc" }}>
        טקסט משנה עם הסבר נוסף
      </p>
    </AbsoluteFill>
  );
};
```

## RTL Flex Containers (Icons + Hebrew Text)

In RTL flex containers, `flex-start` means RIGHT and `flex-end` means LEFT. This catches everyone. When you have icon + text rows (checkmarks, bullet points, list items), use `justifyContent: "flex-start"` to right-align them. The RTL direction already reverses DOM order, so the first child (icon) renders on the right:

```tsx
// WRONG -- icon on left, row centered (ignores RTL)
<div style={{ direction: "rtl" }}>
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 12 }}>
    <span>✅</span>
    <span>פונטים עבריים</span>  {/* centered row, looks wrong in RTL */}
  </div>
</div>

// CORRECT -- icon on right, row right-aligned
<div style={{ direction: "rtl" }}>
  <div style={{
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-start",
    gap: 12,
  }}>
    <span>✅</span>
    <span>פונטים עבריים</span>  {/* icon on RIGHT, row hugs the right edge */}
  </div>
</div>
```

The critical insight: in an RTL flex container, `flex-start` = RIGHT and `flex-end` = LEFT. This is the opposite of what you expect. So to right-align rows in RTL, use `justifyContent: "flex-start"`. No need for `flexDirection: "row-reverse"` -- the RTL direction already reverses item order (first DOM child renders on the right).

Never set `direction: "ltr"` on Hebrew text spans inside an RTL flex container. It breaks the visual ordering and makes punctuation jump to the wrong side.

## RTL Multi-Group Text (Equations, Mixed Colors, Accent Phrases)

When you need a single line of Hebrew text split into multiple groups (different colors, different animation timings, or accent phrases), the same RTL rule applies at the outer flex level.

Reading order for `A + B = C` in Hebrew should be: start from the RIGHT with "A", flow left through "+ B = C" and end with "C" on the LEFT.

```tsx
// WRONG -- row-reverse + RTL double-reverses, ordering is broken
<div style={{
  direction: "rtl",
  display: "flex",
  flexDirection: "row-reverse",
  gap: 20,
}}>
  <KineticWords words={["Remotion", "+", "עברית", "="]} color="black" />
  <KineticWords words={["כאב", "ראש"]} color="red" />
</div>

// CORRECT -- default flex row in RTL puts first DOM child on the RIGHT
<div style={{
  direction: "rtl",
  display: "flex",
  justifyContent: "flex-start",
  gap: 20,
}}>
  <KineticWords words={["Remotion", "+", "עברית", "="]} color="black" />
  {/* renders on the RIGHT */}
  <KineticWords words={["כאב", "ראש"]} color="red" />
  {/* renders on the LEFT */}
</div>
```

The rule: the FIRST DOM child goes on the RIGHT in an RTL flex row. Write your DOM in natural reading order (what comes FIRST in Hebrew reading goes FIRST in the JSX), and RTL will position it correctly without needing `row-reverse`.

## Preventing Line Wrapping on Hebrew Titles

Hebrew fonts like Heebo at display weights are wider than their English equivalents. Multi-word titles that look fine in English often wrap to 2 lines in Hebrew.

```tsx
// WRONG -- words wrap, breaking the composition rhythm
<div style={{ display: "flex", gap: 12 }}>
  {words.map(w => <span>{w}</span>)}
</div>

// CORRECT -- force single line, shrink font if needed
<div style={{
  display: "flex",
  gap: 12,
  flexWrap: "nowrap",
  whiteSpace: "nowrap",
}}>
  {words.map(w => <span>{w}</span>)}
</div>
```

Rule of thumb: Hebrew at the same font size renders ~20-30% wider than English. If an English title at `fontSize: 72` fits, the Hebrew equivalent needs `fontSize: 54-60` on the same canvas width.

## Hebrew Copy in Video Captions -- Natural Israeli Phrasing

Hebrew captions and on-screen text in videos must sound like natural spoken Israeli Hebrew, not translated English. Translated-sounding Hebrew makes videos feel AI-generated and loses native viewers.

Red flags to avoid in Hebrew video copy:

| Translated feel | Natural Israeli |
|-----------------|-----------------|
| "תמיכה מלאה ב-X" (full support for X) | "זה עובד עם X, כמו שצריך" (it works with X, as it should) |
| "טקסט מיושר לשמאל" (passive participle, spec-like) | "עברית מתיישרת לשמאל" / "הטקסט נדחף לשמאל" (active verb) |
| "פונטים לא נטענים" (formal) | "פונטים לא עולים" (Israeli dev slang for "load") |
| "מכונת כתיבה" (typewriter = physical machine) | "אפקט הקלדה" (typing effect = actual CSS term) |
| "ניתן להשתמש" (formal passive) | "אפשר להשתמש" / "השתמשו" (imperative or casual) |
| "על ידי" (by means of) | just drop it, use active voice |

For interjections and excitement: "סוף סוף" (finally), "כמו שצריך" (as it should), "באמת" (really), "בטח" (sure) -- these make Hebrew copy feel native.

**Warning: do not invent vivid metaphors in Hebrew that work in English.** English metaphors rarely translate. "Hebrew falls to the left" (עברית נופלת שמאלה) sounds wrong in Hebrew because `נופלת` means "falls down" (gravity direction), not "goes sideways". Stick to active-voice verbs that Israeli developers actually say: `מתיישרת` (aligns itself), `נדחפת` (gets pushed), `יוצאת` (comes out), `מופיעה` (appears). When in doubt, keep it simple over poetic. Ask a native speaker before using any unusual verb choice.

## Em Dashes Forbidden

Never use em dashes (`—`) or en dashes (`–`) in skill content, video captions, or any Hebrew/English text. Replace with:
- `,` (comma) for mid-sentence pauses
- `:` (colon) for explanations
- `()` (parentheses) for asides
- `--` (double hyphen) for stronger breaks
- `.` (period) to split into two sentences

Em dashes do not exist on standard keyboards and don't render reliably in every rendering context. They also make text feel machine-generated to Israeli readers.

## Bidirectional Text (Bidi)

When mixing Hebrew with English or numbers, use Unicode bidi isolates to prevent reordering bugs:

```tsx
// Numbers in Hebrew context -- wrap numbers in LTR isolate
const price = 299;
const text = `המחיר הוא \u2066${price}\u2069 שקלים`;

// Brand names in Hebrew -- wrap English in LTR isolate
const brand = "Remotion";
const text2 = `צור סרטונים עם \u2066${brand}\u2069 בקלות`;

// Hebrew in English context -- wrap Hebrew in RTL isolate
const feature = "כתוביות";
const text3 = `Supports \u2067${feature}\u2069 rendering`;
```

Unicode bidi isolates:
- `\u2066` (LRI) -- Left-to-Right Isolate (wrap English/numbers in Hebrew context)
- `\u2067` (RLI) -- Right-to-Left Isolate (wrap Hebrew in English context)
- `\u2069` (PDI) -- Pop Directional Isolate (close the isolate)

For Remotion components, apply bidi at the container level:

```tsx
<div style={{ direction: "rtl", unicodeBidi: "isolate" }}>
  {hebrewTextWithNumbers}
</div>
```

## Hebrew Captions (RTL TikTok-Style)

When displaying Hebrew captions using `createTikTokStyleCaptions()`, the caption container MUST have RTL direction. Without it, word highlighting breaks because tokens are rendered in visual LTR order.

```tsx
import type { TikTokPage } from "@remotion/captions";

const HIGHLIGHT_COLOR = "#39E508";

const HebrewCaptionPage: React.FC<{ page: TikTokPage }> = ({ page }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentTimeMs = (frame / fps) * 1000;
  const absoluteTimeMs = page.startMs + currentTimeMs;

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          fontSize: 72,
          fontWeight: "bold",
          whiteSpace: "pre",
          direction: "rtl",        // CRITICAL for Hebrew
          textAlign: "center",
          fontFamily,              // Hebrew font
        }}
      >
        {page.tokens.map((token) => {
          const isActive =
            token.fromMs <= absoluteTimeMs && token.toMs > absoluteTimeMs;

          return (
            <span
              key={token.fromMs}
              style={{ color: isActive ? HIGHLIGHT_COLOR : "white" }}
            >
              {token.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
```

For Hebrew transcription with Whisper, use the `medium` model (not `medium.en`) which supports Hebrew:

```ts
await downloadWhisperModel({
  model: "medium",  // NOT "medium.en" -- Hebrew needs multilingual model
  folder: to,
});
```

## Hebrew Typewriter Effect

Standard typewriter effects slice from the left. For Hebrew, you must slice from the RIGHT (end of string) to reveal characters in reading order:

```tsx
const HebrewTypewriter: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Characters per second
  const CPS = 15;
  const charsToShow = Math.min(
    Math.floor((frame / fps) * CPS),
    text.length
  );

  // Hebrew: slice from the END to reveal right-to-left
  const visibleText = text.slice(text.length - charsToShow);

  return (
    <div
      style={{
        direction: "rtl",
        textAlign: "right",
        fontFamily,
        fontSize: 64,
        color: "white",
        whiteSpace: "pre",
      }}
    >
      {visibleText}
    </div>
  );
};
```

For word-by-word reveal (more natural for Hebrew):

```tsx
const HebrewWordReveal: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const words = text.split(" ");
  const WORDS_PER_SECOND = 3;
  const wordsToShow = Math.min(
    Math.floor((frame / fps) * WORDS_PER_SECOND),
    words.length
  );

  // Take first N words (Hebrew reading order is maintained by RTL direction)
  const visibleWords = words.slice(0, wordsToShow).join(" ");

  return (
    <div
      style={{
        direction: "rtl",
        textAlign: "right",
        fontFamily,
        fontSize: 56,
        color: "white",
      }}
    >
      {visibleWords}
    </div>
  );
};
```

## Hebrew Voiceover

When using ElevenLabs TTS for Hebrew voiceover, use the `eleven_multilingual_v2` model:

```ts
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
      text: "שלום, ברוכים הבאים לסרטון שלנו",
      model_id: "eleven_multilingual_v2", // Required for Hebrew
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75,
        style: 0.3,
      },
    }),
  },
);
```

ElevenLabs Hebrew voices: check the voice library for voices tagged with Hebrew support. The multilingual v2 model handles Hebrew nikkud (vowel marks) but works better without them in most cases.

## Israeli Map Defaults

When using Mapbox for Israeli map animations, use these coordinates:

```ts
// Major Israeli cities
const ISRAEL_LOCATIONS = {
  telAviv: { center: [34.7818, 32.0853] as [number, number], zoom: 13 },
  jerusalem: { center: [35.2137, 31.7683] as [number, number], zoom: 13 },
  haifa: { center: [34.9896, 32.7940] as [number, number], zoom: 13 },
  beerSheva: { center: [34.7913, 31.2520] as [number, number], zoom: 13 },
  eilat: { center: [34.9519, 29.5577] as [number, number], zoom: 13 },
};

// Israel overview (shows full country)
const ISRAEL_OVERVIEW = {
  center: [35.0, 31.5] as [number, number],
  zoom: 7.5,
  pitch: 0,
  bearing: 0,
};

// Tel Aviv to Jerusalem route
const TLV_TO_JLM: [number, number][] = [
  [34.7818, 32.0853], // Tel Aviv
  [34.8516, 31.9000], // Ramla area
  [34.9800, 31.8000], // Sha'ar HaGai
  [35.2137, 31.7683], // Jerusalem
];
```

For Hebrew map labels, use Mapbox's built-in Hebrew localization:

```tsx
_map.setConfigProperty("basemap", "language", "he");
```

## Text Measurement with Hebrew Fonts

When using `measureText()` or `fitText()` with Hebrew fonts, ensure the font is fully loaded first:

```tsx
import { loadFont } from "@remotion/google-fonts/Heebo";
import { measureText, fitText } from "@remotion/layout-utils";

const { fontFamily, waitUntilDone } = loadFont("normal", {
  weights: ["400", "700"],
  subsets: ["hebrew"],
});

// Wait for Hebrew font before measuring
await waitUntilDone();

const { fontSize } = fitText({
  text: "כותרת ראשית לסרטון",
  withinWidth: 800,
  fontFamily,
  fontWeight: "bold",
});
```

Hebrew text tends to be ~20-30% wider than equivalent English text at the same font size. Account for this when setting container widths.
