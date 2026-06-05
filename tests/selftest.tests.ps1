. "$PSScriptRoot/lib/assert.ps1"

# This should pass
Assert-Equal (1 + 1) 2 "1+1 should be 2"
Assert-True ($true) "true is true"

Write-Host "selftest.tests.ps1: OK"
