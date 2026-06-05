import { describe, it, expect, vi, beforeEach } from "vitest";

const { mockExecute } = vi.hoisted(() => ({ mockExecute: vi.fn() }));
vi.mock("../../../src/tools/scan-codebase", () => ({
  uaScanCodebase: { execute: mockExecute }
}));

import { onProjectStart, _resetForTests } from "../../../src/hooks/on-project-start";

describe("onProjectStart", () => {
  beforeEach(() => { _resetForTests(); mockExecute.mockReset(); });

  it("triggers scan on first message for a project", async () => {
    mockExecute.mockResolvedValueOnce({ output: "{}", metadata: { nodeCount: 5, durationMs: 100 } } as any);
    const r = await onProjectStart({ directory: "/tmp/projA", sessionID: "s1" });
    expect(r.scanned).toBe(true);
    expect(r.nodeCount).toBe(5);
  });

  it("does not re-scan on second message of same project", async () => {
    mockExecute.mockResolvedValue({ output: "{}", metadata: { nodeCount: 5, durationMs: 100 } } as any);
    await onProjectStart({ directory: "/tmp/projA", sessionID: "s1" });
    const callsAfterFirst = mockExecute.mock.calls.length;
    const r = await onProjectStart({ directory: "/tmp/projA", sessionID: "s2" });
    expect(r.scanned).toBe(false);
    expect(mockExecute.mock.calls.length).toBe(callsAfterFirst);
  });

  it("does not throw on scan failure", async () => {
    mockExecute.mockRejectedValueOnce(new Error("boom"));
    const r = await onProjectStart({ directory: "/tmp/projB", sessionID: "s3" });
    expect(r.scanned).toBe(false);
    expect(r.error).toBe("boom");
  });
});
