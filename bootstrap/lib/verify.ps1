. "$PSScriptRoot/common.ps1"

function Test-ConfigJsonValid {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    try {
        $content = Get-Content -LiteralPath $Path -Raw
        $null = ConvertFrom-Json $content -ErrorAction Stop
        return $true
    } catch {
        Write-Log -Level "ERROR" -Message ("Invalid JSON in {0}: {1}" -f $Path, $_)
        return $false
    }
}

function Test-FileReachable {
    param([string]$Path)
    return (Test-Path -LiteralPath $Path)
}

function Test-Install {
    param(
        [string]$ConfigPath,
        [string]$PluginDistPath,
        [string]$SkillsDir
    )
    $failures = @()
    if (-not (Test-ConfigJsonValid -Path $ConfigPath)) {
        $failures += "Config JSON invalid: $ConfigPath"
    }
    if (-not (Test-FileReachable -Path $PluginDistPath)) {
        $failures += "Plugin dist not found: $PluginDistPath"
    }
    if (-not (Test-FileReachable -Path $SkillsDir)) {
        $failures += "Skills dir not found: $SkillsDir"
    }
    return @{
        Ok = ($failures.Count -eq 0)
        Failures = $failures
    }
}
