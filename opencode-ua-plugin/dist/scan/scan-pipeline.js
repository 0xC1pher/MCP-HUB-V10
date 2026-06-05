import { readdirSync, statSync, existsSync, readFileSync } from "node:fs";
import { join, basename, relative, extname } from "node:path";
import { execSync } from "node:child_process";
import { GraphBuilder } from "@understand-anything/core";
const SKIP_DIRS = new Set([
    "node_modules", ".git", "dist", "build", ".next", ".opencode",
    "coverage", "__snapshots__", ".cache", "target", "out", "vendor"
]);
const CODE_EXTS = new Set([
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".java", ".kt", ".rb", ".php",
    ".cs", ".cpp", ".c", ".h", ".hpp", ".swift"
]);
const DOC_EXTS = new Set([".md", ".mdx", ".rst", ".txt"]);
const CONFIG_EXTS = new Set([".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".xml", ".properties"]);
const DATA_EXTS = new Set([".sql", ".csv", ".tsv", ".graphql", ".gql", ".proto"]);
const SCRIPT_EXTS = new Set([".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"]);
function classifyNonCodeNodeType(ext) {
    if (DOC_EXTS.has(ext))
        return "document";
    if (CONFIG_EXTS.has(ext))
        return "config";
    if (DATA_EXTS.has(ext))
        return "table";
    if (SCRIPT_EXTS.has(ext))
        return "module";
    return "module";
}
function walk(dir, out = []) {
    let entries;
    try {
        entries = readdirSync(dir);
    }
    catch {
        return out;
    }
    for (const e of entries) {
        if (SKIP_DIRS.has(e))
            continue;
        const full = join(dir, e);
        let s;
        try {
            s = statSync(full);
        }
        catch {
            continue;
        }
        if (s.isDirectory())
            walk(full, out);
        else if (s.isFile())
            out.push(full);
    }
    return out;
}
function computeGitHash(projectRoot) {
    try {
        return execSync("git rev-parse --short HEAD", {
            cwd: projectRoot,
            encoding: "utf-8",
            stdio: ["pipe", "pipe", "pipe"]
        }).trim();
    }
    catch {
        return "no-git";
    }
}
function readProjectName(projectRoot) {
    const pkgPath = join(projectRoot, "package.json");
    if (existsSync(pkgPath)) {
        try {
            const pkg = JSON.parse(readFileSync(pkgPath, "utf-8"));
            if (typeof pkg.name === "string" && pkg.name)
                return pkg.name;
        }
        catch { /* ignore */ }
    }
    return basename(projectRoot);
}
export async function scanProject(projectRoot) {
    const projectName = readProjectName(projectRoot);
    const gitHash = computeGitHash(projectRoot);
    const files = walk(projectRoot);
    const builder = new GraphBuilder(projectName, gitHash);
    for (const filePath of files) {
        const rel = relative(projectRoot, filePath).replace(/\\/g, "/");
        const ext = extname(filePath).toLowerCase();
        if (CODE_EXTS.has(ext)) {
            builder.addFile(rel, { summary: "", tags: [], complexity: "moderate" });
        }
        else {
            const nodeType = classifyNonCodeNodeType(ext);
            builder.addNonCodeFile(rel, {
                summary: "",
                tags: [],
                complexity: "simple",
                nodeType
            });
        }
    }
    return builder.build();
}
