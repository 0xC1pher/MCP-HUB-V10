. "$PSScriptRoot/lib/assert.ps1"

# Portability contract: the bootstrap code must not depend on the developer
# machine's specific paths. A "fresh Windows install" must work as long as
# USERPROFILE is set and the user has populated bootstrap/.env.

$repoRoot = (Resolve-Path "$PSScriptRoot/..").Path
$bootstrapLib = Join-Path $repoRoot "bootstrap/lib"
$bootstrapScripts = Join-Path $repoRoot "bootstrap"
$envExample = Join-Path $bootstrapScripts ".env.example"

# Test 1: bootstrap/lib/*.ps1 must not contain literal "C:\Users\Admin" or
# "C:/Users/Admin" -- the code should be env-driven, not hardcoded.
# Single-quoted strings in PS treat backslashes literally (1 backslash, not 2).
$libFiles = Get-ChildItem -LiteralPath $bootstrapLib -Filter "*.ps1"
$forbidden = @('C:\Users\Admin', 'C:/Users/Admin')
foreach ($f in $libFiles) {
    $content = Get-Content -LiteralPath $f.FullName -Raw
    foreach ($bad in $forbidden) {
        if ($content.Contains($bad)) {
            throw "PORTABILITY VIOLATION: $($f.Name) contains literal '$bad'. " +
                  "Code must derive paths from `$env:USERPROFILE, not hardcode them."
        }
    }
}

# Test 2: bootstrap/setup.ps1 must not contain literal user paths
$setupScript = Join-Path $bootstrapScripts "setup.ps1"
$setupContent = Get-Content -LiteralPath $setupScript -Raw
foreach ($bad in $forbidden) {
    if ($setupContent.Contains($bad)) {
        throw "PORTABILITY VIOLATION: setup.ps1 contains literal '$bad'."
    }
}

# Test 3: bootstrap/.env.example must not contain literal user paths
# (it should only have empty placeholders for the user to fill in)
$envExampleContent = Get-Content -LiteralPath $envExample -Raw
foreach ($bad in $forbidden) {
    if ($envExampleContent.Contains($bad)) {
        throw "PORTABILITY VIOLATION: .env.example contains literal '$bad'."
    }
}

# Test 4: Get-ConfigSubstitutions must respect a mocked USERPROFILE.
# The default PLUGIN_PATH comes from `$env:USERPROFILE`; if we point
# USERPROFILE at a different drive, the default must follow.
. "$bootstrapLib/common.ps1"
. "$bootstrapLib/config.ps1"

$fakeHome = "C:/fake-home-$(Get-Random)"
$originalHome = $env:USERPROFILE
$env:USERPROFILE = $fakeHome
try {
    Initialize-Logging -LogPath (Join-Path $env:TEMP "port-test-$(Get-Random).log")
    $substs = Get-ConfigSubstitutions
    $expectedPlugin = "$fakeHome/Desktop/tools/opencode-ua-plugin/dist/index.js"
    # PluginPath is normalized backslash -> forward slash
    Assert-Equal $substs["PLUGIN_PATH"] $expectedPlugin "PLUGIN_PATH default must follow `$env:USERPROFILE (proves no hardcoded user path)"
    Assert-Equal $substs["USERPROFILE"] $fakeHome "USERPROFILE in substitutions must echo the (mocked) env var, not a hardcoded literal"
} finally {
    $env:USERPROFILE = $originalHome
}

# Test 5: tests/skills.tests.ps1 itself must not hardcode the developer's
# machine path (this is what the fix is about -- guard against regression).
$skillsTest = Join-Path $PSScriptRoot "skills.tests.ps1"
$skillsTestContent = Get-Content -LiteralPath $skillsTest -Raw
foreach ($bad in $forbidden) {
    if ($skillsTestContent.Contains($bad)) {
        throw "PORTABILITY VIOLATION: tests/skills.tests.ps1 contains literal '$bad'. " +
              "Tests must derive paths from `$PSScriptRoot so the suite runs on any machine."
    }
}

Write-Host "portability.tests.ps1: OK"
