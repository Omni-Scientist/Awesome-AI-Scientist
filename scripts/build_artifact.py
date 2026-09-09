#!/usr/bin/env python3
"""Fold the multi-page site into one self-contained file for claude.ai Artifacts.

The host wraps the output in its own <!doctype>/<head>/<body>, so this emits
page content only: one shared nav and footer, every route as a <div data-route>,
and a hash router. Sub-category pages are left out; their sub-tabs become
in-page anchors to the same entries on the category page, so nothing dead-ends.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/_artifact.html"

ROUTES = ["", "ai-scientists", "research", "domains", "resources", "benchmarks", "learn", "about"]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import FONTS  # noqa: E402  single source for the webfont URL

GFONTS = f"@import url('{FONTS}');"

ROUTER = """
(function () {
  var pages = [].slice.call(document.querySelectorAll('[data-route]'));
  var links = [].slice.call(document.querySelectorAll('[data-nav]'));
  function show(id, anchor) {
    var hit = null;
    pages.forEach(function (p) {
      var on = p.dataset.route === id;
      p.hidden = !on;
      if (on) hit = p;
    });
    links.forEach(function (a) {
      if (a.dataset.nav === id) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    if (hit && window.__aaisListing) window.__aaisListing(hit);
    if (anchor) {
      var el = document.getElementById(anchor);
      if (el) { el.scrollIntoView({ block: 'start' }); return; }
    }
    window.scrollTo(0, 0);
  }
  function route() {
    var h = location.hash.replace(/^#/, '');
    if (!h) return show('home', null);
    if (pages.some(function (p) { return p.dataset.route === h; })) return show(h, null);
    var el = document.getElementById(h);
    var owner = el && el.closest('[data-route]');
    if (owner) return show(owner.dataset.route, h);
    show('home', null);
  }
  window.addEventListener('hashchange', route);
  route();
})();
"""


def content_of(html):
    body = re.search(r"</nav>(.*?)<footer", html, re.S)
    return body.group(1).strip()


def inline_avatars(fragment):
    """The Artifact CSP blocks external images, so logos and icons ship as data URIs."""
    import base64
    cache = {}

    def sub(m):
        name = m.group(1)
        if name not in cache:
            f = DOCS / f"assets/avatars/{name}.png"
            cache[name] = ("data:image/png;base64,"
                           + base64.b64encode(f.read_bytes()).decode()) if f.exists() else ""
        return 'src="%s"' % cache[name]

    def sub_icon(m):
        f = DOCS / f"assets/icons/{m.group(1)}.svg"
        if not f.exists():
            return m.group(0)
        return ('src="data:image/svg+xml;base64,'
                + base64.b64encode(f.read_bytes()).decode() + '"')

    fragment = re.sub(r'src="(?:\.\./)*assets/avatars/([^."]+)\.png"', sub, fragment)
    return re.sub(r'src="(?:\.\./)*assets/icons/([^."]+)\.svg"', sub_icon, fragment)


def rewrite(fragment):
    """Turn on-disk paths into hash routes."""
    def sub(m):
        href = m.group(1)
        if href.startswith(("http", "#", "mailto:")):
            return m.group(0)
        clean = href.lstrip("./")
        while clean.startswith("../"):
            clean = clean[3:]
        clean = clean.strip("/")
        if clean.startswith("assets"):
            return 'href="#"'
        if clean == "":
            return 'href="#"'
        parts = clean.split("/")
        if len(parts) == 2:                      # category/sub -> the group on the category page
            return 'href="#g-%s-%s"' % (parts[0], parts[1])
        return 'href="#%s"' % parts[0]
    return re.sub(r'href="([^"]*)"', sub, fragment)


def main():
    css = (DOCS / "assets/site.css").read_text(encoding="utf-8")
    js = (DOCS / "assets/site.js").read_text(encoding="utf-8")
    home = (DOCS / "index.html").read_text(encoding="utf-8")

    nav = rewrite(re.search(r"(<nav class=\"nav\">.*?</nav>)", home, re.S).group(1))
    nav = re.sub(r'<a href="#([a-z-]+)"', lambda m: '<a data-nav="%s" href="#%s"' % (m.group(1), m.group(1)), nav)
    nav = nav.replace('class="brand" href="#"', 'class="brand" data-nav="home" href="#"')
    foot = rewrite(re.search(r"(<footer class=\"foot\">.*?</footer>)", home, re.S).group(1))

    blocks = []
    for slug in ROUTES:
        path = DOCS / (slug + "/index.html" if slug else "index.html")
        frag = inline_avatars(rewrite(content_of(path.read_text(encoding="utf-8"))))
        rid = slug or "home"
        blocks.append('<div data-route="%s"%s>%s</div>'
                      % (rid, "" if rid == "home" else " hidden", frag))

    css = css.replace("/* ============================================================",
                      GFONTS + "\n/* ============================================================", 1)
    assert GFONTS in css, "font import not injected"

    page = ("<title>Awesome AI Scientist</title>\n"
            f"<style>\n{css}\n</style>\n{nav}\n" + "\n".join(blocks) + f"\n{foot}\n"
            f"<script>\n{js}\n{ROUTER}\n</script>\n")
    page = "".join(ch if ord(ch) < 128 else f"&#{ord(ch)};" for ch in page)

    for banned in ("<!doctype", "<html", "<head>", "<body>"):
        assert banned not in page.lower(), f"host skeleton tag leaked: {banned}"
    assert max(map(ord, page)) < 128, "non-ascii survived"
    left = re.findall(r'src="(?!data:)([^"]+)"', page)
    assert not left, f"images that would be blocked: {left[:3]}"
    dead = [h for h in re.findall(r'href="([^"]+)"', page)
            if not h.startswith(("http", "#", "mailto:"))]
    assert not dead, f"unrewritten links: {dead[:5]}"

    OUT.write_text(page, encoding="ascii")
    print(f"{OUT.name}  {OUT.stat().st_size / 1024:.0f} KB  "
          f"{len(blocks)} routes  (pure ASCII)")


if __name__ == "__main__":
    main()
