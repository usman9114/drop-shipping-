"""Compose a README banner and GitHub social preview from an AI illustration.

The illustration (docs/assets/hero-art.png) has no text by design. All text is
set here in real type so it is sharp and correct. Output: docs/assets/hero.png
and docs/assets/social-preview.png, both 1280x640.

Example (from the repo root):
  python docs/assets/tools/compose_banner.py --title "Line one|Line two" \
      --tagline "First line|Second line" --footer "Tech · stack" [--side right] [--flip]
"""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
WHITE, MUTED, TEAL = "#F1F5F9", "#94A3B8", "#5EEAD4"


def font(weight, size):
    try:
        return ImageFont.truetype(INTER.format(weight), size)
    except OSError:
        return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", default="docs/assets/hero-art.png")
    ap.add_argument("--out-dir", default="docs/assets")
    ap.add_argument("--title", required=True, help="lines separated by |")
    ap.add_argument("--tagline", required=True, help="lines separated by |")
    ap.add_argument("--footer", default="")
    ap.add_argument("--side", choices=["left", "right"], default="left")
    ap.add_argument(
        "--flip", action="store_true", help="mirror the illustration horizontally"
    )
    a = ap.parse_args()

    img = Image.open(a.art).convert("RGB").resize((W, H), Image.LANCZOS)
    if a.flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    d = ImageDraw.Draw(img)
    x = 64 if a.side == "left" else 836
    y = 150
    for line in a.title.split("|"):
        d.text((x, y), line, font=font("Bold", 54), fill=WHITE)
        y += 66
    y += 18
    for line in a.tagline.split("|"):
        d.text((x, y), line, font=font("Regular", 26), fill=MUTED)
        y += 36
    if a.footer:
        d.text((x, H - 70), a.footer, font=ImageFont.truetype(MONO, 18), fill=TEAL)
    out = Path(a.out_dir)
    for name in ("hero.png", "social-preview.png"):
        img.save(out / name, optimize=True)
        print("wrote", out / name)


if __name__ == "__main__":
    main()
