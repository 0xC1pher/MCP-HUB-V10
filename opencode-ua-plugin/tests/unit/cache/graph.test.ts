import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { GraphCache } from "../../../src/cache/graph";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

describe("GraphCache", () => {
  let tmpDir: string;
  let cache: GraphCache;

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), "ua-graph-"));
    cache = new GraphCache(tmpDir);
  });

  afterEach(() => rmSync(tmpDir, { recursive: true, force: true }));

  it("loadGraph returns null when missing", async () => {
    expect(await cache.loadGraph()).toBeNull();
  });

  it("saveGraph + loadGraph roundtrip", async () => {
    const g = {
      version: "1.0.0",
      project: { name: "x", languages: [], frameworks: [], description: "", analyzedAt: new Date().toISOString(), gitCommitHash: "abc" },
      nodes: [{ id: "f:a", type: "file", name: "a", summary: "" }],
      edges: [], layers: [], tour: []
    };
    await cache.saveGraph(g);
    expect(await cache.loadGraph()).toEqual(g);
  });

  it("saveMeta + loadMeta roundtrip", async () => {
    const m = { lastAnalyzedAt: new Date().toISOString(), gitCommitHash: "def", version: "1.0.0" };
    await cache.saveMeta(m);
    expect(await cache.loadMeta()).toEqual(m);
  });

  it("loadEmbeddings returns {} when missing", async () => {
    expect(await cache.loadEmbeddings()).toEqual({});
  });

  it("saveEmbeddings + loadEmbeddings roundtrip", async () => {
    await cache.saveEmbeddings({ "node:1": [0.1, 0.2, 0.3] });
    expect(await cache.loadEmbeddings()).toEqual({ "node:1": [0.1, 0.2, 0.3] });
  });
});
