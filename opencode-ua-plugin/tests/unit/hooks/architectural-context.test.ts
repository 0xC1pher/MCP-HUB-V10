import { describe, it, expect, vi, beforeEach } from "vitest";

const { mockLoadGraph } = vi.hoisted(() => ({
  mockLoadGraph: vi.fn()
}));

vi.mock("../../../src/cache/graph", () => ({
  GraphCache: vi.fn().mockImplementation(() => ({
    loadGraph: mockLoadGraph
  }))
}));

import { buildArchitecturalContext } from "../../../src/hooks/architectural-context.js";

const graph = {
  version: "1.0.0",
  project: {
    name: "test-proj",
    languages: ["TypeScript", "Python"],
    frameworks: ["Bun", "Vitest"],
    description: "Test project for UA plugin",
    analyzedAt: "2026-06-05T00:00:00Z",
    gitCommitHash: "abc1234"
  },
  nodes: [
    { id: "file:src/index.ts", type: "file", name: "src/index.ts", layer: "core", summary: "Entry point" },
    { id: "file:src/auth.ts", type: "file", name: "src/auth.ts", layer: "core", summary: "Auth flow" },
    { id: "file:src/api/login.ts", type: "file", name: "src/api/login.ts", layer: "api", summary: "Login endpoint" },
    { id: "file:src/db/conn.ts", type: "file", name: "src/db/conn.ts", layer: "data", summary: "DB connection" },
    { id: "config:tsconfig.json", type: "config", name: "tsconfig.json", layer: "config", summary: "TypeScript config" }
  ],
  edges: [],
  layers: [
    { id: "core", name: "core", description: "Core domain", nodeIds: ["file:src/index.ts", "file:src/auth.ts"] },
    { id: "api", name: "api", description: "API surface", nodeIds: ["file:src/api/login.ts"] },
    { id: "data", name: "data", description: "Data layer", nodeIds: ["file:src/db/conn.ts"] },
    { id: "config", name: "config", description: "Configuration", nodeIds: ["config:tsconfig.json"] }
  ]
};

describe("buildArchitecturalContext", () => {
  beforeEach(() => mockLoadGraph.mockReset());

  it("returns null when no graph", async () => {
    mockLoadGraph.mockResolvedValue(null);
    const ctx = await buildArchitecturalContext("/tmp/nonexistent");
    expect(ctx).toBeNull();
  });

  it("builds structured context from real graph", async () => {
    mockLoadGraph.mockResolvedValue(graph);
    const ctx = await buildArchitecturalContext("/tmp");
    expect(ctx).not.toBeNull();
    expect(ctx!.project).toBe("test-proj");
    expect(ctx!.languages).toContain("TypeScript");
    expect(ctx!.frameworks).toContain("Bun");
    expect(ctx!.description).toBe("Test project for UA plugin");
    expect(ctx!.layers.length).toBe(4);
    expect(ctx!.commit).toBe("abc1234");
    expect(ctx!.rendered).toContain("test-proj");
    expect(ctx!.rendered).toContain("Core");
    expect(ctx!.rendered).toContain("Auth flow");
  });

  it("respects token budget", async () => {
    mockLoadGraph.mockResolvedValue(graph);
    const ctx = await buildArchitecturalContext("/tmp", { maxTokens: 30 });
    expect(ctx!.rendered.length).toBeLessThan(150);
  });

  it("truncates long layer lists", async () => {
    const manyNodesGraph = {
      ...graph,
      layers: [
        { id: "ui", name: "ui", description: "UI layer", nodeIds: Array.from({ length: 30 }, (_, i) => `file:src/ui/${i}.tsx`) }
      ]
    };
    mockLoadGraph.mockResolvedValue(manyNodesGraph);
    const ctx = await buildArchitecturalContext("/tmp", { maxNodesPerLayer: 5 });
    expect(ctx!.rendered).toContain("(25 more)");
  });
});
