---
name: remotion-best-practices
description: "איך ליצור סרטונים מקוד עם Remotion ב-React, כולל תמיכה מלאה בעברית ו-RTL. השתמשו כשאתם עובדים עם Remotion, כשאתם יוצרים סרטונים פרוגרמטיים, כשאתם בונים תוכן וידאו בעברית עם כתוביות RTL ואנימציות טקסט, או כשאתם מייצרים סרטוני סושיאל עם פונטים עבריים. כולל אנימציות, קומפוזיציות, סיקוונסים, מעברים, אודיו/וידאו, כתוביות, תלת-ממד, גרפים, קריינות, ורינדור טקסט עברי RTL. אל תשתמשו לעריכת וידאו מחוץ ל-Remotion, לפיתוח React כללי, או ליצירת תמונות סטטיות."
license: MIT
---

# Remotion למפתחים ישראלים

## בעיה

יצירת סרטונים מקוד עם טקסט עברי ב-Remotion פשוט לא עובדת out of the box. ברירת המחדל של Remotion מייצרת טקסט עם יישור שמאלי, אנימציות מכונת כתיבה שרצות משמאל לימין, וכתוביות שמרונדרות הפוך בתוכן RTL. מפתחים ישראלים מבזבזים שעות על דיבוג בעיות RTL, טעינת פונטים לא נכונה, ובאגים של טקסט דו-כיווני שהדוקומנטציה של Remotion פשוט לא מכסה.

## הוראות

### מתי להשתמש

השתמשו בסקיל הזה כשאתם עובדים עם קוד Remotion, במיוחד כשיוצרים תוכן וידאו בעברית או דו-לשוני.

### הקמת פרויקט חדש

בתיקייה ריקה בלי פרויקט Remotion:

```bash
npx create-video@latest --yes --blank --no-tailwind my-video
```

### הרצת תצוגה מקדימה

```bash
npx remotion studio
```

### בדיקת פריים בודד (אופציונלי)

```bash
npx remotion still [composition-id] --scale=0.25 --frame=30
```

### יצירת וידאו עברי עם RTL

לכל תוכן וידאו בעברית, טענו את [./rules/hebrew-rtl.md](./rules/hebrew-rtl.md). בפנים תמצאו:

- פונטים עבריים מ-Google (Heebo, Rubik, Assistant, Noto Sans Hebrew) עם `subsets: ["hebrew"]`
- כיוון טקסט RTL (`direction: "rtl"`, `textAlign: "right"`)
- עבודה עם טקסט דו-כיווני (Unicode bidi isolates לשילוב עברית/אנגלית)
- כתוביות עבריות עם הדגשת מילים בזמן אמת
- אפקט מכונת כתיבה עברית (חשיפת תווים מימין לשמאל)
- קריינות עברית עם ElevenLabs multilingual v2
- נקודות ציון של ערים ישראליות ותוויות מפה בעברית

### כתוביות

לעבודה עם כתוביות, טענו את [./rules/subtitles.md](./rules/subtitles.md).

### שימוש ב-FFmpeg

לפעולות וידאו כמו חיתוך וזיהוי שקט, טענו את [./rules/ffmpeg.md](./rules/ffmpeg.md).

### זיהוי שקט

כשצריך לזהות ולחתוך קטעים שקטים מקבצי וידאו או אודיו, טענו את [./rules/silence-detection.md](./rules/silence-detection.md).

### ויזואליזציה של אודיו

כשצריך להציג גלים של אודיו (עמודות ספקטרום, צורות גל, אפקטים שמגיבים לבאס), טענו את [./rules/audio-visualization.md](./rules/audio-visualization.md).

### אפקטים קוליים

כשצריך להוסיף אפקטים קוליים, טענו את [./rules/sfx.md](./rules/sfx.md).

### רינדור ורינדור בענן

סטודיו הוא לתצוגה מקדימה בלבד. כדי להפיק קובץ וידאו סופי צריך לרנדר אותו. טענו את [./rules/rendering.md](./rules/rendering.md) בשביל פקודת `npx remotion render`, הדגלים המרכזיים (`--concurrency`, `--scale`, `--codec`) ורינדור בענן עם `@remotion/lambda` ו-`@remotion/cloudrun`.

### קבצי כללים

כל קובץ כללים מכיל הסברים מפורטים עם דוגמאות קוד:

- [rules/hebrew-rtl.md](rules/hebrew-rtl.md) - טקסט עברי RTL, פונטים, כתוביות, bidi ומפות ישראליות
- [rules/3d.md](rules/3d.md) - תוכן תלת-ממדי עם Three.js ו-React Three Fiber
- [rules/animations.md](rules/animations.md) - יסודות אנימציה ב-Remotion
- [rules/assets.md](rules/assets.md) - ייבוא תמונות, סרטונים, אודיו ופונטים
- [rules/audio.md](rules/audio.md) - שימוש באודיו ב-Remotion
- [rules/calculate-metadata.md](rules/calculate-metadata.md) - הגדרת משך, מימדים ו-props דינמיים
- [rules/can-decode.md](rules/can-decode.md) - בדיקה אם וידאו יכול להיפתח בדפדפן
- [rules/charts.md](rules/charts.md) - גרפים והצגת נתונים
- [rules/compositions.md](rules/compositions.md) - הגדרת קומפוזיציות, stills ותיקיות
- [rules/display-captions.md](rules/display-captions.md) - כתוביות בסגנון TikTok עם הדגשת מילים
- [rules/extract-frames.md](rules/extract-frames.md) - שליפת פריימים מוידאו בזמנים ספציפיים
- [rules/fonts.md](rules/fonts.md) - טעינת Google Fonts ופונטים מקומיים
- [rules/get-audio-duration.md](rules/get-audio-duration.md) - קבלת משך אודיו עם Mediabunny
- [rules/get-video-dimensions.md](rules/get-video-dimensions.md) - קבלת רוחב וגובה של וידאו
- [rules/get-video-duration.md](rules/get-video-duration.md) - קבלת משך וידאו בשניות
- [rules/gifs.md](rules/gifs.md) - הצגת GIFs מסונכרנים לציר הזמן
- [rules/images.md](rules/images.md) - הטמעת תמונות עם קומפוננטת Img
- [rules/import-srt-captions.md](rules/import-srt-captions.md) - ייבוא קבצי כתוביות srt
- [rules/light-leaks.md](rules/light-leaks.md) - אפקטים של דליפת אור
- [rules/lottie.md](rules/lottie.md) - הטמעת אנימציות Lottie
- [rules/maps.md](rules/maps.md) - אנימציות מפה עם Mapbox
- [rules/measuring-dom-nodes.md](rules/measuring-dom-nodes.md) - מדידת מימדים של אלמנטי DOM
- [rules/measuring-text.md](rules/measuring-text.md) - מדידת מימדי טקסט והתאמה לקונטיינר
- [rules/parameters.md](rules/parameters.md) - הפיכת סרטון לפרמטרי עם Zod
- [rules/sequencing.md](rules/sequencing.md) - פטרנים של סיקוונסים לתזמון והשהייה
- [rules/silence-detection.md](rules/silence-detection.md) - זיהוי שקט אדפטיבי עם FFmpeg
- [rules/tailwind.md](rules/tailwind.md) - שימוש ב-TailwindCSS ב-Remotion
- [rules/text-animations.md](rules/text-animations.md) - אנימציות טיפוגרפיה וטקסט
- [rules/timing.md](rules/timing.md) - עקומות אינטרפולציה, easing ואנימציות spring
- [rules/transcribe-captions.md](rules/transcribe-captions.md) - תמלול אודיו לכתוביות עם Whisper
- [rules/transitions.md](rules/transitions.md) - פטרנים של מעברים בין סצנות
- [rules/transparent-videos.md](rules/transparent-videos.md) - רינדור וידאו שקוף
- [rules/trimming.md](rules/trimming.md) - פטרנים של חיתוך אנימציות
- [rules/videos.md](rules/videos.md) - הטמעת סרטונים עם חיתוך, ווליום ומהירות
- [rules/rendering.md](rules/rendering.md) - רינדור סרטונים מקומית ובענן (Lambda, Cloud Run)
- [rules/voiceover.md](rules/voiceover.md) - קריינות AI עם ElevenLabs TTS

## דוגמאות

### דוגמה 1: סרטון כתוביות בסגנון TikTok בעברית

המשתמש רוצה קליפ סושיאל אנכי (1080x1920) עם קריינות בעברית וכתוביות עם הדגשת מילים.

אחד, מקימים פרויקט: `npx create-video@latest --yes --blank --no-tailwind my-video`.
שתיים, מייצרים את הקריינות בעברית (טוענים את `rules/voiceover.md`, ElevenLabs multilingual v2).
שלוש, מתמללים את הקריינות לכתוביות (טוענים את `rules/transcribe-captions.md`, משתמשים במודל הרב-לשוני `medium`, אף פעם לא `medium.en`).
ארבע, מרנדרים כתוביות בסגנון TikTok עם הדגשת מילים (טוענים את `rules/display-captions.md` ואת `rules/hebrew-rtl.md`): מגדירים `direction: "rtl"`, `textAlign: "right"` ועוטפים ספרות לטיניות מוטמעות ב-bidi isolates.
חמש, מגדירים קומפוזיציה בגודל 1080x1920 ומקטינים את הפונט העברי בשתי דרגות מתחת לגודל שהייתם נותנים באנגלית (מלכודת 7).
שש, מציגים תצוגה מקדימה ב-`npx remotion studio` ואז מרנדרים עם `npx remotion render` (טוענים את `rules/rendering.md`).

### דוגמה 2: סרטון גרף מבוסס נתונים

המשתמש רוצה סרטון הסבר ביחס 16:9 שבו גרף עמודות מונפש מתוך מערך נתונים JSON.

אחד, הופכים את הקומפוזיציה לפרמטרית עם סכמת Zod (טוענים את `rules/parameters.md`) כך שמערך הנתונים הוא prop עם טיפוס.
שתיים, מחשבים משך ומימדים מתוך הנתונים ב-`calculateMetadata` (טוענים את `rules/calculate-metadata.md`); שומרים על זה עצל כדי לא להאט כל רינדור.
שלוש, בונים גרף עמודות מונפש שמונע על ידי `useCurrentFrame()` ועקומות אינטרפולציה/spring (טוענים את `rules/charts.md` ואת `rules/timing.md`). אף פעם לא משתמשים באנימציות CSS (מלכודת 1).
ארבע, בשביל תוויות צירים וכותרות בעברית, מחילים כיוון RTL ו-bidi isolates סביב מספרים (טוענים את `rules/hebrew-rtl.md`).
חמש, מרנדרים ל-MP4 עם `npx remotion render`, או מרנדרים בכמות גדולה בענן עם `@remotion/lambda` (טוענים את `rules/rendering.md`).

## משאבים מצורפים

### קבצי כללים (`rules/`)

תיקיית `rules/` מכילה קבצי נושא ממוקדים שנטענים לפי הצורך. בין השאר: `hebrew-rtl.md` (פונטים עבריים, RTL, bidi, מפות ישראליות), `animations.md`, `timing.md`, `sequencing.md`, `transitions.md`, `compositions.md`, `calculate-metadata.md`, `parameters.md`, `charts.md`, `text-animations.md`, `3d.md`, קבצי אודיו (`audio.md`, `audio-visualization.md`, `sfx.md`, `voiceover.md`, `get-audio-duration.md`, `silence-detection.md`), קבצי וידאו (`videos.md`, `assets.md`, `images.md`, `gifs.md`, `lottie.md`, `transparent-videos.md`, `light-leaks.md`, `maps.md`, `tailwind.md`, `fonts.md`), קבצי כתוביות (`subtitles.md`, `display-captions.md`, `transcribe-captions.md`, `import-srt-captions.md`), עוזרי מדידה ופענוח (`measuring-dom-nodes.md`, `measuring-text.md`, `can-decode.md`, `extract-frames.md`, `get-video-dimensions.md`, `get-video-duration.md`, `trimming.md`), `ffmpeg.md` ו-`rendering.md`. הרשימה המלאה נמצאת תחת "קבצי כללים" למעלה.

### נכסים (`rules/assets/`)

דוגמאות קומפוננטות TSX מוכנות לשימוש שקבצי הכללים מפנים אליהן: `charts-bar-chart.tsx` (גרף עמודות מונפש), `text-animations-typewriter.tsx` (אפקט מכונת כתיבה) ו-`text-animations-word-highlight.tsx` (הדגשת כתוביות מילה אחר מילה).

## מלכודות נפוצות

1. **אנימציות CSS אסורות ב-Remotion.** אל תשתמשו ב-`transition-*`, `animate-*`, `@keyframes` או קלאסים של Tailwind animation. כל תנועה חייבת לעבור דרך `useCurrentFrame()`. אנימציות CSS לא ירונדרו נכון בייצוא הסרטון.

2. **טקסט עברי בלי `direction: "rtl"` מרונדר הפוך.** סימני פיסוק, מספרים וסוגריים יקפצו לצד הלא נכון.

3. **מודל Whisper `medium.en` לא מבין עברית.** תמלול עברי דורש את `medium` (בלי ה-en). הסיומת `.en` אומרת אנגלית בלבד.

4. **`useFrame()` של React Three Fiber אסור לשימוש.** בתוך `<ThreeCanvas>`, רק `useCurrentFrame()` של Remotion. `useFrame()` גורם להבהוב כי הוא מנפש מחוץ לציר הזמן של Remotion.

5. **אלמנטי `<img>` ו-`<video>` רגילים יגרמו לפריימים ריקים.** תמיד תשתמשו ב-`<Img>` מ-remotion וב-`<Video>` מ-`@remotion/media`. הם מוודאים שהקובץ נטען לפני הרינדור.

6. **RTL הופך את `flex-start` ו-`flex-end`.** בתוך flex עם RTL, `flex-start` זה ימין ו-`flex-end` זה שמאל -- ההפך ממה שמצפים. כדי ליישר שורות אייקון+טקסט לימין בעברית, תשתמשו ב-`justifyContent: "flex-start"` (לא `flex-end`). הכיוון RTL כבר הופך את סדר ה-DOM, אז האלמנט הראשון (אייקון) מרונדר בצד ימין. אל תשתמשו ב-`flexDirection: "row-reverse"` בתוך RTL -- זה הופך פעמיים וחוזר לסדר LTR.

7. **טקסט עברי נשבר לשורה שנייה בגודל פונט שבו אנגלית נכנסת בשורה אחת.** פונטים עבריים (Heebo, Rubik, Assistant) בגדלים גדולים רחבים ב-20-30% מאנגלית באותו גודל. אם כותרת באנגלית עובדת ב-`fontSize: 72`, הגרסה העברית צריכה `54-60`. תוסיפו גם `flexWrap: "nowrap"` ו-`whiteSpace: "nowrap"` לכל שורת flex עם מילים עבריות גדולות כדי למנוע שבירת שורה באמצע המשפט.

8. **כתוביות עבריות חייבות להישמע ישראלי, לא מתורגם.** תתרחקו מביטויים קורפורטיביים כמו "תמיכה מלאה", מתיאורים בבניין סביל, ומתרגומים מילוליים של ביטויים באנגלית. סלנג של מפתחים ישראלים: "עולים" (load), "נופלת" (falls), "אפקט הקלדה" (לא "מכונת כתיבה"). תשתמשו ב-"אפשר" לא "ניתן", בבניין פעיל, ותפזרו מחברים טבעיים כמו "סוף סוף", "כמו שצריך", "באמת".

9. **לעולם אל תשתמשו ב-em dash או en dash.** תחליפו אותם בפסיק, נקודתיים, סוגריים או שני מקפים (`--`). הם לא על מקלדת סטנדרטית, לא תמיד מרונדרים נכון, וגורמים לטקסט להרגיש כאילו מכונה כתבה אותו. הכלל תקף גם באנגלית וגם בעברית בקובצי SKILL.md, כתוביות וטקסט ממשק.

10. **רמושן לא חינמי בלי תנאים.** הוא חינמי ליחידים, למלכ"רים ולארגונים עסקיים עם 3 עובדים או פחות. ארגונים של 4 עובדים ומעלה חייבים לקנות רישיון Company License בתשלום מ-remotion.pro. זה תקף לשימוש ב-Remotion בכלל (סטודיו, רינדור, CI), לא רק לפיצ'ר מסוים. בדקו את https://www.remotion.dev/docs/license ואת קובץ ה-`LICENSE` המצורף לפני שמשחררים פרויקט מסחרי.

11. **כווננו את ביצועי הרינדור, אל תקבלו סתם את ברירות המחדל.** הורידו את `--concurrency` אם רינדור נגמר לו הזיכרון; העלו אותו במכונות עם הרבה ליבות בשביל רינדור מהיר יותר. השתמשו ב-`--scale` קטן מ-1 לרינדור טיוטה מהיר וגדול מ-1 למאסטר ברזולוציה גבוהה. העדיפו את `<OffthreadVideo>` על פני `<Video>` לוידאו מוטמע בזמן רינדור (הוא שולף פריימים בצורה דטרמיניסטית מחוץ ל-thread הראשי). שמרו על `calculateMetadata` זול ועצל כי הוא רץ לפני כל רינדור. ראו את `rules/rendering.md`.

## קישורי עזר

| מקור | URL | מה לבדוק |
|------|-----|----------|
| תיעוד Remotion | https://www.remotion.dev/docs | API reference, שינויי גרסה |
| GitHub של Remotion | https://github.com/remotion-dev/remotion | קוד מקור, issues, releases |
| רישיון Remotion | https://www.remotion.dev/docs/license | חינמי מול רישיון בתשלום, סף 4 עובדים ומעלה |
| רינדור / CLI של Remotion | https://www.remotion.dev/docs/cli/render | דגלי `npx remotion render`: concurrency, scale, codec |
| @remotion/lambda | https://www.remotion.dev/docs/lambda | רינדור בענן על AWS Lambda בכמות גדולה |
| @remotion/google-fonts | https://www.remotion.dev/docs/google-fonts | פונטים עם תמיכה בעברית |
| @remotion/captions | https://www.remotion.dev/docs/captions | סוגי כתוביות, API לכתוביות TikTok |
| ElevenLabs TTS | https://elevenlabs.io/docs | מודל multilingual v2, תמיכה בקולות עבריים |
| Google Fonts Hebrew | https://fonts.google.com/?subset=hebrew | עיון בפונטים התומכים בעברית |

## פתרון בעיות

### טקסט עברי מיושר לשמאל
הוסיפו `direction: "rtl"` ו-`textAlign: "right"` לסגנון של כל אלמנט עם טקסט עברי. בלייאאוט של פריים מלא, שימו `direction: "rtl"` על ה-`<AbsoluteFill>`. בלי זה גם סימני פיסוק יופיעו בצד הלא נכון.

### כתוביות מציגות מילים בסדר הפוך
הקונטיינר צריך `direction: "rtl"` וגם `whiteSpace: "pre"`. בלי RTL, סדר הרינדור של הטוקנים הוא LTR וההדגשה של המילה הנוכחית תופיע על המילה הלא נכונה.

### פונט עברי לא מרונדר (מציג ריבועים)
ודאו שטענתם את הפונט עם `subsets: ["hebrew"]` וקראתם ל-`waitUntilDone()` לפני שמתחילים לרנדר. בלי ה-subset, הגליפים העבריים לא יורדים בכלל.

### מספרים מופיעים בצד הלא נכון של טקסט עברי
השתמשו ב-Unicode bidi isolates: עטפו מספרים או שמות אנגליים עם `\u2066...\u2069` (LTR Isolate) בתוך טקסט עברי. בלי זה, אלגוריתם ה-bidi של הדפדפן עשוי לערבב את הסדר.

### Whisper מייצר ג'יבריש לאודיו עברי
החליפו ממודל `medium.en` למודל `medium`. הסיומת `.en` פירושה אנגלית בלבד - המודל הרב-לשוני תומך בעברית ובעוד עשרות שפות.

### אייקונים מופיעים בצד הלא נכון בשורות של flex
בתוך RTL, `justifyContent: "flex-start"` מיישר לימין, לא לשמאל. אל תשתמשו ב-`flexDirection: "row-reverse"` כי הוא הופך את הסדר פעמיים. פשוט שימו את האייקון כאלמנט הראשון ב-DOM.
