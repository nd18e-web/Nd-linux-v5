#!/usr/bin/env python3
# ND18E - generuje tapete (1920x1080) oraz grafiki intro (N + poswiata) w wysokiej jakosci.
# Uzycie: nd18e-make-assets.py <plik_tapety.png> <katalog_motywu_plymouth>
# Wymaga: python3-pil
import os
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

# Ksztalt litery N zmierzony z wzorcowej tapety (szerokosc 158, wysokosc 159, grubosc slupka 30)
N_PTS = [(0, 0), (30, 0), (128, 118), (128, 0), (158, 0), (158, 159),
         (128, 159), (30, 41), (30, 159), (0, 159)]


def n_mask(w, h, ss=4):
    m = Image.new("L", (w * ss, h * ss), 0)
    pts = [(x * w * ss / 158.0, y * h * ss / 159.0) for x, y in N_PTS]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def gradient(size, tl, tr, bl, br):
    g = Image.new("RGB", (2, 2))
    g.putdata([tl, tr, bl, br])
    return g.resize(size, Image.BICUBIC)


def wallpaper(path, W=1920, H=1080):
    bg = Image.new("RGB", (W, H))
    bg.paste(gradient((W // 2, H), (30, 30, 30), (26, 26, 26), (20, 20, 20), (16, 16, 16)), (0, 0))
    bg.paste(gradient((W - W // 2, H), (170, 40, 38), (164, 36, 34), (140, 22, 20), (118, 14, 12)), (W // 2, 0))
    nw, nh = 593, 596
    x0, y0 = (W - nw) // 2, (H - nh) // 2
    mask = n_mask(nw, nh)
    sh = Image.new("L", (W, H), 0)
    sh.paste(mask, (x0 + 16, y0 + 20))
    sh = sh.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.55))
    bg.paste((0, 0, 0), (0, 0, W, H), sh)
    bg.paste(gradient((nw, nh), (242, 242, 242), (224, 224, 224), (206, 206, 206), (172, 172, 172)),
             (x0, y0), mask)
    bg.save(path, optimize=True)


def splash(d):
    C, nw, nh = 1100, 380, 383
    m = Image.new("L", (C, C), 0)
    m.paste(n_mask(nw, nh), ((C - nw) // 2, (C - nh) // 2))
    n = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    n.paste(gradient((C, C), (255, 255, 255), (242, 242, 242), (218, 218, 218), (192, 192, 192)), (0, 0), m)
    n.save(os.path.join(d, "n.png"), optimize=True)
    a = ImageChops.add(m.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.9)),
                       m.filter(ImageFilter.GaussianBlur(70)).point(lambda v: int(v * 0.9)))
    g = Image.new("RGBA", (C, C), (255, 45, 60, 0))
    g.putalpha(a)
    g.save(os.path.join(d, "glow.png"), optimize=True)


def logo(d, S=256):
    """Male logo "N" (ciemny zaokraglony kwadrat, czerwona ramka, bialy znak) - dla instalatora."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((6, 6, S - 7, S - 7), radius=52, fill=(10, 10, 10, 255),
                                          outline=(225, 29, 46, 255), width=9)
    nw, nh = 118, 119
    m = Image.new("L", (S, S), 0)
    m.paste(n_mask(nw, nh), ((S - nw) // 2, (S - nh) // 2))
    img.paste(gradient((S, S), (255, 255, 255), (242, 242, 242), (218, 218, 218), (192, 192, 192)), (0, 0), m)
    img.save(os.path.join(d, "logo.png"), optimize=True)


if __name__ == "__main__":
    wp, sd = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(wp) or ".", exist_ok=True)
    os.makedirs(sd, exist_ok=True)
    wallpaper(wp)
    splash(sd)
    logo(sd)
