# dev-bootstrap

Portable OpenCode configuration for Windows. One-command setup of plugin + MCPs + skills on any new machine.

## What this is

A self-contained repo that replicates your OpenCode configuration (plugin, MCPs, skills) on a new Windows machine. Does **not** re-clone the 5 development tools (claw-code, ECC, cult-ui, presenton, Understand-Anything) — those stay where they are.

## What it includes

- `opencode-ua-plugin/` — source code of the UA plugin (snapshot of the current 17-commit version, 52 tests, pre-built dist)
- `vendor/understand-anything-core/` — vendored copy of the plugin's UA core dependency (so the kit is self-contained)
- `skills/` — snapshot of 124 skills (in 68 directories, each `skill-name/SKILL.md`) from your current setup
- `templates/config.json.tmpl` — parameterized config template
- `bootstrap/` — PowerShell scripts that do the actual setup
- `tests/` — test suite (8 tests, all pure-PowerShell)

## Prerequisites

- Windows 10+ with PowerShell 5.1+
- git
- bun
- node
- Python 3.11+ (for MCPs)

## Quick start

```powershell
git clone <repo-url>
cd dev-bootstrap
.\bootstrap\setup.ps1
```

The script:
1. Checks prereqs (fails loud if missing)
2. Builds the plugin (`bun install && bun run build`)
3. Sets up MCP venvs
4. Copies skills to `~/.opencode/skills/` (preserving the `skill-name/SKILL.md` directory structure)
5. Renders `~/.opencode/config.json` from the template
6. Verifies the install

Safe to re-run. Idempotent (skips unchanged files, byte-for-byte config check).

## Configuration

Edit `bootstrap/.env` (create from `bootstrap/.env.example` if needed) to override defaults. Recognized keys:

- `MCP_HUB_V8_VENV_PYTHON` — full path to the python.exe inside your mcp-hub-v8 venv
- `MCP_HUB_V8_SERVER_PY` — full path to the server.py entry point for mcp-hub-v8
- `MCP_HUB_V8_REQUIREMENTS` — full path to requirements.txt (used by setup to pip install)
- `MCP_HUB_V8_VENV_PATH` — full path where the venv should be created (defaults to derived location)
- `PYTHON_EXE` — override the Python interpreter used by the `filesystem` MCP (default: `C:/Program Files/Python311/python.exe`)

If you don't have `.env` or any of the MCP_HUB_V8_* keys, setup will fail loud with a clear "unsubstituted placeholder" error. We never silently produce a broken config.

## Path handling

All paths in the rendered config use forward slashes (the JSON-on-Windows convention). The substitution layer normalizes backslashes to forward slashes automatically — you can use either in `.env`.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — design and structure
- [docs/how-it-works.md](docs/how-it-works.md) — detailed bootstrap flow
- [docs/troubleshooting.md](docs/troubleshooting.md) — common issues
- [docs/adding-a-mcp.md](docs/adding-a-mcp.md) — how to add a new MCP

## Testing

```powershell
.\tests\run-all.ps1
```

8 tests, all pure-PowerShell, no external test framework.

## License

MIT.
