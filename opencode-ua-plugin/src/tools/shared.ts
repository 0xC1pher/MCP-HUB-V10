import { z } from "zod";

export interface ToolResponse<T> {
  output: string;
  metadata?: T;
}

export const jsonResponse = <T>(data: T): ToolResponse<T> => ({
  output: JSON.stringify(data, null, 2),
  metadata: data
});
