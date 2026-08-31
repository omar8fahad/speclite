<#
.SYNOPSIS
    Detect where a speclite project/feature currently stands, and what to run next.

.DESCRIPTION
    This is what lets the manager skill chain phases automatically without the user
    having to remember the order or where they left off. Run any time; it never asks a
    question itself - it just reports NEXT_PHASE and REASON, and the calling agent
    decides how to act on that (including asking the user something, if
    NEEDS_USER_INPUT is true).

    Every phase's completion is read directly from its artifact, Spec Kit's own style -
    there is no separate check-log this script relies on:
      - specify:   spec.md has no [NEEDS CLARIFICATION] marker left
      - plan:      plan.md's Pre-Implementation Checklist is fully checked
      - tasks:     tasks.md's "Analysis complete" checkbox is ticked
      - implement: every task is [X] AND tasks.md's Final Gap-Check checkbox is ticked

    Constitution (Phase 1) is recommended as the first thing to run in a brand-new
    project, but - matching Spec Kit's own model - it's not a hard gate: once a feature
    exists, its absence never blocks specify/plan/tasks/implement. Later phases just
    read .speclite/memory/principles.md "if it exists".

    Also computes MAP_SUGGESTION/MAP_REASON - a purely informational, non-blocking nudge
    about the optional Project Map. This never affects NEXT_PHASE; the calling agent
    decides *when* to actually mention it (natural breakpoints, not mid-phase).
#>
[CmdletBinding()]
param([switch]$Json)

. (Join-Path $PSScriptRoot 'common.ps1')

$Script:OwnScaffolding = @('.speclite', '.agents', 'skills', 'specs', 'speclite', '.git')

function Get-MapSuggestion {
    param([string]$RepoRoot)
    $mapPaths = Get-MapFilePaths -RepoRoot $RepoRoot
    $projectMap = $mapPaths.project_map

    if (-not (Test-Path $projectMap)) {
        $hasOtherFiles = $false
        Get-ChildItem $RepoRoot -Force | ForEach-Object {
            if ($Script:OwnScaffolding -notcontains $_.Name) { $hasOtherFiles = $true }
        }
        if ($hasOtherFiles) {
            return @{
                MAP_SUGGESTION = 'build'
                MAP_REASON     = "There's real code in this repo and no project map yet - consider suggesting /speclite.map at a natural breakpoint (project start, or right after a feature completes)."
            }
        }
        return @{ MAP_SUGGESTION = $null; MAP_REASON = $null }
    }

    $mapMtime = (Get-Item $projectMap).LastWriteTime
    $newestTasksMtime = [datetime]::MinValue
    foreach ($feature in (Get-AllFeatures -RepoRoot $RepoRoot)) {
        $tasksPath = Join-Path (Join-Path $RepoRoot 'specs') "$feature/tasks.md"
        if (Test-Path $tasksPath) {
            $mtime = (Get-Item $tasksPath).LastWriteTime
            if ($mtime -gt $newestTasksMtime) { $newestTasksMtime = $mtime }
        }
    }

    if ($newestTasksMtime -gt $mapMtime) {
        return @{
            MAP_SUGGESTION = 'update'
            MAP_REASON     = "A feature's tasks.md changed more recently than the last map sync - consider suggesting /speclite.map (feature-integration) at a natural breakpoint, such as right after implement finishes."
        }
    }
    return @{ MAP_SUGGESTION = $null; MAP_REASON = $null }
}

function Get-SpecliteStatus {
    param([string]$RepoRoot)

    $installed = Test-Path (Join-Path $RepoRoot '.speclite') -PathType Container
    $payload = [ordered]@{ INSTALLED = $installed; REPO_ROOT = $RepoRoot }
    if (-not $installed) {
        $payload['NEXT_PHASE'] = 'install'
        $payload['REASON'] = 'No .speclite/ directory found - run install.py / install.ps1 first.'
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    $allFeatures = @(Get-AllFeatures -RepoRoot $RepoRoot)
    $payload['ALL_FEATURES'] = $allFeatures
    $hasProjectPrinciples = Test-Path (Get-ProjectPrinciplesPath -RepoRoot $RepoRoot)
    $payload['HAS_PROJECT_PRINCIPLES'] = $hasProjectPrinciples

    $activeRel = Read-FeatureJson -RepoRoot $RepoRoot
    $activeFeatureDir = $null
    if ($activeRel) {
        $candidate = Join-Path $RepoRoot $activeRel
        if (Test-Path $candidate -PathType Container) { $activeFeatureDir = $candidate }
    }

    if (-not $activeFeatureDir -and $allFeatures.Count -eq 0) {
        if (-not $hasProjectPrinciples) {
            $payload['ACTIVE_FEATURE'] = $null
            $payload['NEXT_PHASE'] = 'constitution'
            $payload['REASON'] = "No project constitution yet - recommended as Phase 1 before the first feature, though it's optional and can be skipped straight to specify."
            $payload['NEEDS_USER_INPUT'] = $false
            return $payload
        }
        $payload['ACTIVE_FEATURE'] = $null
        $payload['NEXT_PHASE'] = 'specify'
        $payload['REASON'] = 'No feature exists yet - start with /speclite.specify.'
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    if (-not $activeFeatureDir) {
        if ($allFeatures.Count -eq 1) {
            $activeFeatureDir = Join-Path (Join-Path $RepoRoot 'specs') $allFeatures[0]
        } else {
            $payload['ACTIVE_FEATURE'] = $null
            $payload['NEXT_PHASE'] = 'ambiguous'
            $payload['REASON'] = "$($allFeatures.Count) features exist and none is marked active - ask the user which one to resume (or whether to start a new one)."
            $payload['NEEDS_USER_INPUT'] = $true
            return $payload
        }
    }

    $payload['ACTIVE_FEATURE'] = $activeFeatureDir

    $spec = Join-Path $activeFeatureDir 'spec.md'
    $plan = Join-Path $activeFeatureDir 'plan.md'
    $tasks = Join-Path $activeFeatureDir 'tasks.md'

    if (-not (Test-Path $spec)) {
        $payload['NEXT_PHASE'] = 'specify'
        $payload['REASON'] = 'spec.md not created yet.'
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    $specText = Get-Content -Raw -LiteralPath $spec
    if ($specText -match '\[NEEDS CLARIFICATION') {
        $payload['NEXT_PHASE'] = 'specify'
        $payload['REASON'] = 'spec.md still has open [NEEDS CLARIFICATION] markers.'
        $payload['NEEDS_USER_INPUT'] = $true
        return $payload
    }

    if (-not (Test-Path $plan)) {
        $payload['NEXT_PHASE'] = 'plan'
        $payload['REASON'] = 'plan.md not created yet.'
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    $planText = Get-Content -Raw -LiteralPath $plan
    $checklistSection = Get-SpecliteSection -MarkdownText $planText -Heading 'Pre-Implementation Checklist'
    $uncheckedPlan = Get-UncheckedBoxCount -Text $checklistSection
    if ($uncheckedPlan -gt 0) {
        $payload['NEXT_PHASE'] = 'plan'
        $payload['REASON'] = "$uncheckedPlan Pre-Implementation Checklist item(s) still unchecked in plan.md."
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    if (-not (Test-Path $tasks)) {
        $payload['NEXT_PHASE'] = 'tasks'
        $payload['REASON'] = 'tasks.md not created yet.'
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    $tasksText = Get-Content -Raw -LiteralPath $tasks
    if (-not (Test-MarkerChecked -Text $tasksText -Marker 'Analysis complete')) {
        $payload['NEXT_PHASE'] = 'tasks'
        $payload['REASON'] = "tasks.md exists but the Analysis Pass checkbox isn't checked yet."
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    $uncheckedTasks = Get-UncheckedTaskCount -Text $tasksText
    if ($uncheckedTasks -gt 0) {
        $payload['NEXT_PHASE'] = 'implement'
        $payload['REASON'] = "$uncheckedTasks task(s) still unchecked in tasks.md."
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    if (-not (Test-MarkerChecked -Text $tasksText -Marker 'Verified against spec.md')) {
        $payload['NEXT_PHASE'] = 'implement'
        $payload['REASON'] = "All tasks are checked off, but the Final Gap-Check checkbox isn't checked yet."
        $payload['NEEDS_USER_INPUT'] = $false
        return $payload
    }

    $payload['NEXT_PHASE'] = 'done'
    $payload['REASON'] = 'Everything is checked off and the final gap-check passed.'
    $payload['NEEDS_USER_INPUT'] = $false
    return $payload
}

$repoRoot = Get-RepoRoot -ScriptFile $PSCommandPath
$payload = Get-SpecliteStatus -RepoRoot $repoRoot

if ($payload['INSTALLED']) {
    $suggestion = Get-MapSuggestion -RepoRoot $repoRoot
    foreach ($key in $suggestion.Keys) { $payload[$key] = $suggestion[$key] }
}

if ($Json) {
    $payload | ConvertTo-Json -Depth 5
} else {
    $payload.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key): $($_.Value)" }
}
