import { describe, it, expect, vi, beforeEach } from "vitest";

const { mockBuild } = vi.hoisted(() => ({
  mockBuild: vi.fn()
}));

vi.mock("../../../src/hooks/architectural-context.js", () => ({
  buildArchitecturalContext: mockBuild
}));

import { transformSystemPrompt } from "../../../src/hooks/system-transform.js";

describe("transformSystemPrompt", () => {
  beforeEach(() => mockBuild.mockReset());

  it("appends context when enabled and graph exists", async () => {
    mockBuild.mockResolvedValue({
      project: "p",
      description: "d",
      languages: [],
      frameworks: [],
      commit: null,
      layers: [],
      rendered: "[UA-CONTEXT] my context"
    });
    const out = await transformSystemPrompt(
      { system: "You are a helper", model: { providerID: "x" } },
      { directory: "/tmp", config: { enableAutoContext: true } as any }
    );
    expect(out.system).toContain("You are a helper");
    expect(out.system).toContain("[UA-CONTEXT] my context");
  });

  it("passes through when disabled", async () => {
    const out = await transformSystemPrompt(
      { system: "You are a helper" } as any,
      { directory: "/tmp", config: { enableAutoContext: false } as any }
    );
    expect(out.system).toBe("You are a helper");
    expect(mockBuild).not.toHaveBeenCalled();
  });

  it("passes through when no graph (graph returns null)", async () => {
    mockBuild.mockResolvedValue(null);
    const out = await transformSystemPrompt(
      { system: "You are a helper" } as any,
      { directory: "/tmp", config: { enableAutoContext: true } as any }
    );
    expect(out.system).toBe("You are a helper");
  });
});
