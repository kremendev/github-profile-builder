# Changelog

## v1.1.0 (2026-11-03)

- **Profile analyser:** an optional weekly "recent activity" section built from the 5 most recently active public repos. It shows a status dot, the latest meaningful commit, releases shipped, and totals.
  - Treats commit text as untrusted: strips HTML, links, control and bidi characters, escapes Markdown, neutralises @mentions.
  - Counts only the owner's own commits, skipping bots, merges and wip commits.
  - Uses fixed dates, so quiet weeks don't commit. Standard library only, with a pinned checkout.
- **Images are off-limits** to the analyser. It writes only between its markers in `README.md` and never emits image syntax. A workflow guard fails the run if any other file, or any text outside the markers, would change.
- **Ranking by real work:** repos are ranked by the owner's latest own commit, not GitHub's `pushed_at`, which force-pushes and rewrites reset. Found in the first live week, with a regression test.
- **Offline tests** (`tests/`), with a real-data fixture and a hostile one.
- **Git publishing route:** push when the session has access, and tag through a GitHub Release when tag pushes are refused.
- **No AI co-author trailers** on commits in the person's repos by default.
- `CLAUDE.md` with this repo's attribution and release rules.

## v1.0.0 (2026-11-03)

First release.

- Full workflow: gather facts, design from top-profile patterns, build, verify, show the draft, publish with explicit OK, check the live page.
- `banner_kit.py`: pixel font (A-Z, 0-9, punctuation), typing animation, sprites, stars, CSS motion and SVG assembly, all self-contained so banners work in GitHub's image sandbox.
- Banner design guide: every person gets a new scene from a five-line brief (person, feel, metaphor, layout, motion), with a variety check against the examples.
- Three example scenes with different motifs, layouts and palettes: space, terminal and trail.
- `render_check.py`: renders a banner inside `<img>` on GitHub's dark and light themes at several moments.
- Secure contribution-game workflow: third-party code runs read-only, every action is pinned to a SHA, and the GIF lives on an orphan branch.
- Verified notes on widgets (dead shields logos, skillicons, rendering rules) and a browser publishing playbook.
