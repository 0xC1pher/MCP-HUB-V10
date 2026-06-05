import { describe, it, expect, vi } from "vitest";

const { mockGetChangedFiles } = vi.hoisted(() => ({
  mockGetChangedFiles: vi.fn().mockResolvedValue(["src/auth.ts"])
}));

vi.mock("@understand-anything/core", () => ({
  getChangedFiles: mockGetChangedFiles
}));

vi.mock("../../../src/cache/graph", () => ({
  GraphCache: vi.fn().mockImplementation(() => ({
    loadGraph: vi.fn().mockResolvedValue({
      project: { gitCommitHash: "abc123" },
      edges: [
        { source: "file:src/session.ts", target: "file:src/auth.ts", type: "calls" },
        { source: "file:src/auth.ts", target: "file:src/login.ts", type: "imports" }
      ]
    })
  }))
}));

import { uaDiffImpact } from "../../../src/tools/diff-impact";

describe("ua_diff_impact", () => {
  it("returns affected callers from graph edges", async () => {
    const r: any = await uaDiffImpact.execute({} as any, { directory: "/tmp/proj" } as any);
    expect(r.changedFiles).toEqual(["src/auth.ts"]);
    expect(r.directCallers).toContain("file:src/session.ts");
    expect(r.impactLevel).toBe("STRUCTURAL");
    expect(r.affectedFiles.length).toBeGreaterThan(0);
  });

  it("returns NONE for empty changes", async () => {
    mockGetChangedFiles.mockResolvedValueOnce([]);
    const r: any = await uaDiffImpact.execute({} as any, { directory: "/tmp" } as any);
    expect(r.impactLevel).toBe("NONE");
    expect(r.changedFiles).toEqual([]);
  });
});
