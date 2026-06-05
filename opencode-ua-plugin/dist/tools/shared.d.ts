export interface ToolResponse<T> {
    output: string;
    metadata?: T;
}
export declare const jsonResponse: <T>(data: T) => ToolResponse<T>;
