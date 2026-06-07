. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/config.ps1"

$tmpl = Join-Path $PSScriptRoot "fixtures/config-template.json"
$out = Join-Path $env:TEMP "ua-test-config-$(Get-Random).json"
$substs = @{
    SCHEMA = "https://opencode.ai/config.json"
    PLUGIN_PATH = "C:\Users\Test\Desktop\tools\opencode-ua-plugin\dist\index.js"
}

# Test: Render-Config substitutes placeholders
Render-Config -TemplatePath $tmpl -Substitutions $substs -OutputPath $out
Assert-FileExists $out "Output file should be created"
$content = Get-Content $out -Raw
Assert-Contains $content "https://opencode.ai/config.json" "Should substitute SCHEMA"
Assert-Contains $content "C:\Users\Test\Desktop" "Should substitute PLUGIN_PATH"
Assert-False ($content.Contains("{{")) "Should not contain unsubstituted placeholders"

# Test: idempotency -- Test-ConfigMatches
Assert-True (Test-ConfigMatches -OutputPath $out -ExpectedContent $content) "Should match identical content"
$different = $content.Replace("https", "http")
Assert-False (Test-ConfigMatches -OutputPath $out -ExpectedContent $different) "Should not match different content"

# Cleanup
Remove-Item $out -Force

# Test: Get-ConfigSubstitutions normalizes backslashes to forward slashes
$realSubsts = Get-ConfigSubstitutions
Assert-True ($null -ne $realSubsts) "Get-ConfigSubstitutions should return a hashtable"
Assert-False ($realSubsts["USERPROFILE"].Contains("\")) "USERPROFILE should be normalized to forward slashes"
Assert-False ($realSubsts["PLUGIN_PATH"].Contains("\")) "PLUGIN_PATH should be normalized to forward slashes"
Assert-False ($realSubsts["PYTHON_EXE"].Contains("\")) "PYTHON_EXE should be normalized to forward slashes"

# Test: Get-ConfigSubstitutions output produces valid JSON when applied to template
$prodTmpl = Join-Path $PSScriptRoot "..\templates\config.json.tmpl"
$renderedOut = Join-Path $env:TEMP "ua-test-rendered-$(Get-Random).json"
$realSubsts["MCP_HUB_V12_VENV_PYTHON"] = "C:/test/venv/Scripts/python.exe"
$realSubsts["MCP_HUB_V12_REPO_PATH"] = "C:/test/repo"
Render-Config -TemplatePath $prodTmpl -Substitutions $realSubsts -OutputPath $renderedOut
$renderedContent = Get-Content $renderedOut -Raw
try {
    $null = ConvertFrom-Json $renderedContent
} catch {
    throw "Rendered config from prod template with real substitutions is not valid JSON: $_"
}
Remove-Item $renderedOut -Force

# Test: Get-ConfigSubstitutions rejects empty values (MCP_HUB_V12_REPO_PATH= with no value)
# Bug: the previous regex only checked key presence, not value content. An
# entry like "MCP_HUB_V12_REPO_PATH=" would silently set the substitution to "" and
# bypass the fail-loud "unsubstituted placeholder" check, producing a broken config.
$emptyEnv = Join-Path $env:TEMP "ua-empty-env-$(Get-Random).env"
Set-Content -LiteralPath $emptyEnv -Value "MCP_HUB_V12_REPO_PATH=" -Encoding UTF8
try {
    $emptySubsts = Get-ConfigSubstitutions -EnvFile $emptyEnv
    $placeholderLeaked = $emptySubsts.ContainsKey("MCP_HUB_V12_REPO_PATH") -and
        ($emptySubsts["MCP_HUB_V12_REPO_PATH"] -match "^\{\{.*\}\}$")
    Assert-True $placeholderLeaked "Empty value for MCP_HUB_V12_REPO_PATH should keep the placeholder, not silently store an empty string"
} finally {
    Remove-Item $emptyEnv -Force -ErrorAction SilentlyContinue
}

# Test: Get-ConfigSubstitutions -EnvFile param lets tests point at isolated .env files
$isolatedEnv = Join-Path $env:TEMP "ua-isolated-env-$(Get-Random).env"
Set-Content -LiteralPath $isolatedEnv -Value "MCP_HUB_V12_REPO_PATH=C:/from/isolated/env`nMCP_HUB_V12_VENV_PYTHON=C:/from/isolated/venv/Scripts/python.exe" -Encoding UTF8
try {
    $isolatedSubsts = Get-ConfigSubstitutions -EnvFile $isolatedEnv
    Assert-Equal $isolatedSubsts["MCP_HUB_V12_REPO_PATH"] "C:/from/isolated/env" "EnvFile param should override the default env lookup"
    Assert-Equal $isolatedSubsts["MCP_HUB_V12_VENV_PYTHON"] "C:/from/isolated/venv/Scripts/python.exe" "EnvFile param should load all keys from the provided file"
} finally {
    Remove-Item $isolatedEnv -Force -ErrorAction SilentlyContinue
}

# Test: Get-ConfigSubstitutions -EnvFile param with whitespace-only value should also be rejected
$wsEnv = Join-Path $env:TEMP "ua-ws-env-$(Get-Random).env"
Set-Content -LiteralPath $wsEnv -Value "MCP_HUB_V12_REPO_PATH=   " -Encoding UTF8
try {
    $wsSubsts = Get-ConfigSubstitutions -EnvFile $wsEnv
    $placeholderLeaked = $wsSubsts.ContainsKey("MCP_HUB_V12_REPO_PATH") -and
        ($wsSubsts["MCP_HUB_V12_REPO_PATH"] -match "^\{\{.*\}\}$")
    Assert-True $placeholderLeaked "Whitespace-only value should be treated as empty"
} finally {
    Remove-Item $wsEnv -Force -ErrorAction SilentlyContinue
}

Write-Host "config.tests.ps1: OK"
