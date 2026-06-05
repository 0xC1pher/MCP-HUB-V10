#!/usr/bin/env node
// Install UA pre-commit hook into the current repo.

import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const hookPath = join(process.cwd(), ".git", "hooks", "pre-commit");
const thisScript = resolve(__dirname, "ua-precommit.mjs");
const hookContent = `#!/usr/bin/env node
// Installed by opencode-ua-plugin via bin/ua-install-hooks.mjs
// Auto-runs the UA pre-commit staleness check (non-blocking).
import("${thisScript.replace(/\\\\/g, "/")}")
  .catch(err => { console.error("[ua-precommit] hook error:", err.message); process.exit(0); });
`;

if (existsSync(hookPath)) {
  const existing = readFileSync(hookPath, "utf8");
  if (existing.includes("opencode-ua-plugin")) {
    console.log("[ua-install-hooks] hook already installed (idempotent)");
    process.exit(0);
  }
  console.log("[ua-install-hooks] .git/hooks/pre-commit already exists and is not from us.");
  console.log("  refusing to overwrite. Inspect it manually if you want to chain hooks.");
  process.exit(1);
}

mkdirSync(dirname(hookPath), { recursive: true });
writeFileSync(hookPath, hookContent, { mode: 0o755 });
console.log("[ua-install-hooks] installed .git/hooks/pre-commit");
console.log("  (uninstall with: rm .git/hooks/pre-commit)");
