---
name: create-auth-skill
description: "Add authentication to TypeScript/JavaScript applications using Better Auth. Use when setting up login, OAuth, passkeys, 2FA, or auth in Next.js, Express, SvelteKit, or Nuxt projects."
---

# Create Auth Skill — Better Auth

Add authentication to TypeScript/JavaScript applications using Better Auth.

## Phase 1: Planning (Required First)

Before implementing:

1. **Scan your project** to auto-detect framework, database/ORM, existing auth libraries, and package manager
2. **Ask planning questions** covering: project type, framework, database setup, authentication methods, social providers, email handling, features, pages needed, and UI style
3. **Summarize the plan** as a checklist and get user confirmation before proceeding

Skip questions where you already have confident answers from your scan.

## Phase 2: Implementation

Only start after plan confirmation. Follow the decision tree based on whether this is a new project, adding to an existing one, or migrating from another auth library.

## Key Setup Steps

**Installation:**
```bash
npm install better-auth
```
Plus optional scoped packages: `@better-auth/passkey`, `@better-auth/sso`, etc.

**Server config** goes in `lib/auth.ts` with database adapter, email/password settings, OAuth providers, and plugins.

**Client config** goes in `lib/auth-client.ts` using framework-specific imports (React, Vue, Svelte, Solid, or vanilla JS).

**Route handlers** vary by framework — Next.js App Router uses `app/api/auth/[...all]/route.ts`, while Express uses middleware at `/api/auth/*`.

**Database migrations** depend on adapter: Kysely runs directly, Prisma requires `prisma migrate dev`, Drizzle requires `drizzle-kit push`.

## Required Environment Variables

- `BETTER_AUTH_SECRET` (32+ characters)
- `BETTER_AUTH_URL` (your app URL)
- `DATABASE_URL` (your database connection)
- OAuth credentials as needed (GITHUB_CLIENT_ID, GOOGLE_CLIENT_ID, etc.)

## Common Plugins

- `twoFactor` — 2FA/TOTP
- `organization` — Teams
- `admin` — User management
- `bearer` — API tokens
- `passkey` — WebAuthn

## Documentation

[better-auth.com/docs](https://better-auth.com/docs)
