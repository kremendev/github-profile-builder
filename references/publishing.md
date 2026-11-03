# Publishing the profile through the browser

Use this when there's no git or `gh` access to the person's GitHub, only a
browser tool. With a git remote and credentials you'd simply push.

## 1. Sign-in

- The person signs in themselves. Never type their password.
- Make sure they sign in to the browser **you** can drive:
  - The Claude app's built-in browser pane (Ctrl/Cmd+Shift+B) has its own logins, separate from their normal Chrome.
  - Claude in Chrome uses their real Chrome, but only if the extension is installed and connected.
- People often sign in to the wrong one. Say which browser it is.
- Check from any github.com page: `document.querySelector('meta[name="user-login"]')?.content`.
- If a tool says the site isn't allowed yet, call the browser's `request_access` and retry. Don't work around it.

## 2. Pre-flight checks

- `fetch('/<user>/<user>', {method: 'HEAD'})`: a 404 means the profile repo doesn't exist yet.
- Fetch `/<user>?tab=repositories` while signed in. It also lists private repos, so you can spot a half-made or private `<user>` repo that would clash.

## 3. Get an explicit OK

Creating a public repo and committing to it publish content under the
person's name. Sign-in alone isn't consent, and the harness may block the
click without a clear yes in chat. List exactly what will happen:
- create public repo `<user>/<user>`
- commit `README.md`, `assets/banner.svg` and `.github/workflows/<name>.yml`
- run the workflow once

Ask for a "yes, publish". Or let them click **Create repository** themselves, then continue.

## 4. Create the repo

1. Go to `https://github.com/new`.
2. Repository name: exactly the username. Type it with a click and type, since React inputs ignore programmatic value changes. GitHub then shows a "special repository" notice.
3. Set visibility to **Public**.
4. Turn **Add README** on. The initial commit makes the upload page work, and your README replaces the starter one.

## 5. Upload files

The upload URL takes a folder path and creates new folders:
`/<user>/<user>/upload/main/assets`, `/<user>/<user>/upload/main/.github/workflows`, `/<user>/<user>/upload/main`.

Upload in this order so the live README never points at missing files:
1. assets
2. workflow
3. README

**If the browser tool has a file-upload tool** (Claude in Chrome's `file_upload`): copy the files into the session's shared outputs folder, find the file input with `find`/`read_page`, and upload.

**If it doesn't** (the built-in pane): inject the file with JavaScript.
1. Gzip and base64 the file in the shell (`gzip -9 -c f | base64 -w0`), and take its SHA-256.
2. Run this on the upload page:

```js
const b64 = "...";  // gzip+base64 of the file
const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
const raw = new Uint8Array(await new Response(new Blob([bytes]).stream()
  .pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', raw))]
  .map(b => b.toString(16).padStart(2, '0')).join('');
if (hash.startsWith(EXPECTED)) {          // never upload a mismatched file
  const dt = new DataTransfer();
  dt.items.add(new File([raw], 'banner.svg', {type: 'image/svg+xml'}));
  const input = document.getElementById('upload-manifest-files-input');
  input.files = dt.files;
  input.dispatchEvent(new Event('change', {bubbles: true}));
}
```

3. Confirm the file name appears in the page's file list.
4. Leave "Commit directly to the branch" selected and click **Commit changes**.

**Commit message:** clicking `#commit-summary-input` and typing did not register in one run, and all commits got GitHub's default "Add files via upload". Try `form_input` on the field, or React's native value setter followed by an `input` event, then read the field back before committing. This fix is untested. If it still fails, the default message is cosmetic, so don't rewrite history over it.

**Content credentials:** files copied into the session's shared outputs folder may get a C2PA provenance block added. SVGs grow a `<metadata>` element and their hash changes. It's harmless and invisible, so leave it in:
- compare hashes against the staged copy, not your original
- re-run `render_check.py` on the staged copy

## 6. Verify each commit

```js
const r = await fetch('https://raw.githubusercontent.com/<user>/<user>/main/<path>', {cache: 'no-store'});
const buf = new Uint8Array(await r.arrayBuffer());
// compare the SHA-256 with the staged file
```

## 7. Run the workflow and check the live profile

1. Go to the Actions tab, open the workflow, click **Run workflow**, then the green **Run workflow** in the menu. Poll `GET /repos/<u>/<u>/actions/runs/<id>` until `status` is `completed` (see workflow.md).
2. On `https://github.com/<user>`, check:
   - every `article.markdown-body img` has `naturalWidth > 0`
   - the headings are all there
   - the task-list checkbox count is right
   - a screenshot shows the banner animating
3. Report what's live, what you checked, and any cosmetic misses honestly.

## 8. Offer profile settings, don't just do them

Name, bio, pinned repos and repo descriptions are account and repo settings, so ask first.

Pinning their best project is the highest-impact follow-up. Without pins, GitHub shows "Popular repositories", which often aren't the best work.
