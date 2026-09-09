#!/usr/bin/env python3
"""Download the Twemoji glyphs the README already uses for its sections.

Real, published artwork (CC-BY 4.0) rather than icons drawn here. The emoji per
category is the one that heading carries in README.md.
"""
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/assets/icons"
BASE = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/svg"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taxonomy import EMOJI  # noqa: E402  single source for the icon assignments


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = sorted(EMOJI.items())
    for i, (key, cp) in enumerate(items, 1):
        dest = OUT / (key.replace("/", "--") + ".svg")
        if not dest.exists():
            req = urllib.request.Request(f"{BASE}/{cp}.svg",
                                         headers={"User-Agent": "awesome-ai-scientist-site-build"})
            with urllib.request.urlopen(req, timeout=25) as r:
                data = r.read()
            assert data.lstrip().startswith(b"<svg"), f"{key}: not an SVG"
            dest.write_bytes(data)
        if i % max(1, len(items) // 10) == 0 or i == len(items):
            print(f"  [{100 * i // len(items):3d}%] {i}/{len(items)}", file=sys.stderr)
    (OUT / "LICENSE.txt").write_text(
        "Icons in this directory are from Twemoji (https://github.com/jdecked/twemoji),\n"
        "copyright Twitter, Inc and other contributors, licensed CC-BY 4.0.\n")
    have = len(list(OUT.glob("*.svg")))
    size = sum(f.stat().st_size for f in OUT.glob("*.svg"))
    print(f"icons={have}/{len(EMOJI)}  {size / 1024:.1f} KB", file=sys.stderr)
    assert have == len(EMOJI), "some icons missing"


if __name__ == "__main__":
    main()
