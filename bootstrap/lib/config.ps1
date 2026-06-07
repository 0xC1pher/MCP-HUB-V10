. "$PSScriptRoot/common.ps1"

function Get-ConfigSubstitutions {
    param(
        [string]$PluginPath = (Join-Path $env:USERPROFILE "Desktop\tools\opencode-ua-plugin\dist\index.js"),
        # Optional explicit path to the .env file. When omitted, falls back to
        # <repoRoot>/bootstrap/.env (the historical default). Tests pass an
        # isolated file to exercise this function without touching the real .env.
        [string]$EnvFile = (Join-Path (Split-Path -Parent $PSScriptRoot) ".env")
    )
    $substs = @{
        USERPROFILE = $env:USERPROFILE
        SCHEMA = "https://opencode.ai/config.json"
        PLUGIN_PATH = $PluginPath
        PYTHON_EXE = "C:\Program Files\Python311\python.exe"
    }
    if (Test-Path -LiteralPath $EnvFile) {
        Get-Content -LiteralPath $EnvFile | ForEach-Object {
            # Skip blanks and comments so users can document their .env.
            $line = $_
            if ([string]::IsNullOrWhiteSpace($line)) { return }
            if ($line -match "^\s*#") { return }
            if ($line -match "^(\w+)=(.*)$") {
                $key = $Matches[1]
                $value = $Matches[2]
                # Reject empty / whitespace-only values: the previous code stored
                # them as-is, which silently bypassed the fail-loud "unsubstituted
                # placeholder" check and produced a broken config. Keep the
                # placeholder so Render-Config throws a clear error.
                if ([string]::IsNullOrWhiteSpace($value)) {
                    Write-Log -Level "WARN" -Message "Ignoring empty value for '$key' in $EnvFile"
                    return
                }
                $substs[$key] = $value
            }
        }
    }
    if (-not $substs.ContainsKey("MCP_HUB_V12_REPO_PATH")) {
        $substs["MCP_HUB_V12_REPO_PATH"] = "{{MCP_HUB_V12_REPO_PATH}}"
    }
    if (-not $substs.ContainsKey("MCP_HUB_V12_VENV_PYTHON")) {
        $substs["MCP_HUB_V12_VENV_PYTHON"] = "{{MCP_HUB_V12_VENV_PYTHON}}"
    }
    foreach ($key in @($substs.Keys)) {
        $value = [string]$substs[$key]
        if ($value -match "\\") {
            $substs[$key] = $value.Replace("\", "/")
        }
    }
    return $substs
}

function Render-Config {
    param(
        [string]$TemplatePath,
        [hashtable]$Substitutions,
        [string]$OutputPath
    )
    Write-Log -Level "INFO" -Message "Rendering config from $TemplatePath to $OutputPath"
    $content = Get-Content -LiteralPath $TemplatePath -Raw
    foreach ($key in $Substitutions.Keys) {
        $placeholder = "{{$key}}"
        $content = $content.Replace($placeholder, $Substitutions[$key])
    }
    if ($content.Contains("{{")) {
        throw "Unsubstituted placeholders remain in rendered config: $content"
    }
    # Use -NoNewline: Set-Content on PS 5.1 adds a trailing newline by default,
    # which would make the file differ from the rendered content and break the
    # idempotency check.
    Set-Content -LiteralPath $OutputPath -Value $content -Encoding UTF8 -NoNewline
    Write-Log -Level "INFO" -Message "Config rendered successfully"
}

function Test-ConfigMatches {
    param(
        [string]$OutputPath,
        [string]$ExpectedContent
    )
    if (-not (Test-Path -LiteralPath $OutputPath)) { return $false }
    $actual = Get-Content -LiteralPath $OutputPath -Raw
    # Normalize trailing whitespace: PS 5.1 Set-Content/Get-Content can introduce
    # or strip trailing newlines depending on how the file was written, so a
    # strict byte comparison is brittle. Trim both sides for the check.
    return (($actual.TrimEnd("`r", "`n", " ")) -eq ($ExpectedContent.TrimEnd("`r", "`n", " ")))
}
