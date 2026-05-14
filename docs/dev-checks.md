# Developer Checks

This repo is mostly a static website with a small Node MCP server in
`ads/mcp-video` and Python utility scripts. There is no website build step.

Use these checks before committing code changes. They are local-only and do
not deploy, send messages, call providers, or require secrets.

## Safe Daily Verification

From the repo root:

```bash
cd ads/mcp-video
npm run verify
```

`npm run verify` runs:

- MCP server JavaScript syntax check
- MCP stdio `tools/list` smoke check
- static homepage hero regression test
- Python syntax compilation with pycache redirected to `/private/tmp`

## Individual Commands

Run the MCP package checks from `ads/mcp-video`:

```bash
npm test
npm run check
```

Run the full safe verifier from `ads/mcp-video`:

```bash
npm run verify
```

Run the static hero regression from the repo root:

```bash
python3 website/tests/hero-regression.py
```

Run Python syntax compilation from the repo root:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/thecalltaker-pycache python3 -m compileall -q ops max ben sam water-damage netlify tools website/scripts *.py
```

Run the MCP stdio smoke check from `ads/mcp-video`:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | TCT_VIDEO_OUTPUT_DIR=/private/tmp/thecalltaker-mcp-video-smoke node server.js
```

## Optional Checks

The hero regression has an optional live Chrome layer:

```bash
python3 website/tests/hero-regression.py --live --url http://localhost:8765
```

Do not include the live Chrome layer in default verification. It depends on a
local browser and can skip viewport extraction even when static checks pass.

`npm audit` is useful before dependency changes, but it reaches the npm
registry, so it is not part of the default verifier:

```bash
cd ads/mcp-video
npm audit --audit-level=moderate
```

## Safety Rules

- Do not run provider-backed MCP tools during routine verification.
- Do not run deploy workflows from local verification.
- Do not run ops scripts that send email, SMS, calls, ntfy alerts, or mutate CRM/provider state.
- Do not print or commit `.env` values or API keys.
- Keep generated outputs such as `node_modules/`, `__pycache__/`, and `ads/videos/` unstaged.
