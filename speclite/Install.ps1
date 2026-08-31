<#
.SYNOPSIS
    Install speclite into a project, non-destructively.

.DESCRIPTION
    Typical use: copy this whole `speclite/` folder into your project root, then run:
        pwsh speclite/Install.ps1

    By default the target project is the PARENT of the folder this script lives in.
    Pass -TargetDir to install somewhere else.

    What gets installed where:
      .speclite/scripts/, .speclite/templates/  - internal machinery (state, scripts,
                                                    templates)
      .agents/commands/                          - the 5 phase command files plus the optional Project Map command, flat, for
                                                    any agent that reads custom
                                                    slash-commands from a project-level
                                                    .agents/ directory
      skills/speclite/, skills/speclite-<phase>/ - the same 5 phases (plus the manager)
                                                    as self-contained Skill-format
                                                    folders, matching Spec Kit's own
                                                    skills/speckit-<name>/SKILL.md layout

    Guarantees:
      - Only ever writes inside <target>/.speclite/, <target>/.agents/commands/, and
        <target>/skills/ - nothing else in the project is touched.
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

$CopySets = @(
    @{ Src = 'templates'; Dst = '.speclite/templates' },
    @{ Src = 'scripts/python'; Dst = '.speclite/scripts/python' },
    @{ Src = 'scripts/powershell'; Dst = '.speclite/scripts/powershell' },
    @{ Src = 'commands'; Dst = '.agents/commands' },
    @{ Src = 'skills'; Dst = 'skills' }
)
$EnsureDirs = @('.speclite/memory', '.speclite/logs')

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

Write-Output "Installing speclite into: $TargetDir"
Write-Output '  -> .speclite/    (scripts, templates, project state)'
Write-Output '  -> .agents/commands/  (the 5 phase command files + map)'
Write-Output '  -> skills/       (Skill-format wrappers, one per phase + the manager)'
if ($DryRun) { Write-Output '(dry run - nothing will be written)' }

$allInstalled = @()
$allSkipped = @()

foreach ($set in $CopySets) {
    $src = Join-Path $PackageRoot $set.Src
    $dst = Join-Path $TargetDir $set.Dst
    $result = Copy-TreeNonDestructive -Src $src -Dst $dst -DryRun $DryRun
    $allInstalled += $result.Installed
    $allSkipped += $result.Skipped
}

foreach ($rel in $EnsureDirs) {
    if (-not $DryRun) {
        New-Item -ItemType Directory -Force -Path (Join-Path $TargetDir $rel) | Out-Null
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
