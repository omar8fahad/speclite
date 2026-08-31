<#
.SYNOPSIS
    Stage the Project Map (optional, cross-cutting capability - not one of the 5 phases).

.DESCRIPTION
    Auto-detects build vs update mode, and for updates, computes a cheap changed-files
    delta (git diff since last sync, or file-mtime fallback if there's no git) so the
    agent only has to read what actually changed instead of re-scanning the whole
    repository every time.

    The map lives directly in specs/ (PROJECT_MAP.md, PRD_TRACEABILITY.md,
    ARCHITECTURE_MAP.md, FILE_INDEX.md, PROJECT_MAP.json), alongside the
    specs/NNN-feature/ directories - never inside any one of them.

    No logs/ integration by design - PROJECT_MAP.md carries its own sync state (an
    invisible <!-- speclite-map-state --> block at the top) instead of a separate log.
#>
[CmdletBinding()]
param(
    [switch]$Json,
    [string]$KnownChanges,
    [string]$FeatureDir
)

. (Join-Path $PSScriptRoot 'common.ps1')

# Above this many changed files, stop listing individually and recommend a broader
# full-sync pass instead - keeps a single update from ballooning into a full re-read.
$ChangedFilesCap = 200

function Get-KnownFilesFromFileIndex {
    param([string]$FileIndexPath)
    if (-not (Test-Path $FileIndexPath)) { return @() }
    $text = Get-Content -Raw -LiteralPath $FileIndexPath
    $matches = [regex]::Matches($text, '`([\w./\-]+\.\w+)`')
    return @($matches | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
}

$repoRoot = Get-RepoRoot -ScriptFile $PSCommandPath
$mapPaths = Get-MapFilePaths -RepoRoot $repoRoot
New-Item -ItemType Directory -Force -Path (Split-Path $mapPaths.project_map -Parent) | Out-Null

$buildMode = -not (Test-Path $mapPaths.project_map)
$state = Read-MapState -ProjectMapPath $mapPaths.project_map
$currentCommit = if (Test-IsGitRepo -RepoRoot $repoRoot) { Get-GitCurrentCommit -RepoRoot $repoRoot } else { $null }

$changedFiles = @()
$changedFilesTruncated = $false
$scanBasis = 'full (build mode - no prior sync)'

if (-not $buildMode) {
    $lastCommit = $state['last_sync_commit']
    $lastTimestamp = $state['last_sync_timestamp']

    $result = $null
    if ($lastCommit -and $lastCommit -ne 'none' -and (Test-IsGitRepo -RepoRoot $repoRoot)) {
        $result = Get-GitChangedFilesSince -RepoRoot $repoRoot -SinceCommit $lastCommit
        if ($null -ne $result) { $scanBasis = "git diff since $($lastCommit.Substring(0, [Math]::Min(12, $lastCommit.Length)))" }
    }

    if ($null -eq $result -and $lastTimestamp) {
        $knownFiles = Get-KnownFilesFromFileIndex -FileIndexPath $mapPaths.file_index
        $result = Get-MtimeChangedFilesSince -RepoRoot $repoRoot -SinceTimestamp $lastTimestamp -KnownFiles $knownFiles
        $scanBasis = "file mtimes since $lastTimestamp (no usable git history)"
    }

    if ($null -eq $result) {
        $scanBasis = 'full (no prior sync state found - treat as full-sync)'
        $changedFiles = @()
    } else {
        $changedFiles = @($result)
    }

    if ($changedFiles.Count -gt $ChangedFilesCap) {
        $changedFilesTruncated = $true
        $changedFiles = @($changedFiles | Select-Object -First $ChangedFilesCap)
    }
}

if ($buildMode) {
    $templateMap = @{
        project_map      = 'project-map-template'
        prd_traceability = 'prd-traceability-template'
        architecture_map = 'architecture-map-template'
        file_index       = 'file-index-template'
    }
    foreach ($key in $templateMap.Keys) {
        $template = Resolve-SpecliteTemplate -Name $templateMap[$key] -RepoRoot $repoRoot
        if ($template) { Copy-Item $template $mapPaths[$key] }
    }
}

$triggeringFeature = $null
if ($FeatureDir) {
    $fd = $FeatureDir
    if (-not [System.IO.Path]::IsPathRooted($fd)) { $fd = Join-Path $repoRoot $fd }
    $triggeringFeature = if (Test-Path $fd) { [System.IO.Path]::GetRelativePath($repoRoot, $fd) -replace '\\', '/' } else { $FeatureDir }
}

$payload = [ordered]@{
    MODE                    = if ($buildMode) { 'build' } else { 'update' }
    MAP_FILES               = $mapPaths
    SOURCE_PRDS             = @(Get-SourcePrds -RepoRoot $repoRoot)
    GIT_AVAILABLE           = (Test-IsGitRepo -RepoRoot $repoRoot)
    LAST_SYNC_COMMIT        = $state['last_sync_commit']
    CURRENT_COMMIT          = $currentCommit
    SCAN_BASIS              = $scanBasis
    CHANGED_FILES           = @($changedFiles | ForEach-Object { [ordered]@{ status = $_.Status; path = $_.Path } })
    CHANGED_FILES_TRUNCATED = $changedFilesTruncated
    TRIGGERING_FEATURE_DIR  = $triggeringFeature
    KNOWN_CHANGES_HINT      = $KnownChanges
    JSON_EXPORT_ENABLED     = $true
    DEFAULT_EXCLUDES        = @($Script:DefaultMapExcludes | Sort-Object)
}

if ($Json) {
    $payload | ConvertTo-Json -Depth 6 -Compress
} else {
    $payload.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key): $($_.Value)" }
}
