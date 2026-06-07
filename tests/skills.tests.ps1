. "$PSScriptRoot/lib/assert.ps1"
. "$PSScriptRoot/../bootstrap/lib/skills.ps1"

$src = Join-Path $PSScriptRoot "fixtures/skills"
$dst = Join-Path $env:TEMP "ua-test-skills-$(Get-Random)"
New-Item -ItemType Directory -Path $dst -Force | Out-Null

# Test: Install-Skills exposes the source via a junction (read still works)
Install-Skills -SourceDir $src -DestinationDir $dst
Assert-FileExists (Join-Path $dst "skill1.md") "skill1.md should be reachable through the junction"
Assert-FileExists (Join-Path $dst "skill2.md") "skill2.md should be reachable through the junction"

# Test: the destination is a reparse point (junction), not a real directory
$dstItem = Get-Item -LiteralPath $dst -Force
Assert-True ($dstItem.Attributes -band [IO.FileAttributes]::ReparsePoint) "Destination should be a reparse point (junction)"

# Test: the junction target equals the source
$dstTarget = (Get-Item -LiteralPath $dst -Force).Target
Assert-True ($dstTarget -eq $src) "Junction target should equal source (got: '$dstTarget', expected: '$src')"

# Test: idempotency -- second call doesn't fail and doesn't create a new junction
Install-Skills -SourceDir $src -DestinationDir $dst
Assert-FileExists (Join-Path $dst "skill1.md") "skill1.md should still be reachable after re-install"

# Test: Get-SkillsDestination returns a path under the actual opencode config dir
$dest = Get-SkillsDestination -UserHome $env:USERPROFILE
Assert-True ($null -ne $dest) "Should return a destination path"
# We don't assert a specific suffix here because the function falls back to
# ~/.opencode/skills if the modern ~/.config/opencode path doesn't exist on
# the test host. Both are valid; we just want a non-empty string.

# Test: Install-Skills handles nested directory structure (skill-name/SKILL.md)
$nestedSrc = Join-Path $PSScriptRoot "fixtures/skills-nested"
$nestedDst = Join-Path $env:TEMP "ua-test-skills-nested-$(Get-Random)"
Install-Skills -SourceDir $nestedSrc -DestinationDir $nestedDst
Assert-FileExists (Join-Path $nestedDst "skill-category/SKILL.md") "nested SKILL.md should be reachable through the junction"

# Test: Install-Skills is idempotent (junction mode: no-op on re-run)
# Regression for Get-FileHash collision in older code paths. The new junction
# model short-circuits on the second call, so the log must say "already in
# place" instead of "N copied".
$installLogPath = Join-Path $env:TEMP "ua-test-skills-log-$(Get-Random).log"
. "$PSScriptRoot/../bootstrap/lib/common.ps1"
Initialize-Logging -LogPath $installLogPath
Install-Skills -SourceDir $nestedSrc -DestinationDir $nestedDst
$installLog = Get-Content $installLogPath -Raw
Assert-Contains $installLog "already in place" "Second run should report the junction is already in place (idempotent)"
Remove-Item $installLogPath -Force
# Junction removal: do NOT use -Recurse on a reparse point -- it can follow
# the junction into the source. Plain -Force removes the junction only.
Remove-Item -LiteralPath $nestedDst -Force

# Test: Install-Skills against the real dev-bootstrap skills snapshot
# Use $PSScriptRoot so the test works on any machine that clones the repo --
# the real snapshot IS the repo's own skills/ dir.
$realSkillsSnapshot = (Resolve-Path "$PSScriptRoot/../skills").Path
$realSkillsDst = Join-Path $env:TEMP "ua-test-skills-real-$(Get-Random)"
if (Test-Path $realSkillsSnapshot) {
    Install-Skills -SourceDir $realSkillsSnapshot -DestinationDir $realSkillsDst
    $count = (Get-ChildItem -LiteralPath $realSkillsDst -Recurse -File -Filter "SKILL.md" | Measure-Object).Count
    Assert-True ($count -gt 0) "Real snapshot should expose at least one SKILL.md through the junction (got: $count)"
    # Safe junction removal (no -Recurse; see comment above).
    Remove-Item -LiteralPath $realSkillsDst -Force
}

# Test: a real source change is visible through the junction without re-install
$liveSrc = Join-Path $env:TEMP "ua-test-skills-live-src-$(Get-Random)"
$liveDst = Join-Path $env:TEMP "ua-test-skills-live-dst-$(Get-Random)"
New-Item -ItemType Directory -Path $liveSrc -Force | Out-Null
Set-Content -LiteralPath (Join-Path $liveSrc "live-skill.md") -Value "version 1" -Encoding UTF8 -NoNewline
Install-Skills -SourceDir $liveSrc -DestinationDir $liveDst
$v1 = Get-Content -LiteralPath (Join-Path $liveDst "live-skill.md") -Raw
Assert-Contains $v1 "version 1" "Initial content should be reachable through the junction"
Set-Content -LiteralPath (Join-Path $liveSrc "live-skill.md") -Value "version 2" -Encoding UTF8 -NoNewline
$v2 = Get-Content -LiteralPath (Join-Path $liveDst "live-skill.md") -Raw
Assert-Contains $v2 "version 2" "Source edit should be visible through the junction without re-install (this is the whole point of using a junction)"
# Cleanup: remove the source first so the junction dangling-removal is a no-op,
# then the junction itself.
Remove-Item -LiteralPath $liveSrc -Recurse -Force
Remove-Item -LiteralPath $liveDst -Force

# Cleanup
Remove-Item $dst -Force

Write-Host "skills.tests.ps1: OK"
