# Sample Hebrew prompts for the conversation phase

Moved out of SKILL.md Step 9 at v1.4.0 to stay under the 5,000-word body cap.

video-use's "Converse" step (step 3 of "The process" upstream) asks questions shaped by the material. Hebrew messages users send, and what each maps to:

| Hebrew user message | What it maps to in the upstream workflow |
|---------------------|------------------------------------------|
| "ערוך את הקבצים האלה לסרטון השקה" | "edit these into a launch video", full inventory then strategy then execute |
| "תנקה את השתיקות ואת המילים המיותרות" | Filler removal + dead-space cuts only |
| "תוסיף כתוביות בעברית במרכז התחתון" | Subtitle generation with Hebrew SUB_FORCE_STYLE override AND `burn-hebrew-captions.sh` |
| "תוסיף גרידינג חם" | `grade.py --preset warm_cinematic` (language-agnostic) |
| "תפצל למקטעים של 30 שניות לאינסטה" | Vertical 1080x1920 reformat with `vertical-social-he` style |
| "תבדוק שאין שגיאות בכתוביות בעברית" | Trigger Step 6 frame-sampling self-eval (glyph fallback + RTL pixel order) |
