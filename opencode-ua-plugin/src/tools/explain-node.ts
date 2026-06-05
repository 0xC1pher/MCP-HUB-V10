import { tool } from "@opencode-ai/plugin";
import { GraphCache } from "../cache/graph.js";

const zod = tool.schema;

export const uaExplainNode = Object.assign(
  tool({
    description:
      "Explain a specific node (file, function, class, etc.) with its incoming and outgoing edges.",
    args: {
      node_id: zod.string()
        .describe('Node ID like "file:src/auth.ts" or "class:src/auth.ts:UserService"')
    },
    async execute(args, ctx): Promise<any> {
      const cache = new GraphCache(ctx.directory);
      const graph = await cache.loadGraph();
      if (!graph) return { incoming: [], outgoing: [], error: "no_graph" };

      const node = graph.nodes.find((n) => n.id === args.node_id);
      if (!node) return { incoming: [], outgoing: [], error: "not_found" };

      return {
        node: {
          id: node.id,
          name: node.name,
          summary: node.summary ?? "",
          type: node.type,
          complexity: node.complexity,
          tags: node.tags ?? []
        },
        incoming: graph.edges
          .filter((e) => e.target === args.node_id)
          .map((e) => ({ from: e.source, type: e.type })),
        outgoing: graph.edges
          .filter((e) => e.source === args.node_id)
          .map((e) => ({ to: e.target, type: e.type }))
      };
    }
  }),
  { name: "ua_explain_node" }
) as any;
