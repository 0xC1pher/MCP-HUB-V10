import { describe, it, expect, vi } from "vitest";

const { mockFuzzySearch, mockSemanticSearch } = vi.hoisted(() => ({
  mockFuzzySearch: vi.fn().mockReturnValue([
    { nodeId: "file:auth", score: 0.1 }
  ]),
  mockSemanticSearch: vi.fn().mockReturnValue([
    { nodeId: "file:auth", score: 0.05 }
  ])
}));

vi.mock("@understand-anything/core", () => ({
  SearchEngine: vi.fn().mockImplementation(() => ({ search: mockFuzzySearch })),
  SemanticSearchEngine: vi.fn().mockImplementation(() => ({ search: mockSemanticSearch }))
}));

vi.mock("../../../src/cache/graph", () => ({
  GraphCache: vi.fn().mockImplementation(() => ({
    loadGraph: vi.fn().mockResolvedValue({
      nodes: [{ id: "file:auth", type: "file", name: "auth.ts", summary: "auth logic", tags: [] }]
    }),
    loadEmbeddings: vi.fn().mockResolvedValue({})
  }))
}));

import { uaSearchSemantic } from "../../../src/tools/search-semantic";

describe("ua_search_semantic", () => {
  it("falls back to fuzzy when no embeddings", async () => {
    const r: any = await uaSearchSemantic.execute(
      { query: "auth", limit: 5 } as any,
      { directory: "/tmp" } as any
    );
    expect(r.mode).toBe("fuzzy");
    expect(r.results.length).toBeGreaterThan(0);
    expect(r.results[0]).toMatchObject({ id: "file:auth", name: "auth.ts", score: 0.1 });
  });

  it("reports semantic mode when embeddings present", async () => {
    const { GraphCache } = await import("../../../src/cache/graph");
    (GraphCache as any).mockImplementation(() => ({
      loadGraph: vi.fn().mockResolvedValue({
        nodes: [{ id: "file:auth", type: "file", name: "auth.ts", summary: "auth logic", tags: [] }]
      }),
      loadEmbeddings: vi.fn().mockResolvedValue({ "file:auth": [0.1, 0.2, 0.3] })
    }));
    const r: any = await uaSearchSemantic.execute(
      { query: "auth", limit: 5 } as any,
      { directory: "/tmp" } as any
    );
    expect(r.mode).toBe("semantic");
    expect(r.results.length).toBeGreaterThan(0);
  });

  it("returns empty results when no graph", async () => {
    const { GraphCache } = await import("../../../src/cache/graph");
    (GraphCache as any).mockImplementation(() => ({
      loadGraph: vi.fn().mockResolvedValue(null),
      loadEmbeddings: vi.fn().mockResolvedValue({})
    }));
    const r: any = await uaSearchSemantic.execute(
      { query: "x", limit: 5 } as any,
      { directory: "/tmp" } as any
    );
    expect(r).toMatchObject({ mode: "fuzzy", results: [] });
  });
});
