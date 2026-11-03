# Installe les outils du projet Djamtala sur un nouveau PC.
# Usage : powershell -ExecutionPolicy Bypass -File setup.ps1

winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements --silent
winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements --silent
winget install --id Python.Python.3.14 -e --accept-source-agreements --accept-package-agreements --silent

$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')

python -m pip install -U openai-whisper
npm install -g @remotion/cli remotion hyperframes

# Rend la commande `whisper` accessible
$scripts = python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
$userPath = [Environment]::GetEnvironmentVariable('Path','User')
if ($userPath -notlike "*$scripts*") { [Environment]::SetEnvironmentVariable('Path', "$userPath;$scripts", 'User') }

Write-Host "Installation terminée. Ouvre un nouveau terminal."
