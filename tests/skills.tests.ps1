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

# Test: Install-Skills handles nested directory structure (skill-name/SKILL.md)
$nestedSrc = Join-Path $PSScriptRoot "fixtures/skills-nested"
$nestedDst = Join-Path $env:TEMP "ua-test-skills-nested-$(Get-Random)"
Install-Skills -SourceDir $nestedSrc -DestinationDir $nestedDst
Assert-FileExists (Join-Path $nestedDst "skill-category/SKILL.md") "nested SKILL.md should be copied with dir structure preserved"
Remove-Item $nestedDst -Recurse -Force

# Test: Install-Skills against the real dev-bootstrap skills snapshot
$realSkillsSnapshot = "C:\Users\Admin\Desktop\tools\dev-bootstrap\skills"
$realSkillsDst = Join-Path $env:TEMP "ua-test-skills-real-$(Get-Random)"
if (Test-Path $realSkillsSnapshot) {
    Install-Skills -SourceDir $realSkillsSnapshot -DestinationDir $realSkillsDst
    $count = (Get-ChildItem -LiteralPath $realSkillsDst -Recurse -File -Filter "SKILL.md" | Measure-Object).Count
    Assert-True ($count -gt 0) "Real snapshot should install at least one SKILL.md (got: $count)"
    Remove-Item $realSkillsDst -Recurse -Force
}

# Cleanup
Remove-Item $dst -Recurse -Force

Write-Host "skills.tests.ps1: OK"
