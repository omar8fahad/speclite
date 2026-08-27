<#
.SYNOPSIS
    Detect where a speclite project/feature currently stands, and what to run next.

.DESCRIPTION
    This is what lets the manager skill chain phases automatically without the user
    having to remember the order or where they left off. Run any time; it never asks a
    question itself - it just reports NEXT_PHASE and REASON, and the calling agent
    decides how to act on that (including asking the user something, if
    NEEDS_USER_INPUT is true).

    Constitution (Phase 1) is recommended as the first thing to run in a brand-new
    project, but - matching Spec Kit's own model - it's not a hard gate: once a feature
    exists, its absence never blocks specify/plan/tasks/implement. Later phases just
    read .speclite/memory/principles.md "if it exists".
#>
[CmdletBinding()]
param([switch]$Json)

. (Join-Path $PSScriptRoot 'common.ps1')

function Write-StatusPayload {
    param([System.Collections.Specialized.OrderedDictionary]$Payload, [bool]$AsJson)
    if ($AsJson) {
        $Payload | ConvertTo-Json -Depth 5
    } else {
        $Payload.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key): $($_.Value)" }
    }
}

function Test-LogHasStatus {
    param([string]$LogText, [string[]]$Statuses)
    foreach ($status in $Statuses) {
        if ($LogText -match [regex]::Escape(" $status ") -or $LogText -match [regex]::Escape(" $status |")) {
            return $true
        }
    }
    return $false
}

$repoRoot = Get-RepoRoot -ScriptFile $PSCommandPath
$installed = Test-Path (Join-Path $repoRoot '.speclite') -PathType Container

$payload = [ordered]@{ INSTALLED = $installed; REPO_ROOT = $repoRoot }
if (-not $installed) {
    $payload['NEXT_PHASE'] = 'install'
    $payload['REASON'] = 'No .speclite/ directory found - run install.py / install.ps1 first.'
    $payload['NEEDS_USER_INPUT'] = $false
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

$allFeatures = @(Get-AllFeatures -RepoRoot $repoRoot)
$payload['ALL_FEATURES'] = $allFeatures
$hasProjectPrinciples = Test-Path (Get-ProjectPrinciplesPath -RepoRoot $repoRoot)
$payload['HAS_PROJECT_PRINCIPLES'] = $hasProjectPrinciples

$activeRel = Read-FeatureJson -RepoRoot $repoRoot
$activeFeatureDir = $null
if ($activeRel) {
    $candidate = Join-Path $repoRoot $activeRel
    if (Test-Path $candidate -PathType Container) { $activeFeatureDir = $candidate }
}

if (-not $activeFeatureDir -and $allFeatures.Count -eq 0) {
    # Nothing has started yet in this project at all.
    if (-not $hasProjectPrinciples) {
        $payload['ACTIVE_FEATURE'] = $null
        $payload['NEXT_PHASE'] = 'constitution'
        $payload['REASON'] = "No project constitution yet - recommended as Phase 1 before the first feature, though it's optional and can be skipped straight to specify."
        $payload['NEEDS_USER_INPUT'] = $false
        Write-StatusPayload -Payload $payload -AsJson $Json
        return
    }
    $payload['ACTIVE_FEATURE'] = $null
    $payload['NEXT_PHASE'] = 'specify'
    $payload['REASON'] = 'No feature exists yet - start with /speclite.specify.'
    $payload['NEEDS_USER_INPUT'] = $false
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

if (-not $activeFeatureDir) {
    if ($allFeatures.Count -eq 1) {
        $activeFeatureDir = Join-Path (Join-Path $repoRoot 'specs') $allFeatures[0]
    } else {
        $payload['ACTIVE_FEATURE'] = $null
        $payload['NEXT_PHASE'] = 'ambiguous'
        $payload['REASON'] = "$($allFeatures.Count) features exist and none is marked active - ask the user which one to resume (or whether to start a new one)."
        $payload['NEEDS_USER_INPUT'] = $true
        Write-StatusPayload -Payload $payload -AsJson $Json
        return
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
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

$specText = Get-Content -Raw -LiteralPath $spec
if ($specText -match '\[NEEDS CLARIFICATION') {
    $payload['NEXT_PHASE'] = 'specify'
    $payload['REASON'] = 'spec.md still has open [NEEDS CLARIFICATION] markers.'
    $payload['NEEDS_USER_INPUT'] = $true
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

if (-not (Test-Path $plan)) {
    $payload['NEXT_PHASE'] = 'plan'
    $payload['REASON'] = 'plan.md not created yet.'
    $payload['NEEDS_USER_INPUT'] = $false
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

$planText = Get-Content -Raw -LiteralPath $plan
$checklistSection = Get-SpecliteSection -MarkdownText $planText -Heading 'Pre-Implementation Checklist'
$uncheckedPlan = Get-UncheckedBoxCount -Text $checklistSection
if ($uncheckedPlan -gt 0) {
    $payload['NEXT_PHASE'] = 'plan'
    $payload['REASON'] = "$uncheckedPlan Pre-Implementation Checklist item(s) still unchecked in plan.md."
    $payload['NEEDS_USER_INPUT'] = $false
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

if (-not (Test-Path $tasks)) {
    $payload['NEXT_PHASE'] = 'tasks'
    $payload['REASON'] = 'tasks.md not created yet.'
    $payload['NEEDS_USER_INPUT'] = $false
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

$analyzeLog = Get-SpecliteLogText -BaseDir $activeFeatureDir -Phase 'tasks'
if (-not (Test-LogHasStatus -LogText $analyzeLog -Statuses @('PASS', 'WARN'))) {
    $payload['NEXT_PHASE'] = 'tasks'
    $payload['REASON'] = "tasks.md exists but the analyze consistency pass hasn't been logged yet."
    $payload['NEEDS_USER_INPUT'] = $false
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

$tasksText = Get-Content -Raw -LiteralPath $tasks
$uncheckedTasks = Get-UncheckedBoxCount -Text $tasksText
if ($uncheckedTasks -gt 0) {
    $payload['NEXT_PHASE'] = 'implement'
    $payload['REASON'] = "$uncheckedTasks task(s) still unchecked in tasks.md."
    $payload['NEEDS_USER_INPUT'] = $false
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

$implementLog = Get-SpecliteLogText -BaseDir $activeFeatureDir -Phase 'implement'
if (-not (Test-LogHasStatus -LogText $implementLog -Statuses @('PASS'))) {
    $payload['NEXT_PHASE'] = 'implement'
    $payload['REASON'] = "All tasks are checked off, but the final gap-check hasn't been logged as clean yet."
    $payload['NEEDS_USER_INPUT'] = $false
    Write-StatusPayload -Payload $payload -AsJson $Json
    return
}

$payload['NEXT_PHASE'] = 'done'
$payload['REASON'] = 'Everything is checked off and the final gap-check passed.'
$payload['NEEDS_USER_INPUT'] = $false
Write-StatusPayload -Payload $payload -AsJson $Json
