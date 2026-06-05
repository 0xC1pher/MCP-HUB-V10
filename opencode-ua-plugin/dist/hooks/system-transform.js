import { buildArchitecturalContext } from "./architectural-context.js";
export async function transformSystemPrompt(input, ctx) {
    if (!ctx.config?.enableAutoContext)
        return input;
    const ctxObj = await buildArchitecturalContext(ctx.directory, {
        maxTokens: ctx.config.maxContextTokens
    });
    if (!ctxObj)
        return input;
    const base = input.system ?? "";
    return { ...input, system: `${base}\n\n${ctxObj.rendered}` };
}
