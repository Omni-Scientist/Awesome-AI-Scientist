#!/usr/bin/env python3
"""Render the 1200x630 social card in the site's own visual language."""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SANS = ROOT / "scripts/.fontcache/geist.woff2"
MONO = ROOT / "scripts/.fontcache/geist-mono.woff2"

BG = (255, 255, 255)
TEXT = (17, 24, 39)
TEXT2 = (102, 112, 133)
TEXT3 = (152, 162, 179)
BORDER = (231, 234, 240)
TEAL = (25, 184, 165)
ORANGE = (245, 158, 66)


def sans(size, weight=400):
    f = ImageFont.truetype(str(SANS), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def mono(size):
    return ImageFont.truetype(str(MONO), size)


def build(stats):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x = 84

    # brand mark: the two overlapping discs from the favicon
    d.rounded_rectangle([x, 74, x + 44, 118], radius=11, fill=TEXT)
    d.ellipse([x + 8, 86, x + 28, 106], fill=TEAL)
    d.ellipse([x + 18, 86, x + 38, 106], fill=ORANGE)
    d.text((x + 58, 84), "AWESOME AI SCIENTIST", font=mono(17), fill=TEXT2)

    d.text((x, 176), "A curated map of", font=sans(62, 600), fill=TEXT)
    d.text((x, 248), "AI systems that do", font=sans(62, 600), fill=TEXT)
    d.text((x, 320), "science.", font=sans(62, 600), fill=TEXT)

    d.text((x, 418), "End-to-end scientists, co-scientists, workbenches,",
           font=sans(24, 400), fill=TEXT2)
    d.text((x, 452), "benchmarks and data. Curated and kept current.",
           font=sans(24, 400), fill=TEXT2)

    # tally rail
    d.line([(x, 506), (W - 84, 506)], fill=BORDER, width=1)
    cells = [(str(stats["entries"]), "entries"), (str(stats["papers"]), "papers"),
             (str(stats["repos"]), "repositories"), (stats["starsum"], "stars tracked")]
    cx = x
    for value, label in cells:
        d.text((cx, 530), value, font=sans(34, 600), fill=TEXT)
        d.text((cx, 576), label.upper(), font=mono(13), fill=TEXT3)
        cx += max(d.textlength(value, font=sans(34, 600)),
                  d.textlength(label.upper(), font=mono(13))) + 64

    url = "omni-scientist.github.io/Awesome-AI-Scientist"
    d.text((W - 84 - d.textlength(url, font=mono(16)), 92), url, font=mono(16), fill=TEXT3)

    out = ROOT / "docs/assets/og.png"
    img.save(out, optimize=True)
    print(f"og.png  {img.size[0]}x{img.size[1]}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    build(json.loads(sys.argv[1]))
