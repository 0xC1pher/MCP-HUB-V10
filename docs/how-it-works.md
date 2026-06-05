# How it works

The setup script runs 5 steps. Each is independent and idempotent.

## Step 0: Prereq check

Verifies:
- PowerShell 5.1+
- git
- bun
- node
- python3 (or python)

If any are missing, prints a clear error and exits 1.

## Step 1: Build the plugin

First builds the vendored `@understand-anything/core` (in `vendor/understand-anything-core`) with `bun install && bun run build`. The core's `package.json` points to `dist/index.js`, so without this step the plugin's `tsc` can't find the core's types.

Then runs `bun install && bun run build` in `opencode-ua-plugin/`. The build:
- Resolves `@understand-anything/core` from the local `vendor/` directory (via `file:../vendor/understand-anything-core`)
- Compiles TypeScript with `tsc`
- Copies `bin/*.mjs` scripts to `dist/` (cross-platform)
- Outputs `dist/index.js` (the plugin entry)

The `Test-PluginBuilt` check skips rebuild if `dist/index.js` is newer than all source files. The freshness check uses `StartsWith` on normalized paths so it works on Windows.

## Step 2: Set up MCPs

For each MCP in the config:

- **filesystem**: detects Python 3.11+ in standard locations, uses it directly (no venv). Default: `C:/Program Files/Python311/python.exe`.
- **yari-mcp-v8**: creates a venv at the path specified by `MCP_HUB_V8_VENV_PATH` in `.env`, then pip installs from `MCP_HUB_V8_REQUIREMENTS`.

If a specific MCP setup fails, the script logs and continues with the others (per spec: never fail the whole install for one MCP). The final `verify` step will surface the broken MCP.

## Step 3: Install skills

Recursively copies `dev-bootstrap/skills/` to the destination. The structure `skill-name/SKILL.md` is preserved. Skips files with matching SHA-256. Destination is `~/.opencode/skills/` (or follows the junction if one exists — `Get-SkillsDestination` resolves the junction's target).

## Step 4: Render config.json

Reads `templates/config.json.tmpl`, substitutes placeholders with detected paths, writes to `~/.opencode/config.json`. Skips if the file already matches byte-for-byte. The substitution layer normalizes backslashes to forward slashes so the rendered config is valid JSON on Windows.

Placeholders:
- `{{USERPROFILE}}` — `$env:USERPROFILE` (normalized to forward slashes)
- `{{SCHEMA}}` — `https://opencode.ai/config.json`
- `{{PLUGIN_PATH}}` — the actual path of the plugin's `dist/index.js` in this repo, passed from `setup.ps1` (after backslash normalization)
- `{{PYTHON_EXE}}` — default `C:/Program Files/Python311/python.exe` (overridable via `.env`)
- `{{MCP_HUB_V8_VENV_PYTHON}}` and `{{MCP_HUB_V8_SERVER_PY}}` — required, must be in `.env` (otherwise setup fails loud with "unsubstituted placeholder" error)

## Step 5: Verify

Checks that:
- Config is valid JSON
- Plugin `dist/index.js` exists
- Skills directory has files

Prints a green success message or red failure summary.
