import { tool } from "@opencode-ai/plugin";
import { GraphCache } from "../cache/graph.js";

const zod = tool.schema;

export const uaGetTour = Object.assign(
  tool({
    description:
      "Get a guided tour of the codebase for onboarding. " +
      "Returns step-by-step narrative derived from the knowledge graph.",
    args: {
      step: zod.number().int().positive().optional()
        .describe("1-indexed step number; omit to get step 1"),
      topic: zod.string().optional()
        .describe("Custom tour topic (filter step descriptions)")
    },
    async execute(args, ctx): Promise<any> {
      const cache = new GraphCache(ctx.directory);
      const graph = await cache.loadGraph();
      if (!graph?.tour?.length) return { totalSteps: 0 };

      let steps = [...graph.tour].sort((a, b) => a.order - b.order);
      if (args.topic) {
        const q = args.topic.toLowerCase();
        steps = steps.filter(s =>
          s.title.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          (s.nodeIds ?? []).some(n => n.toLowerCase().includes(q))
        );
      }

      if (steps.length === 0) return { totalSteps: 0 };

      const stepNum = args.step ?? 1;
      const current = steps.find(s => s.order === stepNum) ?? steps[0];
      const next = current.order < steps.length ? current.order + 1 : undefined;

      return {
        currentStep: current,
        totalSteps: steps.length,
        nextStep: next
      };
    }
  }),
  { name: "ua_get_tour" }
) as any;
