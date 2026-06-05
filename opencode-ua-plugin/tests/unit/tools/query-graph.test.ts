import { describe, it, expect, vi } from "vitest";

const mockGraph = {
  nodes: [
    { id: "file:a", type: "file", name: "auth.ts", summary: "auth logic", tags: [] },
    { id: "file:b", type: "file", name: "login.ts", summary: "login flow", tags: [] },
    { id: "class:x", type: "class", name: "UserService", summary: "user ops", tags: [] }
  ],
  edges: [],
  layers: [{ id: "api", name: "API", nodeIds: ["file:a", "file:b"] }]
};

vi.mock("../../../src/cache/graph", () => ({
  GraphCache: vi.fn().mockImplementation(() => ({
    loadGraph: vi.fn().mockResolvedValue(mockGraph)
  }))
}));

import { uaQueryGraph } from "../../../src/tools/query-graph";

describe("ua_query_graph", () => {
  it("filters by node_type=file", async () => {
    const r: any = await uaQueryGraph.execute(
      { query: "auth", node_type: "file" } as any,
      { directory: "/tmp" } as any
    );
    expect(r.nodes.length).toBe(1);
    expect(r.nodes[0].name).toBe("auth.ts");
  });

  it("filters by layer=api", async () => {
    const r: any = await uaQueryGraph.execute(
      { query: "auth", layer: "api" } as any,
      { directory: "/tmp" } as any
    );
    expect(r.nodes.length).toBe(1);
    expect(r.nodes[0].name).toBe("auth.ts");
  });

  it("returns empty on missing layer", async () => {
    const r: any = await uaQueryGraph.execute(
      { query: "x", layer: "nope" } as any,
      { directory: "/tmp" } as any
    );
    expect(r.nodes).toEqual([]);
  });

  it("returns empty when no graph", async () => {
    const { GraphCache } = await import("../../../src/cache/graph");
    (GraphCache as any).mockImplementation(() => ({
      loadGraph: vi.fn().mockResolvedValue(null)
    }));
    const r: any = await uaQueryGraph.execute(
      { query: "x" } as any,
      { directory: "/tmp" } as any
    );
    expect(r.nodes).toEqual([]);
  });
});
