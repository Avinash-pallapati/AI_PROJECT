# ==============================================================================
# Automate Remote Repository Creation and Push to GitHub
# ==============================================================================
$ErrorActionPreference = "Stop"

$ghPath = "C:\Program Files\GitHub CLI\gh.exe"
$gitPath = "C:\Users\palla\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe"

Write-Host "Verifying GitHub CLI authentication..." -ForegroundColor Cyan
& $ghPath auth status

Write-Host "Creating public GitHub repository 'AI_PROJECT' and pushing all commits..." -ForegroundColor Cyan
& $ghPath repo create AI_PROJECT --public --source="C:\Users\palla\Downloads\AI_PROJECT" --remote=origin --push --description "Hardware-Aware Per-Layer Mixed-Precision Optimization for Custom QCore-INT8 FPGA AI Accelerator (Tasks 1-9 Complete)"

Write-Host "Verifying remote repository..." -ForegroundColor Green
& $gitPath remote -v
& $gitPath branch -a

Write-Host "Repository published successfully!" -ForegroundColor Green
Write-Host "Access URL: https://github.com/Avinash-pallapati/AI_PROJECT" -ForegroundColor Yellow
