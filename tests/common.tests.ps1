. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/common.ps1"

# Test: banner contains the version
$banner = Write-Banner -Version "0.1.0"
Assert-Contains $banner "0.1.0" "Banner should contain version"

# Test: prereq passes for git (assumed installed)
Assert-True (Test-Prereq -Command "git" -Argument "--version") "git should be installed"

# Test: prereq fails loud for a missing tool
$threw = $false
try {
    Test-Prereq -Command "this-tool-does-not-exist-12345" -Argument "--version" -ShouldThrow
} catch {
    $threw = $true
}
Assert-True $threw "Test-Prereq should throw for missing tool"

# Test: Write-Log creates a log file
$testLog = Join-Path $env:TEMP "ua-test-$(Get-Random).log"
$Script:LogPath = $testLog
Write-Log -Level "INFO" -Message "test message"
Assert-FileExists $testLog "Log file should be created"
Assert-Contains (Get-Content $testLog -Raw) "test message" "Log should contain message"
Remove-Item $testLog -Force

Write-Host "common.tests.ps1: OK"
