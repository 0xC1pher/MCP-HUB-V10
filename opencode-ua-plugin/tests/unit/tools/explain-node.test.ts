import { describe, it, expect, vi } from "vitest";

vi.mock("../../../src/cache/graph", () => ({
  GraphCache: vi.fn().mockImplementation(() => ({
    loadGraph: vi.fn().mockResolvedValue({
      nodes: [
        { id: "file:auth", type: "file", name: "auth.ts", summary: "auth logic", tags: ["sec"] }
      ],
      edges: [
        { source: "file:session", target: "file:auth", type: "calls" },
        { source: "file:auth", target: "file:login", type: "imports" }
      ]
    })
  }))
}));

import { uaExplainNode } from "../../../src/tools/explain-node";

describe("ua_explain_node", () => {
  it("returns node + incoming + outgoing", async () => {
    const r: any = await uaExplainNode.execute(
      { node_id: "file:auth" } as any,
      { directory: "/tmp" } as any
    );
    expect(r.node.name).toBe("auth.ts");
    expect(r.incoming.length).toBe(1);
    expect(r.incoming[0]).toMatchObject({ from: "file:session", type: "calls" });
    expect(r.outgoing.length).toBe(1);
    expect(r.outgoing[0]).toMatchObject({ to: "file:login", type: "imports" });
  });

  it("returns not_found for missing node", async () => {
    const r: any = await uaExplainNode.execute(
      { node_id: "file:nope" } as any,
      { directory: "/tmp" } as any
    );
    expect(r.error).toBe("not_found");
  });

  it("returns no_graph when no cache", async () => {
    const { GraphCache } = await import("../../../src/cache/graph");
    (GraphCache as any).mockImplementation(() => ({
      loadGraph: vi.fn().mockResolvedValue(null)
    }));
    const r: any = await uaExplainNode.execute(
      { node_id: "file:x" } as any,
      { directory: "/tmp" } as any
    );
    expect(r.error).toBe("no_graph");
  });
});
