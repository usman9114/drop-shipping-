"""Compose a README banner and GitHub social preview from an AI illustration.

The illustration (docs/assets/hero-art.png) has no text by design. All text is
set here in real type so it is sharp and correct. Output: docs/assets/hero.jpg
and docs/assets/social-preview.jpg, both 1280x640 JPEG (GitHub limits the social preview to 1 MB). Colours and placement are set
per repo because each illustration has its own palette.

Example (from the repo root):
  python docs/assets/tools/compose_banner.py --title "Line one|Line two" \
      --tagline "First line|Second line" --footer "Tech - stack" \
      --fg "#FFFFFF" --muted "#D8C7FF" --accent "#C6FF3D" --title-size 46
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-{}.ttf"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"


def load(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", default="docs/assets/hero-art.png")
    ap.add_argument("--out-dir", default="docs/assets")
    ap.add_argument("--title", required=True, help="lines separated by |")
    ap.add_argument("--tagline", required=True, help="lines separated by |")
    ap.add_argument("--footer", default="")
    ap.add_argument("--fg", default="#F1F5F9")
    ap.add_argument("--muted", default="#94A3B8")
    ap.add_argument("--accent", default="#5EEAD4")
    ap.add_argument("--serif", action="store_true", help="serif title font")
    ap.add_argument("--title-size", type=int, default=54)
    ap.add_argument("--tag-size", type=int, default=24)
    ap.add_argument("--x", type=int, default=64)
    ap.add_argument("--y", type=int, default=140)
    ap.add_argument("--footer-y", type=int, default=H - 70)
    a = ap.parse_args()

    img = Image.open(a.art).convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    tfont = load(
        SERIF.format("Bold") if a.serif else INTER.format("Bold"), a.title_size
    )
    gfont = load(
        SERIF.format("Italic") if a.serif else INTER.format("Regular"), a.tag_size
    )
    y = a.y
    for line in a.title.split("|"):
        d.text((a.x, y), line, font=tfont, fill=a.fg)
        y += int(a.title_size * 1.2)
    y += 14
    for line in a.tagline.split("|"):
        d.text((a.x, y), line, font=gfont, fill=a.muted)
        y += int(a.tag_size * 1.45)
    if a.footer:
        d.text((a.x, a.footer_y), a.footer, font=load(MONO, 17), fill=a.accent)
    out = Path(a.out_dir)
    for name in ("hero.jpg", "social-preview.jpg"):
        img.save(out / name, quality=90, optimize=True, progressive=True)
        print("wrote", out / name)


if __name__ == "__main__":
    main()
