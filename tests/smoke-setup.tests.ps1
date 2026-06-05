. "$PSScriptRoot/lib/assert.ps1"

$tokens = $null
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile(
    "$PSScriptRoot\..\bootstrap\setup.ps1", [ref]$tokens, [ref]$errors) | Out-Null
Assert-Equal $errors.Count 0 "setup.ps1 should parse with no errors"

if ($errors.Count -gt 0) {
    foreach ($e in $errors) {
        Write-Host "  parse error: $e" -ForegroundColor Red
    }
}

Write-Host "smoke-setup.tests.ps1: OK"
