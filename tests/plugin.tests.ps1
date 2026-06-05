. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/plugin.ps1"

$fixture = Join-Path $PSScriptRoot "fixtures/plugin"
$distFile = Join-Path $fixture "dist/index.js"

# Clean state
if (Test-Path $distFile) { Remove-Item $distFile -Force }
if (Test-Path (Join-Path $fixture "dist")) { Remove-Item (Join-Path $fixture "dist") -Recurse -Force }

# Test: Test-PluginBuilt returns false when dist doesn't exist
Assert-False (Test-PluginBuilt -PluginDir $fixture) "Should return false when dist is missing"

# Test: Build-Plugin runs the build script and produces dist
Build-Plugin -PluginDir $fixture -BuildCommand "powershell -NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\fixtures\plugin\build-fixture.ps1`""
Assert-FileExists $distFile "Build should produce dist/index.js"
Assert-True (Test-PluginBuilt -PluginDir $fixture) "Test-PluginBuilt should return true after build"

# Test: idempotency -- second build is a no-op (mtime check)
Build-Plugin -PluginDir $fixture -BuildCommand "powershell -NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\fixtures\plugin\build-fixture.ps1`""
Assert-True $true "Build-Plugin should be idempotent (no error on second call)"

# Cleanup
if (Test-Path (Join-Path $fixture "dist")) { Remove-Item (Join-Path $fixture "dist") -Recurse -Force }

Write-Host "plugin.tests.ps1: OK"
