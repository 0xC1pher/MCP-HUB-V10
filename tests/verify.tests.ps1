. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/verify.ps1"

# Test: Test-ConfigJsonValid returns true for valid JSON
$validJson = Join-Path $env:TEMP "ua-test-valid-$(Get-Random).json"
Set-Content -LiteralPath $validJson -Value '{"a": 1}' -Encoding UTF8
Assert-True (Test-ConfigJsonValid -Path $validJson) "Valid JSON should pass"
Remove-Item $validJson -Force

# Test: Test-ConfigJsonValid returns false for invalid JSON
$invalidJson = Join-Path $env:TEMP "ua-test-invalid-$(Get-Random).json"
Set-Content -LiteralPath $invalidJson -Value '{not valid' -Encoding UTF8
Assert-False (Test-ConfigJsonValid -Path $invalidJson) "Invalid JSON should fail"
Remove-Item $invalidJson -Force

# Test: Test-FileReachable returns true for existing file
$existing = Join-Path $PSScriptRoot "fixtures/config-template.json"
Assert-True (Test-FileReachable -Path $existing) "Existing file should be reachable"

# Test: Test-FileReachable returns false for missing file
$missing = Join-Path $env:TEMP "ua-missing-$(Get-Random).txt"
Assert-False (Test-FileReachable -Path $missing) "Missing file should not be reachable"

Write-Host "verify.tests.ps1: OK"
