#!/usr/bin/env python3
"""Priprema sajt za GitHub Pages (project site, servira se iz /vodomajstor/).

Izvorni kod koristi apsolutne putanje (/css/style.css), jer je to tačno za
pravi domen. GitHub Pages servira projekat iz poddirektorijuma, pa se te
putanje ovde prepisuju u kopiji. Original ostaje netaknut.

Upotreba:  python3 build-pages.py [prefiks]     (podrazumevano /vodomajstor)
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "_pages"

ASSET_DIRS = ["css", "js", "slike"]
PAGE_DIRS = ["odgusenje-kanalizacije"]


def build(prefix: str) -> pathlib.Path:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for d in ASSET_DIRS:
        src = ROOT / d
        if src.exists():
            shutil.copytree(src, OUT / d)

    for d in PAGE_DIRS:
        src = ROOT / d / "index.html"
        if not src.exists():
            continue
        dst = OUT / d / "index.html"
        dst.parent.mkdir(parents=True, exist_ok=True)

        html = src.read_text(encoding="utf-8")
        # apsolutne putanje ka fajlovima i stranicama dobijaju prefiks;
        # canonical, og:url i schema (puni URL-ovi) se ne diraju
        html = re.sub(r'((?:href|src)=")/(?!/)', r"\1" + prefix + "/", html)
        dst.write_text(html, encoding="utf-8")

    # prva stranica je ujedno i ulaz dok home ne postoji
    (OUT / "index.html").write_text(
        f'<meta http-equiv="refresh" content="0; url={prefix}/odgusenje-kanalizacije/">\n'
        f'<p><a href="{prefix}/odgusenje-kanalizacije/">Odgušenje kanalizacije</a></p>\n',
        encoding="utf-8",
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
