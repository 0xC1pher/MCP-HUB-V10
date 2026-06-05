import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, rmSync, cpSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { uaScanCodebase } from "../../src/tools/scan-codebase.js";
import { GraphCache } from "../../src/cache/graph.js";

describe("scan_codebase E2E", () => {
  let tmpDir: string;
  const fixturePath = join(__dirname, "../fixtures/sample-node-project");

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), "ua-e2e-"));
    cpSync(fixturePath, tmpDir, { recursive: true });
  });
  afterEach(() => rmSync(tmpDir, { recursive: true, force: true }));

  it("scans fixture and writes cache", async () => {
    const r: any = await uaScanCodebase.execute(
      { force_full: true } as any,
      { directory: tmpDir } as any
    );
    expect(r).toBeDefined();
    const meta = r.metadata ?? r;
    expect(meta.success).toBe(true);
    expect(meta.nodeCount).toBeGreaterThan(0);
    const cache = new GraphCache(tmpDir);
    const g = await cache.loadGraph();
    expect(g).not.toBeNull();
    const metaFile = await cache.loadMeta();
    expect(metaFile?.gitCommitHash).toBeTruthy();
  }, 60000);

  it("second call is cached", async () => {
    await uaScanCodebase.execute({ force_full: true } as any, { directory: tmpDir } as any);
    const r2: any = await uaScanCodebase.execute({ force_full: false } as any, { directory: tmpDir } as any);
    const meta = r2.metadata ?? r2;
    expect(meta.cached).toBe(true);
  }, 60000);
});
