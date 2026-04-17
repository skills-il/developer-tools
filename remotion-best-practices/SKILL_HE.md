---
name: remotion-best-practices
description: "שיטות עבודה מומלצות ליצירת סרטונים ב-Remotion עם תמיכה מלאה בעברית ו-RTL. השתמשו כשאתם עובדים עם קוד Remotion, יוצרים סרטונים פרוגרמטיים, בונים תוכן וידאו בעברית עם כתוביות RTL ואנימציות טקסט, או מייצרים סרטוני סושיאל עם פונטים עבריים. מכסה אנימציות, קומפוזיציות, סיקוונסים, מעברים, אודיו/וידאו, כתוביות, תלת-ממד, גרפים, קריינות, ורינדור טקסט עברי RTL מלא. אל תשתמשו לעריכת וידאו שאינה Remotion, פיתוח React כללי, או יצירת תמונות סטטיות."
license: MIT
---

# שיטות עבודה מומלצות ב-Remotion למפתחים ישראלים

## בעיה

יצירת סרטונים פרוגרמטיים עם טקסט עברי ב-Remotion שבורה כברירת מחדל. הפטרנים הסטנדרטיים של Remotion מייצרים טקסט עם יישור שמאלי, אנימציות מכונת כתיבה שנחשפות משמאל לימין, וכתוביות שמרונדרות הפוך עבור תוכן RTL. מפתחים ישראלים מבזבזים שעות על דיבוג בעיות RTL, טעינת פונטים עבריים לא נכונה, ובאגים של טקסט דו-כיווני שהתיעוד הסטנדרטי של Remotion לא מתייחס אליהם.

## הוראות

### מתי להשתמש

השתמשו בסקיל הזה בכל פעם שאתם עובדים עם קוד Remotion, במיוחד כשיוצרים תוכן וידאו בעברית או דו-לשוני.

### הקמת פרויקט חדש

בתיקייה ריקה או workspace ללא פרויקט Remotion קיים:

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

לכל תוכן וידאו בעברית, טענו את הקובץ [./rules/hebrew-rtl.md](./rules/hebrew-rtl.md). הוא מכסה:

- פונטים עבריים מ-Google (Heebo, Rubik, Assistant, Noto Sans Hebrew) עם `subsets: ["hebrew"]`
- כיוון טקסט RTL (`direction: "rtl"`, `textAlign: "right"`)
- טיפול בטקסט דו-כיווני (Unicode bidi isolates לשילוב עברית/אנגלית)
- כתוביות עבריות עם הדגשת מילים בזמן אמת
- אפקט מכונת כתיבה עברית (חשיפת תווים מימין לשמאל)
- קריינות עברית עם ElevenLabs multilingual v2
- קואורדינטות מפה ישראליות ותוויות מפה בעברית

### כתוביות

לעבודה עם כתוביות, טענו את [./rules/subtitles.md](./rules/subtitles.md).

### שימוש ב-FFmpeg

לפעולות וידאו כמו חיתוך וזיהוי שקט, טענ�� את [./rules/ffmpeg.md](./rules/ffmpeg.md).

### קבצי כללים

קראו קבצי כללים בודדים להסברים מפורטים ודוגמאות קוד:

- [rules/hebrew-rtl.md](rules/hebrew-rtl.md) - טקסט עברי RTL, פונטים, כתוביות, bidi ומפות ישראליות
- [rules/3d.md](rules/3d.md) - תוכן תלת-ממדי עם Three.js ו-React Three Fiber
- [rules/animations.md](rules/animations.md) - יסודות אנימציה ב-Remotion
- [rules/assets.md](rules/assets.md) - ייבוא תמונות, סרטונים, אודיו ופונטים
- [rules/audio.md](rules/audio.md) - שימוש באודיו ב-Remotion
- [rules/calculate-metadata.md](rules/calculate-metadata.md) - הגדרת משך, מימדים ו-props דינמיים
- [rules/charts.md](rules/charts.md) - גרפים והצגת נתונים
- [rules/compositions.md](rules/compositions.md) - הגדרת קומפוזיציות, stills ותיקיות
- [rules/display-captions.md](rules/display-captions.md) - כתוביות בסגנון TikTok עם הדגשת מילים
- [rules/fonts.md](rules/fonts.md) - טעינת Google Fonts ופונטים מקומיים
- [rules/images.md](rules/images.md) - הטמעת תמונות עם קומפוננטת Img
- [rules/sequencing.md](rules/sequencing.md) - פטרנים של סיקוונסים לתזמון והשהייה
- [rules/text-animations.md](rules/text-animations.md) - אנימציות טיפוגרפיה וטקסט
- [rules/timing.md](rules/timing.md) - עקומות אינטרפולציה, easing ואנימציות spring
- [rules/transitions.md](rules/transitions.md) - פטרנים של מעברים בין סצנות
- [rules/videos.md](rules/videos.md) - הטמעת סרטונים עם חיתוך, ווליום ומהירות
- [rules/voiceover.md](rules/voiceover.md) - קריינות AI עם ElevenLabs TTS

## מלכודות נפוצות

1. **אנימציות CSS אסורות ב-Remotion.** לעולם אל תשתמשו ב-`transition-*`, `animate-*`, `@keyframes` או מחלקות אנימציה של Tailwind. כל התנועה חייבת להיות מונעת על ידי `useCurrentFrame()`.

2. **טקסט עברי ללא `direction: "rtl"` מרונדר הפוך.** סימני פיסוק, מספרים וסוגריים יופיעו בצד הלא נכון.

3. **מודל Whisper `medium.en` לא תומך בעברית.** השתמשו ב-`medium` (המודל הרב-לשוני) לתמלול עברי.

4. **`useFrame()` מ-React Three Fiber אסור.** בתוך `<ThreeCanvas>` רק `useCurrentFrame()` מ-Remotion מותר. שימוש ב-`useFrame()` גורם להבהוב ברינדור.

5. **אלמנטי `<img>` ו-`<video>` מקוריים גורמים לפריימים ריקים.** תמיד השתמשו ב-`<Img>` מ-remotion וב-`<Video>` מ-`@remotion/media`.

## קישורי עזר

| מקור | URL | מה לבדוק |
|------|-----|----------|
| תיעוד Remotion | https://www.remotion.dev/docs | API reference, שינויי גרסה |
| GitHub של Remotion | https://github.com/remotion-dev/remotion | קוד מקור, issues, releases |
| @remotion/google-fonts | https://www.remotion.dev/docs/google-fonts | פונטים עם תמיכה בעברית |
| @remotion/captions | https://www.remotion.dev/docs/captions | סוגי כתוביות, API לכתוביות TikTok |
| ElevenLabs TTS | https://elevenlabs.io/docs | מודל multilingual v2, תמיכה בקולות עבריים |
| Google Fonts Hebrew | https://fonts.google.com/?subset=hebrew | עיון בפונטים התומכים בעברית |

## פתרון בעיות

### טקסט עברי מיושר לשמאל
הוסיפו `direction: "rtl"` ו-`textAlign: "right"` לסגנון הקונטיינר.

### כתוביות מציגות מילים בסדר הפוך
הקונטיינר צריך `direction: "rtl"` ו-`whiteSpace: "pre"`.

### פונט עברי לא מרונדר (מציג ריבועים)
ודאו שטענתם את הפונט עם `subsets: ["hebrew"]` וקראתם ל-`waitUntilDone()`.

### מספרים מופיעים בצד הלא נכון של טקסט עברי
השתמשו ב-Unicode bidi isolates: עטפו מספרים עם `\u2066...\u2069` בתוך טקסט עברי.

### Whisper מייצר ג'יבריש לאודיו עברי
החליפו ממודל `medium.en` למודל `medium`. הסיומת `.en` פירושה אנגלית בלבד.
