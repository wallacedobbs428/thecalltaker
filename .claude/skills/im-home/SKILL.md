---
name: im-home
description: "Run when Wallace gets home to his Mac. Sets up Meta ads credentials, launches the roofing campaign, installs the daily report service, and runs a full system health check. Use when Wallace says 'I'm home' or 'home' or 'back on mac'."
allowed-tools: Read, Write, Bash, Glob, Grep
---

# I'm Home — Deploy Everything That Was Built Remotely

Wallace just got home to the Mac. Time to deploy everything that was staged during the remote session.

## Step 1: Run the Meta Setup Wizard

```bash
python3 ~/thecalltaker-ops/ops/meta-setup-wizard.py
```

This will:
- Open Facebook Developers in the browser automatically
- Walk through getting META_ACCESS_TOKEN + META_AD_ACCOUNT_ID step by step
- Validate both credentials format (EAA token, numeric account ID)
- Test the Meta API connection with a real call
- Write credentials to `~/.zshrc`, `~/.bashrc`, and `~/thecalltaker-ops/.env`
- Set them live in the current environment

If credentials are already set and valid, it skips straight to confirmation.

## Step 2: Launch the Roofing Ad Campaign

Once credentials are confirmed, run `/ads-launch roofing` to build the full campaign via Meta Marketing API:

- Campaign: "TCT - Roofing - Lead Gen" ($5/day, PAUSED)
- Ad Set: US roofing owners, age 25-65, small business behaviors
- Ad 1: "Storm Season. Missed Calls. Lost Jobs."
- Ad 2: "$97/Mo Beats Your $800 Receptionist"
- Ad 3: "That 2AM Call Was a $15,000 Roof Job"
- Lead Form: 5 questions → Thank You → Call Demo Line (615) 784-5747

ALL ADS START PAUSED. Show the full campaign structure and wait for explicit "launch" confirmation before activating anything.

## Step 3: Install the Daily Ad Report Service

```bash
# Copy the launchd plist to LaunchAgents
cp ~/thecalltaker-ops/ops/com.thecalltaker.ads-daily-report.plist \
   ~/Library/LaunchAgents/com.thecalltaker.ads-daily-report.plist

# Load it
launchctl load ~/Library/LaunchAgents/com.thecalltaker.ads-daily-report.plist
```

This fires every day at 9:00 AM:
- Pulls Meta API performance for all active campaigns
- Compares against CPL benchmarks (roofing: $22 target, $44 kill)
- Generates kill/hold/scale recommendations
- Sends results to ntfy SALES topic
- Saves report to `~/thecalltaker-ops/ads/reports/`

## Step 4: Run Full Health Check

```bash
python3 ~/thecalltaker-ops/ops/ads-health-check.py
```

Verify all systems green:
- META_ACCESS_TOKEN: SET
- META_AD_ACCOUNT_ID: SET
- API Connection: LIVE
- All 6 /ads-* skills: READY
- All roofing campaign files: EXISTS
- Daily report service: LOADED

## Step 5: Report Results

Print a summary of everything deployed:
- Credentials status
- Campaign IDs captured
- Ads created (with headlines)
- launchd service status
- Any remaining blockers

If any step fails, explain exactly what went wrong and how to fix it.
