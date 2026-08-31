# Shared helpers for speclite's PowerShell scripts.
# Mirrors scripts/python/common.py function-for-function.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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
    <#
    Create the single, flat logs/ folder for a feature (idempotent). Free-form only -
    test output, screenshots, session notes - organized by the agent into its own
    subfolders as needed. Never split by phase, never used to decide completion.
    #>
    param([string]$BaseDir)
    $logsDir = Join-Path $BaseDir 'logs'
    New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
    return $logsDir
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

function Test-MarkerChecked {
    <#
    Whether a checkbox line containing $Marker (case-insensitive) is ticked [x] anywhere
    in $Text. Used to read artifact-based completion signals directly out of tasks.md
    (the Analysis Pass / Final Gap-Check checkboxes) instead of a log.
    #>
    param([string]$Text, [string]$Marker)
    $pattern = '(?mi)^\s*-\s\[[xX]\].*' + [regex]::Escape($Marker)
    return [regex]::IsMatch($Text, $pattern)
}

function Get-UncheckedTaskCount {
    <#
    Count only real T-prefixed task lines (e.g. '- [ ] T001 ...') - deliberately distinct
    from Get-UncheckedBoxCount, which would also match tasks.md's own Analysis Pass /
    Final Gap-Check checkboxes and miscount them as tasks.
    #>
    param([string]$Text)
    $matches = [regex]::Matches($Text, '(?m)^\s*-\s\[([ xX])\]\s+T\d+')
    return @($matches | Where-Object { $_.Groups[1].Value -eq ' ' }).Count
}

# --------------------------------------------------------------------------
# Project Map - lives in specs/ directly (PROJECT_MAP.md, PRD_TRACEABILITY.md,
# ARCHITECTURE_MAP.md, FILE_INDEX.md, optionally PROJECT_MAP.json), alongside
# the specs/NNN-feature/ directories, never inside them. Optional, project-
# wide, not part of the logs/ system - its own sync state lives in an HTML
# comment at the top of PROJECT_MAP.md instead of a separate log file.
# --------------------------------------------------------------------------

$Script:MapFileNames = [ordered]@{
    project_map      = 'PROJECT_MAP.md'
    prd_traceability = 'PRD_TRACEABILITY.md'
    architecture_map = 'ARCHITECTURE_MAP.md'
    file_index       = 'FILE_INDEX.md'
    changelog        = 'MAP_CHANGELOG.md'
    json             = 'PROJECT_MAP.json'
}

$Script:DefaultMapExcludes = @(
    '.git', '.speclite', '.agents', 'skills', 'node_modules', '__pycache__',
    'dist', 'build', '.venv', 'venv', '.next', 'target', 'vendor'
)

function Get-MapFilePaths {
    param([string]$RepoRoot)
    $specsDir = Join-Path $RepoRoot 'specs'
    $result = [ordered]@{}
    foreach ($key in $Script:MapFileNames.Keys) {
        $result[$key] = Join-Path $specsDir $Script:MapFileNames[$key]
    }
    return $result
}

function Get-SourcePrds {
    param([string]$RepoRoot)
    $specsDir = Join-Path $RepoRoot 'specs'
    $found = @()
    if (-not (Test-Path $specsDir)) { return $found }
    Get-ChildItem $specsDir -Directory | Sort-Object Name | ForEach-Object {
        $spec = Join-Path $_.FullName 'spec.md'
        if (Test-Path $spec) { $found += $spec }
        $prdDir = Join-Path $_.FullName 'references/PRD'
        if (Test-Path $prdDir) {
            Get-ChildItem $prdDir -File | Where-Object { $_.Name -ne '.gitkeep' } | Sort-Object Name | ForEach-Object {
                $found += $_.FullName
            }
        }
    }
    return @($found | ForEach-Object { [System.IO.Path]::GetRelativePath($RepoRoot, $_) -replace '\\', '/' })
}

function Read-MapState {
    param([string]$ProjectMapPath)
    $state = @{}
    if (-not (Test-Path $ProjectMapPath)) { return $state }
    $text = Get-Content -Raw -LiteralPath $ProjectMapPath
    $match = [regex]::Match($text, '(?s)<!--\s*speclite-map-state\n(.*?)-->')
    if (-not $match.Success) { return $state }
    foreach ($line in $match.Groups[1].Value -split "`n") {
        $fieldMatch = [regex]::Match($line, '^(\w+):\s*(.*)$')
        if ($fieldMatch.Success) {
            $state[$fieldMatch.Groups[1].Value] = $fieldMatch.Groups[2].Value.Trim()
        }
    }
    return $state
}

function Test-IsGitRepo {
    param([string]$RepoRoot)
    return Test-Path (Join-Path $RepoRoot '.git')
}

function Get-GitCurrentCommit {
    param([string]$RepoRoot)
    Push-Location $RepoRoot
    try {
        $out = & git rev-parse HEAD 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return $out.Trim()
    } catch { return $null }
    finally { Pop-Location }
}

function Test-GitCommitExists {
    param([string]$RepoRoot, [string]$Commit)
    Push-Location $RepoRoot
    try {
        & git cat-file -e $Commit 2>$null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
    finally { Pop-Location }
}

function Get-GitChangedFilesSince {
    <#
    Returns an array of @{Status=...; Path=...} since $SinceCommit, or $null if git isn't
    usable / the commit is invalid - caller should fall back to mtime scanning.
    #>
    param([string]$RepoRoot, [string]$SinceCommit)
    if (-not (Test-IsGitRepo -RepoRoot $RepoRoot)) { return $null }
    if (-not (Test-GitCommitExists -RepoRoot $RepoRoot -Commit $SinceCommit)) { return $null }

    $changes = [ordered]@{}
    Push-Location $RepoRoot
    try {
        $committed = & git diff --name-status "$SinceCommit..HEAD" 2>$null
        if ($LASTEXITCODE -eq 0 -and $committed) {
            foreach ($line in $committed) {
                $parts = $line -split "`t"
                if ($parts.Count -ge 2) {
                    $changes[$parts[-1]] = $parts[0].Substring(0, 1)
                }
            }
        }
        $workingTree = & git status --porcelain 2>$null
        if ($LASTEXITCODE -eq 0 -and $workingTree) {
            foreach ($line in $workingTree) {
                if ($line.Length -lt 4) { continue }
                $code = $line.Substring(0, 2).Trim()
                $path = $line.Substring(3)
                if ($code -match 'D') { $status = 'D' }
                elseif ($code -match 'A' -or $code -match '\?') { $status = 'A' }
                else { $status = 'M' }
                $changes[$path] = $status
            }
        }
    } finally {
        Pop-Location
    }

    $result = @()
    foreach ($path in ($changes.Keys | Sort-Object)) {
        $result += [PSCustomObject]@{ Status = $changes[$path]; Path = $path }
    }
    return @($result | Sort-Object Status)
}

function Get-MtimeChangedFilesSince {
    param([string]$RepoRoot, [string]$SinceTimestamp, [string[]]$KnownFiles)
    $cutoff = $null
    try { $cutoff = [datetime]::Parse($SinceTimestamp) } catch { $cutoff = [datetime]'1970-01-01' }

    $changed = @()
    $seenOnDisk = New-Object System.Collections.Generic.HashSet[string]
    Get-ChildItem $RepoRoot -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
        $relParts = [System.IO.Path]::GetRelativePath($RepoRoot, $_.FullName) -split '[\\/]'
        if ($Script:DefaultMapExcludes -contains $relParts[0]) { return }
        $rel = ([System.IO.Path]::GetRelativePath($RepoRoot, $_.FullName)) -replace '\\', '/'
        [void]$seenOnDisk.Add($rel)
        if ($_.LastWriteTime -gt $cutoff) {
            $changed += [PSCustomObject]@{ Status = 'M'; Path = $rel }
        }
    }
    foreach ($known in $KnownFiles) {
        if (-not $seenOnDisk.Contains($known)) {
            $changed += [PSCustomObject]@{ Status = 'D'; Path = $known }
        }
    }
    return @($changed)
}
