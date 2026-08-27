[CmdletBinding()]
param([switch]$Json)

. (Join-Path $PSScriptRoot 'common.ps1')

$paths = Get-FeaturePaths -ScriptFile $PSCommandPath

if (-not (Test-Path $paths.Spec)) {
    Write-Error "ERROR: spec.md not found in $($paths.FeatureDir). Run /speclite.specify first."
    exit 1
}

$specText = Get-Content -Raw -LiteralPath $paths.Spec
if ($specText -match '\[NEEDS CLARIFICATION') {
    Write-Error 'ERROR: spec.md still has open [NEEDS CLARIFICATION] markers. Finish /speclite.specify before planning.'
    exit 1
}

if (-not (Test-Path $paths.Plan)) {
    $template = Resolve-SpecliteTemplate -Name 'plan-template' -RepoRoot $paths.RepoRoot
    if ($template) {
        Copy-Item $template $paths.Plan
    } else {
        New-Item -ItemType File -Path $paths.Plan | Out-Null
    }
}

$references = @()
if (Test-Path $paths.ReferencesDir) {
    Get-ChildItem $paths.ReferencesDir -Directory | Sort-Object Name | ForEach-Object {
        $files = Get-ChildItem $_.FullName -File | Where-Object { $_.Name -ne '.gitkeep' }
        if ($files) { $references += "$($_.Name)/ ($($files.Count) file(s))" }
    }
}

$projectPrinciples = Get-ProjectPrinciplesPath -RepoRoot $paths.RepoRoot

$payload = [ordered]@{
    FEATURE_DIR     = $paths.FeatureDir
    SPEC_FILE       = $paths.Spec
    PLAN_FILE       = $paths.Plan
    PRINCIPLES_FILE = if (Test-Path $projectPrinciples) { $projectPrinciples } else { $null }
    REFERENCES      = $references
}

if ($Json) {
    $payload | ConvertTo-Json -Compress
} else {
    $payload.GetEnumerator() | ForEach-Object { Write-Output "$($_.Key): $($_.Value)" }
}
