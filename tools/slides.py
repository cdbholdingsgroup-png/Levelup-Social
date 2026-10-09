"""Level Up slide renderer: vertical 1080x1920 JPEGs for TikTok / Instagram / Facebook.

Slide types (dicts):
  {"type": "hook", "label": "...", "text": "..."}
  {"type": "side", "who": "her"|"him", "text": "..."}
  {"type": "thread", "messages": [["her"|"him", "text"], ...]}
  {"type": "question", "text": "..."}
  {"type": "cta", "book": "king"|"queen"|"bundle", "line": "...", "sub": "..."}
"""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
FB = os.path.join(A, "fonts", "Poppins-Bold.ttf")
FS = os.path.join(A, "fonts", "Poppins-SemiBold.ttf")
FR = os.path.join(A, "fonts", "Poppins-Regular.ttf")
FP = os.path.join(A, "fonts", "PlayfairDisplay-Bold.ttf")

W, H = 1080, 1920
BG = (16, 14, 20)
GOLD = (214, 176, 92)
WHITE = (246, 242, 234)
GREY = (160, 154, 148)
HER = (226, 132, 150)
HIM = (110, 160, 226)
HANDLE = "Level Up · C.D. Barros"


def font(path, size):
    f = ImageFont.truetype(path, size)
    if path == FP:
        try:
            f.set_variation_by_axes([700])
        except Exception:
            pass
    return f


def wrap_px(d, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(d, text, path, max_w, max_h, start=88, minimum=46, spacing=1.25):
    size = start
    while size >= minimum:
        f = font(path, size)
        lines = wrap_px(d, text, f, max_w)
        h = len(lines) * size * spacing
        if h <= max_h:
            return f, lines, h
        size -= 4
    f = font(path, minimum)
    lines = wrap_px(d, text, f, max_w)
    return f, lines, len(lines) * minimum * spacing


def center_block(d, lines, f, y, fill, spacing=1.25):
    for line in lines:
        w = d.textlength(line, font=f)
        d.text(((W - w) / 2, y), line, font=f, fill=fill)
        y += f.size * spacing
    return y


def base():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # soft gold glow top
    glow = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-300, -700, W + 300, 500), fill=(48, 38, 24))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.blend(img, glow, 0.9)
    d = ImageDraw.Draw(img)
    f = font(FS, 30)
    w = d.textlength(HANDLE, font=f)
    d.text(((W - w) / 2, H - 120), HANDLE, font=f, fill=GREY)
    return img, d


def label(d, text, y, color=GOLD):
    f = font(FB, 40)
    t = text.upper()
    w = d.textlength(t, font=f)
    d.text(((W - w) / 2, y), t, font=f, fill=color)
    d.line([(W / 2 - 60, y + 72), (W / 2 + 60, y + 72)], fill=color, width=4)


def photo_base(path):
    """Full-bleed photo, cover-cropped to 9:16, darkened toward the bottom for text."""
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
    x = (im.width - W) // 2
    im = im.crop((x, 0, x + W, H))
    shade = Image.new("L", (W, H))
    sd = ImageDraw.Draw(shade)
    for y in range(H):  # 35% at top -> 88% at bottom
        sd.line([(0, y), (W, y)], fill=int(255 * (0.35 + 0.53 * (y / H))))
    im = Image.composite(Image.new("RGB", (W, H), (10, 8, 12)), im, shade)
    d = ImageDraw.Draw(im)
    f = font(FS, 30)
    w = d.textlength(HANDLE, font=f)
    d.text(((W - w) / 2, H - 120), HANDLE, font=f, fill=GREY)
    return im, d


def slide_hook(s):
    if s.get("photo"):
        img, d = photo_base(s["photo"])
        f, lines, h = fit_text(d, s["text"], FB, W - 140, 760, start=80)
        y = H - 300 - h  # text sits in lower half over the dark part
    else:
        img, d = base()
        f, lines, h = fit_text(d, s["text"], FB, W - 160, 1000, start=84)
        y = (H - h) / 2
    if s.get("label"):
        label(d, s["label"], y - 150)
    center_block(d, lines, f, y, WHITE)
    return img


def slide_quote(s):
    """A real line from the book, with its source."""
    img, d = base()
    f, lines, h = fit_text(d, "“" + s["text"] + "”", FP, W - 170, 1000, start=84)
    y = (H - h) / 2
    label(d, s.get("label", "From the book"), y - 150)
    y = center_block(d, lines, f, y, WHITE)
    center_block(d, [s["source"]], font(FS, 38), y + 50, GOLD)
    return img


def slide_side(s):
    img, d = base()
    color = HER if s["who"] == "her" else HIM
    f, lines, h = fit_text(d, "“" + s["text"] + "”", FP, W - 180, 900, start=92)
    y = (H - h) / 2
    label(d, s.get("label") or ("Her" if s["who"] == "her" else "Him"), y - 150, color)
    center_block(d, lines, f, y, WHITE)
    return img


def slide_question(s):
    img, d = base()
    f, lines, h = fit_text(d, s["text"], FB, W - 160, 900, start=80)
    y = (H - h) / 2 - 80
    if s.get("label"):
        label(d, s["label"], y - 150)
    y = center_block(d, lines, f, y, WHITE)
    if s.get("prompt"):
        center_block(d, [s["prompt"]], font(FS, 42), y + 70, GOLD)
    return img


def slide_thread(s):
    img, d = base()
    f = font(FR, 40)
    pad, maxw = 34, 700
    y = 340
    hdr = font(FS, 36)
    center_block(d, [s.get("title", "Him")], hdr, 220, GREY)
    for who, text in s["messages"]:
        lines = wrap_px(d, text, f, maxw - 2 * pad)
        bw = max(d.textlength(l, font=f) for l in lines) + 2 * pad
        bh = len(lines) * 54 + 2 * pad - 10
        if who == "her":  # sender (right, coloured)
            x0, fill, col = W - 70 - bw, (52, 120, 246), WHITE
        else:
            x0, fill, col = 70, (58, 56, 64), WHITE
        d.rounded_rectangle((x0, y, x0 + bw, y + bh), radius=36, fill=fill)
        ty = y + pad - 6
        for l in lines:
            d.text((x0 + pad, ty), l, font=f, fill=col)
            ty += 54
        y += bh + 28
    if s.get("footer"):
        center_block(d, [s["footer"]], font(FS, 34), y + 30, GREY)
    return img


def _cover(name, height):
    c = Image.open(os.path.join(A, f"{name}_cover.jpg")).convert("RGB")
    r = height / c.height
    return c.resize((int(c.width * r), height))


def slide_cta(s):
    img, d = base()
    book = s["book"]
    if book == "bundle":
        k, q = _cover("king", 700), _cover("queen", 700)
        total = k.width + q.width + 40
        x = (W - total) // 2
        img.paste(k, (x, 330)); img.paste(q, (x + k.width + 40, 330))
        top = 330 + 700
    else:
        c = _cover(book, 860)
        img.paste(c, ((W - c.width) // 2, 300))
        top = 300 + 860
    d = ImageDraw.Draw(img)
    f, lines, h = fit_text(d, s["line"], FP, W - 160, 300, start=66, minimum=44)
    y = center_block(d, lines, f, top + 70, WHITE)
    center_block(d, [s.get("sub", "Link in bio")], font(FB, 44), y + 40, GOLD)
    return img


RENDER = {"hook": slide_hook, "quote": slide_quote, "side": slide_side, "question": slide_question,
          "thread": slide_thread, "cta": slide_cta}


def render(s, out):
    RENDER[s["type"]](s).save(out, "JPEG", quality=90)
