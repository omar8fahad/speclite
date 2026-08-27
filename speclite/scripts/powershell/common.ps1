# Shared helpers for speclite's PowerShell scripts.
# Mirrors scripts/python/common.py function-for-function.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Canonical phase keys -> their log/reference folder names, in execution order.
$Script:PhaseDirs = [ordered]@{
    constitution = '1-constitution'
    specify      = '2-specify'
    plan         = '3-plan'
    tasks        = '4-tasks'
    implement    = '5-implement'
}
$Script:PhaseOrder = @($Script:PhaseDirs.Keys)

# Default reference subfolders created for every new feature.
$Script:ReferenceSubdirs = @('PRD', 'images', 'fonts', 'sounds', 'videos', 'data', 'docs')

function Find-SpecliteRoot {
    param([string]$StartDir = (Get-Location).Path)
    $current = (Resolve-Path -LiteralPath $StartDir).Path
    while ($true) {
        if (Test-Path (Join-Path $current '.speclite') -PathType Container) {
            return $current
        }
        $parent = Split-Path $current -Parent
        if ([string]::IsNullOrEmpty($parent) -or $parent -eq $current) {
            return $null
        }
        $current = $parent
    }
}

function Get-RepoRoot {
    param([string]$ScriptFile)
    $root = Find-SpecliteRoot
    if ($root) { return $root }
    if ($ScriptFile) {
        $scriptDir = Split-Path (Resolve-Path -LiteralPath $ScriptFile).Path -Parent
        $root = Find-SpecliteRoot -StartDir $scriptDir
        if ($root) { return $root }
        # Installed scripts live at .speclite/scripts/powershell/<script>.ps1
        try {
            return (Resolve-Path (Join-Path $scriptDir '../../..')).Path
        } catch { }
    }
    return (Get-Location).Path
}

# --------------------------------------------------------------------------
# The project constitution - always ONE file for the whole project, matching
# Spec Kit's own model. No scope decision, no per-feature variant.
# --------------------------------------------------------------------------

function Get-ProjectPrinciplesPath {
    param([string]$RepoRoot)
    return Join-Path $RepoRoot '.speclite/memory/principles.md'
}

# --------------------------------------------------------------------------
# .speclite/feature.json
# --------------------------------------------------------------------------

function Read-FeatureJson {
    param([string]$RepoRoot)
    $path = Join-Path $RepoRoot '.speclite/feature.json'
    if (-not (Test-Path $path)) { return '' }
    try {
        $data = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
        if ($null -eq $data.feature_directory) { return '' }
        return [string]$data.feature_directory
    } catch { return '' }
}

function Save-FeatureJson {
    param([string]$RepoRoot, [string]$FeatureDirValue)
    $value = $FeatureDirValue
    if ([System.IO.Path]::IsPathRooted($value)) {
        $value = [System.IO.Path]::GetRelativePath($RepoRoot, $value) -replace '\\', '/'
    }
    if ((Read-FeatureJson -RepoRoot $RepoRoot) -eq $value) { return }
    $dir = Join-Path $RepoRoot '.speclite'
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $json = (@{ feature_directory = $value } | ConvertTo-Json -Compress)
    [System.IO.File]::WriteAllText((Join-Path $dir 'feature.json'), $json, [System.Text.UTF8Encoding]::new($false))
}

function Get-AllFeatures {
    param([string]$RepoRoot)
    $specsDir = Join-Path $RepoRoot 'specs'
    if (-not (Test-Path $specsDir)) { return @() }
    return @(Get-ChildItem $specsDir -Directory | Sort-Object Name | Select-Object -ExpandProperty Name)
}

function Get-FeaturePaths {
    param([switch]$NoPersist, [string]$ScriptFile)
    $repoRoot = Get-RepoRoot -ScriptFile $ScriptFile
    $envDir = $env:SPECLITE_FEATURE_DIRECTORY
    if ($envDir) {
        $featureDir = $envDir
        if (-not [System.IO.Path]::IsPathRooted($featureDir)) { $featureDir = Join-Path $repoRoot $featureDir }
        if (-not $NoPersist) { Save-FeatureJson -RepoRoot $repoRoot -FeatureDirValue $envDir }
    } else {
        $stored = Read-FeatureJson -RepoRoot $repoRoot
        if (-not $stored) {
            Write-Error 'No active feature. Run New-Feature.ps1 first, or set $env:SPECLITE_FEATURE_DIRECTORY.'
            exit 1
        }
        $featureDir = $stored
        if (-not [System.IO.Path]::IsPathRooted($featureDir)) { $featureDir = Join-Path $repoRoot $featureDir }
    }

    [PSCustomObject]@{
        RepoRoot      = $repoRoot
        FeatureDir    = $featureDir
        Spec          = Join-Path $featureDir 'spec.md'
        Plan          = Join-Path $featureDir 'plan.md'
        Tasks         = Join-Path $featureDir 'tasks.md'
        ReferencesDir = Join-Path $featureDir 'references'
        LogsDir       = Join-Path $featureDir 'logs'
    }
}

function Resolve-SpecliteTemplate {
    param([string]$Name, [string]$RepoRoot)
    $override = Join-Path $RepoRoot ".speclite/templates/overrides/$Name.md"
    if (Test-Path $override) { return $override }
    $core = Join-Path $RepoRoot ".speclite/templates/$Name.md"
    if (Test-Path $core) { return $core }
    return $null
}

function New-SpecliteReferenceDirs {
    param([string]$FeatureDir)
    $referencesDir = Join-Path $FeatureDir 'references'
    foreach ($name in $Script:ReferenceSubdirs) {
        $sub = Join-Path $referencesDir $name
        New-Item -ItemType Directory -Force -Path $sub | Out-Null
        $keep = Join-Path $sub '.gitkeep'
        if (-not (Test-Path $keep)) { New-Item -ItemType File -Path $keep | Out-Null }
    }
    return $referencesDir
}

function New-SpecliteLogDirs {
    param([string]$BaseDir)
    $logsDir = Join-Path $BaseDir 'logs'
    foreach ($phaseKey in $Script:PhaseDirs.Keys) {
        if ($phaseKey -eq 'constitution') { continue }
        New-Item -ItemType Directory -Force -Path (Join-Path $logsDir $Script:PhaseDirs[$phaseKey]) | Out-Null
    }
    return $logsDir
}

# --------------------------------------------------------------------------
# Check log: one row per check, appended to <base>/logs/<phase>/index.md.
# --------------------------------------------------------------------------

function Add-SpecliteLog {
    param(
        [Parameter(Mandatory)][string]$BaseDir,
        [Parameter(Mandatory)][ValidateSet('constitution', 'specify', 'plan', 'tasks', 'implement')]
        [string]$Phase,
        [Parameter(Mandatory)][string]$Status,
        [Parameter(Mandatory)][string]$Summary,
        [string]$Details = ''
    )
    $phaseDir = Join-Path (Join-Path $BaseDir 'logs') $Script:PhaseDirs[$Phase]
    New-Item -ItemType Directory -Force -Path $phaseDir | Out-Null
    $logPath = Join-Path $phaseDir 'index.md'
    $isNew = -not (Test-Path $logPath)
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm'
    $badges = @{ PASS = '✅'; WARN = '⚠️'; FAIL = '❌'; INFO = 'ℹ️' }
    $statusUpper = $Status.ToUpper()
    $badge = $badges[$statusUpper]
    if (-not $badge) { $badge = '•' }

    if ($isNew) {
        $titlePhase = $Phase.Substring(0, 1).ToUpper() + $Phase.Substring(1)
        Add-Content -LiteralPath $logPath -Value "# $titlePhase - Check Log`n"
        Add-Content -LiteralPath $logPath -Value 'Other files in this folder (test output, screenshots, extra docs) are organized by the agent as needed - this table only tracks pass/fail checks.'
        Add-Content -LiteralPath $logPath -Value ''
        Add-Content -LiteralPath $logPath -Value '| Time | Status | Summary |'
        Add-Content -LiteralPath $logPath -Value '|------|--------|---------|'
    }
    $rowSummary = ($Summary -replace '\|', '/') -replace "`n", ' '
    Add-Content -LiteralPath $logPath -Value "| $ts | $badge $statusUpper | $rowSummary |"

    if ($Details) {
        Add-Content -LiteralPath $logPath -Value "`n<details><summary>$ts details</summary>`n"
        Add-Content -LiteralPath $logPath -Value $Details
        Add-Content -LiteralPath $logPath -Value "`n</details>`n"
    }
    return $logPath
}

function Get-SpecliteLogText {
    param([string]$BaseDir, [string]$Phase)
    $logPath = Join-Path (Join-Path (Join-Path $BaseDir 'logs') $Script:PhaseDirs[$Phase]) 'index.md'
    if (-not (Test-Path $logPath)) { return '' }
    return (Get-Content -Raw -LiteralPath $logPath)
}

# --------------------------------------------------------------------------
# Small text-scanning helpers used by Get-SpecliteStatus.ps1
# --------------------------------------------------------------------------

function Get-SpecliteSection {
    param([string]$MarkdownText, [string]$Heading)
    $pattern = '(?ms)^##\s+' + [regex]::Escape($Heading) + '\s*$(.*?)(?=^##\s|\z)'
    $match = [regex]::Match($MarkdownText, $pattern)
    if ($match.Success) { return $match.Groups[1].Value }
    return ''
}

function Get-UncheckedBoxCount {
    param([string]$Text)
    return ([regex]::Matches($Text, '(?m)^\s*-\s\[\s\]')).Count
}

function Get-CheckedBoxCount {
    param([string]$Text)
    return ([regex]::Matches($Text, '(?m)^\s*-\s\[[xX]\]')).Count
}
