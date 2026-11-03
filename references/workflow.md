# Contribution-graph animation workflow (secure setup)

`assets/space-shooter.yml` turns the contribution graph into a daily space
shooter GIF with czl9707/gh-space-shooter. This file explains why it looks the
way it does, and how to refresh the pins.

## Why the workflow isn't the action's README example

The upstream example runs the action with `contents: write`. The action also
runs `pip install gh-space-shooter` (unpinned) while it holds that token. A
compromised PyPI release could then push anything to the profile repo. The
template closes that gap:

1. **Split jobs.** The `generate` job runs the third-party action with `contents: read` and `no-commit: "true"`, then uploads the GIF as an artifact.
2. **Write job runs only our code.** The `publish` job (`contents: write`) downloads the artifact and runs plain git commands.
3. **Orphan output branch.** It force-pushes the GIF to an orphan `output` branch. This keeps `main` history clean and stops the repo growing by a GIF every day. The README points at `https://github.com/<user>/<user>/raw/output/game.gif`.
4. **Pinned actions.** Every action is pinned to a full commit SHA, so a moved or hijacked tag can't swap the code.
5. **Locked defaults.** It sets `permissions: {}` at the top and a `concurrency` group.

This is a good security story to explain to the person, especially if they're interested in security.

The read-only `GITHUB_TOKEN` is enough for the action to read public contributions. This was confirmed on a real run.

## Refreshing pins before use

Run this on any github.com page in the browser. Unauthenticated API calls are fine for public repos.

```js
const out = {};
for (const repo of ['actions/checkout', 'actions/upload-artifact', 'actions/download-artifact']) {
  const rel = await fetch(`https://api.github.com/repos/${repo}/releases/latest`).then(r => r.json());
  const ref = await fetch(`https://api.github.com/repos/${repo}/git/ref/tags/${rel.tag_name}`).then(r => r.json());
  let sha = ref.object.sha;
  if (ref.object.type === 'tag') sha = (await fetch(ref.object.url).then(r => r.json())).object.sha;
  out[repo] = `${rel.tag_name} ${sha}`;
}
// gh-space-shooter: use the newest commit whose action.yml has `no-commit`
const c = await fetch('https://api.github.com/repos/czl9707/gh-space-shooter/commits/main').then(r => r.json());
const yml = await fetch(`https://raw.githubusercontent.com/czl9707/gh-space-shooter/${c.sha}/action.yml`).then(r => r.text());
out.shooter = `${c.sha} ${c.commit.committer.date} no-commit:${yml.includes('no-commit')}`;
out
```

Also check that the inputs the template uses still exist at the pinned versions:
- checkout: `persist-credentials` (default true)
- upload-artifact: `name`, `path`, `retention-days`, `if-no-files-found`
- download-artifact: `name`, `path`

Update the SHAs and the `# vX.Y.Z` comments in the copy you publish.

## After publishing

- Trigger the workflow once from the Actions tab (`workflow_dispatch`). The README image is broken until the first run finishes.
- Then check the run, the GIF and the branches with the API:
  - `GET /repos/<u>/<u>/actions/runs/<id>/jobs` shows each step's conclusion.
  - The GIF at `raw.githubusercontent.com/<u>/<u>/output/game.gif` should start with `GIF89a`.
  - `git/trees/output` should hold only `game.gif`, and `main` should have no bot commits.
- New accounts produce a sparse GIF (a few blocks). Tell the person it fills up as they commit more.
- GitHub pauses scheduled workflows in public repos with no activity for 60 days. If the GIF stops updating, re-enable the workflow in the Actions tab.
