# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is a GitHub **profile README** repository (`SVADEZI/svadezi` — the repo name matches the user, which is what makes it special). The sole purpose of this repo is that its `README.md` is rendered at the top of the user's GitHub profile page at https://github.com/SVADEZI.

There is no application code, no build system, no tests, and no CI. The entire deliverable is `README.md`.

## Working in this repo

- Edits should target `README.md` unless the user explicitly asks for something else.
- The current `README.md` is the default GitHub template with the body commented out (`<!-- ... -->`). Uncomment / replace content rather than appending below the comment, so the template hints don't end up shipping to the profile page.
- GitHub-flavored Markdown is rendered. HTML is permitted (used for things like centered images, profile stats cards, badges) — GitHub sanitizes it, so `<script>` and most attributes are stripped.
- Emoji shortcodes (`:wave:`) render on GitHub profiles. Only add emoji if the user asks for them.
- Relative image/file links resolve against this repo, so any assets referenced should be committed here (or use absolute URLs to external services like shields.io).

## Verifying changes

There is nothing to build or test. To sanity-check Markdown rendering before pushing, paste the file into the GitHub web editor preview, or render locally with any Markdown previewer. After pushing to `main`, the profile page updates within seconds.

## Branching

Per the task instructions for this session, development happens on `claude/add-claude-documentation-tcF1u`. Commit and push there; do not push to `main` without explicit permission.
