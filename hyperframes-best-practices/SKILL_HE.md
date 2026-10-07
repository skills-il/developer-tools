---
name: hyperframes-best-practices
description: "שיטות עבודה מומלצות להפקת וידאו מקוד עם HyperFrames. קומפוזיציה זה קובץ HTML רגיל עם אנימציות GSAP שהמנוע מרנדר ל-MP4, וכל זה עם תמיכה מלאה בעברית ו-RTL. מכסה כתיבת קומפוזיציה, מאפייני data-* לתזמון, חוזה ה-Timeline של GSAP, השיטה של Layout-Before-Animation, ה-Visual Identity Gate, פונטים עבריים דרך Google Fonts (Heebo, Rubik, Assistant), טקסט RTL עם dir=\"rtl\", כתוביות עברית בסגנון TikTok/Reels עם Whisper, אפקטים שמגיבים לאודיו, מעברי סצנות, וטקסט מעורב עברית ואנגלית. השתמשו כשבונים תוכן וידאו מבוסס-HTML או סרטוני סושיאל ושיווק בעברית בלי React. לא מתאים ל-Remotion ולעבודת וידאו ב-React, שם השתמשו ב-remotion-best-practices."
license: Apache-2.0
---

# HyperFrames, שיטות עבודה מומלצות

> עיבוד של סקיל HyperFrames מ-[heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) (Apache-2.0). שכבת העברית וה-RTL נוספה על ידי [skills-il](https://agentskills.co.il).

ב-HyperFrames, ה-HTML הוא מה שקובע איך הוידאו נראה. קומפוזיציה זה פשוט קובץ HTML עם מאפייני `data-*` לתזמון, Timeline של GSAP לאנימציה, ו-CSS לעיצוב. המנוע לוקח מפה, דואג להצגת הקליפים, ניגון המדיה והסנכרון של ה-Timeline.

## בעיה

שלוש בעיות עיקריות מחכות למי שבונה סרטון בעברית ב-HyperFrames. ראשית, אף פונט עברי לא מגיע מובנה, ולכן צריך להצהיר על Heebo, Rubik או Assistant עם `<link>` של Google Fonts, אחרת ה-lint מחזיר שגיאה שמשביתה חלק מהבדיקות. שנית, `dir="rtl"` לא מתפשט לבד לכל המקומות הנכונים, ו-GSAP לא הופך כיווני אנימציה בשבילכם. שלישית, הקריינות המובנית של HyperFrames (Kokoro-82M) מכסה תשעה locales בלבד (en-us, en-gb, es, fr-fr, hi, it, pt-br, ja, zh), ועברית לא ברשימה, אז קריינות עברית חייבת לבוא מבחוץ: או דרך מנוע האודיו של media-use (הסדר האוטומטי הוא HeyGen Starfish ואז ElevenLabs ואז Kokoro, ו-Gemini TTS, שטבלת השפות שלו כוללת עברית, נבחר במפורש עם `"provider": "gemini"` מחוץ לסדר הזה), או בהפקת הקובץ בשירות חיצוני וטעינתו כאלמנט `<audio>`. הפקודה `hyperframes tts` עצמה היא מקומית בלבד ואין לה ארגומנט ספק. הסקיל הזה מרכז את כל הפתרונות.

## עברית ו-RTL

<HARD-GATE>
**אף פעם לא לשים `dir="rtl"` (או `dir="auto"`) על אלמנט ה-`<html>`.** ב-preview וב-snapshot זה נראה מצוין, וברנדר עלול לצאת MP4 שחור לגמרי, כשהסימן היחיד הוא קובץ פלט קטן בהרבה מהצפוי. ב-upstream זה כלל lint ברמת חומרה `error` בשם `html_dir_attribute_breaks_render`, עם ההערה "a confirmed, silent failure". בגרסה 0.8.138 רנדר מקומי שלנו של קובץ כזה התאושש, אחרי שהרנדרר זיהה "suspect small frame" בפריים 0, אבל זו רשת ביטחון ולא תיקון: הכלל נשאר, ו-`render` נעצר עליו רק עם `--strict`. השאירו `lang="he"` על ה-`<html>` והורידו את הכיווניות לאלמנטים שנושאים טקסט: `dir="rtl"` על ה-div של שורש הקומפוזיציה, על מכולות טקסט בעברית, ועל ה-spans של מילות הכתוביות. הטקסט עדיין יסתדר נכון, כי אלגוריתם ה-bidi של הדפדפן עובד לפי הכיווניות של האלמנט עצמו. זו הטעות היקרה ביותר שאפשר לעשות בקומפוזיציה עברית, ואפשר להגיע אליה רק מעברית.
</HARD-GATE>

לכל קומפוזיציה בעברית, טענו את [references/hebrew-rtl.md](./references/hebrew-rtl.md). הקובץ מכסה איך לטעון פונטים עבריים (מצהירים עם `<link>` של Google Fonts, והמהדר מטמיע בזמן הבנייה), איפה לשים `dir="rtl"`, איך להפוך את ציר ה-X של GSAP, איך להפיק כתוביות עברית עם `hyperframes transcribe --language he`, מאיפה להביא קריינות עברית, ואיך לטפל בטקסט מעורב עברית+אנגלית עם `<bdi>`.

## מה אפשר להריץ ואיפה

כל שער איכות בסקיל הזה (`npx hyperframes check`, `render`, `transcribe`, `normalize-audio`, `doctor`, ושני הסקריפטים המצורפים) הוא פקודת שורת פקודה שדורשת התקנה מקומית של Node 22 ומעלה ושל FFmpeg. חלקו את הציפיות לפי המארח:

| שכבה | מארחים | מה מקבלים |
|---|---|---|
| עם shell | claude-code, cursor, windsurf, github-copilot, opencode, codex | הסקיל כולו, כולל השערים |
| בלי shell | chatgpt, claude-ai, claude-desktop, manus | הנחיות כתיבה בלבד. אפשר לכתוב קומפוזיציה תקינה, אי אפשר להריץ lint, ביקורת ניגודיות, תמלול או רנדר |

במארח בלי shell, אמרו את זה מראש ומסרו למשתמש את הפקודות שיריץ; כללי העברית חייבים אז להישמר מראש, כי שום דבר לא בודק אותם.

## איך ניגשים לבניית סרטון

לפני שמתחילים לכתוב HTML, שוו לרגע בעיניים מה הצופה צריך לקבל:

1. **מה הסיפור?** מהו הקו, איזה רגעים באמת חשובים, ומה הטון הרגשי.
2. **מבנה.** כמה קומפוזיציות, מה inline ומה sub-composition, ובאיזה טרקים יושבים הוידאו, האודיו, האוברלי והכתוביות.
3. **תזמון.** איזה קליפ קובע את האורך, איפה המעברים נוחתים, ומה הקצב.
4. **פריסה (Layout).** בונים קודם את המצב הסופי. הפירוט ב"Layout Before Animation" למטה.
5. **אנימציה.** רק עכשיו מוסיפים תנועה, לפי הכללים.

לתיקונים קטנים (צבע, כוונון של תזמון, תוספת של אלמנט בודד), אפשר לקפוץ ישר לכלל הרלוונטי.

### Visual Identity Gate

אסור להתחיל לכתוב HTML של קומפוזיציה בלי זהות ויזואלית. צבעים גנריים והגדרות דיפולט זה לא הסגנון שלנו.

זה סדר הבדיקה:

1. **יש DESIGN.md בפרויקט?** קראו אותו. הצבעים, הפונטים, כללי התנועה ורשימת ה"מה לא לעשות" שם, זה מה שמוביל.
2. **יש visual-style.md?** קראו אותו. תפעילו את `style_prompt_full` ואת השדות המובנים.
3. **המשתמש נקב בסגנון** ("Swiss Pulse", "כהה וטכני", וכו')? קראו את [visual-styles.md](./visual-styles.md) שבו שמונה presets, וייצרו DESIGN.md מינימלי מזה.
4. **אין כלום מכל אלה?** שאלו שלוש שאלות לפני שורת HTML אחת: איזה טון (חגיגי, נמרץ, רגוע), בהיר או כהה, ואם יש מותג או רפרנסים.

כל קומפוזיציה חייבת להתבסס על DESIGN.md, visual-style.md, או הכוונה ברורה מהמשתמש. אם אתם מוצאים את עצמכם שולפים `#333`, `#3b82f6` או Roboto, דילגתם על השלב הזה.

## Layout Before Animation

תמקמו כל אלמנט במקום שבו הוא אמור לשבת **ברגע המלא ביותר שלו**, הפריים שבו הוא כבר נכנס, ממוקם נכון, ועוד לא יצא. את זה כותבים כ-HTML+CSS סטטי לפני שנוגעים ב-GSAP.

**למה?** אם מתחילים מהמצב ההתחלתי של האנימציה (מחוץ למסך, scale 0, opacity 0) ומנפישים ל"איפה שנראה לי שזה אמור לנחות", בפועל מנחשים. חפיפות לא מתגלות עד הרנדר הראשון. בנייה של המצב הסופי קודם חושפת את בעיות ה-Layout לפני שמוסיפים בכלל תנועה.

### התהליך

1. **בחרו את ה-hero frame** של כל סצנה. הרגע עם הכי הרבה אלמנטים גלויים בו-זמנית. זה ה-Layout שאתם בונים.
2. **כתבו CSS סטטי** בדיוק לפריים הזה. `.scene-content` חייב למלא את הסצנה עם `width: 100%; height: 100%; padding: Npx;` ועם `display: flex; flex-direction: column; gap: Npx; box-sizing: border-box`. השתמשו ב-padding למרווחים, לא ב-`position: absolute; top: Npx`.
3. **כניסות עם `gsap.from()`.** מנפישים מהמצב שמחוץ למסך אל המיקום הסופי שב-CSS.
4. **יציאות עם `gsap.to()`.** מנפישים מהמיקום שב-CSS אל מחוץ למסך.

הדוגמה המלאה (CSS נכון ושגוי, tweens של כניסה ויציאה) ושני מקרי הקצה נמצאים ב-[references/layout-before-animation.md](references/layout-before-animation.md).

## מאפייני Data

מסונכרן מול `skills/hyperframes-core/references/data-attributes.md` של ה-upstream, שם גם הרשימה המלאה.

### כל הקליפים

| מאפיין | חובה | ערכים |
|---|---|---|
| `id` | חובה על `<video>`/`<audio>`, מומלץ בשאר | `<audio>` בלי id לא נכנס למיקס, והרנדר יוצא שקט |
| `data-start` | כן | שניות או הפניה לקליפ (`"el-1"`, `"intro + 2"`). זה מה שהופך אלמנט לקליפ מתוזמן |
| `data-duration` | חובה ל-`div` ולתת-קומפוזיציות | שניות. `img` מקבל 3 שניות כברירת מחדל, וידאו ואודיו את אורך המקור |
| `data-track-index` | לא | נתיב תצוגה ב-Studio בלבד, לא אילוץ תזמון ולא שכבת z |
| `data-media-start` | לא | היסט חיתוך בתוך המקור (שניות) |
| `data-volume` | לא | הגבר קבוע, ברירת מחדל 1, עד 3.98 (+12 dB). לפייד ולדאקינג: `data-automation` |
| `data-has-audio` | על `<video>` מתוזמן שאינו `muted` | `"true"` משאיר את הסאונד של הצילום |

חלון הנראות חצי-פתוח, `[start, start + duration)`: קליפ מוסתר בדיוק ב-`start + duration`, אז מסיימים tweens אחרונים (fade סוגר, יציאה של כתובית) קצת לפני, אחרת הפריים האחרון שלהם לא מתרנדר אף פעם.

המאפיין `class="clip"` הוא מוסכמה שה-runtime לא קורא, אבל כדאי לכתוב אותו על אלמנטים מתוזמנים: הוא נותן את התיבה במסך מלא, Studio נעזר בו, וה-lint מזהיר (`timed_element_missing_clip_class`) כשהוא חסר. לא שמים אותו על `<video>` ו-`<audio>`.

### שורש הקומפוזיציה ומארחים

| מאפיין | חובה | ערכים |
|---|---|---|
| `data-composition-id` | כן על השורש (תואם למפתח ב-`window.__timelines`); מומלץ על מארח | מזהה ייחודי |
| `data-width` / `data-height` | כן על השורש; מארח יכול לוותר (נלקח מהקובץ שנטען) | 1920x1080 או 1080x1920 |
| `data-duration` | שורש: אלא אם ה-runtime מסיק אותו (Timeline רשום, קליפים מתוזמנים); מארח: כן | גובר על אורך ה-Timeline של GSAP |
| `data-composition-src` | כן על מארח | נתיב לקובץ התת-קומפוזיציה |
| `data-fps` | לא | קצב פריימים על השורש; `render --fps` גובר עליו, אחרת 30 |

## מבנה, וידאו ואודיו

תת-קומפוזיציה שנטענת דרך `data-composition-src` עטופה ב-`<template>`, וה-runtime משכפל רק את התוכן שלו לתוך ה-DOM של המארח, כך שהיא יורשת את כיוון המארח. ה-`index.html` הראשי לא עטוף ב-`<template>`. גם כך שימו `dir="rtl"` על שורש התת-קומפוזיציה, כי רנדר או snapshot של הקובץ לבד לא מקבלים כיוון מבחוץ. כל מה שה-runtime צריך (סגנונות, markup, סקריפטים) נכנס לתוך ה-`<template>`, ה-`<head>` של הקובץ נזרק, ואת GSAP טוען המארח פעם אחת.

צילום שקט ו-b-roll מקבלים `muted playsinline`. צילום שרוצים את הסאונד שלו שומר אותו על ה-`<video>` עם `data-has-audio="true"` ובלי `muted` (וידאו מתוזמן בלי אף אחד מהשניים נכשל ב-lint, `video_missing_muted`). קריינות, מוזיקה ואודיו חלופי יושבים באלמנטי `<audio>` נפרדים, כל אחד עם `id`.

## חוזה ה-Timeline

- כל Timeline נפתח עם `{ paused: true }`. הנגן שולט בניגון, לא האנימציה.
- כל Timeline נרשם ב-`window.__timelines["<composition-id>"] = tl`, וזה הצעד האחרון של הבנייה (את ה-registry עצמו ה-runtime יוצר לבד).
- המנוע מקונן sub-timelines לבד, לא להוסיף אותם ידנית.
- המשך של הקליפ מגיע מ-`data-duration`, לא מאורך ה-Timeline של GSAP.

## כללים נוקשים

- **דטרמיניסטיות קודם לכל.** בלי `Math.random()`, `Date.now()`, `new Date()`, `performance.now()`, `requestAnimationFrame`, `gsap.utils.random()` או ערכי tween מסוג `"random(...)"`; כל אחד מהם הוא שגיאת lint, ושגיאת lint עוצרת את `check` מוקדם. צריך ערכים פסאודו-רנדומיים? PRNG עם seed (למשל mulberry32).
- **עדיפות ל-transform ול-opacity.** אסור להנפיש `display`, `visibility` או `autoAlpha` על אלמנט קליפ (שגיאת lint בשם `gsap_animates_clip_element`), מנפישים ילד שלו במקום.
- **אין `repeat: -1`.** בלי `data-duration` סופי על השורש זו שגיאת lint (`gsap_infinite_repeat`) ותכנון הרנדר עלול להיכשל, ועם `data-duration` סופי זו רק אזהרה, אבל מספר חזרות סופי הוא עדיין ברירת המחדל הבטוחה. סופרים עם `Math.floor` ולא עם `Math.ceil`: `repeat: Math.max(0, Math.floor(Math.round((available / cycle) * 1000) / 1000) - 1)`, כש-`available` הוא הזמן שנשאר אחרי היסט ההתחלה של ה-tween ו-`cycle` כולל `repeatDelay` אם יש (העיגול מונע שגיאת float כמו `0.3 / 0.1` שמתעגל למטה ל-2). ה-upstream מסמן את צורת ה-`Math.ceil(...) - 1` ככלל lint בשם `gsap_repeat_ceil_overshoot`, כי ceil מריץ מחזור אחד מעבר לסוף והמחזור האחרון נחתך באמצע התנועה.
- **לא קוראים ל-`video.play()` ו-`video.pause()`.** המנוע שולט במדיה, נקודה.
- **רושמים בסוף.** מותר לבנות Timeline בתוך callback אסינכרוני (למשל `document.fonts.ready`), אסור לרשום את המפתח לפני שה-tweens נוספו: Timeline ריק שנרשם מוקדם מתרנדר ריק (שגיאת lint בשם `gsap_timeline_registered_before_async_build`). כשמודדים טקסט עברי עם `fitTextFontSize`, בונים בתוך `document.fonts.ready` כדי שהמדידה תיעשה על הפונט העברי ולא על ה-fallback.

## מעברי סצנות (חובה)

כל קומפוזיציה עם כמה סצנות חייבת לעמוד בארבעת הכללים, והפרה של אחד מהם היא קומפוזיציה שבורה:

1. **תמיד מעבר בין סצנות.** בלי jump cuts.
2. **תמיד אנימציית כניסה לכל אלמנט בכל סצנה,** עם `gsap.from()`. שום אלמנט לא מופיע מוכן.
3. **אף פעם לא אנימציית יציאה** לפני מעבר, חוץ מהסצנה האחרונה. המעבר הוא היציאה, ותוכן הסצנה היוצאת חייב להיות גלוי במלואו ברגע שהמעבר מתחיל.
4. **רק בסצנה האחרונה** מותר להעלים אלמנטים (למשל fade לשחור), וזה המקום היחיד שבו `gsap.to(..., { opacity: 0 })` מותר.

בעברית, מעברים כיווניים (push, slide, wipe) הולכים לפי כיוון הקריאה, וב-Reel לאורך ערכי הפיקסלים של הקטלוג (`x: 1920`, `y: 1080`) שגויים וצריך `xPercent` / `yPercent`. הפירוט ב-references/hebrew-rtl.md.

## פונטים ונכסים

- **פונטים:** 18 משפחות (Inter, Roboto, Montserrat ועוד, אף אחת לא עברית) מגיעות מובנות. כל משפחה אחרת, וכל משפחה עברית בפרט, חייבת הצהרה, אחרת ה-lint מחזיר `font_family_without_font_face`. ראו את המלכודת על פונטים למטה.
- **אף פעם לא `crossorigin` על `<video>`/`<audio>`.** ה-lint דוחה את זה (`media_crossorigin_breaks_preview`, שגיאה) כי זה עלול להעלים את המדיה ב-preview של Studio.
- **נתיבי נכסים יחסיים לשורש הפרויקט,** גם בתוך תת-קומפוזיציות (`assets/narration-he.wav`). נתיב עם `../` הוא שגיאת lint (`invalid_parent_traversal_in_asset_path`).
- **התאמת טקסט:** `window.__hyperframes.fitTextFontSize` מחזיר אובייקט `{ fontSize, fits }` ולא מספר. ברירות המחדל הן `maxWidth: 1600` ו-`fontFamily: "Outfit"`, אז כתובית עברית לאורך חייבת להעביר את שניהם.

## רשימת בדיקה לפני מסירה

ל-Reel מתחילים מ-`npx hyperframes init <name> --resolution portrait`: שינוי של `data-width`/`data-height` בלבד משאיר את `html`, `body` ותגית ה-viewport על 1920x1080, ו-`body { overflow: hidden }` ישן חותך את הפריים בזמן שה-lint רק מזהיר (`root_dimensions_mismatch`). הפקודות `npx hyperframes catalog` ו-`npx hyperframes add <name>` מתקינות בלוקים מוכנים מה-registry (גם מעברים), והשמות והתגיות שם באנגלית, אז מחפשים באנגלית.

- [ ] תצוגה מקדימה עם `npx hyperframes preview`, שבה קורא עברית תופס סדר מילים, bidi ופונט fallback לפני שמשלמים על רנדר
- [ ] הפקודה `npx hyperframes check --strict` עוברת (בזמן עבודה `check` רגיל; ל-Reels מוסיפים `--caption-zone` עם רשימת `seek`, כדי להרחיק כותרות מרצועת הכתוביות, ראו references/hebrew-rtl.md). אלמנט מתוזמן ברמת השורש שיש בו layout מקונן מעלה את האזהרה `nested_structure_needs_subcomposition`; divs של סצנות לא מתוזמנים שה-Timeline של השורש מניע (התבנית של קטלוג המעברים) לא מעלים אותה. היא מריצה lint, runtime, layout, motion ובדיקת ניגודיות WCAG בסשן דפדפן אחד, אבל שגיאת lint עוצרת אותה לפני הסשן ("Browser session never ran"), ואז שאר הבדיקות מדווחות כלום בשקט. הדגל `--strict` מכשיל גם על אזהרות כמו `root_dimensions_mismatch`. `validate`, `inspect` ו-`layout` נשארו ככינויים לתאימות, ו-`lint` לא
- [ ] כשלי ניגודיות תוקנו (ראו בדיקות איכות)
- [ ] הכוריאוגרפיה נבדקה עם `animation-map.mjs`
- [ ] רינדור עם `npx hyperframes render --strict`. בלי `--strict` הרנדר ממשיך לקודד דרך שגיאות lint, כולל `html_dir_attribute_breaks_render`. דגלי פלט: `--fps` (אחרת `data-fps` של השורש, אחרת 30), `--quality draft|looks|delivery` (ברירת מחדל `looks`, CRF 16), `--format`, `--crf`, ו-`--resolution portrait|portrait-4k`, שיחס הממדים שלו חייב להתאים לקומפוזיציה

## בדיקות איכות

### ניגודיות

הפקודה `check` מריצה כברירת מחדל בדיקת ניגודיות WCAG AA על חמישה פריימים, וכל כשל הוא שגיאה שמכשילה את `check`, עם הצעת צבע (`Try rgb(...)`). ב-WCAG 2.2 טקסט רגיל צריך 4.5:1 וטקסט גדול 3:1, כשגדול פירושו 18pt (24px) או 14pt מודגש (בערך 18.66px). הקו של `check` לטקסט מודגש הוא 19px, כך שטקסט מודגש בין 18.66px ל-19px עלול להיכשל ב-`check` ולעבור ב-WCAG; הסקריפט `contrast-report.mjs` המצורף משתמש בקו של WCAG. מתקנים בתוך משפחת הפלטה: מבהירים על רקע כהה ומכהים על רקע בהיר, ומריצים שוב עד שזה נקי.

## מלכודות שסוכני AI נופלים בהן (עברית ו-RTL)

אלו הטעויות הספציפיות של עבודה בעברית. המלכודות הכלליות של HyperFrames (ראו ה-upstream) חלות גם הן.

- **מצהירים על כל פונט עברי עם `<link>` של Google Fonts, ולא מסתמכים על `font-family: 'Heebo'` לבד.** אף משפחה עברית לא מובנית. משפחה בלי הצהרה עדיין מתרנדרת מקומית, כי המהדר מוריד אותה (`packages/core/src/fonts/deterministicFonts.ts`), אבל ה-lint מחזיר `font_family_without_font_face` ברמת error, והשגיאה הזאת עוצרת את `npx hyperframes check` לפני סשן הדפדפן, כך שבדיקות הניגודיות, ה-layout והתנועה לא רצות בכלל (נמדד בגרסה 0.8.138). ה-`<link>` נקי מבחינת lint: המהדר מוריד בזמן הבנייה בדיוק את המשקלים שבקישור (כמו שהוא מוריד משפחה בלי הצהרה) ומזריק כללי `@font-face` דטרמיניסטיים. ה-lint בודק כל קובץ לבד, אז כל תת-קומפוזיציה שמשתמשת במשפחה עברית צריכה `@import` משלה בראש ה-`<style>` שבתוך ה-`<template>` (ה-`<head>` של תת-קומפוזיציה נזרק). הפירוט ב-references/hebrew-rtl.md.
- **לא להיעזר ב-`hyperframes tts` המובנה לעברית.** הפקודה מקומית בלבד, מתוארת ב-upstream כ-"Generate speech audio from text using a local AI model (Kokoro-82M)", והארגומנטים שלה הם בדיוק `input, text-file, output, voice, speed, lang, list, json`. אין ארגומנט ספק, ולכן שום משתנה סביבה לא יגרום לפקודה הזאת לדבר עברית. Kokoro ממפה תשעה locales לפי האות הראשונה של ה-voice ID: `a`=אנגלית אמריקאית, `b`=אנגלית בריטית, `e`=ספרדית, `f`=צרפתית, `h`=הינדי, `i`=איטלקית, `j`=יפנית, `p`=פורטוגזית ברזילאית, `z`=מנדרינית. עברית לא ביניהם. שתי דרכים שכן עובדות: (א) מסלול האודיו של media-use, שסדר בחירת המנוע שלו הוא HeyGen Starfish, אחריו ElevenLabs (דורש `ELEVENLABS_API_KEY` וגם שמודול הפייתון `elevenlabs` יהיה מותקן), ואחריהם Kokoro המקומי, ובנוסף Gemini TTS כבחירה מפורשת עם `"provider": "gemini"` ו-`"lang": "he"` (גוגל מציינת עברית במודלי ה-TTS של גרסה 3.8). הפקודה `hyperframes doctor` בודקת רק את התלויות של Kokoro, ולכן היא לא יכולה להראות איזה ספק ענן ייבחר. (ב) לייצר את ה-WAV/MP3 בשירות חיצוני (ElevenLabs, OpenAI TTS, Google Cloud TTS עם קולות `he-IL-*`) ולהטעין כאלמנט `<audio>` רגיל. דרך (ב) היא זו שעובדת בלי חשבון ובלי תלויות פייתון.
- **תמיד מעבירים `--language he` ל-`transcribe`.** מודל ברירת המחדל הוא `small.en`, ובלי `--language` ה-CLI כופה אנגלית, כך שקובץ עברי חוזר כטקסט באנגלית. עם `--language he` ה-CLI מחליף כל מודל `.en` בגרסה הרב-לשונית שלו, ו-`--engine auto` חוזר ל-Whisper כי ל-Parakeet אין עברית. תריצו `npx hyperframes transcribe audio.wav --model medium --language he` (המודל `small` חלש לעברית; עלו ל-`large-v3` כשהאודיו רועש). הקובץ `references/captions.md` הוא טקסט upstream שממליץ על `--model small` לכל דבר, ולעברית הכלל הזה גובר עליו.
- **שמים `dir="rtl"` על מכולות טקסט בעברית ועל השורש של כל תת-קומפוזיציה.** ברנדר המלא תת-קומפוזיציה יורשת את כיוון המארח, אבל לא כשמרנדרים או מצלמים את הקובץ לבד. גם tweens של GSAP לא הופכים את הכיוון אוטומטית. כותרת עם `gsap.from({x: -80})` נכנסת משמאל ב-LTR וב-RTL כאחד. לעברית, הפכו לערך חיובי `x: 80` כדי שהכותרת תיכנס מצד ימין, בהתאם לכיוון הקריאה.
- **שמות מותג באנגלית צריכים `<bdi>` או `unicode-bidi: isolate`.** בלי בידוד, האלגוריתם הדו-כיווני של Unicode מסדר מחדש את ה-runs ולעתים ממקם פיסוק בצד הלא נכון, או הופך את המותג ויזואלית. פשוט עוטפים: `הצטרפו ל־<bdi>HyperFrames</bdi> עכשיו`.

- **אל תתקנו כניסה עברית רק בגלל ש-`animation-map.mjs` אומר שהיא זזה לכיוון ההפוך.** הסקריפט מתאר תנועה לפי הפרשי bounding box במרחב המסך, בלי שום מושג של כיוון קריאה. בקומפוזיציית RTL, כניסה עברית תקינה כמו `gsap.from(".subtitle", { x: 80 })` שמכניסה את הטקסט מימין, מדווחת כתנועה שמאלה (למשל `moves 32px left`; מספר הפיקסלים משתנה לפי הדגימה). התיאור מדויק לגבי פיקסלים ומטעה לגבי כוונה. קראו את הסיכומים בשביל הכוריאוגרפיה והדגלים, לא בשביל הכיוון, ואל תהפכו סימן של tween רק כדי שהתיאור המילולי יצא "right".
- **קריינות עברית מעל מצע מוזיקה: מקבצים את הקולות, ואז מייצרים את ה-carve.** שמים רק את קליפי הקריינות בקבוצת אודיו (`data-audio-group="voiceover"`), אף פעם לא את המוזיקה, אפקטים או את המצע עצמו. המצע מונמך על ידי carve, אבל `data-fx-carve` שנכתב ביד לא עושה כלום: לפי ה-upstream ההגדרות של ה-carve "are never read at playback", ומה שמתנגן הוא ה-`data-fx-chain` וה-`data-automation` שהוא מייצר. מייצרים אותו במודול ה-carve של Studio או עם `skills/hyperframes-audio/scripts/carve.mjs --comp index.html` של ה-upstream, ומוודאים ששני המאפיינים נכתבו לפני הרנדר. בלי אף אחד מהם, שמים על המצע נתיב ווליום ב-`data-automation`. לעוצמה: `npx hyperframes normalize-audio --target <element-id> --lufs -16 --write` (`--target` הוא ה-id של הקליפ; `--lufs` ברירת מחדל -16).

## סקריפטים מצורפים

בתיקייה `scripts/` יש שני כלי Node שהועתקו מה-upstream בגרסה `d94708e` (`animation-map.mjs` עם קובץ העזר `animation-map-sampling.mjs`, `contrast-report.mjs`, ו-`package-loader.mjs` המשותף). מריצים אותם מתוך שורש הפרויקט ומצביעים על תיקיית הסקיל; הם מאתרים את `@hyperframes/producer`, `@hyperframes/core` ו-`sharp` קודם כל מתיקיית העבודה. לפרויקט חדש של `hyperframes init` אין `node_modules`, אז או שמתקינים אותם, או שנותנים לטוען לבצע התקנה זמנית חד-פעמית (`npm install --ignore-scripts --no-save` לתיקייה זמנית) עם `HYPERFRAMES_SKILL_BOOTSTRAP_DEPS=1`; בלי TTY הוא עוצר ומדפיס את ההוראה הזאת. את הגרסה נועלים עם `HYPERFRAMES_SKILL_PKG_VERSION`.

```bash
# פורמט לאורך (טיקטוק / רילס). שני הסקריפטים מוגדרים כברירת מחדל
# ל-viewport של 1920x1080, אז לקומפוזיציה לאורך חובה להעביר --width/--height.
export HYPERFRAMES_SKILL_PKG_VERSION="$(npx hyperframes --version)"
HYPERFRAMES_SKILL_BOOTSTRAP_DEPS=1 node <skill-dir>/scripts/animation-map.mjs . --width 1080 --height 1920 --out .hyperframes/anim-map
HYPERFRAMES_SKILL_BOOTSTRAP_DEPS=1 node <skill-dir>/scripts/contrast-report.mjs . --width 1080 --height 1920 --samples 10 --out .hyperframes/contrast
```

שניהם מקבלים גם `--fps` (ברירת מחדל 30). התאימו אותו לרנדר שלכם, ושימו `data-fps` על שורש הקומפוזיציה אם אתם לא מרנדרים ב-30.

| סקריפט | מה הוא עושה |
|---|---|
| `scripts/animation-map.mjs` | עובר על כל tween ב-`window.__timelines`, דוגם bounding boxes, ומייצר `animation-map.json` עם סיכום לכל tween, ציר זמן ASCII, זיהוי stagger, אזורים מתים ודגלים. |
| `scripts/contrast-report.mjs` | ביקורת WCAG 2.2 עם רשת תמונות `contrast-overlay.png` (מג'נטה נכשל AA, צהוב AA בלבד, ירוק AAA, אפור לא נמדד), ש-`check` לא מייצר; `check` נשאר השער. יוצאת עם 1 על כשל AA, ועם 3 כשיש טקסט שלא נמדד (צבע שלא מתפענח, רקע שקוף), ואף פעם לא מחשיבה אותו כמעבר. התוצאות שלה תאמו את `check` במקרים שב-`scripts/test/contrast-report.regression.mjs`. |

שניהם דורשים Node 22 ומעלה (חבילת ה-producer מצהירה `"engines": { "node": ">=22" }`).

## פרטי Bidi בעברית

הכלל של `<bdi>` למעלה מכסה שמות מותג. קומפוזיציות עברית עם כיוון מעורב צריכות עוד שלושה הרגלי bidi:

- **שבירת שורות לכותרות עברית ארוכות.** עברית לא עוברת מיקוף. כותרת עברית ארוכה שגולשת חייבת להישבר בגבולות מילים, לעולם לא באמצע מילה. הגדירו `max-width` כדי שהיא תישבר באופן טבעי, והדפדפן כבר שובר עברית רק ברווחים (`word-break: keep-all` משנה שבירה של CJK, לא של עברית). אל תשתמשו ב-`<br>` כדי לכפות שבירה. לכותרות תצוגה שבהן כל מילה בכוונה בשורה משלה, תנו לכל מילה אלמנט נפרד.
- **ספרות עם סימנים צמודים בתוך runs של RTL.** רצף ספרות בודד מטופל נכון על ידי האלגוריתם הדו-כיווני של Unicode: `2025` ליד מילה עברית נשאר משמאל-לימין בתוך פסקת RTL בעצמו, הוא לא מתהפך ל-`5202`, אז מספר שלם פשוט לא צריך עטיפה. הסכנה האמיתית היא ספרה שנוגעת בסימן, בטווח, או באסימון לטיני: סימן אחוז, סימן מטבע, או מקף-טווח יכולים להתנתק ולנחות בצד הלא נכון. עטפו את אלה ב-`<bdi>` או ב-`⁦...⁩` (LTR isolate): `<bdi>15%</bdi> הנחה`, `<bdi>₪199</bdi>`, `<bdi>10-20</bdi>`. ככה הסימן נשאר צמוד למספר. ראו references/hebrew-rtl.md.
- **שיקוף סימני פיסוק.** סוגריים, סוגריים מרובעים ומרכאות הם תווים משוקפים: `(` הופך ויזואלית ל-`)` בתוך run של RTL. בכתוביות ובפסקאות עברית תנו לדפדפן לשקף אותם בזה שתשמרו את הטקסט בתוך קונטיינר `dir="rtl"` תקין. אל תחליפו ידנית `(` ו-`)` כדי "לתקן" את זה, וכשבתוך הסוגריים יש תוכן LTR (מותג, URL, מספר) עטפו את התוכן הפנימי ב-`<bdi>` כך שרק ה-run הפנימי יהיה LTR והסוגריים יישארו משוקפים נכון.

## פתרון בעיות

### הפקודה `hyperframes` לא נמצאת או שהרנדר נכשל מיד
הפריימוורק דורש Node 22 ומעלה ו-FFmpeg ב-PATH. ודאו ש-`node --version` הוא 22 ומעלה ושה-`ffmpeg -version` עובד. ב-macOS מתקינים FFmpeg עם `brew install ffmpeg`, ב-Debian/Ubuntu עם `apt install ffmpeg`. בלי FFmpeg המהדר לא יכול לקודד את ה-MP4 והוא עוצר עוד לפני שהוא מרנדר פריים אחד.

### ה-lint מדווח `font_family_without_font_face`, או שהעברית מרונדרת בפונט fallback
משפחות עבריות לא מגיעות מובנות, אז צריך להצהיר על כל אחת. הוסיפו `<link rel="stylesheet">` של Google Fonts (או `@import`) עם המשפחה והמשקלים, למשל `family=Heebo:wght@400;800`, והשאירו `font-family: 'Heebo', sans-serif;` ב-CSS. הודעת ה-lint אומרת שהטקסט "will fall back to a generic font", אבל ברנדר מקומי בגרסה 0.8.138 משפחה אמיתית מ-Google עדיין הוטמעה; המחיר האמיתי הוא ש-`check` נעצר מוקדם. פונט fallback ב-MP4 פירושו שם משפחה עם שגיאת כתיב או הורדה שנכשלה, ופונט מורשה שלא מ-Google צריך `@font-face` משלכם שמצביע על קובץ בפרויקט.

### ביקורת ניגודיות WCAG נכשלת (`hyperframes check`)
הפקודה `check` מריצה lint, runtime, layout, motion ובדיקת ניגודיות WCAG בסשן דפדפן אחד, והיא זו שמחליפה את `validate` שסומן ב-upstream כ-deprecated. היא דוגמת פיקסלים של רקע מאחורי כל אלמנט טקסט בחמישה פריימים ונכשלת על יחסים מתחת ל-4.5:1 (טקסט רגיל) או 3:1 (טקסט גדול). מתקנים בזה שמכווננים את הצבע שנכשל בתוך משפחת הפלטה: מבהירים אותו על רקע כהה, מכהים אותו על רקע בהיר. אל תמציאו צבע חדש. תריצו `hyperframes check` שוב עד שזה נקי. השתמשו ב-`--no-contrast` רק בזמן עבודה, אף פעם לא כמצב סופי, ו-`--snapshots` שומר את חמשת הפריימים שנבדקו כ-PNG תחת `snapshots/`.

### הקומפוזיציה מרונדרת ריקה או שהתוכן לא נראה
**אם הקומפוזיציה בעברית וה-preview תקין אבל ה-MP4 שחור, בדקו קודם כל אם יש `dir` על ה-`<html>`.** `<html dir="rtl">` או `dir="auto"` עלולים לייצר רנדר ריק בזמן ש-preview ו-snapshot נראים תקינים. הסירו את זה, השאירו את `lang`, והורידו את `dir="rtl"` לאלמנטים שנושאים טקסט. `npx hyperframes check` מדווח על זה כ-`html_dir_attribute_breaks_render` ברמת חומרה error. אחרת, הסיבה הכי נפוצה היא עטיפת `<template>` על קומפוזיציה standalone. ה-`index.html` הראשי חייב לשים את ה-div עם `data-composition-id` ישירות ב-`<body>`, לא בתוך `<template>`. בדקו גם שכל timeline נרשם דרך `window.__timelines["<composition-id>"] = tl` ושבנייה אסינכרונית רושמת את המפתח רק אחרי שה-tweens נוספו (`gsap_timeline_registered_before_async_build`); Timeline ריק שנרשם מוקדם מתרנדר ריק.

### כותרת עברית נכנסת מהצד הלא נכון
אנימציות `x:` ב-GSAP לא מתהפכות אוטומטית. הפכו את הסימן (`x: 80`, כניסה מימין); מעברים כיווניים מוסברים ב-`references/hebrew-rtl.md`.

## קישורי עזר

| מקור | URL | מה בודקים |
|---|---|---|
| HyperFrames GitHub | https://github.com/heygen-com/hyperframes | ה-repo המקורי, issues, releases |
| HyperFrames docs | https://hyperframes.heygen.com/quickstart | ה-CLI, דרישות Node 22+ ו-FFmpeg |
| לוגיקת הפונטים של המהדר | https://github.com/heygen-com/hyperframes/blob/main/packages/core/src/fonts/deterministicFonts.ts | רשימת הפונטים המובנים, ההורדה מ-Google Fonts, נתיב ה-cache |
| חוזה הקומפוזיציה | https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-core/references/data-attributes.md | מאפייני `data-*` עדכניים, `class="clip"`, שדות חובה |
| קולות Kokoro TTS | https://github.com/heygen-com/hyperframes/blob/main/skills/media-use/audio/references/tts.md | תחיליות הקולות של Kokoro, תשעה locales, בלי עברית |
| מדריך מודלים של Whisper | https://github.com/skills-il/developer-tools/blob/master/hyperframes-best-practices/references/transcript-guide.md | `.en` מול רב-לשוני, הדגל `--language` |
| Google Fonts עם תמיכה בעברית | https://fonts.google.com/?subset=hebrew | Heebo, Rubik, Assistant, Alef, Frank Ruhl Libre, Noto Sans Hebrew |
| מפרט unicode-bidi | https://developer.mozilla.org/en-US/docs/Web/CSS/unicode-bidi | `isolate`, `<bdi>`, טקסט דו-כיווני |

## מסמכי עיון

רשימת הרפרנסים המלאה (palettes, house style, motion principles, transitions, captions, audio-reactive, TTS, typography, dynamic techniques, transcript guide) מופיעה ב-SKILL.md. הקובץ הזה מתרכז רק בשכבת העברית וה-RTL. לעבודה ללא עברית אפשר לפנות ישר ל-SKILL.md.
