param([string]$Feature)

if (-not $Feature) {
    Write-Host "Usage: .\automations\build_feature.ps1 -Feature 'mo ta tinh nang'"
    exit 1
}

Write-Host "=== BUILD: $Feature ==="

# 1. TestAgent
Write-Host "`n--- [1/3] TestAgent viet tests ---"
$TestOutput = & .\automations\run_agent.ps1 -AgentName "test-agent" -Prompt $Feature
Write-Host $TestOutput
$TestOutput | Out-File "$env:TEMP\w4_test.txt"

Read-Host "`nCopy test code vao backend/tests/ xong nhan Enter"

# 2. CodeAgent
Write-Host "`n--- [2/3] CodeAgent implement ---"
$TestContent = Get-Content "$env:TEMP\w4_test.txt" -Raw
$CodeOutput = & .\automations\run_agent.ps1 -AgentName "code-agent" -Prompt "Implement de pass tests sau:`n$TestContent"
Write-Host $CodeOutput
$CodeOutput | Out-File "$env:TEMP\w4_code.txt"

Read-Host "`nCopy code vao routers/ xong nhan Enter"

# 3. Chay test
Write-Host "`n--- [3/3] make test ---"
make test
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL - sua loi roi chay lai"
    exit 1
}

# 4. DocsAgent
Write-Host "`n--- DocsAgent viet docs ---"
$CodeContent = Get-Content "$env:TEMP\w4_code.txt" -Raw
& .\automations\run_agent.ps1 -AgentName "docs-agent" -Prompt "Feature: $Feature`nCode: $CodeContent"

Write-Host "`n=== XONG ==="
Write-Host "[] Paste docs vao docs/API.md"
Write-Host "[] make format && make lint"
Write-Host "[] git add . && git commit"