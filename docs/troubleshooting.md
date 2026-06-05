# Troubleshooting

## "Prerequisite not found: bun"

Install bun: https://bun.sh/docs/installation

On Windows: `irm bun.sh/install.ps1 | iex`

## "Prerequisite not found: python3" or "Python 3.11+ not found in standard locations"

The script tries `C:/Program Files/Python311/python.exe` first (the typical install location), then `py -3.11` launcher, then `python3` on PATH. If none work:

- Install Python 3.11+ from https://www.python.org/downloads/
- Make sure it's on PATH (check "Add to PATH" during install)
- Or set `PYTHON_EXE` in `bootstrap/.env` to your Python's full path (use forward slashes or backslashes — both work; they're normalized)

## "yari-mcp-v8 setup failed"

This MCP requires specific paths. Set these in `bootstrap/.env`:

```
MCP_HUB_V8_VENV_PATH=C:/path/to/where/you/want/the/venv
MCP_HUB_V8_VENV_PYTHON=C:/path/to/where/you/want/the/venv/Scripts/python.exe
MCP_HUB_V8_SERVER_PY=C:/path/to/mcp-hub-v8/src/server.py
MCP_HUB_V8_REQUIREMENTS=C:/path/to/mcp-hub-v8/requirements.txt
```

If the source isn't available, the script continues with a warning. OpenCode will fail to start that MCP, but other config is intact.

## "Unsubstituted placeholders remain in rendered config"

The template has `{{...}}` placeholders that weren't filled. The most common cause: missing `MCP_HUB_V8_*` keys in `bootstrap/.env`. The script fails loud — you can never end up with a broken config silently.

Fix: add the missing keys to `bootstrap/.env` and re-run.

## "bun install fails with cannot resolve @understand-anything/core"

The plugin's `package.json` has a `file:` dep pointing to `vendor/understand-anything-core`. If that directory is missing or incomplete, you have an incomplete clone. Verify:

```powershell
Test-Path "vendor/understand-anything-core/package.json"  # must be True
```

If False, your clone is incomplete — try `git pull` or re-clone.

## Skills junction issues

If `~/.opencode/skills` is a junction pointing to a non-existent target, the bootstrap will create a regular directory instead. To preserve a junction:

1. Manually re-create the junction: `New-Item -ItemType Junction -Path ~/.opencode/skills -Target <real-path>`
2. Re-run setup

## Skills install is slow

The recursive install reads and SHA-256 hashes every file. With 124 skills and ~277 files, this takes a few seconds. Subsequent runs are fast because the SHA check skips unchanged files.

## Tests fail

Run `.\tests\run-all.ps1` from the repo root. Each test file is independent; failures point to the specific component.

## How to reset and start over

```powershell
Remove-Item ~/.opencode/config.json -Force  # only if you want to regenerate
.\bootstrap\setup.ps1
```

The bootstrap is safe to re-run; reset only if the config is broken.

## How to upgrade the plugin

The plugin is a snapshot. To upgrade:

1. Pull the latest from upstream (or copy new source)
2. Run tests in the snapshot: `cd opencode-ua-plugin && bun run test`
3. Commit the new snapshot

To upgrade UA core:

1. Update `vendor/understand-anything-core/` to the new version
2. Re-run `bun install` in `opencode-ua-plugin/`
3. Commit the new vendor
