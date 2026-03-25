# GitHub Trending Analyzer: Tool Guide

## Overview
The GitHub Trending Analyzer contains two complementary Skills for discovering and analyzing trending repositories on GitHub.

---

## Skill 1: trending-analyzer

### Purpose
Automatically scan GitHub's trending repositories across specified timeframes and languages, generate daily/weekly/monthly summary reports.

### Trigger Method
**Via Skill command**: `/trending-analyzer`

**Parameters**:
- `timeframe`: daily | weekly | monthly (default: daily)
- `language`: optional (e.g., python, javascript, all)
- `limit`: number of repos to include (default: 25)

### Output Format
**File location**: `github-trending-reports/all-{timeframe}-summary-{YYYY-MM-DD}.md`

**Content structure**:
1. Summary metadata (scan date, repo count, trending criteria)
2. Ranked repository list with:
   - Repo name (owner/repo)
   - Star count & trend velocity (⭐/day)
   - Primary language
   - One-line description
3. Top 5 aggregated insights (emerging patterns, technology shifts)
4. Trend analysis (sector growth, language popularity changes)

**Example filename**: `all-daily-summary-2026-03-24.md`

---

## Skill 2: deep-research

### Purpose
Generate comprehensive research reports on individual repositories: codebase analysis, architectural patterns, maintenance health, use cases, community metrics.

### Trigger Method
**Via Skill command**: `/deep-research [owner/repo]`

**Parameters**:
- `repo`: required, format: owner/repo (e.g., anthropic/anthropic-sdk)
- `depth`: light | standard | deep (default: standard)
  - light: basic stats + recent activity
  - standard: architecture, tech stack, contributors, ecosystem
  - deep: code quality metrics, security scan, dependency tree, maintenance trajectory

### Output Format
**File location**: `github-trending-reports/research_{owner}_{repo}.md`

**Content structure**:
1. Repository overview (description, homepage, topics)
2. Metrics snapshot:
   - Stars, forks, watchers (last 30/90/365 days)
   - Open issues, PR velocity
   - Last commit, latest release
3. Technical profile:
   - Primary language, dependencies (count)
   - Coding patterns & architecture highlights
   - Maintenance health score (0–100)
4. Community:
   - Top 10 contributors
   - Issue response time (median)
   - Release cadence
5. Use cases & integrations
6. Risk assessment (deprecated dependencies, security flags)
7. Similar projects (ecosystem neighbors)

**Example filename**: `research_anthropic_anthropic-sdk.md`

---

## Integration Pattern
1. Run `trending-analyzer` daily → generate summary reports
2. Identify promising/interesting repos in summary
3. Run `/deep-research owner/repo` on candidates of interest
4. Aggregate research reports into project decision docs

All outputs stored in `/github-trending-reports/` for indexing and historical trend analysis.
