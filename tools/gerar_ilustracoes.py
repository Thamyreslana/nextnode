"""
NextNode — Gerador de ilustrações dos produtos

Uso (na pasta do projeto):
    uv run python tools/gerar_ilustracoes.py

Gera um SVG por produto em static/images/ilustracoes/<nome>.svg, usando o
mesmo nome-base do campo `image` (ex.: gpu_rx9070xt.jpg -> gpu_rx9070xt.svg).

As ilustrações são desenhos ORIGINAIS e genéricos, feitos só com formas
geométricas. Não reproduzem fotos, logotipos nem o design exato de nenhum
fabricante: servem apenas para representar o tipo de peça. Cada SVG traz a
marcação "ILUSTRAÇÃO" e o site mostra o aviso "Imagem meramente ilustrativa".

Como funciona: cada categoria tem uma função de desenho (gpu, cpu, ram...).
Ela lê os dados do produto (specs/compat, ex.: capacidade, potência, número de
ventoinhas) e um pequeno estilo por produto em STYLES (cores, rótulo...).
Para um produto novo, adicione o estilo dele em STYLES e rode o script.
"""

import os
import re
import sys
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from data.products import PRODUCTS  # noqa: E402

OUT_DIR = os.path.join(ROOT, "static", "images", "ilustracoes")
W, H = 480, 360
FONT = "Arial, Helvetica, sans-serif"
GOLD = "#c9a23f"

# Estilo de cada produto (por id). Cores são genéricas, não as do fabricante.
STYLES = {
    # GPU: body = (cor de cima, cor de baixo) da carcaça
    1:  {"body": ("#3b4049", "#15181d"), "accent": "#e8364f", "fans": 3, "ring": "#e8364f", "label": "RTX 5090", "xl": True},
    2:  {"body": ("#33373e", "#141619"), "accent": "#d94141", "fans": 3, "label": "RX 9070 XT"},
    3:  {"body": ("#2e323a", "#121418"), "accent": "#9b6bff", "fans": 3, "ring": "#9b6bff", "label": "RTX 5070 Ti"},
    4:  {"body": ("#e4e7eb", "#a6aeb8"), "accent": "#2d7ff9", "fans": 2, "label": "ARC B580", "dark_text": True},
    # CPU
    5:  {"label": ("RYZEN 9", "9950X")},
    6:  {"label": ("CORE i9", "14900K")},
    7:  {"label": ("RYZEN 7", "9700X")},
    8:  {"label": ("CORE i7", "14700K")},
    # RAM: spreader = cores do dissipador
    9:  {"spreader": ("#dfe3e7", "#8d939b"), "accent": "#ffffff", "rgb": True, "dark_text": True},
    10: {"spreader": ("#3a3e45", "#16181b"), "accent": "#7b838c"},
    11: {"spreader": ("#33373d", "#131518"), "accent": "#c0392b"},
    12: {"spreader": ("#2c2f34", "#0f1113"), "accent": "#a0a7ae", "low": True},
    # SSD
    13: {"accent": "#ff8a3d"},
    14: {"accent": "#e9ecef"},
    15: {"accent": "#ff5a1f"},
    16: {"accent": "#d62d2d"},
    # Placas-mãe
    17: {"pcb": "#17191d", "metal": ("#3a3f47", "#1f2227"), "accent": "#e8364f", "dimms": 2},
    18: {"pcb": "#17191d", "metal": ("#43474f", "#24272c"), "accent": "#e8364f", "dimms": 4},
    19: {"pcb": "#141619", "metal": ("#4a4d53", "#26282c"), "accent": "#ff7a1a", "dimms": 4},
    20: {"pcb": "#e6e8eb", "metal": ("#ffffff", "#cfd3d8"), "accent": "#c9a24a", "dimms": 4, "light": True},
    # Refrigeração: pump = estilo da bomba do water cooler
    21: {"pump": "lcd", "accent": "#7c5cff", "ring": "#7c5cff"},
    22: {"pump": "ring", "accent": "#36c5f0", "ring": "#36c5f0"},
    23: {},
    24: {"pump": "mirror", "accent": "#ff4fd8", "ring": "#ff4fd8"},
    # Gabinetes
    25: {"white": True, "front": "glass", "rgb": "#00cdb5"},
    26: {"front": "mesh"},
    27: {"front": "glass", "rgb": "#9b6bff"},
    28: {"front": "slats"},
    # Fontes
    29: {}, 30: {}, 31: {}, 32: {},
}

EFFICIENCY_COLORS = {"Bronze": "#b07a4a", "Gold": "#d4a937", "Platinum": "#c3ccd6", "Titanium": "#8e9aa6"}


# ─── Pequenos ajudantes de SVG ────────────────────────────────────────────────

def attrs(**kw):
    return " ".join(f'{k.rstrip("_").replace("_", "-")}="{v}"' for k, v in kw.items() if v is not None)


def rect(x, y, w, h, **kw):
    return f'<rect {attrs(x=round(x, 1), y=round(y, 1), width=round(w, 1), height=round(h, 1), **kw)}/>'


def circle(cx, cy, r, **kw):
    return f'<circle {attrs(cx=round(cx, 1), cy=round(cy, 1), r=round(r, 1), **kw)}/>'


def path(d, **kw):
    return f'<path {attrs(d=d, **kw)}/>'


def text(x, y, content, size=14, weight="bold", fill="#ffffff", anchor="middle", **kw):
    a = attrs(x=round(x, 1), y=round(y, 1), font_family=FONT, font_size=size, font_weight=weight,
              fill=fill, text_anchor=anchor, **kw)
    return f"<text {a}>{escape(content)}</text>"


def linear(id_, top, bottom, horizontal=False):
    x2, y2 = ("1", "0") if horizontal else ("0", "1")
    return (f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')


def shadow(cx, cy, rx, ry=14):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity="0.35"/>'


def fan(cx, cy, r, blade="#2a2e35", hub="#3b4048", ring=None, blades=9, frame="#0d0f12"):
    """Ventoinha vista de frente: moldura, pás curvas e cubo central."""
    blade_d = "M0,-0.24 C0.28,-0.44 0.66,-0.34 0.86,-0.06 C0.6,-0.1 0.34,-0.02 0.14,0.12 Z"
    out = [circle(cx, cy, r + 4, fill=frame), circle(cx, cy, r, fill="#08090b")]
    for k in range(blades):
        out.append(path(blade_d, fill=blade, transform=f"translate({cx} {cy}) scale({r}) rotate({k * 360 / blades:.1f})"))
    out.append(circle(cx, cy, r * 0.3, fill=hub))
    out.append(circle(cx, cy, r * 0.12, fill="#000", opacity="0.35"))
    if ring:
        out.append(circle(cx, cy, r + 1.5, fill="none", stroke=ring, stroke_width=3, opacity="0.9"))
    return "".join(out)


def document(product, body, defs=""):
    title = f"Ilustração: {product['name']}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title>"
        f"<defs>{defs}</defs>"
        f"{body}"
        f'<text x="{W - 14}" y="{H - 12}" font-family="{FONT}" font-size="10" font-weight="bold" letter-spacing="2" '
        f'fill="#ffffff" opacity="0.4" text-anchor="end">ILUSTRAÇÃO</text>'
        "</svg>"
    )


def spec_number(product, key, default=0):
    match = re.search(r"\d+", str(product["specs"].get(key, "")))
    return int(match.group()) if match else default


# ─── Desenhos por categoria ───────────────────────────────────────────────────

def draw_gpu(p, s):
    n = s["fans"]
    x0, x1 = (36, 444) if n == 3 else (88, 392)
    y0, y1 = (84, 252) if s.get("xl") else (96, 240)
    h = y1 - y0
    label_fill = "#1b1e23" if s.get("dark_text") else "#e9edf1"

    defs = linear("body", *s["body"]) + linear("metal", "#d5d9de", "#8e959e", horizontal=True)
    out = [shadow(240, y1 + 40, 200)]
    # PCB e conector PCIe (dourado)
    out.append(rect(x0 + 10, y1 - 8, x1 - x0 - 20, 18, fill="#1d2a22"))
    out.append(rect(x0 + 80, y1 + 8, 200, 13, fill=GOLD, rx=1))
    out += [rect(x0 + 84 + i * 8, y1 + 9, 4, 11, fill="#a8842c") for i in range(24)]
    # Suporte metálico (bracket) com saídas de vídeo
    out.append(rect(x0 - 24, y0 - 12, 16, h + 44, rx=2, fill="url(#metal)"))
    out += [rect(x0 - 21, y0 + 18 + i * 34, 10, 22, rx=2, fill="#2a2e33") for i in range(4)]
    # Carcaça
    out.append(rect(x0, y0, x1 - x0, h, rx=16, fill="url(#body)", stroke="#000", stroke_opacity="0.4", stroke_width=2))
    out.append(path(f"M{x0 + 16},{y0 + 26} H{x1 - 16}", stroke="#ffffff", stroke_opacity="0.08", stroke_width=2))
    # Detalhes de cor nas pontas
    out.append(path(f"M{x0},{y1 - 34} L{x0 + 40},{y1 - 34} L{x0 + 58},{y1} L{x0 + 16},{y1} Z", fill=s["accent"], opacity="0.85"))
    out.append(path(f"M{x1},{y0 + 34} L{x1 - 40},{y0 + 34} L{x1 - 58},{y0} L{x1 - 16},{y0} Z", fill=s["accent"], opacity="0.85"))
    out.append(text(x0 + 22, y0 + 19, s["label"], size=13, fill=label_fill, anchor="start", letter_spacing="1"))
    # Conector de energia
    out.append(rect(x1 - 120, y0 - 9, 38, 10, rx=2, fill="#0b0c0e"))
    # Ventoinhas
    r = min(h * 0.36, (x1 - x0) / (2 * n) - 10)
    cy = (y0 + y1) / 2 + 9
    step = (x1 - x0) / n
    for i in range(n):
        out.append(fan(x0 + step * (i + 0.5), cy, r, ring=s.get("ring")))
    return document(p, "".join(out), defs)


def draw_cpu(p, s):
    amd = p["brand"] == "AMD"
    w, h = (210, 210) if amd else (190, 230)
    substrate, substrate_side = "#2f6b3e", "#1d4527"
    iso = "matrix(0.866 0.5 -0.866 0.5 240 160)"   # projeção isométrica

    def package(fill):
        return rect(-w / 2, -h / 2, w, h, rx=8, fill=fill)

    defs = linear("ihs", "#e7eaee", "#a3aab3")
    out = [shadow(240, 300, 170, 18)]
    out.append(f'<g transform="translate(0 16)"><g transform="{iso}">{package(substrate_side)}</g></g>')
    out.append(f'<g transform="{iso}">')
    out.append(package(substrate))
    # Componentes (capacitores) e marcador do pino 1
    for i in range(6):
        out.append(rect(-w / 2 + 14 + i * 9, h / 2 - 14, 5, 8, fill=GOLD))
    out.append(path(f"M{-w / 2 + 6},{-h / 2 + 6} l16,0 l-16,16 Z", fill=GOLD))
    # Tampa metálica (IHS)
    if amd:
        m = 18
        out.append(rect(-w / 2 + m, -h / 2 + m, w - 2 * m, h - 2 * m, rx=10, fill="url(#ihs)"))
        # Recortes nas bordas da tampa, típicos do AM5 (2 por lado)
        top, bottom = -h / 2 + m, h / 2 - m - 14
        left, right = -w / 2 + m, w / 2 - m - 14
        for off in (-48, 48):
            out.append(rect(off - 14, top, 28, 14, fill=substrate))
            out.append(rect(off - 14, bottom, 28, 14, fill=substrate))
            out.append(rect(left, off - 14, 14, 28, fill=substrate))
            out.append(rect(right, off - 14, 14, 28, fill=substrate))
    else:
        out.append(rect(-w / 2 + 24, -h / 2 + 30, w - 48, h - 60, rx=8, fill="url(#ihs)"))
        out.append(rect(-w / 2 + 14, -26, 14, 52, rx=3, fill="url(#ihs)"))
        out.append(rect(w / 2 - 28, -26, 14, 52, rx=3, fill="url(#ihs)"))
    out.append(text(0, -6, s["label"][0], size=26, fill="#7d838b", letter_spacing="2"))
    out.append(text(0, 24, s["label"][1], size=18, fill="#8d939b", letter_spacing="1"))
    out.append("</g>")
    return document(p, "".join(out), defs)


def draw_ram(p, s):
    count, size = re.match(r"(\d+)\D+(\d+GB)", p["specs"]["Capacidade"]).groups()
    memory = p["compat"]["memory"]
    h = 74 if s.get("low") else 90
    w = 330
    label_fill = "#1b1e23" if s.get("dark_text") else "#e9edf1"
    defs = linear("spreader", *s["spreader"])
    defs += ('<linearGradient id="rgb" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#ff4d6d"/><stop offset=".35" stop-color="#ffd23f"/>'
             '<stop offset=".65" stop-color="#3ee8b5"/><stop offset="1" stop-color="#7c5cff"/></linearGradient>')

    def stick(x, y):
        out = [rect(x + 4, y + h - 4, w - 8, 26, fill="#1f4d33")]                       # placa (PCB)
        notch = x + w * (0.55 if memory == "DDR5" else 0.6)                            # chanfro do encaixe
        out.append(rect(x + 10, y + h + 12, notch - x - 14, 10, fill=GOLD))
        out.append(rect(notch + 6, y + h + 12, x + w - notch - 16, 10, fill=GOLD))
        if s.get("rgb"):
            out.append(rect(x + 8, y - 16, w - 16, 20, rx=6, fill="url(#rgb)", opacity="0.95"))
        out.append(rect(x, y, w, h, rx=6, fill="url(#spreader)", stroke="#000", stroke_opacity="0.35", stroke_width=2))
        out.append(path(f"M{x + w - 120},{y} L{x + w - 80},{y} L{x + w - 130},{y + h} L{x + w - 170},{y + h} Z",
                        fill=s["accent"], opacity="0.25"))
        out.append(path(f"M{x + 14},{y + 12} H{x + w - 14}", stroke="#ffffff", stroke_opacity="0.12", stroke_width=2))
        out.append(text(x + 22, y + h / 2 + 7, f"{memory}  ·  {size}", size=17, fill=label_fill, anchor="start", letter_spacing="1"))
        return "".join(out)

    out = [shadow(250, 318, 190)]
    out.append(stick(110, 66))     # pente de trás
    out.append(stick(60, 150))     # pente da frente
    return document(p, "".join(out), defs)


def draw_ssd(p, s):
    capacity = p["specs"]["Capacidade"]
    w, h = 380, 96
    accent = s["accent"]

    def body(fill):
        return rect(-w / 2, -h / 2, w, h, rx=5, fill=fill)

    tilt = "translate(240 168) rotate(-9)"
    out = [shadow(240, 262, 200, 16)]
    out.append(f'<g transform="translate(0 10)"><g transform="{tilt}">{body("#050607")}</g></g>')
    out.append(f'<g transform="{tilt}">')
    out.append(body("#13171b"))
    # Contatos dourados (pinos finos) com o chanfro "M"
    for y in range(int(-h / 2 + 6), int(h / 2 - 6), 5):
        if not (14 <= y <= 24):
            out.append(rect(-w / 2, y, 14, 3, fill=GOLD))
    out.append(circle(w / 2 - 4, 0, 10, fill="#0b191b"))                               # encaixe do parafuso
    # Etiqueta
    out.append(rect(-w / 2 + 28, -h / 2 + 8, w - 64, h - 16, rx=4, fill="#1d2228"))
    out.append(rect(-w / 2 + 28, -h / 2 + 8, 10, h - 16, fill=accent))
    out.append(text(-w / 2 + 56, 4, capacity, size=30, fill="#f1f5f4", anchor="start"))
    out.append(text(-w / 2 + 58, 26, "NVMe  ·  PCIe 4.0", size=12, weight="normal", fill="#9aa5ad", anchor="start", letter_spacing="1"))
    out += [rect(60 + i * 26, -22, 18, 44, rx=2, fill="#2a3037") for i in range(3)]       # chips sob a etiqueta
    out.append("</g>")
    return document(p, "".join(out))


def draw_motherboard(p, s):
    x0, y0, w, h = 114, 22, 252, 312
    light = s.get("light")
    accent = s["accent"]
    socket = p["compat"]["socket"]
    chipset = p["specs"]["Chipset"]
    defs = linear("metal", *s["metal"])
    slot = "#c7cbd0" if light else "#2a2e33"
    trace = "#cfd3d8" if light else "#22262b"

    out = [shadow(240, 340, 160, 10)]
    out.append(rect(x0, y0, w, h, rx=6, fill=s["pcb"], stroke="#000", stroke_opacity="0.4", stroke_width=2))
    out += [path(f"M{x0 + 20},{y0 + 180 + i * 9} H{x0 + w - 20}", stroke=trace, stroke_width=1, opacity="0.6") for i in range(4)]
    # Tampa das conexões traseiras e dissipadores do VRM
    out.append(rect(x0 + 6, y0 + 8, 52, 120, rx=6, fill="url(#metal)"))
    out.append(path(f"M{x0 + 12},{y0 + 100} L{x0 + 52},{y0 + 70}", stroke=accent, stroke_width=4))
    out.append(rect(x0 + 64, y0 + 8, 112, 30, rx=5, fill="url(#metal)"))
    out.append(rect(x0 + 64, y0 + 30, 10, 2, fill=accent))
    out.append(path(f"M{x0 + 70},{y0 + 30} H{x0 + 170}", stroke=accent, stroke_width=3))
    # Soquete do processador
    sx, sy = x0 + 82, y0 + 56
    if socket == "AM5":
        out.append(rect(sx, sy, 76, 76, rx=4, fill="#9aa1a9"))
        out.append(rect(sx + 8, sy + 8, 60, 60, rx=2, fill="#5d646c"))
        out.append(path(f"M{sx + 82},{sy + 4} V{sy + 76}", stroke="#b8bec5", stroke_width=4, stroke_linecap="round"))
    else:
        out.append(rect(sx + 4, sy - 4, 68, 84, rx=4, fill="#9aa1a9"))
        out.append(rect(sx + 14, sy + 8, 48, 60, rx=2, fill="#5d646c"))
        out.append(path(f"M{sx},{sy + 2} V{sy + 74}", stroke="#b8bec5", stroke_width=4, stroke_linecap="round"))
    # Slots de memória
    for i in range(s["dimms"]):
        out.append(rect(x0 + 186 + i * 13, y0 + 46, 8, 120, rx=2, fill=slot))
    out.append(rect(x0 + w - 12, y0 + 60, 8, 64, rx=2, fill=slot))                       # conector 24 pinos
    # Slots PCIe e dissipadores de M.2
    out.append(rect(x0 + 22, y0 + 172, 200, 12, rx=2, fill="#d5d9de"))
    out.append(rect(x0 + 22, y0 + 200, 180, 22, rx=4, fill="url(#metal)"))
    out.append(path(f"M{x0 + 28},{y0 + 211} H{x0 + 80}", stroke=accent, stroke_width=3))
    out.append(rect(x0 + 22, y0 + 236, 200, 12, rx=2, fill=slot))
    out.append(rect(x0 + 22, y0 + 262, 150, 22, rx=4, fill="url(#metal)"))
    # Dissipador do chipset
    cx, cy = x0 + w - 74, y0 + h - 74
    out.append(rect(cx, cy, 62, 62, rx=8, fill="url(#metal)"))
    out.append(rect(cx + 6, cy + 6, 50, 4, fill=accent))
    out.append(text(cx + 31, cy + 40, chipset, size=13, fill="#1b1e23" if light else "#e9edf1"))
    return document(p, "".join(out), defs)


def draw_cooler(p, s):
    if p["specs"]["Tipo"].lower().startswith("air"):
        return draw_air_cooler(p, s)

    defs = linear("pump", "#33373e", "#121417")
    out = [shadow(240, 330, 190, 12)]
    # Radiador com 3 ventoinhas
    out.append(rect(36, 36, 408, 116, rx=8, fill="#1b1e22", stroke="#000", stroke_opacity="0.4", stroke_width=2))
    out.append(rect(36, 36, 22, 116, rx=4, fill="#2a2e34"))
    out.append(rect(422, 36, 22, 116, rx=4, fill="#2a2e34"))
    for i in range(3):
        out.append(fan(108 + i * 132, 94, 48, ring=s.get("ring")))
    # Mangueiras até a bomba
    out.append(path("M66,150 C66,250 140,262 186,262", fill="none", stroke="#0b0c0e", stroke_width=15, stroke_linecap="round"))
    out.append(path("M96,150 C96,228 150,232 186,232", fill="none", stroke="#141619", stroke_width=15, stroke_linecap="round"))
    # Bomba
    bx, by, size = 184, 190, 116
    cx, cy = bx + size / 2, by + size / 2
    out.append(rect(bx, by, size, size, rx=24, fill="url(#pump)", stroke="#000", stroke_opacity="0.4", stroke_width=2))
    pump = s.get("pump")
    if pump == "lcd":
        defs += (f'<radialGradient id="screen"><stop offset="0" stop-color="{s["accent"]}"/>'
                 '<stop offset="1" stop-color="#120b2e"/></radialGradient>')
        out.append(circle(cx, cy, 44, fill="url(#screen)", stroke="#000", stroke_width=3))
        out.append(text(cx, cy + 8, "36°", size=24, fill="#ffffff"))
    elif pump == "ring":
        out.append(circle(cx, cy, 40, fill="#0d0f12"))
        out.append(circle(cx, cy, 36, fill="none", stroke=s["accent"], stroke_width=5))
        out.append(circle(cx, cy, 16, fill="#2a2e34"))
    else:  # mirror: quadrados concêntricos, efeito "espelho infinito"
        for i in range(5):
            m = 14 + i * 9
            out.append(rect(bx + m, by + m, size - 2 * m, size - 2 * m, rx=14 - i * 2, fill="none",
                            stroke=s["accent"], stroke_width=2.5, opacity=f"{1 - i * 0.18:.2f}"))
    return document(p, "".join(out), defs)


def draw_air_cooler(p, s):
    out = [shadow(240, 312, 150, 12)]
    # Heatpipes e base
    out += [path(f"M{x},{288} V{70}", stroke="#2b2f35", stroke_width=7, stroke_linecap="round") for x in (150, 170, 190, 290, 310, 330)]
    out.append(rect(186, 276, 108, 22, rx=4, fill="#8d949c"))
    # Duas torres de aletas
    for tx in (112, 262):
        out.append(rect(tx, 52, 106, 220, rx=4, fill="#15171a", stroke="#000", stroke_width=2))
        out += [path(f"M{tx + 4},{60 + i * 8} H{tx + 102}", stroke="#2a2e33", stroke_width=2) for i in range(26)]
        out.append(rect(tx - 4, 44, 114, 18, rx=5, fill="#25282d"))
        out.append(path(f"M{tx + 10},{53} H{tx + 96}", stroke="#c9ced4", stroke_width=1.5, opacity="0.7"))
    # Ventoinha central
    out.append(fan(240, 164, 66, blade="#1f2227", hub="#2c3036"))
    return document(p, "".join(out))


def draw_psu(p, s):
    watts = p["compat"]["watts"]
    efficiency = p["specs"]["Eficiência"].replace("80+", "").strip()
    badge = EFFICIENCY_COLORS.get(efficiency, "#c3ccd6")
    fx0, fy0, size, depth, rise = 92, 116, 190, 150, 64

    defs = linear("front", "#2a2d32", "#141619") + linear("side", "#1d2024", "#0e1012")
    out = [shadow(250, 330, 190, 14)]
    # Face de cima e face lateral (perspectiva)
    out.append(path(f"M{fx0},{fy0} L{fx0 + depth},{fy0 - rise} L{fx0 + depth + size},{fy0 - rise} L{fx0 + size},{fy0} Z", fill="#33373d"))
    out.append(path(f"M{fx0 + size},{fy0} L{fx0 + size + depth},{fy0 - rise} L{fx0 + size + depth},{fy0 - rise + size} L{fx0 + size},{fy0 + size} Z", fill="url(#side)"))
    # Etiqueta na lateral (desenhada no plano da lateral)
    side = f"matrix(1 {-rise / depth:.4f} 0 1 {fx0 + size} {fy0})"
    out.append(f'<g transform="{side}">')
    out.append(rect(16, 34, depth - 32, size - 68, rx=4, fill="#e9ecef"))
    out.append(text(depth / 2, 84, f"{watts}W", size=26, fill="#15171a"))
    out.append(rect(30, 100, depth - 60, 26, rx=13, fill=badge))
    out.append(text(depth / 2, 118, f"80+ {efficiency.upper()}", size=11, fill="#15171a", letter_spacing="1"))
    out.append("</g>")
    # Frente com a grade da ventoinha
    out.append(rect(fx0, fy0, size, size, rx=4, fill="url(#front)", stroke="#000", stroke_opacity="0.4", stroke_width=2))
    cx, cy = fx0 + size / 2, fy0 + size / 2
    out.append(fan(cx, cy, 74, blade="#24272c", hub="#30343a"))
    out += [circle(cx, cy, r, fill="none", stroke="#5b6168", stroke_width=1.5, opacity="0.8") for r in (22, 40, 58, 76)]
    out.append(path(f"M{cx - 78},{cy} H{cx + 78} M{cx},{cy - 78} V{cy + 78}", stroke="#5b6168", stroke_width=1.5, opacity="0.8"))
    return document(p, "".join(out), defs)


def draw_case(p, s):
    full = p["specs"]["Formato"].startswith("Full")
    white = s.get("white")
    # Gabinetes pretos usam um cinza-escuro com borda clara, para não sumirem no fundo escuro do site
    body, body_dark, edge = ("#eceef1", "#c9ced4", "#aab1b9") if white else ("#2c3036", "#1e2125", "#5a626b")
    fx0, fy0 = (96, 92) if full else (110, 98)
    fw, height = (76, 240) if full else (68, 224)
    depth, rise = (250, 72) if full else (232, 66)
    rgb = s.get("rgb")

    defs = (f'<pattern id="mesh" width="6" height="6" patternUnits="userSpaceOnUse">'
            f'<circle cx="3" cy="3" r="1.4" fill="{"#8f979f" if white else "#000"}" opacity="0.7"/></pattern>')
    out = [shadow(260, fy0 + height + 18, 200, 14)]
    # Topo
    out.append(path(f"M{fx0},{fy0} L{fx0 + fw},{fy0} L{fx0 + fw + depth},{fy0 - rise} L{fx0 + depth},{fy0 - rise} Z", fill=body_dark))
    # Lateral com o vidro (desenhada no plano da lateral)
    side = f"matrix(1 {-rise / depth:.4f} 0 1 {fx0 + fw} {fy0})"
    out.append(f'<g transform="{side}">')
    out.append(rect(0, 0, depth, height, fill=body, stroke=edge, stroke_opacity="0.5"))
    out.append(rect(12, 12, depth - 24, height - 24, rx=4, fill="#0b1214"))
    out.append(rect(depth * 0.38, 26, depth * 0.5, height * 0.52, rx=3, fill="#171b1f"))              # placa-mãe
    out.append(rect(depth * 0.52, 46, 40, 40, rx=6, fill="#2a2f36"))                                  # cooler
    out.append(rect(depth * 0.3, height * 0.5, depth * 0.6, 24, rx=4, fill="#2a2f36"))                # placa de vídeo
    if rgb:
        out.append(path(f"M{depth * 0.32},{height * 0.5 + 21} H{depth * 0.88}", stroke=rgb, stroke_width=3))
    out.append(rect(12, height - 66, depth - 24, 54, fill=body_dark))                                # cobertura da fonte
    for i in range(3):                                                                               # ventoinhas da frente
        out.append(fan(40, 54 + i * 58, 22, ring=rgb, blades=7))
    out.append(path(f"M{depth * 0.15},12 L{depth * 0.42},12 L{depth * 0.1},{height - 12} L12,{height - 12} L12,{height * 0.6} Z",
                    fill="#ffffff", opacity="0.05"))                                                 # reflexo no vidro
    out.append("</g>")
    # Frente
    out.append(rect(fx0, fy0, fw, height, fill=body, stroke=edge, stroke_opacity="0.5"))
    front = s.get("front")
    if front == "mesh":
        out.append(rect(fx0 + 8, fy0 + 16, fw - 16, height - 32, rx=3, fill="url(#mesh)"))
    elif front == "glass":
        out.append(rect(fx0 + 8, fy0 + 12, fw - 16, height - 24, rx=3, fill="#0b1214", opacity="0.92"))
        if rgb:
            out += [circle(fx0 + fw / 2, fy0 + 58 + i * 64, 20, fill="none", stroke=rgb, stroke_width=3, opacity="0.85") for i in range(3)]
    else:  # slats: frente com aletas inclinadas e duas ventoinhas grandes
        out.append(rect(fx0 + 8, fy0 + 14, fw - 16, height - 28, rx=3, fill="#0d0f12"))
        out.append(fan(fx0 + fw / 2, fy0 + 76, fw / 2 - 12, blades=7))
        out.append(fan(fx0 + fw / 2, fy0 + 166, fw / 2 - 12, blades=7))
        slats = int((height - 40) / 22)
        out += [path(f"M{fx0 + 8},{fy0 + 30 + i * 22} L{fx0 + fw - 8},{fy0 + 16 + i * 22}", stroke=body, stroke_width=5) for i in range(slats)]
    # Pés
    out.append(rect(fx0 + 6, fy0 + height, 18, 7, rx=2, fill="#0b0c0e"))
    out.append(rect(fx0 + fw - 24, fy0 + height, 18, 7, rx=2, fill="#0b0c0e"))
    return document(p, "".join(out), defs)


DRAWERS = {
    "gpu": draw_gpu, "cpu": draw_cpu, "ram": draw_ram, "ssd": draw_ssd,
    "motherboard": draw_motherboard, "cooler": draw_cooler, "psu": draw_psu, "case": draw_case,
}


def illustration_name(product):
    return os.path.splitext(product["image"])[0] + ".svg"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    created = 0
    for product in PRODUCTS:
        style = STYLES.get(product["id"])
        drawer = DRAWERS.get(product["category"])
        if style is None or drawer is None:
            print(f"  pulado (sem estilo): {product['name']}")
            continue
        svg = drawer(product, style)
        with open(os.path.join(OUT_DIR, illustration_name(product)), "w", encoding="utf-8") as f:
            f.write(svg)
        created += 1
    print(f"{created} ilustrações geradas em {os.path.relpath(OUT_DIR, ROOT)}")


if __name__ == "__main__":
    main()
