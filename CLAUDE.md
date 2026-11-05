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

## Comptes et monétisation
L'utilisateur réside au **Canada** (vérifié en novembre 2026) :
- **YouTube** : Programme Partenaire disponible. Plateforme prioritaire — seule vraie
  rémunération aux vues. Pubs à partir de 1 000 abonnés + 10 M vues Shorts / 90 jours.
- **TikTok** : Creator Rewards **non disponible** au Canada. Revenus via LIVE, Creator
  Marketplace, Series. Garder un compte personnel (pas Business).
- **Instagram** : cadeaux et abonnements disponibles ; bonus Reels sur invitation.
  Compte professionnel « Créateur ».

Un e-mail dédié à la chaîne a été créé. Comptes à créer dans l'ordre : YouTube, TikTok,
Instagram — même pseudo `@djamtala` partout si possible.

## Méthode de production
En cours de construction. Ce qui est en place :

1. **Montage** : une composition HyperFrames par vidéo dans `projets/<nom>/` (modèle :
   `projets/test-style`). Aperçu via `.claude/launch.json`, rendu MP4 dans `Export/`.
2. **Musique de fond** : `<audio>` dans `index.html`, fichier dans `projets/<nom>/assets/music/`,
   licence notée en commentaire. Volume discret (≈ -23 LUFS) pour laisser la place à la voix.
3. **Effets sonores** : skill `real-sfx` (installé dans `~/.claude/skills/real-sfx`,
   bibliothèque = `B-Roll/SFX/`, le sous-dossier `perso/` de sons de memes est exclu).
   Liste des sons calée sur les temps GSAP de la vidéo dans `projets/<nom>/sfx-cues.json`,
   puis `mix.py --target-lufs -14` → `Export/<nom>-sfx.mp4`.

4. **Voix off (provisoire, gratuite)** : texte dans `projets/<nom>/voix.txt`, puis
   `HYPERFRAMES_PYTHON=<python.exe> npx hyperframes tts voix.txt -v ff_siwis -o assets/voice/voix.wav`
   (Kokoro, local, licence Apache 2.0 ; `pip install kokoro-onnx soundfile`). Plus tard : vraies voix.
   Dans `index.html` : `<audio id="voice">` décalé de 0,2 s, musique baissée à `data-volume="0.32"`.
   **Voix MiniMax (EN PAUSE — l'utilisateur ne veut pas payer la recharge minimum de 25 $)** : `python outils/voix_minimax.py essai|voix|generer <voix.txt> --voix <id>`
   (API T2A, modèle `speech-2.8-hd`, `language_boost: French`, voix `French_MaleNarrator`,
   `French_FemaleAnchor`…). Clé API dans la variable d'environnement `MINIMAX_API_KEY`,
   jamais dans le projet. Payant (≈ 100 $ / M caractères, pas de crédit gratuit trouvé) ;
   droits commerciaux à vérifier dans leurs conditions avant de publier.
5. **Sous-titres** : `faster-whisper` (modèle `small`, `language="fr"`, `word_timestamps=True`,
   texte de `voix.txt` en `initial_prompt`) → `transcript.json` ; morceaux de 1 à 4 mots calés
   sur la voix, mots-clés en or (`.hl`). Le whisper-cpp de HyperFrames n'est pas installé.
6. **SFX sous la voix** : `mix.py ... --voice-safe --target-lufs -14`, `highpass: 140` sur les impacts.

## Scripts (outil anti-doublons)
Tous les scripts vivent dans `scripts/` (un fichier `NNN-titre.md` par vidéo) et sont gérés
par `python outils/scripts.py`. Tableau de bord : `scripts/INDEX.md` (généré, ne pas éditer).

**L'app « Djamtala Scripts »** : double-clic sur `Djamtala-Scripts.bat` (ou
`python outils/app_scripts.py`) → http://127.0.0.1:8765. Tableau par statut (glisser une carte
pour changer d'étape), recherche, édition du script, alerte doublon en direct. Elle écrit les
mêmes fichiers que la ligne de commande. Dans Claude : aperçu `scripts-app` de `.claude/launch.json`.

- **Avant d'écrire un script** : `python outils/scripts.py verifier "<sujet>"`. Un même sujet
  principal (ex. Mansa Moussa / Mansa Musa) bloque la création ; des mots en commun donnent un
  simple avertissement « sujet proche » → choisir un autre angle.
- Créer : `nouveau "<titre>" --sujet ... --pays ... --theme ... --mots a,b,c` (ou `--corps fichier.md`).
- Faire avancer : `statut <n°> idee|ecrit|verifie|voix|monte|publie [--lien URL]`.
- Toujours remplir « Sources à vérifier » : les faits historiques sont vérifiés avant `verifie`.

## Sons et musique
- **Sources** : Freesound en CC0 uniquement (liste à télécharger : `SFX-liste-freesound.md`).
  Openverse sert plutôt aux images d'archives / B-Roll.
- **Éviter** les sons de memes, de films, de jeux ou de marques (risque Content ID, ton
  pas adapté). BO de jeux vidéo : seulement si le compositeur l'autorise explicitement.
- Musique tendance : l'ajouter dans l'appli au moment de publier (licence de la plateforme).

## Références de style (s'inspirer, ne pas copier)
- instagram.com/reel/DecctgYO5KY — deconstruct.labb : infographie plate fond sombre.
- instagram.com/reel/DfP-dpzDGjc — alfred.explique : illustration affiche, titre orange.
- instagram.com/reel/DetdoAzxwx9 — ottok.zz : 3D filaire néon vert.

Formule commune : titre-accroche dès la 1re seconde, une scène animée centrale,
compteurs/étiquettes de données, voix off + sous-titres courts, fond sombre + accent
fort, question finale pour les commentaires.

## Identité visuelle Djamtala
**Or et indigo** : bleu nuit indigo (comme les tissus teints d'Afrique de l'Ouest) et or.
Éviter l'or orangé sur fond brun : ça rappelle trop la marque Claude.

Badge d'année en haut à droite, frise de motifs africains en bas (or + bleu), étiquettes
en police machine à écrire, illustrations plates style affiche.

| Rôle | Couleur |
|---|---|
| Fond | `#070914` |
| Scène / panneaux | `#10142B` |
| Titres, badge, accents (or) | `#F2C94C` |
| Éléments secondaires (bleu clair) | `#85B7EB` |
| Frise (bleu) | `#378ADD` |
| Texte / sous-titres | `#FFFFFF` |

**Police des titres** : Anton (Google Fonts), en majuscules, condensée.

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
