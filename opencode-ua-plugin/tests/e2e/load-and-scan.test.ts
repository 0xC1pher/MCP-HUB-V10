import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { mkdtempSync, writeFileSync, rmSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";
import plugin from "../../src/index.js";

const EXPECTED_TOOLS = [
  "ua_scan_codebase",
  "ua_search_semantic",
  "ua_query_graph",
  "ua_explain_node",
  "ua_get_tour",
  "ua_diff_impact"
];

describe("E2E: plugin loads, scans, and queries", () => {
  let workDir: string;
  let prevCwd: string;

  beforeEach(() => {
    prevCwd = process.cwd();
    workDir = mkdtempSync(join(tmpdir(), "ua-e2e-"));

    execFileSync("git", ["init", "--initial-branch=main"], { cwd: workDir, stdio: "ignore" });
    execFileSync("git", ["config", "user.email", "t@t"], { cwd: workDir, stdio: "ignore" });
    execFileSync("git", ["config", "user.name", "t"], { cwd: workDir, stdio: "ignore" });

    mkdirSync(join(workDir, "src"), { recursive: true });

    writeFileSync(
      join(workDir, "package.json"),
      JSON.stringify({ name: "e2e-fixture", type: "module" })
    );
    writeFileSync(
      join(workDir, "src/index.ts"),
      "export const greet = (name: string) => `Hello ${name}`;\n"
    );
    writeFileSync(
      join(workDir, "src/auth.ts"),
      "export function login(user: string) { return user; }\n"
    );

    execFileSync("git", ["add", "."], { cwd: workDir, stdio: "ignore" });
    execFileSync("git", ["commit", "-m", "init"], { cwd: workDir, stdio: "ignore" });

    process.chdir(workDir);
  });

  afterEach(() => {
    process.chdir(prevCwd);
    rmSync(workDir, { recursive: true, force: true });
  });

  it("plugin returns all tools and hooks", async () => {
    const result: any = await (plugin as any)({} as any, {} as any);
    expect(result.tool).toBeDefined();
    const toolNames = Object.keys(result.tool);
    for (const name of EXPECTED_TOOLS) {
      expect(toolNames, `missing tool: ${name}`).toContain(name);
    }
    expect(toolNames).toHaveLength(EXPECTED_TOOLS.length);
    expect(typeof result["chat.message"]).toBe("function");
    expect(typeof result["command.execute.before"]).toBe("function");
    expect(typeof result["experimental.chat.system.transform"]).toBe("function");
  });

  it("scans fixture and writes cache", async () => {
    const result: any = await (plugin as any)({} as any, {} as any);
    const scan: any = result.tool.ua_scan_codebase;
    const out = await scan.execute({ force_full: true }, { directory: workDir });
    expect(out.success).toBe(true);
    expect(out.nodeCount).toBeGreaterThan(0);
    expect(out.cached).toBe(false);
    const cachePath = join(workDir, ".opencode/cache/ua-graph/knowledge-graph.json");
    expect(existsSync(cachePath)).toBe(true);
  }, 30000);

  it("queries graph after scan", async () => {
    const result: any = await (plugin as any)({} as any, {} as any);
    const scan: any = result.tool.ua_scan_codebase;
    await scan.execute({ force_full: true }, { directory: workDir });
    const query: any = result.tool.ua_query_graph;
    const r = await query.execute({ query: "index" }, { directory: workDir });
    expect(r.totalMatched).toBeGreaterThan(0);
    expect(r.nodes.length).toBeGreaterThan(0);
  }, 30000);
});
