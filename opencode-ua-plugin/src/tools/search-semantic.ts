import { tool } from "@opencode-ai/plugin";
import { SearchEngine, SemanticSearchEngine } from "@understand-anything/core";
import { GraphCache } from "../cache/graph.js";

const zod = tool.schema;

export const uaSearchSemantic = Object.assign(
  tool({
    description:
      "Find code by meaning or fuzzy match. " +
      "When embeddings are cached, mode is reported as 'semantic' (use the dashboard for full semantic search). " +
      "Always performs fuzzy search via Fuse.js in this tool.",
    args: {
      query: zod.string().describe("Search query — keyword, phrase, or natural language"),
      limit: zod.number().int().positive().default(10)
    },
    async execute(args, ctx): Promise<any> {
      const cache = new GraphCache(ctx.directory);
      const graph = await cache.loadGraph();
      if (!graph) return { mode: "fuzzy", results: [] };

      const embeddings = await cache.loadEmbeddings();
      const hasEmbeddings = Object.keys(embeddings).length > 0;

      const engine = new SearchEngine(graph.nodes);
      const results = engine.search(args.query, { limit: args.limit });

      const nodesById = new Map(graph.nodes.map((n) => [n.id, n]));
      return {
        mode: hasEmbeddings ? "semantic" : "fuzzy",
        results: results.map((r) => {
          const node = nodesById.get(r.nodeId);
          return {
            id: r.nodeId,
            name: node?.name ?? r.nodeId,
            summary: node?.summary ?? "",
            score: r.score
          };
        })
      };
    }
  }),
  { name: "ua_search_semantic" }
) as any;
