. "$PSScriptRoot/common.ps1"

function Get-SkillsDestination {
    param([string]$UserHome)
    $skillsPath = Join-Path $UserHome ".opencode/skills"
    if (Test-Path -LiteralPath $skillsPath) {
        $item = Get-Item -LiteralPath $skillsPath -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            return $item.Target
        }
    }
    return $skillsPath
}

function Get-FileHash {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    }
    return $null
}

function Install-Skills {
    param(
        [string]$SourceDir,
        [string]$DestinationDir
    )
    Write-Log -Level "INFO" -Message "Installing skills from $SourceDir to $DestinationDir"
    if (-not (Test-Path -LiteralPath $DestinationDir)) {
        New-Item -ItemType Directory -Path $DestinationDir -Force | Out-Null
    }
    $files = Get-ChildItem -LiteralPath $SourceDir -File
    $copied = 0
    $skipped = 0
    foreach ($f in $files) {
        $destFile = Join-Path $DestinationDir $f.Name
        $srcHash = Get-FileHash -Path $f.FullName
        $dstHash = Get-FileHash -Path $destFile
        if ($srcHash -eq $dstHash) {
            $skipped++
            continue
        }
        Copy-Item -LiteralPath $f.FullName -Destination $destFile -Force
        $copied++
    }
    Write-Log -Level "INFO" -Message "Skills: $copied copied, $skipped skipped (unchanged)"
}
