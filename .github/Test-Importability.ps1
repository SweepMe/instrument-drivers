$ErrorActionPreference = "Stop"

[Ref]$Imports = 0
[Ref]$SuccessfulImports = 0

function Import-Driver {
    Param(
        [Parameter(Mandatory)]
        [string]$DriverName
    )
    $Imports.Value++
    python ./tests/importability/import_driver.py $DriverName
    if ($?) {
        $SuccessfulImports.Value++
    }
}

Get-ChildItem -Path src -Attributes Directory | % { Import-Driver -DriverName $_.name }

if ($SuccessfulImports.Value -ne $Imports.Value)
{
    Throw "Only $($SuccessfulImports.Value) out of $($Imports.Value) imports were successful."
}

if ($SuccessfulImports.Value -eq 0)
{
    Throw "Could not import any drivers."
}
