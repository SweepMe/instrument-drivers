Param(
    [Parameter(Mandatory)]
    [string]$TargetBranch
)

git fetch origin $TargetBranch
# To identify the changed drivers
# 1. Get all files that changed, could look like "src/Logger-PC_CPU-Memory/main.py"
# 2. Filter on entries that start with "src/"
# 3. Remove the leading "src/"
# 4. Remaining string must contain another "/" (i.e. be a directory)
# 5. Use everything before the "/" (i.e. the driver name)
# 6. Remove duplicates
# 7. Remove drivers where the folder does no longer exist (i.e. all files were deleted) - must be checked at the very last, single files that were deleted should not count
$ChangedFiles = git diff --name-only "origin/$TargetBranch"
$ChangedDrivers = $ChangedFiles | ? { $_.StartsWith("src/") } | % { $_.Substring(4) } | ? { $_.Contains("/") } | % { $_.Split("/")[0] } | Get-Unique
$ChangedDrivers = $ChangedDrivers | ? { Test-Path -Path "src/$_" }

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
    Write-Host "Installing python requirements"
    python -m pip install --upgrade pip
    pip install --upgrade -r .\requirements.txt
    $ChangedDrivers | % { Import-Driver -DriverName $_ }
}
else {
    Write-Host "No modified drivers were detected."
}

