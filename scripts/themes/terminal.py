#!/usr/bin/env python3
"""Example scene: hacker terminal. A terminal window types `$ whoami`, the name and
cycling lines; binary rain falls behind a glowing padlock on the right.

Made for someone into cybersecurity, CLI tools or backend work. An EXAMPLE of
technique: design a new scene for each person (references/banner-design.md).

    python3 terminal.py config.json banner.svg
config: name (<=29), lines (<=37 each), greeting (shown as the command, default
        "whoami"), footer (<=50), handle (window title, <=24), title, accent colour
"""
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import banner_kit as k  # noqa: E402

W, H = 1200, 300
WX, WY, WW, WH = 36, 28, 760, 244  # terminal window

LOCK = [
    "....######....",
    "...########...",
    "..###....###..",
    "..##......##..",
    "..##......##..",
    "..##......##..",
    "BBBBBBBBBBBBBB",
    "BLLLLLLLLLLLLB",
    "BLLLLLKKLLLLLB",
    "BLLLLKKKKLLLLB",
    "BLLLLLKKLLLLLB",
    "BLLLLLKKLLLLLB",
    "BLLLLLKKLLLLLB",
    "BLLLLLLLLLLLLB",
    "BDDDDDDDDDDDDB",
    "BBBBBBBBBBBBBB",
]


def build(cfg):
    name = k.clean(cfg["name"], "name", 29)
    command = k.clean(cfg.get("greeting", "whoami"), "greeting", 30)
    lines = [k.clean(l, f"lines[{i}]", 37) for i, l in enumerate(cfg.get("lines", []))]
    if not lines:
        k.die('config needs at least one entry in "lines"')
    footer = k.clean(cfg.get("footer", ""), "footer", 50)
    handle = k.clean(cfg.get("handle", "~/" + cfg["name"].split()[0]), "handle", 24)
    title = cfg.get("title", f"{cfg['name']}: GitHub profile banner")
    accent = cfg.get("accent", "#4ade80")
    rng = random.Random(11)

    body = [f'<rect width="{W}" height="{H}" fill="#04060a"/>',
            '<ellipse cx="1000" cy="150" rx="330" ry="210" fill="url(#glow-bg)"/>']

    # binary rain on the right, clipped to its own area
    cols = []
    for ci in range(13):
        x = 822 + ci * 28
        glyphs = []
        for gi in range(14):
            ch = rng.choice("01")
            op = 0.95 if gi == 13 else 0.15 + 0.6 * gi / 13  # brightest at the falling head
            fill = "#d1fae5" if gi == 13 else accent
            glyphs.append(k.text_path(ch, x, gi * 22, 2, fill, attrs=f'opacity="{k.r1(op)}" '))
        dur = rng.uniform(4.5, 9.0)
        delay = -rng.uniform(0, dur)
        cols.append(f'<g class="rain" style="animation-duration:{k.r1(dur)}s;'
                    f'animation-delay:{k.r1(delay)}s">{"".join(glyphs)}</g>')
    body.append(f'<g clip-path="url(#rain-area)">{"".join(cols)}</g>')

    # padlock on a dark halo so it reads over the rain
    LX, LY, LP = 952, 92, 7
    body.append(f'<circle cx="{LX + 7 * LP}" cy="{LY + 8 * LP}" r="92" fill="#04060a" opacity="0.88"/>')
    body.append(f'<circle class="pulse" cx="{LX + 7 * LP}" cy="{LY + 8 * LP}" r="92" fill="url(#lock-glow)"/>')
    body.append(k.sprite_svg(LOCK, {"#": "#9ca3af", "B": "#14532d", "L": accent, "D": "#16a34a", "K": "#04060a"},
                             LX, LY, LP))

    # terminal window
    body.append(f'<rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="10" fill="#0a0f14" stroke="#1f2937" stroke-width="2"/>')
    body.append(f'<path d="M{WX + 1} {WY + 28}h{WW - 2}" stroke="#1f2937" stroke-width="2"/>')
    for i, c in enumerate(("#ef4444", "#f59e0b", "#22c55e")):
        body.append(f'<rect x="{WX + 16 + i * 18}" y="{WY + 9}" width="10" height="10" fill="{c}"/>')
    hx = WX + (WW - k.text_width(handle, 2)) // 2
    body.append(k.text_path(handle, hx, WY + 8, 2, "#6b7280"))

    TX = WX + 28
    body.append(k.text_path("$", TX, 74, 3, accent))
    body.append(k.text_path(command, TX + 2 * 18, 74, 3, "#9ca3af"))

    NS = max(4, min(7, 700 // (len(name) * k.ADV)))
    body.append(f'<g filter="url(#glow)" opacity="0.7">{k.text_path(name, TX, 108, NS, accent)}</g>')
    body.append(k.text_path(name, TX, 108, NS, "#dcfce7"))

    clips, typed, cycle = k.typing(lines, TX, 180, 3, "#86efac", prompt="$", prompt_color=accent)
    body.append(typed)

    if footer:
        body.append(k.text_path("[OK]", TX, 234, 2, accent))
        body.append(k.text_path(footer, TX + 5 * 12, 234, 2, "#4b5563"))

    body.append(f'<rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="10" fill="url(#scan)"/>')

    style = (
        ".rain{animation:fall 6s linear infinite}"
        "@keyframes fall{from{transform:translateY(-310px)}to{transform:translateY(310px)}}"
        + k.CSS["pulse"] + k.CSS["blink"]
        + k.reduced_motion(["rain", "pulse", "blink"])
    )
    defs = f"""<defs>
<radialGradient id="glow-bg"><stop offset="0" stop-color="#16a34a" stop-opacity="0.22"/><stop offset="1" stop-color="#16a34a" stop-opacity="0"/></radialGradient>
<radialGradient id="lock-glow"><stop offset="0.55" stop-color="{accent}" stop-opacity="0"/><stop offset="0.8" stop-color="{accent}" stop-opacity="0.28"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="0.35"/></pattern>
<clipPath id="rain-area"><rect x="810" y="0" width="{W - 810}" height="{H}"/></clipPath>
{k.frame_clip(W, H)}
{clips}
</defs>"""
    return k.svg_doc(W, H, title, style, defs, "".join(body), border="#22c55e"), cycle


if __name__ == "__main__":
    k.run(build)
