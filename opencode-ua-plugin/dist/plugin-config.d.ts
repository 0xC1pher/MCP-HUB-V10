export interface PluginOptions {
    cacheDir?: string;
    toolPrefix?: string;
    enableEmbeddings?: boolean;
    autoScan?: boolean;
    enableAutoContext?: boolean;
    maxContextTokens?: number;
}
export declare const DEFAULTS: Required<PluginOptions>;
export declare const resolveOptions: (opts?: PluginOptions) => Required<PluginOptions>;
