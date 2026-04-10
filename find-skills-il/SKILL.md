---
name: find-skills-il
description: >-
  Find and compare Skills IL entries. Use when user asks to find a skill, search
  the Skills IL registry, filter by category, agent, tag, creator, or page, or
  inspect a skill before install. Do NOT use for general web search outside Skills IL.
license: MIT
allowed-tools: 'Bash(python:*) WebFetch'
compatibility: >-
  Requires network access to agentskills.co.il and a web fetch tool. Works with
  Claude Code, Claude.ai, Cursor, OpenClaw, and other supported Skills IL agents.
metadata:
  author: TheCommandCat
  version: 1.1.0
  category: developer-tools
  tags:
    he:
      - מאגר
      - חיפוש
      - גילוי
      - סקילס-אי-אל
    en:
      - registry
      - search
      - discovery
      - skills-il
  display_name:
    he: "מאתר סקילס IL"
    en: Skills IL Finder
  display_description:
    he: "חיפוש, סינון ובדיקה מהירה של סקילים ב-Skills IL"
    en: >-
      Find and compare Skills IL entries. Use when user asks to find a skill,
      search the Skills IL registry, filter by category, agent, tag, creator, or
      page, or inspect a skill before install. Do NOT use for general web search
      outside Skills IL.
  supported_agents:
    - claude-code
    - cursor
    - github-copilot
    - windsurf
    - opencode
    - codex
    - openclaw
---

# Skills IL Finder

This skill helps you find, compare, and install skills from the Skills IL registry.

## Instructions

### Step 1: Understand the need
Identify the topic, the target category, and whether the user wants discovery,
comparison, or install help.

### Step 2: Search the registry
Start at `https://agentskills.co.il/en/skills` or `https://agentskills.co.il/he/skills`.
Use `?q=` for search terms and `?page=N` to move through results.

### Step 3: Filter and inspect
Narrow by category, trust tier, agent, tag, creator, rating, or maintenance status.
Open the skill page before recommending it and check the description, trust score,
supported agents, install command, and whether `Download ZIP` is offered.

### Step 4: Recommend or install
If multiple skills fit, choose the one with the best match and trust score. If the
user wants install help, copy the exact `npx skills-il add ...` command from the page
or use `Download ZIP` for manual install.

## Examples

### Example 1: Find a skill
User says: "Find a skill for Hebrew PDFs."
Result: Search, filter, inspect top matches, and return the best one.

### Example 2: Filter by agent
User says: "Show developer tools skills with OpenClaw."
Result: Filter by category and agent, then shortlist compatible skills.

### Example 3: Install check
User says: "Is this skill safe to install?"
Result: Open the page, check trust score and install options, then answer briefly.

## Troubleshooting

### No results
Broaden the query or switch category.

### Wrong agent
Recommend a different skill or say the agent is unsupported.
