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
