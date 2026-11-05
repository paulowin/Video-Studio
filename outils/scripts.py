#!/usr/bin/env python3
"""Gestion des scripts Djamtala : un fichier par vidéo, un index, et un garde-fou anti-doublons.

Chaque script est un fichier Markdown dans `scripts/` (ex. `scripts/001-mansa-moussa-plus-riche.md`)
avec un en-tête (sujet, pays, thème, mots-clés, statut...) et le texte de la vidéo.
`scripts/INDEX.md` est régénéré à chaque modification : c'est le tableau de bord.

Utilisation (depuis le dossier Video-Studio) :
  python outils/scripts.py verifier "reine Pokou"               # déjà traité ? (avant d'écrire)
  python outils/scripts.py nouveau "Titre" --sujet "Reine Pokou" --pays "Côte d'Ivoire" \
         --theme histoire --mots baoule,exode,sacrifice          # refuse si doublon probable
  python outils/scripts.py liste [--statut publie]
  python outils/scripts.py voir 3
  python outils/scripts.py statut 3 publie [--lien https://youtube.com/shorts/...]
  python outils/scripts.py index                                # régénère INDEX.md

Statuts, dans l'ordre : idee -> ecrit -> verifie -> voix -> monte -> publie
"""
import argparse
import difflib
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "scripts"
INDEX = DOSSIER / "INDEX.md"

STATUTS = ["idee", "ecrit", "verifie", "voix", "monte", "publie"]
LIBELLES = {
    "idee": "💡 idée",
    "ecrit": "✍️ écrit",
    "verifie": "🔎 faits vérifiés",
    "voix": "🎙️ voix faite",
    "monte": "🎬 monté",
    "publie": "✅ publié",
}
CHAMPS = ["id", "titre", "sujet", "pays", "theme", "mots", "statut", "cree", "projet", "liens"]

MOTS_VIDES = set(
    "le la les l un une des de du d et ou a au aux en dans sur pour par avec sans qui que quoi "
    "dont ce cet cette ces son sa ses leur leurs il elle ils elles on se s est etait sont fut "
    "plus moins tres tout tous toute toutes comme mais ne pas n y qu c ca".split()
)

SEUIL_DOUBLON = 0.6   # au-dessus : doublon probable, création refusée sans --force
SEUIL_PROCHE = 0.3    # au-dessus : sujet proche, simple avertissement


# ---------- texte ----------

def normaliser(texte):
    t = unicodedata.normalize("NFD", texte.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def mots_cles(*textes):
    out = set()
    for t in textes:
        for m in normaliser(t).split():
            if m not in MOTS_VIDES and len(m) > 1:
                out.add(m)
    return out


def slug(texte, maxi=40):
    s = normaliser(texte).replace(" ", "-")
    return s[:maxi].rstrip("-") or "script"


# ---------- fichiers ----------

def lire(chemin):
    texte = chemin.read_text(encoding="utf-8")
    meta, corps = {}, texte
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", texte, re.S)
    if m:
        for ligne in m.group(1).splitlines():
            if ":" in ligne:
                k, v = ligne.split(":", 1)
                v = v.strip()
                if v.startswith("[") and v.endswith("]"):
                    v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
                meta[k.strip()] = v
        corps = m.group(2)
    meta.setdefault("mots", [])
    meta.setdefault("liens", [])
    for k in ("mots", "liens"):
        if isinstance(meta[k], str):
            meta[k] = [x.strip() for x in meta[k].split(",") if x.strip()]
    meta["_chemin"] = chemin
    meta["_corps"] = corps
    return meta


def ecrire(meta):
    lignes = ["---"]
    for k in CHAMPS:
        v = meta.get(k, "")
        if isinstance(v, list):
            v = "[" + ", ".join(v) + "]"
        lignes.append(f"{k}: {v}")
    lignes.append("---")
    meta["_chemin"].write_text("\n".join(lignes) + "\n" + meta["_corps"], encoding="utf-8")


def tous():
    if not DOSSIER.exists():
        return []
    out = [lire(p) for p in sorted(DOSSIER.glob("[0-9][0-9][0-9]-*.md"))]
    return sorted(out, key=lambda m: int(m.get("id", 0)))


def trouver(ident):
    for m in tous():
        if str(int(m["id"])) == str(int(ident)):
            return m
    sys.exit(f"Aucun script avec le numéro {ident}. Voir : python outils/scripts.py liste")


# ---------- doublons ----------

def score(candidat, existant):
    """0 = rien à voir, 1 = même sujet. Le sujet principal pèse le plus lourd."""
    s1, s2 = normaliser(candidat["sujet"]), normaliser(existant.get("sujet", ""))
    if s1 and s2:
        if s1 == s2:
            return 1.0, "même sujet principal"
        r = difflib.SequenceMatcher(None, s1, s2).ratio()
        if r >= 0.8:
            return r, f"sujet presque identique (« {existant['sujet']} »)"
    a = mots_cles(candidat["titre"], candidat["sujet"], " ".join(candidat["mots"]))
    b = mots_cles(existant.get("titre", ""), existant.get("sujet", ""), " ".join(existant.get("mots", [])))
    if not a or not b:
        return 0.0, ""
    communs = a & b
    # mots proches (Moussa / Musa, Pokou / Poku)
    for x in a - communs:
        for y in b - communs:
            if len(x) > 3 and difflib.SequenceMatcher(None, x, y).ratio() >= 0.8:
                communs = communs | {x}
                break
    j = len(communs) / min(len(a), len(b))
    if s1 and s2:
        # sujets principaux différents : des mots en commun font un sujet proche, jamais un doublon
        j = min(j, SEUIL_DOUBLON - 0.05)
    return j, ("mots en commun : " + ", ".join(sorted(communs))) if communs else ""


def chercher_doublons(candidat):
    res = []
    for m in tous():
        s, pourquoi = score(candidat, m)
        if s >= SEUIL_PROCHE:
            res.append((s, pourquoi, m))
    return sorted(res, key=lambda x: -x[0])


def afficher_doublons(res):
    for s, pourquoi, m in res:
        niveau = "DOUBLON PROBABLE" if s >= SEUIL_DOUBLON else "sujet proche"
        print(f"  [{niveau} {s:.0%}] #{int(m['id']):03d} « {m['titre']} » "
              f"({LIBELLES.get(m.get('statut'), m.get('statut'))}) — {pourquoi}")


# ---------- index ----------

def regenerer_index():
    DOSSIER.mkdir(exist_ok=True)
    scripts = tous()
    lignes = [
        "# Scripts Djamtala — tableau de bord",
        "",
        "Fichier généré par `python outils/scripts.py` : ne pas modifier à la main.",
        "",
    ]
    compte = {s: sum(1 for m in scripts if m.get("statut") == s) for s in STATUTS}
    lignes.append(" · ".join(f"{LIBELLES[s]} : {compte[s]}" for s in STATUTS) + f" · **total : {len(scripts)}**")
    lignes += ["", "| # | Titre | Sujet | Pays | Thème | Statut | Fichier |", "|---|---|---|---|---|---|---|"]
    for m in scripts:
        f = m["_chemin"].name
        lignes.append(
            f"| {int(m['id']):03d} | {m.get('titre','')} | {m.get('sujet','')} | {m.get('pays','')} | "
            f"{m.get('theme','')} | {LIBELLES.get(m.get('statut'), m.get('statut',''))} | [{f}]({f}) |"
        )
    sujets = sorted({m.get("sujet", "") for m in scripts if m.get("sujet")}, key=normaliser)
    lignes += ["", "## Sujets déjà traités", "", ", ".join(sujets) if sujets else "_aucun_", ""]
    INDEX.write_text("\n".join(lignes), encoding="utf-8")


# ---------- commandes ----------

MODELE = """
# {titre}

## Accroche (1re seconde, à l'écran)


## Voix off


## Scènes et visuels
-

## Question finale (commentaires)


## Sources à vérifier
-

## Notes
"""


def cmd_verifier(a):
    cand = {"titre": a.texte, "sujet": a.texte, "mots": a.mots.split(",") if a.mots else []}
    res = chercher_doublons(cand)
    if not res:
        print(f"OK : rien de proche de « {a.texte} » parmi {len(tous())} script(s).")
    else:
        print(f"Attention, « {a.texte} » ressemble à :")
        afficher_doublons(res)


def creer(titre, sujet, pays="", theme="", mots=None, statut="idee", projet="", corps=None):
    """Crée le fichier du script et régénère l'index. Ne vérifie pas les doublons (voir chercher_doublons)."""
    DOSSIER.mkdir(exist_ok=True)
    num = max([int(m["id"]) for m in tous()] or [0]) + 1
    meta = {
        "id": f"{num:03d}", "titre": titre, "sujet": sujet, "pays": pays or "",
        "theme": theme or "", "mots": mots or [], "statut": statut, "cree": date.today().isoformat(),
        "projet": projet or "", "liens": [],
        "_chemin": DOSSIER / f"{num:03d}-{slug(titre)}.md",
        "_corps": ("\n" + corps.strip() + "\n") if corps else MODELE.format(titre=titre),
    }
    ecrire(meta)
    regenerer_index()
    return meta


def cmd_nouveau(a):
    mots = [x.strip() for x in a.mots.split(",") if x.strip()] if a.mots else []
    res = chercher_doublons({"titre": a.titre, "sujet": a.sujet, "mots": mots})
    if res:
        print("Sujets déjà présents qui ressemblent :")
        afficher_doublons(res)
        if res[0][0] >= SEUIL_DOUBLON and not a.force:
            sys.exit("\nCréation refusée : doublon probable. Choisis un autre angle, "
                     "ou ajoute --force si c'est voulu (ex. une partie 2).")
    corps = Path(a.corps).read_text(encoding="utf-8") if a.corps else None
    meta = creer(a.titre, a.sujet, a.pays, a.theme, mots, a.statut, a.projet, corps)
    print(f"Créé : scripts/{meta['_chemin'].name}  (#{int(meta['id']):03d}, statut {LIBELLES[a.statut]})")


def cmd_liste(a):
    scripts = [m for m in tous() if not a.statut or m.get("statut") == a.statut]
    if not scripts:
        print("Aucun script." if not a.statut else f"Aucun script au statut {a.statut}.")
        return
    for m in scripts:
        print(f"#{int(m['id']):03d}  {LIBELLES.get(m.get('statut'), m.get('statut','')):18s} "
              f"{m.get('titre','')}  [{m.get('sujet','')}]")


def cmd_voir(a):
    m = trouver(a.id)
    print(m["_chemin"].read_text(encoding="utf-8"))


def cmd_statut(a):
    m = trouver(a.id)
    avant = m.get("statut")
    m["statut"] = a.statut
    if a.lien:
        m["liens"] = m.get("liens", []) + [a.lien]
    if a.projet:
        m["projet"] = a.projet
    ecrire(m)
    regenerer_index()
    print(f"#{int(m['id']):03d} « {m['titre']} » : {LIBELLES.get(avant, avant)} -> {LIBELLES[a.statut]}")


def main():
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Gestion des scripts Djamtala")
    sp = p.add_subparsers(dest="cmd", required=True)

    v = sp.add_parser("verifier", help="un sujet est-il déjà traité ?")
    v.add_argument("texte")
    v.add_argument("--mots", help="mots-clés séparés par des virgules")
    v.set_defaults(f=cmd_verifier)

    n = sp.add_parser("nouveau", help="créer un script (refuse les doublons)")
    n.add_argument("titre")
    n.add_argument("--sujet", required=True, help="le personnage / événement / lieu principal")
    n.add_argument("--pays")
    n.add_argument("--theme", help="histoire, culture, personnalite, fait-surprenant...")
    n.add_argument("--mots", help="mots-clés séparés par des virgules")
    n.add_argument("--statut", choices=STATUTS, default="idee")
    n.add_argument("--projet", help="dossier HyperFrames, ex. projets/test-style")
    n.add_argument("--corps", help="fichier .md dont le contenu devient le texte du script")
    n.add_argument("--force", action="store_true", help="créer même si doublon probable")
    n.set_defaults(f=cmd_nouveau)

    l = sp.add_parser("liste", help="lister les scripts")
    l.add_argument("--statut", choices=STATUTS)
    l.set_defaults(f=cmd_liste)

    o = sp.add_parser("voir", help="afficher un script")
    o.add_argument("id")
    o.set_defaults(f=cmd_voir)

    s = sp.add_parser("statut", help="changer le statut d'un script")
    s.add_argument("id")
    s.add_argument("statut", choices=STATUTS)
    s.add_argument("--lien", help="lien de la vidéo publiée")
    s.add_argument("--projet")
    s.set_defaults(f=cmd_statut)

    i = sp.add_parser("index", help="régénérer scripts/INDEX.md")
    i.set_defaults(f=lambda a: (regenerer_index(), print("INDEX.md régénéré.")))

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
