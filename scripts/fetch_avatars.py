#!/usr/bin/env python3
"""Download each project's GitHub avatar so cards carry a real logo."""
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_readme import parse  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/assets/avatars"
UA = {"User-Agent": "awesome-ai-scientist-site-build"}


def orgs():
    sections, _ = parse(ROOT / "README.md")
    found = set()
    for sec in sections:
        for node in [sec] + sec["subs"]:
            for e in node["entries"]:
                src = e["meta"].get("stars_src")
                if src:
                    found.add(src.split("/")[0])
    return sorted(found)


def grab(login):
    dest = OUT / f"{login}.png"
    if dest.exists() and dest.stat().st_size > 0:
        return login, True
    try:
        req = urllib.request.Request(f"https://github.com/{login}.png?size=80", headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        if not data.startswith(b"\x89PNG") and not data.startswith(b"\xff\xd8"):
            return login, False
        dest.write_bytes(data)
        return login, True
    except Exception:
        return login, False


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = orgs()
    todo = [n for n in names if not (OUT / f"{n}.png").exists()]
    print(f"orgs={len(names)}  to_fetch={len(todo)}", file=sys.stderr)
    done = 0
    missing = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for login, ok in pool.map(grab, todo):
            done += 1
            if not ok:
                missing.append(login)
            if done % max(1, len(todo) // 10) == 0 or done == len(todo):
                pct = 100 * done // max(len(todo), 1)
                print(f"  [{pct:3d}%] {done}/{len(todo)}", file=sys.stderr)
    have = len(list(OUT.glob("*.png")))
    size = sum(f.stat().st_size for f in OUT.glob("*.png"))
    print(f"avatars={have}/{len(names)}  {size / 1024:.0f} KB  missing={len(missing)}", file=sys.stderr)
    for m in missing[:10]:
        print(f"  no avatar: {m}", file=sys.stderr)


if __name__ == "__main__":
    main()
