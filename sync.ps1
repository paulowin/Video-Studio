# Synchronise le projet avec GitHub : récupère les changements de l'autre PC,
# puis envoie les tiens. Lance-le au début et à la fin de chaque session.
# Usage : powershell -ExecutionPolicy Bypass -File sync.ps1

Set-Location $PSScriptRoot

git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Sync depuis $env:COMPUTERNAME — $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

git pull --rebase origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Conflit pendant la récupération. Demande à Claude de le résoudre." -ForegroundColor Red
    exit 1
}

git push origin main
Write-Host "Synchronisé." -ForegroundColor Green
