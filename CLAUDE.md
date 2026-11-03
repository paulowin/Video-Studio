# Video-Studio — Djamtala

## La chaîne
- **Nom** : Djamtala
- **Sujet** : vidéos courtes sur l'histoire, la culture, les faits surprenants et les
  grandes personnalités de la Côte d'Ivoire et de l'Afrique.
- **Diffusion** : YouTube Shorts, TikTok et Instagram Reels — format vertical 9:16
  (1080×1920).
- **Style** : la nouvelle tendance des vidéos montées avec Claude (montage piloté par
  code / IA).
- **Langue** : français.

## Méthode de production
Pas encore définie. L'utilisateur regarde des tutos Instagram sur ce type de vidéos et
va décrire les outils et étapes qu'ils utilisent, pour construire ensemble son propre
processus. Quand c'est fait, documenter le processus ici.

## Outils installés
- **ffmpeg** (winget `Gyan.FFmpeg`) — conversion, découpe, assemblage.
- **Whisper** (`pip install openai-whisper`) — transcription / sous-titres.
- **Remotion** (`npm i -g @remotion/cli remotion`) — vidéos en React.
- **HyperFrames** (`npm i -g hyperframes`) — vidéos en HTML.

## Organisation des dossiers
- `A-Roll/` — rushs principaux (face caméra, voix).
- `B-Roll/` — images d'illustration, archives, plans de coupe.
- `References/` — vidéos et captures d'inspiration.
- `Export/` — vidéos finales.

Les fichiers médias (vidéo, audio, images lourdes) ne sont **pas** dans Git (voir
`.gitignore`) : Git ne synchronise que les scripts, textes et projets. Les médias se
synchronisent à part (OneDrive, Google Drive, disque externe…).

## Travailler sur deux PC
- Nouveau PC : lancer `setup.ps1` une fois.
- Au début et à la fin de chaque session : lancer `sync.ps1` (pull + commit + push).
