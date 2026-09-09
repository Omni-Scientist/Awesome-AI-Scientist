#!/usr/bin/env python3
"""Generate the multi-page site in docs/ from README.md.

One page per browse category and per sub-category, plus a real homepage.
Every number on the site is computed from the README or from the GitHub API
cache; nothing here is hand-written.
"""
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_readme import parse                                   # noqa: E402
from taxonomy import CATEGORIES, SORT, STYLE, find, entries_of, icon  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CACHE = ROOT / "scripts/.stars_cache.json"

SITE = "https://omni-scientist.github.io/Awesome-AI-Scientist/"
REPO = "https://github.com/Omni-Scientist/Awesome-AI-Scientist"
TAGLINE = "A curated map of AI systems that automate and accelerate scientific discovery."

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Noto+Sans:wght@400;500;600;700;800&display=swap")

I = {  # 14px line icons, currentColor
    "paper": '<svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.5 1.5H4a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V5z"/><path d="M9.5 1.5V5H13"/></svg>',
    "code": '<svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5.5 11 2.5 8l3-3M10.5 5l3 3-3 3"/></svg>',
    "globe": '<svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="8" cy="8" r="6.2"/><path d="M1.8 8h12.4M8 1.8c1.7 1.9 2.5 4 2.5 6.2S9.7 12.3 8 14.2C6.3 12.3 5.5 10.2 5.5 8S6.3 3.7 8 1.8Z"/></svg>',
    "search": '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="7.2" cy="7.2" r="4.7"/><path d="m10.8 10.8 2.7 2.7"/></svg>',
    "moon": '<svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M13.5 9.6A5.8 5.8 0 0 1 6.4 2.5a5.8 5.8 0 1 0 7.1 7.1Z"/></svg>',
    "github": '<svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 .2a8 8 0 0 0-2.5 15.6c.4.1.5-.2.5-.4v-1.4c-2 .4-2.5-.5-2.7-1 0-.1-.5-.9-.9-1.1-.3-.2-.8-.6 0-.6.7 0 1.2.7 1.4 1 .8 1.3 2 1 2.5.8.1-.6.3-1 .6-1.2-2-.2-4-1-4-4.4 0-1 .3-1.8.9-2.4-.1-.2-.4-1.1.1-2.3 0 0 .7-.2 2.4.9a8.2 8.2 0 0 1 4.4 0c1.7-1.1 2.4-.9 2.4-.9.5 1.2.2 2.1.1 2.3.6.6.9 1.4.9 2.4 0 3.4-2 4.2-4 4.4.3.3.6.8.6 1.7v2.5c0 .2.1.5.5.4A8 8 0 0 0 8 .2Z"/></svg>',
    "hf": '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.6A9.4 9.4 0 1 0 21.4 12 9.4 9.4 0 0 0 12 2.6Zm-3.4 6.9a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6Zm6.8 0a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6ZM12 17.6a4.9 4.9 0 0 1-4.6-3.2.8.8 0 0 1 1.5-.5 3.3 3.3 0 0 0 6.2 0 .8.8 0 0 1 1.5.5 4.9 4.9 0 0 1-4.6 3.2Z"/></svg>',
    "chart": '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M2.5 13.5V7M6.5 13.5V3M10.5 13.5v-4M14 13.5H2"/></svg>',
    "box": '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M8 1.8 14 5v6l-6 3.2L2 11V5Z"/><path d="M2 5l6 3.2L14 5M8 8.2v6"/></svg>',
    "star": '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 1.6l1.9 3.9 4.3.6-3.1 3 .7 4.3L8 11.4l-3.8 2 .7-4.3-3.1-3 4.3-.6Z"/></svg>',
}
EXT = '<svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 2h6v6M10 2 2.5 9.5"/></svg>'
MARK = ('<svg width="17" height="17" viewBox="0 0 20 20" aria-hidden="true">'
        '<rect x="1.5" y="1.5" width="17" height="17" rx="5" fill="none" stroke="var(--border-2)"/>'
        '<circle cx="7.6" cy="10" r="3.1" fill="var(--teal)"/>'
        '<circle cx="12.6" cy="10" r="3.1" fill="var(--orange)" opacity=".85"/></svg>')


def esc(t):
    return html.escape(t or "", quote=True)


def human(n):
    if n is None:
        return None
    if n >= 10000:
        return "%.0fk" % (n / 1000.0)
    if n >= 1000:
        return "%.1fk" % (n / 1000.0)
    return str(n)


# ---------------------------------------------------------------- data

def created_of(entry, stars):
    """Best available creation date, as (year, month).

    The arXiv identifier encodes the posting month exactly, so it wins where it
    exists; otherwise the repository's own creation date; otherwise the
    publication year, placed mid-year since the month is unknown.
    """
    arxiv = entry["meta"].get("arxiv")
    if arxiv and "." in arxiv:
        head = arxiv.split(".")[0]
        if len(head) == 4 and head.isdigit():
            return (2000 + int(head[:2]), int(head[2:]))
    src = entry["meta"].get("stars_src")
    made = stars.get(src, {}).get("created") if src else None
    if made:
        return (int(made[:4]), int(made[5:7]))
    if entry.get("year"):
        return (entry["year"], 6)
    return (0, 0)


def enrich(sections, stars, first_seen):
    """Attach year, owner and star count. All three are derived, never invented."""
    for sec in sections:
        for node in [sec] + sec["subs"]:
            for e in node["entries"]:
                m = e["meta"]
                src = m.get("stars_src")
                e["stars"] = stars.get(src, {}).get("stars") if src else None
                e["org"] = src.split("/")[0] if src else ""
                year = None
                if m.get("venue"):
                    hit = re.search(r"\b(20\d{2})\b", m["venue"])
                    if hit:
                        year = int(hit.group(1))
                if year is None and m.get("arxiv"):
                    yy = m["arxiv"].split(".")[0][:2]
                    if yy.isdigit():
                        year = 2000 + int(yy)
                e["year"] = year
                e["venue_name"] = re.sub(r"\s*\b20\d{2}\b\s*", " ", m.get("venue") or "").strip()
                e["added"] = first_seen.get(e["url"], "")
                e["created"] = created_of(e, stars)
                e["has_avatar"] = bool(e["org"]) and (
                    DOCS / ("assets/avatars/%s.png" % e["org"])).exists()
    return sections


def git_first_seen():
    """First commit in which each entry URL appears. Real dates, straight from git."""
    import subprocess
    link = re.compile(r"^- (?:⭐ )?\[[^\]]*\]\(([^)\s]+)\)", re.M)
    log = subprocess.run(["git", "log", "--reverse", "--format=%H %ad", "--date=short",
                          "--", "README.md"], cwd=ROOT, capture_output=True, text=True).stdout
    seen = {}
    for line in log.split("\n"):
        if not line.strip():
            continue
        sha, day = line.split()
        blob = subprocess.run(["git", "show", f"{sha}:README.md"], cwd=ROOT,
                              capture_output=True, text=True).stdout
        for url in link.findall(blob):
            seen.setdefault(url, day)
    return seen


# ---------------------------------------------------------------- components

def card(e, base=""):
    m = e["meta"]
    tags = []
    if e["venue_name"]:
        tags.append('<span class="tag">%s</span>' % esc(e["venue_name"]))
    if e["year"]:
        tags.append('<span class="tag">%d</span>' % e["year"])

    acts = []
    paper = m.get("arxiv") and f"https://arxiv.org/abs/{m['arxiv']}" or (
        m.get("venue_href") or (e["url"] if not e["url"].startswith("https://github.com/") else ""))
    if paper:
        acts.append('<a class="act paper" href="%s" target="_blank" rel="noopener">%sPaper</a>'
                    % (esc(paper), I["paper"]))
    if m.get("repo"):
        acts.append('<a class="act code" href="%s" target="_blank" rel="noopener">%sCode</a>'
                    % (esc(m["repo"]), I["github"]))
    site = m.get("website") or m.get("docs")
    if site:
        acts.append('<a class="act site" href="%s" target="_blank" rel="noopener">%sProject</a>'
                    % (esc(site), I["globe"]))
    if m.get("hf"):
        acts.append('<a class="act data" href="%s" target="_blank" rel="noopener">%sData</a>'
                    % (esc(m["hf"]), I["hf"]))

    hay = " ".join([e["title"], e["subtitle"], e["desc"], e["venue_name"], e["org"]]).lower()
    body = e["subtitle"] or e["desc"]
    return (
        '<article class="card" data-s="{hay}" data-stars="{stars}" '
        'data-year="{year}" data-title="{sort}">'
        '<div class="card-top">{ava}<h3 class="card-title">'
        '<a href="{url}" target="_blank" rel="noopener">{title}</a></h3>'
        '{tags}</div>'
        '{body}'
        '<div class="card-foot"><div class="acts">{acts}</div>{stars_el}</div>'
        "</article>"
    ).format(
        hay=esc(hay),
        stars="" if e["stars"] is None else e["stars"],
        year=e["year"] or "", sort=esc(e["title"].lower()),
        url=esc(e["url"]), title=esc(e["title"]),
        ava=('<img class="ava" src="%sassets/avatars/%s.png" alt="" loading="lazy" '
             'width="26" height="26">' % (base, esc(e["org"]))) if e.get("has_avatar")
        else '<span class="ava ava-none" aria-hidden="true">%s</span>' % esc(e["title"][:1].upper()),
        tags='<div class="tags">%s</div>' % "".join(tags) if tags else "",
        body='<p class="card-desc">%s</p>' % esc(body) if body else "",
        acts="".join(acts),
        stars_el='<span class="stars"><span class="s">&#9733;</span> %s</span>' % human(e["stars"])
        if e["stars"] is not None else "",
    )


def nav(base, current):
    links = '<a href="%s"%s>Home</a>' % (base, ' aria-current="page"' if current == "" else "")
    links += "".join(
        '<a href="%s%s/"%s>%s</a>' % (base, slug, ' aria-current="page"' if slug == current else "", esc(label))
        for slug, label, _, _, _ in CATEGORIES)
    links += '<a href="%sabout/"%s>About</a>' % (base, ' aria-current="page"' if current == "about" else "")
    return f"""<nav class="nav"><div class="nav-in">
<a class="brand" href="{base}">{MARK}Awesome AI Scientist</a>
<div class="nav-links">{links}</div>
<div class="nav-end">
<button class="icon-btn" id="theme" type="button" aria-label="Switch colour theme">{I['moon']}</button>
<a class="icon-btn" href="{REPO}" target="_blank" rel="noopener" aria-label="Repository on GitHub">{I['github']}</a>
</div></div></nav>"""


def foot(base, stats):
    cat_links = "".join(
        '<a href="%s%s/">%s</a>' % (base, slug, esc(label))
        for slug, label, _, _, _ in CATEGORIES)
    return f"""<footer class="foot"><div class="shell">
<div class="foot-row">
<a class="brand" href="{base}">{MARK}Awesome AI Scientist</a>
<nav class="foot-links" aria-label="Footer">{cat_links}
<a href="{base}about/">About</a>
<a href="{REPO}" target="_blank" rel="noopener">GitHub</a></nav>
</div>
<p class="colophon">{stats['entries']} entries &middot; list content CC BY 4.0 &middot;
section icons from <a href="https://github.com/jdecked/twemoji" target="_blank" rel="noopener">Twemoji</a>,
CC BY 4.0 &middot; updated {stats['today']}</p>
</div></footer>"""


def page(base, current, title, desc, path, body, stats, ld=None):
    canonical = SITE + path
    blocks = [{
        "@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "#website",
        "url": SITE, "name": "Awesome AI Scientist", "description": TAGLINE, "inLanguage": "en",
    }]
    if ld:
        blocks.append(ld)
    scripts = "".join('<script type="application/ld+json">%s</script>' % json.dumps(b, ensure_ascii=False)
                      for b in blocks)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Awesome AI Scientist">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}assets/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}assets/og.png">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E1116" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{base}assets/site.css">
{scripts}
</head>
<body>
{nav(base, current)}
{body}
{foot(base, stats)}
<script src="{base}assets/site.js" defer></script>
</body>
</html>
"""


def toolbar(entries, total_label):
    years = sorted({e["year"] for e in entries if e["year"]}, reverse=True)
    opts = "".join('<option value="%d">%d</option>' % (y, y) for y in years)
    return f"""<div class="tools">
<label class="field">{I['search']}<span class="sr">Search this page</span>
<input data-role="q" type="search" autocomplete="off" spellcheck="false" placeholder="Search {esc(total_label)}\u2026">
</label>
<select class="pick-sel" data-role="year" aria-label="Filter by year">
<option value="">All years</option>{opts}</select>
<select class="pick-sel" data-role="sort" aria-label="Sort order">
<option value="default">Sort: Default</option>
<option value="stars">Sort: Most stars</option>
<option value="year">Sort: Newest</option>
<option value="title">Sort: A&ndash;Z</option>
</select>
<span class="result" data-role="count">{len(entries)} entries</span>
</div>"""


def listing(groups, prefix="", base=""):
    """groups: [(slug, label, [entries])]. A single unlabelled group renders bare."""
    out = []
    if len(groups) == 1 and not groups[0][1]:
        out.append('<div class="grid">%s</div>' % "".join(card(e, base) for e in groups[0][2]))
    else:
        for slug, label, ents in groups:
            if not ents:
                continue
            out.append('<section class="group" id="g-%s-%s" data-group>'
                       '<h2>%s <span class="n" data-live="%d">%d</span></h2>'
                       '<div class="grid">%s</div></section>'
                       % (esc(prefix), esc(slug), esc(label), len(ents), len(ents),
                          "".join(card(e, base) for e in ents)))
    out.append('<p class="empty" data-role="empty">Nothing matches those filters.</p>')
    return "".join(out)


# ---------------------------------------------------------------- pages

def build_home(sections, index, stats, teaser):
    blocks = []
    for slug, label, title, intro, subs in CATEGORIES:
        colour, _ = STYLE[slug]
        chips = "".join(
            '<li><a href="{s}/{ss}/">{ico}<span>{lbl}</span><b>{n}</b></a></li>'.format(
                s=slug, ss=ss, lbl=esc(slabel), n=index["sub_counts"][slug][ss],
                ico=icon(f"{slug}/{ss}", 18))
            for ss, slabel, _, _ in subs)
        blocks.append(
            '<section class="mapcat" style="--c:{c}">'
            '<a class="mapcat-head" href="{s}/">{ico}'
            '<span class="mapcat-name">{label}</span>'
            '<span class="mapcat-n">{n}</span>'
            '<span class="mapcat-go" aria-hidden="true">&rarr;</span></a>'
            '<p class="mapcat-note">{intro}</p>'
            '<ul class="mapcat-subs">{chips}</ul>'
            "</section>".format(
                c=colour, s=slug, ico=icon(slug, 30), label=esc(label),
                n=index["counts"][slug], intro=esc(intro), chips=chips))

    body = """<header class="hero"><div class="shell">
<h1>Awesome AI&nbsp;Scientist</h1>
<p class="lede">{tagline}</p>
<div class="cta">
<a class="btn solid" href="ai-scientists/">Browse the collection</a>
<a class="btn" href="{repo}" target="_blank" rel="noopener">{gh}GitHub{ext}</a>
</div>
<ul class="badges">
<li><a class="badge b-paper" href="{repo}#readme" target="_blank" rel="noopener">
<span class="k">{i_paper}Papers</span><span class="v">{papers}</span></a></li>
<li><a class="badge b-code" href="resources/workbenches/">
<span class="k">{i_github}Repositories</span><span class="v">{repos}</span></a></li>
<li><a class="badge b-hf" href="https://huggingface.co/papers" target="_blank" rel="noopener">
<span class="k">{i_hf}Hugging Face</span><span class="v">{hf}</span></a></li>
<li><a class="badge b-bench" href="benchmarks/">
<span class="k">{i_chart}Benchmarks</span><span class="v">{benchmarks}</span></a></li>
<li><a class="badge b-data" href="resources/datasets/">
<span class="k">{i_box}Datasets</span><span class="v">{datasets}</span></a></li>
<li><a class="badge b-star" href="{repo}/stargazers" target="_blank" rel="noopener">
<span class="k">{i_star}Stars</span><span class="v">{starsum}</span></a></li>
</ul>
</div></header>
<div class="shell"><div class="map">{blocks}</div></div>""".format(
        tagline=esc(TAGLINE), repo=REPO, gh=I["github"], ext=EXT,
        entries=stats["entries"], papers=stats["papers"], repos=stats["repos"],
        hf=stats["hf"], benchmarks=stats["benchmarks"], datasets=stats["datasets"],
        i_paper=I["paper"], i_github=I["github"], i_hf=I["hf"],
        i_chart=I["chart"], i_box=I["box"], i_star=I["star"],
        starsum=stats["starsum"], today=stats["today"], blocks="".join(blocks))

    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "@id": SITE + "#page",
          "url": SITE, "name": "Awesome AI Scientist", "description": TAGLINE,
          "isPartOf": {"@id": SITE + "#website"}, "dateModified": stats["today"],
          "mainEntity": {"@type": "ItemList", "numberOfItems": stats["entries"],
                         "itemListElement": [
                             {"@type": "ListItem", "position": i + 1, "name": label,
                              "url": SITE + slug + "/"}
                             for i, (slug, label, _, _, _) in enumerate(CATEGORIES)]}}
    return page("", "", "Awesome AI Scientist: a curated map of AI for scientific discovery",
                f"{TAGLINE} {stats['entries']} papers, systems, benchmarks and datasets, "
                "curated and kept current.", "", body, stats, ld)


def crumbs(items):
    parts = []
    for label, href in items[:-1]:
        parts.append('<a href="%s">%s</a>' % (href, esc(label)))
    parts.append(esc(items[-1][0]))
    return '<p class="crumb">%s</p>' % ' <span>/</span> '.join(parts)


def subtabs(base, cat_slug, subs, counts, active):
    out = ['<a href="%s%s/"%s>All <span class="n">%d</span></a>'
           % (base, cat_slug, ' aria-current="page"' if active is None else "", counts["_all"])]
    for ss, label, _, _ in subs:
        out.append('<a href="%s%s/%s/"%s>%s <span class="n">%d</span></a>'
                   % (base, cat_slug, ss, ' aria-current="page"' if active == ss else "",
                      esc(label), counts[ss]))
    return '<div class="subtabs">%s</div>' % "".join(out)


def build_category(sections, slug, label, title, intro, subs, index, stats):
    base = "../"
    counts = index["sub_counts"][slug]
    groups = [(ss, lbl, index["sub_entries"][slug][ss]) for ss, lbl, _, _ in subs]
    ents = index["cat_entries"][slug]
    body = f"""<div class="shell" style="--c:{STYLE[slug][0]}">
<header class="page-head">
{crumbs([("Home", base), (title, "")])}
<h1>{icon(slug, 38, base)}{esc(title)}</h1>
{subtabs(base, slug, subs, counts, None)}
</header>
{toolbar(ents, title)}
<main>{listing(groups, slug, base)}</main>
</div>"""
    ld = {"@context": "https://schema.org", "@type": "CollectionPage",
          "url": SITE + slug + "/", "name": title, "description": intro,
          "isPartOf": {"@id": SITE + "#website"},
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
              {"@type": "ListItem", "position": 2, "name": title, "item": SITE + slug + "/"}]},
          "mainEntity": {"@type": "ItemList", "numberOfItems": len(ents)}}
    return page(base, slug, f"{title} &middot; Awesome AI Scientist",
                f"{intro} {len(ents)} curated entries with papers, code and project links.",
                slug + "/", body, stats, ld)


def build_sub(slug, cat_title, sub_slug, sub_label, sub_intro, subs, index, stats):
    base = "../../"
    counts = index["sub_counts"][slug]
    ents = index["sub_entries"][slug][sub_slug]
    body = f"""<div class="shell" style="--c:{STYLE[slug][0]}">
<header class="page-head">
{crumbs([("Home", base), (cat_title, base + slug + "/"), (sub_label, "")])}
<h1>{icon(slug, 38, base)}{esc(sub_label)}</h1>
{subtabs(base, slug, subs, counts, sub_slug)}
</header>
{toolbar(ents, sub_label)}
<main>{listing([(sub_slug, "", ents)], "", base)}</main>
</div>"""
    url = f"{slug}/{sub_slug}/"
    ld = {"@context": "https://schema.org", "@type": "CollectionPage",
          "url": SITE + url, "name": sub_label, "description": sub_intro,
          "isPartOf": {"@id": SITE + "#website"},
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
              {"@type": "ListItem", "position": 2, "name": cat_title, "item": SITE + slug + "/"},
              {"@type": "ListItem", "position": 3, "name": sub_label, "item": SITE + url}]},
          "mainEntity": {"@type": "ItemList", "numberOfItems": len(ents)}}
    return page(base, slug, f"{sub_label} &middot; {cat_title} &middot; Awesome AI Scientist",
                f"{sub_intro} {len(ents)} curated entries.", url, body, stats, ld)


def build_about(stats):
    base = "../"
    cite = ("@misc{awesome_ai_scientist,\n"
            "  title        = {Awesome AI Scientist},\n"
            "  year         = {2026},\n"
            "  howpublished = {\\url{%s}},\n"
            "  note         = {A curated list of AI systems, benchmarks, datasets\n"
            "                  and platforms for scientific discovery}\n}" % REPO)
    body = f"""<div class="shell">
<header class="page-head">{crumbs([("Home", base), ("About", "")])}
<h1>About this list</h1>
<p class="lede">What belongs here, how entries are chosen, and how to add one.</p></header>
<div class="prose">
<h2>Scope</h2>
<p>An <strong>AI Scientist</strong> is a system that uses foundation models, tools, code, data and
sometimes laboratory hardware to carry out or support part of the scientific discovery loop:
literature review, hypothesis generation, experiment design, experimentation, analysis and writing.
This list collects the strongest work on building and evaluating such systems.</p>
<p>It is deliberately not a general AI-for-Science catalogue. The centre of gravity is agentic
scientific work: systems that reason over evidence, call tools, write and execute programs,
interact with experiments, and produce artefacts a scientist can inspect and reproduce.</p>
<h2>Contribute</h2>
<p>Additions and corrections are welcome. Read the
<a href="{REPO}/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener">contribution guide</a>,
then <a href="{REPO}/issues/new" target="_blank" rel="noopener">open an issue</a> or send a pull request.</p>
<h2>Cite</h2>
<pre class="cite" id="cite">{esc(cite)}</pre>
<button class="btn" id="copycite" type="button">Copy BibTeX</button>
</div></div>"""
    return page(base, "about", "About &middot; Awesome AI Scientist",
                "What belongs in the Awesome AI Scientist list, how entries are selected, "
                "how the site is generated, and how to contribute.",
                "about/", body, stats)


# ---------------------------------------------------------------- main

def main():
    teaser = "fieldmap"
    for arg in sys.argv[1:]:
        if arg.startswith("--teaser="):
            teaser = {"fig1": "fig1.png", "fieldmap": "fieldmap", "none": ""}[arg.split("=")[1]]

    sections, skipped = parse(ROOT / "README.md")
    stars = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    enrich(sections, stars, git_first_seen())

    index = {"all": [], "counts": {}, "cat_entries": {}, "sub_entries": {}, "sub_counts": {}}
    for slug, label, title, intro, subs in CATEGORIES:
        index["sub_entries"][slug] = {}
        index["sub_counts"][slug] = {}
        cat = []
        for ss, slabel, source, sintro in subs:
            ents = entries_of(find(sections, source))
            if f"{slug}/{ss}" in SORT:
                ents = sorted(ents, key=lambda e: e["created"], reverse=True)
            index["sub_entries"][slug][ss] = ents
            index["sub_counts"][slug][ss] = len(ents)
            cat += ents
        index["cat_entries"][slug] = cat
        index["counts"][slug] = len(cat)
        index["sub_counts"][slug]["_all"] = len(cat)
        index["all"] += cat

    total = sum(len(s["entries"]) + sum(len(x["entries"]) for x in s["subs"]) for s in sections)
    assert len(index["all"]) == total, f"taxonomy covers {len(index['all'])} of {total} entries"

    repos = {e["meta"]["stars_src"] for e in index["all"] if e["meta"].get("stars_src")}
    stats = {
        "entries": total,
        "papers": sum(1 for e in index["all"] if e["meta"].get("arxiv") or e["meta"].get("venue")),
        "repos": len(repos),
        "starsum": human(sum(stars.get(r, {}).get("stars") or 0 for r in repos)),
        "hf": sum(1 for e in index["all"] if e["meta"].get("hf")),
        "benchmarks": index["counts"]["benchmarks"],
        "datasets": index["sub_counts"]["resources"]["datasets"],
        "today": date.today().isoformat(),
    }

    if teaser.endswith(".png"):
        shutil.copy(ROOT / "assets/fig1.png", DOCS / "assets/fig1.png")

    if DOCS.exists():
        for child in DOCS.iterdir():
            if child.name != "assets":
                shutil.rmtree(child) if child.is_dir() else child.unlink()
    DOCS.mkdir(exist_ok=True)

    urls = [""]
    (DOCS / "index.html").write_text(build_home(sections, index, stats, teaser), encoding="utf-8")
    for slug, label, title, intro, subs in CATEGORIES:
        d = DOCS / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(
            build_category(sections, slug, label, title, intro, subs, index, stats), encoding="utf-8")
        urls.append(slug + "/")
        for ss, slabel, source, sintro in subs:
            sd = d / ss
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "index.html").write_text(
                build_sub(slug, title, ss, slabel, sintro, subs, index, stats), encoding="utf-8")
            urls.append(f"{slug}/{ss}/")
    (DOCS / "about").mkdir(exist_ok=True)
    (DOCS / "about/index.html").write_text(build_about(stats), encoding="utf-8")
    urls.append("about/")

    (DOCS / ".nojekyll").write_text("")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    (DOCS / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join('  <url><loc>%s%s</loc><lastmod>%s</lastmod>'
                  '<changefreq>weekly</changefreq><priority>%s</priority></url>\n'
                  % (SITE, u, stats["today"], "1.0" if u == "" else ("0.8" if u.count("/") == 1 else "0.6"))
                  for u in urls)
        + "</urlset>\n")
    (DOCS / "404.html").write_text(
        page("", "", "Page not found &middot; Awesome AI Scientist",
             "That page is not part of this list.", "404.html",
             '<div class="shell"><header class="page-head"><h1>Page not found</h1>'
             '<p class="lede">That page is not part of this list.</p>'
             '<div class="cta" style="justify-content:flex-start;margin-top:24px">'
             '<a class="btn solid" href="/Awesome-AI-Scientist/">Back to the homepage</a></div>'
             "</header></div>", stats).replace('name="robots" content="index, follow',
                                               'name="robots" content="noindex'),
        encoding="utf-8")

    pages = len(urls)
    size = sum(f.stat().st_size for f in DOCS.rglob("*.html"))
    print(f"pages    {pages}  (+404)")
    print(f"entries  {total} across {len(CATEGORIES)} categories, {len(urls) - 8} sub-pages")
    print(f"html     {size / 1024:.0f} KB total, {size / 1024 / pages:.0f} KB average")
    print(f"skipped  {len(skipped)} README bullets (contribution criteria)")
    return stats


if __name__ == "__main__":
    main()
