. "$PSScriptRoot/common.ps1"

function Test-PluginBuilt {
    param([string]$PluginDir)
    $distFile = Join-Path $PluginDir "dist/index.js"
    return (Test-Path -LiteralPath $distFile)
}

function Build-Plugin {
    param(
        [string]$PluginDir,
        [string]$BuildCommand
    )
    if (Test-PluginBuilt -PluginDir $PluginDir) {
        $distFile = Get-Item (Join-Path $PluginDir "dist/index.js")
        $sourceFiles = Get-ChildItem -Path $PluginDir -Recurse -Include "*.ts", "*.json", "*.ps1" |
            Where-Object { $_.FullName -notlike "*/dist/*" -and $_.FullName -notlike "*/node_modules/*" }
        $needsBuild = $false
        foreach ($src in $sourceFiles) {
            if ($src.LastWriteTime -gt $distFile.LastWriteTime) {
                $needsBuild = $true
                break
            }
        }
        if (-not $needsBuild) {
            Write-Log -Level "INFO" -Message "Plugin already built (dist is fresh), skipping"
            return
        }
    }

    Write-Log -Level "INFO" -Message "Building plugin at $PluginDir"
    Push-Location $PluginDir
    try {
        iex $BuildCommand
        if ($LASTEXITCODE -ne 0) {
            throw "Build command failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
    Write-Log -Level "INFO" -Message "Plugin built successfully"
}
