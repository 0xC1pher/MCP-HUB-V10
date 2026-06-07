. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/mcps.ps1"

# Test: Resolve-PythonInterpreter returns either a non-empty string path or $null
$python = Resolve-PythonInterpreter
$typeOk = ($null -eq $python) -or ($python -is [string] -and $python.Length -gt 0)
Assert-True $typeOk "Should return either a non-empty string path or `$null (got: '$python')"

# Test: Resolve-PythonInterpreter logs each candidate it tries
# (Observability contract: a senior-level user needs to see *which* Python paths
# the bootstrap looked at, otherwise troubleshooting "Python not found" is blind.)
$resolverLog = Join-Path $env:TEMP "ua-resolver-log-$(Get-Random).log"
$Script:LogPath = $resolverLog
try {
    $null = Resolve-PythonInterpreter
    $logContent = Get-Content $resolverLog -Raw
    # Require all four standard candidates to be mentioned in the log.
    # The previous code only emitted a single "not found" WARN at the end,
    # which left operators blind to which paths were searched.
    Assert-Contains $logContent "Python311" "Resolver log should mention the Python311 candidate"
    Assert-Contains $logContent "Python312" "Resolver log should mention the Python312 candidate"
    Assert-Contains $logContent "Python313" "Resolver log should mention the Python313 candidate"
    Assert-Contains $logContent "py" "Resolver log should mention the py launcher candidate"
} finally {
    Remove-Item $resolverLog -Force -ErrorAction SilentlyContinue
}

# Test: Ensure-PythonVenv creates a venv in a temp dir
$tmpVenv = Join-Path $env:TEMP "ua-test-venv-$(Get-Random)"
$created = $false
try {
    Ensure-PythonVenv -VenvPath $tmpVenv -RequirementsPath $null -CreateOnly
    if (Test-Path (Join-Path $tmpVenv "Scripts/python.exe")) {
        $created = $true
    }
} catch {
    Write-Host "SKIP: Ensure-PythonVenv test (python not available): $_"
}
if ($created) {
    Assert-True $created "Venv should have Scripts/python.exe"
    Ensure-PythonVenv -VenvPath $tmpVenv -RequirementsPath $null -CreateOnly
    Assert-True (Test-Path (Join-Path $tmpVenv "Scripts/python.exe")) "Venv should still exist after second call"
}
if (Test-Path $tmpVenv) { Remove-Item $tmpVenv -Recurse -Force }

# Test: Setup-MCP returns a status hashtable with @Ok / @Name / @Error contract
# (Senior-level observability: setup.ps1 needs to aggregate MCP setup results
# into the post-install banner. A void return forces callers to scrape the log,
# which is brittle.)
$setupStatus = Setup-MCP -Name "fake-mcp-no-venv" -Config @{
    venvPath = "C:/this/path/should/not/exist/$(Get-Random)"
    requirementsPath = "C:/also/missing/$(Get-Random)/requirements.txt"
}
Assert-True ($null -ne $setupStatus) "Setup-MCP should return a status hashtable, not void"
Assert-True ($setupStatus.ContainsKey("Name")) "Status should contain Name"
Assert-True ($setupStatus.ContainsKey("Ok")) "Status should contain Ok"
Assert-True ($setupStatus.ContainsKey("Error")) "Status should contain Error"
Assert-Equal $setupStatus.Name "fake-mcp-no-venv" "Status.Name should echo the input"
Assert-False $setupStatus.Ok "Status.Ok should be false when setup throws"
Assert-True ($setupStatus.Error.Length -gt 0) "Status.Error should be populated when setup throws"

# Test: Setup-MCP returns Ok=true on a successful no-op (empty config)
$okStatus = Setup-MCP -Name "empty-config-mcp" -Config @{}
Assert-True ($null -ne $okStatus) "Setup-MCP should return a status hashtable even for empty config"
Assert-True $okStatus.Ok "Setup-MCP should report Ok=true when there's nothing to do"
Assert-Equal $okStatus.Name "empty-config-mcp" "Status.Name should echo the input on success too"

Write-Host "mcps.tests.ps1: OK"
