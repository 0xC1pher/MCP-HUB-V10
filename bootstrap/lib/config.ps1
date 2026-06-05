. "$PSScriptRoot/common.ps1"

function Get-ConfigSubstitutions {
    param(
        [string]$PluginPath = (Join-Path $env:USERPROFILE "Desktop\tools\opencode-ua-plugin\dist\index.js")
    )
    $substs = @{
        USERPROFILE = $env:USERPROFILE
        SCHEMA = "https://opencode.ai/config.json"
        PLUGIN_PATH = $PluginPath
        PYTHON_EXE = "C:\Program Files\Python311\python.exe"
    }
    $envFile = Join-Path $PSScriptRoot "..\\.env"
    if (Test-Path -LiteralPath $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^(\w+)=(.*)$") {
                $substs[$Matches[1]] = $Matches[2]
            }
        }
    }
    if (-not $substs.ContainsKey("MCP_HUB_V8_VENV_PYTHON")) {
        $substs["MCP_HUB_V8_VENV_PYTHON"] = "{{MCP_HUB_V8_VENV_PYTHON}}"
    }
    if (-not $substs.ContainsKey("MCP_HUB_V8_SERVER_PY")) {
        $substs["MCP_HUB_V8_SERVER_PY"] = "{{MCP_HUB_V8_SERVER_PY}}"
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
