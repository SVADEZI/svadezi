# Chatplace MCP Setup

This repo registers the [Chatplace](https://app.chatplace.io) MCP server for Claude Code via [`.mcp.json`](./.mcp.json).

| Field | Value |
| --- | --- |
| Transport | `http` |
| Endpoint | `https://mcp.chatplace.io/mcp` |
| Auth | `Authorization: Bearer <CHATPLACE_API_KEY>` |

## Provide your API key

The key is **not** stored in the repo. `.mcp.json` reads it from the
`CHATPLACE_API_KEY` environment variable at launch time.

1. Copy the example env file and add your real key:
   ```sh
   cp .env.example .env
   # then edit .env and set CHATPLACE_API_KEY=cpk_...
   ```
2. Export it into your shell before starting Claude Code:
   ```sh
   export CHATPLACE_API_KEY="cpk_your_api_key_here"
   ```
   (or use a tool like `direnv` / `dotenv` to load `.env` automatically).

3. Start Claude Code in this directory. It will pick up the `chatplace`
   server from `.mcp.json` and substitute `${CHATPLACE_API_KEY}`.

> Your API key is a secret. Keep it in `.env` (gitignored) or your shell
> environment — never commit it.

## Alternative: add via CLI

```sh
claude mcp add --transport http --scope project chatplace https://mcp.chatplace.io/mcp \
  --header "Authorization: Bearer $CHATPLACE_API_KEY"
```

## Network egress (Claude Code on the web)

If you run this in a **remote/web Claude Code session**, outbound traffic is
governed by the environment's network egress allowlist. By default
`mcp.chatplace.io` is **not** allowlisted, so the connection is blocked at the
firewall before it reaches Chatplace:

```
HTTP/2 403  x-deny-reason: host_not_allowed
Host not in allowlist: mcp.chatplace.io. Add this host to your network egress settings to allow access.
```

To use the MCP from a web session, add these hosts to the environment's egress
allowlist, then start a fresh session:

- `mcp.chatplace.io` — the MCP endpoint
- `app.chatplace.io` — Chatplace app/auth (may be needed by the account flow)

See the network policy docs:
<https://code.claude.com/docs/en/claude-code-on-the-web>

Running Claude Code **locally** has no such restriction.

## What you can do once connected

The Chatplace MCP connector covers automations/funnels, keyword chatbots,
**audience analytics**, AI Agent training, and content creation. To analyze an
Instagram account, the account must first be **connected inside Chatplace**
(the AI trains on it); then ask Claude to analyze the audience and the MCP
tools will pull the data.
