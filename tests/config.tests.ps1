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

Write-Host "config.tests.ps1: OK"
