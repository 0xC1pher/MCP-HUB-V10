# Adding a new MCP

To add a new MCP to the bootstrap:

## 1. Add the MCP definition to `templates/config.json.tmpl`

```json
{
  "mcp": {
    "my-new-mcp": {
      "type": "local",
      "command": "{{MY_NEW_MCP_COMMAND}}",
      "args": ["{{MY_NEW_MCP_ARG}}"]
    }
  }
}
```

Use forward slashes in path placeholders (e.g. `C:/path/to/command`). The substitution layer accepts backslashes too but normalizes them.

## 2. Add placeholder substitutions in `bootstrap/lib/config.ps1`

In `Get-ConfigSubstitutions`, add the default:

```powershell
$substs["MY_NEW_MCP_COMMAND"] = "C:/default/path/to/command"
$substs["MY_NEW_MCP_ARG"] = "C:/default/path/to/arg"
```

For user-overridable paths, read from `bootstrap/.env`:

```powershell
if ($envContent.ContainsKey("MY_NEW_MCP_PATH")) {
    $substs["MY_NEW_MCP_COMMAND"] = $envContent["MY_NEW_MCP_PATH"]
}
```

Remember: the substitution layer normalizes backslashes → forward slashes, so users can use either in `.env`.

## 3. If the MCP needs setup (venv, pip install, etc.), add to `bootstrap/setup.ps1`

```powershell
$mcps = @{
    "my-new-mcp" = @{
        venvPath = "{{MY_NEW_MCP_VENV_PATH}}"
        requirementsPath = "{{MY_NEW_MCP_REQUIREMENTS}}"
    }
}
foreach ($name in $mcps.Keys) {
    Setup-MCP -Name $name -Config $mcps[$name]
}
```

For MCPs that don't need setup (e.g. just shelling out to an existing binary), you can skip the `mcps` hashtable entry and just have the config rendered.

## 4. Update tests if needed

If the new MCP requires new logic in any library, add tests to the corresponding `*.tests.ps1` file. The tests are scripts that throw on failure; the runner reports pass/fail per file.

## 5. Update the verification step

`Test-Install` in `bootstrap/lib/verify.ps1` checks that the rendered config has valid JSON, the plugin dist exists, and skills are present. It doesn't currently verify per-MCP connectivity. If your new MCP needs a specific health check, add a function in `verify.ps1` and call it from `Test-Install`.

## 6. Commit and test

```powershell
git add templates/ bootstrap/ tests/ docs/
git commit -m "feat(mcps): add my-new-mcp"
.\tests\run-all.ps1
.\bootstrap\setup.ps1
```
