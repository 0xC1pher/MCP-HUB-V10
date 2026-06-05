// Copy bin/ to dist/bin/ after tsc build.
// Cross-platform (uses node:fs cpSync with recursive).
import { cpSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const src = join(root, "bin");
const dest = join(root, "dist", "bin");

if (!existsSync(src)) {
  console.error(`[copy-bin] source not found: ${src}`);
  process.exit(1);
}

cpSync(src, dest, { recursive: true });
console.log(`[copy-bin] ${src} -> ${dest}`);
