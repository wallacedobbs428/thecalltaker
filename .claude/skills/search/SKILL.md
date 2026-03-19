---
name: search
description: "Perform deep web research and information gathering. Use when researching competitors, market data, industry trends, pricing intelligence, technology comparisons, or gathering data for business decisions. Covers search strategies, source evaluation, data synthesis, and competitive intelligence."
category: research
---

# Search — Deep Research Skill

Systematic approach to gathering, evaluating, and synthesizing information from the web.

---

## Research Framework

### Step 1: Define the Question
Before searching, write down:
- **What specifically do I need to know?**
- **What will I do with this information?**
- **What format should the output be in?**

### Step 2: Search Strategy
Use multiple query formulations:

```
Primary query:    [exact topic]
Comparison query: [topic] vs [alternative]
Review query:     [topic] review 2026
Pricing query:    [topic] pricing plans cost
Problem query:    [topic] problems issues complaints
```

### Step 3: Evaluate Sources
| Source Type | Reliability | Use For |
|------------|------------|---------|
| Company website | Medium (biased) | Official features, pricing |
| G2/Capterra reviews | High | Real user experiences |
| Reddit/forums | Medium | Unfiltered opinions |
| Industry reports | High | Market data, trends |
| Blog posts | Low-Medium | Analysis, how-tos |
| News articles | Medium-High | Recent events, funding |

### Step 4: Synthesize
- Cross-reference claims across 3+ sources
- Note conflicting information
- Distinguish facts from opinions
- Date-stamp everything (info expires)

---

## Competitive Intelligence Template

```markdown
## Competitor: [Company Name]

**URL:** [website]
**Founded:** [year]
**Funding:** [amount/stage]
**Team size:** [estimate]

### Product
- **What they do:** [1-2 sentences]
- **Target market:** [who they sell to]
- **Key features:** [bullet list]
- **Missing features:** [what they DON'T do]

### Pricing
| Plan | Price | What's Included |
|------|-------|----------------|
| [Plan 1] | $X/mo | [features] |
| [Plan 2] | $X/mo | [features] |

### Strengths
- [What they do well]

### Weaknesses
- [Where they fall short]
- [Common complaints from reviews]

### How We Win Against Them
- [Our advantage 1]
- [Our advantage 2]
```

---

## Market Research Template

```markdown
## Market: [Industry/Niche]

### Market Size
- TAM: [Total Addressable Market]
- SAM: [Serviceable Addressable Market]
- SOM: [Serviceable Obtainable Market]

### Key Players
| Company | Market Share | Pricing | Differentiation |
|---------|-------------|---------|-----------------|

### Trends
- [Trend 1 with data]
- [Trend 2 with data]

### Customer Pain Points
1. [Pain point + evidence]
2. [Pain point + evidence]

### Opportunities
- [Underserved segment]
- [Emerging need]
```

---

## Search Query Techniques

### For Business Research
```
"answering service" HVAC pricing 2026
site:g2.com "answering service" review
"smith.ai" OR "ruby receptionists" pricing
"AI receptionist" -"call center" startup
```

### For Technical Research
```
"GHL API" "voice AI" integration guide
python asyncio "rate limiting" best practices
"GitHub Actions" deploy "GitHub Pages" workflow
```

### For Lead Research
```
"[company name]" "[city]" [industry] phone
site:yelp.com "[company name]" reviews
site:bbb.org "[company name]" complaints
```

---

## Output Formats

### Quick Summary (for Slack/ntfy)
```
[Company] — $X/mo, does [feature], weak on [gap]. We win on [advantage].
```

### Decision Brief (for strategy)
```markdown
## Decision: [Question]

### Options
1. **Option A:** [Description] — Pros: [X]. Cons: [Y].
2. **Option B:** [Description] — Pros: [X]. Cons: [Y].

### Recommendation
[Option X] because [evidence-based reason].

### Sources
- [URL 1] — [what it confirmed]
- [URL 2] — [what it confirmed]
```

### Data Table (for comparison)
```markdown
| Criteria | Us | Competitor A | Competitor B |
|----------|-----|-------------|-------------|
| Price | $97/mo | $300/mo | $200/mo |
| 24/7 | Yes | Yes | No |
| AI-powered | Yes | No | Partial |
| Setup time | Same day | 1-2 weeks | 3-5 days |
```
