# Simulates a build: writes a marker file
$distDir = Join-Path $PSScriptRoot "dist"
New-Item -ItemType Directory -Path $distDir -Force | Out-Null
Set-Content -LiteralPath (Join-Path $distDir "index.js") -Value "export default {};"
