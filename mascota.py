"""Inspector Bigotes: mascota original de Datazo Diario (gato detective).
Genera assets/mascota/<expresion>.png (600x600, fondo transparente) con rsvg-convert.
Uso: python mascota.py
"""
import os, subprocess, math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mascota")
LN = "#232733"          # contorno
FUR = "#9AA8C0"         # pelaje gris azulado
FUR_D = "#6F7C96"       # rayas
MUZ = "#F5F1E8"         # hocico
PINK = "#F08DA0"
HAT = "#8A5A33"; HAT_D = "#5E3B20"; HAT_L = "#B07A48"
COAT = "#D2A86A"; COAT_D = "#A97F45"
SW = 8                  # grosor de línea

def st(fill, w=SW):
    return f'fill="{fill}" stroke="{LN}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'

def star(cx, cy, r, fill="#FFD23F"):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" {st(fill, 6)}/>'

def drop(x, y, s=1.0, fill="#7FD3FF"):
    return (f'<path d="M{x} {y} q{14*s} {22*s} {14*s} {32*s} a{14*s} {14*s} 0 0 1 {-28*s} 0 '
            f'q0 {-10*s} {14*s} {-32*s}z" {st(fill, 5)}/>')

def paw(x, y, r=40):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" {st(FUR)}/>'
            f'<path d="M{x-14} {y-r+6} v14 M{x+14} {y-r+6} v14" stroke="{LN}" stroke-width="5" stroke-linecap="round"/>')

def lupa(cx, cy, r=62, hx=None, hy=None):
    hx = cx + r * 1.5 if hx is None else hx; hy = cy + r * 1.5 if hy is None else hy
    a = math.atan2(hy - cy, hx - cx)
    sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
    return (f'<line x1="{sx:.0f}" y1="{sy:.0f}" x2="{hx}" y2="{hy}" stroke="{LN}" stroke-width="30" stroke-linecap="round"/>'
            f'<line x1="{sx:.0f}" y1="{sy:.0f}" x2="{hx}" y2="{hy}" stroke="{HAT_D}" stroke-width="16" stroke-linecap="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#BFE6FF" fill-opacity="0.35" stroke="{LN}" stroke-width="22"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#E2B13C" stroke-width="10"/>'
            f'<path d="M{cx-r*0.55:.0f} {cy-r*0.2:.0f} a{r*0.6:.0f} {r*0.6:.0f} 0 0 1 {r*0.45:.0f} {-r*0.4:.0f}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity="0.9"/>')

# ---------- piezas de la cara ----------
EL, ER, EY = 238, 362, 318

def eye(cx, cy, rx=40, ry=46, px=0, py=0, pr=21, shine=True):
    s = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" {st("#fff", 7)}/>'
    s += f'<circle cx="{cx+px}" cy="{cy+py}" r="{pr}" fill="{LN}"/>'
    if shine:
        s += f'<circle cx="{cx+px-pr*0.35:.0f}" cy="{cy+py-pr*0.4:.0f}" r="{max(4,pr*0.36):.0f}" fill="#fff"/>'
    return s

def lid(cx, cy, rx=40, ry=46, cut=0.0):
    """párpado: tapa la parte superior del ojo hasta 'cut' (fracción desde arriba)."""
    y = cy - ry + 2 * ry * cut
    return (f'<clipPath id="c{cx}{cy}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>'
            f'<rect x="{cx-rx-2}" y="{cy-ry-2}" width="{2*rx+4}" height="{y-(cy-ry)+2:.0f}" fill="{FUR}" clip-path="url(#c{cx}{cy})"/>'
            f'<line x1="{cx-rx+4}" y1="{y:.0f}" x2="{cx+rx-4}" y2="{y:.0f}" stroke="{LN}" stroke-width="8" stroke-linecap="round"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{LN}" stroke-width="7"/>')

def brow(x1, y1, x2, y2, w=11, curve=0):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - curve
    return f'<path d="M{x1} {y1} Q{mx} {my} {x2} {y2}" fill="none" stroke="{LN}" stroke-width="{w}" stroke-linecap="round"/>'

def happy_eye(cx, cy):   # ^
    return f'<path d="M{cx-30} {cy+12} Q{cx} {cy-34} {cx+30} {cy+12}" fill="none" stroke="{LN}" stroke-width="12" stroke-linecap="round"/>'

def closed_eye(cx, cy):  # ︶
    return f'<path d="M{cx-30} {cy-4} Q{cx} {cy+28} {cx+30} {cy-4}" fill="none" stroke="{LN}" stroke-width="10" stroke-linecap="round"/>'

def squeeze_eye(cx, cy, left=True):  # > <
    s = 1 if left else -1
    return f'<path d="M{cx-26*s} {cy-26} L{cx+22*s} {cy} L{cx-26*s} {cy+26}" fill="none" stroke="{LN}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'

MOUTH_CAT = f'<path d="M300 384 Q300 404 280 404 Q266 403 263 392 M300 384 Q300 404 320 404 Q334 403 337 392" fill="none" stroke="{LN}" stroke-width="7" stroke-linecap="round"/>'

def open_mouth(d, tongue=True):
    s = f'<path d="{d}" {st("#6B1F2E", 7)}/>'
    if tongue:
        s += f'<clipPath id="m{abs(hash(d))%9999}"><path d="{d}"/></clipPath>'
        s += f'<ellipse cx="300" cy="468" rx="40" ry="26" fill="{PINK}" clip-path="url(#m{abs(hash(d))%9999})"/>'
    return s

# ---------- cuerpo base ----------
def base(face, back="", front="", ears="normal", hat_dy=0, hat_rot=0, tint=""):
    if ears == "down":
        earL = f'<path d="M150 270 L82 190 L215 205 Z" {st(FUR)}/><path d="M150 255 L110 208 L190 214 Z" fill="{PINK}"/>'
        earR = f'<path d="M450 270 L518 190 L385 205 Z" {st(FUR)}/><path d="M450 255 L490 208 L410 214 Z" fill="{PINK}"/>'
    else:
        earL = f'<path d="M140 262 L112 112 L232 190 Z" {st(FUR)}/><path d="M150 236 L134 148 L204 196 Z" fill="{PINK}"/>'
        earR = f'<path d="M460 262 L488 112 L368 190 Z" {st(FUR)}/><path d="M450 236 L466 148 L396 196 Z" fill="{PINK}"/>'
    coat = (f'<path d="M95 610 Q110 500 205 462 L395 462 Q490 500 505 610 Z" {st(COAT)}/>'
            f'<path d="M250 466 L300 560 L350 466 Z" {st("#FFFFFF", 6)}/>'
            f'<path d="M286 500 L314 500 L322 560 L300 585 L278 560 Z" {st("#D9534F", 6)}/>'
            f'<path d="M205 462 L250 466 L292 590 L215 540 Z" {st(COAT_D, 7)}/>'
            f'<path d="M395 462 L350 466 L308 590 L385 540 Z" {st(COAT_D, 7)}/>')
    cheeks = (f'<path d="M140 350 L102 372 L138 386 L108 408 L160 410 Z" {st(FUR)}/>'
              f'<path d="M460 350 L498 372 L462 386 L492 408 L440 410 Z" {st(FUR)}/>')
    head = f'<ellipse cx="300" cy="335" rx="172" ry="148" {st(FUR)}/>'
    stripes = (f'<path d="M300 232 v34 M262 236 l8 28 M338 236 l-8 28" stroke="{FUR_D}" stroke-width="12" stroke-linecap="round"/>'
               f'<path d="M134 320 h30 M136 345 h26 M466 320 h-30 M464 345 h-26" stroke="{FUR_D}" stroke-width="10" stroke-linecap="round"/>')
    muzzle = (f'<ellipse cx="268" cy="394" rx="46" ry="36" fill="{MUZ}"/><ellipse cx="332" cy="394" rx="46" ry="36" fill="{MUZ}"/>'
              f'<ellipse cx="300" cy="418" rx="40" ry="28" fill="{MUZ}"/>')
    nose = f'<path d="M284 366 L316 366 L300 384 Z" {st(PINK, 6)}/>'
    wh = "".join(f'<path d="M{x1} {y1} Q{(x1+x2)/2} {(y1+y2)/2-6} {x2} {y2}" fill="none" stroke="{LN}" stroke-width="4.5" stroke-linecap="round"/>'
                 for x1, y1, x2, y2 in [(222, 396, 116, 380), (222, 408, 112, 410), (226, 420, 122, 440),
                                        (378, 396, 484, 380), (378, 408, 488, 410), (374, 420, 478, 440)])
    plaid = "".join(f'<line x1="{x}" y1="60" x2="{x}" y2="240" stroke="{HAT_D}" stroke-width="5" opacity=".55"/>' for x in range(190, 420, 34))
    plaid += "".join(f'<line x1="160" y1="{y}" x2="440" y2="{y}" stroke="{HAT_L}" stroke-width="5" opacity=".6"/>' for y in range(110, 240, 30))
    hat = (f'<g transform="translate(0 {hat_dy}) rotate({hat_rot} 300 200)">'
           f'<clipPath id="hc"><path d="M170 222 Q168 92 300 84 Q432 92 430 222 Z"/></clipPath>'
           f'<path d="M300 236 Q190 236 140 214 Q180 252 300 256 Q420 252 460 214 Q410 236 300 236 Z" {st(HAT_D)}/>'
           f'<path d="M170 222 Q168 92 300 84 Q432 92 430 222 Z" {st(HAT)}/>'
           f'<g clip-path="url(#hc)">{plaid}</g>'
           f'<path d="M170 222 Q168 92 300 84 Q432 92 430 222 Z" fill="none" stroke="{LN}" stroke-width="{SW}"/>'
           f'<path d="M168 218 Q300 246 432 218" fill="none" stroke="{LN}" stroke-width="{SW}"/>'
           f'<ellipse cx="270" cy="82" rx="26" ry="14" transform="rotate(-20 270 82)" {st(HAT_L, 6)}/>'
           f'<ellipse cx="330" cy="82" rx="26" ry="14" transform="rotate(20 330 82)" {st(HAT_L, 6)}/>'
           f'<circle cx="300" cy="84" r="11" {st(HAT_D, 6)}/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">'
            f'{back}{coat}{earL}{earR}{cheeks}{head}{stripes}{tint}{muzzle}{nose}{wh}{face}{hat}{front}</svg>')

def txt(s, x, y, size, fill="#FFD23F", rot=0):
    return (f'<text x="{x}" y="{y}" font-family="Poppins" font-weight="700" font-size="{size}" fill="{fill}" '
            f'stroke="{LN}" stroke-width="8" paint-order="stroke" text-anchor="middle" transform="rotate({rot} {x} {y})">{s}</text>')

# ---------- expresiones ----------
def build():
    E = {}
    BIGO = open_mouth("M262 400 Q300 392 338 400 Q348 470 300 486 Q252 470 262 400 Z", tongue=False)
    E["shock"] = base(
        eye(EL, EY, 48, 56, 0, 0, 10) + eye(ER, EY, 48, 56, 0, 0, 10)
        + brow(196, 236, 270, 230, curve=18) + brow(330, 230, 404, 236, curve=18)
        + open_mouth("M280 404 Q300 396 320 404 Q330 450 300 458 Q270 450 280 404 Z", tongue=False),
        front=drop(470, 250, 1.1) + drop(118, 270, 0.8) + paw(150, 470) + paw(450, 470), hat_dy=-44)
    E["grito"] = base(
        squeeze_eye(EL, EY, True) + squeeze_eye(ER, EY, False)
        + open_mouth("M240 396 Q300 388 360 396 Q362 500 300 512 Q238 500 240 396 Z"),
        back=''.join(f'<line x1="{300+250*math.cos(a):.0f}" y1="{330+250*math.sin(a):.0f}" x2="{300+290*math.cos(a):.0f}" y2="{330+290*math.sin(a):.0f}" stroke="#FFD23F" stroke-width="12" stroke-linecap="round"/>' for a in [-2.6, -2.1, -1.05, -0.55, 0.0, 3.14]),
        front=paw(130, 420) + paw(470, 420), hat_dy=-30, hat_rot=-6)
    E["duda"] = base(
        eye(EL, EY, 40, 46, 10, 4, 21) + eye(ER, EY + 6, 34, 36, 8, 4, 18)
        + brow(200, 262, 272, 258, curve=0) + brow(326, 250, 402, 238, curve=26)
        + f'<path d="M270 404 q10 -10 20 0 t20 0 t20 0" fill="none" stroke="{LN}" stroke-width="7" stroke-linecap="round"/>',
        front=txt("?", 505, 205, 150, rot=12) + txt("?", 92, 175, 90, "#5CE1E6", -14) + paw(420, 520))
    E["sospecha"] = base(
        eye(EL, EY, 40, 42, 16, 8, 20) + lid(EL, EY, 40, 42, 0.5) + eye(ER, EY, 52, 58, 18, 8, 28) + lid(ER, EY, 52, 58, 0.38)
        + brow(200, 266, 276, 280, curve=-4) + brow(318, 262, 410, 250, curve=10)
        + f'<path d="M276 406 Q302 414 330 398" fill="none" stroke="{LN}" stroke-width="7" stroke-linecap="round"/>',
        front=lupa(ER, EY, 76, 470, 540) + paw(470, 540, 42))
    E["serio"] = base(
        eye(EL, EY, 40, 28, 0, 2, 17) + eye(ER, EY, 40, 28, 0, 2, 17)
        + brow(198, 278, 276, 286, w=13) + brow(324, 286, 402, 278, w=13)
        + f'<line x1="276" y1="408" x2="324" y2="408" stroke="{LN}" stroke-width="8" stroke-linecap="round"/>',
        front=f'<path d="M180 535 Q300 575 420 535 L420 585 Q300 620 180 585 Z" {st(COAT)}/>' + paw(205, 548, 38) + paw(395, 548, 38))
    E["risa"] = base(
        happy_eye(EL, EY + 6) + happy_eye(ER, EY + 6)
        + open_mouth("M236 394 Q300 384 364 394 Q356 482 300 488 Q244 482 236 394 Z")
        + drop(180, 300, 0.7) + drop(420, 300, 0.7),
        front=txt("JA", 500, 170, 70, rot=14) + txt("JA", 100, 150, 56, "#FF6FB5", -12) + paw(160, 500) + paw(440, 500), hat_rot=8)
    E["feliz"] = base(
        eye(EL, EY, 44, 50, 0, 2, 28) + eye(ER, EY, 44, 50, 0, 2, 28)
        + f'<circle cx="{EL+12}" cy="{EY+14}" r="6" fill="#fff"/><circle cx="{ER+12}" cy="{EY+14}" r="6" fill="#fff"/>'
        + f'<ellipse cx="196" cy="384" rx="30" ry="16" fill="{PINK}" opacity=".7"/><ellipse cx="404" cy="384" rx="30" ry="16" fill="{PINK}" opacity=".7"/>'
        + open_mouth("M276 398 Q300 392 324 398 Q324 436 300 440 Q276 436 276 398 Z"),
        front=star(505, 160, 34) + star(95, 200, 24, "#5CE1E6") + star(470, 70, 18, "#FF6FB5") + paw(475, 400)
              + f'<path d="M520 340 q22 -10 30 6 M530 300 q24 -6 28 12" fill="none" stroke="#FFD23F" stroke-width="9" stroke-linecap="round"/>')
    E["enojo"] = base(
        eye(EL, EY + 4, 40, 34, 4, 4, 14) + eye(ER, EY + 4, 40, 34, -4, 4, 14)
        + brow(196, 258, 280, 294, w=15) + brow(320, 294, 404, 258, w=15)
        + f'<rect x="258" y="398" width="84" height="38" rx="10" {st("#fff", 7)}/>'
        + ''.join(f'<line x1="{x}" y1="400" x2="{x}" y2="434" stroke="{LN}" stroke-width="5"/>' for x in (279, 300, 321))
        + f'<line x1="260" y1="417" x2="340" y2="417" stroke="{LN}" stroke-width="5"/>',
        tint='<ellipse cx="300" cy="280" rx="150" ry="90" fill="#FF3B3B" opacity=".28"/>',
        front=f'<g transform="translate(470 250)" stroke="#E5383B" stroke-width="13" stroke-linecap="round" fill="none">'
              f'<path d="M-30 -10 q14 0 18 -18 M30 -10 q-14 0 -18 -18 M-30 10 q14 0 18 18 M30 10 q-14 0 -18 18"/></g>'
              + f'<path d="M95 150 q-20 -30 10 -50 q10 -30 40 -14" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" opacity=".85"/>'
              + paw(160, 520) + paw(440, 520), hat_dy=-14)
    E["triste"] = base(
        eye(EL, EY, 42, 48, 0, 6, 27) + eye(ER, EY, 42, 48, 0, 6, 27)
        + f'<circle cx="{EL+10}" cy="{EY+18}" r="6" fill="#fff"/><circle cx="{ER+10}" cy="{EY+18}" r="6" fill="#fff"/>'
        + brow(200, 264, 268, 246, curve=-6) + brow(332, 246, 400, 264, curve=-6)
        + f'<path d="M272 418 Q300 396 328 418" fill="none" stroke="{LN}" stroke-width="8" stroke-linecap="round"/>'
        + f'<path d="M214 360 q-8 40 4 90" fill="none" stroke="#7FD3FF" stroke-width="16" stroke-linecap="round" opacity=".9"/>'
        + f'<path d="M386 360 q8 40 -4 90" fill="none" stroke="#7FD3FF" stroke-width="16" stroke-linecap="round" opacity=".9"/>',
        ears="down", hat_dy=10, hat_rot=-4)
    E["dormido"] = base(
        closed_eye(EL, EY + 6) + closed_eye(ER, EY + 6)
        + f'<ellipse cx="300" cy="418" rx="14" ry="12" {st("#6B1F2E", 6)}/>'
        + f'<circle cx="340" cy="392" r="26" fill="#BFE6FF" fill-opacity=".6" stroke="#7FB8E6" stroke-width="5"/>',
        front=txt("Z", 470, 200, 80, "#5CE1E6", 10) + txt("z", 520, 140, 60, "#5CE1E6", 14) + txt("z", 552, 96, 44, "#5CE1E6", 18),
        hat_dy=18, hat_rot=-12)
    E["eureka"] = base(
        star(EL, EY, 48) + star(ER, EY, 48)
        + open_mouth("M248 396 Q300 388 352 396 Q346 470 300 476 Q254 470 248 396 Z"),
        back=(f'<g transform="translate(500 120)">'
              + ''.join(f'<line x1="{58*math.cos(a):.0f}" y1="{58*math.sin(a):.0f}" x2="{82*math.cos(a):.0f}" y2="{82*math.sin(a):.0f}" stroke="#FFD23F" stroke-width="10" stroke-linecap="round"/>' for a in [-2.5, -1.57, -0.6, 0.3, 3.4])
              + f'<circle r="44" {st("#FFE66D")}/><rect x="-20" y="38" width="40" height="30" rx="6" {st("#C9CED8", 6)}/>'
              + f'<path d="M-12 8 q12 -24 24 0" fill="none" stroke="#E2B13C" stroke-width="6"/></g>'),
        front=paw(450, 330) + f'<path d="M450 290 v-48" stroke="{LN}" stroke-width="30" stroke-linecap="round"/><path d="M450 290 v-48" stroke="{FUR}" stroke-width="16" stroke-linecap="round"/>',
        hat_dy=-20)
    E["pensando"] = base(
        eye(EL, EY, 40, 46, -10, -16, 20) + eye(ER, EY, 40, 46, -10, -16, 20)
        + brow(200, 256, 272, 258) + brow(330, 248, 402, 240, curve=16)
        + f'<path d="M286 408 Q304 404 320 412" fill="none" stroke="{LN}" stroke-width="7" stroke-linecap="round"/>',
        back=(f'<circle cx="95" cy="235" r="14" {st("#fff", 5)}/><circle cx="72" cy="185" r="22" {st("#fff", 5)}/>'
              f'<ellipse cx="110" cy="105" rx="80" ry="56" {st("#fff", 6)}/>'
              + ''.join(f'<circle cx="{x}" cy="105" r="10" fill="{LN}"/>' for x in (80, 110, 140))),
        front=paw(330, 470) + lupa(470, 470, 50, 470, 590))
    return E

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, svg in build().items():
        sp = os.path.join(OUT, name + ".svg")
        open(sp, "w").write(svg)
        subprocess.run(["rsvg-convert", "-w", "600", "-h", "600", sp, "-o", os.path.join(OUT, name + ".png")], check=True)
        os.remove(sp)
    print("mascota ok:", ", ".join(sorted(build())))
