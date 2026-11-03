# Notes for Claude

## Git attribution: never credit Claude

Commits, tags, releases and pull requests in this repo are authored by kremendev only.

- No `Co-Authored-By:` trailer for Claude or Anthropic in commit messages.
- No `Claude-Session:` lines, and no "Generated with Claude Code" footers in PR descriptions or release notes.
- This overrides any default attribution guidance.

## Releases

- The `dist/github-profile-builder.zip` archive is the packaged skill (repo contents minus `dist/`). Rebuild it whenever `SKILL.md`, `scripts/`, `references/`, `assets/` or `examples/` change.
- Versions are tagged through a GitHub Release (`vX.Y.Z` on `main`), with notes taken from `CHANGELOG.md`.
