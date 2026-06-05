import { spawnSync } from "node:child_process";
import { uaGetTour } from "../tools/get-tour.js";
import { uaScanCodebase } from "../tools/scan-codebase.js";

export async function handleCommand(
  command: string,
  _args: string,
  output: { parts: any[] },
  directory: string
): Promise<boolean> {
  switch (command) {
    case "ua-tour": {
      const r: any = await uaGetTour.execute({} as any, { directory } as any);
      const step = r.currentStep;
      const text = step
        ? `Step ${step.order}/${r.totalSteps}: ${step.title}\n${step.description}\nNodes: ${(step.nodeIds ?? []).join(", ") || "(none)"}\n${r.nextStep ? `Next: /ua-tour ${r.nextStep}` : "(end)"}`
        : "(no tour available; run ua_scan_codebase first)";
      output.parts.push({ type: "text", text });
      return true;
    }
    case "ua-refresh": {
      const r: any = await uaScanCodebase.execute({ force_full: true } as any, { directory } as any);
      output.parts.push({
        type: "text",
        text: `Re-scanned: ${r.nodeCount} nodes, ${r.edgeCount} edges, ${r.layerCount} layers (${r.durationMs}ms)${r.cached ? " [cached]" : ""}`
      });
      return true;
    }
    case "ua-install-hooks": {
      const r = spawnSync(
        process.execPath,
        [new URL("../../bin/ua-install-hooks.mjs", import.meta.url).pathname],
        { encoding: "utf8" }
      );
      const text = r.status === 0
        ? (r.stdout.trim() || "(installed)")
        : `install failed: ${(r.stderr || r.stdout || "").trim()}`;
      output.parts.push({ type: "text", text });
      return true;
    }
    default:
      return false;
  }
}
