import { uaScanCodebase } from "../tools/scan-codebase.js";

const seenProjects = new Set<string>();

export function _resetForTests() { seenProjects.clear(); }

export interface ProjectStartResult {
  scanned: boolean;
  nodeCount?: number;
  durationMs?: number;
  error?: string;
}

export async function onProjectStart(input: { directory: string; sessionID: string }): Promise<ProjectStartResult> {
  if (seenProjects.has(input.directory)) return { scanned: false };
  try {
    const r = await uaScanCodebase.execute({ force_full: false } as any, { directory: input.directory } as any);
    seenProjects.add(input.directory);
    const meta = (r as any).metadata ?? {};
    return { scanned: true, nodeCount: meta.nodeCount, durationMs: meta.durationMs };
  } catch (e: any) {
    return { scanned: false, error: e?.message ?? String(e) };
  }
}
