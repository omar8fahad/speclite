<#
.SYNOPSIS
    Start a new speclite feature (Phase 2: specify).

.DESCRIPTION
    Creates specs/NNN-short-name/ with spec.md, the standard references/ subfolders, and
    the per-feature logs/ phase folders (2-specify through 5-implement - constitution is
    always project-wide, so it has no per-feature folder here).
#>
[CmdletBinding()]
param(
    [switch]$Json,
    [string]$ShortName,
    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Description
)

. (Join-Path $PSScriptRoot 'common.ps1')

$stopWords = @(
    'a', 'an', 'the', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
    'is', 'are', 'was', 'were', 'i', 'want', 'need', 'add', 'build', 'create', 'make', 'new'
)

function Get-ShortName {
    param([string]$Text)
    $words = ($Text.ToLower() -replace '[^a-z0-9]', ' ') -split '\s+' | Where-Object { $_ }
    $meaningful = $words | Where-Object { $_.Length -ge 3 -and ($stopWords -notcontains $_) }
    if ($meaningful.Count -gt 0) { return ($meaningful | Select-Object -First 4) -join '-' }
    return ($words | Select-Object -First 3) -join '-'
}

function Get-NextNumber {
    param([string]$SpecsDir)
    $highest = 0
    if (Test-Path $SpecsDir) {
        Get-ChildItem $SpecsDir -Directory | ForEach-Object {
            if ($_.Name -match '^(\d{3,})-') {
                $n = [int]$Matches[1]
                if ($n -gt $highest) { $highest = $n }
            }
        }
    }
    return $highest + 1
}

$descText = ($Description -join ' ').Trim()
if (-not $descText) {
    Write-Error 'Error: feature description is required'
    exit 1
}

$repoRoot = Get-RepoRoot -ScriptFile $PSCommandPath
$specsDir = Join-Path $repoRoot 'specs'
New-Item -ItemType Directory -Force -Path $specsDir | Out-Null

$suffix = if ($ShortName) { $ShortName } else { Get-ShortName $descText }
$number = Get-NextNumber $specsDir
$dirName = '{0:D3}-{1}' -f $number, $suffix
$featureDir = Join-Path $specsDir $dirName

if (Test-Path $featureDir) {
    Write-Error "Error: $featureDir already exists"
    exit 1
}

New-Item -ItemType Directory -Force -Path $featureDir | Out-Null
$referencesDir = New-SpecliteReferenceDirs -FeatureDir $featureDir
New-SpecliteLogDirs -BaseDir $featureDir | Out-Null

$specFile = Join-Path $featureDir 'spec.md'
$template = Resolve-SpecliteTemplate -Name 'spec-template' -RepoRoot $repoRoot
if ($template) {
    Copy-Item $template $specFile
} else {
    Set-Content -LiteralPath $specFile -Value "# Feature Specification: $descText`n`n[NEEDS CLARIFICATION: spec-template.md not found - see .speclite/templates/]"
}

Save-FeatureJson -RepoRoot $repoRoot -FeatureDirValue "specs/$dirName"
Add-SpecliteLog -BaseDir $featureDir -Phase 'specify' -Status 'INFO' -Summary "Feature created: $descText" | Out-Null

$projectPrinciples = Get-ProjectPrinciplesPath -RepoRoot $repoRoot
$hasProjectPrinciples = Test-Path $projectPrinciples

$payload = [ordered]@{
    FEATURE_DIR              = $featureDir
    SPEC_FILE                = $specFile
    REFERENCES_DIR           = $referencesDir
    FEATURE_NUM              = '{0:D3}' -f $number
    PROJECT_PRINCIPLES_FILE  = if ($hasProjectPrinciples) { $projectPrinciples } else { $null }
}

if ($Json) {
    $payload | ConvertTo-Json -Compress
} else {
    $payload.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key): $($_.Value)" }
    Write-Output ""
    Write-Output "Drop any PRDs, guidelines, fonts, sounds, videos, data, or docs into: $referencesDir"
    if (-not $hasProjectPrinciples) {
        Write-Output "Note: no project constitution yet - consider running /speclite.constitution first (it's optional, but recommended as Phase 1)."
    }
}
