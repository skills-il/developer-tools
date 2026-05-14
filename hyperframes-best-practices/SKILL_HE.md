---
name: hyperframes-best-practices
description: "שיטות עבודה מומלצות להפקת וידאו מקוד עם HyperFrames. קומפוזיציה זה קובץ HTML רגיל עם אנימציות GSAP שהמנוע מרנדר ל-MP4, וכל זה עם תמיכה מלאה בעברית ו-RTL. מכסה כתיבת קומפוזיציה, מאפייני data-* לתזמון, חוזה ה-Timeline של GSAP, השיטה של Layout-Before-Animation, ה-Visual Identity Gate, פונטים עבריים דרך Google Fonts (Heebo, Rubik, Assistant), טקסט RTL עם dir=\"rtl\", כתוביות עברית בסגנון TikTok/Reels עם Whisper, אפקטים שמגיבים לאודיו, מעברי סצנות, וטקסט מעורב עברית ואנגלית. השתמשו כשבונים תוכן וידאו מבוסס-HTML או סרטוני סושיאל ושיווק בעברית בלי React. לא מתאים ל-Remotion ולעבודת וידאו ב-React, שם השתמשו ב-remotion-best-practices."
license: Apache-2.0
---

# HyperFrames, שיטות עבודה מומלצות

> עיבוד של סקיל HyperFrames גרסה 1.0.x מ-[heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) (Apache-2.0). שכבת העברית וה-RTL נוספה על ידי [skills-il](https://agentskills.co.il).

ב-HyperFrames, ה-HTML הוא מה שקובע איך הוידאו נראה. קומפוזיציה זה פשוט קובץ HTML עם מאפייני `data-*` לתזמון, Timeline של GSAP לאנימציה, ו-CSS לעיצוב. המנוע לוקח מפה, דואג להצגת הקליפים, ניגון המדיה והסנכרון של ה-Timeline.

## בעיה

שלוש בעיות עיקריות מחכות למי שבונה סרטון בעברית ב-HyperFrames. ראשית, טעינת פונטים עבריים (Heebo, Rubik, Assistant) עובדת מצוין, אבל רק אם כותבים את זה נכון, בלי `<link>` או `@import` כמו שרוב האנשים רגילים. שנית, `dir="rtl"` לא מתפשט לבד לכל המקומות הנכונים, ו-GSAP לא הופך כיווני אנימציה בשבילכם. שלישית, הקריינות המובנית של HyperFrames (Kokoro-82M) תומכת ב-8 שפות בלבד (en-us, en-gb, es, fr-fr, hi, it, pt-br, ja, zh), ועברית לא ברשימה, אז קריינות עברית חייבת לבוא משירות חיצוני. הסקיל הזה מרכז את כל הפתרונות.

## עברית ו-RTL

לכל קומפוזיציה בעברית, טענו את [references/hebrew-rtl.md](./references/hebrew-rtl.md). הקובץ מכסה איך לטעון פונטים עבריים (המהדר כבר מטפל ב-Google Fonts אוטומטית), איפה לשים `dir="rtl"`, איך להפוך את ציר ה-X של GSAP, איך להפיק כתוביות עברית עם `hyperframes transcribe --language he`, מאיפה להביא קריינות עברית, ואיך לטפל בטקסט מעורב עברית+אנגלית עם `<bdi>`.

## איך ניגשים לבניית סרטון

לפני שמתחילים לכתוב HTML, שוו לרגע בעיניים מה הצופה צריך לקבל:

1. **מה הסיפור?** מהו הקו, איזה רגעים באמת חשובים, ומה הטון הרגשי.
2. **מבנה.** כמה קומפוזיציות, מה inline ומה sub-composition, ובאיזה טרקים יושבים הוידאו, האודיו, האוברלי והכתוביות.
3. **תזמון.** איזה קליפ קובע את האורך, איפה המעברים נוחתים, ומה הקצב.
4. **Layout.** בונים קודם את המצב הסופי. הפירוט ב"Layout Before Animation" למטה.
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
3. **entrances עם `gsap.from()`.** מנפישים מהמצב שמחוץ למסך אל המיקום הסופי שב-CSS.
4. **exits עם `gsap.to()`.** מנפישים מהמיקום שב-CSS אל מחוץ למסך.

## חוזה ה-Timeline

- כל Timeline נפתח עם `{ paused: true }`. הנגן שולט בניגון, לא האנימציה.
- כל Timeline חייב להירשם: `window.__timelines["<composition-id>"] = tl`.
- המנוע מקונן sub-timelines לבד, לא להוסיף אותם ידנית.
- המשך של הקליפ מגיע מ-`data-duration`, לא מאורך ה-Timeline של GSAP.

## כללים נוקשים

- **דטרמיניסטיות קודם לכל.** בלי `Math.random()`, בלי `Date.now()`, בלי שום דבר שתלוי בזמן רץ. צריך ערכים פסאודו-רנדומיים? PRNG עם seed (למשל mulberry32).
- **אין אנימציה על `display` או `visibility`.** עובדים עם opacity ו-transform.
- **אין `repeat: -1`.** מחשבים כמה חזרות מתוך משך הקליפ.
- **לא קוראים ל-`video.play()` ו-`video.pause()`.** המנוע שולט במדיה, נקודה.
- **הבנייה של Timeline היא סינכרונית.** בלי `setTimeout`, בלי `async` בתוך הבנייה.

## מלכודות שסוכני AI נופלים בהן (עברית ו-RTL)

אלו הטעויות הספציפיות של עבודה בעברית. המלכודות הכלליות של HyperFrames (ראו ה-upstream) חלות גם הן.

- **לא להוסיף `<link>` של Google Fonts ולא `@import` ב-CSS לפונטים עבריים.** המהדר של HyperFrames כבר מוריד את Google Fonts מצד השרת דרך `fetchGoogleFont()` (בקובץ `packages/producer/src/services/deterministicFonts.ts`), שומר את ה-WOFF2 ב-`~/.cache/hyperframes/fonts/<slug>/`, ומטמיע אותו כ-base64 data URI ישירות ב-HTML הסופי. stylesheet חיצוני שובר דטרמיניסטיות (פתאום יש תלות ברשת ברנדר) וגם כופל את הטעינה. פשוט כתבו `font-family: 'Heebo', sans-serif;` וזהו.
- **לא להיעזר ב-`hyperframes tts` המובנה לעברית.** Kokoro-82M תומך בדיוק ב-8 שפות: `a`=אנגלית אמריקאית, `b`=אנגלית בריטית, `e`=ספרדית, `f`=צרפתית, `h`=הינדי, `i`=איטלקית, `j`=יפנית, `p`=פורטוגזית ברזילאית, `z`=מנדרינית. האות הראשונה של ה-voice ID קובעת את השפה. עברית לא ברשימה. צריך לייצר את הקריינות במקום חיצוני (ElevenLabs, OpenAI TTS, Google Cloud TTS עם קולות `he-IL-*`) ולהטעין את קובץ ה-WAV/MP3 כאלמנט `<audio>` רגיל בקומפוזיציה.
- **לא להשתמש במודלי `.en` של Whisper על אודיו בעברית.** גרסאות `.en` **מתרגמות** כל שפה שהיא לא אנגלית, לאנגלית, במקום לתמלל. לכתוביות עברית תריצו `npx hyperframes transcribe audio.wav --model small --language he` (או `medium` / `large-v3` כשהאודיו רועש יותר). הסיומת `.en` נכונה רק כשהמשתמש אמר במפורש שהאודיו באנגלית.
- **`dir="rtl"` לא נרשם לבד.** גם אם הקומפוזיציה ברירת המחדל שלה RTL, תת-קומפוזיציות קובעות הקשר כיווני בעצמן. גם tweens של GSAP לא הופכים את הכיוון אוטומטית. כותרת עם `gsap.from({x: -80})` נכנסת משמאל ב-LTR וב-RTL כאחד. לעברית, הפכו לערך חיובי `x: 80` כדי שהכותרת תיכנס מצד ימין, בהתאם לכיוון הקריאה.
- **שמות מותג באנגלית צריכים `<bdi>` או `unicode-bidi: isolate`.** בלי בידוד, האלגוריתם הדו-כיווני של Unicode מסדר מחדש את ה-runs ולעתים ממקם פיסוק בצד הלא נכון, או הופך את המותג ויזואלית. פשוט עוטפים: `הצטרפו ל־<bdi>HyperFrames</bdi> עכשיו`.

## פרטי Bidi בעברית

הכלל של `<bdi>` למעלה מכסה שמות מותג. קומפוזיציות עברית עם כיוון מעורב צריכות עוד שלושה הרגלי bidi:

- **שבירת שורות לכותרות עברית ארוכות.** עברית לא עוברת מיקוף. כותרת עברית ארוכה שגולשת חייבת להישבר בגבולות מילים, לעולם לא באמצע מילה. הגדירו `max-width` כדי שהיא תישבר באופן טבעי, והוסיפו `word-break: keep-all` (או `overflow-wrap: normal`) כדי שהמהדר לא ישבור בתוך מילה עברית. אל תשתמשו ב-`<br>` כדי לכפות שבירה. לכותרות תצוגה שבהן כל מילה בכוונה בשורה משלה, תנו לכל מילה אלמנט נפרד.
- **ספרות ואחוזים בתוך runs של RTL.** ספרות לטיניות (שנים, אחוזים, מחירים) שמוטמעות במשפט עברי הן באג bidi נפוץ: `2025` ליד מילה עברית יכול להתרנדר כ-`5202` או לקפוץ לצד הלא נכון. עטפו כל רצף ספרות ב-`<bdi>` או ב-`⁦...⁩` (LTR isolate): `בשנת <bdi>2025</bdi>`, `<bdi>15%</bdi> הנחה`, `<bdi>₪199</bdi>`. ככה סימן המטבע נשאר צמוד למספר.
- **שיקוף סימני פיסוק.** סוגריים, סוגריים מרובעים ומרכאות הם תווים משוקפים: `(` הופך ויזואלית ל-`)` בתוך run של RTL. בכתוביות ובפסקאות עברית תנו לדפדפן לשקף אותם בזה שתשמרו את הטקסט בתוך קונטיינר `dir="rtl"` תקין. אל תחליפו ידנית `(` ו-`)` כדי "לתקן" את זה, וכשבתוך הסוגריים יש תוכן LTR (מותג, URL, מספר) עטפו את התוכן הפנימי ב-`<bdi>` כך שרק ה-run הפנימי יהיה LTR והסוגריים יישארו משוקפים נכון.

## פתרון בעיות

### הפקודה `hyperframes` לא נמצאת או שהרנדר נכשל מיד
HyperFrames דורש Node 22 ומעלה ו-FFmpeg ב-PATH. ודאו ש-`node --version` הוא 22 ומעלה ושה-`ffmpeg -version` עובד. ב-macOS מתקינים FFmpeg עם `brew install ffmpeg`, ב-Debian/Ubuntu עם `apt install ffmpeg`. בלי FFmpeg המהדר לא יכול לקודד את ה-MP4 והוא עוצר עוד לפני שהוא מרנדר פריים אחד.

### המהדר מזהיר "font not supported" או שהעברית מרונדרת בפונט fallback
המהדר מטמיע רק פונטים שהוא מצליח להוריד מ-Google Fonts. השתמשו במשפחה עברית שקיימת ב-Google Fonts (Heebo, Rubik, Assistant, Alef, Frank Ruhl Libre, Noto Sans Hebrew) וכתבו אותה רגיל ב-CSS: `font-family: 'Heebo', sans-serif;`. אל תוסיפו `<link rel="stylesheet">` או `@import` (ראו מלכודות), זה שובר דטרמיניסטיות בלי לפתור את האזהרה. אם צריך פונט מותאם שלא מ-Google, התיעוד של ה-upstream מכסה הטמעת פונט מקומי.

### ביקורת ניגודיות WCAG נכשלת (`hyperframes validate`)
הפקודה `validate` דוגמת פיקסלים של רקע מאחורי כל אלמנט טקסט בחמישה חותמות זמן ומסמנת יחסים מתחת ל-4.5:1 (טקסט רגיל) או 3:1 (טקסט גדול). מתקנים בזה שמכווננים את הצבע שנכשל בתוך משפחת הפלטה: מבהירים אותו על רקע כהה, מכהים אותו על רקע בהיר. אל תמציאו צבע חדש. תריצו `hyperframes validate` שוב עד שזה נקי. השתמשו ב-`--no-contrast` רק בזמן עבודה, אף פעם לא כמצב סופי.

### הקומפוזיציה מרונדרת ריקה או שהתוכן לא נראה
הסיבה הכי נפוצה היא עטיפת `<template>` על קומפוזיציה standalone. ה-`index.html` הראשי חייב לשים את ה-div עם `data-composition-id` ישירות ב-`<body>`, לא בתוך `<template>`. בדקו גם שכל timeline נרשם דרך `window.__timelines["<composition-id>"] = tl` ושנבנה באופן סינכרוני (לא בתוך `async`, `setTimeout` או Promise), מנוע הלכידה קורא את `window.__timelines` באופן סינכרוני אחרי טעינת הדף.

### כותרת עברית נכנסת מהצד הלא נכון
tweens של `x:` ב-GSAP לא מתהפכים אוטומטית ל-RTL. `gsap.from({x: -80})` נכנס משמאל גם ב-LTR וגם ב-RTL. לעברית, הפכו לערך חיובי (`x: 80`) כדי שהאלמנט ייכנס מצד ימין, בהתאם לכיוון הקריאה. ראו את `references/hebrew-rtl.md`.

## קישורי עזר

| מקור | URL | מה בודקים |
|---|---|---|
| HyperFrames GitHub | https://github.com/heygen-com/hyperframes | ה-repo המקורי, issues, releases |
| HyperFrames docs | https://hyperframes.heygen.com/quickstart | ה-CLI, דרישות Node 22+ ו-FFmpeg |
| לוגיקת הפונטים של המהדר | https://github.com/heygen-com/hyperframes/blob/main/packages/producer/src/services/deterministicFonts.ts | רשימת הפונטים הקנוניים, ה-fallback ל-Google Fonts, נתיב ה-cache |
| קולות Kokoro TTS | https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/narration.md | קולות Kokoro, 8 שפות, בלי עברית |
| מדריך מודלים של Whisper | https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/transcript-guide.md | `.en` מול רב-לשוני, הדגל `--language` |
| Google Fonts עם תמיכה בעברית | https://fonts.google.com/?subset=hebrew | Heebo, Rubik, Assistant, Alef, Frank Ruhl Libre, Noto Sans Hebrew |
| מפרט unicode-bidi | https://developer.mozilla.org/en-US/docs/Web/CSS/unicode-bidi | `isolate`, `<bdi>`, טקסט דו-כיווני |

## References

רשימת הרפרנסים המלאה (palettes, house style, motion principles, transitions, captions, audio-reactive, TTS, typography, dynamic techniques, transcript guide) מופיעה ב-SKILL.md. הקובץ הזה מתרכז רק בשכבת העברית וה-RTL. לעבודה ללא עברית אפשר לפנות ישר ל-SKILL.md.
