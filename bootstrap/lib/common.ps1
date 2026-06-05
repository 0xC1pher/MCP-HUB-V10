# Dev-Bootstrap common library: logging, prereq checks, banner.

$Script:LogPath = $null

function Write-Banner {
    param([string]$Version)
    @"
==================================================
  Dev-Bootstrap v$Version
  Portable OpenCode configuration
==================================================
"@
}

function Test-Prereq {
    param(
        [string]$Command,
        [string]$Argument = "--version",
        [switch]$ShouldThrow
    )
    $found = $null
    try {
        $found = Get-Command $Command -ErrorAction Stop
    } catch {
        $msg = "Prerequisite not found: $Command. Please install it and re-run."
        if ($ShouldThrow) { throw $msg } else { return $false }
    }
    if ($null -eq $found) {
        $msg = "Prerequisite not found: $Command. Please install it and re-run."
        if ($ShouldThrow) { throw $msg } else { return $false }
    }
    return $true
}

function Write-Log {
    param(
        [ValidateSet("DEBUG", "INFO", "WARN", "ERROR")]
        [string]$Level = "INFO",
        [string]$Message
    )
    if ([string]::IsNullOrEmpty($Script:LogPath)) { return }
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    $line = "[$timestamp] [$Level] $Message"
    Add-Content -LiteralPath $Script:LogPath -Value $line
    switch ($Level) {
        "WARN"  { Write-Host $line -ForegroundColor Yellow }
        "ERROR" { Write-Host $line -ForegroundColor Red }
        default { Write-Host $line -ForegroundColor Gray }
    }
}

function Initialize-Logging {
    param([string]$LogPath)
    $Script:LogPath = $LogPath
    if (Test-Path -LiteralPath $LogPath) { Remove-Item $LogPath -Force }
    New-Item -ItemType File -Path $LogPath -Force | Out-Null
}
