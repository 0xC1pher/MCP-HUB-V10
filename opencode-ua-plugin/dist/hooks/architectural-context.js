import { GraphCache } from "../cache/graph.js";
export async function buildArchitecturalContext(directory, options = {}) {
    const maxNodesPerLayer = options.maxNodesPerLayer ?? 10;
    const cache = new GraphCache(directory);
    const graph = await cache.loadGraph();
    if (!graph)
        return null;
    const p = graph.project;
    const layers = (graph.layers ?? []).map((l) => {
        const sampleNodes = [];
        for (const id of l.nodeIds) {
            if (sampleNodes.length >= maxNodesPerLayer)
                break;
            const n = graph.nodes.find((x) => x.id === id);
            const label = n?.name ?? id;
            const summary = n?.summary ? ` - ${n.summary}` : "";
            sampleNodes.push(`${label}${summary}`);
        }
        return {
            name: l.name,
            description: l.description,
            nodeCount: l.nodeIds.length,
            sampleNodes
        };
    });
    const maxChars = (options.maxTokens ?? 1500) * 4;
    const parts = [];
    parts.push(`# ${p.name} - ${p.description || "(no description)"}`);
    parts.push(`Languages: ${p.languages.join(", ") || "(unknown)"}`);
    parts.push(`Frameworks: ${p.frameworks.join(", ") || "(unknown)"}`);
    if (p.gitCommitHash)
        parts.push(`Last analyzed: ${p.gitCommitHash}`);
    for (const l of layers) {
        const header = `\n## ${l.name[0].toUpperCase()}${l.name.slice(1)} (${l.nodeCount} nodes) - ${l.description}`;
        parts.push(header);
        const sample = l.sampleNodes.slice(0, maxNodesPerLayer);
        const extra = l.nodeCount - sample.length;
        if (sample.length > 0) {
            parts.push(sample.map(n => `- ${n}`).join("\n"));
            if (extra > 0)
                parts.push(`- ...(${extra} more)`);
        }
    }
    let rendered = parts.join("\n");
    if (rendered.length > maxChars) {
        rendered = rendered.slice(0, maxChars) + "\n... (truncated)";
    }
    return {
        project: p.name,
        description: p.description ?? "",
        languages: p.languages ?? [],
        frameworks: p.frameworks ?? [],
        commit: p.gitCommitHash ?? null,
        layers,
        rendered
    };
}
