. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/plugin.ps1"

# Build a tiny fake "core" package in a temp dir.
# It has a package.json with "build: tsc" and a single .ts file that compiles cleanly.
$tmp = Join-Path $env:TEMP "ua-test-core-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
try {
    $src = Join-Path $tmp "src"
    New-Item -ItemType Directory -Path $src -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $src "index.ts") -Value "export const x: number = 1;`nexport default x;`n"
    @'
{
  "name": "fake-core",
  "version": "0.0.0",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": { "build": "tsc" },
  "devDependencies": { "typescript": "^5.7.0" }
}
'@ | Set-Content -LiteralPath (Join-Path $tmp "package.json")
    @'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "declaration": true,
    "outDir": "dist",
    "rootDir": "src",
    "skipLibCheck": true
  },
  "include": ["src"]
}
'@ | Set-Content -LiteralPath (Join-Path $tmp "tsconfig.json")

    # Sanity: not built yet
    Assert-False (Test-PluginCoreBuilt -CoreDir $tmp) "Fresh core should not be reported as built"

    # Build it
    Build-PluginCore -CoreDir $tmp
    Assert-True (Test-Path (Join-Path $tmp "dist/index.js")) "Core build should produce dist/index.js"
    Assert-True (Test-Path (Join-Path $tmp "dist/index.d.ts")) "Core build should produce dist/index.d.ts"

    # Idempotency: second call should be a no-op (no throw, no error)
    Build-PluginCore -CoreDir $tmp
    Assert-True (Test-PluginCoreBuilt -CoreDir $tmp) "Core should still be reported as built after second call"
} finally {
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
}

Write-Host "plugin-core.tests.ps1: OK"
