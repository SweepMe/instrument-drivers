Param(
    [Parameter(Mandatory)]
    [string]$TargetBranch,

    [Parameter(Mandatory=$false)]
    [string]$DevRequirementsFile = ".\requirements_dev.txt"
)

# Runs tools/check_driver.py and ruff on the drivers a pull request changes and reports their findings as annotations
# in the pull request. It does not fail: most drivers are not modernized yet, and a small fix to one of them must not
# require its whole modernization. Each driver's findings are a work list (DRIVER_GUIDE.md, section 13).

git fetch origin $TargetBranch
$ChangedDrivers = & "$PSScriptRoot\Get-ModifiedDrivers.ps1" -TargetBranch $TargetBranch

if (-not $ChangedDrivers) {
    Write-Host "No modified drivers were detected."
    exit 0
}

$RuffRequirement = Get-Content $DevRequirementsFile | ? { $_ -match "^ruff\b" }
Write-Host "Installing $RuffRequirement from $DevRequirementsFile"
python -m pip install --upgrade $RuffRequirement

foreach ($Driver in $ChangedDrivers) {
    Write-Host "[$Driver] check_driver.py"
    python ./tools/check_driver.py "src/$Driver"
    python ./tools/check_driver.py "src/$Driver" --github
    Write-Host "[$Driver] ruff"
    # ruff writes ::error annotations; as warnings they do not read as a failed check
    python -m ruff check "src/$Driver" --output-format github --exit-zero | % { $_ -replace "^::error ", "::warning " }
}
exit 0
