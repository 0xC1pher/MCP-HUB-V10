export interface ArchitecturalContext {
    project: string;
    description: string;
    languages: string[];
    frameworks: string[];
    commit: string | null;
    layers: Array<{
        name: string;
        description: string;
        nodeCount: number;
        sampleNodes: string[];
    }>;
    rendered: string;
}
export interface ContextOptions {
    maxTokens?: number;
    maxNodesPerLayer?: number;
}
export declare function buildArchitecturalContext(directory: string, options?: ContextOptions): Promise<ArchitecturalContext | null>;
