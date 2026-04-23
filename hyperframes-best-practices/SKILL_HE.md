---
name: hyperframes-best-practices
description: "שיטות עבודה מומלצות ליצירת סרטונים מקוד עם HyperFrames — קומפוזיציות HTML רגילות עם אנימציות GSAP שמתרנדרות ל-MP4 — כולל תמיכה מלאה בעברית ו-RTL. מכסה כתיבת קומפוזיציות, מאפייני data-* לתזמון, חוזה Timeline של GSAP, מתודולוגיית Layout-Before-Animation, Visual Identity Gate, פונטים עבריים דרך Google Fonts (Heebo, Rubik, Assistant), רינדור טקסט RTL עם dir=\"rtl\", כתוביות TikTok/Reels בעברית דרך Whisper, אפקטים מגיבים לאודיו, מעברי סצנות, וטקסט דו-כיווני עברית+אנגלית. השתמשו כשאתם בונים תוכן וידאו מבוסס-HTML או סרטוני סושיאל/שיווק בעברית בלי React. אל תשתמשו עבור Remotion או עבודת וידאו כללית ב-React — השתמשו ב-remotion-best-practices לזה."
license: Apache-2.0
---

# HyperFrames - שיטות עבודה מומלצות

> עיבוד של [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) (Apache-2.0). התאמות עברית ו-RTL על ידי [skills-il](https://agentskills.co.il).

HTML הוא מקור האמת של הוידאו ב-HyperFrames. קומפוזיציה היא קובץ HTML עם מאפייני `data-*` לתזמון, Timeline של GSAP לאנימציה, ו-CSS לעיצוב. המנוע מטפל בהצגת הקליפים, הנגנת המדיה, וסנכרון ה-Timeline.

## בעיה

בניית סרטונים מבוססי-HTML עם טקסט עברי דורשת שהמהדר יוריד פונטים עבריים מ-Google Fonts לפי דרישה, `dir="rtl"` מפורש על מכלי טקסט בעברית, היפוך של כיווני entrance ב-GSAP, וסנכרון כתוביות עברית דרך Whisper — ש-HyperFrames לא מתעד מחוץ לקופסה. קריינות בעברית היא פער נפרד: ה-TTS המובנה (Kokoro) לא תומך בעברית (רק 8 שפות: en-us, en-gb, es, fr-fr, hi, it, pt-br, ja, zh), אז צריך להפיק את הקריינות בשירות חיצוני ולהטעין אותה כ-`<audio>`.

## עברית ו-RTL

לקומפוזיציות בעברית ו-RTL, טענו את [references/hebrew-rtl.md](./references/hebrew-rtl.md). הקובץ מכסה טעינת פונטים עבריים (המהדר מוריד אוטומטית מ-Google Fonts), scoping של `dir="rtl"`, היפוך ציר X ב-GSAP, סנכרון כתוביות עברית דרך `hyperframes transcribe --language he`, קריינות בעברית דרך TTS חיצוני, וטקסט דו-כיווני עם `<bdi>`.

## גישה

לפני שכותבים HTML, חשבו ברמה גבוהה:

1. **מה** — מה הצופה אמור לחוות? מהו קו העלילה, מהם הרגעים החשובים, מה הטון הרגשי.
2. **מבנה** — כמה קומפוזיציות, מי תת-קומפוזיציות מול inline, איזה טרק נושא מה (וידאו, אודיו, אוברליי, כתוביות).
3. **תזמון** — איזה קליפ מגדיר את האורך, איפה המעברים נוחתים, מהי הפעימה.
4. **Layout** — בונים את המצב הסופי קודם. ראו "Layout Before Animation" למטה.
5. **Animate** — רק אז מוסיפים תנועה לפי הכללים.

לעריכות קטנות (תיקון צבע, כיוון תזמון, תוספת אלמנט אחד) — עוברים ישר לכללים.

### Visual Identity Gate

לפני שכותבים HTML של קומפוזיציה, חובה שתהיה זהות ויזואלית מוגדרת. אל תכתבו קומפוזיציות עם צבעים דיפולטיביים או גנריים.

סדר הבדיקה:

1. **יש DESIGN.md בפרויקט?** → קראו אותו. השתמשו בצבעים, פונטים, כללי תנועה וגבולות ה-"מה לא לעשות" שלו בדיוק.
2. **יש visual-style.md?** → קראו אותו והחילו את `style_prompt_full` והשדות המובנים.
3. **המשתמש נקב בסגנון** (למשל "Swiss Pulse", "כהה ומתוחכם")? → קראו את [visual-styles.md](./visual-styles.md) לשמונה presets ייעודיים ו-generu DESIGN.md מינימלי.
4. **אף אחד מהנ"ל?** → שאלו שלוש שאלות לפני שמתחילים לכתוב HTML (מה הטון, רקע בהיר או כהה, צבעי מותג או רפרנסים).

כל קומפוזיציה חייבת להישען על DESIGN.md, visual-style.md, או הכוונה מפורשת של המשתמש. אם אתם בורחים ל-`#333`, `#3b82f6` או Roboto — דילגתם על השלב הזה.

## Layout Before Animation

מקמו כל אלמנט במקום שבו הוא אמור להיות ב**רגע הכי גלוי** שלו — הפריים שבו הוא ממוקם סופית ולא יוצא עדיין. כתבו את זה כ-HTML+CSS סטטי קודם. בלי GSAP.

**למה זה חשוב:** אם ממקמים אלמנטים במצב התחלתי של אנימציה (מחוץ למסך, scale 0, opacity 0) ומנסים להנפיש למה שנראה כמו הסוף — מנחשים. חפיפות לא נראות עד הרנדר. בניית המצב הסופי קודם חושפת בעיות layout לפני שמוסיפים תנועה.

### התהליך

1. **זהו את ה-hero frame** לכל סצנה — הרגע עם הכי הרבה אלמנטים נראים בו-זמנית. זה ה-layout שאתם בונים.
2. **כתבו CSS סטטי** לפריים הזה. ה-`.scene-content` חייב למלא את הסצנה עם `width: 100%; height: 100%; padding: Npx;` ו-`display: flex; flex-direction: column; gap: Npx; box-sizing: border-box`. השתמשו ב-padding, לא ב-`position: absolute; top: Npx`.
3. **הוסיפו entrances עם `gsap.from()`** — מנפישים מהמצב שמחוץ למסך אל המיקום ב-CSS.
4. **הוסיפו exits עם `gsap.to()`** — מנפישים מהמיקום ב-CSS אל מחוץ למסך.

## חוזה ה-Timeline

- כל ה-timelines מתחילים עם `{ paused: true }` — הנגן שולט בהנגנה.
- רשמו כל timeline: `window.__timelines["<composition-id>"] = tl`.
- המנוע מנסת sub-timelines אוטומטית — אל תוסיפו ידנית.
- משך מגיע מ-`data-duration`, לא מאורך Timeline של GSAP.

## כללים (לא ניתנים למשא ומתן)

- **דטרמיניסטי:** לא `Math.random()`, לא `Date.now()`, לא לוגיקה תלוית-זמן. השתמשו ב-PRNG עם seed (למשל mulberry32) כשצריך ערכים פסאודו-רנדומיים.
- **לא אנימציות עם `display` או `visibility`.** השתמשו ב-opacity ו-transform.
- **לא `repeat: -1`.** חשבו כמות סופית מתוך משך הקליפ.
- **לא קוראים ל-`video.play()` או `video.pause()`.** המנוע שולט במדיה.
- **Timeline נבנה סינכרונית.** לא `setTimeout`, לא `async` בתוך הבנייה.

## מלכודות נפוצות

אלו failure modes של סוכני AI ספציפית לעבודה בעברית/RTL עם HyperFrames. מלכודות כלליות של HyperFrames (ראו upstream) עדיין חלות.

- **לא להוסיף תג `<link rel="stylesheet">` של Google Fonts או הצהרת `@import url(...)` ב-CSS לפונטים עבריים.** המהדר כבר מוריד את Google Fonts בצד-שרת דרך `fetchGoogleFont()` ב-`packages/producer/src/services/deterministicFonts.ts`, מטמין את ה-WOFF2 ב-`~/.cache/hyperframes/fonts/<slug>/`, ומטמיע כ-base64 data URI ב-HTML המקומפל. stylesheet חיצוני שובר דטרמיניסטיות (תלות רשת ברנדר) וכופל את טעינת הפונט. פשוט כתבו `font-family: 'Heebo', sans-serif;`.
- **לא לנסות את `hyperframes tts` המובנה לקריינות עברית.** Kokoro-82M תומך ב-8 שפות שמקודדות באות הראשונה של מזהה הקול — `a`=אנגלית אמריקאית, `b`=אנגלית בריטית, `e`=ספרדית, `f`=צרפתית, `h`=הינדי, `i`=איטלקית, `j`=יפנית, `p`=פורטוגזית ברזילאית, `z`=מנדרינית. עברית לא שם. הפיקו WAV/MP3 בשירות חיצוני (ElevenLabs, OpenAI TTS, Google Cloud TTS בעברית) והטעינו כ-`<audio>` רגיל בקומפוזיציה.
- **לא להשתמש במודלי `.en` של Whisper על אודיו בעברית.** גרסאות `.en` **מתרגמות** אודיו לא-אנגלי לאנגלית במקום לתמלל אותו. לכתוביות עברית השתמשו ב-`npx hyperframes transcribe audio.wav --model small --language he` (או `medium` / `large-v3` לאודיו רועש). הסיומת `.en` נכונה רק כשהמשתמש ציין במפורש שהאודיו אנגלי.
- **לא לשכוח `dir="rtl"` על מכלי טקסט עבריים גם בקומפוזיציה שברירת המחדל שלה RTL.** תת-קומפוזיציות ב-HyperFrames קובעות את ההקשר הכיווני שלהן בעצמן. גם tweens של GSAP לא עושים mirror אוטומטי. כותרת ש-`gsap.from({x: -80})` נכנסת משמאל גם ב-LTR וגם ב-RTL — לעברית, הפכו ל-`x: 80` כדי שתיכנס מימין בהתאם לכיוון קריאה.
- **לא להדביק מותגים באנגלית בפסקה עברית בלי `<bdi>` או `unicode-bidi: isolate`.** בלי בידוד, האלגוריתם הבידירקציונלי של Unicode מסדר מחדש runs בכיוונים שונים ויכול למקם סימני פיסוק בצד הלא נכון של המותג או להפוך אותו ויזואלית. עטפו מותגים: `הצטרפו ל־<bdi>HyperFrames</bdi> עכשיו`.

## קישורי עזר

| מקור | URL | מה לבדוק |
|---|---|---|
| HyperFrames GitHub | https://github.com/heygen-com/hyperframes | ה-repo המקורי, issues, releases |
| HyperFrames docs | https://hyperframes.heygen.com/quickstart | CLI, דרישות Node 22+ ו-FFmpeg |
| לוגיקת פונטים של המהדר | https://github.com/heygen-com/hyperframes/blob/main/packages/producer/src/services/deterministicFonts.ts | רשימת הפונטים הקנוניים, fallback ל-Google Fonts, נתיב cache |
| Kokoro TTS voices | https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/tts.md | 54 קולות ב-8 שפות (אין עברית) |
| Whisper model guide | https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/transcript-guide.md | `.en` מול מודלים רב-לשוניים, דגל `--language` |
| Google Fonts עברית | https://fonts.google.com/?subset=hebrew | Heebo, Rubik, Assistant, Alef, Frank Ruhl Libre, Noto Sans Hebrew |
| Unicode bidi spec | https://developer.mozilla.org/en-US/docs/Web/CSS/unicode-bidi | `isolate`, `<bdi>`, טקסט דו-כיווני |

## References

הרפרנסים המלאים (כולל palettes, house style, motion principles, transitions, captions, audio-reactive, TTS, typography, dynamic techniques, transcript guide) מופיעים ב-SKILL.md. קובץ זה מרחיב רק את שכבת העברית/RTL. לעבודה ללא עברית, התייחסו ישירות ל-SKILL.md.
