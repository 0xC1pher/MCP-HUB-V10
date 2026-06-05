import { describe, it, expect, vi } from "vitest";

const mockTour = [
  { order: 1, title: "Entry point", description: "Start here", nodeIds: ["file:src/index.ts"] },
  { order: 2, title: "Auth layer", description: "Login flow", nodeIds: ["file:src/auth.ts"] }
];

vi.mock("../../../src/cache/graph", () => ({
  GraphCache: vi.fn().mockImplementation(() => ({
    loadGraph: vi.fn().mockResolvedValue({ tour: mockTour })
  }))
}));

import { uaGetTour } from "../../../src/tools/get-tour";

describe("ua_get_tour", () => {
  it("returns step 1 by default", async () => {
    const r: any = await uaGetTour.execute({} as any, { directory: "/tmp" } as any);
    expect(r.currentStep?.order).toBe(1);
    expect(r.totalSteps).toBe(2);
    expect(r.nextStep).toBe(2);
  });

  it("returns requested step", async () => {
    const r: any = await uaGetTour.execute({ step: 2 } as any, { directory: "/tmp" } as any);
    expect(r.currentStep?.order).toBe(2);
    expect(r.nextStep).toBeUndefined();
  });

  it("returns empty when no tour", async () => {
    const { GraphCache } = await import("../../../src/cache/graph");
    (GraphCache as any).mockImplementation(() => ({
      loadGraph: vi.fn().mockResolvedValue({ tour: [] })
    }));
    const r: any = await uaGetTour.execute({} as any, { directory: "/tmp" } as any);
    expect(r.totalSteps).toBe(0);
  });

  it("returns empty when no graph", async () => {
    const { GraphCache } = await import("../../../src/cache/graph");
    (GraphCache as any).mockImplementation(() => ({ loadGraph: vi.fn().mockResolvedValue(null) }));
    const r: any = await uaGetTour.execute({} as any, { directory: "/tmp" } as any);
    expect(r.totalSteps).toBe(0);
  });
});
