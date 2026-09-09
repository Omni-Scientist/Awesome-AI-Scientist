#!/usr/bin/env python3
"""Verify the built site in a real browser. Every page, not a spot check."""
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, "/home/bobo/workspace/papers/21_ai_scientist/webdev/tools")
from cdp import CDP, launch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_readme import parse                              # noqa: E402
from taxonomy import CATEGORIES, find, entries_of           # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CHROME = "/home/bobo/.cache/ms-playwright/chromium-1234/chrome-linux/chrome"
BASE = "http://127.0.0.1:8790/"

fails = []


def check(name, got, want):
    ok = want(got) if callable(want) else got == want
    show = got if not isinstance(got, list) or len(got) < 6 else got[:5] + ["..."]
    print(("  PASS  " if ok else "  FAIL  ") + name.ljust(46) + f" {show!r}")
    if not ok:
        fails.append(name)


def all_pages():
    return sorted(p for p in DOCS.rglob("index.html")) + [DOCS / "404.html"]


def static_checks():
    print("static")
    pages = all_pages()
    check("page count", len(pages), 31)

    titles, canons, descs, bad_links, orphan_assets = [], [], [], [], []
    for f in pages:
        h = f.read_text(encoding="utf-8")
        rel = f.relative_to(DOCS).as_posix()
        t = re.search(r"<title>(.*?)</title>", h, re.S)
        c = re.search(r'<link rel="canonical" href="([^"]+)"', h)
        d = re.search(r'name="description" content="([^"]*)"', h)
        titles.append(t.group(1) if t else f"MISSING:{rel}")
        if c:
            canons.append(c.group(1))
        descs.append((rel, len(d.group(1)) if d else 0))
        if len(re.findall(r"<h1", h)) != 1:
            bad_links.append(f"{rel}: h1 count")
        # every internal href must resolve on disk
        for href in re.findall(r'href="((?:\.\./|assets/|[a-z0-9-]+/)[^"#:]*)"', h):
            target = (f.parent / href).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                bad_links.append(f"{rel} -> {href}")

    check("every page has a title", [t for t in titles if t.startswith("MISSING")], [])
    check("all titles unique", len(set(titles)), len(titles))
    check("all canonicals unique", len(set(canons)), len(canons))
    check("canonical on every indexable page", len(canons), 31)
    check("no description under 60 chars",
          [r for r, n in descs if n < 60 and r != "404.html"], [])
    check("no description over 300 chars", [r for r, n in descs if n > 300], [])
    check("every internal link resolves", bad_links, [])

    css = (DOCS / "assets/site.css").read_text()
    check("no character-width caps force early wrapping",
          re.findall(r"max-width:\s*\d+ch", css), [])
    for rule in (".btn {", ".btn.solid {", ".badge {", ".card {", ".mapcat-head {"):
        check(f"stylesheet keeps {rule.strip(' {')}", rule in css, True)

    for name in ("robots.txt", "sitemap.xml", ".nojekyll", "assets/site.css",
                 "assets/site.js", "assets/og.png", "assets/favicon.svg"):
        check(f"file exists: {name}", (DOCS / name).exists(), True)

    sm = (DOCS / "sitemap.xml").read_text()
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    check("sitemap lists every page", len(locs), 30)
    check("sitemap has no duplicates", len(set(locs)), len(locs))

    # the taxonomy must still consume the whole README
    sections, skipped = parse(ROOT / "README.md")
    total = sum(len(s["entries"]) + sum(len(x["entries"]) for x in s["subs"]) for s in sections)
    mapped = sum(len(entries_of(find(sections, src)))
                 for _, _, _, _, subs in CATEGORIES for _, _, src, _ in subs)
    check("taxonomy covers the whole README", mapped, total)
    check("parser skips only the criteria bullets", len(skipped), 4)

    home = (DOCS / "index.html").read_text()
    check("homepage lists no entries, only the map",
          len(re.findall(r'class="card"', home)), 0)
    check("homepage links every category", len(re.findall(r'class="mapcat-head"', home)), 6)
    check("homepage links every sub-category",
          len(re.findall(r'<li><a href="[a-z-]+/[a-z-]+/"', home)), 22)
    check("homepage is short", len(home), lambda n: n < 40000)
    check("every heading carries a line of context",
          len(re.findall(r'class="mapcat-note"', home)), 6)
    check("homepage json-ld parses",
          bool(json.loads(re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                                     home, re.S)[-1])), True)
    cat = (DOCS / "ai-scientists/index.html").read_text()
    check("category page holds its entries", len(re.findall(r'class="card"', cat)), 62)

    avatars = {f.stem for f in (DOCS / "assets/avatars").glob("*.png")}
    missing = sorted(set(re.findall(r'assets/avatars/([^."]+)\.png', cat)) - avatars)
    check("every logo referenced exists", missing, [])
    check("cards carry a logo or an initial",
          len(re.findall(r'class="ava', cat)), 62)
    about = (DOCS / "about/index.html").read_text()
    for phrase in ("How the site is built", "What makes a strong entry",
                   "Star counts come from"):
        check(f"About does not explain itself: {phrase[:22]}", phrase in about, False)

    check("no editor's-pick marker survives",
          sum('class="pick"' in f.read_text() for f in all_pages()), 0)


def live_checks():
    print("\nlive browser")
    proc, ws = launch(9345, CHROME)
    try:
        c = CDP(ws)
        c.call("Page.enable")
        c.call("Runtime.enable")
        c.call("Page.addScriptToEvaluateOnNewDocument",
               source="window.__e=[];addEventListener('error',"
                      "function(e){window.__e.push(''+e.message)},true);")

        errs = []
        for url in ["", "ai-scientists/", "research/", "research/ideation/", "domains/biology/",
                    "resources/workbenches/", "benchmarks/", "learn/surveys/", "about/"]:
            c.call("Page.navigate", url=BASE + url)
            time.sleep(1.7)
            e = c.js("JSON.stringify(window.__e)")
            if e != "[]":
                errs.append(url + " " + e)
        check("no console errors on any page", errs, [])

        c.call("Page.navigate", url=BASE)
        time.sleep(1.8)
        check("section notes fit on one line", c.js("""
          (function(){
            return [].slice.call(document.querySelectorAll('.mapcat-note'))
              .filter(function(p){
                var lh = parseFloat(getComputedStyle(p).lineHeight);
                return p.getBoundingClientRect().height > lh * 1.4;
              }).map(function(p){ return p.textContent.slice(0, 24); });
          })()"""), [])

        c.call("Page.navigate", url=BASE + "benchmarks/")
        time.sleep(2.2)
        total = c.js("document.querySelectorAll('.card').length")
        check("benchmarks page card count", total, 90)
        # wait for the face to arrive, then prove it is the one being drawn with
        check("webfont loaded and applied", c.js('document.fonts.ready.then(function(){var mk=function(f){var s=document.createElement("span");s.style.cssText="position:absolute;visibility:hidden;font-size:64px;font-family:"+f;s.textContent="Awesome Scientist";document.body.appendChild(s);var w=s.getBoundingClientRect().width;s.remove();return Math.round(w)};return document.fonts.check(\'700 32px "Noto Sans"\') && mk(\'"Noto Sans"\')!==mk("serif");})'), True)

        c.js("var q=document.querySelector('[data-role=\"q\"]');q.value='reproducibility';"
             "q.dispatchEvent(new Event('input'))")
        time.sleep(0.6)
        check("search filters", c.js("document.querySelectorAll('.card.is-hidden').length"),
              lambda n: 0 < n < total)
        check("counter updates", c.js("document.querySelector('[data-role=\"count\"]').textContent"),
              lambda t: " of " in t)
        c.js("var q=document.querySelector('[data-role=\"q\"]');q.value='';q.dispatchEvent(new Event('input'))")
        time.sleep(0.5)
        check("clearing restores all",
              c.js("document.querySelectorAll('.card.is-hidden').length"), 0)

        c.js("var y=document.querySelector('[data-role=\"year\"]');y.value='2024';"
             "y.dispatchEvent(new Event('change'))")
        time.sleep(0.5)
        check("year filter keeps only that year", c.js(
            "[].slice.call(document.querySelectorAll('.card:not(.is-hidden)'))"
            ".every(function(e){return e.dataset.year==='2024'})"), True)
        c.js("var y=document.querySelector('[data-role=\"year\"]');y.value='';"
             "y.dispatchEvent(new Event('change'))")
        time.sleep(0.4)

        c.js("var s=document.querySelector('[data-role=\"sort\"]');s.value='stars';"
             "s.dispatchEvent(new Event('change'))")
        time.sleep(0.5)
        check("sort by stars descends", c.js(
            "(function(){var g=document.querySelector('.grid');"
            "var k=[].slice.call(g.children).map(function(e){return Number(e.dataset.stars)||-1});"
            "for(var i=1;i<k.length;i++){if(k[i]>k[i-1])return false}return true})()"), True)

        c.js("document.getElementById('theme').click()")
        time.sleep(0.3)
        check("theme toggles", c.js("document.documentElement.getAttribute('data-theme')"), "dark")
        check("dark ground is actually dark", c.js(
            "getComputedStyle(document.body).backgroundColor"), "rgb(14, 17, 22)")

        c.call("Page.navigate", url=BASE + "domains/?q=protein")
        time.sleep(2.0)
        check("deep-link ?q= filters on load",
              c.js("document.querySelectorAll('.card.is-hidden').length"), lambda n: n > 0)

        for w, h, label in ((390, 844, "phone"), (768, 1024, "tablet")):
            c.call("Emulation.setDeviceMetricsOverride", width=w, height=h,
                   deviceScaleFactor=2, mobile=w < 700)
            for url in ["", "resources/"]:
                c.call("Page.navigate", url=BASE + url)
                time.sleep(1.8)
                check(f"no sideways scroll on {label} /{url}", c.js(
                    "document.documentElement.scrollWidth<="
                    "document.documentElement.clientWidth"), True)
    finally:
        proc.kill()


def serving():
    try:
        with urllib.request.urlopen(BASE, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    server = None
    if serving():
        print(f"reusing the preview server on {BASE}\n")
    else:
        server = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8790", "--bind", "127.0.0.1"],
            cwd=DOCS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5)
    try:
        static_checks()
        live_checks()
    finally:
        if server is not None:
            server.terminate()
    print()
    if fails:
        print(f"FAILED ({len(fails)}): " + "; ".join(fails))
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
