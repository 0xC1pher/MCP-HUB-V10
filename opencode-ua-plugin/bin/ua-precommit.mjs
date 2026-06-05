#!/usr/bin/env node
// Understand-Anything pre-commit check (non-blocking).
// Runs as git pre-commit hook. Warns if cached graph is stale but NEVER blocks commit.

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { execSync } from "node:child_process";

const cacheDir = process.env.UA_CACHE_DIR ?? ".opencode/cache/ua-graph";
const metaFile = join(cacheDir, "meta.json");

function color(s, c) {
  const codes = { red: 31, yellow: 33, green: 32, cyan: 36, dim: 2, reset: 0 };
  return process.stdout.isTTY ? `\x1b[${codes[c] ?? 0}m${s}\x1b[0m` : s;
}

if (!existsSync(metaFile)) {
  console.error(color("[ua-precommit] no cache found, skipping (run ua_scan_codebase)", "dim"));
  process.exit(0);
}

let meta;
try {
  meta = JSON.parse(readFileSync(metaFile, "utf8"));
} catch (e) {
  console.error(color(`[ua-precommit] could not read meta.json: ${e.message}`, "yellow"));
  process.exit(0);
}

const lastHash = meta.lastCommitHash ?? meta?.project?.gitCommitHash;
if (!lastHash) {
  console.error(color("[ua-precommit] no commit hash in meta, skipping", "dim"));
  process.exit(0);
}

let currentHash;
try {
  currentHash = execSync("git rev-parse --short HEAD", { encoding: "utf8" }).trim();
} catch {
  console.error(color("[ua-precommit] not a git repo or git unavailable, skipping", "dim"));
  process.exit(0);
}

if (lastHash === currentHash) {
  console.error(color("[ua-precommit] cache is up-to-date", "green"));
  process.exit(0);
}

let diffCount = 0;
try {
  const diff = execSync(`git diff --name-only ${lastHash}..HEAD`, { encoding: "utf8" });
  diffCount = diff.trim().split("\n").filter(Boolean).length;
} catch {
  // ignore
}

if (diffCount > 0) {
  console.error(color(
    `[ua-precommit] cache is stale: ${diffCount} file(s) changed since last analysis (${lastHash}..${currentHash})`,
    "yellow"
  ));
  console.error(color("  refresh with /ua-refresh in OpenCode or ua_scan_codebase tool", "dim"));
  console.error(color("  (this is a warning; commit will proceed)", "dim"));
} else {
  console.error(color(`[ua-precommit] HEAD moved to ${currentHash} but no working-tree changes detected`, "dim"));
}

process.exit(0);
