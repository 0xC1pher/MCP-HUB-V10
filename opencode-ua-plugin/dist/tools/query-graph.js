import { tool } from "@opencode-ai/plugin";
import { GraphCache } from "../cache/graph.js";
const zod = tool.schema;
const NODE_TYPE_VALUES = [
    "file", "function", "class", "module",
    "config", "service", "endpoint"
];
export const uaQueryGraph = Object.assign(tool({
    description: "Query the knowledge graph. Filter by node type and/or layer. " +
        "Substring match (case-insensitive) on name and summary.",
    args: {
        query: zod.string().describe("Search query — substring matched against node name and summary"),
        node_type: zod.enum(NODE_TYPE_VALUES).optional()
            .describe("Filter to nodes of this type"),
        layer: zod.string().optional()
            .describe("Filter to nodes in this layer (by id or name)"),
        limit: zod.number().int().positive().default(20)
    },
    async execute(args, ctx) {
        const cache = new GraphCache(ctx.directory);
        const graph = await cache.loadGraph();
        if (!graph)
            return { nodes: [], totalMatched: 0 };
        let candidates = graph.nodes;
        if (args.node_type) {
            candidates = candidates.filter((n) => n.type === args.node_type);
        }
        if (args.layer) {
            const layer = graph.layers.find((l) => l.id === args.layer || l.name === args.layer);
            if (!layer)
                return { nodes: [], totalMatched: 0 };
            candidates = candidates.filter((n) => layer.nodeIds.includes(n.id));
        }
        const q = args.query.toLowerCase();
        const matched = candidates.filter((n) => n.name.toLowerCase().includes(q) ||
            (n.summary ?? "").toLowerCase().includes(q));
        return {
            nodes: matched.slice(0, args.limit).map((n) => ({
                id: n.id,
                name: n.name,
                summary: n.summary ?? "",
                type: n.type
            })),
            totalMatched: matched.length
        };
    }
}), { name: "ua_query_graph" });
