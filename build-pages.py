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
PAGE_DIRS = ["odgusenje-kanalizacije", "hitne-intervencije"]

# Prekidač paleta — postoji SAMO na staging kopiji, ne u izvornom kodu.
STAGING_HEAD = """<link rel="stylesheet" href="{prefix}/css/palete.css?v={v}">
<script>
  (function () {{
    var q = new URLSearchParams(location.search);
    var p = q.get("paleta");
    if (p) document.documentElement.setAttribute("data-paleta", p);
    if (q.get("hero") === "centar") {{
      document.addEventListener("DOMContentLoaded", function () {{
        var h = document.querySelector(".hero");
        if (h) h.classList.add("hero--centar");
      }});
    }}
  }})();
</script>
"""

SWITCH = """<nav class="paleta-switch" aria-label="Izbor palete">
  <a href="?paleta=petrol">Petrol</a>
  <a href="?paleta=teget">Teget</a>
  <a href="?paleta=grafit">Grafit</a>
  <a href="?paleta=maslina">Maslina</a>
  <a href="?paleta=mornarska">Mornarska</a>
  <a href="?paleta=petrol-narandza">Narandža</a>
  <a href="?hero=centar">Hero centar</a>
</nav>
<script>
  (function () {{
    var p = new URLSearchParams(location.search).get("paleta") || "petrol";
    var a = document.querySelector('.paleta-switch a[href="?paleta=' + p + '"]');
    if (a) a.setAttribute("data-active", "");
  }})();
</script>
""".replace("{{", "{").replace("}}", "}")


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
        html = html.replace("</head>", STAGING_HEAD.format(prefix=prefix, v=stamp("css/palete.css")) + "</head>")
        html = html.replace("<body>", "<body>\n" + SWITCH)

        # GitHub Pages kesira fajlove 10 minuta. Bez ovoga se posle deploya ume
        # ucitati nov HTML sa starim CSS-om, pa stranica izgleda razvaljeno.
        html = html.replace("/css/style.css", "/css/style.css?v=" + stamp("css/style.css"))
        html = html.replace("/js/site.js", "/js/site.js?v=" + stamp("js/site.js"))

        dst.write_text(html, encoding="utf-8")

    # spisak gotovih stranica dok home ne postoji
    veze = "\n".join(
        f'<li><a href="{prefix}/{d}/">/{d}/</a></li>' for d in PAGE_DIRS
    )
    (OUT / "index.html").write_text(
        "<title>VodoMajstor Beograd — pregled</title>"
        "<style>body{font:16px/1.6 system-ui;margin:40px;max-width:40rem}</style>"
        f"<h1>Gotove stranice</h1><ul>{veze}</ul>",
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
