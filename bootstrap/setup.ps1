# Dev-Bootstrap entry point. Run from the repo root.
# Usage: .\bootstrap\setup.ps1

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$version = Get-Content -LiteralPath (Join-Path $repoRoot "version.txt") -Raw
$version = $version.Trim()

# Source libraries
. "$PSScriptRoot/lib/common.ps1"
. "$PSScriptRoot/lib/plugin.ps1"
. "$PSScriptRoot/lib/mcps.ps1"
. "$PSScriptRoot/lib/skills.ps1"
. "$PSScriptRoot/lib/config.ps1"
. "$PSScriptRoot/lib/verify.ps1"

# Initialize logging
Initialize-Logging -LogPath (Join-Path $repoRoot "bootstrap/setup.log")

# Banner
Write-Host (Write-Banner -Version $version)

# Prereq checks
$prereqs = @(
    @{ Name = "PowerShell 5.1+"; Check = { $PSVersionTable.PSVersion.Major -ge 5 } }
    @{ Name = "git";            Check = { (Get-Command git -ErrorAction SilentlyContinue) -ne $null } }
    @{ Name = "bun";            Check = { (Get-Command bun -ErrorAction SilentlyContinue) -ne $null } }
    @{ Name = "node";           Check = { (Get-Command node -ErrorAction SilentlyContinue) -ne $null } }
    @{ Name = "python3";        Check = { (Get-Command python3 -ErrorAction SilentlyContinue) -ne $null -or (Get-Command python -ErrorAction SilentlyContinue) -ne $null } }
)

foreach ($p in $prereqs) {
    try {
        if (& $p.Check) {
            Write-Log -Level "INFO" -Message "Prereq OK: $($p.Name)"
        } else {
            throw "Prereq missing: $($p.Name)"
        }
    } catch {
        Write-Host "MISSING: $($p.Name)" -ForegroundColor Red
        Write-Host "  Please install it and re-run setup." -ForegroundColor Yellow
        exit 1
    }
}

# Step 1: Build plugin
$pluginDir = Join-Path $repoRoot "opencode-ua-plugin"
$pluginBuildCmd = "bun install && bun run build"
Build-Plugin -PluginDir $pluginDir -BuildCommand $pluginBuildCmd

# Step 2: Setup MCPs
$mcps = @{
    filesystem = @{
        venvPath = $null
        requirementsPath = $null
    }
    "yari-mcp-v8" = @{
        venvPath = "{{MCP_HUB_V8_VENV_PATH}}"
        requirementsPath = "{{MCP_HUB_V8_REQUIREMENTS}}"
    }
}
foreach ($name in $mcps.Keys) {
    Setup-MCP -Name $name -Config $mcps[$name]
}

# Step 3: Install skills
$skillsSource = Join-Path $repoRoot "skills"
$skillsDest = Get-SkillsDestination -UserHome $env:USERPROFILE
Install-Skills -SourceDir $skillsSource -DestinationDir $skillsDest

# Step 4: Render config
$tmpl = Join-Path $repoRoot "templates/config.json.tmpl"
$substs = Get-ConfigSubstitutions
$configOut = Join-Path $env:USERPROFILE ".opencode/config.json"

# Compute the rendered content for idempotency check
$renderedContent = Get-Content -LiteralPath $tmpl -Raw
foreach ($key in $substs.Keys) {
    $renderedContent = $renderedContent.Replace("{{$key}}", $substs[$key])
}

if (Test-ConfigMatches -OutputPath $configOut -ExpectedContent $renderedContent) {
    Write-Log -Level "INFO" -Message "Config already matches, skipping write"
} else {
    Render-Config -TemplatePath $tmpl -Substitutions $substs -OutputPath $configOut
}

# Step 5: Verify
$pluginDist = Join-Path $pluginDir "dist/index.js"
$result = Test-Install -ConfigPath $configOut -PluginDistPath $pluginDist -SkillsDir $skillsDest
if ($result.Ok) {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  Setup complete!" -ForegroundColor Green
    Write-Host "  Config: $configOut" -ForegroundColor Green
    Write-Host "  Plugin: $pluginDir" -ForegroundColor Green
    Write-Host "  Skills: $skillsDest" -ForegroundColor Green
    Write-Host "  Log:    $(Join-Path $repoRoot 'bootstrap/setup.log')" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Setup completed with failures:" -ForegroundColor Red
    foreach ($f in $result.Failures) {
        Write-Host "  - $f" -ForegroundColor Red
    }
    exit 1
}
