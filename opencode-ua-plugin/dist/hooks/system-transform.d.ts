import type { PluginOptions } from "../plugin-config.js";
export interface SystemTransformInput {
    system?: string;
    model?: {
        providerID: string;
        modelID?: string;
    };
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
export declare function transformSystemPrompt(input: SystemTransformInput, ctx: SystemTransformArgs): Promise<SystemTransformInput>;
