param(
    [string]$TaskName = "LinkedInJobsBotDaily",
    [string]$ScheduleTime = "09:00",
    [string]$ConfigPath = "..\config.json",
    [switch]$NoNotify
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runnerPath = (Resolve-Path (Join-Path $scriptDir "run_linkedin_jobs_bot.ps1")).Path
$projectRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path
$resolvedConfigPath = (Resolve-Path (Join-Path $scriptDir $ConfigPath)).Path

$timeParts = $ScheduleTime.Split(":")
if ($timeParts.Count -ne 2) {
    throw "Use o formato HH:mm para ScheduleTime. Exemplo: 09:00"
}

$hour = [int]$timeParts[0]
$minute = [int]$timeParts[1]
$triggerTime = Get-Date -Hour $hour -Minute $minute -Second 0
if ($triggerTime -lt (Get-Date)) {
    $triggerTime = $triggerTime.AddDays(1)
}

$argumentList = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", ('"{0}"' -f $runnerPath),
    "-ConfigPath", ('"{0}"' -f $resolvedConfigPath)
)

if ($NoNotify) {
    $argumentList += "-NoNotify"
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ($argumentList -join " ")
$trigger = New-ScheduledTaskTrigger -Daily -At $triggerTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Executa diariamente o LinkedIn Jobs Bot com coleta e envio de alertas." `
    -Force | Out-Null

Write-Host "Tarefa registrada com sucesso."
Write-Host "Nome: $TaskName"
Write-Host "Horario: $ScheduleTime"
Write-Host "Config: $resolvedConfigPath"
