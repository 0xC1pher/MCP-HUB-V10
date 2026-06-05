import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, rmSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { scanProject } from "../../../src/scan/scan-pipeline.js";

describe("scanProject", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), "ua-scan-pipe-"));
    mkdirSync(join(tmpDir, "src"), { recursive: true });
    writeFileSync(join(tmpDir, "package.json"), JSON.stringify({ name: "demo" }));
    writeFileSync(join(tmpDir, "src", "index.ts"), "export const x = 1;");
    writeFileSync(join(tmpDir, "src", "README.md"), "# Demo");
    mkdirSync(join(tmpDir, "node_modules"), { recursive: true });
    writeFileSync(join(tmpDir, "node_modules", "junk.js"), "ignored");
  });

  afterEach(() => rmSync(tmpDir, { recursive: true, force: true }));

  it("walks project and produces a graph", async () => {
    const graph = await scanProject(tmpDir);
    expect(graph).toBeDefined();
    expect(graph.project.name).toBe("demo");
    expect(graph.nodes.length).toBeGreaterThanOrEqual(3);
    const fileNames = graph.nodes.map(n => n.name);
    expect(fileNames).toContain("index.ts");
    expect(fileNames).toContain("README.md");
    expect(fileNames).toContain("package.json");
    expect(fileNames).not.toContain("junk.js");
  });

  it("returns synchronous build wrapped in promise", async () => {
    const t0 = Date.now();
    await scanProject(tmpDir);
    expect(Date.now() - t0).toBeLessThan(5000);
  });

  it("classifies README.md as document nodeType", async () => {
    const graph = await scanProject(tmpDir);
    const readme = graph.nodes.find(n => n.name === "README.md");
    expect(readme).toBeDefined();
    expect(readme?.type).toBe("document");
  });

  it("classifies package.json as config nodeType", async () => {
    const graph = await scanProject(tmpDir);
    const pkg = graph.nodes.find(n => n.name === "package.json");
    expect(pkg).toBeDefined();
    expect(pkg?.type).toBe("config");
  });

  it("classifies index.ts as file nodeType", async () => {
    const graph = await scanProject(tmpDir);
    const ts = graph.nodes.find(n => n.name === "index.ts");
    expect(ts).toBeDefined();
    expect(ts?.type).toBe("file");
  });
});
