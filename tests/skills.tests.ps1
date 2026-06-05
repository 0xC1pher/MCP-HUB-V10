. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/skills.ps1"

$src = Join-Path $PSScriptRoot "fixtures/skills"
$dst = Join-Path $env:TEMP "ua-test-skills-$(Get-Random)"
New-Item -ItemType Directory -Path $dst -Force | Out-Null

# Test: Install-Skills copies files
Install-Skills -SourceDir $src -DestinationDir $dst
Assert-FileExists (Join-Path $dst "skill1.md") "skill1.md should be copied"
Assert-FileExists (Join-Path $dst "skill2.md") "skill2.md should be copied"

# Test: idempotency -- second call doesn't fail
Install-Skills -SourceDir $src -DestinationDir $dst
Assert-FileExists (Join-Path $dst "skill1.md") "skill1.md should still exist"

# Test: Get-SkillsDestination returns a path
$dest = Get-SkillsDestination -UserHome $env:USERPROFILE
Assert-True ($null -ne $dest) "Should return a destination path"

# Cleanup
Remove-Item $dst -Recurse -Force

Write-Host "skills.tests.ps1: OK"
