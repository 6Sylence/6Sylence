#!/usr/bin/env python3
"""Cápsula Relieve — Topografía Real (SRHOOD).

Genera los archivos de impresión de la cápsula: cartas topográficas con
curvas de nivel alrededor de una "cordillera corona" (cinco picos en arco
y una cumbre central). Cada pieza usa una composición distinta para no
repetir el mismo motivo en toda la cápsula.

Salida (en store-assets/out-relieve/):
  rl_tank_front.png        1800x2400  medallón circular, líneas crema (fondo transparente)
  rl_ls_front.png          1800x2400  carta rectangular con marco y ticks (transparente)
  rl_zip_back.png          1800x2400  gran carta con leyenda y rosa de los vientos (transparente)
  rl_slipon_left/right.png 2325x2325  patrón continuo oliva sobre crema
  rl_hightop_quarters.png  2250x2250  patrón continuo oliva sobre crema (denso)
  rl_hightop_tongue.png    2250x2250  variación centrada en la cumbre
  rl_bucket_out.png        2700x3150  exterior crema con contornos oliva
  rl_bucket_in.png         2700x3150  interior oliva con contornos crema (reversible)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out-relieve")
os.makedirs(OUT, exist_ok=True)

CREAM = "#F2EAD8"
GOLD = "#D4AF37"
SAGE = "#A8B78F"
OLIVE = "#3E4A32"
OLIVE_SOFT = "#68774F"
CREAM_BG = "#F4EFE3"

MONO = {"family": "DejaVu Sans Mono"}


def crown_field(seed=7, nx=900, ny=900, extent=3.2, arc_r=1.35, main_h=1.0):
    """Campo escalar: cumbre central + cinco picos en arco (corona) + ruido suave."""
    rng = np.random.default_rng(seed)
    x = np.linspace(-extent, extent, nx)
    y = np.linspace(-extent, extent, ny)
    X, Y = np.meshgrid(x, y)
    Z = main_h * np.exp(-((X + 0.15) ** 2 + (Y - 0.1) ** 2) / 0.55)
    for i, ang in enumerate(np.linspace(-0.15 * np.pi, 1.15 * np.pi, 5)):
        px, py = arc_r * np.cos(ang), arc_r * np.sin(ang) + 0.25
        h = 0.55 + 0.18 * ((i * 37) % 5) / 4.0
        s = 0.16 + 0.05 * ((i * 53) % 3) / 2.0
        Z += h * np.exp(-((X - px) ** 2 + (Y - py) ** 2) / s)
    # colinas menores y ruido de baja frecuencia para contornos orgánicos
    for _ in range(7):
        px, py = rng.uniform(-2.6, 2.6, 2)
        Z += rng.uniform(0.10, 0.28) * np.exp(
            -((X - px) ** 2 + (Y - py) ** 2) / rng.uniform(0.25, 0.9)
        )
    for _ in range(6):
        fx, fy, ph = rng.uniform(0.5, 1.6), rng.uniform(0.5, 1.6), rng.uniform(0, 6.28)
        Z += 0.045 * np.sin(fx * X + ph) * np.cos(fy * Y + ph * 0.7)
    return X, Y, Z


def fig_canvas(w_px, h_px, facecolor="none"):
    fig = plt.figure(figsize=(w_px / 300.0, h_px / 300.0), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_px)
    ax.set_ylim(0, h_px)
    ax.invert_yaxis()
    ax.axis("off")
    if facecolor != "none":
        ax.add_patch(Rectangle((0, 0), w_px, h_px, facecolor=facecolor, zorder=0))
    return fig, ax


def draw_topo(ax, cx, cy, half, field, line_color, minor_color, lw_scale=1.0,
              clip=None, levels=22, label_every=None, label_size=7, label_keep=None):
    """Dibuja contornos del campo mapeados a un cuadrado centrado en (cx, cy)."""
    X, Y, Z = field
    ex = X.max()
    Xp = cx + (X / ex) * half
    Yp = cy + (Y / ex) * half
    lv = np.linspace(Z.min() + 0.12, Z.max() - 0.05, levels)
    minor = ax.contour(Xp, Yp, Z, levels=lv, colors=minor_color,
                       linewidths=0.9 * lw_scale, alpha=0.85, zorder=2)
    index_lv = lv[::5]
    major = ax.contour(Xp, Yp, Z, levels=index_lv, colors=line_color,
                       linewidths=2.2 * lw_scale, alpha=1.0, zorder=3)
    if clip is not None:
        for cs in (minor, major):
            cs.set_clip_path(clip)
    if label_every:
        fmt = {l: f"{int(400 + 900 * (l - Z.min()) / (Z.max() - Z.min()))}" for l in index_lv}
        labels = ax.clabel(major, levels=index_lv[::label_every], fmt=fmt,
                           fontsize=label_size, colors=line_color, inline=True)
        for t in labels:
            t.set_fontfamily("DejaVu Sans Mono")
            if label_keep is not None and not label_keep(*t.get_position()):
                t.remove()
    return Xp, Yp, Z


def summits(ax, pts, color, size=90, text_color=None, labels=None, fontsize=9, clip=None):
    for i, (px, py) in enumerate(pts):
        m = ax.scatter([px], [py], marker="^", s=size, facecolors="none",
                       edgecolors=color, linewidths=1.6, zorder=5)
        if clip is not None:
            m.set_clip_path(clip)
        if labels and text_color:
            t = ax.text(px, py + size * 0.45, labels[i], color=text_color,
                        fontsize=fontsize, ha="center", va="top", zorder=5, **MONO)
            if clip is not None:
                t.set_clip_path(clip)


def crown_mark(ax, cx, cy, w, color, lw=2.0):
    """Corona lineal de tres puntas (marca de la cumbre principal)."""
    h = w * 0.62
    pts = [(cx - w / 2, cy + h / 2), (cx - w / 2, cy - h * 0.1), (cx - w / 4, cy + h * 0.12),
           (cx, cy - h / 2), (cx + w / 4, cy + h * 0.12), (cx + w / 2, cy - h * 0.1),
           (cx + w / 2, cy + h / 2)]
    ax.add_patch(Polygon(pts, closed=True, fill=False, edgecolor=color, linewidth=lw, zorder=6))
    ax.plot([cx - w / 2, cx + w / 2], [cy + h / 2, cy + h / 2], color=color, lw=lw, zorder=6)


def compass(ax, cx, cy, r, color):
    ax.add_patch(Circle((cx, cy), r, fill=False, edgecolor=color, lw=1.4, zorder=5))
    ax.annotate("", xy=(cx, cy - r * 0.72), xytext=(cx, cy + r * 0.72),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4), zorder=6)
    ax.text(cx, cy - r * 1.25, "N", color=color, fontsize=10, ha="center", va="bottom", **MONO)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, transparent=True)
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------- tank (medallón)
def tank_front():
    W, H = 1800, 2400
    fig, ax = fig_canvas(W, H)
    cx, cy, R = W / 2, 1000, 730
    ring = Circle((cx, cy), R, fill=False, edgecolor=CREAM, lw=3.0, zorder=4)
    ax.add_patch(ring)
    ax.add_patch(Circle((cx, cy), R - 26, fill=False, edgecolor=CREAM, lw=1.0, alpha=0.7, zorder=4))
    clip = Circle((cx, cy), R - 34, transform=ax.transData)
    f = crown_field(seed=7)
    draw_topo(ax, cx, cy + 60, R * 1.25, f, CREAM, SAGE, lw_scale=1.0, clip=clip,
              levels=24, label_every=2, label_size=7,
              label_keep=lambda lx, ly: (lx - cx) ** 2 + (ly - cy) ** 2 < (R - 90) ** 2)
    # cumbre principal: corona dorada + picos secundarios
    crown_mark(ax, cx - 55, cy + 20, 92, GOLD, lw=2.4)
    summits(ax, [(cx + 420, cy - 260), (cx - 470, cy - 180), (cx + 250, cy + 430)],
            GOLD, size=70, text_color=CREAM, labels=["1204", "1130", "987"],
            fontsize=7.5, clip=None)
    ax.text(cx, cy + R + 90, "RELIEVE REAL", color=CREAM, fontsize=17,
            ha="center", va="top", weight="bold", **MONO)
    ax.text(cx, cy + R + 168, "CARTA TOPOGRÁFICA · SRHOOD · 41°N 3°W", color=SAGE,
            fontsize=9.5, ha="center", va="top", **MONO)
    save(fig, "rl_tank_front.png")


# ------------------------------------------------------- long sleeve (carta con marco)
def ls_front():
    W, H = 1800, 2400
    fig, ax = fig_canvas(W, H)
    x0, y0, x1, y1 = 210, 330, 1590, 2010
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=CREAM, lw=3.0, zorder=4))
    ax.add_patch(Rectangle((x0 + 22, y0 + 22), x1 - x0 - 44, y1 - y0 - 44, fill=False,
                           edgecolor=CREAM, lw=1.0, alpha=0.7, zorder=4))
    # ticks de coordenadas en el marco
    for t in np.linspace(x0, x1, 7)[1:-1]:
        ax.plot([t, t], [y0, y0 + 16], color=CREAM, lw=1.2, zorder=5)
        ax.plot([t, t], [y1 - 16, y1], color=CREAM, lw=1.2, zorder=5)
    for t in np.linspace(y0, y1, 9)[1:-1]:
        ax.plot([x0, x0 + 16], [t, t], color=CREAM, lw=1.2, zorder=5)
        ax.plot([x1 - 16, x1], [t, t], color=CREAM, lw=1.2, zorder=5)
    clip = Rectangle((x0 + 26, y0 + 26), x1 - x0 - 52, y1 - y0 - 52, transform=ax.transData)
    f = crown_field(seed=23, arc_r=1.5)
    draw_topo(ax, (x0 + x1) / 2 + 40, (y0 + y1) / 2 + 70, (x1 - x0) * 0.78, f,
              CREAM, SAGE, lw_scale=0.95, clip=clip, levels=26, label_every=2, label_size=6.5)
    crown_mark(ax, (x0 + x1) / 2 - 10, (y0 + y1) / 2 + 10, 80, GOLD, lw=2.2)
    summits(ax, [(x0 + 330, y0 + 420), (x1 - 300, y1 - 520)], GOLD, size=62,
            text_color=CREAM, labels=["1055", "918"], fontsize=7)
    compass(ax, x1 - 150, y0 + 150, 62, CREAM)
    ax.text(x0, y1 + 70, "COTA MIL — SERIE RELIEVE", color=CREAM, fontsize=15,
            ha="left", va="top", weight="bold", **MONO)
    ax.text(x0, y1 + 140, "EQUIDISTANCIA 50 M · SRHOOD ©", color=SAGE, fontsize=9,
            ha="left", va="top", **MONO)
    save(fig, "rl_ls_front.png")


# ------------------------------------------------------------- zip hoodie (espalda)
def zip_back():
    W, H = 1800, 2400
    fig, ax = fig_canvas(W, H)
    x0, y0, x1, y1 = 150, 260, 1650, 2060
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=CREAM, lw=3.2, zorder=4))
    clip = Rectangle((x0 + 6, y0 + 6), x1 - x0 - 12, y1 - y0 - 12, transform=ax.transData)
    f = crown_field(seed=41, arc_r=1.3, main_h=1.15)
    draw_topo(ax, (x0 + x1) / 2 - 60, (y0 + y1) / 2 - 40, (x1 - x0) * 0.92, f,
              CREAM, SAGE, lw_scale=1.1, clip=clip, levels=28, label_every=2, label_size=7.5)
    crown_mark(ax, (x0 + x1) / 2 - 130, (y0 + y1) / 2 - 60, 110, GOLD, lw=2.8)
    summits(ax, [(x0 + 400, y0 + 500), (x1 - 380, y0 + 700), (x0 + 560, y1 - 420),
                 (x1 - 480, y1 - 300)], GOLD, size=85, text_color=CREAM,
            labels=["1204", "1130", "987", "842"], fontsize=8, clip=clip)
    compass(ax, x1 - 170, y1 - 180, 78, CREAM)
    # leyenda
    lx, ly = x0 + 40, y1 - 260
    ax.add_patch(Rectangle((lx, ly), 430, 210, fill=False, edgecolor=CREAM, lw=1.6, zorder=6))
    ax.text(lx + 22, ly + 30, "RELIEVE REAL", color=CREAM, fontsize=11, weight="bold",
            va="top", zorder=7, **MONO)
    ax.plot([lx + 22, lx + 122], [ly + 105, ly + 105], color=CREAM, lw=2.2, zorder=7)
    ax.text(lx + 140, ly + 92, "CURVA MAESTRA", color=SAGE, fontsize=7.5, va="top", zorder=7, **MONO)
    ax.plot([lx + 22, lx + 122], [ly + 155, ly + 155], color=SAGE, lw=1.0, zorder=7)
    ax.text(lx + 140, ly + 142, "CURVA DE NIVEL", color=SAGE, fontsize=7.5, va="top", zorder=7, **MONO)
    ax.text((x0 + x1) / 2, y1 + 80, "STREET ROYALTY HOOD — CORDILLERA CORONA",
            color=CREAM, fontsize=13.5, ha="center", va="top", weight="bold", **MONO)
    ax.text((x0 + x1) / 2, y1 + 150, "HOJA 06-26 · ESCALA 1:25 000", color=SAGE,
            fontsize=9, ha="center", va="top", **MONO)
    save(fig, "rl_zip_back.png")


# ------------------------------------------------------------------ shoes / bucket
def full_pattern(name, W, H, seed, base, minor, major, accents, lw=1.0, levels=30,
                 half_scale=0.72, cx_off=0, cy_off=0):
    fig, ax = fig_canvas(W, H, facecolor=base)
    f = crown_field(seed=seed, extent=3.6, arc_r=1.6)
    draw_topo(ax, W / 2 + cx_off, H / 2 + cy_off, max(W, H) * half_scale, f,
              major, minor, lw_scale=lw, levels=levels)
    for (px, py, s) in accents:
        m = ax.scatter([px], [py], marker="^", s=s, facecolors="none",
                       edgecolors=major, linewidths=1.4, zorder=5)
    save(fig, name)


def shoes_and_bucket():
    rng = np.random.default_rng(5)

    def acc(W, H, n):
        return [(rng.uniform(0.1, 0.9) * W, rng.uniform(0.1, 0.9) * H, rng.uniform(45, 80))
                for _ in range(n)]

    # Slip-on hombre: patrón amplio, izquierda/derecha con encuadres distintos
    full_pattern("rl_slipon_left.png", 2325, 2325, 61, CREAM_BG, OLIVE_SOFT, OLIVE,
                 acc(2325, 2325, 4), lw=1.35, levels=30, half_scale=0.78, cx_off=-160)
    full_pattern("rl_slipon_right.png", 2325, 2325, 61, CREAM_BG, OLIVE_SOFT, OLIVE,
                 acc(2325, 2325, 4), lw=1.35, levels=30, half_scale=0.78, cx_off=160)
    # Zapatillas altas mujer: más denso y fino
    full_pattern("rl_hightop_quarters.png", 2250, 2250, 87, CREAM_BG, OLIVE_SOFT, OLIVE,
                 acc(2250, 2250, 5), lw=1.05, levels=38, half_scale=0.72)
    full_pattern("rl_hightop_tongue.png", 2250, 2250, 87, CREAM_BG, OLIVE_SOFT, OLIVE,
                 [], lw=1.5, levels=22, half_scale=1.05)
    # Bucket reversible: exterior crema/oliva, interior oliva/crema
    full_pattern("rl_bucket_out.png", 2700, 3150, 19, CREAM_BG, OLIVE_SOFT, OLIVE,
                 acc(2700, 3150, 4), lw=1.5, levels=30, half_scale=0.75)
    full_pattern("rl_bucket_in.png", 2700, 3150, 19, OLIVE, "#8FA075", CREAM_BG,
                 [], lw=1.3, levels=26, half_scale=0.75)


if __name__ == "__main__":
    tank_front()
    ls_front()
    zip_back()
    shoes_and_bucket()
