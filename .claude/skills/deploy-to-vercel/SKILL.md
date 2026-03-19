---
name: deploy-to-vercel
description: Deploy projects to Vercel through git push, CLI deploy, or fallback script. Handles linked/unlinked projects, team selection, and preview vs production deployments.
---

# Deploy to Vercel — Agent Guide

This documentation outlines how to deploy projects to Vercel through four primary methods, determined by your project's current state.

## Key Decision Flow

Before choosing a deployment strategy, gather project state by checking:
- Whether a git remote exists
- If the project is linked to Vercel (`.vercel/project.json` or `.vercel/repo.json`)
- Vercel CLI installation and authentication status
- Available teams (if multiple)

## Four Deployment Methods

**1. Linked + Git Remote → Git Push**
This is the ideal long-term setup. After asking for user approval, commit changes and push. Vercel automatically triggers deployments; non-production branches get previews.

**2. Linked + No Git Remote → Direct CLI Deploy**
Use `vercel deploy [path] -y --no-wait` to deploy directly without git integration.

**3. Not Linked + CLI Authenticated → Link First**
Link the project to Vercel (using `vercel link --repo` for git repos or `vercel link` otherwise), then deploy via the appropriate method above.

**4. CLI Not Available → Fallback Script**
In sandboxed environments, use the deployment script at `/mnt/skills/user/deploy-to-vercel/resources/deploy.sh`, which requires no authentication and returns both preview and claim URLs.

## Important Principles

- **Always deploy as preview** unless explicitly requested otherwise
- **Ask before pushing** to avoid unexpected commits
- **Use `--no-wait`** to return immediately with deployment URLs
- **Present team options** as a bulleted list when multiple exist
- **Never use interactive CLI checks** (`vercel ls`, `vercel link`) to detect unlinked state — they trigger side effects

## Output Requirements

Always provide deployment URLs to users. For fallback deployments, show both the preview URL and claim URL for account transfer.
