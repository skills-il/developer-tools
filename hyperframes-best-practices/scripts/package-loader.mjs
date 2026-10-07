// package-loader: resolve the helper packages these scripts need
// (@hyperframes/producer, @hyperframes/core, sharp) from the working directory
// first, then from node_modules beside the script, $HYPERFRAMES_SKILL_NODE_MODULES
// and PATH-adjacent node_modules.
//
// Vendored from heygen-com/hyperframes skills/*/scripts @ d94708e (Apache-2.0).
// skills-il change: upstream could bootstrap missing packages with a temporary
// `npm install`. This copy never spawns a process; when a package is missing it
// stops and prints the install command for you to run.
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { basename, delimiter, dirname, join, parse, resolve, win32 as win32Path } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const VERSION_OVERRIDE_ENV = "HYPERFRAMES_SKILL_PKG_VERSION";
const NODE_MODULES_ENV = "HYPERFRAMES_SKILL_NODE_MODULES";

export async function importPackagesOrBootstrap(packageNames, options = {}) {
  const entries = new Map();
  const missing = [];

  for (const packageName of packageNames) {
    const entry = resolvePackageEntry(packageName);
    if (entry) entries.set(packageName, entry);
    else missing.push(packageName);
  }

  // skills-il: the upstream loader could spawn a temporary `npm install`.
  // This copy never spawns a process; it prints the install command instead.
  if (missing.length > 0) {
    const npmPackages = options.npmPackages ?? missing;
    throw new Error(
      [
        `Could not resolve required package(s): ${missing.join(", ")}`,
        "Run this from your HyperFrames project root, then re-run the script from there:",
        `  npm install --save-dev ${npmPackages.map(shellQuote).join(" ")}`,
      ].join("\n"),
    );
  }

  const modules = {};
  for (const [packageName, entry] of entries) {
    modules[packageName] = await import(pathToFileURL(entry).href);
  }
  return modules;
}

export async function bundleCompositionForCapture(compiler, projectDir) {
  const compiledDir = mkdtempSync(join(tmpdir(), "hyperframes-skill-bundle-"));
  try {
    const html = await compiler.bundleToSingleHtml(projectDir);
    writeFileSync(join(compiledDir, "index.html"), html);
    return {
      compiledDir,
      cleanup() {
        rmSync(compiledDir, { recursive: true, force: true });
      },
    };
  } catch (error) {
    rmSync(compiledDir, { recursive: true, force: true });
    throw error;
  }
}

// ── Transient-init retry ─────────────────────────────────────────────────────
// Frozen snapshot of the engine's TRANSIENT_BROWSER_ERROR_PATTERNS (see
// packages/engine frameCapture.ts), used only when the imported
// @hyperframes/producer predates the isTransientBrowserError re-export. The
// last pattern is the load-bearing one for modular projects: sub-composition
// timelines register asynchronously, so a first init attempt can time out as
// "zero duration / Runtime ready: false" on a valid project.
const FALLBACK_TRANSIENT_PATTERNS = [
  /Navigating frame was detached/i,
  /Target closed/i,
  /Session closed/i,
  /browser has disconnected/i,
  /Page crashed/i,
  /Execution context was destroyed/i,
  /Cannot find context with specified id/i,
  /Failed to launch the browser process/i,
  /Navigation timeout of \d+ ms exceeded/i,
  /ECONNREFUSED/i,
  /net::ERR_NETWORK_CHANGED/i,
  /Composition has zero duration[\s\S]*Runtime ready: false/,
];

/**
 * Create + initialize a capture session with the canonical transient-init
 * retry/cleanup the render pipeline uses (see probeStage in
 * @hyperframes/producer): on a transient failure, close the crashed session
 * and retry ONCE with a fresh browser. Without this, a standalone helper
 * false-fails valid modular projects whose sub-composition timelines land a
 * beat after the first readiness deadline ("zero duration" with
 * "Runtime ready: false").
 *
 * `producer` is the imported @hyperframes/producer namespace;
 * `createSession` is a factory returning a fresh (uninitialized) session.
 * Non-transient init failures (e.g. the "Runtime ready: true" zero-duration
 * fast-fail, a genuine authoring bug) still throw on the first attempt.
 */
export async function initializeSessionWithRetry(producer, createSession, options = {}) {
  const maxAttempts = options.maxAttempts ?? 2;
  const log = options.log ?? ((message) => console.error(message));
  const isTransient =
    typeof producer.isTransientBrowserError === "function"
      ? producer.isTransientBrowserError
      : (err) => {
          const message = err instanceof Error ? err.message : String(err);
          return FALLBACK_TRANSIENT_PATTERNS.some((pattern) => pattern.test(message));
        };

  for (let attempt = 1; ; attempt++) {
    const session = await createSession();
    try {
      await producer.initializeSession(session);
      return session;
    } catch (error) {
      await producer.closeCaptureSession(session).catch(() => {});
      if (attempt >= maxAttempts || !isTransient(error)) throw error;
      log(
        `transient browser-init failure (attempt ${attempt}/${maxAttempts}): ${
          error instanceof Error ? error.message : String(error)
        }`,
      );
      log("retrying with a fresh browser session...");
    }
  }
}

export function hyperframesPackageSpec(packageName) {
  const override = process.env[VERSION_OVERRIDE_ENV]?.trim();
  if (override) return `${packageName}@${override}`;

  const version = readBundledHyperframesVersion();
  if (version) return `${packageName}@${version}`;

  // Global skill installs have no hyperframes package.json
  // in their ancestor chain, so the bundled version is unknowable. Fall back to
  // @latest instead of throwing: already-installed packages still import, and a
  // bootstrap install can still proceed (@latest satisfies the pinned-spec guard).
  return `${packageName}@latest`;
}

function resolvePackageEntry(packageName) {
  const bases = [process.cwd(), HERE, ...envNodeModulesDirs(), ...nodeModulesDirsFromPath()];
  const { rootName, subpath } = splitPackageSpecifier(packageName);

  const seen = new Set();
  for (const base of bases) {
    const normalized = resolve(base);
    if (seen.has(normalized)) continue;
    seen.add(normalized);

    try {
      return createRequire(join(normalized, "__hyperframes_skill_loader__.cjs")).resolve(
        packageName,
      );
    } catch {
      const packageDir = findPackageDir(normalized, rootName);
      const packageEntry = packageDir ? readPackageEntry(packageDir, subpath) : null;
      if (packageEntry) return packageEntry;
    }
  }

  return null;
}

function splitPackageSpecifier(packageName) {
  const segments = packageName.split("/");
  const rootLength = packageName.startsWith("@") ? 2 : 1;
  return {
    rootName: segments.slice(0, rootLength).join("/"),
    subpath: segments.slice(rootLength).join("/"),
  };
}

function readBundledHyperframesVersion() {
  for (const ancestor of ancestors(HERE)) {
    const directVersion = readPackageVersion(join(ancestor, "package.json"));
    if (directVersion) return directVersion;

    const monorepoCliVersion = readPackageVersion(
      join(ancestor, "packages", "cli", "package.json"),
    );
    if (monorepoCliVersion) return monorepoCliVersion;
  }
  return null;
}

function readPackageVersion(packageJsonPath) {
  try {
    const manifest = JSON.parse(readFileSync(packageJsonPath, "utf8"));
    if (manifest.name === "hyperframes" || manifest.name === "@hyperframes/cli") {
      return typeof manifest.version === "string" ? manifest.version : null;
    }
  } catch {
    // Keep searching ancestor package manifests.
  }
  return null;
}

function envNodeModulesDirs() {
  return (process.env[NODE_MODULES_ENV] ?? "").split(delimiter).filter(Boolean);
}

function nodeModulesDirsFromPath() {
  const dirs = [];
  for (const entry of (process.env.PATH ?? "").split(delimiter)) {
    if (!entry.endsWith(`${join("node_modules", ".bin")}`)) continue;
    dirs.push(dirname(entry));
  }
  return dirs;
}

function findPackageDir(base, packageName) {
  const packageSegments = packageName.split("/");
  const roots =
    basename(base) === "node_modules"
      ? [base]
      : ancestors(base).map((ancestor) => join(ancestor, "node_modules"));

  for (const root of roots) {
    const packageDir = join(root, ...packageSegments);
    if (existsSync(join(packageDir, "package.json"))) return packageDir;
  }
  return null;
}

function readPackageEntry(packageDir, subpath = "") {
  try {
    const manifest = JSON.parse(readFileSync(join(packageDir, "package.json"), "utf8"));
    const requestedExport = subpath ? manifest.exports?.[`./${subpath}`] : manifest.exports;
    const entry =
      exportEntry(requestedExport) ??
      (!subpath ? (manifest.module ?? manifest.main ?? "index.js") : null);
    if (!entry) return null;
    const entryPath = join(packageDir, entry);
    return existsSync(entryPath) ? entryPath : null;
  } catch {
    return null;
  }
}

function exportEntry(exports) {
  const root =
    typeof exports === "object" && exports !== null ? (exports["."] ?? exports) : exports;
  if (typeof root === "string") return root;
  if (typeof root !== "object" || root === null) return null;
  if (typeof root.import === "string") return root.import;
  if (typeof root.default === "string") return root.default;
  if (typeof root.node === "string") return root.node;
  if (typeof root.node === "object" && root.node !== null) {
    return root.node.import ?? root.node.default ?? null;
  }
  return null;
}

function assertPinnedPackageSpecs(packageSpecs) {
  const unpinned = packageSpecs.filter((spec) => !hasVersionSpec(spec));
  if (unpinned.length === 0) return;
  throw new Error(
    [
      `Refusing to bootstrap unpinned package spec(s): ${unpinned.join(", ")}`,
      "Pass pinned npm package specs, for example:",
      `  ${packageSpecs.map((spec) => (hasVersionSpec(spec) ? spec : `${spec}@<version>`)).join(" ")}`,
    ].join("\n"),
  );
}

function hasVersionSpec(packageSpec) {
  if (packageSpec.startsWith("@")) {
    const slash = packageSpec.indexOf("/");
    return slash !== -1 && packageSpec.indexOf("@", slash + 1) !== -1;
  }
  return packageSpec.includes("@");
}


function ancestors(start) {
  const dirs = [];
  let current = resolve(start);
  const root = parse(current).root;
  while (current && current !== root) {
    dirs.push(current);
    current = dirname(current);
  }
  dirs.push(root);
  return dirs;
}



function shellQuote(value) {
  if (/^[A-Za-z0-9_./:@=-]+$/.test(value)) return value;
  return `'${value.replace(/'/g, "'\\''")}'`;
}
