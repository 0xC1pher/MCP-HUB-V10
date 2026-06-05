import { promises as fs } from "node:fs";
import { join } from "node:path";
import type { KnowledgeGraph } from "@understand-anything/core";

const CACHE_SUBDIR = ".opencode/cache/ua-graph";
const GRAPH_FILE = "knowledge-graph.json";
const META_FILE = "meta.json";
const EMB_FILE = "embeddings.json";

export interface AnalysisMeta {
  lastAnalyzedAt: string;
  gitCommitHash: string;
  version: string;
}

export class GraphCache {
  constructor(private projectRoot: string) {}
  private get dir() { return join(this.projectRoot, CACHE_SUBDIR); }
  private get graphPath() { return join(this.dir, GRAPH_FILE); }
  private get metaPath() { return join(this.dir, META_FILE); }
  private get embPath() { return join(this.dir, EMB_FILE); }

  private async readJson<T>(p: string): Promise<T | null> {
    try { return JSON.parse(await fs.readFile(p, "utf-8")) as T; }
    catch (e: any) { if (e.code === "ENOENT") return null; throw e; }
  }
  private async writeJson(p: string, v: unknown) {
    await fs.mkdir(this.dir, { recursive: true });
    await fs.writeFile(p, JSON.stringify(v, null, 2));
  }

  loadGraph() { return this.readJson<KnowledgeGraph>(this.graphPath); }
  saveGraph(g: KnowledgeGraph) { return this.writeJson(this.graphPath, g); }
  loadMeta() { return this.readJson<AnalysisMeta>(this.metaPath); }
  saveMeta(m: AnalysisMeta) { return this.writeJson(this.metaPath, m); }
  loadEmbeddings() { return this.readJson<Record<string, number[]>>(this.embPath).then(v => v ?? {}); }
  saveEmbeddings(m: Record<string, number[]>) { return this.writeJson(this.embPath, m); }
}
