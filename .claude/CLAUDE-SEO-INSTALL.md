# claude-seo — project-level install

[claude-seo](https://github.com/AgriciDaniel/claude-seo) v2.2.4 by AgriciDaniel (MIT),
installed into this repository's `.claude/` directory so it is available to every
Claude Code session on this repo.

## Why it's vendored instead of `/plugin install`

`/plugin` is unavailable in the Claude Code remote/web environment, and the
container is ephemeral — a `~/.claude` install would not survive. Committing the
skills and agents under `.claude/` makes them load automatically at session start.

## Layout

The upstream `install.sh` manual-install layout, rooted at `.claude/` instead of
`$HOME/.claude`:

| Path | Contents |
|------|----------|
| `.claude/skills/seo/` | Orchestrator skill + bundled runtime (`bin/`, `scripts/`, `schema/`, `pdf/`, `data/`, `hooks/`, `extensions/`) |
| `.claude/skills/seo-*/` | 30 sub-skills (24 core + 6 extension mirrors) |
| `.claude/agents/` | 18 SEO sub-agents |
| `.claude/settings.json` | `PostToolUse` hook running the JSON-LD schema validator on Edit/Write |

## Usage

Skills are user-invocable, e.g. `/seo audit https://example.com`, `/seo-page <url>`,
`/seo-schema`. Agents are delegated to automatically by `/seo audit`.

## Python runtime

Bundled Python tools must run through the managed launcher, never a bare
interpreter:

```
./.claude/skills/seo/bin/claude-seo doctor     # diagnose
./.claude/skills/seo/bin/claude-seo setup      # create the managed venv (needs network)
./.claude/skills/seo/bin/claude-seo run <script.py>
```

The launcher self-locates and stores its virtualenv outside the repo (under
`$XDG_DATA_HOME`), so nothing it creates gets committed. `setup` has not been run
here — run it in any session that needs the Python-backed checks (fetching,
rendering, PageSpeed, backlinks). Skills that only reason over content work
without it.

Docs in this install have had the bare `claude-seo` command rewritten to the
launcher path above, matching what upstream's manual installer does for `$HOME`.

## Updating

Replace the trees above from a fresh upstream checkout and re-apply the same
command rewrite. Nothing in this install is modified beyond that rewrite, so it
diffs cleanly against upstream.
