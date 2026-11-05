#!/usr/bin/env python3
"""Djamtala Scripts : l'app locale pour gérer les scripts (tableau, édition, anti-doublons).

Lancer :  python outils/app_scripts.py        (ou double-clic sur Djamtala-Scripts.bat)
Puis ouvrir http://127.0.0.1:8765 (s'ouvre tout seul). Fermer la fenêtre noire pour arrêter.

L'app ne fait que lire et écrire les fichiers de `scripts/` (via outils/scripts.py) :
tout reste compatible avec la ligne de commande et avec Git.
"""
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scripts as S  # noqa: E402

HOTE, PORT = "127.0.0.1", 8765
PAGE = Path(__file__).resolve().parent / "app_scripts.html"
CHAMPS_EDITABLES = ["titre", "sujet", "pays", "theme", "mots", "statut", "projet", "liens"]


def public(m, corps=False):
    d = {k: m.get(k, "") for k in S.CHAMPS}
    d["id"] = int(m["id"])
    d["fichier"] = m["_chemin"].name
    if corps:
        d["corps"] = m["_corps"]
    return d


def par_id(ident):
    for m in S.tous():
        if int(m["id"]) == int(ident):
            return m
    return None


def liste(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip() for x in str(v or "").split(",") if x.strip()]


def doublons(titre, sujet, mots, sauf=None):
    res = S.chercher_doublons({"titre": titre or "", "sujet": sujet or "", "mots": liste(mots)})
    return [
        {"score": round(s, 2), "niveau": "doublon" if s >= S.SEUIL_DOUBLON else "proche",
         "pourquoi": pourquoi, "id": int(m["id"]), "titre": m.get("titre", ""),
         "statut": m.get("statut", "")}
        for s, pourquoi, m in res if sauf is None or int(m["id"]) != int(sauf)
    ]


class App(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def envoyer(self, code, corps, type_="application/json; charset=utf-8"):
        data = corps if isinstance(corps, bytes) else json.dumps(corps, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", type_)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def lire_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.envoyer(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/scripts":
            return self.envoyer(200, {"scripts": [public(m) for m in S.tous()],
                                      "statuts": S.STATUTS, "libelles": S.LIBELLES})
        if self.path.startswith("/api/scripts/"):
            m = par_id(self.path.rsplit("/", 1)[1])
            return self.envoyer(200, public(m, True)) if m else self.envoyer(404, {"erreur": "introuvable"})
        self.envoyer(404, {"erreur": "introuvable"})

    def do_POST(self):
        d = self.lire_json()
        if self.path == "/api/verifier":
            return self.envoyer(200, {"doublons": doublons(d.get("titre"), d.get("sujet"), d.get("mots"), d.get("sauf"))})
        if self.path == "/api/scripts":
            titre, sujet = (d.get("titre") or "").strip(), (d.get("sujet") or "").strip()
            if not titre or not sujet:
                return self.envoyer(400, {"erreur": "Le titre et le sujet principal sont obligatoires."})
            res = doublons(titre, sujet, d.get("mots"))
            if any(r["niveau"] == "doublon" for r in res) and not d.get("force"):
                return self.envoyer(409, {"erreur": "Doublon probable", "doublons": res})
            statut = d.get("statut") if d.get("statut") in S.STATUTS else "idee"
            m = S.creer(titre, sujet, d.get("pays", ""), d.get("theme", ""), liste(d.get("mots")),
                        statut, d.get("projet", ""), d.get("corps") or None)
            return self.envoyer(201, public(m, True))
        self.envoyer(404, {"erreur": "introuvable"})

    def do_PUT(self):
        if not self.path.startswith("/api/scripts/"):
            return self.envoyer(404, {"erreur": "introuvable"})
        m = par_id(self.path.rsplit("/", 1)[1])
        if not m:
            return self.envoyer(404, {"erreur": "introuvable"})
        d = self.lire_json()
        for k in CHAMPS_EDITABLES:
            if k in d:
                m[k] = liste(d[k]) if k in ("mots", "liens") else str(d[k]).replace("\n", " ").strip()
        if m.get("statut") not in S.STATUTS:
            return self.envoyer(400, {"erreur": "statut inconnu"})
        if "corps" in d:
            corps = d["corps"].replace("\r\n", "\n")
            m["_corps"] = corps if corps.startswith("\n") else "\n" + corps
        S.ecrire(m)
        S.regenerer_index()
        self.envoyer(200, public(m, True))


def main():
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8")
    S.DOSSIER.mkdir(exist_ok=True)
    try:
        srv = ThreadingHTTPServer((HOTE, PORT), App)
    except OSError:
        print(f"L'app tourne déjà : http://{HOTE}:{PORT}")
        webbrowser.open(f"http://{HOTE}:{PORT}")
        return
    url = f"http://{HOTE}:{PORT}"
    print(f"Djamtala Scripts : {url}   (ferme cette fenêtre pour arrêter)")
    if "--no-open" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    srv.serve_forever()


if __name__ == "__main__":
    main()
