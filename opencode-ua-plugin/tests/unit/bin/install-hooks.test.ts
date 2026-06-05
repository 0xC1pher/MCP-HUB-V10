import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

describe("ua-install-hooks", () => {
  let workDir: string;
  let prevCwd: string;

  beforeEach(() => {
    prevCwd = process.cwd();
    workDir = mkdtempSync(join(tmpdir(), "ua-test-"));
    execFileSync("git", ["init", "--initial-branch=main"], { cwd: workDir, stdio: "ignore" });
    execFileSync("git", ["config", "user.email", "test@test"], { cwd: workDir, stdio: "ignore" });
    execFileSync("git", ["config", "user.name", "test"], { cwd: workDir, stdio: "ignore" });
    process.chdir(workDir);
  });

  afterEach(() => {
    process.chdir(prevCwd);
    rmSync(workDir, { recursive: true, force: true });
  });

  it("installs pre-commit hook", () => {
    const binPath = join(prevCwd, "bin", "ua-install-hooks.mjs");
    execFileSync("node", [binPath], { cwd: workDir, stdio: "pipe" });
    const hookPath = join(workDir, ".git", "hooks", "pre-commit");
    expect(existsSync(hookPath)).toBe(true);
    const content = readFileSync(hookPath, "utf8");
    expect(content).toContain("opencode-ua-plugin");
  });

  it("is idempotent on second run", () => {
    const binPath = join(prevCwd, "bin", "ua-install-hooks.mjs");
    execFileSync("node", [binPath], { cwd: workDir, stdio: "pipe" });
    expect(() => {
      execFileSync("node", [binPath], { cwd: workDir, stdio: "pipe" });
    }).not.toThrow();
  });

  it("refuses to overwrite non-UA hook", () => {
    mkdirSync(join(workDir, ".git", "hooks"), { recursive: true });
    writeFileSync(join(workDir, ".git", "hooks", "pre-commit"), "#!/bin/sh\necho 'preexisting'\n");
    const binPath = join(prevCwd, "bin", "ua-install-hooks.mjs");
    try {
      execFileSync("node", [binPath], { cwd: workDir, stdio: "pipe" });
      expect.fail("should have refused");
    } catch (e: any) {
      expect(e.status).toBe(1);
    }
  });
});
