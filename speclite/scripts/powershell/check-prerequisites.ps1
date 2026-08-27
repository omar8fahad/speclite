[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$RequirePlan,
    [switch]$RequireTasks,
    [switch]$PathsOnly
)

. (Join-Path $PSScriptRoot 'common.ps1')

$paths = Get-FeaturePaths -NoPersist:$PathsOnly -ScriptFile $PSCommandPath

if ($PathsOnly) {
    $payload = [ordered]@{
        REPO_ROOT   = $paths.RepoRoot
        FEATURE_DIR = $paths.FeatureDir
        SPEC_FILE   = $paths.Spec
        PLAN_FILE   = $paths.Plan
        TASKS_FILE  = $paths.Tasks
        LOGS_DIR    = $paths.LogsDir
    }
    if ($Json) { $payload | ConvertTo-Json -Compress }
    else { $payload.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key): $($_.Value)" } }
    exit 0
}

if (-not (Test-Path $paths.Spec)) {
    Write-Error "ERROR: spec.md not found in $($paths.FeatureDir). Run /speclite.specify first."
    exit 1
}
if ($RequirePlan -and -not (Test-Path $paths.Plan)) {
    Write-Error "ERROR: plan.md not found in $($paths.FeatureDir). Run /speclite.plan first."
    exit 1
}
if ($RequireTasks -and -not (Test-Path $paths.Tasks)) {
    Write-Error "ERROR: tasks.md not found in $($paths.FeatureDir). Run /speclite.tasks first."
    exit 1
}
if ($RequireTasks -and (Test-Path $paths.Tasks)) {
    $tasksText = Get-Content -Raw -LiteralPath $paths.Tasks
    if ((Get-UncheckedBoxCount -Text $tasksText) -eq 0 -and $tasksText -notmatch 'T00') {
        Write-Error "ERROR: tasks.md in $($paths.FeatureDir) has no tasks yet. Run /speclite.tasks first."
        exit 1
    }
}

$docs = @()
if (Test-Path $paths.Plan) { $docs += 'plan.md' }
if (Test-Path $paths.Tasks) { $docs += 'tasks.md' }
if (Test-Path (Get-ProjectPrinciplesPath -RepoRoot $paths.RepoRoot)) { $docs += 'principles.md (project-wide)' }
if (Test-Path $paths.ReferencesDir) {
    Get-ChildItem $paths.ReferencesDir -Directory | Sort-Object Name | ForEach-Object {
        $hasFiles = Get-ChildItem $_.FullName -File | Where-Object { $_.Name -ne '.gitkeep' }
        if ($hasFiles) { $docs += "references/$($_.Name)/" }
    }
}

$payload = [ordered]@{ FEATURE_DIR = $paths.FeatureDir; AVAILABLE_DOCS = $docs }
if ($Json) {
    $payload | ConvertTo-Json -Compress
} else {
    Write-Output "FEATURE_DIR: $($paths.FeatureDir)"
    Write-Output "AVAILABLE_DOCS: $(if ($docs.Count -gt 0) { $docs -join ', ' } else { '(none)' })"
}
