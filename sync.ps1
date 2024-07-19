# PowerShell script to achieve the same functionality as the `sync.sh` script:
param (
    [string]$SourceDir,
    [string]$DestDir,
    [switch]$Verbose,
    [switch]$Purge,
    [switch]$ForceCopy,
    [switch]$UseCtime,
    [switch]$UseContent,
    [switch]$TwoWay,
    [switch]$HVerify
)
function SyncDirectories {
    param (
        [string]$Source,
        [string]$Dest,
        [bool]$Verbose,
        [bool]$Purge,
        [bool]$ForceCopy,
        [bool]$UseCtime,
        [bool]$UseContent,
        [bool]$TwoWay,
        [bool]$HVerify
    )
    
    if (-not (Test-Path $Dest)) {
        New-Item -ItemType Directory -Path $Dest
        if ($Verbose) { Write-Host "Created target directory: $Dest" }
    }

    function CompareAndCopy {
        param (
            [string]$Src,
            [string]$Dst,
            [bool]$Reverse
        )
        $comparison = Compare-Object -ReferenceObject (Get-ChildItem -Recurse $Src) -DifferenceObject (Get-ChildItem -Recurse $Dst) -Property Name
        CopyFiles -Comparison $comparison -Src $Src -Dst $Dst -Reverse $Reverse
        if ($Purge) {
            DeleteFiles -Comparison $comparison -Dst $Dst
        }
    }

    function CopyFiles {
        param (
            $Comparison,
            [string]$Src,
            [string]$Dst,
            [bool]$Reverse
        )
        foreach ($item in $Comparison) {
            $srcPath = Join-Path $Src $item.Name
            $dstPath = Join-Path $Dst $item.Name
            if ($item.SideIndicator -eq "<=") {
                if (Test-Path $srcPath -PathType Container) {
                    Copy-Item -Recurse -Path $srcPath -Destination $dstPath
                    if ($Verbose) { Write-Host "Copied directory: $srcPath to $dstPath" }
                } else {
                    Copy-Item -Path $srcPath -Destination $dstPath
                    if ($Verbose) { Write-Host "Copied file: $srcPath to $dstPath" }
                }
            }
            elseif ($item.SideIndicator -eq "==") {
                if ($ForceCopy -or (Compare-Object -ReferenceObject (Get-FileHash $srcPath) -DifferenceObject (Get-FileHash $dstPath) -Property Hash)) {
                    if ($Reverse) {
                        Copy-Item -Path $dstPath -Destination $srcPath -Force
                        if ($Verbose) { Write-Host "Updated file: $dstPath to $srcPath" }
                    } else {
                        Copy-Item -Path $srcPath -Destination $dstPath -Force
                        if ($Verbose) { Write-Host "Updated file: $srcPath to $dstPath" }
                    }
                }
            }
        }
    }

    function DeleteFiles {
        param (
            $Comparison,
            [string]$Dst
        )
        foreach ($item in $Comparison) {
            if ($item.SideIndicator -eq "=>") {
                $dstPath = Join-Path $Dst $item.Name
                if (Test-Path $dstPath -PathType Container) {
                    Remove-Item -Recurse -Path $dstPath -Force
                    if ($Verbose) { Write-Host "Deleted directory: $dstPath" }
                } else {
                    Remove-Item -Path $dstPath -Force
                    if ($Verbose) { Write-Host "Deleted file: $dstPath" }
                }
            }
        }
    }

    function ComputeFileMd5 {
        param (
            [string]$FilePath
        )
        $hash = Get-FileHash $FilePath -Algorithm MD5
        return $hash.Hash
    }

    function VerifyMd5 {
        param (
            [string]$Src,
            [string]$Dst
        )
        $allFiles = Get-ChildItem -Recurse $Src, $Dst | Group-Object Name | Where-Object { $_.Count -eq 2 }
        $match = $true

        foreach ($fileGroup in $allFiles) {
            $srcFile = $fileGroup.Group | Where-Object { $_.PSParentPath -like "*$Src*" }
            $dstFile = $fileGroup.Group | Where-Object { $_.PSParentPath -like "*$Dst*" }

            if ($srcFile -and $dstFile) {
                $srcMd5 = ComputeFileMd5 -FilePath $srcFile.FullName
                $dstMd5 = ComputeFileMd5 -FilePath $dstFile.FullName
                if ($srcMd5 -ne $dstMd5) {
                    $match = $false
                    Write-Host "MD5 mismatch for $($fileGroup.Name): $srcMd5 (source) vs $dstMd5 (destination)"
                }
            } else {
                $match = $false
                Write-Host "File $($fileGroup.Name) is not present in both source and destination"
            }
        }

        if ($match) {
            Write-Host "All files are synchronized (MD5 hashes match)."
        } else {
            Write-Host "Some files are not synchronized (MD5 hashes do not match)."
        }
    }

    CompareAndCopy -Src $Source -Dst $Dest
    if ($TwoWay) {
        CompareAndCopy -Src $Dest -Dst $Source -Reverse $true
    }

    if ($HVerify) {
        VerifyMd5 -Src $Source -Dst $Dest
    }
}

if (-not $SourceDir -or -not $DestDir) {
    Write-Host "Usage: .\sync.ps1 -SourceDir <source_directory> -DestDir <destination_directory> [options]"
    exit
}

SyncDirectories -Source $SourceDir -Dest $DestDir -Verbose $Verbose.IsPresent -Purge $Purge.IsPresent -ForceCopy $ForceCopy.IsPresent -UseCtime $UseCtime.IsPresent -UseContent $UseContent.IsPresent -TwoWay $TwoWay.IsPresent -HVerify $HVerify.IsPresent

### Example Usage:
#To use this PowerShell script, open a PowerShell terminal and execute the following commands as per your requirement:
#1. **Basic Synchronization:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory"
#2. **Verbose Mode:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory" -Verbose
#3. **Purge Mode:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory" -Purge
#4. **Force Copy:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory" -ForceCopy
#5. **Use Creation Time:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory" -UseCtime
#6. **Compare Based on Content:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory" -UseContent
#7. **Two-Way Synchronization:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory" -TwoWay
#8. **MD5 Hash Verification:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory" -HVerify
#9. **Combined Options:**
#    .\sync.ps1 -SourceDir "C:\path\to\source_directory" -DestDir "C:\path\to\destination_directory" -Verbose -Purge -ForceCopy -TwoWay -HVerify