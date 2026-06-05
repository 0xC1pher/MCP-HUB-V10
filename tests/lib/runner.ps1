# Runs a single test file and reports pass/fail.
function Run-TestFile {
    param([string]$Path)
    $name = Split-Path $Path -Leaf
    try {
        $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Path 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Test file exited with code $LASTEXITCODE" }
        $output | ForEach-Object { Write-Host $_ }
        Write-Host "PASS: $name" -ForegroundColor Green
        return @{ Name = $name; Passed = $true }
    } catch {
        Write-Host "FAIL: $name - $_" -ForegroundColor Red
        return @{ Name = $name; Passed = $false; Error = "$_" }
    }
}

function Run-AllTests {
    param([string]$TestsDir)
    $files = Get-ChildItem -LiteralPath $TestsDir -Filter "*.tests.ps1" -Recurse
    $results = @()
    foreach ($f in $files) {
        $results += Run-TestFile -Path $f.FullName
    }
    $passed = @($results | Where-Object { $_.Passed }).Count
    $failed = @($results | Where-Object { -not $_.Passed }).Count
    Write-Host ""
    Write-Host "Tests: $passed passed, $failed failed, $($results.Count) total"
    if ($failed -gt 0) { exit 1 }
}
