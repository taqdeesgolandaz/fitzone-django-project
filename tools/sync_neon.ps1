param(
    [string]$RemoteUrl = $env:NEON_DATABASE_URL,
    [switch]$DryRun,
    [switch]$Import
)

$ErrorActionPreference = "Stop"

if (-not $RemoteUrl) {
    $RemoteUrl = $env:DATABASE_URL
}

if (-not $RemoteUrl) {
    Write-Error "No remote URL provided. Set NEON_DATABASE_URL or DATABASE_URL, or pass -RemoteUrl."
    exit 1
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "myenv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$commandArgs = @("manage.py", "sync_neon", "--remote-url", $RemoteUrl)

if ($DryRun) {
    $commandArgs += "--dry-run"
}
elseif ($Import) {
    $commandArgs += "--import"
}
else {
    $commandArgs += "--import"
}

Push-Location $repoRoot
try {
    & $pythonExe $commandArgs
}
finally {
    Pop-Location
}
