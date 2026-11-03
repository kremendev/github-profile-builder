#!/usr/bin/env python3
"""Screenshot an SVG inside an <img> tag, the way GitHub renders README images.

Usage:
    python3 render_check.py banner.svg out_dir [--times 1.5,3.5,9] [--width 900]

Writes dark-<t>.png and light-<t>.png for each moment (seconds after load), on
GitHub's dark (#0d1117) and light (#ffffff) page colours. Look at them: check
that text is readable, nothing overlaps, and the animation is at a sensible
point in each frame.

Needs Playwright (pip install playwright). Uses Playwright's own Chromium if
installed, otherwise a system Chrome/Chromium.
"""
import argparse
import pathlib
import shutil

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("svg")
ap.add_argument("out_dir")
ap.add_argument("--times", default="1.5,3.5,9")
ap.add_argument("--width", type=int, default=900)
args = ap.parse_args()

svg = pathlib.Path(args.svg).resolve()
out = pathlib.Path(args.out_dir)
out.mkdir(parents=True, exist_ok=True)
moments = sorted(float(x) for x in args.times.split(","))
height = int(args.width * 0.25) + 48  # banner is 4:1, plus page padding


def launch(p):
    try:
        return p.chromium.launch(args=["--no-sandbox"])
    except Exception:
        for name in ("google-chrome", "chromium", "chromium-browser"):
            exe = shutil.which(name)
            if exe:
                return p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
        raise SystemExit("render_check: no Chromium found. Run `playwright install chromium` or install Chrome.")


written = []
with sync_playwright() as p:
    browser = launch(p)
    for theme, bg in (("dark", "#0d1117"), ("light", "#ffffff")):
        html = out / f"frame-{theme}.html"
        html.write_text(
            f'<body style="margin:0;padding:24px;background:{bg}">'
            f'<img src="{svg.as_uri()}" style="width:{args.width}px;display:block"></body>'
        )
        page = browser.new_page(viewport={"width": args.width + 48, "height": height})
        page.goto(html.as_uri())
        page.wait_for_load_state("load")
        last = 0.0
        for m in moments:
            page.wait_for_timeout(int((m - last) * 1000))
            last = m
            shot = out / f"{theme}-{m:04.1f}s.png"
            page.screenshot(path=str(shot))
            written.append(shot.name)
        page.close()
    browser.close()
print("wrote", ", ".join(written), "in", out)
