# Designing a banner from someone's info

Every person gets their own scene. The examples in `scripts/themes/` (space,
terminal, trail) show *technique*. Copying one with a new name is the failure
this guide exists to prevent: two profiles shouldn't share a banner unless the
person picks an existing look on purpose.

## 1. Write a short brief first

Write these five lines and show them to the person with the draft. They make
the reasoning visible, and they're easy to correct.

```
Person:    who they are in one line (role, stack, stage)
Feel:      the 2-3 things they care about most (interests, projects, goals)
Metaphor:  ONE world that ties those together
Layout:    which composition family (below), and why
Motion:    the 2-4 things that move
```

Get the material from what they told you, their repos (a pixel-art game, a
robotics project, a data tool) and their stated goals. If there's nothing
personal to go on, ask one question: "what are you into outside code?"

## 2. One world, not a collage

Pick a single metaphor that can hold the person's themes. A hiker who's a
data engineer and shoots film becomes "a mountain ridge at dusk, seen through
a camera viewfinder". It doesn't become a mountain, a database icon and a
camera side by side.

Idea starters. Combine and twist them, and don't treat them as a menu:

| If they're into | Scene ideas | Motion ideas |
| --- | --- | --- |
| Space, sci-fi | starfield, planets, ships, space station window | twinkle, drifting ship, shooting star |
| Cybersecurity | terminal window, padlock, shield, network map, radar sweep | binary rain, pulsing lock, radar arc |
| AI / ML | neural-net constellation, robot head, glowing nodes | nodes pulsing in sequence, signals along edges |
| Robotics, hardware | workshop bench, robot arm, circuit board, gears | arm swinging, gears turning, LED blink |
| Data, backend | pipes and flowing packets, server rack, pipeline diagram | packets sliding along pipes, rack LEDs |
| Nature, hiking | mountain ridges, forest, lake, dusk sky | clouds drifting, a walking animal, birds |
| Ocean, sailing | waves, boat, lighthouse, underwater | wave bob, beam sweep, bubbles |
| Music | stage, equalizer, vinyl, cassette, synth | equalizer bars, spinning record |
| Gaming | arcade cabinet, HUD with health/XP bars, dialog box, level map | bars filling, coin spin, blinking "press start" |
| Cooking, coffee | kitchen counter, steaming pot or cup, café sign | steam rising, flickering flame |
| Photography, film | viewfinder frame, film strip, darkroom | frame counter, shutter blink, focus marks |
| Cities, travel | skyline, night train, map with route | windows lighting up, train passing, dotted route |
| Retro, synthwave | neon grid horizon, striped sun | grid scrolling toward the viewer |

## 3. Pick a composition family, and vary it

Don't default to "text left, picture right". Choose the family that suits the metaphor:

- **Split.** Text on one side, scene on the other (example: space).
- **Framed.** Text inside an object from their world: a terminal window, game dialog box, phone screen, film frame or ship's monitor (example: terminal).
- **Centered over a landscape.** Name centered on a full-width scene. Works for horizons, cities and seas (example: trail).
- **Overlay.** A full-bleed scene with a HUD or viewfinder laid over it.
- **Panels.** 2-3 panels like a comic strip or dashboard.

The banner is 1200x300 by default. Keep a clear zone of about 40px around all text, and keep particles out of it with `banner_kit.box_avoider`.

## 4. Palette

- One background family plus 1-2 accents.
- The name and typed lines need strong contrast against what's directly behind them. Add a text shadow (a dark copy offset by 4px) or a soft dark band if the background is busy.
- The banner carries its own background and rounded frame, so it works on GitHub's dark and light themes alike. Check both with `render_check.py`.
- Colours can echo their world: phosphor green for a terminal, dusk oranges for hiking, neon magenta and cyan for synthwave.

## 5. Motion budget

- 2-4 moving things, plus the typing line. One should clearly be the focus.
- Use slow loops (3-30 seconds). Nothing that flashes large areas more than about 3 times a second.
- Use CSS keyframes for loops (transform, opacity) and SMIL for anything stepwise, like typing.
- Always add `banner_kit.reduced_motion([...])` for every animated class.

## 6. Sprites

- Draw them as string grids with a small palette. `banner_kit.sprite_svg(grid, palette, x, y, px)` turns them into paths.
- Size: 10-20 columns, pixel size 4-8. Use 3-5 colours: outline or shadow, base, highlight, one accent.
- The silhouette must read at a glance. Check it at the rendered size, not zoomed in.
- Two-frame animation (walking legs, flame, blink): draw both frames and alternate them with `steps(1)` opacity classes, like `CSS["flicker"]`.
- **Originality.** Never draw known characters, mascots, logos or game sprites. Evoke the genre instead: "a cat walking a ridge", not a famous cat. This holds even if the person asks for their favourite game's hero.

## 7. Text

- Use the kit's pixel font through `text_path`, `typing` and `clean`. `clean` uppercases text and rejects characters it can't draw (non-Latin, emoji), so ask the person for a transliteration.
- Work out character limits from the layout, and enforce them with `clean(text, field, limit)` so overflow fails loudly instead of rendering off-canvas.
- Shrink long names: `NS = max(4, min(MAX, available_px // (len(name) * ADV)))`.
- Accept the same config keys as the examples (name, greeting, lines, footer, title, colours) so configs stay interchangeable.

## 8. Build and check

1. Write the scene as `scene.py` in the working directory, not inside the skill. Start from the example closest in *technique*, and aim for under about 200 lines. Import the kit from the skill's `scripts/` folder:
   ```python
   import sys; sys.path.insert(0, "<skill directory>/scripts")
   import banner_kit as k
   ...
   def build(cfg):            # returns (svg_text, typing_cycle_seconds)
       ...
   if __name__ == "__main__":
       k.run(build)
   ```
2. Run `python3 scene.py banner.json out/assets/banner.svg`. Keep the result under about 100 KB by merging rectangles per colour into one `<path>` and avoiding thousands of separate elements.
3. Run `python3 scripts/render_check.py out/assets/banner.svg shots --times 1,4,9`, and actually look at every frame:
   - Is every piece of text readable, with nothing on top of it?
   - Does the motion look right at each moment, and does nothing leave the frame?
   - Does it work on both the dark and light page?
   - **Variety:** does it differ from every example in motif *and* in layout or palette? If it could pass for an example with a new name, redesign it.
4. Show the brief and the frames. Iterate on what the person says.
