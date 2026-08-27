[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('constitution', 'specify', 'plan', 'tasks', 'implement')]
    [string]$Phase,

    [Parameter(Mandatory)]
    [ValidateSet('PASS', 'WARN', 'FAIL', 'INFO')]
    [string]$Status,

    [Parameter(Mandatory)]
    [string]$Summary,

    [string]$Details = ''
)

. (Join-Path $PSScriptRoot 'common.ps1')

$repoRoot = Get-RepoRoot -ScriptFile $PSCommandPath

if ($Phase -eq 'constitution') {
    $baseDir = Join-Path $repoRoot '.speclite'
} else {
    $paths = Get-FeaturePaths -ScriptFile $PSCommandPath
    $baseDir = $paths.FeatureDir
}

$logPath = Add-SpecliteLog -BaseDir $baseDir -Phase $Phase -Status $Status -Summary $Summary -Details $Details
Write-Output "Logged [$Status] ${Phase}: $Summary"
Write-Output "-> $logPath"
