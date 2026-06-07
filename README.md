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
- `tests/` — test suite (12 tests, all pure-PowerShell)

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

## Fresh-machine checklist

If you're on a brand-new Windows box, follow these in order. Skip any you've already done.

1. **Install prereqs** (one-time):
   - PowerShell 5.1+ (built into Windows 10+)
   - [git](https://git-scm.com/download/win)
   - [bun](https://bun.sh/docs/installation) (used to build the bundled plugin)
   - [node](https://nodejs.org/) (the plugin's runtime)
   - [Python 3.11+](https://www.python.org/downloads/) (required for MCPs)
2. **Clone** this repo to a stable location (e.g. `~/Desktop/tools/dev-bootstrap`).
3. **Set up `.env`** from the template:
   ```powershell
   copy bootstrap\.env.example bootstrap\.env
   notepad bootstrap\.env
   ```
   Fill in the four `MCP_HUB_V12_*` paths. Suggested defaults on a fresh box:
   - `MCP_HUB_V12_REPO_PATH` → `%USERPROFILE%\Desktop\tools\mcp-hub-v12`
   - `MCP_HUB_V12_VENV_PATH` → `%USERPROFILE%\AppData\Local\mcp-hub-v12-venv`
   - `MCP_HUB_V12_VENV_PYTHON` → `%USERPROFILE%\AppData\Local\mcp-hub-v12-venv\Scripts\python.exe`
   - `MCP_HUB_V12_REQUIREMENTS` → `%USERPROFILE%\Desktop\tools\mcp-hub-v12\requirements.txt`
4. **Run setup**: `.\bootstrap\setup.ps1`. The script clones the mcp-hub V12 repo, creates the venv, installs deps, builds the plugin, and writes your `~/.opencode/config.json`.
5. **(One-time) verify** with the test suite: `.\tests\run-all.ps1`. All 12 tests should pass on a clean install.

## Configuration

Edit `bootstrap/.env` (create from `bootstrap/.env.example` if needed) to override defaults. Recognized keys:

- `MCP_HUB_V12_REPO_PATH` — clone location of the mcp-hub V12 repo (default: `~/Desktop/tools/mcp-hub-v12`)
- `MCP_HUB_V12_VENV_PATH` — full path where the venv should be created
- `MCP_HUB_V12_VENV_PYTHON` — full path to the python.exe inside that venv
- `MCP_HUB_V12_REQUIREMENTS` — full path to requirements.txt (used by setup to `pip install`)
- `PYTHON_EXE` — override the Python interpreter used by the `filesystem` MCP (default: `C:/Program Files/Python311/python.exe`)

If you don't have `.env` or any of the `MCP_HUB_V12_*` keys, setup will fail loud with a clear "unsubstituted placeholder" error. Empty values are also rejected (warned + ignored) so a stale `.env` can't silently produce a broken config.

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

12 tests, all pure-PowerShell, no external test framework.

## License

MIT.
