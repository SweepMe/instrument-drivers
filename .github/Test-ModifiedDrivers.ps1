Param(
    [Parameter(Mandatory)]
    [string]$TargetBranch,

    [Parameter(Mandatory=$false)]
    [string]$RequirementsFile = ".\requirements.txt"
)

git fetch origin $TargetBranch
$ChangedDrivers = & "$PSScriptRoot\Get-ModifiedDrivers.ps1" -TargetBranch $TargetBranch

function Import-Driver {
    Param(
        [Parameter(Mandatory)]
        [string]$DriverName
    )
    Write-Host "Running Tests for ${DriverName}:"
    Write-Host "[$DriverName] Test Importability"
    python ./tests/importability/import_driver.py $DriverName
    if (-not $?) {
        throw "Driver $DriverName could not be imported."
    }
}

if ($ChangedDrivers) {
    Write-Host "Following drivers were modified:"
    Write-Host $ChangedDrivers -Separator "`n"
    Write-Host "Installing python requirements from $RequirementsFile"
    python -m pip install --upgrade pip
    pip install --upgrade -r $RequirementsFile
    $ChangedDrivers | % { Import-Driver -DriverName $_ }
}
else {
    Write-Host "No modified drivers were detected."
}

