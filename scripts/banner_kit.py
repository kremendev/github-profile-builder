"""Building blocks for animated, self-contained SVG banners for GitHub READMEs.

GitHub shows README images inside an <img> sandbox: no scripts, no external
fonts, no external images. Everything here draws with plain SVG shapes, inline
CSS animations and SMIL, which all work in that sandbox.

A scene script imports this module, draws its own background, motifs and
sprites, and calls svg_doc() to assemble the file. See scripts/themes/ for three
very different examples. They show technique; design a new scene for each person.

Main pieces:
    clean(text, field, limit)       validate text for the pixel font (uppercases it)
    text_path(text, x, y, s, fill)  pixel-font text as one <path>
    text_width(text, s)             width of text at pixel size s
    sprite_svg(grid, palette, ...)  pixel sprite from a list of strings
    typing(lines, x, y, s, ...)     typed-and-erased cycling lines (SMIL), with cursor
    starfield(rng, ...)             twinkling stars and sparkles
    CSS                             ready-made keyframe animations
    reduced_motion(classes)         prefers-reduced-motion rule
    svg_doc(...)                    wraps everything in a rounded, framed <svg>
    run(build)                      command-line runner: build(config) -> (svg, cycle)
"""
import json
import sys

# ---------------------------------------------------------------- pixel font (5x7)
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ";": [".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "<": ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    "@": [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "%": ["##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"],
    "~": [".....", ".....", ".#...", "#.#.#", "...#.", ".....", "....."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "[": [".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."],
    "]": [".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."],
    "{": ["..##.", ".#...", ".#...", "#....", ".#...", ".#...", "..##."],
    "}": [".##..", "...#.", "...#.", "....#", "...#.", "...#.", ".##.."],
    "|": ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "*": [".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    " ": ["....."] * 7,
}
ADV = 6  # columns per character: 5 glyph + 1 gap
GLYPH_H = 7


def die(msg):
    sys.exit(f"banner: {msg}")


def clean(text, field, limit):
    """Uppercase text and check the font can draw it and it fits the layout."""
    text = str(text).upper()
    bad = sorted({ch for ch in text if ch not in FONT})
    if bad:
        die(f"{field} has characters the pixel font can't draw: {' '.join(repr(c) for c in bad)}. "
            "Transliterate or remove them.")
    if len(text) > limit:
        die(f"{field} is {len(text)} characters; this layout fits at most {limit}. Shorten it.")
    return text


def text_rects(text, x0, y0, s):
    """Rectangles for text at pixel size s, merging runs of lit pixels per row."""
    rects = []
    for ci, ch in enumerate(text):
        gx = x0 + ci * ADV * s
        for r, row in enumerate(FONT[ch]):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    rects.append((gx + start * s, y0 + r * s, (c - start) * s, s))
                else:
                    c += 1
    return rects


def d(rects):
    """SVG path data for a list of (x, y, w, h) rectangles."""
    return "".join(f"M{x} {y}h{w}v{h}h{-w}z" for x, y, w, h in rects)


def r1(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_width(text, s):
    """Advance width of text at pixel size s (includes the trailing 1-column gap)."""
    return len(text) * ADV * s


def text_path(text, x, y, s, fill, attrs=""):
    """Pixel-font text as one <path>. attrs, if given, must end with a space."""
    return f'<path {attrs}d="{d(text_rects(text, x, y, s))}" fill="{fill}"/>'


def sprite_rects(grid, palette, x, y, px):
    """{key: rects} for a pixel sprite. grid: list of equal-length strings; '.' is empty."""
    out = {k: [] for k in palette}
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch in out:
                out[ch].append((x + c * px, y + r * px, px, px))
    return out


def sprite_svg(grid, palette, x, y, px):
    """A pixel sprite as one <path> per palette colour, in palette order."""
    return "".join(f'<path d="{d(v)}" fill="{palette[k]}"/>'
                   for k, v in sprite_rects(grid, palette, x, y, px).items())


# ---------------------------------------------------------------- typing animation
def typing(lines, x, y, s, color, prompt=">", prompt_color="#f472b6", prompt_cols=2,
           timing=(0.055, 2.2, 0.022, 0.35), id_prefix="c", cursor_class="blink"):
    """Lines that type in, hold, erase, and hand over to the next line, forever.

    Returns (clip_defs, body, cycle_seconds). Put clip_defs inside <defs> and body
    in the scene. The cursor uses CSS class `cursor_class` (CSS["blink"] makes it blink).
    prompt=None draws no prompt and starts the text at x.
    """
    type_s, hold, erase, gap = timing
    adv = ADV * s
    lx = x + prompt_cols * adv if prompt else x
    body = [text_path(prompt, x, y, s, prompt_color)] if prompt else []

    events, t = [], 0.0  # (time, line index, chars visible)
    for li, line in enumerate(lines):
        for k in range(1, len(line) + 1):
            t += type_s
            events.append((t, li, k))
        t += hold
        for k in range(len(line) - 1, -1, -1):
            t += erase
            events.append((t, li, k))
        t += gap
    total = t

    def timeline(values_at):
        times, vals = [0.0], [values_at(None)]
        for et, li, k in events:
            v = values_at((li, k))
            if v != vals[-1]:
                times.append(et / total)
                vals.append(v)
        times.append(1.0)
        vals.append(vals[-1])
        return ";".join(r1(v) for v in times), ";".join(str(v) for v in vals)

    def width_of(target):
        def at(ev):
            if ev is None:
                return 0
            li, k = ev
            return k * adv if li == target else 0
        return at

    clips = []
    for li, line in enumerate(lines):
        kt, vals = timeline(width_of(li))
        cid = f"{id_prefix}{li}"
        clips.append(
            f'<clipPath id="{cid}"><rect x="{lx}" y="{y - 2}" height="{GLYPH_H * s + 4}" width="0">'
            f'<animate attributeName="width" dur="{r1(total)}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="{kt}" values="{vals}"/></rect></clipPath>'
        )
        body.append(text_path(line, lx, y, s, color, attrs=f'clip-path="url(#{cid})" '))

    kt, vals = timeline(lambda ev: lx if ev is None else lx + ev[1] * adv)
    body.append(
        f'<rect class="{cursor_class}" x="{lx}" y="{y}" width="{3 * s}" height="{GLYPH_H * s}" fill="{color}">'
        f'<animate attributeName="x" dur="{r1(total)}s" repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="{kt}" values="{vals}"/></rect>'
    )
    return "".join(clips), "".join(body), total


# ---------------------------------------------------------------- stars
def starfield(rng, w, h, count=170, avoid=lambda x, y: False):
    """Static stars, 4 twinkle groups (CSS classes tw t0..t3) and a few sparkles."""
    static = {"#ffffff": [], "#c7d2fe": [], "#a5f3fc": []}
    twinkle = [[] for _ in range(4)]
    sparkles = []
    for _ in range(count):
        x, y = rng.randrange(8, w - 8), rng.randrange(8, h - 8)
        if avoid(x, y):
            continue
        roll = rng.random()
        if roll < 0.06:
            sparkles.append((x, y, rng.randrange(4)))
            continue
        size = 2 if roll < 0.78 else 3
        rect = (x, y, size, size)
        if rng.random() < 0.35:
            twinkle[rng.randrange(4)].append(rect)
        else:
            static[rng.choice(list(static))].append(rect)
    out = [f'<path d="{d(rects)}" fill="{color}" opacity="0.55"/>' for color, rects in static.items()]
    out += [f'<path class="tw t{i}" d="{d(rects)}" fill="#ffffff"/>' for i, rects in enumerate(twinkle)]
    for x, y, g in sparkles:
        cross = [(x - 4, y, 3, 2), (x + 3, y, 3, 2), (x - 1, y - 4, 2, 3), (x - 1, y + 2, 2, 3), (x - 1, y, 4, 2)]
        out.append(f'<path class="tw t{g}" d="{d(cross)}" fill="#e0e7ff"/>')
    return "".join(out)


def box_avoider(boxes):
    """avoid() function for starfield/particles: True inside any (x0, y0, x1, y1) box."""
    return lambda x, y: any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in boxes)


# ---------------------------------------------------------------- CSS animations
CSS = {
    "twinkle": ".tw{animation:tw 3.2s ease-in-out infinite}"
               ".t1{animation-delay:-0.8s}.t2{animation-delay:-1.6s}.t3{animation-delay:-2.4s}"
               "@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}",
    "bob": ".bob{animation:bob 3s ease-in-out infinite}"
           "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}",
    "blink": ".blink{animation:blink 1s steps(1) infinite}@keyframes blink{0%{opacity:1}50%{opacity:0}}",
    "flicker": ".fa{animation:fa .24s steps(1) infinite}.fb{animation:fb .24s steps(1) infinite}"
               "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}",
    "pulse": ".pulse{animation:pulse 2.4s ease-in-out infinite}"
             "@keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}",
}


def reduced_motion(classes, hidden=()):
    """Stops the given CSS classes for people who ask for less motion."""
    rule = ",".join("." + c for c in classes) + "{animation:none}"
    if hidden:
        rule += ",".join("." + c for c in hidden) + "{opacity:0}"
    return "@media (prefers-reduced-motion:reduce){" + rule + "}"


# ---------------------------------------------------------------- assembly
def frame_clip(w, h, rx=18):
    return f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>'


def svg_doc(w, h, title, style, defs, body, rx=18, border="#94a3b8"):
    """The final SVG. defs must include frame_clip(); body is clipped to the rounded frame."""
    edge = (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="none" '
            f'stroke="{border}" stroke-opacity="0.22"/>') if border else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'shape-rendering="crispEdges" role="img" aria-labelledby="t">'
        f'<title id="t">{esc(title)}</title>'
        f"<style>{style.strip()}</style>{defs}"
        f'<g clip-path="url(#frame)">{body}</g>{edge}'
        f"</svg>"
    )


def run(build):
    """CLI: python3 scene.py config.json out.svg, where build(config) -> (svg, cycle)."""
    if len(sys.argv) != 3:
        die(f"usage: {sys.argv[0]} config.json out.svg")
    with open(sys.argv[1]) as fh:
        config = json.load(fh)
    if "name" not in config:
        die('config needs at least a "name"')
    svg, cycle = build(config)
    with open(sys.argv[2], "w") as fh:
        fh.write(svg)
    print(f"wrote {sys.argv[2]}: {len(svg) / 1024:.1f} KB, typing cycle {cycle:.1f}s")
