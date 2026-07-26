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

The launcher self-locates. In `manual` install mode — which this is — it resolves
its data dir to the **skill root itself**, so `setup` writes all of the following
*inside* the repo:

| Generated path | Size | Purpose |
|---|---|---|
| `.claude/skills/seo/.venv/` | ~800 MB | isolated Python environment |
| `.claude/skills/seo/ms-playwright/` | varies | Playwright browser cache |
| `.claude/skills/seo/runtime-state.json` | tiny | setup state |

All three are per-machine build output and are gitignored in `.claude/.gitignore`.
Re-run `setup` in each new container; never commit them.

Skills that only reason over content work without `setup`. The Python-backed
checks (fetching, PageSpeed, backlinks, sitemaps) need the core runtime.

### Chromium / rendered-page features

Rendered-mode features (SPA rendering, screenshots, the `seo-visual` agent) need
Chromium, which is **not available in the Claude Code remote environment**:

- The network policy rejects `cdn.playwright.dev` (`403 host not permitted`), so
  `playwright install chromium` cannot download it.
- The environment pre-installs Chromium 141 at `/opt/pw-browsers`
  (Playwright build 1194), but that pairs only with `playwright==1.56.0`.
- `requirements.txt` pins `playwright>=1.59.0` for the CVE-2025-59288 fix, and no
  version at or above 1.59.0 ships build 1194 (1.59.0→1217, 1.60.0→1223,
  1.61.0→1228).

So the pinned runtime and the available browser cannot be reconciled without
either allowing `cdn.playwright.dev` in the environment's network policy (the
clean fix) or downgrading below the CVE pin. `render_page.py` degrades with a
clear error rather than crashing, and static-fetch analysis is unaffected.

Docs in this install have had the bare `claude-seo` command rewritten to the
launcher path above, matching what upstream's manual installer does for `$HOME`.

## Updating

Replace the trees above from a fresh upstream checkout and re-apply the same
command rewrite. Nothing in this install is modified beyond that rewrite, so it
diffs cleanly against upstream.
