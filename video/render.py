"""Montaje del vídeo FactoryMind · Antes y después (61 s con locución ElevenLabs, 1920x1080, 30 fps).

Uso:  python3 render.py            -> extrae fotogramas de clips/, renderiza y codifica out/
      python3 render.py --preview  -> solo genera una hoja de contacto de control
"""
import math
import os
import subprocess
import sys
from multiprocessing import Pool

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

ROOT = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(ROOT, "clips")
WORK = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "out")
W, H, FPS, DUR = 1920, 1080, 30, 61.0

NAVY = (11, 30, 51)
RED = (229, 57, 53)
GREEN = (30, 158, 90)
BLUE = (74, 127, 181)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/opentype/inter"
_fonts = {}


def font(weight, size):
    key = (weight, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(os.path.join(FONT_DIR, f"Inter-{weight}.otf"), size)
    return _fonts[key]


# ---------------------------------------------------------------- utilidades de tiempo

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def prog(t, start, dur):
    return ease((t - start) / dur)


def window(t, start, end, fin=0.35, fout=0.3):
    """Opacidad 0..1 que entra en `start` y sale en `end`."""
    return min(prog(t, start, fin), 1 - ease_io((t - (end - fout)) / fout))


# ---------------------------------------------------------------- clips

# escena -> (archivo, segundo de inicio en el clip, factor de velocidad)
CLIP_SPEC = {
    "E1": ("E1.mp4", 0.0, 0.9),
    "E2": ("E2.mp4", 0.0, 1.0),
    "E3": ("E3.mp4", 0.0, 0.7),
    "E5": ("E5.mp4", 0.0, 0.8),
    "E7": ("E7.mp4", 0.0, 0.69),
}


def extract_frames():
    for name, (fn, _, speed) in CLIP_SPEC.items():
        d = os.path.join(WORK, name)
        if os.path.isdir(d) and os.listdir(d):
            continue
        os.makedirs(d, exist_ok=True)
        vf = f"setpts=PTS/{speed},fps={FPS},scale={W}:{H}:flags=lanczos"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(CLIPS, fn), "-vf", vf,
                        "-q:v", "2", os.path.join(d, "%04d.jpg")], check=True)


_nframes = {}
CUR_K = 1.0


def clip_frame(name, local_t):
    fn, start, _ = CLIP_SPEC[name]
    d = os.path.join(WORK, name)
    if name not in _nframes:
        _nframes[name] = len(os.listdir(d))
    # local_t llega en tiempo de guion; CUR_K lo pasa a tiempo real de la escena reajustada
    idx = int(round((start + local_t * CUR_K) * FPS)) + 1
    idx = max(1, min(_nframes[name], idx))
    return Image.open(os.path.join(d, f"{idx:04d}.jpg")).convert("RGB")


# ---------------------------------------------------------------- dibujo

def layer():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def comp(base, lay, opacity=1.0):
    if opacity <= 0:
        return base
    if opacity < 1:
        a = lay.getchannel("A").point(lambda v: int(v * opacity))
        lay.putalpha(a)
    base.alpha_composite(lay)
    return base


def rgba(c, a=255):
    return (c[0], c[1], c[2], int(a))


def text_w(txt, f):
    return f.getlength(txt)


def badge(base, t, start, end, color, left, right, y=70):
    """Etiqueta superior tipo 'ANTES | LÍNEA DESEQUILIBRADA'."""
    op = window(t, start, end)
    if op <= 0:
        return
    lay, d = layer()
    f = font("ExtraBold", 46)
    x = 90 - int((1 - prog(t, start, 0.45)) * 60)
    pad = 30
    wl, wr = text_w(left, f), text_w(right, f)
    total = pad + 34 + wl + 50 + wr + pad
    d.rounded_rectangle([x, y, x + total, y + 84], radius=10, fill=rgba(color, 240))
    pulse = 0.6 + 0.4 * math.sin(t * 6)
    cx = x + pad + 10
    d.ellipse([cx - 10, y + 32, cx + 10, y + 52], fill=rgba(WHITE, 255 * pulse))
    tx = x + pad + 34
    d.text((tx, y + 42), left, font=f, fill=WHITE, anchor="lm")
    sx = tx + wl + 25
    d.line([sx, y + 22, sx, y + 62], fill=rgba(WHITE, 200), width=3)
    d.text((sx + 25, y + 42), right, font=f, fill=WHITE, anchor="lm")
    comp(base, lay, op)


def caption(base, t, start, end, lines):
    """Rótulo inferior a todo el ancho (sustituye a la locución)."""
    op = window(t, start, end, 0.4, 0.3)
    if op <= 0:
        return
    lay, d = layer()
    h = 70 + 58 * len(lines)
    top = H - h
    for i in range(h):
        a = int(215 * min(1, i / 40))
        d.line([0, top + i, W, top + i], fill=(8, 22, 40, a))
    f = font("SemiBold", 44)
    dy = int((1 - prog(t, start, 0.5)) * 25)
    for i, ln in enumerate(lines):
        d.text((90, top + 50 + i * 58 + dy), ln, font=f, fill=WHITE, anchor="lm")
    d.rectangle([90, top + 14 + dy, 150, top + 19 + dy], fill=rgba(GREEN))
    comp(base, lay, op)


def panel(d, box, title=None, a=215):
    d.rounded_rectangle(box, radius=14, fill=(8, 24, 44, a), outline=(120, 170, 220, 120), width=2)
    if title:
        d.text((box[0] + 26, box[1] + 30), title, font=font("Bold", 26), fill=WHITE, anchor="lm")
        d.line([box[0] + 26, box[1] + 54, box[2] - 26, box[1] + 54], fill=(120, 170, 220, 90), width=1)


def vignette(base, strength=0.55):
    lay, d = layer()
    for i in range(0, 260, 4):
        a = int(strength * 255 * (1 - i / 260) ** 2)
        d.rectangle([i, i, W - i, H - i], outline=(0, 0, 0, a), width=4)
    comp(base, lay)


def darken(base, amount, color=(5, 15, 28)):
    lay = Image.new("RGBA", (W, H), color + (int(255 * amount),))
    base.alpha_composite(lay)


BEFORE = [15, 19, 30, 12, 14]
AFTER = [17, 18, 20, 18, 17]


# ---------------------------------------------------------------- escenas

def scene1(t):  # 0 – 5
    base = clip_frame("E1", t).convert("RGBA")
    vignette(base, 0.45)
    badge(base, t, 0.3, 5.3, RED, "ANTES", "LÍNEA DESEQUILIBRADA")
    caption(base, t, 0.8, 5.2, ["Cinco operarios, una misma línea…",
                                "pero cada puesto trabaja a un ritmo diferente."])
    return base


def scene2(t):  # 5 – 12
    lt = t - 5
    base = clip_frame("E2", lt).convert("RGBA")
    vignette(base, 0.5)
    lay, d = layer()
    # tira de tiempos de ciclo
    x0, y0, cw, ch = 1050, 70, 150, 120
    for i, v in enumerate(BEFORE):
        p = prog(lt, 0.4 + i * 0.22, 0.35)
        if p <= 0:
            continue
        x = x0 + i * (cw + 8)
        yy = y0 + int((1 - p) * 30)
        hot = i == 2 and lt > 1.8
        if hot:
            glow = 0.5 + 0.5 * math.sin(lt * 7)
            fill = rgba(RED, 235)
            d.rounded_rectangle([x - 6, yy - 6, x + cw + 6, yy + ch + 6], radius=14,
                                outline=rgba(RED, 120 + 135 * glow), width=5)
        else:
            fill = (8, 24, 44, 225)
        d.rounded_rectangle([x, yy, x + cw, yy + ch], radius=10, fill=fill)
        a = int(255 * p)
        d.text((x + cw / 2, yy + 36), f"P{i + 1}", font=font("Bold", 30), fill=(255, 255, 255, a), anchor="mm")
        d.text((x + cw / 2, yy + 84), f"{v} s", font=font("ExtraBold", 44), fill=(255, 255, 255, a), anchor="mm")
    comp(base, lay)
    # bloque cuello de botella
    op = window(lt, 2.4, 7.3)
    if op > 0:
        lay, d = layer()
        bx = 1366 + int((1 - prog(lt, 2.4, 0.5)) * 80)
        d.rounded_rectangle([bx, 240, bx + 470, 380], radius=12, fill=rgba(RED, 240))
        d.text((bx + 30, 278), "CUELLO DE BOTELLA", font=font("Bold", 30), fill=WHITE, anchor="lm")
        d.text((bx + 30, 335), "30 s", font=font("ExtraBold", 62), fill=WHITE, anchor="lm")
        comp(base, lay, op)
    op = window(lt, 3.2, 7.3)
    if op > 0:
        lay, d = layer()
        bx = 1366 + int((1 - prog(lt, 3.2, 0.5)) * 80)
        d.rounded_rectangle([bx, 392, bx + 470, 532], radius=12, fill=(8, 24, 44, 235))
        d.text((bx + 30, 430), "CAPACIDAD TEÓRICA", font=font("Bold", 30), fill=WHITE, anchor="lm")
        n = int(round(120 * prog(lt, 3.3, 1.0)))
        d.text((bx + 30, 487), f"{n}", font=font("ExtraBold", 62), fill=WHITE, anchor="lm")
        d.text((bx + 30 + text_w(f"{n}", font("ExtraBold", 62)) + 14, 495), "bandejas/h",
               font=font("SemiBold", 34), fill=WHITE, anchor="lm")
        comp(base, lay, op)
    caption(base, lt, 1.0, 7.2, ["Un cuello de botella de 30 segundos provoca",
                                 "acumulaciones, esperas y pérdidas de productividad."])
    return base


ICON = None


def icon(size):
    global ICON
    if ICON is None:
        ICON = Image.open(os.path.join(ROOT, "assets", "logo-icon-brain.png")).convert("RGBA")
    return ICON.resize((size, size), Image.LANCZOS)


def wordmark(base, cx, cy, scale, op, slide=0.0):
    """Logo FactoryMind: icono cerebro + FACTORY / MIND."""
    if op <= 0:
        return
    lay, d = layer()
    s = scale
    isz = int(170 * s)
    fF, fM = font("Bold", int(62 * s)), font("ExtraBold", int(92 * s))
    tw = max(text_w("FACTORY", fF), text_w("MIND", fM))
    total = isz + int(30 * s) + tw
    x = int(cx - total / 2)
    ic = icon(isz)
    lay.alpha_composite(ic, (x, int(cy - isz / 2)))
    tx = x + isz + int(30 * s) + int(slide * 40 * s)
    d.text((tx, cy - int(8 * s)), "FACTORY", font=fF, fill=WHITE, anchor="ls")
    d.text((tx - int(3 * s), cy + int(78 * s)), "MIND", font=fM, fill=WHITE, anchor="ls")
    comp(base, lay, op)


def scene3(t):  # 12 – 18
    lt = t - 12
    base = clip_frame("E3", lt).convert("RGBA")
    # degradado para legibilidad a la derecha y abajo
    lay, d = layer()
    for x in range(900, W, 4):
        a = int(170 * ((x - 900) / (W - 900)) ** 1.3)
        d.rectangle([x, 0, x + 4, H], fill=(5, 18, 34, a))
    comp(base, lay)
    # transición de escaneo
    if lt < 0.7:
        sx = int(ease_io(lt / 0.7) * W)
        lay, d = layer()
        d.rectangle([sx, 0, W, H], fill=(6, 20, 38, 255))
        for k in range(30):
            d.line([sx - k, 0, sx - k, H], fill=rgba(GREEN, 220 * (1 - k / 30)))
        comp(base, lay)
    # panel carga por puesto
    op = window(t, 12.8, 18.2)
    if op > 0:
        lay, d = layer()
        bx, by = 1230, 90
        panel(d, [bx, by, bx + 600, by + 400], "CARGA POR PUESTO")
        maxh = 240
        for i, v in enumerate(BEFORE):
            p = prog(lt, 1.1 + i * 0.12, 0.6)
            h = int(maxh * v / 30 * p)
            x = bx + 60 + i * 105
            c = RED if i == 2 else BLUE
            d.rectangle([x, by + 340 - h, x + 62, by + 340], fill=rgba(c, 240))
            d.text((x + 31, by + 362), f"P{i + 1}", font=font("Bold", 22), fill=WHITE, anchor="mm")
            if p > 0.6:
                d.text((x + 31, by + 330 - h), f"{v}s", font=font("Bold", 22), fill=WHITE, anchor="mb")
        # línea de takt / referencia
        ty = by + 340 - int(maxh * 20 / 30)
        if lt > 2.0:
            for xx in range(bx + 40, bx + 570, 18):
                d.line([xx, ty, xx + 9, ty], fill=rgba(GREEN, 230), width=3)
            d.text((bx + 572, ty - 6), "20 s", font=font("Bold", 20), fill=rgba(GREEN), anchor="rb")
        comp(base, lay, op)
    op = window(t, 13.6, 18.2)
    if op > 0:
        lay, d = layer()
        bx, by = 1230, 515
        panel(d, [bx, by, bx + 600, by + 200], "ANÁLISIS DE LA LÍNEA")
        for i in range(5):
            cx = bx + 75 + i * 112
            cy = by + 128
            if i < 4:
                d.line([cx + 34, cy, cx + 78, cy], fill=(150, 190, 230, 200), width=3)
            hot = i == 2
            r = 34
            col = RED if hot else (150, 190, 230)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba(col), width=4, fill=(8, 24, 44, 255))
            if hot:
                g = (lt * 1.2) % 1
                rr = r + int(30 * g)
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=rgba(RED, 255 * (1 - g)), width=3)
            d.text((cx, cy), f"P{i + 1}", font=font("Bold", 24), fill=WHITE, anchor="mm")
        comp(base, lay, op)
    # marca y lema
    op = window(t, 13.2, 18.2)
    if op > 0:
        lay, d = layer()
        for y in range(700, H, 4):
            a = int(200 * ((y - 700) / (H - 700)))
            d.rectangle([0, y, W, y + 4], fill=(5, 18, 34, a))
        comp(base, lay, op)
        wordmark(base, 400, 865, 0.62, op, slide=1 - prog(t, 13.2, 0.6))
        lay, d = layer()
        d.text((130, 1010), "ANÁLISIS  ·  CRONOMETRAJE  ·  EQUILIBRADO", font=font("Bold", 30),
               fill=WHITE, anchor="lm")
        comp(base, lay, window(t, 13.9, 18.2))
    return base


_bg4 = None


def scene4(t):  # 18 – 25
    global _bg4
    lt = t - 18
    if _bg4 is None:
        b = clip_frame("E5", 0.2).filter(ImageFilter.GaussianBlur(18))
        b = ImageEnhance.Color(b).enhance(0.4).convert("RGBA")
        darken(b, 0.84, NAVY)
        _bg4 = b
    base = _bg4.copy()
    lay, d = layer()
    d.text((W / 2, 110), "REDISEÑAMOS LA LÍNEA", font=font("ExtraBold", 64), fill=WHITE, anchor="mm")
    d.rectangle([W / 2 - 50, 158, W / 2 + 50, 163], fill=rgba(GREEN))
    comp(base, lay, prog(lt, 0.0, 0.5))

    # barras
    m = ease_io((lt - 1.6) / 2.4)  # 0 = antes, 1 = después
    lay, d = layer()
    gx, gy, bw, gap, maxh = 720, 790, 120, 70, 470
    takt_y = gy - int(maxh * 20 / 30)
    for xx in range(gx - 60, gx + 5 * bw + 4 * gap + 60, 22):
        d.line([xx, takt_y, xx + 11, takt_y], fill=rgba(GREEN, 220 * prog(lt, 0.8, 0.5)), width=3)
    d.text((gx + 5 * bw + 4 * gap + 70, takt_y), "OBJETIVO 20 s", font=font("Bold", 24),
           fill=rgba(GREEN, 255 * prog(lt, 0.8, 0.5)), anchor="lm")
    for i in range(5):
        p_in = prog(lt, 0.3 + i * 0.1, 0.6)
        v = BEFORE[i] + (AFTER[i] - BEFORE[i]) * m
        h = int(maxh * v / 30 * p_in)
        x = gx + i * (bw + gap)
        if i == 2:
            src = RED
        elif i in (3, 4):
            src = (70, 130, 200)
        else:
            src = BLUE
        c = tuple(int(src[k] + (GREEN[k] - src[k]) * m) for k in range(3))
        d.rounded_rectangle([x, gy - h, x + bw, gy], radius=6, fill=rgba(c, 245))
        d.text((x + bw / 2, gy + 34), f"P{i + 1}", font=font("Bold", 32), fill=WHITE, anchor="mm")
        if p_in > 0.5:
            d.text((x + bw / 2, gy - h - 14), f"{int(round(v))} s", font=font("ExtraBold", 38),
                   fill=WHITE, anchor="mb")
    # bloques de tarea que saltan desde P3
    if 1.4 < lt < 4.2:
        moves = [(2, 3, 0.0), (2, 4, 0.35), (2, 0, 0.7), (1, 3, 1.0)]
        for src_i, dst_i, delay in moves:
            q = ease_io((lt - 1.6 - delay) / 0.9)
            if 0 < q < 1:
                sx = gx + src_i * (bw + gap) + bw / 2
                dx = gx + dst_i * (bw + gap) + bw / 2
                sy = gy - maxh * BEFORE[src_i] / 30
                dy = gy - maxh * BEFORE[dst_i] / 30
                x = sx + (dx - sx) * q
                y = sy + (dy - sy) * q - math.sin(q * math.pi) * 140
                d.rounded_rectangle([x - 34, y - 20, x + 34, y + 20], radius=6,
                                    fill=rgba(WHITE, 230), outline=rgba(GREEN), width=3)
    comp(base, lay)

    # textos laterales
    lay, d = layer()
    items = ["Redistribuimos tareas", "Eliminamos esperas", "Nueva secuencia de trabajo", "Sin añadir personal"]
    for k, s in enumerate(items):
        p = prog(lt, 1.8 + k * 0.45, 0.4)
        if p <= 0:
            continue
        y = 330 + k * 80
        x = 90 - int((1 - p) * 40)
        d.ellipse([x, y - 11, x + 22, y + 11], fill=rgba(GREEN, 255 * p))
        d.text((x + 38, y), s, font=font("SemiBold", 32), fill=(255, 255, 255, int(255 * p)), anchor="lm")
    comp(base, lay)

    # sello final
    p = prog(lt, 4.4, 0.5)
    if p > 0:
        lay, d = layer()
        bw2, bh2 = 760, 120
        x = W / 2 - bw2 / 2
        y = 905 + int((1 - p) * 40)
        d.rounded_rectangle([x, y, x + bw2, y + bh2], radius=16, fill=rgba(GREEN, 245))
        cx, cy = x + 70, y + bh2 / 2
        d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], outline=WHITE, width=5)
        d.line([cx - 15, cy, cx - 4, cy + 12, cx + 17, cy - 12], fill=WHITE, width=6, joint="curve")
        d.text((x + 130, y + 40), "EQUILIBRADO OPTIMIZADO", font=font("ExtraBold", 36), fill=WHITE, anchor="lm")
        d.text((x + 130, y + 86), "CICLO:  30 s  →  20 s", font=font("Bold", 34), fill=WHITE, anchor="lm")
        comp(base, lay, p)
    return base


def scene5(t):  # 25 – 34
    lt = t - 25
    base = clip_frame("E5", lt).convert("RGBA")
    vignette(base, 0.45)
    badge(base, lt, 0.3, 9.3, GREEN, "DESPUÉS", "FLUJO EQUILIBRADO")
    caption(base, lt, 1.0, 9.2, ["Ahora cada puesto trabaja al ritmo de la línea.",
                                 "Menos esperas, menos acumulaciones y un flujo mucho más eficiente."])
    return base


def half(name, lt, gray):
    f = clip_frame(name, lt)
    f = f.crop((480, 0, 1440, H))
    if gray:
        f = ImageEnhance.Color(f).enhance(0.25)
        f = ImageEnhance.Brightness(f).enhance(0.85)
    return f.convert("RGBA")


def scene6(t):  # 34 – 42
    lt = t - 34
    base = Image.new("RGBA", (W, H), NAVY + (255,))
    open_p = prog(lt, 0.0, 0.6)
    lh = half("E1", 0.6 + lt * 0.5, True)
    rh = half("E5", lt * 0.9, False)
    off = int((1 - open_p) * 960)
    base.alpha_composite(lh, (-off, 0))
    base.alpha_composite(rh, (960 + off, 0))
    darken(base, 0.35)
    lay, d = layer()
    d.rectangle([956, 0, 964, H], fill=rgba(WHITE, 230 * open_p))
    comp(base, lay)

    rows = [("Operarios", "5", "5"),
            ("Ciclo limitante", "30 s", "20 s"),
            ("Capacidad teórica", "120 bandejas/h", None),
            ("Acumulación intermedia", "Elevada", "Reducida"),
            ("Equilibrado de cargas", "Deficiente", "Mejorado")]
    for side in (0, 1):
        p = prog(lt, 0.5 + side * 0.25, 0.5)
        if p <= 0:
            continue
        lay, d = layer()
        col = RED if side == 0 else GREEN
        x0 = 120 if side == 0 else 1110
        y0 = 120 + int((1 - p) * 40)
        cw = 690
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + 90], radius=12, fill=rgba(col, 245))
        d.text((x0 + cw / 2, y0 + 45), "ANTES" if side == 0 else "DESPUÉS", font=font("ExtraBold", 50),
               fill=WHITE, anchor="mm")
        d.rounded_rectangle([x0, y0 + 100, x0 + cw, y0 + 720], radius=12, fill=(250, 252, 255, 238))
        for k, (lbl, a, b) in enumerate(rows):
            rp = prog(lt, 0.9 + side * 0.25 + k * 0.18, 0.35)
            if rp <= 0:
                continue
            ry = y0 + 150 + k * 118
            val = a if side == 0 else b
            if val is None:
                n = 120 + int(round(60 * prog(lt, 2.0, 1.6)))
                val = f"{n} bandejas/h"
            ia = int(255 * rp)
            # icono de estado
            cx, cy = x0 + 60, ry + 32
            if k >= 3:
                d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=rgba(col, ia))
                if side == 0:
                    d.line([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 255, 255, ia), width=5)
                    d.line([cx - 9, cy + 9, cx + 9, cy - 9], fill=(255, 255, 255, ia), width=5)
                else:
                    d.line([cx - 11, cy, cx - 3, cy + 9, cx + 12, cy - 9], fill=(255, 255, 255, ia), width=5)
            else:
                d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=(11, 30, 51, ia), width=4)
                d.text((cx, cy), str(k + 1), font=font("Bold", 22), fill=(11, 30, 51, ia), anchor="mm")
            d.text((x0 + 105, ry + 10), lbl, font=font("Medium", 26), fill=(90, 100, 115, ia), anchor="lm")
            emph = k in (1, 2)
            d.text((x0 + 105, ry + 52), val, font=font("ExtraBold" if emph else "Bold", 40 if emph else 34),
                   fill=(rgba(col, ia) if emph else (11, 30, 51, ia)), anchor="lm")
            if k < 4:
                d.line([x0 + 30, ry + 96, x0 + cw - 30, ry + 96], fill=(210, 216, 225, ia), width=2)
        comp(base, lay)

    # sello central +50 %
    p = prog(lt, 3.6, 0.6)
    if p > 0:
        lay, d = layer()
        pop = 1 + 0.12 * math.sin(clamp((lt - 3.6) / 0.6) * math.pi)
        r = int(135 * p * pop)
        cx, cy = W // 2, 500
        d.ellipse([cx - r - 12, cy - r - 12, cx + r + 12, cy + r + 12], fill=rgba(WHITE, 240))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(GREEN, 255))
        if p > 0.5:
            d.text((cx, cy - 16), "+50%", font=font("ExtraBold", int(80 * p)), fill=WHITE, anchor="mm")
            d.text((cx, cy + 50), "CAPACIDAD", font=font("Bold", int(28 * p)), fill=WHITE, anchor="mm")
        comp(base, lay)

    # franja inferior
    p = prog(lt, 4.6, 0.5)
    if p > 0:
        lay, d = layer()
        y = 975 + int((1 - p) * 30)
        d.rectangle([0, y - 10, W, H], fill=(8, 22, 40, 235))
        items = ["+50 % CAPACIDAD", "MISMO PERSONAL", "MEJOR ORGANIZACIÓN"]
        f = font("ExtraBold", 38)
        xs = [W * 0.2, W * 0.5, W * 0.8]
        for k, s in enumerate(items):
            d.text((xs[k], y + 45), s, font=f, fill=WHITE if k else rgba((90, 230, 150)), anchor="mm")
            if k:
                d.line([(xs[k - 1] + xs[k]) / 2, y + 20, (xs[k - 1] + xs[k]) / 2, y + 70],
                       fill=rgba(WHITE, 140), width=2)
        comp(base, lay, p)
    return base


def scene7(t):  # 42 – 48
    lt = t - 42
    base = clip_frame("E7", lt).convert("RGBA")
    darken(base, 0.25 + 0.5 * prog(lt, 0.3, 1.2), NAVY)
    vignette(base, 0.6)
    p = prog(lt, 0.7, 0.8)
    wordmark(base, W / 2, 330, 1.0 + 0.08 * (1 - p), p, slide=1 - p)
    lay, d = layer()
    lp = prog(lt, 1.4, 0.6)
    d.line([W / 2 - 330 * lp, 500, W / 2 + 330 * lp, 500], fill=rgba(GREEN), width=4)
    comp(base, lay)
    lay, d = layer()
    f = font("SemiBold", 50)
    d.text((W / 2, 585), "La productividad no consiste en trabajar más rápido,", font=f, fill=WHITE, anchor="mm")
    d.text((W / 2, 655), "sino en trabajar mejor.", font=f, fill=WHITE, anchor="mm")
    comp(base, lay, prog(lt, 1.7, 0.6))
    lay, d = layer()
    d.text((W / 2, 780), "Más productividad. Mismos recursos.", font=font("ExtraBold", 58),
           fill=rgba((90, 230, 150)), anchor="mm")
    comp(base, lay, prog(lt, 2.6, 0.6))
    lay, d = layer()
    d.text((W / 2, 900), "Ingeniería de procesos   ·   Mejora continua   ·   Inteligencia industrial",
           font=font("Medium", 34), fill=(210, 222, 236), anchor="mm")
    comp(base, lay, prog(lt, 3.3, 0.6))
    fade = clamp((lt - 5.5) / 0.5)
    if fade > 0:
        darken(base, fade, (0, 0, 0))
    return base


# Escenas: (inicio y fin en el guion original de 48 s, inicio y fin reales ajustados a la locución)
SCENES = [((0, 5), (0.0, 6.9), scene1), ((5, 12), (6.9, 14.9), scene2), ((12, 18), (14.9, 23.3), scene3),
          ((18, 25), (23.3, 33.3), scene4), ((25, 34), (33.3, 43.1), scene5), ((34, 42), (43.1, 52.3), scene6),
          ((42, 48), (52.3, 61.0), scene7)]
VO_DELAY = 0.3  # la locución empieza 0,3 s después del primer fotograma
XF = 0.3  # fundido cruzado entre escenas


def run_scene(i, t):
    """Evalúa la escena i en el tiempo real t, convirtiéndolo a su tiempo de guion."""
    global CUR_K
    (a, b), (A, B), fn = SCENES[i]
    CUR_K = (B - A) / (b - a)
    return fn(a + (t - A) / CUR_K)


def render_frame(n):
    t = n / FPS
    for i, (_, (A, B), fn) in enumerate(SCENES):
        if A <= t < B or (i == len(SCENES) - 1 and t >= A):
            img = run_scene(i, t)
            # fundido con la escena anterior (excepto la entrada de E3, que tiene escaneo propio)
            if i > 0 and t < A + XF and fn is not scene3:
                prev = run_scene(i - 1, t)
                img = Image.blend(prev, img, ease_io((t - A) / XF))
            if n < 10:
                img = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), img, n / 10)
            return img.convert("RGB")


def worker(n):
    path = os.path.join(WORK, "frames", f"{n:05d}.jpg")
    if not os.path.exists(path):
        render_frame(n).save(path, quality=93)
    return n


def main():
    extract_frames()
    os.makedirs(os.path.join(WORK, "frames"), exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if "--preview" in sys.argv:
        times = [2, 5, 9, 13, 16, 21, 25, 29, 32, 37, 42, 46, 49, 52, 55, 60]
        thumbs = [render_frame(int(s * FPS)).resize((480, 270)) for s in times]
        sheet = Image.new("RGB", (480 * 4, 270 * 4))
        for k, th in enumerate(thumbs):
            sheet.paste(th, ((k % 4) * 480, (k // 4) * 270))
        sheet.save(os.path.join(WORK, "preview.jpg"), quality=85)
        return
    total = int(DUR * FPS)
    with Pool(os.cpu_count()) as pool:
        for k, _ in enumerate(pool.imap_unordered(worker, range(total), chunksize=8)):
            if k % 120 == 0:
                print(f"{k}/{total}", flush=True)
    out = os.path.join(OUT, "factorymind-antes-despues-locucion.mp4")
    vo = os.path.join(ROOT, "audio", "locucion-linea.mp3")
    ms = int(VO_DELAY * 1000)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS),
                    "-i", os.path.join(WORK, "frames", "%05d.jpg"), "-i", vo,
                    "-filter_complex", f"[1:a]adelay={ms}|{ms},apad,loudnorm=I=-16:TP=-1.5:LRA=11[a]",
                    "-map", "0:v", "-map", "[a]", "-t", str(DUR),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
