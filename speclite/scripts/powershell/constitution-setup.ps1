<#
.SYNOPSIS
    Phase 1 (constitution): ensure the ONE project-wide principles.md exists.

.DESCRIPTION
    Matches Spec Kit's own constitution philosophy: a single file for the whole project,
    never per-feature. Never overwrites an existing principles.md - if one is already
    there, it's reported back untouched so the agent offers to *amend* it through
    conversation instead of recreating it. Amending is always a conscious, explicit act -
    never a side effect of some other phase editing around a conflict.
#>
[CmdletBinding()]
param([switch]$Json)

. (Join-Path $PSScriptRoot 'common.ps1')

$repoRoot = Get-RepoRoot -ScriptFile $PSCommandPath
$principlesFile = Get-ProjectPrinciplesPath -RepoRoot $repoRoot
$alreadyExisted = Test-Path $principlesFile

if (-not $alreadyExisted) {
    New-Item -ItemType Directory -Force -Path (Split-Path $principlesFile -Parent) | Out-Null
    $template = Resolve-SpecliteTemplate -Name 'principles-template' -RepoRoot $repoRoot
    if ($template) {
        Copy-Item $template $principlesFile
    } else {
        Set-Content -LiteralPath $principlesFile -Value "# Project Principles`n`n[Fill in]"
    }
}

$logBase = Join-Path $repoRoot '.speclite'
$summary = if (-not $alreadyExisted) { 'principles.md staged from template' } else { 'principles.md already exists - amending, not recreating' }
Add-SpecliteLog -BaseDir $logBase -Phase 'constitution' -Status 'INFO' -Summary $summary | Out-Null

$payload = [ordered]@{
    PRINCIPLES_FILE = $principlesFile
    ALREADY_EXISTED = $alreadyExisted
}

if ($Json) { $payload | ConvertTo-Json -Compress }
else { $payload.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key): $($_.Value)" } }
