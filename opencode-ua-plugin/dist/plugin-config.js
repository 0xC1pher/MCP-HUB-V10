export const DEFAULTS = {
    cacheDir: ".opencode/cache/ua-graph",
    toolPrefix: "ua_",
    enableEmbeddings: false,
    autoScan: true,
    enableAutoContext: false,
    maxContextTokens: 500
};
export const resolveOptions = (opts) => ({
    ...DEFAULTS,
    ...(opts ?? {})
});
