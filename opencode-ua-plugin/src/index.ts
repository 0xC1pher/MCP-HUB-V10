import type { Plugin } from "@opencode-ai/plugin";
import { uaScanCodebase } from "./tools/scan-codebase.js";
import { uaSearchSemantic } from "./tools/search-semantic.js";
import { uaQueryGraph } from "./tools/query-graph.js";
import { uaExplainNode } from "./tools/explain-node.js";
import { uaGetTour } from "./tools/get-tour.js";
import { uaDiffImpact } from "./tools/diff-impact.js";
import { resolveOptions, type PluginOptions } from "./plugin-config.js";
import { onProjectStart } from "./hooks/on-project-start.js";
import { handleCommand } from "./hooks/commands.js";
import { transformSystemPrompt } from "./hooks/system-transform.js";

const plugin: Plugin = async (_input, options) => {
  const opts = resolveOptions(options as PluginOptions);
  return {
    tool: {
      [opts.toolPrefix + "scan_codebase"]: uaScanCodebase,
      [opts.toolPrefix + "search_semantic"]: uaSearchSemantic,
      [opts.toolPrefix + "query_graph"]: uaQueryGraph,
      [opts.toolPrefix + "explain_node"]: uaExplainNode,
      [opts.toolPrefix + "get_tour"]: uaGetTour,
      [opts.toolPrefix + "diff_impact"]: uaDiffImpact
    },
    "chat.message": async (input) => {
      if (!opts.autoScan) return;
      const directory = (input as any).project?.directory ?? (input as any).directory ?? process.cwd();
      onProjectStart({ directory, sessionID: input.sessionID })
        .catch(() => { });
    },
    "command.execute.before": async (input, output) => {
      await handleCommand(
        (input as any).command,
        (input as any).arguments ?? "",
        output as { parts: any[] },
        process.cwd()
      );
    },
    "experimental.chat.system.transform": async (_input, output) => {
      const directory = (_input as any).project?.directory
        ?? (output as any)?.project?.directory
        ?? process.cwd();
      const result = await transformSystemPrompt(
        { system: (output as any).system } as any,
        { directory, config: opts } as any
      );
      if (result.system) (output as any).system = result.system;
    }
  };
};

export default plugin;

export type { PluginOptions } from "./plugin-config.js";
