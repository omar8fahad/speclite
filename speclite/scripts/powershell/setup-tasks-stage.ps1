[CmdletBinding()]
param([switch]$Json)

. (Join-Path $PSScriptRoot 'common.ps1')

$paths = Get-FeaturePaths -ScriptFile $PSCommandPath

if (-not (Test-Path $paths.Plan)) {
    Write-Error "ERROR: plan.md not found in $($paths.FeatureDir). Run /speclite.plan first."
    exit 1
}

$planText = Get-Content -Raw -LiteralPath $paths.Plan
$checklistSection = Get-SpecliteSection -MarkdownText $planText -Heading 'Pre-Implementation Checklist'
$unchecked = Get-UncheckedBoxCount -Text $checklistSection
if ($unchecked -gt 0) {
    Write-Error "ERROR: plan.md's Pre-Implementation Checklist still has $unchecked unchecked item(s). Finish /speclite.plan before generating tasks."
    exit 1
}

if (-not (Test-Path $paths.Tasks)) {
    $template = Resolve-SpecliteTemplate -Name 'tasks-template' -RepoRoot $paths.RepoRoot
    if ($template) {
        Copy-Item $template $paths.Tasks
    } else {
        New-Item -ItemType File -Path $paths.Tasks | Out-Null
    }
}

$payload = [ordered]@{
    FEATURE_DIR = $paths.FeatureDir
    SPEC_FILE   = $paths.Spec
    PLAN_FILE   = $paths.Plan
    TASKS_FILE  = $paths.Tasks
}

if ($Json) {
    $payload | ConvertTo-Json -Compress
} else {
    $payload.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key): $($_.Value)" }
}
