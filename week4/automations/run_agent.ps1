param(
    [string]$AgentName,
    [string]$Prompt
)

$Model = "kimi-k2.5:cloud"
$AgentFile = "automations/agents/$AgentName.md"

if (-not (Test-Path $AgentFile)) {
    Write-Host "Agent khong ton tai: $AgentName"
    Write-Host "Co san:"
    Get-ChildItem "automations/agents/" -Filter "*.md" | ForEach-Object { $_.BaseName }
    exit 1
}

$System = Get-Content $AgentFile -Raw

Write-Host ""
Write-Host "=== $AgentName ==="
Write-Host ""

$FullPrompt = "$System`n---`nTASK: $Prompt"
ollama run $Model $FullPrompt