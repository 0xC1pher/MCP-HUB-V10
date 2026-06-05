import { uaScanCodebase } from "../tools/scan-codebase.js";
const seenProjects = new Set();
export function _resetForTests() { seenProjects.clear(); }
export async function onProjectStart(input) {
    if (seenProjects.has(input.directory))
        return { scanned: false };
    try {
        const r = await uaScanCodebase.execute({ force_full: false }, { directory: input.directory });
        seenProjects.add(input.directory);
        const meta = r.metadata ?? {};
        return { scanned: true, nodeCount: meta.nodeCount, durationMs: meta.durationMs };
    }
    catch (e) {
        return { scanned: false, error: e?.message ?? String(e) };
    }
}
