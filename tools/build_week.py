"""Render every slide in a week file, plus a contact sheet for review.

Usage: python3 tools/build_week.py content/week1.json
Output: posts/<week>/dayN-slideM.jpg and posts/<week>/contact-sheet.jpg
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(path):
    week = json.load(open(path))
    out = os.path.join(ROOT, "posts", week["week"])
    os.makedirs(out, exist_ok=True)
    rows = []
    for p in week["posts"]:
        files = []
        for i, s in enumerate(p["slides"], 1):
            f = os.path.join(out, f"day{p['day']}-slide{i}.jpg")
            slides.render(s, f)
            files.append(f)
        rows.append((p, files))
    # contact sheet: one row per day, thumbnails 216x384
    tw, th, gap = 216, 384, 16
    cols = max(len(f) for _, f in rows)
    sheet = Image.new("RGB", (160 + cols * (tw + gap), len(rows) * (th + gap) + gap), (240, 238, 234))
    d = ImageDraw.Draw(sheet)
    fnt = ImageFont.truetype(slides.FB, 26)
    for r, (p, files) in enumerate(rows):
        y = gap + r * (th + gap)
        d.text((16, y + 150), f"Day {p['day']}\n{p['date'][5:]}", font=fnt, fill=(30, 30, 30))
        for c, f in enumerate(files):
            im = Image.open(f).resize((tw, th))
            sheet.paste(im, (160 + c * (tw + gap), y))
    sheet.save(os.path.join(out, "contact-sheet.jpg"), quality=88)
    print(out, sum(len(f) for _, f in rows), "slides")


if __name__ == "__main__":
    main(sys.argv[1])
