#!/usr/bin/env python3
"""Priprema sajt za GitHub Pages (project site, servira se iz /vodomajstor/).

Izvorni kod koristi apsolutne putanje (/css/style.css), jer je to tačno za
pravi domen. GitHub Pages servira projekat iz poddirektorijuma, pa se te
putanje ovde prepisuju u kopiji. Original ostaje netaknut.

Upotreba:  python3 build-pages.py [prefiks]     (podrazumevano /vodomajstor)
"""
import hashlib
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "_pages"


def stamp(rel):
    """Kratak otisak sadrzaja fajla, za probijanje kesa posle deploya."""
    import hashlib
    return hashlib.sha1((ROOT / rel).read_bytes()).hexdigest()[:8]

ASSET_DIRS = ["css", "js", "slike"]
PAGE_DIRS = ["odgusenje-kanalizacije", "hitne-intervencije", "detekcija-curenja-vode", "ugradnja-sanitarija", "vodovodne-instalacije", "adaptacija-kupatila", "sitne-popravke", "kontakt", "hvala"]


def build(prefix: str) -> pathlib.Path:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for d in ASSET_DIRS:
        src = ROOT / d
        if src.exists():
            shutil.copytree(src, OUT / d)

    def obradi(html: str) -> str:
        # apsolutne putanje ka fajlovima i stranicama dobijaju prefiks;
        # canonical, og:url i schema (puni URL-ovi) se ne diraju
        html = re.sub(r'((?:href|src)=")/(?!/)', r"\1" + prefix + "/", html)

        # GitHub Pages kesira fajlove 10 minuta. Bez ovoga se posle deploya ume
        # ucitati nov HTML sa starim CSS-om, pa stranica izgleda razvaljeno.
        html = html.replace("/css/style.css", "/css/style.css?v=" + stamp("css/style.css"))
        return html.replace("/js/site.js", "/js/site.js?v=" + stamp("js/site.js"))

    for d in PAGE_DIRS:
        src = ROOT / d / "index.html"
        if not src.exists():
            continue
        dst = OUT / d / "index.html"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(obradi(src.read_text(encoding="utf-8")), encoding="utf-8")

    # home ide u koren, kroz istu obradu
    home = ROOT / "index.html"
    if home.exists():
        (OUT / "index.html").write_text(
            obradi(home.read_text(encoding="utf-8")), encoding="utf-8"
        )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    return OUT


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "/vodomajstor"
    out = build(prefix)
    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    print(f"{out}  ({len(files)} fajlova)")
    for f in files:
        print("  ", f)
