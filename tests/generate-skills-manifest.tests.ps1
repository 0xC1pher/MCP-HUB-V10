. "$PSScriptRoot/lib/assert.ps1"

# Source the manifest generator as a library (dot-source the file so its
# New-SkillsManifest function is exposed in the current scope).
. "$PSScriptRoot/../tools/generate-skills-manifest.ps1"

# Build a temp skills tree with a single synthetic SKILL.md that has
# well-formed YAML frontmatter. This lets us assert on rendered output
# without depending on the real skills/ snapshot.
$tmpRoot = Join-Path $env:TEMP "ua-mfst-test-$(Get-Random)"
$tmpSkills = Join-Path $tmpRoot "skills"
$tmpOut = Join-Path $tmpRoot "MANIFEST.md"
$tmpVersionFile = Join-Path $tmpRoot "version.txt"
$cat = Join-Path $tmpSkills "category-a"
New-Item -ItemType Directory -Path $cat -Force | Out-Null
Set-Content -LiteralPath (Join-Path $cat "SKILL.md") -Value @"
---
name: test-skill
description: A test skill for manifest rendering.
---
Body content here.
"@ -Encoding UTF8
Set-Content -LiteralPath $tmpVersionFile -Value "9.9.9" -Encoding UTF8

try {
    # The generator must accept explicit -RepoRoot / -SkillsRoot / -OutputPath
    # so it works from any clone location (no hardcoded absolute paths).
    New-SkillsManifest -RepoRoot $tmpRoot -SkillsRoot $tmpSkills -OutputPath $tmpOut

    # Output file must exist at the requested path
    Assert-FileExists $tmpOut "Manifest output should be created at the explicit -OutputPath"

    $rendered = Get-Content -LiteralPath $tmpOut -Raw

    # The rendered manifest must contain the version read from the explicit
    # version.txt (proves version source-of-truth, no hardcoded literal).
    Assert-Contains $rendered "v9.9.9" "Manifest should embed the version from version.txt"

    # The skill's name and description must appear in the output
    Assert-Contains $rendered "test-skill" "Manifest should list the skill name"
    Assert-Contains $rendered "A test skill for manifest rendering." "Manifest should list the first line of the description"

    # The relative path under skills/ must be preserved (parent dir grouping).
    # The separator is OS-native (backslash on Windows, forward slash elsewhere)
    # because we trim the prefix from the full path -- this is correct.
    Assert-Contains $rendered "category-a" "Manifest should group by parent directory"
    $pathOk = ($rendered -match "category-a[\\/]SKILL\.md")
    Assert-True $pathOk "Manifest should preserve the relative skill path (with native separator)"

    # Sanity: the file should be plain Markdown, not garbage
    Assert-Contains $rendered "# dev-bootstrap Skills Manifest" "Manifest should start with the title heading"
} finally {
    if (Test-Path $tmpRoot) { Remove-Item $tmpRoot -Recurse -Force }
}

# Negative test: New-SkillsManifest should fail loud if -SkillsRoot is missing
$missingSkills = Join-Path $env:TEMP "ua-mfst-missing-$(Get-Random)"
$threw = $false
try {
    New-SkillsManifest -RepoRoot $env:TEMP -SkillsRoot $missingSkills -OutputPath (Join-Path $env:TEMP "should-not-be-created.md")
} catch {
    $threw = $true
}
Assert-True $threw "New-SkillsManifest should throw when -SkillsRoot does not exist"

Write-Host "generate-skills-manifest.tests.ps1: OK"
