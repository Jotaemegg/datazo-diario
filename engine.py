"""Motor de videos de Datazo Diario (9:16). Uso: python engine.py spec.json salida.mp4 [--preview t1,t2,...]"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
OUT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(OUT, "assets")
FONT_B = os.path.join(ASSETS, "fonts", "Poppins-Bold.ttf")
FONT_M = os.path.join(ASSETS, "fonts", "Poppins-Medium.ttf")
FONT_EMOJI = os.path.join(ASSETS, "fonts", "NotoColorEmoji.ttf")

WHITE = (255, 255, 255)
YEL = (255, 210, 63)
PINK = (255, 77, 141)
CYAN = (61, 220, 255)
GRAY = (140, 150, 175)

TOTAL = 30.0  # se fija desde el spec
TAG = "DATO CURIOSO"

# ---------- utilidades ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out_back(p, s=1.7):
    p -= 1; return p * p * ((s + 1) * p + s) + 1
def ease_out(p): return 1 - (1 - p) ** 3
def ease_io(p): return 3 * p * p - 2 * p * p * p
def ease_out5(p): return 1 - (1 - clamp(p)) ** 5          # ~bezier(0.23,1,0.32,1): entradas
def ease_in3(p): p = clamp(p); return p * p * p             # salidas
def snappy(p): return 0.9 + 0.1 * ease_out_back(clamp(p), 1.25)  # spring con un solo rebote mínimo

_font_cache = {}
def font(size, bold=True):
    k = (size, bold)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(FONT_B if bold else FONT_M, size)
    return _font_cache[k]

_sprite_cache = {}
def text_sprite(txt, size, color, bold=True, shadow=True):
    if txt != TAG and txt != '?': size = int(size * 0.8)
    k = (txt, size, color, bold)
    if k in _sprite_cache: return _sprite_cache[k]
    f = font(size, bold)
    l, t, r, b = f.getbbox(txt)
    pad = 30
    w, h = r - l + pad * 2, b - t + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 6, pad - t + 8), txt, font=f, fill=(0, 0, 0, 170))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text((pad - l, pad - t), txt, font=f, fill=color + (255,))
    _sprite_cache[k] = im
    return im

def paste_center(frame, sprite, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.01: return
    s = sprite
    if abs(scale - 1) > 0.005:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BILINEAR)
    if rot: s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = s.getchannel("A").point(lambda v: int(v * alpha))
        s = s.copy(); s.putalpha(a)
    frame.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

DARK = (20, 16, 42)
def words_block(frame, lines, t, cy, gap=10):
    """lines: [[(texto, size, color, t0[, estilo]), ...], ...]
    estilo: pop (defecto) | slam (cae grande, para la palabra clave) | box (tarjeta de color detrás).
    Palabras de size >= 130 usan slam automáticamente."""
    heights = []
    for line in lines:
        heights.append(max(text_sprite(w[0], w[1], w[2]).height for w in line) - 40)
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = cy - total_h / 2
    for line, lh in zip(lines, heights):
        sprites = [text_sprite(w[0], w[1], w[2]) for w in line]
        space = 22
        extra = [40 if len(w) > 4 and w[4] == "box" else 0 for w in line]
        lw = sum(sp.width - 60 + ex for sp, ex in zip(sprites, extra)) + space * (len(sprites) - 1)
        x = W / 2 - lw / 2
        for w, sp, ex in zip(line, sprites, extra):
            txt, s, c, t0 = w[:4]
            x += ex / 2
            style = w[4] if len(w) > 4 else ("slam" if s >= 130 else "pop")
            ww = sp.width - 60; cx = x + ww / 2; cyw = y + lh / 2
            p = (t - t0)
            if p > 0:
                if style == "slam":
                    q = clamp(p / 0.26)
                    sc = 1 + 0.75 * (1 - ease_out5(q))
                    paste_center(frame, sp, cx, cyw, sc, clamp(q * 3))
                elif style == "box":
                    q = clamp(p / 0.24); bw = ww + 36
                    d = ImageDraw.Draw(frame); bh = sp.height - 50
                    x0 = cx - bw / 2
                    d.rounded_rectangle((x0, cyw - bh / 2, x0 + max(24, bw * ease_out5(q)), cyw + bh / 2), 18, fill=c + (255,))
                    if p > 0.1:
                        q2 = clamp((p - 0.1) / 0.3)
                        paste_center(frame, text_sprite(txt, s, DARK, shadow=False), cx, cyw + 22 * (1 - ease_out5(q2)), snappy(q2), clamp(q2 * 3))
                else:
                    q = clamp(p / 0.42)
                    paste_center(frame, sp, cx, cyw + 36 * (1 - ease_out5(q)), snappy(q), clamp(q * 2.5))
            x += ww + space + ex / 2
        y += lh + gap

# ---------- fondo ----------
def make_bg():
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]
    top = np.array([18, 16, 48]); bot = np.array([42, 12, 70])
    g = top * (1 - yy[..., None]) + bot * yy[..., None]
    d = np.sqrt((xx - 0.5) ** 2 + ((yy - 0.42) * 1.2) ** 2)
    g = g * (1 - 0.55 * clamp_np(d * 1.3))[..., None]
    g = np.broadcast_to(g, (H, W, 3))
    return Image.fromarray(g.astype(np.uint8)).convert("RGBA")
def clamp_np(a): return np.clip(a, 0, 1)
BG = make_bg()

random.seed(7)
PARTS = [(random.uniform(0, W), random.uniform(0, H), random.uniform(2, 6),
          random.uniform(20, 60), random.choice([YEL, PINK, CYAN])) for _ in range(45)]

def base_frame(gt):
    fr = BG.copy()
    d = ImageDraw.Draw(fr)
    for x, y, r, sp, c in PARTS:
        yy = (y - gt * sp) % H
        a = int(70 + 50 * math.sin(gt * 2 + x))
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=c + (a,))
    return fr

def overlay(frame, gt):
    d = ImageDraw.Draw(frame)
    # barra de progreso (retención)
    d.rounded_rectangle((60, 70, W - 60, 82), 6, fill=(255, 255, 255, 50))
    d.rounded_rectangle((60, 70, 60 + (W - 120) * clamp(gt / TOTAL), 82), 6, fill=YEL + (255,))
    # etiqueta
    tag = text_sprite(TAG, 34, YEL, shadow=False)
    paste_center(frame, tag, W / 2, 140)

# ---------- sprites dibujados ----------
def glow(im, radius=25, strength=1.0):
    g = im.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        g.putalpha(g.getchannel("A").point(lambda v: min(255, int(v * strength))))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, g); out = Image.alpha_composite(out, im)
    return out

def make_brain():
    S = 620; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    blobs = [(210, 230, 120), (310, 190, 130), (410, 235, 115), (180, 330, 105),
             (300, 320, 140), (430, 330, 100), (360, 400, 90)]
    for x, y, r in blobs: d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 120, 170, 255))
    # cerebelo (atrás, abajo) resaltado en cian
    d.ellipse((380, 380, 520, 480), fill=CYAN + (255,))
    for i in range(3): d.arc((395, 395 + i * 18, 505, 465 + i * 18), 200, 340, fill=(20, 90, 120, 255), width=6)
    # surcos
    lines = [((160, 200, 280, 320), 200, 330), ((260, 150, 380, 270), 190, 320),
             ((340, 210, 470, 340), 210, 340), ((180, 290, 300, 410), 10, 150),
             ((270, 270, 400, 390), 20, 170), ((150, 240, 250, 340), 90, 230)]
    for box, a0, a1 in lines: d.arc(box, a0, a1, fill=(190, 40, 100, 255), width=9)
    d.line((300, 150, 300, 440), fill=(190, 40, 100, 255), width=7)
    return glow(im, 30, 0.9)
BRAIN = make_brain()

def make_feather():
    S = 360; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for i in range(41):
        a = i / 40 * math.pi
        pts.append((180 + 70 * math.sin(a) * (1 - 0.3 * i / 40), 40 + 260 * i / 40))
    for i in range(40, -1, -1):
        a = i / 40 * math.pi
        pts.append((180 - 70 * math.sin(a) * (1 - 0.3 * i / 40), 40 + 260 * i / 40))
    d.polygon(pts, fill=(255, 255, 255, 235))
    for i in range(1, 12):
        y = 50 + i * 21
        d.line((180, y + 14, 120, y - 4), fill=(200, 205, 230, 255), width=3)
        d.line((180, y + 14, 240, y - 4), fill=(200, 205, 230, 255), width=3)
    d.line((180, 30, 180, 340), fill=(170, 175, 205, 255), width=6)
    return glow(im, 14, 0.5)
FEATHER = make_feather()

def make_robot():
    S = 420; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line((210, 40, 210, 100), fill=CYAN + (255,), width=10)
    d.ellipse((190, 20, 230, 60), fill=YEL + (255,))
    d.rounded_rectangle((70, 100, 350, 330), 60, fill=(40, 50, 95, 255), outline=CYAN + (255,), width=12)
    d.rounded_rectangle((110, 150, 310, 260), 40, fill=(15, 20, 45, 255))
    d.ellipse((140, 175, 195, 230), fill=CYAN + (255,)); d.ellipse((225, 175, 280, 230), fill=CYAN + (255,))
    d.rounded_rectangle((165, 280, 255, 300), 10, fill=CYAN + (255,))
    return glow(im, 20, 0.8)
ROBOT = make_robot()

def meter(frame, cx, cy, w, h, val, color, label, alpha=1.0):
    if alpha <= 0: return
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), h / 2, fill=(255, 255, 255, 35), outline=(255, 255, 255, 90), width=4)
    if val > 0.02:
        d.rounded_rectangle((x0 + 8, y0 + 8, x0 + 8 + (w - 16) * val, y0 + h - 8), (h - 16) / 2, fill=color + (255,))
    if alpha < 1: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(layer)
    paste_center(frame, text_sprite(label, 40, WHITE, bold=False), cx, y0 - 45, 1, alpha)

def shake(frame, amt, t):
    if amt <= 0.5: return frame
    dx = int(amt * math.sin(t * 90)); dy = int(amt * math.cos(t * 77))
    a = np.array(frame); a = np.roll(a, (dy, dx), axis=(0, 1))
    return Image.fromarray(a).convert('RGBA')

def burst(frame, cx, cy, p, color):
    if p <= 0 or p >= 1: return
    d = ImageDraw.Draw(frame)
    for i in range(14):
        a = i / 14 * 2 * math.pi
        r0 = 180 + 380 * ease_out(p); r1 = r0 + 120 * (1 - p)
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
               fill=color + (int(255 * (1 - p)),), width=14)

def fade_out(t, dur, frame, last=0.18):
    """Aplica fundido corto a negro-azulado dentro de la escena (corte limpio)."""
    p = clamp((t - (dur - last)) / last)
    if p > 0:
        frame = Image.blend(frame, BG, p * 0.85)
    return frame

# ---------- extras v4: figuras animadas y memes ----------

def meme_card(path, size=520, crop=None):
    im = Image.open(path).convert("RGB")
    if crop: im = im.crop(crop)
    s = min(im.size); l = (im.width - s) // 2; tp = (im.height - s) // 2
    im = im.crop((l, tp, l + s, tp + s)).resize((size, size), Image.LANCZOS)
    b = 14; R = 40; S = size + 2 * b
    card = Image.new("RGBA", (S + 60, S + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((38, 44, 38 + S, 44 + S), R, fill=(0, 0, 0, 160))
    card = Image.alpha_composite(card, sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(card).rounded_rectangle((30, 30, 30 + S, 30 + S), R, fill=(255, 255, 255, 255))
    mask = Image.new("L", (size, size), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), R - 10, fill=255)
    card.paste(im, (30 + b, 30 + b), mask)
    return card


def meme_pop(fr, card, cx, cy, t, t0, t1=99, rot=-5):
    if t < t0 or t > t1 + 0.25: return
    p = clamp((t - t0) / 0.28)
    out = clamp((t - t1) / 0.25)
    sc = (1.35 - 0.35 * ease_out(p)) * (1 - out)  # "zoom punch"
    jitter = 6 * math.sin((t - t0) * 40) * (1 - clamp((t - t0) / 0.3))
    paste_center(fr, card, cx + jitter, cy, sc, clamp(p * 3) * (1 - out), rot + 2 * math.sin(t * 3))

def qmarks(fr, t, a=1.0, cy=1000):
    for i in range(6):
        ang = t * 0.8 + i * 1.05
        x = W / 2 + 400 * math.cos(ang) * (0.8 + 0.2 * math.sin(i))
        y = cy + 260 * math.sin(ang * 1.3 + i)
        sz = [70, 90, 60, 110, 80, 65][i]
        col = [YEL, CYAN, PINK, YEL, CYAN, PINK][i]
        paste_center(fr, text_sprite("?", sz, col), x, y, 1 + 0.15 * math.sin(t * 4 + i), a * 0.85, 20 * math.sin(t * 2 + i))

def face(fr, cx, cy, r, mood, t, a=1.0):
    if a <= 0: return
    layer = Image.new("RGBA", (int(r * 3), int(r * 3)), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    c = r * 1.5
    d.ellipse((c - r, c - r, c + r, c + r), fill=(255, 205, 60, 255), outline=(230, 150, 20, 255), width=6)
    if mood == "laugh":
        for sx in (-1, 1):
            d.arc((c + sx * r * 0.42 - r * 0.2, c - r * 0.35, c + sx * r * 0.42 + r * 0.2, c - r * 0.05), 200, 340, fill=(60, 30, 10, 255), width=8)
        op = 0.35 + 0.1 * math.sin(t * 25)
        d.chord((c - r * 0.55, c - r * 0.05, c + r * 0.55, c + r * (0.4 + op)), 0, 180, fill=(90, 20, 30, 255))
        d.chord((c - r * 0.35, c + r * 0.25, c + r * 0.35, c + r * (0.4 + op)), 0, 180, fill=(255, 100, 120, 255))
        for sx in (-1, 1):  # lágrimas de risa
            ty = c - r * 0.05 + (t * 200 % (r * 0.6))
            d.ellipse((c + sx * r * 0.8 - 12, ty - 16, c + sx * r * 0.8 + 12, ty + 16), fill=(90, 190, 255, 230))
    else:  # neutral / sorprendido
        for sx in (-1, 1):
            d.ellipse((c + sx * r * 0.38 - r * 0.12, c - r * 0.35, c + sx * r * 0.38 + r * 0.12, c - r * 0.05), fill=(60, 30, 10, 255))
        d.ellipse((c - r * 0.15, c + r * 0.2, c + r * 0.15, c + r * 0.5), fill=(90, 20, 30, 255))
    sh = 8 * math.sin(t * 30) if mood == "laugh" else 0
    paste_center(fr, layer, cx + sh, cy, 1, a, 6 * math.sin(t * 6))

def rings(fr, cx, cy, t, color, a=1.0):
    d = ImageDraw.Draw(fr)
    for k in range(3):
        ph = (t * 0.9 + k / 3) % 1
        rr = 40 + 160 * ph
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=color + (int(200 * (1 - ph) * a),), width=5)

def speaker(fr, cx, cy, level, a=1.0):
    if a <= 0: return
    d = ImageDraw.Draw(fr); A = int(255 * a)
    d.rectangle((cx - 50, cy - 22, cx - 22, cy + 22), fill=WHITE + (A,))
    d.polygon([(cx - 22, cy - 22), (cx + 10, cy - 50), (cx + 10, cy + 50), (cx - 22, cy + 22)], fill=WHITE + (A,))
    for k in range(3):
        if level > k / 3 + 0.05:
            rr = 35 + k * 25
            d.arc((cx + 10 - rr, cy - rr, cx + 10 + rr, cy + rr), -45, 45, fill=YEL + (A,), width=7)
    if level < 0.3:
        d.line((cx + 30, cy - 25, cx + 80, cy + 25), fill=PINK + (A,), width=9)
        d.line((cx + 30, cy + 25, cx + 80, cy - 25), fill=PINK + (A,), width=9)

def clock(fr, cx, cy, t, a=1.0):
    if a <= 0: return
    d = ImageDraw.Draw(fr); A = int(255 * a)
    d.ellipse((cx - 45, cy - 45, cx + 45, cy + 45), outline=CYAN + (A,), width=7)
    ang = t * 6
    d.line((cx, cy, cx + 32 * math.sin(ang), cy - 32 * math.cos(ang)), fill=YEL + (A,), width=7)
    d.line((cx, cy, cx, cy - 22), fill=WHITE + (A,), width=6)

random.seed(11)
CONF = [(random.uniform(0, 2 * math.pi), random.uniform(500, 1100), random.choice([YEL, PINK, CYAN, WHITE]),
         random.uniform(-8, 8), random.uniform(10, 22)) for _ in range(70)]
def confetti(fr, cx, cy, t):
    if t <= 0 or t > 2.5: return
    d = ImageDraw.Draw(fr)
    for ang, sp, col, rs, sz in CONF:
        x = cx + math.cos(ang) * sp * t * 0.6
        y = cy + math.sin(ang) * sp * t * 0.6 + 900 * t * t * 0.5
        a = int(255 * clamp(1 - t / 2.5))
        rr = rs * t
        pts = [(x + sz * math.cos(rr + k * math.pi / 2), y + sz * 0.5 * math.sin(rr + k * math.pi / 2)) for k in range(4)]
        d.polygon(pts, fill=col + (a,))

# =====================================================================
#  INTERPRETE DEL SPEC (JSON) — escenas genéricas para cualquier tema
# =====================================================================
import json
COLORS = {"W": WHITE, "Y": YEL, "P": PINK, "C": CYAN, "G": GRAY}
def col(c): return COLORS.get(c, WHITE) if isinstance(c, str) else tuple(c)

_emoji_font = None
_emoji_cache = {}
def emoji_sprite(ch, size):
    global _emoji_font
    k = (ch, size)
    if k in _emoji_cache: return _emoji_cache[k]
    if _emoji_font is None: _emoji_font = ImageFont.truetype(FONT_EMOJI, 109)
    im = Image.new("RGBA", (200, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=_emoji_font, embedded_color=True)
    bb = im.getbbox() or (0, 0, 1, 1); im = im.crop(bb)
    sc = size / max(im.size); im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    pad = 30; out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    shd = Image.new("RGBA", out.size, (0, 0, 0, 0)); shd.paste((0, 0, 0, 120), (pad + 6, pad + 10), im)
    out = Image.alpha_composite(out, shd.filter(ImageFilter.GaussianBlur(8))); out.alpha_composite(im, (pad, pad))
    _emoji_cache[k] = out
    return out

_meme_cache = {}
def meme(tag, size):
    k = (tag, size)
    if k not in _meme_cache:
        p = tag if os.path.exists(tag) else os.path.join(ASSETS, "memes", tag + ".jpg")
        _meme_cache[k] = meme_card(p, size)
    return _meme_cache[k]

_masc_cache = {}
def mascota(tag, size, flip=False):
    k = (tag, size, flip)
    if k not in _masc_cache:
        im = Image.open(os.path.join(ASSETS, "mascota", tag + ".png")).convert("RGBA").resize((size, size), Image.LANCZOS)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        pad = 30; out = Image.new("RGBA", (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
        shd = Image.new("RGBA", out.size, (0, 0, 0, 0)); shd.paste((0, 0, 0, 130), (pad + 8, pad + 14), im)
        out = Image.alpha_composite(out, shd.filter(ImageFilter.GaussianBlur(12))); out.alpha_composite(im, (pad, pad))
        _masc_cache[k] = out
    return _masc_cache[k]

def life(t, e):
    """alpha de entrada/salida de un elemento con t (inicio) y t_end (fin opcional)."""
    t0 = e.get("t", 0); t1 = e.get("t_end", 1e9)
    if t < t0 or t > t1 + 0.25: return 0, 0
    p = clamp((t - t0) / 0.3); o = 1 - clamp((t - t1) / 0.25)
    return p, o

def draw_el(fr, e, t):
    ty = e["type"]; x = e.get("x", W / 2); y = e.get("y", 960)
    if ty == "words":
        lines = [[(w[0], w[1], col(w[2]), w[3], *w[4:]) for w in ln] for ln in e["lines"]]
        words_block(fr, lines, t, y)
    elif ty == "text":
        p, o = life(t, e)
        if p <= 0: return
        wob = e.get("wobble", 0) * math.sin(t * 14)
        paste_center(fr, text_sprite(e["text"], e.get("size", 100), col(e.get("color", "W"))), x, y,
                     ease_out_back(p, 2.2) * (1 - 0.0 * o), p * o, wob)
    elif ty == "emoji":
        p, o = life(t, e)
        if p <= 0: return
        anim = e.get("anim", "float"); lt = t - e.get("t", 0)
        sc = ease_out_back(p); rot = 0; dx = dy = 0
        if "to" in e:  # desplazamiento
            m = ease_io(clamp(lt / e.get("move", 1.0))); dx = (e["to"][0] - x) * m; dy = (e["to"][1] - y) * m
        if anim == "float": dy += 18 * math.sin(lt * 3); rot = 6 * math.sin(lt * 2)
        elif anim == "spin": rot = -lt * 120
        elif anim == "bounce": dy -= abs(math.sin(lt * 6)) * 50
        elif anim == "shake": dx += 10 * math.sin(lt * 45); rot = 8 * math.sin(lt * 30)
        elif anim == "pulse": sc *= 1 + 0.12 * math.sin(lt * 7)
        elif anim == "wiggle": rot = 25 * math.sin(lt * 9)
        paste_center(fr, emoji_sprite(e["char"], e.get("size", 220)), x + dx, y + dy, sc, p * o, rot)
    elif ty == "mascota":
        p, o = life(t, e)
        if p <= 0: return
        lt = t - e.get("t", 0); anim = e.get("anim", "bob")
        dx = dy = 0; rot = e.get("rot", 0); sc = ease_out_back(p, 2.0)
        if anim == "bob": dy = 12 * math.sin(lt * 4); rot += 3 * math.sin(lt * 2.5)
        elif anim == "shake": dx = 12 * math.sin(lt * 45) * max(0, 1 - lt / 0.8); rot += 4 * math.sin(lt * 30)
        elif anim == "bounce": dy = -abs(math.sin(lt * 7)) * 40
        elif anim == "pulse": sc *= 1 + 0.07 * math.sin(lt * 9)
        paste_center(fr, mascota(e["tag"], e.get("size", 460), e.get("flip", False)), x + dx, y + dy, sc, p * o, rot)
    elif ty == "meme":
        meme_pop(fr, meme(e["tag"], e.get("size", 420)), x, y, t, e.get("t", 0), e.get("t_end", 99), e.get("rot", -4))
    elif ty == "meter":
        a = clamp((t - e.get("t", 0)) / 0.3)
        v = e.get("from", 0) + (e.get("to", 1) - e.get("from", 0)) * ease_io(clamp((t - e.get("t0", 0)) / max(0.01, e.get("t1", 1) - e.get("t0", 0))))
        meter(fr, x, y, e.get("w", 720), e.get("h", 66), v, col(e.get("color", "Y")), e.get("label", ""), a)
    elif ty == "counter":
        if t < e.get("t", 0): return
        p = clamp((t - e.get("t", 0)) / 0.3)
        v = e["from"] + (e["to"] - e["from"]) * ease_out(clamp((t - e.get("t", 0)) / e.get("dur", 1.5)))
        dec = e.get("decimals", 0)
        s = f"{v:,.{dec}f}".replace(",", " ") + e.get("suffix", "")
        paste_center(fr, text_sprite(e.get("prefix", "") + s, e.get("size", 140), col(e.get("color", "Y"))), x, y, ease_out_back(p), p)
    elif ty == "qmarks": qmarks(fr, t, clamp((t - e.get("t", 0)) / 0.4) * (life(t, e)[1] if "t_end" in e else 1), y)
    elif ty == "confetti": confetti(fr, x, y, t - e.get("t", 0))
    elif ty == "burst": burst(fr, x, y, clamp((t - e.get("t", 0)) / 0.6), col(e.get("color", "Y")))
    elif ty == "face":
        p, o = life(t, e); face(fr, x, y, e.get("r", 110), e.get("mood", "neutral"), t, p * o)
    elif ty == "rings":
        p, o = life(t, e)
        if p > 0: rings(fr, x, y, t, col(e.get("color", "C")), p * o)
    elif ty == "clock":
        p, o = life(t, e); clock(fr, x, y, t, p * o)
    elif ty == "brain":
        p, o = life(t, e); paste_center(fr, BRAIN, x, y, ease_out_back(p) * e.get("scale", 0.8) * (1 + 0.03 * math.sin(t * 6)), p * o)
    elif ty == "button":
        q = clamp((t - e.get("t", 0)) / 0.35)
        if q > 0:
            d = ImageDraw.Draw(fr); bw, bh = e.get("w", 520) * ease_out_back(q), 140
            d.rounded_rectangle((x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2), 70, fill=col(e.get("color", "P")) + (255,))
            if q > 0.6: paste_center(fr, text_sprite(e.get("text", "SÍGUENOS"), 72, WHITE), x, y, 1 + 0.03 * math.sin(t * 8), clamp((q - 0.6) / 0.4))

TRANS = ["zoom", "slide", "whip"]
TD = 0.34   # duración de transición entre escenas (s)

def camera(fr, z=1.0, dx=0.0, dy=0.0, blur=0.0, layer=False, alpha=1.0):
    """Mueve la 'cámara' sobre el frame. layer=True devuelve capa transparente (para mezclar dos escenas)."""
    if abs(z - 1) > 0.002 or abs(dx) > 0.5 or abs(dy) > 0.5 or layer:
        w2, h2 = int(W * z), int(H * z)
        sc = fr.resize((w2, h2), Image.BILINEAR) if (w2, h2) != fr.size else fr
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0)) if layer else BG.copy()
        out.paste(sc, (int((W - w2) / 2 + dx), int((H - h2) / 2 + dy)))
        fr = out
    if blur > 0.6: fr = fr.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 0.999:
        fr = fr.copy(); fr.putalpha(fr.getchannel("A").point(lambda v: int(v * alpha)))
    return fr

def cam_state(sc, t):
    """drift lento (la toma nunca está congelada) + punches de zoom sincronizados con sonidos."""
    z = 1 + sc.get("drift", 0.03) * clamp(t / sc["dur"])
    for pt in sc.get("punch", []):
        if t >= pt:
            k = t - pt; z += 0.075 * clamp(k / 0.05) * math.exp(-max(0, k - 0.05) / 0.16)
    return z

_last_cache = {}
def last_content(sc, gt):
    k = id(sc)
    if k not in _last_cache:
        fr = render_content(sc, sc["dur"] - 1 / FPS, gt)
        _last_cache[k] = camera(fr, cam_state(sc, sc["dur"]), layer=True)
    return _last_cache[k]

def render_scene_frame(sc, t, gt):
    fr = render_content(sc, t, gt)
    z = cam_state(sc, t); tin = sc.get("in", "cut"); prev = sc.get("_prev")
    q = clamp(t / TD); e = ease_out5(q); m = math.sin(math.pi * q)   # m: blur máximo a mitad
    if prev is not None and q < 1 and tin in TRANS:
        A = last_content(prev, gt)
        if tin == "slide":
            A = camera(A, 1, 0, -H * 0.9 * e, 12 * m, layer=True)
            B = camera(fr, z, 0, H * 0.9 * (1 - e), 12 * m, layer=True)
        elif tin == "whip":
            A = camera(A, 1, -W * e, 0, 16 * m, layer=True)
            B = camera(fr, z, W * (1 - e), 0, 16 * m, layer=True)
        else:  # zoom: la escena vieja "atraviesa" la cámara y la nueva llega desde lejos
            A = camera(A, 1 + 0.5 * e, 0, 0, 14 * m, layer=True, alpha=1 - e)
            B = camera(fr, z * (0.82 + 0.18 * e), 0, 0, 10 * (1 - e), layer=True, alpha=clamp(q * 2))
        out = BG.copy(); out.alpha_composite(A); out.alpha_composite(B); fr = out
    else:
        fr = camera(fr, z)
        if tin == "flash" and t < 0.3:
            fr = Image.blend(fr, Image.new("RGBA", fr.size, (255, 255, 255, 255)), 0.7 * (1 - ease_out5(t / 0.3)))
    overlay(fr, gt)
    return fr

def render_content(sc, t, gt):
    fr = base_frame(gt)
    for e in sc.get("elements", []):
        if e["type"] != "shake": draw_el(fr, e, t)
    for e in sc.get("elements", []):
        if e["type"] == "shake" and t > e["t"]:
            fr = shake(fr, e.get("amount", 18) * (1 - clamp((t - e["t"]) / 0.5)), t)
    return fr

def prep_scenes(scenes):
    scenes[-1]["last"] = True
    for i, sc in enumerate(scenes):
        sc.setdefault("in", "flash" if i == 0 else TRANS[(i - 1) % len(TRANS)])
    for i, sc in enumerate(scenes):
        sc["_prev"] = scenes[i - 1] if i > 0 else None
    return scenes

def render_video(spec, out_video):
    global TOTAL, TAG
    scenes = prep_scenes(spec["scenes"])
    TOTAL = sum(s["dur"] for s in scenes); TAG = spec.get("tag", TAG)
    files = []; start = 0.0
    work = os.path.join(os.path.dirname(os.path.abspath(out_video)), "_work"); os.makedirs(work, exist_ok=True)
    for i, sc in enumerate(scenes):
        n = int(round(sc["dur"] * FPS)); tmp = os.path.join(work, f"s{i}.tmp.mp4"); fin = os.path.join(work, f"s{i}.mp4")
        pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                               "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        for k in range(n):
            pr.stdin.write(render_scene_frame(sc, k / FPS, start + k / FPS).convert("RGB").tobytes())
        pr.stdin.close()
        if pr.wait() != 0: sys.exit(f"falló escena {i}")
        os.replace(tmp, fin); files.append(fin); start += sc["dur"]
    lst = os.path.join(work, "list.txt")
    with open(lst, "w") as f:
        for p in files: f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out_video], check=True)
    return TOTAL

def mix_audio(spec, video_in, out_path, total):
    import music as M
    work = os.path.join(os.path.dirname(os.path.abspath(out_path)), "_work")
    bounds, s = [], 0.0
    for sc in spec["scenes"][:-1]: s += sc["dur"]; bounds.append(s)
    M.save(os.path.join(work, "music.wav"), M.music(total + 0.5))
    M.save(os.path.join(work, "wh.wav"), M.sfx(total + 0.5, bounds or [999], [999]))
    ins = ["-i", video_in, "-i", spec["voice"], "-i", os.path.join(work, "music.wav"), "-i", os.path.join(work, "wh.wav")]
    fl = ["[1:a]aresample=44100,pan=stereo|c0=c0|c1=c0,highpass=f=70,equalizer=f=130:t=q:w=1:g=2.5,equalizer=f=350:t=q:w=1.2:g=-3,"
          "equalizer=f=3200:t=q:w=1:g=2.5,highshelf=f=9000:g=2,acompressor=threshold=-20dB:ratio=3.5:attack=5:release=90:makeup=4,"
          "aecho=0.85:0.8:35|60:0.08|0.05,asplit=2[vox][sc]",
          f"[2:a]volume={spec.get('music_vol', 0.45)}[mus]", "[mus][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck]",
          "[3:a]volume=0.6[wh]"]
    labels = ["[vox]", "[duck]", "[wh]"]
    for i, fx in enumerate(spec.get("sfx", [])):
        p = fx["name"] if os.path.exists(fx["name"]) else os.path.join(ASSETS, "sfx", fx["name"] + ".mp3")
        ins += ["-i", p]; idx = 4 + i; ms = int(fx["t"] * 1000)
        trim = f",atrim=0:{fx['trim']},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, fx['trim'] - 0.4)}:d=0.4" if "trim" in fx else ""
        fl.append(f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo{trim},volume={fx.get('vol', 0.55)},adelay={ms}|{ms}[f{i}]")
        labels.append(f"[f{i}]")
    fl.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    tmp = out_path[:-4] + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y"] + ins + ["-filter_complex", ";".join(fl), "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out_path)

def preview(spec, times, out_png):
    """times: lista de tiempos GLOBALES; arma una hoja de contacto."""
    global TOTAL, TAG
    scenes = prep_scenes(spec["scenes"]); TOTAL = sum(s["dur"] for s in scenes); TAG = spec.get("tag", TAG)
    ims = []
    for gt in times:
        s = 0.0
        for sc in scenes:
            if gt < s + sc["dur"] or sc is scenes[-1]: break
            s += sc["dur"]
        ims.append(render_scene_frame(sc, gt - s, gt).convert("RGB").resize((360, 640)))
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims): sheet.paste(im, (i * 360, 0))
    sheet.save(out_png)

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    if not os.path.isabs(spec["voice"]): spec["voice"] = os.path.join(base, spec["voice"])
    if "--preview" in sys.argv:
        preview(spec, [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")], sys.argv[2]); sys.exit()
    out = sys.argv[2]; silent = out[:-4] + "_mudo.mp4"
    total = render_video(spec, silent)
    mix_audio(spec, silent, out, total)
    os.remove(silent)
    print("ok", out, round(total, 2), "s")
