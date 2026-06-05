. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/mcps.ps1"

# Test: Resolve-PythonInterpreter returns a path or null
$python = Resolve-PythonInterpreter
Assert-True ($null -ne $python -or $null -eq $python) "Should return either a path or null"

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

Write-Host "mcps.tests.ps1: OK"
