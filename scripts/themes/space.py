#!/usr/bin/env python3
"""Example scene: pixel deep space. Text on the left, ship and ringed planet on the right.

Made for someone into space, sci-fi and pixel art. An EXAMPLE of technique:
design a new scene for each person (references/banner-design.md).

    python3 space.py config.json banner.svg
config: name (<=29), lines (<=37 each), greeting, footer (<=60), title,
        title_gradient [3 colours], line_color, prompt_color
"""
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import banner_kit as k  # noqa: E402

W, H = 1200, 300

STYLE = """
.tw{animation:tw 3.2s ease-in-out infinite}
.t1{animation-delay:-0.8s}.t2{animation-delay:-1.6s}.t3{animation-delay:-2.4s}
@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}
.bob{animation:bob 3s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.fa{animation:fa .24s steps(1) infinite}.fb{animation:fb .24s steps(1) infinite}
@keyframes fa{0%{opacity:1}50%{opacity:0}}
@keyframes fb{0%{opacity:0}50%{opacity:1}}
.shoot{opacity:0;animation:shoot 9s linear infinite;animation-delay:2s}
@keyframes shoot{0%{opacity:0;transform:translate(0,0)}2%{opacity:1}11%{opacity:1}13%{opacity:0;transform:translate(-340px,46px)}100%{opacity:0;transform:translate(-340px,46px)}}
.blink{animation:blink 1s steps(1) infinite}
@keyframes blink{0%{opacity:1}50%{opacity:0}}
@media (prefers-reduced-motion:reduce){.tw,.bob,.fa,.fb,.shoot,.blink{animation:none}.fb,.shoot{opacity:0}}
"""

SHIP = [
    "......DD..........",
    "......DHH.........",
    "...RRDHHHH........",
    "..DHHHHHHHHHH.....",
    ".DHHHHHHHCCHHHH...",
    "DHHHHHHHHCWCHHHHH.",
    ".DHHHHHHHCCHHHH...",
    "..DHHHHHHHHHH.....",
    "...RRDHHHH........",
    "......DHH.........",
    "......DD..........",
]
SHIP_COLORS = {"D": "#64748b", "H": "#e2e8f0", "C": "#38bdf8", "W": "#e0f2fe", "R": "#f472b6"}


def planet_and_ring(px, py, pr, p):
    """Shaded pixel gas giant with a tilted ring, drawn back-to-front."""
    light = (-0.55, -0.62, 0.56)
    ln = math.sqrt(sum(c * c for c in light))
    light = tuple(c / ln for c in light)
    tones = ["#1e0b4b", "#3b1a8a", "#5b2bc9", "#7c4dff", "#a78bfa", "#e4dcff"]
    planet = {t: [] for t in tones}
    for j in range(-13, 13):
        for i in range(-13, 13):
            cx, cy = (i + 0.5) * p, (j + 0.5) * p
            dist = math.hypot(cx, cy)
            if dist > pr:
                continue
            nz = math.sqrt(max(0.0, 1 - (dist / pr) ** 2))
            lit = (cx / pr) * light[0] + (cy / pr) * light[1] + nz * light[2]
            lit += 0.07 * math.sin(cy / 7.0 + 0.8)  # gas-giant bands
            lit += 0.025 if (i + j) % 2 else -0.025  # light dither on band edges
            idx = 0 if lit < -0.05 else 1 if lit < 0.22 else 2 if lit < 0.5 else 3 if lit < 0.74 else 4 if lit < 0.9 else 5
            planet[tones[idx]].append((px + i * p, py + j * p, p, p))

    ring_front = {"#fbcfe8": [], "#f472b6": [], "#be185d": []}
    ring_back = {"#fbcfe8": [], "#f472b6": [], "#be185d": []}
    ca, sa = math.cos(-0.32), math.sin(-0.32)
    ra, rb = pr * 1.78, pr * 0.36
    for j in range(-16, 16):
        for i in range(-28, 28):
            cx, cy = (i + 0.5) * p, (j + 0.5) * p
            u = cx * ca + cy * sa
            v = -cx * sa + cy * ca
            e = (u / ra) ** 2 + (v / rb) ** 2
            if not 0.80 < e < 1.16:
                continue
            color = "#fbcfe8" if e < 0.9 else "#f472b6" if e < 1.05 else "#be185d"
            gx, gy = px + i * p, py + j * p
            if v > 0:
                ring_front[color].append((gx, gy, p, p))
            elif math.hypot(cx, cy) > pr:
                ring_back[color].append((gx, gy, p, p))
    out = [f'<path d="{k.d(r)}" fill="{c}" opacity="0.8"/>' for c, r in ring_back.items()]
    out += [f'<path d="{k.d(r)}" fill="{c}"/>' for c, r in planet.items()]
    out += [f'<path d="{k.d(r)}" fill="{c}"/>' for c, r in ring_front.items()]
    return "".join(out)


def build(cfg):
    name = k.clean(cfg["name"], "name", 29)
    greeting = k.clean(cfg.get("greeting", "Hi, I'm"), "greeting", 37)
    lines = [k.clean(l, f"lines[{i}]", 37) for i, l in enumerate(cfg.get("lines", []))]
    if not lines:
        k.die('config needs at least one entry in "lines"')
    footer = k.clean(cfg.get("footer", ""), "footer", 60)
    title = cfg.get("title", f"{cfg['name']}: GitHub profile banner")
    grad = cfg.get("title_gradient", ["#67e8f9", "#a78bfa", "#f472b6"])
    line_color = cfg.get("line_color", "#7dd3fc")
    prompt_color = cfg.get("prompt_color", "#f472b6")

    TX = 64
    NS = max(4, min(8, 700 // (len(name) * k.ADV)))  # name pixel size, shrinks for long names
    name_w = k.text_width(name, NS)
    PX, PY, PR, P = 1068, 222, 72, 6
    rng = random.Random(7)

    text_boxes = [
        (56, 42, max(600, TX + name_w + 8), 152),
        (56, 178, 790, 214),
        (56, 244, max(720, TX + k.text_width(footer, 2) + 8), 272),
        (770, 90, 900, 172),  # ship
    ]
    in_text = k.box_avoider(text_boxes)

    def avoid(x, y):
        return math.hypot(x - PX, y - PY) < PR + 14 or in_text(x, y)

    body = [
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        '<ellipse cx="300" cy="250" rx="420" ry="160" fill="url(#neb1)"/>',
        '<ellipse cx="930" cy="40" rx="360" ry="150" fill="url(#neb2)"/>',
        k.starfield(rng, W, H, 170, avoid),
    ]

    trail = [(0, 0, 4, 4)] + [(6 * i, -1 * i, 3, 3) for i in range(1, 9)]
    streak = "".join(
        f'<rect x="{760 + x}" y="{26 + y}" width="{w}" height="{h}" fill="#ffffff" opacity="{k.r1(1 - i / 10)}"/>'
        for i, (x, y, w, h) in enumerate(trail)
    )
    body.append(f'<g class="shoot">{streak}</g>')
    body.append(planet_and_ring(PX, PY, PR, P))

    SX, SY, SS = 790, 98, 6
    flame_a = [(SX - SS, SY + 4 * SS, SS, 3 * SS), (SX - 2 * SS, SY + 4 * SS, SS, 3 * SS), (SX - 3 * SS, SY + 5 * SS, SS, SS)]
    flame_b = [(SX - SS, SY + 4 * SS, SS, 3 * SS), (SX - 2 * SS, SY + 5 * SS, SS, SS)]
    core = [(SX - SS, SY + 5 * SS, SS, SS)]
    ship = k.sprite_svg(SHIP, SHIP_COLORS, SX, SY, SS)
    ship += f'<path class="fa" d="{k.d(flame_a)}" fill="#fb923c"/>'
    ship += f'<path class="fb" d="{k.d(flame_b)}" fill="#fb923c"/>'
    ship += f'<path d="{k.d(core)}" fill="#fde047"/>'
    body.append(f'<g class="bob">{ship}</g>')

    body.append(k.text_path(greeting, TX, 50, 3, "#94a3b8"))
    body.append(k.text_path(name, TX + 4, 86 + 4, NS, "#1e1b4b"))
    body.append(k.text_path(name, TX, 86, NS, "url(#title)"))

    clips, typed, cycle = k.typing(lines, TX, 186, 3, line_color, prompt=">", prompt_color=prompt_color)
    body.append(typed)
    if footer:
        body.append(k.text_path(footer, TX, 252, 2, "#64748b"))

    defs = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070b17"/><stop offset="0.55" stop-color="#0d1430"/><stop offset="1" stop-color="#160c33"/></linearGradient>
<radialGradient id="neb1"><stop offset="0" stop-color="#7c3aed" stop-opacity="0.30"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
<radialGradient id="neb2"><stop offset="0" stop-color="#0891b2" stop-opacity="0.26"/><stop offset="1" stop-color="#0891b2" stop-opacity="0"/></radialGradient>
<linearGradient id="title" gradientUnits="userSpaceOnUse" x1="{TX}" y1="0" x2="{TX + name_w}" y2="0"><stop offset="0" stop-color="{grad[0]}"/><stop offset="0.5" stop-color="{grad[1]}"/><stop offset="1" stop-color="{grad[2]}"/></linearGradient>
{k.frame_clip(W, H)}
{clips}
</defs>"""
    return k.svg_doc(W, H, title, STYLE, defs, "".join(body)), cycle


if __name__ == "__main__":
    k.run(build)
