export interface PluginOptions {
  cacheDir?: string;
  toolPrefix?: string;
  enableEmbeddings?: boolean;
  autoScan?: boolean;
  enableAutoContext?: boolean;
  maxContextTokens?: number;
}

export const DEFAULTS: Required<PluginOptions> = {
  cacheDir: ".opencode/cache/ua-graph",
  toolPrefix: "ua_",
  enableEmbeddings: false,
  autoScan: true,
  enableAutoContext: false,
  maxContextTokens: 500
};

export const resolveOptions = (opts?: PluginOptions): Required<PluginOptions> => ({
  ...DEFAULTS,
  ...(opts ?? {})
});
