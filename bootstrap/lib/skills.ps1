. "$PSScriptRoot/common.ps1"

function Get-SkillsDestination {
    param([string]$UserHome)
    # OpenCode on Windows reads from %USERPROFILE%\.config\opencode\ (XDG-style,
    # matching Linux). The legacy ~/.opencode/skills path is only kept as a
    # fallback for machines that already have it; the default install targets
    # the modern location so skills are visible to opencode.
    $primary  = Join-Path $UserHome ".config/opencode/skills"
    $fallback = Join-Path $UserHome ".opencode/skills"
    if (Test-Path -LiteralPath $primary)  { return $primary }
    if (Test-Path -LiteralPath $fallback) { return $fallback }
    return $primary
}

function Get-SHA256OfFile {
    # Wrapper that returns just the hex string. Renamed from Get-FileHash
    # to avoid shadowing the built-in Get-FileHash cmdlet (PS 5.1 collision).
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    }
    return $null
}

function Install-Skills {
    # Install skills as a Windows directory junction (symlink equivalent) so
    # updates to the source are immediately visible in any project the user
    # opens. This is the whole point of moving off the copy model: a
    # bootstrap-driven dev machine should not have a stale skill snapshot.
    param(
        [string]$SourceDir,
        [string]$DestinationDir
    )

    if (-not (Test-Path -LiteralPath $SourceDir)) {
        throw "Skills source dir does not exist: $SourceDir"
    }

    $parent = Split-Path -Parent $DestinationDir
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        Write-Log -Level "INFO" -Message "Created parent dir: $parent"
    }

    # Idempotent: if a junction already points at this source, do nothing.
    if (Test-Path -LiteralPath $DestinationDir) {
        $item = Get-Item -LiteralPath $DestinationDir -Force
        $isReparse = $item.Attributes -band [IO.FileAttributes]::ReparsePoint
        if ($isReparse) {
            $existingTarget = (Get-Item -LiteralPath $DestinationDir -Force).Target
            if ($existingTarget -eq $SourceDir) {
                Write-Log -Level "INFO" -Message "Skills junction already in place: $DestinationDir -> $SourceDir"
                return
            }
            Write-Log -Level "WARN" -Message "Junction target differs (existing: '$existingTarget', expected: '$SourceDir'); recreating"
            Remove-Item -LiteralPath $DestinationDir -Force
        } else {
            # Real directory, not a junction. Move it aside so we don't destroy
            # any user-placed skills; they can be merged back manually.
            $stamp = Get-Date -Format "yyyyMMddHHmmss"
            $backup = "$DestinationDir.bak-$stamp"
            Write-Log -Level "WARN" -Message "Destination is a real dir, not a junction. Backing up to $backup"
            Rename-Item -LiteralPath $DestinationDir -NewName (Split-Path -Leaf $backup)
        }
    }

    New-Item -ItemType Junction -Path $DestinationDir -Target $SourceDir | Out-Null
    Write-Log -Level "INFO" -Message "Skills junction created: $DestinationDir -> $SourceDir"
}

# Suppress unused warning for the SHA helper -- kept exported for any future
# caller that needs a content-hash without colliding with the built-in cmdlet.
$null = Get-SHA256OfFile
