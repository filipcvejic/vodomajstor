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

DOMEN = "https://vodomajstor-beograd.rs"

ASSET_DIRS = ["css", "js", "slike", "video"]
PAGE_DIRS = ["odgusenje-kanalizacije", "hitne-intervencije", "detekcija-curenja-vode", "ugradnja-sanitarija", "vodovodne-instalacije", "adaptacija-kupatila", "sitne-popravke", "kontakt", "hvala"]


def build(prefix: str) -> pathlib.Path:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for d in ASSET_DIRS:
        src = ROOT / d
        if src.exists():
            shutil.copytree(src, OUT / d)

    # interni komentari iz CSS-a i JS-a nemaju šta da traže u izvoru koji je javan
    for f in list((OUT / "css").glob("*.css")) + list((OUT / "js").glob("*.js")):
        k = f.read_text(encoding="utf-8")
        k = re.sub(r"/\*.*?\*/", "", k, flags=re.S)
        k = re.sub(r"^\s*//.*$", "", k, flags=re.M)
        f.write_text(re.sub(r"\n{3,}", "\n\n", k).strip() + "\n", encoding="utf-8")

    def obradi(html: str) -> str:
        # HTML komentari ne idu u promet: interne beleške i sklonjena galerija
        # nemaju šta da traže u izvoru koji korisnik može da otvori
        html = re.sub(r"<!--(?!\[if).*?-->", "", html, flags=re.S)
        html = re.sub(r"\n{3,}", "\n\n", html)

        # apsolutne putanje ka fajlovima i stranicama dobijaju prefiks;
        # canonical, og:url i schema (puni URL-ovi) se ne diraju
        html = re.sub(r'((?:href|src)=")/(?!/)', r"\1" + prefix + "/", html)
        # srcset nosi više URL-ova u jednom atributu, pa ga gornji izraz ne hvata
        html = re.sub(r'(srcset=")([^"]*)"',
                      lambda m: m.group(1) + m.group(2).replace("/slike/", prefix + "/slike/") + '"',
                      html)

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
    # sitemap i robots idu samo na pravi domen, ne na staging
    if not prefix:
        adrese = ["/"] + [f"/{d}/" for d in PAGE_DIRS if d != "hvala"]
        stavke = "\n".join(
            f"  <url><loc>{DOMEN}{a}</loc><changefreq>monthly</changefreq>"
            f"<priority>{'1.0' if a == '/' else '0.8'}</priority></url>"
            for a in adrese
        )
        (OUT / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{stavke}\n</urlset>\n", encoding="utf-8")
        (OUT / "robots.txt").write_text(
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /hvala/\n\n"
            f"Sitemap: {DOMEN}/sitemap.xml\n", encoding="utf-8")

    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    return OUT


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    out = build(prefix)
    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    print(f"{out}  ({len(files)} fajlova)")
    for f in files:
        print("  ", f)
