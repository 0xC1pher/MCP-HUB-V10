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
$realSubsts["MCP_HUB_V8_VENV_PYTHON"] = "C:/test/venv/Scripts/python.exe"
$realSubsts["MCP_HUB_V8_SERVER_PY"] = "C:/test/server.py"
Render-Config -TemplatePath $prodTmpl -Substitutions $realSubsts -OutputPath $renderedOut
$renderedContent = Get-Content $renderedOut -Raw
try {
    $null = ConvertFrom-Json $renderedContent
} catch {
    throw "Rendered config from prod template with real substitutions is not valid JSON: $_"
}
Remove-Item $renderedOut -Force

Write-Host "config.tests.ps1: OK"
