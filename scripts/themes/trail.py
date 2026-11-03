#!/usr/bin/env python3
"""Example scene: mountain ridge at dusk through a film viewfinder, a cat walking the ridge.

Designed by following references/banner-design.md for a test persona: a data
engineer who hikes, has cats and shoots film. Centered text over a full-bleed
landscape, with a viewfinder overlay. An EXAMPLE of technique: design a new
scene for each person.

    python3 trail.py config.json banner.svg
config: name (<=29), lines (<=36 each), greeting, footer (<=44), frame (corner
        counter, e.g. "24/36"), title, title_gradient [3 colours], line_color
"""
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import banner_kit as k  # noqa: E402

W, H = 1200, 300
GROUND = 264
P = 6  # landscape pixel size

SKY = ["#0f172a", "#1e1b4b", "#3b0764", "#701a75", "#9d174d", "#c2410c", "#f97316", "#fdba74"]

CAT = [  # facing right
    "................#.#.",
    "#...............###.",
    "#..............##E##",
    ".#.............#####",
    "..###############.#.",
    "..###############...",
    "..##############....",
]
LEGS_A = ["..#..#......#..#....", "..#..#......#..#...."]
LEGS_B = ["...##........##.....", "...##........##....."]

CLOUD = [
    "....LLLL........",
    "..LLLLLLLL.LLL..",
    ".LLLLLLLLLLLLLL.",
    "SSSSSSSSSSSSSSSS",
]

PINE = [
    "..#..",
    ".###.",
    "..#..",
    ".###.",
    "#####",
    "..#..",
]


def mix(a, b, t):
    a, b = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def sky():
    """Dusk sky in many thin pixel bands (smooth enough to read text over), with a
    sparse dither row at each band edge for the pixel-art feel."""
    steps = 24
    band = math.ceil(GROUND / steps / P) * P  # whole pixels, bands reach the ground
    colors = []
    for i in range(steps):
        t = i / (steps - 1) * (len(SKY) - 1)
        lo = min(int(t), len(SKY) - 2)
        colors.append(mix(SKY[lo], SKY[lo + 1], t - lo))
    out = []
    for i, c in enumerate(colors):
        y = i * band
        h = band + 1 if i < steps - 1 else H - y
        out.append(f'<rect x="0" y="{y}" width="{W}" height="{h}" fill="{c}"/>')
        if i + 1 < steps:
            dots = [(x + (2 * P if i % 2 else 0), y + band - P, P, P) for x in range(0, W, 4 * P)]
            out.append(f'<path d="{k.d(dots)}" fill="{colors[i + 1]}"/>')
    return "".join(out)


def tri(v):
    """Triangle wave in 0..1, peaks at odd integers: pointy mountain tops."""
    return 1 - abs((v % 2) - 1)


def ridge(base, amp, period, phase, color, sharp=True):
    """Mountain layer as one path: a column of pixels from the ridge line down."""
    rects, tops = [], []
    for x in range(0, W, P):
        if sharp:
            h = tri(x / period + phase) ** 1.6 + 0.45 * tri(x / (period * 0.43) + phase * 2.1) ** 2
        else:
            h = abs(math.sin(x / period + phase)) + 0.3 * math.sin(x / (period * 0.37))
        y = int((base - amp * h) // P * P)
        tops.append((x, y))
        rects.append((x, y, P, H - y))
    return f'<path d="{k.d(rects)}" fill="{color}"/>', tops


def build(cfg):
    name = k.clean(cfg["name"], "name", 29)
    greeting = k.clean(cfg.get("greeting", "Hi, I'm"), "greeting", 40)
    lines = [k.clean(l, f"lines[{i}]", 36) for i, l in enumerate(cfg.get("lines", []))]
    if not lines:
        k.die('config needs at least one entry in "lines"')
    footer = k.clean(cfg.get("footer", ""), "footer", 44)
    frame = k.clean(cfg.get("frame", "24/36"), "frame", 8)
    title = cfg.get("title", f"{cfg['name']}: GitHub profile banner")
    grad = cfg.get("title_gradient", ["#fde68a", "#fdba74", "#f9a8d4"])
    line_color = cfg.get("line_color", "#fef3c7")
    rng = random.Random(5)

    NS = max(4, min(7, 1000 // (len(name) * k.ADV)))
    name_w = k.text_width(name, NS) - NS
    nx = (W - name_w) // 2
    longest = max(len(l) for l in lines) + 2  # + "> " prompt
    tx = (W - longest * k.ADV * 3) // 2
    gx = (W - k.text_width(greeting, 2) + 2) // 2

    body = [sky()]

    # first stars, only high in the sky and away from the text
    text_area = k.box_avoider([(gx - 30, 22, W - gx + 30, 50), (nx - 30, 52, nx + name_w + 30, 114),
                               (tx - 30, 124, W - tx + 30, 160)])
    body.append(k.starfield(rng, W, H, 90, lambda x, y: y > 118 or text_area(x, y)))

    # sun sinking behind the far ridge
    SUNX, SUNY = 936, 196
    sun = []
    for j in range(-7, 7):
        for i in range(-7, 7):
            if math.hypot((i + 0.5) * P, (j + 0.5) * P) < 40:
                sun.append((SUNX + i * P, SUNY + j * P, P, P))
    body.append(f'<circle cx="{SUNX}" cy="{SUNY}" r="70" fill="url(#sun-glow)"/>')
    body.append(f'<path d="{k.d(sun)}" fill="#fde68a"/>')

    far, far_tops = ridge(240, 50, 170, 0.35, "#4c1d95")  # peaks stay below the text panel (y >= 164)
    body.append(far)
    # snow on the top two pixel rows of each local peak
    peaks = [i for i in range(1, len(far_tops) - 1)
             if far_tops[i][1] <= far_tops[i - 1][1] and far_tops[i][1] <= far_tops[i + 1][1] and far_tops[i][1] < 200]
    snow = []
    for i in peaks:
        x, y = far_tops[i]
        snow += [(x - P, y + P, 3 * P, P), (x, y, P, P)]
    body.append(f'<path d="{k.d(snow)}" fill="#e9d5ff"/>')

    # drifting clouds between the text and the peaks
    for ci, (cy, dur, delay) in enumerate(((168, 70, -10), (186, 95, -60))):
        cloud = k.sprite_svg(CLOUD, {"L": "#f5d0fe", "S": "#c084fc"}, 0, cy, 5)
        body.append(f'<g class="drift" style="animation-duration:{dur}s;animation-delay:{delay}s" '
                    f'opacity="0.85">{cloud}</g>')

    mid, mid_tops = ridge(246, 24, 120, 2.3, "#2e1065", sharp=False)
    body.append(mid)
    for x in (96, 264, 438, 702, 1014, 1128):  # pines on the mid ridge
        y = next(yy for xx, yy in mid_tops if xx >= x)
        body.append(k.sprite_svg(PINE, {"#": "#1a0b3d"}, x, y - 5 * 5, 5))

    body.append(f'<rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#0b1020"/>')
    tufts = [(x, GROUND - P, P, P) for x in range(30, W, 84)]
    body.append(f'<path d="{k.d(tufts)}" fill="#0b1020"/>')

    # the cat walks the ridge, left to right, with two-frame legs
    cp = 5
    cy = GROUND - (len(CAT) + 2) * cp
    cat = k.sprite_svg(CAT, {"#": "#0b1020", "E": "#fde047"}, 0, cy, cp)
    cat += f'<g class="fa">{k.sprite_svg(LEGS_A, {"#": "#0b1020"}, 0, cy + len(CAT) * cp, cp)}</g>'
    cat += f'<g class="fb">{k.sprite_svg(LEGS_B, {"#": "#0b1020"}, 0, cy + len(CAT) * cp, cp)}</g>'
    body.append(f'<g class="walk">{cat}</g>')

    # text: centered, with a dark shadow for contrast over the sky
    body.append(k.text_path(greeting, gx, 30, 2, "#e9d5ff"))
    body.append(k.text_path(name, nx + 4, 60 + 4, NS, "#1e1b4b"))
    body.append(k.text_path(name, nx, 60, NS, "url(#title)"))
    pill_w = longest * k.ADV * 3 + 28
    body.append(f'<rect x="{tx - 16}" y="122" width="{pill_w}" height="41" rx="8" fill="#1e1b4b" opacity="0.5"/>')
    clips, typed, cycle = k.typing(lines, tx, 132, 3, line_color, prompt=">", prompt_color="#fb923c")
    body.append(typed)

    # viewfinder overlay: corner brackets and a frame counter
    vf = []
    for x0, y0, sx, sy in ((18, 18, 1, 1), (W - 18, 18, -1, 1), (18, H - 18, 1, -1), (W - 18, H - 18, -1, -1)):
        vf.append(f"M{x0} {y0 + sy * 34}V{y0}H{x0 + sx * 34}")
    body.append(f'<path d="{"".join(vf)}" fill="none" stroke="#fff7ed" stroke-opacity="0.75" stroke-width="4"/>')
    body.append(f'<rect class="blink" x="{W - 64}" y="34" width="10" height="10" fill="#ef4444"/>')
    body.append(k.text_path(frame, W - 48 - k.text_width(frame, 2), 278, 2, "#fdba74"))
    if footer:
        body.append(k.text_path(footer, 48, 278, 2, "#94a3b8"))

    style = (
        ".walk{animation:walk 26s linear infinite}"
        "@keyframes walk{from{transform:translateX(-100px)}to{transform:translateX(1300px)}}"
        ".drift{animation:drift 80s linear infinite}"
        "@keyframes drift{from{transform:translateX(-120px)}to{transform:translateX(1320px)}}"
        ".fa{animation:fa .5s steps(1) infinite}.fb{animation:fb .5s steps(1) infinite}"
        "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}"
        + k.CSS["twinkle"] + k.CSS["blink"]
        + k.reduced_motion(["walk", "drift", "fa", "fb", "tw", "blink"], hidden=["fb"])
    )
    defs = f"""<defs>
<radialGradient id="sun-glow"><stop offset="0.5" stop-color="#fde68a" stop-opacity="0.35"/><stop offset="1" stop-color="#fde68a" stop-opacity="0"/></radialGradient>
<linearGradient id="title" gradientUnits="userSpaceOnUse" x1="{nx}" y1="0" x2="{nx + name_w}" y2="0"><stop offset="0" stop-color="{grad[0]}"/><stop offset="0.5" stop-color="{grad[1]}"/><stop offset="1" stop-color="{grad[2]}"/></linearGradient>
{k.frame_clip(W, H)}
{clips}
</defs>"""
    return k.svg_doc(W, H, title, style, defs, "".join(body), border="#fdba74"), cycle


if __name__ == "__main__":
    k.run(build)
