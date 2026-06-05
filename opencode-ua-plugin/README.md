# opencode-ua-plugin

[Understand-Anything](https://github.com/...) integration for OpenCode. Provides 6 tools + 3 hooks + 3 slash commands + 2 bin scripts that give the LLM a structured view of your codebase.

## Installation

Edit `~/.opencode/config.json` and add the `plugin` field:

```json
{
  "plugin": ["./tools/opencode-ua-plugin/dist/index.js"]
}
```

The path is resolved relative to the config file's location. For absolute paths, use the full path or a `file://` URL on Windows.

Restart OpenCode to load the plugin.

## Configuration

Pass options as the second arg of the plugin entry in `config.json`:

```json
{
  "plugin": [
    {
      "path": "./tools/opencode-ua-plugin/dist/index.js",
      "options": {
        "cacheDir": ".opencode/cache/ua-graph",
        "toolPrefix": "ua_",
        "enableEmbeddings": false,
        "autoScan": true,
        "enableAutoContext": false,
        "maxContextTokens": 500
      }
    }
  ]
}
```

| Option | Default | Description |
|---|---|---|
| `cacheDir` | `.opencode/cache/ua-graph` | Where to store the knowledge graph (per-project, relative to project root) |
| `toolPrefix` | `ua_` | Prefix for all tool names |
| `enableEmbeddings` | `false` | Reserved — semantic search is currently fuzzy (see Known limitations) |
| `autoScan` | `true` | Lazy-scan on first chat message in a new project |
| `enableAutoContext` | `false` | Inject graph context into every system prompt (opt-in, off by default) |
| `maxContextTokens` | `500` | Token budget for auto-injected context |

## Tools (6)

- `ua_scan_codebase` — Build/refresh the knowledge graph for the current project
- `ua_search_semantic` — Substring + Fuse.js fuzzy search across node names and summaries
- `ua_query_graph` — Filter nodes by type and/or layer with substring matching on name/summary
- `ua_explain_node` — Show incoming and outgoing edges for a single node
- `ua_get_tour` — Step-by-step onboarding tour of the codebase
- `ua_diff_impact` — Show what code is affected by the current git diff (changed files, callers, impact level)

## Slash commands

- `/ua-tour [step]` — Show a tour step (or the first one)
- `/ua-refresh` — Force a full rescan
- `/ua-install-hooks` — Install the git pre-commit hook (see below)

## Hooks

- `chat.message` — Lazy scan on first message of a session (when `autoScan: true`)
- `command.execute.before` — Dispatches `/ua-*` slash commands
- `experimental.chat.system.transform` — Injects graph context into system prompt (when `enableAutoContext: true`)

## Pre-commit hook (optional)

```bash
node bin/ua-install-hooks.mjs
```

or in OpenCode:

```
/ua-install-hooks
```

This installs a non-blocking `.git/hooks/pre-commit` that **warns** when the cached graph is stale relative to the working tree. It NEVER blocks commits. To uninstall: `rm .git/hooks/pre-commit`.

## Cache

Lives at `<projectRoot>/.opencode/cache/ua-graph/` with three files:

- `knowledge-graph.json` — Full graph (nodes, edges, layers, project metadata)
- `meta.json` — `{ lastAnalyzedAt, gitCommitHash, version }`
- `embeddings.json` — Reserved for future semantic search (not currently written)

## Development

```bash
bun install
bun run test        # 49 unit/integration + 3 E2E = 52 total
bun run typecheck   # tsc --noEmit
bun run build       # emits dist/ and copies bin/
```

The plugin consumes `@understand-anything/core` via a `file:` dependency on `C:/Users/Admin/Desktop/tools/Understand-Anything/understand-anything-plugin/packages/core`.

## Known limitations

- `enableEmbeddings: true` is reserved. `ua_search_semantic` uses Fuse.js fuzzy matching, not LLM embeddings. The `mode: "semantic" | "fuzzy"` field in results reports whether the project HAS cached embeddings (capability signal), not which algorithm ran. True semantic search requires the dashboard.
- `ua_diff_impact.impactLevel` is computed heuristically (`NONE` / `COSMETIC` / `STRUCTURAL`) from edge traversal, not from UA core's full `analyzeChanges` pipeline — that requires a `FingerprintStore` + `PluginRegistry` we don't persist in the plugin.
- Project root is resolved via `ctx.directory` for tools and via `process.cwd()` for slash commands (where OpenCode passes the launch directory). Hooks read `input.project.directory` first, falling back to `output.project.directory`, then `process.cwd()`.
