export declare function _resetForTests(): void;
export interface ProjectStartResult {
    scanned: boolean;
    nodeCount?: number;
    durationMs?: number;
    error?: string;
}
export declare function onProjectStart(input: {
    directory: string;
    sessionID: string;
}): Promise<ProjectStartResult>;
