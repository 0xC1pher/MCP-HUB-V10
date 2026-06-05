import { tool } from "@opencode-ai/plugin";
import { GraphCache } from "../cache/graph.js";
import { scanProject } from "../scan/scan-pipeline.js";
const zod = tool.schema;
export const uaScanCodebase = Object.assign(tool({
    description: "Analyze the project and build/update the knowledge graph. " +
        "Returns counts and a cached flag. Safe to call repeatedly.",
    args: {
        force_full: zod.boolean().optional()
            .describe("Force a full re-scan even if cache is fresh")
    },
    async execute(args, ctx) {
        const start = Date.now();
        const cache = new GraphCache(ctx.directory);
        if (!args.force_full) {
            const meta = await cache.loadMeta();
            const graph = await cache.loadGraph();
            if (meta && graph) {
                return {
                    success: true,
                    nodeCount: graph.nodes.length,
                    edgeCount: graph.edges.length,
                    layerCount: graph.layers.length,
                    durationMs: Date.now() - start,
                    cached: true
                };
            }
        }
        const graph = await scanProject(ctx.directory);
        await cache.saveGraph(graph);
        await cache.saveMeta({
            lastAnalyzedAt: new Date().toISOString(),
            gitCommitHash: graph.project.gitCommitHash,
            version: graph.version
        });
        return {
            success: true,
            nodeCount: graph.nodes.length,
            edgeCount: graph.edges.length,
            layerCount: graph.layers.length,
            durationMs: Date.now() - start,
            cached: false
        };
    }
}), { name: "ua_scan_codebase" });
