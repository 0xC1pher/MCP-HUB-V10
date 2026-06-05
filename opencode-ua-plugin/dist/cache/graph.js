import { promises as fs } from "node:fs";
import { join } from "node:path";
const CACHE_SUBDIR = ".opencode/cache/ua-graph";
const GRAPH_FILE = "knowledge-graph.json";
const META_FILE = "meta.json";
const EMB_FILE = "embeddings.json";
export class GraphCache {
    projectRoot;
    constructor(projectRoot) {
        this.projectRoot = projectRoot;
    }
    get dir() { return join(this.projectRoot, CACHE_SUBDIR); }
    get graphPath() { return join(this.dir, GRAPH_FILE); }
    get metaPath() { return join(this.dir, META_FILE); }
    get embPath() { return join(this.dir, EMB_FILE); }
    async readJson(p) {
        try {
            return JSON.parse(await fs.readFile(p, "utf-8"));
        }
        catch (e) {
            if (e.code === "ENOENT")
                return null;
            throw e;
        }
    }
    async writeJson(p, v) {
        await fs.mkdir(this.dir, { recursive: true });
        await fs.writeFile(p, JSON.stringify(v, null, 2));
    }
    loadGraph() { return this.readJson(this.graphPath); }
    saveGraph(g) { return this.writeJson(this.graphPath, g); }
    loadMeta() { return this.readJson(this.metaPath); }
    saveMeta(m) { return this.writeJson(this.metaPath, m); }
    loadEmbeddings() { return this.readJson(this.embPath).then(v => v ?? {}); }
    saveEmbeddings(m) { return this.writeJson(this.embPath, m); }
}
