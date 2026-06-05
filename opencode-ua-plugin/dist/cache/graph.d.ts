import type { KnowledgeGraph } from "@understand-anything/core";
export interface AnalysisMeta {
    lastAnalyzedAt: string;
    gitCommitHash: string;
    version: string;
}
export declare class GraphCache {
    private projectRoot;
    constructor(projectRoot: string);
    private get dir();
    private get graphPath();
    private get metaPath();
    private get embPath();
    private readJson;
    private writeJson;
    loadGraph(): Promise<KnowledgeGraph | null>;
    saveGraph(g: KnowledgeGraph): Promise<void>;
    loadMeta(): Promise<AnalysisMeta | null>;
    saveMeta(m: AnalysisMeta): Promise<void>;
    loadEmbeddings(): Promise<Record<string, number[]>>;
    saveEmbeddings(m: Record<string, number[]>): Promise<void>;
}
