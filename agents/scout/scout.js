#!/usr/bin/env node
// ============================================================
// SCOUT — Business Intelligence Researcher
// Researches a target business: reviews, reputation, team size,
// hours, website quality, social presence, pain signals.
// Outputs structured intel to intelligence/contacts/<id>.json
// ============================================================

const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// ── CONFIG ──────────────────────────────────────────────────
const REPO_DIR = path.resolve(__dirname, "../..");
const INTEL_DIR = path.join(REPO_DIR, "intelligence/contacts");
const INTEL_INDEX = path.join(REPO_DIR, "intelligence/intelligence.json");
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY || "";
const MODEL = "claude-sonnet-4-20250514";
const MAX_TOKENS = 4096;

// ── HELPERS ─────────────────────────────────────────────────

function log(msg) {
  const ts = new Date().toISOString().replace("T", " ").slice(0, 19);
  console.log(`[${ts}] SCOUT: ${msg}`);
}

function slugify(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function httpGet(url, maxRedirects = 3) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith("https") ? https : http;
    const req = client.get(url, { timeout: 15000, headers: { "User-Agent": "Mozilla/5.0 (compatible; TCTScout/1.0)" } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && maxRedirects > 0) {
        let redirectUrl = res.headers.location;
        if (redirectUrl.startsWith("/")) {
          const u = new URL(url);
          redirectUrl = `${u.protocol}//${u.host}${redirectUrl}`;
        }
        return httpGet(redirectUrl, maxRedirects - 1).then(resolve).catch(reject);
      }
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => resolve({ status: res.statusCode, body: data.slice(0, 50000) }));
    });
    req.on("error", (err) => reject(err));
    req.on("timeout", () => { req.destroy(); reject(new Error("timeout")); });
  });
}

function callAnthropic(systemPrompt, userMsg) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: systemPrompt,
      messages: [{ role: "user", content: userMsg }],
    });

    const req = https.request(
      {
        hostname: "api.anthropic.com",
        path: "/v1/messages",
        method: "POST",
        timeout: 120000,
        headers: {
          "x-api-key": ANTHROPIC_API_KEY,
          "anthropic-version": "2023-06-01",
          "content-type": "application/json",
          "content-length": Buffer.byteLength(body),
        },
      },
      (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            const parsed = JSON.parse(data);
            if (parsed.content && parsed.content.length > 0) {
              resolve(parsed.content[0].text);
            } else if (parsed.error) {
              reject(new Error(`API error: ${parsed.error.message}`));
            } else {
              reject(new Error("Unexpected API response"));
            }
          } catch (e) {
            reject(new Error(`Parse error: ${e.message}`));
          }
        });
      }
    );
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(); reject(new Error("API timeout")); });
    req.write(body);
    req.end();
  });
}

// ── RESEARCH FUNCTIONS ──────────────────────────────────────

async function searchBing(query) {
  try {
    const encoded = encodeURIComponent(query);
    const res = await httpGet(`https://www.bing.com/search?q=${encoded}&count=10`);
    if (res.status !== 200) return [];

    const results = [];
    const linkRegex = /<a[^>]+href="(https?:\/\/[^"]+)"[^>]*>(.*?)<\/a>/gi;
    let match;
    while ((match = linkRegex.exec(res.body)) !== null) {
      const url = match[1];
      if (!url.includes("bing.com") && !url.includes("microsoft.com") && !url.includes("go.microsoft")) {
        const title = match[2].replace(/<[^>]+>/g, "").trim();
        if (title.length > 3) {
          results.push({ url, title });
        }
      }
    }
    return results.slice(0, 8);
  } catch (e) {
    log(`Bing search failed: ${e.message}`);
    return [];
  }
}

async function searchDDG(query) {
  try {
    const encoded = encodeURIComponent(query);
    const res = await httpGet(`https://html.duckduckgo.com/html/?q=${encoded}`);
    if (res.status !== 200) return [];

    const results = [];
    const linkRegex = /class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)<\/a>/gi;
    let match;
    while ((match = linkRegex.exec(res.body)) !== null) {
      let url = match[1];
      if (url.includes("uddg=")) {
        try { url = decodeURIComponent(url.split("uddg=")[1].split("&")[0]); } catch (_) {}
      }
      const title = match[2].replace(/<[^>]+>/g, "").trim();
      if (title.length > 3 && url.startsWith("http")) {
        results.push({ url, title });
      }
    }

    // Also grab snippets
    const snippetRegex = /class="result__snippet"[^>]*>(.*?)<\/(?:a|td|div|span)/gis;
    let i = 0;
    while ((match = snippetRegex.exec(res.body)) !== null && i < results.length) {
      results[i].snippet = match[1].replace(/<[^>]+>/g, "").trim().slice(0, 300);
      i++;
    }

    return results.slice(0, 8);
  } catch (e) {
    log(`DDG search failed: ${e.message}`);
    return [];
  }
}

async function scrapeWebsite(url) {
  try {
    const res = await httpGet(url);
    if (res.status !== 200) return null;

    const html = res.body;

    // Extract useful data from HTML
    const titleMatch = html.match(/<title[^>]*>(.*?)<\/title>/is);
    const metaDescMatch = html.match(/<meta[^>]+name=["']description["'][^>]+content=["'](.*?)["']/is);
    const phoneRegex = /(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}/g;
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;

    // JSON-LD structured data
    const jsonLdMatches = html.match(/<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi) || [];
    const structuredData = [];
    for (const block of jsonLdMatches) {
      const jsonContent = block.replace(/<\/?script[^>]*>/gi, "").trim();
      try {
        structuredData.push(JSON.parse(jsonContent));
      } catch (_) {}
    }

    // Strip HTML for text content
    const text = html
      .replace(/<script[\s\S]*?<\/script>/gi, "")
      .replace(/<style[\s\S]*?<\/style>/gi, "")
      .replace(/<[^>]+>/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 5000);

    return {
      title: titleMatch ? titleMatch[1].trim() : null,
      description: metaDescMatch ? metaDescMatch[1].trim() : null,
      phones: [...new Set((html.match(phoneRegex) || []).map((p) => p.trim()))].slice(0, 5),
      emails: [...new Set((html.match(emailRegex) || []).filter((e) => !e.includes("@example") && !e.includes("@sentry")))].slice(0, 5),
      structuredData,
      textPreview: text.slice(0, 3000),
      hasSSL: url.startsWith("https"),
      url,
    };
  } catch (e) {
    log(`Scrape failed for ${url}: ${e.message}`);
    return null;
  }
}

async function findReviews(businessName, location) {
  const query = `"${businessName}" ${location || ""} reviews`;
  const ddgResults = await searchDDG(query);
  const reviewSources = [];

  for (const r of ddgResults) {
    const isReviewSite =
      r.url.includes("google.com/maps") ||
      r.url.includes("yelp.com") ||
      r.url.includes("bbb.org") ||
      r.url.includes("facebook.com") ||
      r.url.includes("angieslist") ||
      r.url.includes("homeadvisor") ||
      r.url.includes("thumbtack") ||
      r.url.includes("nextdoor");

    if (isReviewSite || (r.snippet && /\d+(\.\d+)?\s*(star|rating|review)/i.test(r.snippet))) {
      // Try to extract rating from snippet
      const ratingMatch = r.snippet ? r.snippet.match(/(\d+(?:\.\d+)?)\s*(?:star|\/\s*5|rating)/i) : null;
      const countMatch = r.snippet ? r.snippet.match(/(\d+)\s*review/i) : null;

      reviewSources.push({
        source: new URL(r.url).hostname.replace("www.", ""),
        url: r.url,
        rating: ratingMatch ? parseFloat(ratingMatch[1]) : null,
        reviewCount: countMatch ? parseInt(countMatch[1]) : null,
        snippet: r.snippet || "",
      });
    }
  }

  return reviewSources;
}

// ── MAIN SCOUT FUNCTION ─────────────────────────────────────

async function scoutBusiness(businessName, options = {}) {
  const { location, phone, website, industry } = options;
  const slug = slugify(businessName);
  const outputFile = path.join(INTEL_DIR, `${slug}.json`);

  log(`Scouting: ${businessName}`);
  log(`  Location: ${location || "unknown"}`);
  log(`  Industry: ${industry || "unknown"}`);
  log(`  Phone: ${phone || "unknown"}`);
  log(`  Website: ${website || "will search"}`);

  // Phase 1: Web search
  log("Phase 1: Web search");
  const searchQuery = `"${businessName}" ${location || ""} ${industry || ""}`;
  const [bingResults, ddgResults] = await Promise.all([
    searchBing(searchQuery),
    searchDDG(searchQuery),
  ]);

  // Merge and deduplicate results
  const allResults = [...bingResults];
  for (const r of ddgResults) {
    if (!allResults.some((a) => a.url === r.url)) {
      allResults.push(r);
    }
  }
  log(`  Found ${allResults.length} search results`);

  // Phase 2: Find & scrape website
  log("Phase 2: Website scrape");
  let websiteUrl = website;
  if (!websiteUrl && allResults.length > 0) {
    // Find the most likely company website
    const companyResult = allResults.find(
      (r) =>
        !r.url.includes("yelp.com") &&
        !r.url.includes("facebook.com") &&
        !r.url.includes("bbb.org") &&
        !r.url.includes("google.com") &&
        !r.url.includes("yellowpages")
    );
    if (companyResult) websiteUrl = companyResult.url;
  }

  let websiteData = null;
  if (websiteUrl) {
    websiteData = await scrapeWebsite(websiteUrl);
    if (websiteData) {
      log(`  Scraped: ${websiteData.title || websiteUrl}`);
    }
  }

  // Phase 3: Reviews
  log("Phase 3: Review research");
  const reviews = await findReviews(businessName, location);
  log(`  Found ${reviews.length} review sources`);

  // Phase 4: Social presence check
  log("Phase 4: Social presence");
  const socialQuery = `"${businessName}" site:facebook.com OR site:instagram.com OR site:linkedin.com`;
  const socialResults = await searchDDG(socialQuery);
  const socialPresence = socialResults.map((r) => ({
    platform: new URL(r.url).hostname.replace("www.", ""),
    url: r.url,
    snippet: r.snippet || "",
  }));

  // Phase 5: Analyze with Claude
  log("Phase 5: AI analysis");
  let aiAnalysis = null;

  if (ANTHROPIC_API_KEY) {
    const systemPrompt = `You are SCOUT — a business intelligence analyst for The Call Taker, an AI receptionist SaaS ($97-$497/mo). Your job is to research a business and produce actionable intel that helps our sales team close them.

Output ONLY valid JSON (no markdown, no backticks). Use this exact schema:
{
  "summary": "2-3 sentence business overview",
  "pain_signals": ["list of pain points that suggest they need an AI receptionist"],
  "opportunity_score": 1-10,
  "opportunity_reasons": ["why they're a good/bad fit"],
  "team_size_estimate": "solo/small (2-5)/medium (6-15)/large (15+)",
  "hours_of_operation": "best guess from data",
  "services_offered": ["list"],
  "website_quality": "none/poor/average/good/excellent",
  "online_reputation": "poor/mixed/good/excellent",
  "avg_rating": null or number,
  "total_reviews": null or number,
  "social_presence": "none/minimal/active/strong",
  "call_handling_guess": "owner answers/receptionist/voicemail/answering service/unknown",
  "recommended_plan": "$97 After-Hours/$297 Full Coverage/$497 Premium",
  "recommended_approach": "cold call/email/demo link/referral",
  "opening_line": "personalized cold outreach opener for this specific business",
  "objection_prediction": "most likely objection and pre-handle",
  "revenue_potential": "estimated monthly value of missed calls for this business"
}`;

    const rawData = {
      businessName,
      location,
      phone,
      industry,
      searchResults: allResults.slice(0, 5).map((r) => ({ title: r.title, url: r.url, snippet: r.snippet })),
      website: websiteData
        ? {
            title: websiteData.title,
            description: websiteData.description,
            phones: websiteData.phones,
            emails: websiteData.emails,
            hasSSL: websiteData.hasSSL,
            textPreview: websiteData.textPreview.slice(0, 2000),
            structuredData: websiteData.structuredData,
          }
        : null,
      reviews,
      socialPresence,
    };

    try {
      const analysisText = await callAnthropic(systemPrompt, JSON.stringify(rawData));
      // Try to parse — handle potential markdown wrapping
      let cleanText = analysisText.trim();
      if (cleanText.startsWith("```")) {
        cleanText = cleanText.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "");
      }
      aiAnalysis = JSON.parse(cleanText);
      log(`  Opportunity score: ${aiAnalysis.opportunity_score}/10`);
    } catch (e) {
      log(`  AI analysis failed: ${e.message}`);
    }
  } else {
    log("  Skipped (no ANTHROPIC_API_KEY)");
  }

  // Phase 6: Assemble intel dossier
  log("Phase 6: Assembling dossier");

  const dossier = {
    id: slug,
    business_name: businessName,
    location: location || null,
    phone: phone || (websiteData && websiteData.phones[0]) || null,
    email: (websiteData && websiteData.emails[0]) || null,
    website: websiteUrl || null,
    industry: industry || null,
    scouted_at: new Date().toISOString(),
    search_results_count: allResults.length,
    website_data: websiteData
      ? {
          title: websiteData.title,
          description: websiteData.description,
          phones: websiteData.phones,
          emails: websiteData.emails,
          has_ssl: websiteData.hasSSL,
        }
      : null,
    reviews,
    social_presence: socialPresence,
    ai_analysis: aiAnalysis,
    raw_search_results: allResults.slice(0, 5),
  };

  // Write to file
  fs.mkdirSync(INTEL_DIR, { recursive: true });
  fs.writeFileSync(outputFile, JSON.stringify(dossier, null, 2));
  log(`Dossier saved: ${outputFile}`);

  // Update intelligence index
  updateIntelIndex(dossier);

  return dossier;
}

// ── INTELLIGENCE INDEX ──────────────────────────────────────

function updateIntelIndex(dossier) {
  let index = { contacts: [], last_updated: null };

  if (fs.existsSync(INTEL_INDEX)) {
    try {
      index = JSON.parse(fs.readFileSync(INTEL_INDEX, "utf8"));
    } catch (_) {}
  }

  // Update or add entry
  const existing = index.contacts.findIndex((c) => c.id === dossier.id);
  const entry = {
    id: dossier.id,
    business_name: dossier.business_name,
    location: dossier.location,
    industry: dossier.industry,
    opportunity_score: dossier.ai_analysis ? dossier.ai_analysis.opportunity_score : null,
    phone: dossier.phone,
    email: dossier.email,
    website: dossier.website,
    scouted_at: dossier.scouted_at,
  };

  if (existing >= 0) {
    index.contacts[existing] = entry;
  } else {
    index.contacts.push(entry);
  }

  index.last_updated = new Date().toISOString();
  index.total = index.contacts.length;

  fs.mkdirSync(path.dirname(INTEL_INDEX), { recursive: true });
  fs.writeFileSync(INTEL_INDEX, JSON.stringify(index, null, 2));
  log(`Intelligence index updated (${index.total} contacts)`);
}

// ── PRINT REPORT ────────────────────────────────────────────

function printReport(dossier) {
  console.log("\n" + "=".repeat(60));
  console.log(`SCOUT REPORT: ${dossier.business_name}`);
  console.log("=".repeat(60));
  console.log(`Location:  ${dossier.location || "unknown"}`);
  console.log(`Industry:  ${dossier.industry || "unknown"}`);
  console.log(`Phone:     ${dossier.phone || "not found"}`);
  console.log(`Email:     ${dossier.email || "not found"}`);
  console.log(`Website:   ${dossier.website || "not found"}`);
  console.log(`Scouted:   ${dossier.scouted_at}`);

  if (dossier.reviews.length > 0) {
    console.log("\nREVIEWS:");
    for (const r of dossier.reviews) {
      const rating = r.rating ? `${r.rating}/5` : "?";
      const count = r.reviewCount ? `(${r.reviewCount} reviews)` : "";
      console.log(`  ${r.source}: ${rating} ${count}`);
    }
  }

  if (dossier.social_presence.length > 0) {
    console.log("\nSOCIAL:");
    for (const s of dossier.social_presence) {
      console.log(`  ${s.platform}: ${s.url}`);
    }
  }

  if (dossier.ai_analysis) {
    const a = dossier.ai_analysis;
    console.log("\nAI ANALYSIS:");
    console.log(`  Opportunity Score: ${a.opportunity_score}/10`);
    console.log(`  Team Size:        ${a.team_size_estimate}`);
    console.log(`  Website Quality:  ${a.website_quality}`);
    console.log(`  Reputation:       ${a.online_reputation}`);
    console.log(`  Call Handling:     ${a.call_handling_guess}`);
    console.log(`  Recommended Plan: ${a.recommended_plan}`);
    console.log(`  Revenue Potential: ${a.revenue_potential}`);

    if (a.pain_signals && a.pain_signals.length > 0) {
      console.log("\n  PAIN SIGNALS:");
      for (const p of a.pain_signals) {
        console.log(`    - ${p}`);
      }
    }

    console.log(`\n  OPENING LINE: "${a.opening_line}"`);
    console.log(`  OBJECTION: ${a.objection_prediction}`);
  }

  console.log("\n" + "=".repeat(60));
}

// ── CLI ─────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes("--help")) {
    console.log(`
SCOUT — Business Intelligence Researcher for The Call Taker

Usage:
  node scout.js <business-name> [options]
  node scout.js --test

Options:
  --location <city, state>   Business location
  --phone <number>           Business phone number
  --website <url>            Business website
  --industry <type>          Industry (hvac, plumbing, dental, etc.)
  --test                     Run test with Carolina Locksmith

Examples:
  node scout.js "Carolina Locksmith" --location "Charlotte, NC" --industry locksmith
  node scout.js "Arctic Air HVAC" --location "Nashville, TN" --industry hvac
  node scout.js --test
`);
    return;
  }

  if (args.includes("--test")) {
    log("Running test: Carolina Locksmith");
    const dossier = await scoutBusiness("Carolina Locksmith", {
      location: "Charlotte, NC",
      industry: "locksmith",
    });
    printReport(dossier);
    return;
  }

  // Parse args
  const businessName = args[0];
  const options = {};

  for (let i = 1; i < args.length; i++) {
    if (args[i] === "--location" && args[i + 1]) { options.location = args[++i]; }
    else if (args[i] === "--phone" && args[i + 1]) { options.phone = args[++i]; }
    else if (args[i] === "--website" && args[i + 1]) { options.website = args[++i]; }
    else if (args[i] === "--industry" && args[i + 1]) { options.industry = args[++i]; }
  }

  const dossier = await scoutBusiness(businessName, options);
  printReport(dossier);
}

main().catch((e) => {
  log(`FATAL: ${e.message}`);
  process.exit(1);
});
