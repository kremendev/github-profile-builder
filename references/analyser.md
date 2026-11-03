# Profile analyser: a "recent activity" section that updates itself

`scripts/github_analyser.py` plus `assets/analyser.yml` keep one section of the
profile README current. Once a week they read the owner's **5 most recently
active public repos**, never all of them, and rewrite the block between:

```
<!-- analyser:start -->
<!-- analyser:end -->
```

## What the section shows

- **A table of the last 5 active repos**, newest push first. Each row has:
  - a status dot: 🟢 this week, 🟡 this month, ⚪ quieter
  - the repo name and language
  - the latest meaningful commit, linked, plus how many more there were in the window
  - the date
- **Recently shipped:** releases published in the window, if there are any.
- **A totals line:** commits in the window, active repos, and the main language.

Skipped on purpose:
- forks, archived repos, private repos, and the profile repo itself
- commits by anyone other than the owner, bots, merges, and wip/fixup/squash commits

## Setup in the profile repo

1. Copy `scripts/github_analyser.py` to `.github/scripts/github_analyser.py`.
2. Copy `assets/analyser.yml` to `.github/workflows/analyser.yml`. Refresh the checkout pin first (workflow.md).
3. Put the two markers in the README where the section should go. Projects or right below the about section works well. The script refuses to run without them, so it never rewrites the wrong part.
4. Publish, then run the workflow once from the Actions tab (**Run workflow**). Check the run succeeded and that the live profile shows the table.

### Options (in the workflow's `run:` line)

| Flag | Default | Use |
| --- | --- | --- |
| `--count` | 5 | How many recent repos to show |
| `--days` | 30 | Window for commits and releases |
| `--exclude a,b` | none | Repos to leave out, e.g. coursework the person doesn't want shown |
| `--title` | 🔭 Recent activity | Match the profile's theme, e.g. "🗺️ Recent quests" or "🛰️ Mission log" |

Ask the person which repos to exclude. "Recent" can surface things they'd rather not feature.

## Images are off-limits

Once the banner and other images exist, the analyser can't change them. Three layers enforce this:

1. **The script.** It only ever writes `README.md`, and only the text between the markers. It refuses to run if its own section would contain any image syntax (`<img>`, `<picture>`, `<svg>`, `![...]`).
2. **The workflow guard.** Before committing, it fails the run if any file other than `README.md` changed, or if a single byte outside the markers differs from the last commit.
3. **The commit step** stages `README.md` only.

The space shooter GIF is separate. It's meant to regenerate daily, and lives on its own `output` branch.

## Why it's built this way

- **Commit messages are untrusted input.** Anyone whose pull request gets merged writes text that would land on the owner's public profile. The script:
  - keeps only the first line
  - strips HTML (tracking `<img>`, `<script>`), bare URLs, control characters and bidi overrides
  - truncates the text and escapes Markdown, so `|`, `[` and `(` can't break the table or create links
  - neutralises `@mentions`
  - only links to URLs inside the owner's own `github.com/<user>/` space
- **Read 5, write 1.** The token in the workflow is the profile repo's own `GITHUB_TOKEN`. It can read public data and write only the profile repo. Never give it a personal token with access to other repos.
- **No relative dates.** "3 days ago" would change on every run and create a commit every week even with no activity. Fixed dates mean no new activity, no change, no commit.
- **Standard library only.** The job installs nothing, so the only third-party code is the pinned checkout action.

## Testing

```bash
python3 -m unittest discover tests
```

The tests run offline against two fixtures:
- `tests/fixtures/kremendev.json`: real public data
- `tests/fixtures/attacks.json`: hostile commit messages, other authors, bots, merges, forks, private repos and a draft release

They check that:
- the right 5 repos are picked
- the counts are correct
- nothing dangerous gets through
- updating the README twice with the same data changes nothing the second time

To preview someone's section before publishing when the workspace can't reach api.github.com, capture their data with the browser tool on any github.com page and save it as a fixture:

```js
const api = p => fetch('https://api.github.com' + p).then(r => r.json());
const u = '<user>';
const repos = await api(`/users/${u}/repos?per_page=100&sort=pushed`);
const pick = repos.filter(r => !r.fork && !r.archived && !r.private && r.name.toLowerCase() !== u).slice(0, 5);
const since = new Date(Date.now() - 30 * 864e5).toISOString();
const detail = {};
for (const r of pick) detail[r.name] = {
  commits: await api(`/repos/${u}/${r.name}/commits?since=${since}&per_page=100`),
  releases: await api(`/repos/${u}/${r.name}/releases?per_page=5`)
};
JSON.stringify({now: new Date().toISOString(), repos, detail})
```

Then run `python3 scripts/github_analyser.py --user <user> --fixture saved.json` to print the section. Render it with the markdown API check in widgets.md.
