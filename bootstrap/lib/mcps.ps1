. "$PSScriptRoot/common.ps1"

function Resolve-PythonInterpreter {
    $candidates = @(
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python313\python.exe",
        "py"
    )
    foreach ($c in $candidates) {
        # Log every candidate we try so operators can see *which* paths were
        # searched. The previous code only emitted a single "not found" WARN
        # at the end, which left troubleshooting blind.
        $label = if ($c -eq "py") { "py launcher (-3.11)" } else { $c }
        Write-Log -Level "INFO" -Message "Trying Python candidate: $label"
        try {
            if ($c -eq "py") {
                $out = & py -3.11 -c "import sys; print(sys.executable)" 2>$null
            } else {
                if (-not (Test-Path $c)) {
                    Write-Log -Level "INFO" -Message "Skipping $c (not found)"
                    continue
                }
                $out = & $c -c "import sys; print(sys.executable)" 2>$null
            }
            if ($LASTEXITCODE -eq 0 -and $out) {
                Write-Log -Level "INFO" -Message "Resolved Python: $($out.Trim())"
                return $out.Trim()
            }
        } catch {
            Write-Log -Level "INFO" -Message "Candidate $c threw: $_"
            continue
        }
    }
    Write-Log -Level "WARN" -Message "Python 3.11+ not found in standard locations"
    return $null
}

function Ensure-PythonVenv {
    param(
        [string]$VenvPath,
        [string]$RequirementsPath,
        [switch]$CreateOnly
    )
    $pythonExe = Join-Path $VenvPath "Scripts/python.exe"
    if (Test-Path -LiteralPath $pythonExe) {
        Write-Log -Level "INFO" -Message "Venv already exists at $VenvPath, skipping creation"
    } else {
        Write-Log -Level "INFO" -Message "Creating venv at $VenvPath"
        $python = Resolve-PythonInterpreter
        if ($null -eq $python) { throw "Python not found; cannot create venv at $VenvPath" }
        & $python -m venv $VenvPath
        if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
    }

    if ($CreateOnly) { return }
    if ($RequirementsPath -and (Test-Path -LiteralPath $RequirementsPath)) {
        Write-Log -Level "INFO" -Message "Installing requirements from $RequirementsPath"
        & $pythonExe -m pip install -r $RequirementsPath
        if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
    }
}

function Setup-MCP {
    param(
        [string]$Name,
        [hashtable]$Config
    )
    Write-Log -Level "INFO" -Message "Setting up MCP: $Name"
    try {
        $venvPath = $null
        $reqPath = $null
        if ($Config.ContainsKey("venvPath")) { $venvPath = $Config.venvPath }
        if ($Config.ContainsKey("requirementsPath")) { $reqPath = $Config.requirementsPath }
        if ($venvPath -and $reqPath) {
            Ensure-PythonVenv -VenvPath $venvPath -RequirementsPath $reqPath
        }
        Write-Log -Level "INFO" -Message "MCP $Name setup complete"
        return @{
            Name = $Name
            Ok = $true
            Error = $null
        }
    } catch {
        Write-Log -Level "ERROR" -Message "MCP $Name setup failed: $_"
        return @{
            Name = $Name
            Ok = $false
            Error = "$_"
        }
    }
}
