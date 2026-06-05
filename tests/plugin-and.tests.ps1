. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/plugin.ps1"

$fixture = Join-Path $PSScriptRoot "fixtures/plugin"
$distFile = Join-Path $fixture "dist/index.js"
$distDir = Join-Path $fixture "dist"

if (Test-Path $distFile) { Remove-Item $distFile -Force }
if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }

# Test: Build-Plugin handles && in build command (PS 5.1 iex doesn't parse &&).
# First powershell writes a marker; second must still run because first exits 0.
# This is the exact pattern from setup.ps1 (bun install && bun run build).
$step1 = 'powershell -NoProfile -Command "New-Item -ItemType Directory -Path dist -Force | Out-Null"'
$step2 = 'powershell -NoProfile -Command "Set-Content -LiteralPath dist/index.js -Value ''export default {};''"'
$cmd = "$step1 && $step2"

try {
    Build-Plugin -PluginDir $fixture -BuildCommand $cmd 2>&1 | Out-Null
    Assert-True (Test-Path $distFile) "Build with && should produce dist/index.js (second step should run after first succeeds)"
} catch {
    Assert-True $false "Build with && should not throw on PS 5.1: $_"
}

# Cleanup
if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }

Write-Host "plugin-and.test.ps1: OK"
