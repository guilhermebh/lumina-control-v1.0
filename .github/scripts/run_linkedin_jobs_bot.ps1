param(
    [string]$ConfigPath = "..\config.json",
    [switch]$NoNotify
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$resolvedConfigPath = (Resolve-Path (Join-Path $scriptDir $ConfigPath)).Path
$pythonCmd = "python"

$arguments = @(
    (Join-Path $projectRoot "main.py"),
    "--config",
    $resolvedConfigPath,
    "--collect"
)

if ($NoNotify) {
    $arguments += "--no-notify"
}

Push-Location $projectRoot
try {
    & $pythonCmd @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Execucao do bot falhou com codigo $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
