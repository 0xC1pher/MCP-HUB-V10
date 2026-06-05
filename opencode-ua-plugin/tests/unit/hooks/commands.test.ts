import { describe, it, expect, vi } from "vitest";

const { mockGetTour, mockScan, mockSpawn } = vi.hoisted(() => ({
  mockGetTour: vi.fn().mockResolvedValue({ currentStep: { order: 1, title: "T", description: "d", nodeIds: [] }, totalSteps: 3, nextStep: 2 }),
  mockScan: vi.fn().mockResolvedValue({ success: true, nodeCount: 5, edgeCount: 3, layerCount: 2, cached: false, durationMs: 42 }),
  mockSpawn: vi.fn()
}));

vi.mock("../../../src/tools/get-tour", () => ({ uaGetTour: { execute: mockGetTour } }));
vi.mock("../../../src/tools/scan-codebase", () => ({ uaScanCodebase: { execute: mockScan } }));
vi.mock("node:child_process", () => ({
  spawnSync: mockSpawn
}));

import { handleCommand } from "../../../src/hooks/commands.js";

describe("handleCommand", () => {
  it("/ua-tour returns tour text", async () => {
    const out: any = { parts: [] };
    const handled = await handleCommand("ua-tour", "", out, "/tmp");
    expect(handled).toBe(true);
    expect(out.parts.length).toBe(1);
    expect(out.parts[0].text).toContain("T");
  });

  it("/ua-refresh triggers scan", async () => {
    const out: any = { parts: [] };
    const handled = await handleCommand("ua-refresh", "", out, "/tmp");
    expect(handled).toBe(true);
    expect(mockScan).toHaveBeenCalled();
  });

  it("/ua-install-hooks delegates to bin script (success)", async () => {
    mockSpawn.mockReturnValueOnce({ status: 0, stdout: "[ua-install-hooks] installed\n", stderr: "" });
    const out: any = { parts: [] };
    const handled = await handleCommand("ua-install-hooks", "", out, "/tmp");
    expect(handled).toBe(true);
    expect(out.parts.length).toBe(1);
    expect(out.parts[0].text).toContain("installed");
    expect(mockSpawn).toHaveBeenCalled();
    const [cmd, args, opts] = mockSpawn.mock.calls[0];
    expect(cmd).toBe(process.execPath);
    expect(args[0]).toMatch(/ua-install-hooks\.mjs$/);
    expect(opts.encoding).toBe("utf8");
  });

  it("/ua-install-hooks reports failure", async () => {
    mockSpawn.mockReturnValueOnce({ status: 1, stdout: "", stderr: "permission denied" });
    const out: any = { parts: [] };
    const handled = await handleCommand("ua-install-hooks", "", out, "/tmp");
    expect(handled).toBe(true);
    expect(out.parts[0].text).toContain("install failed");
    expect(out.parts[0].text).toContain("permission denied");
  });

  it("unknown command returns false", async () => {
    const out: any = { parts: [] };
    const handled = await handleCommand("ua-bogus", "", out, "/tmp");
    expect(handled).toBe(false);
    expect(out.parts.length).toBe(0);
  });
});
