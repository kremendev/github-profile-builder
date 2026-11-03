# Widgets and rendering: verified facts

Last verified 2026-11-03. External services change, so re-run the checks
below for whatever you actually use, every time. A broken badge on a public
profile looks worse than no badge.

## Where to run checks from

The workspace shell is often blocked from `raw.githubusercontent.com` and other
sites. Run checks with the browser tool's JavaScript instead: open any page on
the target site (same-origin `fetch` avoids CORS), or a `github.com` page for
GitHub API and raw-file reads.

## shields.io badges

- Logos come from Simple Icons, which removes and renames brands.
  - `logo=css3` is dead: no logo renders. Use `logo=css`.
  - `logo=linkedin` is dead (removed at LinkedIn's request). Use a plain badge with no logo.
  - These worked: html5, css, javascript, typescript, react, vite, zod, git, github, claude, anthropic, eslint, prettier, linux, gmail, discord, x, telegram, hackthebox, tryhackme.
- Check from a page on img.shields.io: a working logo puts an `<image` element in the SVG.

```js
// run on https://img.shields.io/badge/test-ok-green
const out = {};
for (const l of ['react', 'linkedin']) {
  const s = await fetch(`/badge/x-x-000?logo=${l}&logoColor=white`).then(r => r.text());
  out[l] = s.includes('<image') ? 'logo ok' : 'NO LOGO';
}
out
```

## skillicons.dev

- `https://skillicons.dev/icons?i=html,css,js,ts,react,nextjs,nestjs,nodejs,vite,git,github&perline=11` works.
- Each icon is 48px, so pick `perline` so the row fits about 650px.
- The response starts with a newline before `<svg`. Don't treat that as a failure when checking it.
- Confirm new IDs visually: navigate to the URL and screenshot it.

## github-readme-stats and similar

- The public Vercel instance shares GitHub's API rate limit and is often throttled. Self-hosting fixes that.
- It's not worth it on new or small accounts (see design-patterns.md).

## How GitHub renders README images

- Every image is proxied through camo and shown in an `<img>`.
- **Inside an SVG:** no scripts, no external fonts, no external images. Fonts must be drawn as paths, like `banner_kit.py`'s pixel font, or embedded as base64.
- **What does work:** inline `<style>`, CSS keyframes and SMIL `<animate>`.
- **Relative paths** (`./assets/banner.svg`) resolve against the default branch.
- **Files on another branch** need an absolute URL: `https://github.com/<user>/<user>/raw/<branch>/<file>`.

## Markdown checks before publishing

Render the README with GitHub's own API from a github.com page. Unauthenticated, it allows about 60 calls an hour.

```js
const r = await fetch('https://api.github.com/markdown', {
  method: 'POST',
  headers: {'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'},
  body: JSON.stringify({text: README_TEXT, mode: 'gfm', context: '<user>/<user>'})
});
```

- Use `mode: 'gfm'`. `mode: 'markdown'` does NOT render task lists, so checkboxes look missing even though repo READMEs do render them.
- Check that the headings, tables, task-list checkboxes and highlighted code blocks are all present, and that no HTML comment content leaks.
- To pass README text into the browser, base64-encode it so backticks and quotes survive.
