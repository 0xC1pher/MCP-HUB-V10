import { describe, it, expect, vi } from "vitest";

vi.mock("../../../src/scan/scan-pipeline", () => ({
  scanProject: vi.fn().mockResolvedValue({
    version: "1.0.0",
    project: { name: "t", languages: ["ts"], frameworks: [], description: "", analyzedAt: "2026-06-04T00:00:00Z", gitCommitHash: "abc" },
    nodes: [{ id: "f:a", type: "file", name: "a", summary: "" }],
    edges: [], layers: [], tour: []
  })
}));

vi.mock("../../../src/cache/graph", () => ({
  GraphCache: vi.fn().mockImplementation(() => ({
    loadMeta: vi.fn().mockResolvedValue(null),
    loadGraph: vi.fn().mockResolvedValue(null),
    saveGraph: vi.fn(),
    saveMeta: vi.fn()
  }))
}));

import { uaScanCodebase } from "../../../src/tools/scan-codebase";

describe("ua_scan_codebase", () => {
  it("name and description present", () => {
    expect(uaScanCodebase.name).toBe("ua_scan_codebase");
    expect(uaScanCodebase.description).toContain("knowledge graph");
  });

  it("returns scan result on cold cache", async () => {
    const r: any = await uaScanCodebase.execute({ projectRoot: "/tmp" } as any, { directory: "/tmp" } as any);
    expect(r).toMatchObject({ success: true, nodeCount: 1, cached: false });
  });

  it("returns cached result on warm cache", async () => {
    const { GraphCache } = await import("../../../src/cache/graph");
    (GraphCache as any).mockImplementation(() => ({
      loadMeta: vi.fn().mockResolvedValue({ lastAnalyzedAt: "x", gitCommitHash: "y", version: "1" }),
      loadGraph: vi.fn().mockResolvedValue({ nodes: [{}, {}, {}], edges: [{}], layers: [{}] })
    }));
    const r: any = await uaScanCodebase.execute({ projectRoot: "/tmp" } as any, { directory: "/tmp" } as any);
    expect(r).toMatchObject({ nodeCount: 3, cached: true });
  });
});
