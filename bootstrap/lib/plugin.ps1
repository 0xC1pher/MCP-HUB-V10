. "$PSScriptRoot/common.ps1"

function Test-PluginBuilt {
    param([string]$PluginDir)
    $distFile = Join-Path $PluginDir "dist/index.js"
    return (Test-Path -LiteralPath $distFile)
}

function Test-PluginCoreBuilt {
    param([string]$CoreDir)
    $distFile = Join-Path $CoreDir "dist/index.js"
    return (Test-Path -LiteralPath $distFile)
}

function Get-PluginSourceFiles {
    # Exclude both dist/ and node_modules/. Use StartsWith on a normalized
    # path so it works on Windows (backslashes) and Unix (forward slashes).
    param([string]$PluginDir)
    $distDir = (Join-Path $PluginDir "dist").TrimEnd("\", "/")
    $nodeModulesDir = (Join-Path $PluginDir "node_modules").TrimEnd("\", "/")
    Get-ChildItem -Path $PluginDir -Recurse -Include "*.ts", "*.json", "*.ps1" |
        Where-Object {
            $path = $_.FullName.TrimEnd("\", "/")
            -not $path.StartsWith($distDir, [System.StringComparison]::OrdinalIgnoreCase) -and
            -not $path.StartsWith($nodeModulesDir, [System.StringComparison]::OrdinalIgnoreCase)
        }
}

function Build-PluginCore {
    param([string]$CoreDir)
    if (Test-PluginCoreBuilt -CoreDir $CoreDir) {
        Write-Log -Level "INFO" -Message "Plugin core already built, skipping"
        return
    }
    Write-Log -Level "INFO" -Message "Building plugin core at $CoreDir"
    Push-Location $CoreDir
    try {
        cmd /c "bun install"
        if ($LASTEXITCODE -ne 0) {
            throw "Core bun install failed with exit code $LASTEXITCODE"
        }
        cmd /c "bun run build"
        if ($LASTEXITCODE -ne 0) {
            throw "Core build failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
    Write-Log -Level "INFO" -Message "Plugin core built successfully"
}

function Build-Plugin {
    param(
        [string]$PluginDir,
        [string]$BuildCommand
    )
    if (Test-PluginBuilt -PluginDir $PluginDir) {
        $distFile = Get-Item (Join-Path $PluginDir "dist/index.js")
        $sourceFiles = Get-PluginSourceFiles -PluginDir $PluginDir
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
        # Use cmd /c so build commands can use && and proper exit-code
        # propagation. PowerShell 5.1's Invoke-Expression (iex) doesn't
        # recognize && as a statement separator.
        cmd /c $BuildCommand
        if ($LASTEXITCODE -ne 0) {
            throw "Build command failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
    Write-Log -Level "INFO" -Message "Plugin built successfully"
}
