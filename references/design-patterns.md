# Design patterns for GitHub profile READMEs

Distilled from curated lists (abhisheknaiidu/awesome-github-profile-readme,
maxontech/best-github-profile-readme) and standout profiles. Pick 3 to 5 that fit
the person. Stacking every trick makes a profile look like a template.

## Patterns worth borrowing

| Pattern | Seen on | What it does | Notes |
| --- | --- | --- | --- |
| Header banner | MartinHeinz, M0nica | One wide image that sets the mood before any text | Make it self-hosted in the repo (`assets/`), so no outside service can break it. Design a new scene per person with `scripts/banner_kit.py` (see banner-design.md). |
| Typing animation | DenverCoder1 (readme-typing-svg) | Cycles short role/interest lines | Build it into the banner (SMIL) rather than calling the readme-typing-svg service: one less outside dependency. |
| Code-mode "about me" | the "Code Mode" category of awesome-github-profile-readme | The bio as an object in the person's main language | Match their stack: a TypeScript `const me = {...} as const`, a Python dataclass, a Go struct, and so on. Keep it to facts they gave you. |
| Skill icon grid | many | Stack at a glance | skillicons.dev looks cleaner than a wall of shields badges. Verify every icon ID (see widgets.md). |
| Project cards | leereilly ("Top 10 ships") | 2-column HTML table, one card per project | Each card: name linked to the repo, 1-2 sentences written from the repo's README, stack as `<code>` chips. If a row has one card, use `colspan="2"` so there's no empty cell. |
| Interests / side quests | many | A small table of what they're into outside the job title | Short, honest one-liners. Don't invent specifics. |
| Quest log / roadmap | game-style profiles | `- [x]` / `- [ ]` task list of milestones | Renders as checkboxes in repo READMEs. Only list plans the person is happy to make public. |
| Game mode | rossjrw (Royal Game of Ur), gh-space-shooter, Platane/snk | Interactive or animated contribution graph | gh-space-shooter turns contributions into a space shooter GIF. Use the secure workflow in `assets/space-shooter.yml`. |
| Dark/light images | ouuan | `<picture>` with `prefers-color-scheme` sources | Only needed for images with transparent backgrounds. A banner with its own dark background works on both themes. |

## Theme from the person

Theme the banner *and* the section names around what they love, so the whole
profile feels like theirs, not a template. The banner process is in
banner-design.md. For section names:
- gamers: "Side quests", "Quest log"
- hikers: "Trail log"
- security people: "Recon", "Changelog"
- musicians: "Setlist"
Pixel-art projects can be echoed with pixel fonts and sprites.

Keep emoji to one per heading.

## Content rules

These came from real feedback. Follow them unless the person says otherwise.

- **Ask what to leave out.** People often want only their tech story, not side jobs or unrelated degrees. Ask before including anything non-technical.
- **Never invent facts.** Don't guess their stack, deploy platform, employer, location or years of experience. If something is missing, ask, or leave it out. "Finished a course in 2024" is not "2 years of experience".
- **Describe projects from their actual READMEs and code,** not from repo names. Mark a guess as a guess when you show the draft (e.g. "is pinhole-ai the AI-assisted version?").
- **Planned work is opt-in.** Don't put upcoming projects or applications on a public profile unless they say yes.
- **No raw email address.** Scrapers harvest READMEs. Use a contact page or social link, or nothing.
- **Skip stats cards on young accounts.** github-readme-stats, streaks and trophies make a new account look empty, and the public instances get rate-limited. Suggest them later, once the numbers help.
- **No leftover TODOs.** Placeholder comments end up in a public repo. If a section has no content yet, leave it out.
- **Accessibility:** every image gets real `alt` text, and the banner gets a `<title>`.
