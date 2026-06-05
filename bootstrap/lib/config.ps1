. "$PSScriptRoot/common.ps1"

function Get-ConfigSubstitutions {
    $substs = @{
        USERPROFILE = $env:USERPROFILE
        SCHEMA = "https://opencode.ai/config.json"
        PLUGIN_PATH = Join-Path $env:USERPROFILE "Desktop\tools\opencode-ua-plugin\dist\index.js"
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
    Set-Content -LiteralPath $OutputPath -Value $content -Encoding UTF8
    Write-Log -Level "INFO" -Message "Config rendered successfully"
}

function Test-ConfigMatches {
    param(
        [string]$OutputPath,
        [string]$ExpectedContent
    )
    if (-not (Test-Path -LiteralPath $OutputPath)) { return $false }
    $actual = Get-Content -LiteralPath $OutputPath -Raw
    return ($actual -eq $ExpectedContent)
}
