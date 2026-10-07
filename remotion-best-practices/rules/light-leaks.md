---
name: light-leaks
description: Light leak overlay effects for Remotion using lightLeak() from @remotion/effects (the older @remotion/light-leaks package is deprecated).
metadata:
  tags: light-leaks, overlays, effects, transitions
---

## Light Leaks

This only works from Remotion 4.0.500 and up. Use `npx remotion versions` to check your Remotion version and `npx remotion upgrade` to upgrade your Remotion version.

Apply `lightLeak()` from `@remotion/effects/light-leak` to a canvas-based component such as `<Solid>` from `remotion`. Animate `progress` from `0` to `1`: the light leak reveals during the first half and retracts during the second half.

Typically used inside a `<TransitionSeries.Overlay>` to play over the cut point between two scenes. See the **transitions** rule for `<TransitionSeries>` and overlay usage.

**Do not start new work on `@remotion/light-leaks` (`<LightLeak>`).** The Remotion docs now list that package as deprecated, and the 5.0 migration guide says it gets no 5.x releases: "Replace `@remotion/light-leaks` with `lightLeak()` from `@remotion/effects`". Existing 4.x code that uses `<LightLeak>` still runs; migrate it before upgrading to 5.0.

## Prerequisites

```bash
npx remotion add @remotion/effects
```

## Light leak overlay component

Keep the `progress` calculation inline so it stays editable in Remotion Studio:

```tsx
import { lightLeak } from "@remotion/effects/light-leak";
import { interpolate, Solid, useCurrentFrame, useVideoConfig } from "remotion";

export const LightLeakOverlay: React.FC<{
  seed?: number;
  hueShift?: number;
}> = ({ seed = 0, hueShift = 0 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, height, width } = useVideoConfig();

  return (
    <Solid
      width={width}
      height={height}
      effects={[
        lightLeak({
          seed,
          hueShift,
          progress: interpolate(frame, [0, durationInFrames - 1], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }),
      ]}
    />
  );
};
```

## Basic usage with TransitionSeries

```tsx
import { TransitionSeries } from "@remotion/transitions";

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={60}>
    <SceneA />
  </TransitionSeries.Sequence>
  <TransitionSeries.Overlay durationInFrames={30}>
    <LightLeakOverlay />
  </TransitionSeries.Overlay>
  <TransitionSeries.Sequence durationInFrames={60}>
    <SceneB />
  </TransitionSeries.Sequence>
</TransitionSeries>;
```

## Rendering: WebGL needs the ANGLE renderer

`lightLeak()` needs a WebGL2 context, which the default OpenGL renderer does not provide. Without it a render fails with "Failed to acquire WebGL2 context for light leak effect". The `--blank` template this skill scaffolds does NOT set it (only the Three.js template does), so add `Config.setChromiumOpenGlRenderer("angle")` to `remotion.config.ts` or pass `--gl=angle` to `npx remotion render`, set `chromiumOptions: { gl: "angle" }` for server-side APIs (the config file does not apply to them), or choose "angle" under Advanced in the Studio render dialog. On machines without a GPU (Lambda) use `swangle`, which is the Lambda default. See https://www.remotion.dev/docs/troubleshooting/webgl2-context.

## Options of `lightLeak()`

- `progress` -- `0` to `1`. Reveals during the first half, retracts during the second half.
- `seed` -- determines the shape of the light leak pattern. Different seeds produce different patterns. Default: `0`.
- `hueShift` -- rotates the hue in degrees (`0`-`360`). Default: `0` (yellow-to-orange). `120` shifts toward green, `240` toward blue.

## Customizing the look

```tsx
// Blue-tinted light leak with a different pattern
<LightLeakOverlay seed={5} hueShift={240} />;

// Green-tinted light leak
<LightLeakOverlay seed={2} hueShift={120} />;
```

## Standalone usage

The overlay component can also be used outside of `<TransitionSeries>`, as a decorative layer in any composition. Wrap it in a `<Sequence>` so `durationInFrames` (and therefore `progress`) covers only the span you want:

```tsx
import { AbsoluteFill, Sequence } from "remotion";

const MyComp: React.FC = () => (
  <AbsoluteFill>
    <MyContent />
    <Sequence durationInFrames={60}>
      <LightLeakOverlay seed={3} />
    </Sequence>
  </AbsoluteFill>
);
```
