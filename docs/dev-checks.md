# Developer Checks

This repo is mostly a static website with a small Node MCP server in
`ads/mcp-video` and Python utility scripts. There is no website build step.

Use these checks before committing code changes. The default commands below
are local-only and require no `.env` files, provider credentials, deployment
access, live services, browser automation, or network access.

## Safe Daily Verification

From the repo root:

```bash
cd ads/mcp-video
npm run verify
```

`npm run verify` is the strongest safe default. It runs:

- MCP server JavaScript syntax check
- MCP stdio `tools/list` smoke check, with output redirected to `/private/tmp/thecalltaker-mcp-video-smoke`
- static homepage hero regression test
- Python syntax compilation with pycache redirected to `/private/tmp`

It must stay safe for future Codex lanes: no provider calls, no deployments,
no email/SMS/call/webhook sends, no CRM or provider state mutation, no secret
requirements, and no browser automation that can hang.

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
npm run mcp:smoke
```

The smoke check only asks the MCP server for `tools/list`. It should not call
provider-backed tools such as video generation, status polling against live
providers, email/SMS/call workflows, webhooks, deploys, or state-mutating ops.

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

- Keep `npm run verify` deterministic and local. Do not add checks that depend
  on dirty local files, provider secrets, live services, deployment state, or
  Chrome automation.
- Do not run provider-backed MCP tools during routine verification.
- Do not run deploy workflows from local verification.
- Do not run ops scripts that send email, SMS, calls, ntfy alerts, or mutate CRM/provider state.
- Do not print or commit `.env` values or API keys.
- Keep generated outputs such as `node_modules/`, `__pycache__/`, and `ads/videos/` unstaged.
