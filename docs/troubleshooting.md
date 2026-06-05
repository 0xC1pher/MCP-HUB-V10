# Troubleshooting

## E2E findings: known issues fixed in the bootstrap itself

The setup script was hardened against four PS 5.1 / Windows quirks during E2E. If you upgrade and see a regression, check whether these still apply.

### `iex` rejects `&&` in the build command (PS 5.1)

The build command `bun install && bun run build` was passed to `Invoke-Expression`. PS 5.1's parser doesn't recognize `&&` as a statement separator inside `iex`, so the whole script errored with `The token '&&' is not a valid statement separator`.

Fix: use `cmd /c $BuildCommand` instead of `iex $BuildCommand`. `cmd.exe` understands `&&` and returns a proper exit code.

### Vendored core is built, not just installed

`@understand-anything/core` is vendored at `vendor/understand-anything-core`. Its `package.json` says `main: dist/index.js`, so `bun install` of the plugin finds a broken package. The core must be built first (`bun install && bun run build` in the vendor dir) so `dist/index.d.ts` exists for the plugin's `tsc`.

Fix: a new `Build-PluginCore` step runs before `Build-Plugin` in `setup.ps1`.

### Filesystem MCP setup was being called with `$null` venv path

`Setup-MCP` checked "does the config have venvPath and requirementsPath keys" but didn't check that the values were non-null. The filesystem MCP's config has both keys with `$null` values, so `Ensure-PythonVenv` was called with `$null` and threw.

Fix: `Setup-MCP` now skips venv setup unless both values are non-empty.

### `Get-FileHash` function shadowed the built-in cmdlet

`skills.ps1` defined a wrapper `function Get-FileHash` that recursively called itself instead of the built-in `Get-FileHash` cmdlet. The SHA-256 check always returned a `PSCustomObject`, never a string, so the comparison `$srcHash -eq $dstHash` always failed. Every file was recopied on every run.

Fix: renamed the wrapper to `Get-SHA256OfFile` to avoid the collision.

### Idempotency: `Set-Content` adds a trailing newline on PS 5.1

`Set-Content -Value $content` writes `$content` PLUS a trailing newline. The next run's `Get-Content -Raw` returns the file with the extra newline, which doesn't match the rendered content, so the config was rewritten on every run.

Fix: `Render-Config` now uses `-NoNewline`. `Test-ConfigMatches` also trims trailing whitespace before comparing (defense in depth).

### Idempotency: `*/dist/*` glob only matches forward slashes

`Build-Plugin`'s freshness check used `$_.FullName -notlike "*/dist/*"`. On Windows, `FullName` uses backslashes, so the pattern didn't match `dist\index.d.ts` — those files slipped through the filter and had a later mtime than `dist\index.js` (because `tsc` writes them a millisecond later). The plugin rebuilt on every run.

Fix: use `StartsWith` on a normalized path so it works on Windows backslashes and Unix forward slashes.

### Variable name collision: `$LogPath` (test scope) clobbered by `$Script:LogPath = $null`

PS 5.1 variables are case-insensitive. `common.ps1` had `$Script:LogPath = $null` at module load. A test that set `$logPath` to a temp file then re-dot-sourced `common.ps1` had the test's `$logPath` reset to `$null` because PS treated it as the same variable.

Fix: tests now use a distinct name like `$installLogPath`.

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
