# Architecture

## Design principles

1. **Self-contained**: no submodules, no required remotes, no external clones. The plugin source AND the UA core library it depends on are committed INTO this repo. Clone and run.
2. **Preservation, not modification**: the bootstrap never modifies the 5 development tools (claw-code, ECC, cult-ui, presenton, Understand-Anything). It only writes to:
   - `~/.opencode/config.json` (rendered from the template)
   - `~/.opencode/skills/` (skill install, preserving the junction if one exists)
   - The plugin's own `dist/` and `node_modules/` (build artifacts, inside `opencode-ua-plugin/`)
   - MCP venvs at paths the user provides via `.env`
3. **Idempotent**: every step checks state before acting. Safe to re-run. SHA-256 checked for skills, byte-for-byte check for config, freshness check for plugin dist.
4. **Fail loud on prereqs, fail loud on missing required config**: missing Python is fatal; missing MCP config that can't be defaulted is also fatal. We never produce a broken config silently.

## Repo structure

```
dev-bootstrap/
├── bootstrap/                       # PowerShell setup scripts
│   ├── setup.ps1                    # Entry point (what users run)
│   └── lib/                         # Modular libraries
│       ├── common.ps1               # Logging, prereqs, banner
│       ├── plugin.ps1               # Build the opencode-ua-plugin
│       ├── mcps.ps1                 # Python venv + pip install for MCPs
│       ├── skills.ps1               # Copy skills recursively, with SHA check
│       ├── config.ps1               # Render config.json from template
│       └── verify.ps1               # Post-install health check
├── templates/
│   └── config.json.tmpl             # Parameterized config (uses / paths)
├── opencode-ua-plugin/              # Snapshot of plugin source (17 commits, 52 tests, pre-built dist)
├── vendor/
│   └── understand-anything-core/    # Vendored copy of the plugin's UA core dep
├── skills/                          # Snapshot of 124 skills (skill-name/SKILL.md)
├── tests/                           # Pure-PowerShell test suite
│   ├── lib/
│   │   ├── assert.ps1               # Custom assertion library (no Pester)
│   │   └── runner.ps1
│   ├── run-all.ps1
│   ├── common.tests.ps1
│   ├── plugin.tests.ps1
│   ├── mcps.tests.ps1
│   ├── skills.tests.ps1
│   ├── config.tests.ps1
│   ├── verify.tests.ps1
│   ├── smoke-setup.tests.ps1
│   └── selftest.tests.ps1
└── docs/                            # User-facing documentation
    ├── how-it-works.md
    ├── troubleshooting.md
    └── adding-a-mcp.md
```

## Bootstrap flow

```
setup.ps1
├── Initialize logging
├── Print banner
├── Prereq check (fail loud)
├── Step 1: Build plugin (skip if dist/ is fresh)
├── Step 2: Setup MCPs (per-MCP; filesystem uses system Python, memory-gateway uses a venv)
├── Step 3: Install skills (recursive copy with SHA-256 check; preserves skill-name/SKILL.md structure)
├── Step 4: Render config.json (skip if byte-for-byte match; normalize \ to /)
└── Step 5: Verify (health check, return Ok or list of failures)
```

Each step is independently testable and idempotent. See [docs/how-it-works.md](docs/how-it-works.md) for details.

## Test framework

Custom assertion library in pure PowerShell (no Pester dependency). Tests are scripts that throw on failure. The runner runs all `*.tests.ps1` files and reports pass/fail. The plugin itself uses vitest (committed dependency); the bootstrap tests are pure PS to keep the bootstrap zero-dep.

## Why this approach

- **Git for state**: skills, plugin source, and UA core are all versioned in git, giving history and a backup.
- **PowerShell for setup**: works on native Windows without WSL or Docker.
- **Templates for config**: machine-specific paths are substituted at runtime, not hardcoded. JSON-on-Windows convention uses forward slashes — substitution normalizes backslashes to forward slashes automatically.
- **No external services**: no CI, no cloud storage, no auth required. Pure local.
- **Vendored dependencies**: the plugin's UA core is checked in (under `vendor/`) so the kit is one clone, no separate UA checkout needed.

## Why "no UA core clone" was the right call

The plugin's `package.json` has a `file:../...` dep on UA core. We could have required the user to have UA checked out alongside, but that violates "one command, no external clones". Vendoring is the trade-off: ~0.7 MB of extra repo size in exchange for true self-containment. To upgrade UA, the user edits the `file:../vendor/understand-anything-core` path (e.g. to a `git+ssh` URL once UA is published, or to a new vendored snapshot).
