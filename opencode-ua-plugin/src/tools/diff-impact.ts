import { tool } from "@opencode-ai/plugin";
import { getChangedFiles } from "@understand-anything/core";
import { GraphCache } from "../cache/graph.js";

const zod = tool.schema;

type ImpactLevel = "NONE" | "COSMETIC" | "STRUCTURAL";

function basename(p: string): string {
  return p.replace(/^.*[\\/]/, "");
}

export const uaDiffImpact = Object.assign(
  tool({
    description:
      "Show what code is affected by the current git diff. " +
      "Returns changed files, direct callers (via graph edges), and impact level.",
    args: {},
    async execute(_args, ctx): Promise<any> {
      const cache = new GraphCache(ctx.directory);
      const graph = await cache.loadGraph();
      const commitHash = graph?.project?.gitCommitHash ?? "HEAD~1";
      const changedFiles = await getChangedFiles(ctx.directory, commitHash);

      if (!changedFiles.length) {
        return {
          changedFiles: [], affectedFiles: [], directCallers: [], affectedLayers: [],
          impactLevel: "NONE" as ImpactLevel
        };
      }

      const directCallers = new Set<string>();
      const affectedFiles = new Set<string>(changedFiles);

      if (graph) {
        for (const e of graph.edges) {
          const target = String(e.target ?? "");
          const matches = changedFiles.some(f =>
            target.includes(f) || target.endsWith(basename(f))
          );
          if (matches) {
            directCallers.add(String(e.source));
            affectedFiles.add(String(e.source));
          }
        }
      }

      const level: ImpactLevel =
        directCallers.size === 0 ? "COSMETIC" : "STRUCTURAL";

      return {
        changedFiles,
        affectedFiles: Array.from(affectedFiles),
        directCallers: Array.from(directCallers),
        affectedLayers: [],
        impactLevel: level
      };
    }
  }),
  { name: "ua_diff_impact" }
) as any;
