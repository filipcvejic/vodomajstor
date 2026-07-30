#!/usr/bin/env python3
"""Pravi samostalni (single-file) preview stranice za deljenje.

Ubacuje CSS i JS inline i pretvara placeholder SVG u data URI, jer preview
host blokira zahteve ka spoljnim fajlovima. Original u projektu ostaje
nepromenjen — ovo je samo izvozna kopija za pregled.

Upotreba:  python3 build-preview.py odgusenje-kanalizacije
"""
import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent


def build(slug: str) -> pathlib.Path:
    src = ROOT / slug / "index.html"
    html = src.read_text(encoding="utf-8")

    css = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
    js = (ROOT / "js" / "site.js").read_text(encoding="utf-8")

    svg = (ROOT / "slike" / "_placeholder.svg").read_bytes()
    data_uri = "data:image/svg+xml;base64," + base64.b64encode(svg).decode("ascii")

    # zadrži <title>, odbaci ostatak <head> i omotač dokumenta
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    body = html.split("<body>", 1)[1].rsplit("</body>", 1)[0]

    body = body.replace("/slike/_placeholder.svg", data_uri)
    body = body.replace('<script src="/js/site.js" defer></script>', "")

    out = ROOT / "preview" / f"{slug}.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        f"<title>{title}</title>\n"
        f"<style>\n{css}\n</style>\n"
        f"{body}\n"
        f"<script>\n{js}\n</script>\n",
        encoding="utf-8",
    )
    return out


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "odgusenje-kanalizacije"
    path = build(slug)
    print(f"{path}  ({path.stat().st_size / 1024:.1f} KB)")
