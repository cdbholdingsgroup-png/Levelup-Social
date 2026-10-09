"""Render a vertical 1080x1920 text slide (JPEG) for TikTok/Instagram.

Usage: python3 make_text_slide.py OUT.jpg "Label" "Main text" ["Footer"]
"""
import sys, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG = (18, 16, 22)
GOLD = (212, 175, 90)
WHITE = (245, 242, 236)
GREY = (170, 165, 160)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def draw_centered(d, lines, font, y, fill, gap=18):
    for line in lines:
        w = d.textlength(line, font=font)
        d.text(((W - w) / 2, y), line, font=font, fill=fill)
        y += font.size + gap
    return y


def main(out, label, text, footer=""):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_label = ImageFont.truetype(BOLD, 44)
    f_main = ImageFont.truetype(BOLD, 72)
    f_foot = ImageFont.truetype(REG, 38)

    lines = textwrap.wrap(text, width=22)
    block_h = len(lines) * (72 + 18)
    y = (H - block_h) / 2 - 60
    draw_centered(d, [label.upper()], f_label, y - 120, GOLD)
    d.line([(W / 2 - 60, y - 50), (W / 2 + 60, y - 50)], fill=GOLD, width=4)
    y = draw_centered(d, lines, f_main, y, WHITE)
    if footer:
        draw_centered(d, textwrap.wrap(footer, width=40), f_foot, H - 260, GREY)
    img.save(out, "JPEG", quality=92)


if __name__ == "__main__":
    main(*sys.argv[1:])
