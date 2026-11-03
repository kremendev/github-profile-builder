---
name: github-profile-builder
description: Design, build and publish a standout GitHub profile README: a banner made for the person, project cards, verified widgets, weekly activity. Use for any GitHub profile or profile README request.
---

# GitHub profile builder

Builds a GitHub profile README that looks designed rather than templated,
checks that every piece renders, and publishes it to `<username>/<username>`.

The bundled files hold the hard-won parts:

| File | Use it for |
| --- | --- |
| `scripts/banner_kit.py` | Building blocks for a bespoke animated banner: pixel font, typing animation, sprites, stars, CSS motion, SVG assembly |
| `scripts/themes/space.py`, `terminal.py`, `trail.py` | Three very different example scenes built on the kit. Technique references, not templates. |
| `examples/*.json`, `examples/previews/*.svg` | A config and the rendered result for each example theme |
| `scripts/render_check.py` | Screenshots an SVG inside `<img>`, like GitHub, on dark and light pages at several moments |
| `references/banner-design.md` | How to design a new banner from the person's info. Read before building the banner. |
| `assets/space-shooter.yml` | Secure daily workflow that turns the contribution graph into a space shooter GIF |
| `scripts/github_analyser.py`, `assets/analyser.yml` | Weekly "recent activity" section built from the 5 most recently active public repos |
| `references/analyser.md` | Analyser setup, options, security design and offline testing. Read if adding the section. |
| `tests/` | Offline tests and fixtures for the analyser (`python3 -m unittest discover tests`) |
| `assets/README-template.md` | Example section structure to adapt |
| `references/design-patterns.md` | Patterns from top profiles, and content rules. Read before planning. |
| `references/widgets.md` | Verified facts about badges, icons and GitHub rendering, with check snippets. Read before adding any external image. |
| `references/workflow.md` | Why the workflow is split the way it is, and how to refresh its pins. Read if adding the game. |
| `references/publishing.md` | Browser-based publishing, step by step. Read before touching GitHub. |

## Workflow

Keep a task list. This runs across several turns, and the person may step away.

### 1. Gather the facts

- **Username.** Check whether `<username>/<username>` already exists, so you know if you're creating or redesigning.
- **Their public repos.** Get name, description, language and date from `GET https://api.github.com/users/<u>/repos?per_page=100`, and read each repo's README. Project cards must describe what the code actually is. A repo name is not enough.
- **From the person:** their stack and experience level, what they want to be known for, their interests, and **what to leave out**. If a fact is missing, ask. Don't guess, because it ends up public under their name.
- The workspace shell is often blocked from GitHub's raw files. Do GitHub reads with the browser tool's JavaScript from a github.com page (see widgets.md).

### 2. Plan the design

Read `references/design-patterns.md`. Choose 3 to 5 patterns that fit the person, and theme the banner and section names around their interests. Tell them in a few lines which ideas come from which top profiles. People like knowing the design has a source.

### 3. Build

1. **Banner: design one for this person.** Follow `references/banner-design.md`:
   1. Write the five-line brief (person, feel, metaphor, layout, motion) from what you learned in step 1.
   2. Write `scene.py` in the working directory on top of `scripts/banner_kit.py`. Borrow technique from the closest example in `scripts/themes/`.
   3. Run `python3 scene.py banner.json out/assets/banner.svg`.

   Don't hand out an example scene with a new name. Two people should never get the same banner unless one of them picks an existing look on purpose, in which case run that theme directly with their config.

   The kit's pixel font draws A-Z, 0-9 and common punctuation. Anything else is rejected with a clear error, so ask for a transliteration of non-Latin names.
2. **README.** Adapt `assets/README-template.md`.
   - Write in plain words.
   - One emoji per heading at most.
   - Use `colspan="2"` for an odd project card.
3. **Contribution game (optional).** Copy `assets/space-shooter.yml` to `.github/workflows/`.
   - Refresh its pins first (workflow.md).
   - Never use the upstream example's single write-permission job.
4. **Recent activity (optional).** A weekly section showing what the person is working on, built from their 5 most recently active public repos. Follow `references/analyser.md`:
   - add the markers to the README
   - copy the script and workflow
   - ask which repos to exclude
   - name the section in the profile's theme language

### 4. Verify before showing anything

| Check | How |
| --- | --- |
| Banner | `python3 scripts/render_check.py out/assets/banner.svg shots/ --times 1,4,9`. Look at every frame: text readable, nothing on letters, nothing overlapping, both themes fine, and clearly different from the examples. Measure overlaps you suspect instead of eyeballing them. |
| Every external image | Run the checks in widgets.md. Shields logos and icon IDs break silently. |
| Markdown | Render with GitHub's markdown API in `gfm` mode. Headings, tables, checkboxes and code highlighting present, no comment leaks. |
| Workflow | `yaml.safe_load` parses it, every `uses:` is pinned to a 40-character SHA, and the permissions are split. Dry-run the publish step's git commands on a scratch repo. |
| Analyser | `python3 -m unittest discover tests` passes. Capture the person's data as a fixture (analyser.md), print their section, render it, and check the 5 repos and the counts look right. |

### 5. Show the draft

- Send the banner (`display: render`) and the README, with the banner brief.
- Summarise in a few lines:
  - which top-profile ideas you used
  - what you skipped on purpose, and why (e.g. stats cards on a young account)
  - any security choices
- Ask only the questions that block content: missing facts, and "is X right?" for anything you inferred.
- Apply their edits, then grep the files to confirm removed content is really gone.

### 6. Publish

Follow `references/publishing.md`:
- The person signs in themselves.
- Get an explicit OK before creating the public repo.
- Upload assets, then the workflow, then the README.
- Hash-check each file after commit.
- Run the workflow once.

### 7. Check the live profile and wrap up

- Confirm every image loads on `https://github.com/<username>`, and take a screenshot.
- Report what's live, what you checked, and any cosmetic misses.
- Offer the follow-ups without doing them unasked: name, bio, repo descriptions, and pinning their best repo first.

## Things that went wrong before, so you don't repeat them

- Signing in to their normal Chrome doesn't sign in the app's built-in browser pane. Say which browser to use.
- `logo=css3` and `logo=linkedin` render blank on shields.io. Re-check logos every time.
- gh-space-shooter v2.0.5 has no `no-commit` input. Pin a newer commit.
- GitHub's markdown API in `markdown` mode hides task lists. Use `gfm`.
- Files copied into the shared outputs folder can gain a C2PA provenance block. Hash-check against the staged copy.
- Typing into the upload page's commit-message field may silently fail. Read it back before committing.
- A session with git push access may still be refused tag pushes (HTTP 403). Create the version tag through a GitHub Release instead.
- Don't add AI co-author trailers (`Co-Authored-By`, `Claude-Session`) to commits in the person's repos unless they ask for them. A profile is their personal showcase, and removing trailers later means rewriting published history.
