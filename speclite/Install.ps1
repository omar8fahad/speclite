<#
.SYNOPSIS
    Install speclite into a project, non-destructively.

.DESCRIPTION
    Typical use: copy this whole `speclite/` folder into your project root, then run:
        pwsh speclite/Install.ps1

    By default the target project is the PARENT of the folder this script lives in.
    Pass -TargetDir to install somewhere else.

    Guarantees:
      - Only ever writes inside <target>/.speclite/ - nothing else in the project is touched.
      - Never overwrites or deletes an existing file. If a file already exists at the
        destination, it is left completely alone and reported as "skipped" at the end.
      - Safe to re-run any time - only adds missing files, never clobbers existing ones.
#>
[CmdletBinding()]
param(
    [string]$TargetDir,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PackageRoot = $PSScriptRoot
if (-not $TargetDir) {
    $TargetDir = Split-Path $PackageRoot -Parent
} else {
    $TargetDir = (Resolve-Path $TargetDir).Path
}
$SpecliteDir = Join-Path $TargetDir '.speclite'

$CopySets = @(
    @{ Src = 'templates'; Dst = 'templates' },
    @{ Src = 'scripts/python'; Dst = 'scripts/python' },
    @{ Src = 'scripts/powershell'; Dst = 'scripts/powershell' },
    @{ Src = 'commands'; Dst = 'commands' }
)
$EnsureDirs = @('memory', 'logs')

function Copy-TreeNonDestructive {
    param([string]$Src, [string]$Dst, [bool]$DryRun)
    $installed = New-Object System.Collections.Generic.List[string]
    $skipped = New-Object System.Collections.Generic.List[string]
    if (-not (Test-Path $Src)) { return @{ Installed = $installed; Skipped = $skipped } }

    Get-ChildItem -Path $Src -Recurse -File | Where-Object {
        $_.FullName -notmatch '__pycache__' -and $_.Extension -notin @('.pyc', '.pyo') -and $_.Name -ne '.DS_Store'
    } | Sort-Object FullName | ForEach-Object {
        $rel = $_.FullName.Substring((Resolve-Path $Src).Path.Length).TrimStart('\', '/')
        $destFile = Join-Path $Dst $rel
        if (Test-Path $destFile) {
            $skipped.Add($destFile)
        } else {
            $installed.Add($destFile)
            if (-not $DryRun) {
                New-Item -ItemType Directory -Force -Path (Split-Path $destFile -Parent) | Out-Null
                Copy-Item -LiteralPath $_.FullName -Destination $destFile
            }
        }
    }
    return @{ Installed = $installed; Skipped = $skipped }
}

Write-Output "Installing speclite into: $SpecliteDir"
if ($DryRun) { Write-Output '(dry run - nothing will be written)' }

$allInstalled = @()
$allSkipped = @()

foreach ($set in $CopySets) {
    $src = Join-Path $PackageRoot $set.Src
    $dst = Join-Path $SpecliteDir $set.Dst
    $result = Copy-TreeNonDestructive -Src $src -Dst $dst -DryRun $DryRun
    $allInstalled += $result.Installed
    $allSkipped += $result.Skipped
}

foreach ($rel in $EnsureDirs) {
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force -Path (Join-Path $SpecliteDir $rel) | Out-Null
    }
}

Write-Output ""
Write-Output "Installed $($allInstalled.Count) file(s)."
if ($allSkipped.Count -gt 0) {
    Write-Output "Skipped $($allSkipped.Count) file(s) that already existed (left untouched, nothing was overwritten):"
    foreach ($path in $allSkipped) {
        $relDisplay = $path.Substring($TargetDir.Length).TrimStart('\', '/')
        Write-Output "  - $relDisplay"
    }
    Write-Output ""
    Write-Output "If any of these are stale versions from an older speclite install, compare them by hand and update manually - this installer will never overwrite an existing file automatically."
} else {
    Write-Output 'No conflicts.'
}

if (-not $DryRun) {
    Write-Output ""
    Write-Output 'Done. Next step: run /speclite.constitution (Phase 1) to get started.'
}
