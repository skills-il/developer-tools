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

# מאתר סקילס IL

## הוראות

### שלב 1: להבין את הצורך
זהו את הנושא, הקטגוריה, והאם המשתמש רוצה גילוי, השוואה או עזרה בהתקנה.

### שלב 2: לחפש ברישום
התחילו ב־`https://agentskills.co.il/en/skills` או `https://agentskills.co.il/he/skills`.
השתמשו ב־`?q=` למונחי חיפוש וב־`?page=N` למעבר בין תוצאות.

### שלב 3: לסנן ולבדוק
צמצמו לפי קטגוריה, רמת אמון, סוכן, תגית, יוצר, דירוג או מצב תחזוקה.
פתחו את עמוד הסקיל לפני המלצה ובדקו תיאור, ציון אמון, סוכנים נתמכים,
פקודת התקנה, והאם יש `Download ZIP`.

### שלב 4: להמליץ או להתקין
אם כמה סקילים מתאימים, בחרו את ההתאמה והאמון הטובים ביותר. אם המשתמש רוצה
עזרה בהתקנה, העתיקו את פקודת `npx skills-il add ...` המדויקת מהעמוד או השתמשו
ב־`Download ZIP` להתקנה ידנית.

## דוגמאות

### דוגמה 1: חיפוש סקיל
המשתמש אומר: "Find a skill for Hebrew PDFs."
תוצאה: חיפוש, סינון, בדיקת המועמדים המובילים והחזרת ההתאמה הטובה ביותר.

### דוגמה 2: סינון לפי סוכן
המשתמש אומר: "Show developer tools skills with OpenClaw."
תוצאה: סינון לפי קטגוריה וסוכן, ואז רשימה קצרה של סקילים תואמים.

### דוגמה 3: בדיקת התקנה
המשתמש אומר: "Is this skill safe to install?"
תוצאה: פתיחת העמוד, בדיקת ציון האמון ואפשרויות ההתקנה, ואז תשובה קצרה.

## פתרון בעיות

### אין תוצאות
הרחיבו את החיפוש או החליפו קטגוריה.

### הסוכן לא תואם
המליצו על סקיל אחר או ציינו שהסוכן לא נתמך.
