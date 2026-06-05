import { uaScanCodebase } from "./tools/scan-codebase.js";
import { uaSearchSemantic } from "./tools/search-semantic.js";
import { uaQueryGraph } from "./tools/query-graph.js";
import { uaExplainNode } from "./tools/explain-node.js";
import { uaGetTour } from "./tools/get-tour.js";
import { uaDiffImpact } from "./tools/diff-impact.js";
import { resolveOptions } from "./plugin-config.js";
import { onProjectStart } from "./hooks/on-project-start.js";
import { handleCommand } from "./hooks/commands.js";
import { transformSystemPrompt } from "./hooks/system-transform.js";
const plugin = async (_input, options) => {
    const opts = resolveOptions(options);
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
            if (!opts.autoScan)
                return;
            const directory = input.project?.directory ?? input.directory ?? process.cwd();
            onProjectStart({ directory, sessionID: input.sessionID })
                .catch(() => { });
        },
        "command.execute.before": async (input, output) => {
            await handleCommand(input.command, input.arguments ?? "", output, process.cwd());
        },
        "experimental.chat.system.transform": async (_input, output) => {
            const directory = _input.project?.directory
                ?? output?.project?.directory
                ?? process.cwd();
            const result = await transformSystemPrompt({ system: output.system }, { directory, config: opts });
            if (result.system)
                output.system = result.system;
        }
    };
};
export default plugin;
