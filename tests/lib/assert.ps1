# Simple assertion library. Throws on failure.
function Assert-Equal {
    param($Actual, $Expected, [string]$Message = "")
    if ($Actual -ne $Expected) {
        throw "ASSERT EQUAL FAILED: $Message | Expected: '$Expected' | Actual: '$Actual'"
    }
}

function Assert-True {
    param([bool]$Condition, [string]$Message = "")
    if (-not $Condition) {
        throw "ASSERT TRUE FAILED: $Message"
    }
}

function Assert-False {
    param([bool]$Condition, [string]$Message = "")
    if ($Condition) {
        throw "ASSERT FALSE FAILED: $Message"
    }
}

function Assert-Contains {
    param([string]$Haystack, [string]$Needle, [string]$Message = "")
    if (-not $Haystack.Contains($Needle)) {
        throw "ASSERT CONTAINS FAILED: $Message | '$Haystack' does not contain '$Needle'"
    }
}

function Assert-FileExists {
    param([string]$Path, [string]$Message = "")
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "ASSERT FILE EXISTS FAILED: $Message | File not found: $Path"
    }
}
