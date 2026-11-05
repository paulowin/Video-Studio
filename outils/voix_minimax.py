#!/usr/bin/env python3
"""Voix off Djamtala avec MiniMax (API T2A, platform.minimax.io).

La clé API n'est JAMAIS écrite dans le projet : elle est lue dans la variable
d'environnement MINIMAX_API_KEY (à définir une fois sur chaque PC, voir CLAUDE.md).

Utilisation (depuis le dossier Video-Studio) :
  python outils/voix_minimax.py voix                       # liste les voix françaises du compte
  python outils/voix_minimax.py generer projets/test-style/voix.txt \
         --voix French_MaleNarrator [--emotion calm] [--vitesse 1.0] \
         [--sortie projets/test-style/assets/voice/voix.wav]
  python outils/voix_minimax.py essai --voix French_MaleNarrator     # une phrase test, peu de crédits

Coût indicatif : speech-2.8-hd = 100 $ / million de caractères (≈ 0,04 $ pour un Short de 400 caractères).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.minimax.io/v1"
VOIX_FR = [
    "French_MaleNarrator", "French_Male_Speech_New", "French_CasualMan",
    "French_FemaleAnchor", "French_MovieLeadFemale", "French_Female_News Anchor",
]
EMOTIONS = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent"]
PHRASE_ESSAI = ("En 1324, cet empereur était plus riche que tous les rois d'Europe. "
                "Il s'appelle Mansa Moussa, roi du Mali.")


def cle():
    k = os.environ.get("MINIMAX_API_KEY", "").strip()
    if not k:
        sys.exit("Clé absente : définis la variable MINIMAX_API_KEY (voir CLAUDE.md, section Voix off).")
    return k


def appel(chemin, corps):
    req = urllib.request.Request(
        f"{API}/{chemin}", data=json.dumps(corps).encode("utf-8"), method="POST",
        headers={"Authorization": f"Bearer {cle()}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            rep = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"Erreur HTTP {e.code} : {e.read().decode('utf-8', 'replace')[:300]}")
    br = rep.get("base_resp", {})
    if br.get("status_code", 0) != 0:
        aide = {1004: "clé API refusée", 1002: "trop de requêtes, réessaie dans une minute",
                1008: "solde insuffisant : recharge ton compte MiniMax",
                2013: "paramètre invalide (voix ou émotion ?)"}
        code = br.get("status_code")
        sys.exit(f"MiniMax refuse ({code}) : {br.get('status_msg')} — {aide.get(code, '')}")
    return rep


def cmd_voix(a):
    rep = appel("get_voice", {"voice_type": "all"})
    toutes = (rep.get("system_voice") or []) + (rep.get("voice_cloning") or []) + (rep.get("voice_generation") or [])
    fr = [v for v in toutes if "french" in (v.get("voice_id", "") + " " + str(v.get("voice_name", ""))).lower()
          or v in (rep.get("voice_cloning") or []) or v in (rep.get("voice_generation") or [])]
    for v in fr:
        desc = v.get("description") or ""
        if isinstance(desc, list):
            desc = " ".join(desc)
        print(f"  {v.get('voice_id'):32s} {v.get('voice_name', '') or ''}  {desc}")
    print(f"{len(fr)} voix (françaises + tes voix clonées/créées).")


def synthese(texte, a, sortie):
    corps = {
        "model": a.modele,
        "text": texte,
        "stream": False,
        "language_boost": "French",
        "output_format": "hex",
        "voice_setting": {"voice_id": a.voix, "speed": a.vitesse, "vol": 1, "pitch": a.hauteur},
        "audio_setting": {"sample_rate": 44100, "format": "wav", "channel": 1},
    }
    if a.emotion:
        corps["voice_setting"]["emotion"] = a.emotion
    rep = appel("t2a_v2", corps)
    audio = bytes.fromhex(rep["data"]["audio"])
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_bytes(audio)
    info = rep.get("extra_info", {})
    print(f"OK : {sortie}  ({info.get('audio_length', 0) / 1000:.1f} s, "
          f"{info.get('usage_characters', '?')} caractères facturés, voix {a.voix})")


def cmd_generer(a):
    src = Path(a.texte)
    texte = src.read_text(encoding="utf-8").strip()
    if len(texte) >= 10000:
        sys.exit("Texte trop long (10 000 caractères max).")
    sortie = Path(a.sortie) if a.sortie else src.parent / "assets" / "voice" / "voix.wav"
    synthese(texte, a, sortie)


def cmd_essai(a):
    sortie = Path(a.sortie or f"Export/essai-voix-{a.voix.replace(' ', '_')}.wav")
    synthese(PHRASE_ESSAI, a, sortie)


def main():
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Voix off MiniMax pour Djamtala")
    sp = p.add_subparsers(dest="cmd", required=True)

    sp.add_parser("voix", help="lister les voix françaises").set_defaults(f=cmd_voix)

    for nom, f, aide in (("generer", cmd_generer, "générer la voix d'un fichier texte"),
                         ("essai", cmd_essai, "une phrase test pour comparer les voix")):
        g = sp.add_parser(nom, help=aide)
        if nom == "generer":
            g.add_argument("texte", help="fichier .txt (ex. projets/test-style/voix.txt)")
        g.add_argument("--voix", default="French_MaleNarrator", help="voice_id (voir la commande voix)")
        g.add_argument("--emotion", choices=EMOTIONS)
        g.add_argument("--vitesse", type=float, default=1.0, help="0.5 à 2")
        g.add_argument("--hauteur", type=int, default=0, help="-12 à 12")
        g.add_argument("--modele", default="speech-2.8-hd", help="speech-2.8-hd ou speech-2.8-turbo (moins cher)")
        g.add_argument("--sortie", help="fichier .wav de sortie")
        g.set_defaults(f=f)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
