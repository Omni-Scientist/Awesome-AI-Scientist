#!/usr/bin/env python3
"""Parse README.md into a structured list of sections and entries."""
import json
import re
import sys
from pathlib import Path

LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
LINKED_BADGE = re.compile(r"\[!\[([^\]]*)\]\(([^)\s]+)\)\]\(([^)\s]+)\)")
BARE_BADGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
STARS_SHIELD = re.compile(r"img\.shields\.io/github/stars/([^?/]+/[^?/]+)")
ARXIV_SHIELD = re.compile(r"badge/arXiv-([\d.]+)-")
ARXIV_URL = re.compile(r"arxiv\.org/abs/([\d.]+)")


def slugify(text):
    """GitHub-flavoured anchor slug."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\- ]+", "", s, flags=re.UNICODE)
    s = s.replace(" ", "-")
    return s


def strip_emoji(text):
    """Split a leading emoji cluster off a heading."""
    m = re.match(r"^([^\w\s(\[]+)\s+(.*)$", text.strip())
    if m and not m.group(2).startswith("("):
        return m.group(1).strip(), m.group(2).strip()
    return "", text.strip()


def parse_badges(tail):
    """Pull every badge out of the trailing markup; return (badges, leftover)."""
    badges = []
    for m in LINKED_BADGE.finditer(tail):
        badges.append({"alt": m.group(1), "img": m.group(2), "href": m.group(3)})
    leftover = LINKED_BADGE.sub(" ", tail)
    for m in BARE_BADGE.finditer(leftover):
        badges.append({"alt": m.group(1), "img": m.group(2), "href": None})
    leftover = BARE_BADGE.sub(" ", leftover)
    return badges, re.sub(r"\s+", " ", leftover).strip()


def classify(entry, badges):
    """Turn raw badges into typed metadata fields."""
    meta = {"venue": None, "venue_href": None, "arxiv": None, "repo": None, "stars_src": None,
            "hf": None, "website": None, "docs": None, "dataset": False,
            "extra": []}
    for b in badges:
        alt, img, href = b["alt"], b["img"], b["href"]
        sm = STARS_SHIELD.search(img)
        if sm:
            meta["repo"] = href or ("https://github.com/" + sm.group(1))
            meta["stars_src"] = sm.group(1)
            continue
        am = ARXIV_SHIELD.search(img)
        if am:
            meta["arxiv"] = am.group(1)
            continue
        low = alt.lower()
        if "daily" in low or (href and "huggingface.co/papers" in href):
            meta["hf"] = href
            continue
        if low == "website" or low == "project":
            meta["website"] = href
            continue
        if low == "docs":
            meta["docs"] = href
            continue
        if "dataset" in low or low == "data":
            meta["dataset"] = True
            if href:
                meta["extra"].append({"label": "Dataset", "href": href})
            continue
        label = alt.replace("_", " ").strip()
        if label and not meta["venue"]:
            meta["venue"] = label
            meta["venue_href"] = href
        elif label:
            meta["extra"].append({"label": label, "href": href})
    if not meta["arxiv"]:
        um = ARXIV_URL.search(entry.get("url", ""))
        if um:
            meta["arxiv"] = um.group(1)
    if not meta["repo"] and entry.get("url", "").startswith("https://github.com/"):
        meta["repo"] = entry["url"]
        parts = entry["url"].rstrip("/").split("/")
        if len(parts) >= 5:
            meta["stars_src"] = f"{parts[3]}/{parts[4]}"
    return meta


def parse(md_path):
    lines = Path(md_path).read_text(encoding="utf-8").split("\n")
    sections, section, sub = [], None, None
    in_contents = False
    skipped = []

    for lineno, raw in enumerate(lines, 1):
        line = raw.rstrip()

        if line.startswith("## "):
            title = line[3:].strip()
            title = LINK.sub(r"\1", title).strip()
            in_contents = title.lower() == "contents"
            emoji, clean = strip_emoji(title)
            section = {"title": clean, "emoji": emoji, "anchor": slugify(title),
                       "blurb": "", "notes": [], "subs": [], "entries": []}
            sections.append(section)
            sub = None
            continue

        if line.startswith("### ") and section is not None:
            title = line[4:].strip()
            emoji, clean = strip_emoji(title)
            sub = {"title": clean, "emoji": emoji, "anchor": slugify(title),
                   "blurb": "", "notes": [], "entries": []}
            section["subs"].append(sub)
            continue

        if in_contents or section is None:
            continue

        if line.startswith("- "):
            body = line[2:].strip()
            star = body.startswith("⭐")
            if star:
                body = body.lstrip("⭐").strip()
            m = LINK.match(body)
            if not m:
                skipped.append((lineno, line[:100]))
                continue
            entry = {"title": m.group(1).strip(), "url": m.group(2), "star": star}
            tail = body[m.end():].strip()
            badges, leftover = parse_badges(tail)
            desc = leftover.lstrip(",").strip()
            if desc.startswith('"'):
                # A quoted trailer is the paper's own full title, not prose.
                entry["subtitle"] = desc.strip().rstrip(".").strip('"').strip()
                entry["desc"] = ""
            else:
                if desc and not desc.endswith((".", "!", "?")):
                    desc += "."
                entry["desc"] = desc
                entry["subtitle"] = ""
            entry["meta"] = classify(entry, badges)
            (sub or section)["entries"].append(entry)
            continue

        if line and not line.startswith(("#", "---", "|", ">", "```", "<", "  ")):
            target = sub if sub is not None else section
            if target is None:
                continue
            if not target["entries"] and not target["blurb"] and not line.startswith(("**", "!")):
                target["blurb"] = line.strip()
            elif not line.startswith("!["):
                target["notes"].append(line.strip())

    return sections, skipped


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    sections, skipped = parse(src)
    total = sum(len(s["entries"]) + sum(len(x["entries"]) for x in s["subs"]) for s in sections)
    print(f"sections={len(sections)} entries={total} skipped={len(skipped)}", file=sys.stderr)
    for lineno, text in skipped:
        print(f"  skip L{lineno}: {text}", file=sys.stderr)
    json.dump(sections, sys.stdout, ensure_ascii=False, indent=1)
