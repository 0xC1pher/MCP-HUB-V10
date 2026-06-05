import type { PluginOptions } from "../plugin-config.js";
import { buildArchitecturalContext } from "./architectural-context.js";

export interface SystemTransformInput {
  system?: string;
  model?: { providerID: string; modelID?: string };
  [k: string]: unknown;
}

export interface SystemTransformOutput {
  system?: string;
  [k: string]: unknown;
}

export interface SystemTransformArgs {
  directory: string;
  config?: PluginOptions;
}

export async function transformSystemPrompt(
  input: SystemTransformInput,
  ctx: SystemTransformArgs
): Promise<SystemTransformInput> {
  if (!ctx.config?.enableAutoContext) return input;
  const ctxObj = await buildArchitecturalContext(ctx.directory, {
    maxTokens: ctx.config.maxContextTokens
  });
  if (!ctxObj) return input;
  const base = input.system ?? "";
  return { ...input, system: `${base}\n\n${ctxObj.rendered}` };
}
