#!/usr/bin/env node
// Regression cases for scripts/contrast-report.mjs (skills-il patches).
//
// Each case writes a tiny 1080x1920 composition to a temp dir, runs the
// report on it, and asserts the AA verdict per element. Expected ratios were
// cross-checked against `npx hyperframes check` on HyperFrames 0.8.138.
//
// Usage (from a HyperFrames project root, so @hyperframes/* and sharp resolve,
// or with HYPERFRAMES_SKILL_BOOTSTRAP_DEPS=1):
//   node <skill-dir>/scripts/test/contrast-report.regression.mjs
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), "..", "contrast-report.mjs");

const BODY = `<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1080" data-height="1920">
<p class="t" id="lt">light grey</p><p class="t" id="dk">dark text</p><p class="t pill" id="pill">pill</p><p class="t" id="off">offscreen</p>
<div class="grp"><span id="kara">karaoke</span></div><p class="t" id="ok">oklch light</p><p class="t" id="a14">fourteen pt bold</p><p class="t" id="b18">eighteen px bold</p>
</div>
<script>const tl=gsap.timeline({paused:true});tl.to("#root",{opacity:1,duration:2},0);window.__timelines["main"]=tl;</script>`;

const BASE = `*{margin:0;padding:0;box-sizing:border-box} html,body{width:1080px;height:1920px;overflow:hidden}
#root{width:100%;height:100%;position:relative;font-family:Inter,sans-serif}
.t{position:absolute;left:100px;font-size:40px}
#lt{top:100px;color:#ccc} #dk{top:200px;color:#222}
.pill{top:300px;background:#1a3fbf;color:#1a1a1a;padding:20px 40px}
#off{top:500px;left:1500px;color:#000}
.grp{position:absolute;top:600px;left:100px;opacity:0} .grp span{color:#eee;font-size:40px}
#ok{top:700px;color:oklch(0.9 0 0)}
#a14{top:800px;font-size:14pt;font-weight:700;color:#767676}
#b18{top:900px;font-size:18px;font-weight:700;color:#767676}`;

const page = (bg, bodyAttr = "") => `<!doctype html><html lang="en"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>${BASE}\n${bg}</style></head><body ${bodyAttr}>${BODY}</body></html>`;

// true = passes AA, false = fails AA, "unmeasured", "absent" (must not be reported)
const WHITE = { lt: false, dk: true, pill: false, ok: false, a14: true, b18: true, off: "absent", kara: "absent" };
const CASES = [
  { name: "A solid body bg", html: page("body{background:#fff}"), expect: WHITE, exit: 1 },
  { name: "B gradient body bg", html: page("body{background:linear-gradient(#fff,#f4f4f4)}"), expect: { ...WHITE, b18: false }, exit: 1 },
  { name: "C html #000 under rgba body", html: page("html{background:#000} body{background:rgba(255,255,255,0.5)}"), expect: { lt: false, dk: true, pill: false }, exit: 1 },
  { name: "D body bg via class", html: page(".light{background:#fff}", 'class="light"'), expect: WHITE, exit: 1 },
  { name: "E bg on html only", html: page("html{background:#fff}"), expect: WHITE, exit: 1 },
  { name: "F color plus background-image", html: page("body{background:#fff url(data:image/gif;base64,R0lGODlhAQABAAAAACw=)}"), expect: WHITE, exit: 1 },
  { name: "H no page background at all", html: page(""), expect: { lt: "unmeasured", dk: "unmeasured", pill: false }, exit: 1 },
];

let failures = 0;
for (const c of CASES) {
  const dir = mkdtempSync(join(tmpdir(), "hf-contrast-"));
  try {
    writeFileSync(join(dir, "index.html"), c.html);
    // Run the report in-process: a fresh module instance per case (query
    // string), with argv set for it. No child process is spawned.
    process.argv = [process.argv[0], SCRIPT, dir, "--width", "1080", "--height", "1920", "--samples", "1", "--out", join(dir, "out")];
    process.exitCode = 0;
    await import(`${pathToFileURL(SCRIPT).href}?case=${encodeURIComponent(c.name)}`);
    const r = { status: process.exitCode ?? 0 };
    const report = JSON.parse(readFileSync(join(dir, "out", "contrast-report.json"), "utf8"));
    const byId = Object.fromEntries(report.entries.map((e) => [e.selector.replace(/^#/, ""), e]));
    const problems = [];
    if (r.status !== c.exit) problems.push(`exit ${r.status}, expected ${c.exit}`);
    for (const [id, want] of Object.entries(c.expect)) {
      const e = byId[id];
      const got = !e ? "absent" : e.unmeasured ? "unmeasured" : e.wcagAA;
      if (got !== want) problems.push(`#${id}: got ${got}${e && e.ratio ? ` (${e.ratio}:1)` : ""}, expected ${want}`);
    }
    console.log(`${problems.length ? "FAIL" : "ok  "} ${c.name}${problems.length ? "\n     " + problems.join("\n     ") : ""}`);
    failures += problems.length ? 1 : 0;
  } catch (err) {
    failures++;
    console.log(`FAIL ${c.name}: ${err.message}`);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}
process.exitCode = failures ? 1 : 0;
console.log(failures ? `${failures} case(s) failed` : "all cases passed");
