---
name: cloudinary-assets
description: Manage media assets through Cloudinary's REST API -- upload, transform, optimize, and deliver images and videos. Use when user asks about image upload, media optimization, image transformations, responsive images, video management, CDN delivery, or mentions Cloudinary specifically. Covers Upload API, Admin API, URL-based transformations, AI-powered effects (gen_remove, gen_replace, background removal), and delivery optimization. Israeli-founded (2012) with R&D in Petah Tikva; global HQ in San Jose, California. Do NOT use for non-Cloudinary media hosting or local image processing without cloud upload.
license: MIT
allowed-tools: Bash(python:*) Bash(curl:*) WebFetch
compatibility: Requires Cloudinary account (free tier available). Needs CLOUDINARY_URL or API key/secret/cloud name environment variables.
---

# ניהול מדיה ב-Cloudinary

## הוראות

### שלב 1: אימות הגדרות Cloudinary
בדקו שקיימים פרטי התחברות ל-Cloudinary:

```python
import os

def get_cloudinary_config():
    """Get Cloudinary config from environment."""
    # Option 1: CLOUDINARY_URL (preferred)
    cloudinary_url = os.environ.get('CLOUDINARY_URL')
    if cloudinary_url:
        return {"url": cloudinary_url}

    # Option 2: Individual variables
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    if all([cloud_name, api_key, api_secret]):
        return {"cloud_name": cloud_name, "api_key": api_key, "api_secret": api_secret}

    return None  # Credentials not configured
```

אם לא מוגדר, הנחו את המשתמש:
1. הירשמו בכתובת https://cloudinary.com (מסלול חינמי: 25 קרדיטים בחודש)
2. את שם הענן, מפתח ה-API והסוד מוצאים בעמוד API Keys שבהגדרות הקונסול (Console Settings)
3. הגדירו CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME

### שלב 2: בחירת פעולה

| פעולה | API | שיטה | מתי |
|-------|-----|-------|------|
| העלאת תמונה | Upload API | POST /image/upload | תמונה חדשה לאחסון |
| העלאת וידאו | Upload API | POST /video/upload | וידאו חדש לאחסון |
| שינוי תמונה | מבוסס URL | GET (URL) | שינוי גודל, חיתוך, אפקטים |
| מיטוב הגשה | מבוסס URL | GET (URL) | שיפור ביצועים |
| רשימת נכסים | Admin API | GET /resources | עיון בספריית המדיה |
| מחיקת נכס | Upload API | POST /{resource_type}/destroy | הסרת מדיה (image, video או raw) |
| פרטי נכס | Admin API | GET /resources/{id} | בדיקת מטא-דאטה |

### שלב 3: העלאת מדיה

**העלאת תמונה:**
```python
import requests
import hashlib
import time

def upload_image(file_path, cloud_name, api_key, api_secret,
                 folder="", asset_folder="", tags=None):
    """Upload image to Cloudinary."""
    timestamp = str(int(time.time()))

    # כל פרמטר העלאה חוץ מ-file, cloud_name, api_key, resource_type והחתימה עצמה
    # חייב להיכנס למחרוזת החתומה, ממוינת לפי א-ב. חתימה על חלק מהפרמטרים בלבד
    # (למשל בלי tags) מחזירה "Invalid Signature".
    params = {"timestamp": timestamp}
    if folder:
        params["folder"] = folder            # מצב תיקיות קבוע
    if asset_folder:
        params["asset_folder"] = asset_folder  # מצב תיקיות דינמי (חשבונות חדשים)
    if tags:
        params["tags"] = ",".join(tags)

    params_to_sign = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    signature = hashlib.sha1(
        f"{params_to_sign}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    data = {"api_key": api_key, "signature": signature, **params}

    with open(file_path, "rb") as f:
        response = requests.post(url, data=data, files={"file": f}, timeout=(10, 180))
    response.raise_for_status()
    return response.json()
```

**קבצים מעל 100 MB (רוב הסרטונים האמיתיים)** לא עוברים ב-POST יחיד כזה. Cloudinary מחייב עבורם העלאה במקטעים: משתמשים ב-`upload_large` של ה-SDK בצד השרת (`cloudinary.uploader.upload_large` ב-Python, `cloudinary.v2.uploader.upload_large` ב-Node), ותמיד מעבירים `resource_type="video"` כשמדובר בוידאו. לא סומכים על ברירת המחדל של ה-SDK: בקוד המקור העדכני `upload_large` נופל ל-`raw`, ונכס raw לא מקבל טרנספורמציות וידאו, כך שכל URL של `/video/upload/` עבורו נכשל. העלאה במקטעים לא מגדילה את מגבלת הגודל של התוכנית (ראו פתרון בעיות). בטרנספורמציות eager לוידאו מעבירים גם `eager_async=true` כדי שהקידוד ירוץ ברקע ולא יחסום את ההעלאה, ואת `eager_notification_url` כדי לקבל הודעה כשהוא מסתיים.

**העלאה מהדפדפן או מאפליקציית Next.js.** אף פעם לא שולחים את `api_secret` לצד הלקוח. יש שתי דרכים מתועדות, וכל אחת מהן היא גם הפתרון לשגיאת "blocked by CORS policy" בהעלאה ישירה מהדפדפן:

1. **חתומה (מומלצת להעלאות של משתמשים).** הדפדפן מבקש חתימה מהשרת שלכם ואז מעלה ישירות. עם `next-cloudinary` מעבירים ל-`CldUploadWidget` את `signatureEndpoint`:
   ```ts
   // app/api/sign-cloudinary-params/route.ts (server only)
   import { v2 as cloudinary } from "cloudinary";
   export async function POST(request: Request) {
     // Authenticate the caller first: this route signs whatever it is sent.
     const { paramsToSign } = await request.json();
     const signature = cloudinary.utils.api_sign_request(paramsToSign, process.env.CLOUDINARY_API_SECRET!);
     return Response.json({ signature });
   }
   ```
   ```tsx
   import { CldUploadWidget } from "next-cloudinary";
   <CldUploadWidget signatureEndpoint="/api/sign-cloudinary-params">
     {({ open }) => <button onClick={() => open()}>Upload</button>}
   </CldUploadWidget>
   ```
   משתני סביבה: `NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME`, `NEXT_PUBLIC_CLOUDINARY_API_KEY` (המפתח יכול להיות ציבורי), ו-`CLOUDINARY_API_SECRET` (בשרת בלבד). החבילה `next-cloudinary` כוללת גם את `CldImage` ואת `CldVideoPlayer` להגשה.
2. **לא חתומה.** preset מסוג unsigned שמצוין בבקשה בשם `upload_preset`. כל מי שרואה את שם ה-preset יכול להעלות איתו, ולכן חייבים להקשיח אותו (ראו מלכודות נפוצות).

### שלב 4: טרנספורמציות תמונה דרך URL

בנו כתובות URL לטרנספורמציות לפי התבנית הבאה:
```
https://res.cloudinary.com/{cloud_name}/image/upload/{transformations}/{public_id}.{format}
```

**מתכוני טרנספורמציה נפוצים:**

| מטרה | טרנספורמציה | דוגמה |
|------|-------------|-------|
| תמונה ממוזערת | w_150,h_150,c_fill,g_face | תמונה ממוזערת 150x150 עם זיהוי פנים |
| תמונת גיבור | w_1200,h_600,c_fill,q_auto,f_auto | באנר ראשי ממוטב |
| תמונת פרופיל | w_200,h_200,c_thumb,g_face,r_max | חיתוך עגול עם זיהוי פנים |
| תמונת מוצר | w_800,h_800,c_pad,b_white | ריפוד על רקע לבן |
| שיתוף חברתי | w_1200,h_630,c_fill | גודל תמונת OpenGraph |
| סימן מים | l_{your_logo_public_id},w_200,o_50/fl_layer_apply,g_south_east | סימן מים שקוף למחצה. מחליפים את ה-placeholder ב-public ID אמיתי: `l_watermark` בחשבון שאין בו נכס כזה מחזיר 400 `Resource not found - watermark` |

**מצב התיקיות משנה.** ל-Cloudinary יש שני מצבים, וסביבות מוצר חדשות נוצרות ב-**dynamic folder mode**.
במצב הזה הפרמטר שממקם נכס בעץ התיקיות הוא `asset_folder`, והוא לא משפיע על ה-public ID. הפרמטר
הוותיק `folder` שייך ל-fixed folder mode, שבו התיקייה נהיית חלק מה-public ID. כלומר העברת `folder`
בחשבון שנמצא ב-dynamic mode לא עושה את מה שמדריך ישן מרמז. בדקו את מצב התיקיות של סביבת המוצר
בהגדרות לפני שכותבים סקריפט להעלאות בכמות, והעבירו `asset_folder` כשאתם ב-dynamic mode.

### שלב 4ב: טרנספורמציות מבוססות AI

האפקטים הגנרטיביים של Cloudinary (gen_remove, gen_replace, gen_background_replace, gen_recolor, gen_restore) זמינים כפרמטרי `e_gen_*` ב-URL. מילוי גנרטיבי הוא היוצא מן הכלל: הוא מבדל רקע `b_gen_fill:prompt_<טקסט>` שמשתמשים בו יחד עם crop של padding באותו רכיב, למשל `c_pad,w_1600,h_900,b_gen_fill:prompt_beach` (מחזיר 200). שתי מלכודות: הפרומפט בלי סוגריים בדיוק כמו ב-`e_gen_background_replace` (הצורה `b_gen_fill:prompt_(beach)` מחזירה HTTP 500 עם `General Error`), ובלי crop של padding מוחזר HTTP 400 עם `gen_fill only available for padding crop modes` שממלא אזור מרופד, ולא אפקט `e_gen_fill` (בנייה של `e_gen_fill:...` מחזירה 400). חלק מהווריאנטים עדיין מסומנים כ-Beta בתיעוד, אז כדאי לבדוק את הסטטוס העדכני לפני שמסתמכים על אפקט ספציפי בפרודקשן:

| פרמטר | מה הוא עושה |
|--------|--------------|
| `e_gen_remove:prompt_(person)` | מוחק עם AI את האובייקט שמתאים לתיאור |
| `e_gen_replace:from_car;to_bicycle` | מחליף עם AI אובייקט אחד באחר (הצורה המתועדת היא בלי סוגריים). שגיאת 400 `Invalid input for gen_replace` פירושה בדרך כלל שאובייקט ה-`from` לא נמצא בתמונה, ולא שהתחביר שגוי |
| `e_gen_background_replace:prompt_beach%20at%20sunset` | מחליף את הרקע באופן גנרטיבי. שימו לב שהפרומפט כאן לא עטוף בסוגריים: `prompt_(beach)` מחזיר HTTP 500 עם `General Error`, ואילו `prompt_beach` מחזיר 200. הצורה עם הסוגריים נכונה ל-`e_gen_remove` אבל לא כאן |
| `e_background_removal` | הסרת רקע, טרנספורמציה מובנית (ללא מנוי תוסף נפרד; התוסף הישן סגור לחשבונות חדשים מ-1.2.2026). לא בחינם, מחויב לפי ספירת טרנספורמציות מיוחדת. |
| `e_gen_restore` | שחזור AI לתמונות ישנות, מטושטשות או פגומות |
| `auto_tagging:0.7` | תיוג אוטומטי של העלאות עם AI (סף ביטחון 0.0-1.0); מעבירים בזמן ההעלאה. בניגוד לאפקטי `e_gen_*` זה לא מובנה: צריך קודם לרשום תוסף תיוג (Google Auto Tagging, AWS Rekognition, Imagga) בעמוד ה-Add-ons, אחרת ההעלאה מחזירה שגיאה במקום תגיות |

דוגמה: מסירים אדם מהתמונה ואז מחליפים את הרקע:
```
https://res.cloudinary.com/{cloud_name}/image/upload/e_gen_remove:prompt_(person)/e_gen_background_replace:prompt_modern%20office/{public_id}
```

תיוג אוטומטי בזמן העלאה:
```python
data = {
    "api_key": api_key, "timestamp": timestamp, "signature": signature,
    "categorization": "google_tagging",
    "auto_tagging": 0.7,  # מקבלים תגיות עם ביטחון של 70% ומעלה
}
# categorization and auto_tagging are upload parameters, so both must be in the
# signed string too, or the upload fails with Invalid Signature.
```

### שלב 5: מיטוב ביצועים

**החלת מיטוב אוטומטי:**
```
# הוסיפו f_auto (פורמט) ו-q_auto (איכות) לכל URL
https://res.cloudinary.com/{cloud_name}/image/upload/f_auto,q_auto/{public_id}
```

**יצירת breakpoints רספונסיביים:**
```python
def get_responsive_urls(cloud_name, public_id, widths=None):
    """Generate responsive image URLs."""
    if widths is None:
        widths = [320, 640, 960, 1280, 1920]

    base = f"https://res.cloudinary.com/{cloud_name}/image/upload"
    urls = {}
    for w in widths:
        # c_limit: never upscale. Without it, w_1920 on an 864px original
        # delivers a 1920px image.
        urls[w] = f"{base}/w_{w},c_limit,q_auto,f_auto/{public_id}"

    srcset = ", ".join(f"{url} {w}w" for w, url in urls.items())
    return urls, srcset
```

**תגית HTML לתמונה רספונסיבית:**
```html
<img
  src="https://res.cloudinary.com/{cloud_name}/image/upload/w_960,c_limit,q_auto,f_auto/{public_id}"
  srcset="{generated_srcset}"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Description"
  loading="lazy"
/>
```

**הגשת וידאו.** מגישים מ-`/video/upload/` ולא מ-`/image/upload/` (אותו public ID בנתיב התמונות הוא נכס אחר, ולרוב מחזיר 404):

| מטרה | URL |
|------|-----|
| MP4/WebM פרוגרסיבי ממוטב | `.../video/upload/q_auto,f_auto:video/{public_id}` (משתמשים ב-`f_auto:video` כשאין סיומת ב-URL: עם `f_auto` רגיל, בקשה שכותרת ה-Accept שלה כוללת סוגי תמונה, כמו ניווט רגיל בדפדפן, מקבלת תמונת AVIF במקום הוידאו) |
| הזרמה אדפטיבית (HLS) | `.../video/upload/sp_auto/{public_id}.m3u8` (או `.mpd` ל-DASH). מנגנים עם נגן שתומך ב-HLS/DASH, למשל Cloudinary Video Player |
| תמונת פוסטר | `.../video/upload/so_5,w_800,h_450,c_fill,q_auto,f_jpg/{public_id}` |

שימו לב: `q_auto` על `.m3u8` אינו הזרמה אדפטיבית, הוא מחזיר playlist עם רזולוציה אחת. רק `sp_auto` (או streaming profile בשם) מייצר master playlist עם כמה רזולוציות. כדי להגביל URL של תמונה למועמדי תמונה בלבד משתמשים ב-`f_auto:image`.

### שלב 6: ניהול נכסים

**רשימת כל הנכסים:**
```python
def list_assets(cloud_name, api_key, api_secret, resource_type="image",
                max_results=30, all_pages=False):
    """List assets in Cloudinary media library.

    The Admin API returns at most 500 per call and paginates with next_cursor.
    Ignoring the cursor truncates a "list everything" call at the first page
    with no error, so the short list looks complete.
    """
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/{resource_type}"
    params = {"max_results": min(max_results, 500)}
    resources = []
    while True:
        response = requests.get(url, params=params,
                                auth=(api_key, api_secret), timeout=(10, 60))
        response.raise_for_status()
        payload = response.json()
        resources.extend(payload.get("resources", []))
        cursor = payload.get("next_cursor")
        if not all_pages or not cursor:
            payload["resources"] = resources
            return payload
        params["next_cursor"] = cursor
```

**מחיקת נכס:**
```python
def delete_asset(public_id, cloud_name, api_key, api_secret,
                 resource_type="image"):
    """Delete an asset from Cloudinary.

    destroy is per resource type. Calling the image endpoint for a video
    returns "not found", which reads as "already deleted" while the asset is
    still there consuming storage credits, so pass the type you uploaded with.
    invalidate=true also purges CDN copies; without it delivered versions can
    stay cached for up to 30 days after deletion.
    """
    timestamp = str(int(time.time()))
    signature = hashlib.sha1(
        f"invalidate=true&public_id={public_id}&timestamp={timestamp}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/destroy"
    response = requests.post(url, data={
        "public_id": public_id, "invalidate": "true", "api_key": api_key,
        "timestamp": timestamp, "signature": signature
    }, timeout=(10, 60))
    response.raise_for_status()
    return response.json()
```

### שלב 7: שימוש ב-URL Gen SDK (אופציונלי)

הגישה של URL גולמי עובדת בכל שפה, אבל ל-Cloudinary יש SDK-ים מודרניים שבונים את אותן כתובות עם autocomplete ופחות הרכבת מחרוזות:

- `@cloudinary/url-gen` v1.x (אגנוסטי לפריימוורק, רץ בדפדפן וב-Node)
- `@cloudinary/react` (קומפוננטות `<AdvancedImage />` ו-`<AdvancedVideo />`)
- `@cloudinary/vue` (קומפוננטות ל-Vue 3)

התקנה:
```bash
npm install @cloudinary/url-gen @cloudinary/react
```

המקבילה של `f_auto,q_auto,w_800` יחד עם חיתוך מבוסס זיהוי פנים:
```ts
import { Cloudinary } from "@cloudinary/url-gen";
import { fill } from "@cloudinary/url-gen/actions/resize";
import { focusOn } from "@cloudinary/url-gen/qualifiers/gravity";
import { face } from "@cloudinary/url-gen/qualifiers/focusOn";
import { auto as autoFormat } from "@cloudinary/url-gen/qualifiers/format";
import { auto as autoQuality } from "@cloudinary/url-gen/qualifiers/quality";
import { format, quality } from "@cloudinary/url-gen/actions/delivery";

const cld = new Cloudinary({ cloud: { cloudName: process.env.CLOUDINARY_CLOUD_NAME } });

const url = cld.image("products/shirt-blue")
  .resize(fill().width(800).height(800).gravity(focusOn(face())))
  .delivery(format(autoFormat()))
  .delivery(quality(autoQuality()))
  .toURL();
```

ב-React:
```tsx
import { AdvancedImage } from "@cloudinary/react";
<AdvancedImage cldImg={cld.image("products/shirt-blue").resize(fill().width(800))} />
```

### שלב 8: שכבות טקסט בעברית

האוברליי `l_text:` ב-Cloudinary תומך בעברית כשמקודדים את הטקסט ב-URL ובוחרים פונט שכולל גליפים בעברית. פונטים מובנים שתומכים בעברית (לא צריך להעלות פונט משלכם): **Heebo, Assistant, Rubik, Frank Ruhl Libre, Suez One, Secular One**. גופני Google אחרים, כמו `David Libre` או `Noto Sans Hebrew`, לא נמצאים ברשימה המובנית ולכן השם לבדו מחזיר HTTP 400 עם `Unsupported font family`. אפשר לטעון אותם מ-Google Fonts על ידי הוספת `@google` לשם המשפחה, למשל `l_text:David%20Libre@google_40_700:...`. עם `@google` המשקל חייב להיות מספרי (`700` ולא `bold`): הצורה `Heebo@google_40_bold` מחזירה 400.

תבנית:
```
l_text:{font}_{size}_{style}:{url-encoded-text}
```

דוגמה, "שלום" ב-Heebo 40 מודגש, לבן, בתחתית התמונה:
```
https://res.cloudinary.com/{cloud_name}/image/upload/w_800,c_fill/l_text:Heebo_40_bold:%D7%A9%D7%9C%D7%95%D7%9D,co_white,g_south,y_30/{public_id}
```

טיפ: מקודדים את הטקסט עם `urllib.parse.quote(text, safe="")` בפייתון או `encodeURIComponent()` ב-JS. הגליפים בעברית יוצגו נכון גם בלי דגלי RTL מפורשים, כל עוד הפונט תומך בהם.

## דוגמאות

### דוגמה 1: העלאה ומיטוב
המשתמש אומר: "העלו תמונת מוצר וצרו כתובות URL ממוטבות"
פעולות:
1. העלאה דרך Upload API עם `asset_folder` (מצב dynamic, ברירת המחדל בחשבונות חדשים; `folder` רק בחשבונות במצב fixed) ותגיות
2. יצירת כתובות URL לטרנספורמציה לתמונה ממוזערת, עמוד מוצר ושיתוף חברתי
3. החלת f_auto,q_auto על כל וריאנט
תוצאה: Public ID וכתובות URL ממוטבות מוכנות לשימוש.

### דוגמה 2: סט תמונות רספונסיבי
המשתמש אומר: "צרו תמונות רספונסיביות לבאנר הראשי באתר שלי"
פעולות:
1. קחו את ה-public_id הקיים
2. צרו srcset עם breakpoints ב-320, 640, 960, 1280, 1920 פיקסלים
3. הוסיפו f_auto,q_auto לכל כתובת URL של breakpoint
4. ספקו תגית HTML מלאה של img עם srcset ו-sizes
תוצאה: HTML מוכן להעתקה-הדבקה עבור תמונה רספונסיבית.

### דוגמה 3: העלאת וידאו
המשתמש אומר: "העלו וידאו וקבלו כתובת URL להזרמה"
פעולות:
1. העלאה דרך endpoint של /video/upload (עם `upload_large` של ה-SDK ועם `resource_type="video"` אם הקובץ מעל 100 MB)
2. יצירת כתובת URL להזרמה אדפטיבית עם `sp_auto` וסיומת `.m3u8` (HLS), ולצידה גרסה פרוגרסיבית עם `q_auto,f_auto:video` כגיבוי
3. מתן כתובת URL לתמונת פוסטר (`so_0` או היסט אחר, עם `f_jpg`)
תוצאה: כתובת HLS אדפטיבית, גיבוי פרוגרסיבי ותמונת פוסטר.

## משאבים מצורפים

### סקריפטים
- `scripts/upload_asset.py`, לקוח לניהול נכסי Cloudinary התומך בהעלאת תמונות/וידאו עם ארגון לפי תיקיות ותגיות, יצירת כתובות URL לטרנספורמציות, יצירת סט תמונות רספונסיביות עם srcset ופלט HTML, רשימת נכסים ומחיקת נכסים כולל ביטול מטמון ב-CDN. הסקריפט מסרב לקבצים מעל 100 MB (משתמשים ב-`upload_large` של ה-SDK), דוחה gravity של פנים עם מצבי crop שמחזירים 400, מקודד public IDs ומדפיס את `X-Cld-Error`. קורא פרטי התחברות מ-CLOUDINARY_URL או ממשתני סביבה נפרדים. הרצה: `python scripts/upload_asset.py --help`

### חומרי עזר
- `references/optimization-guide.md`, מדריך מיטוב ביצועים ל-Cloudinary הכולל מיטוב אוטומטי עם f_auto/q_auto, breakpoints לתמונות רספונסיביות עם תבניות HTML srcset, טיפול ב-DPR למסכי רטינה, אסטרטגיות טעינה עצלה כולל placeholders מטושטשים (LQIP), וטרנספורמציות eager בזמן ההעלאה. עיינו בו בעת בניית צינורות הגשת תמונות בעלי ביצועים גבוהים או מיטוב זמני טעינת עמודים.
- `references/domain-checklist.md`, חוזה הכיסוי של הסקיל: נושאי חובה ונושאים מומלצים שאינטגרציה מלאה עם Cloudinary צריכה, כל אחד קשור לעמוד תיעוד רשמי, ורשימה מפורשת של מה שמחוץ לתחום. עיינו בו לפני שקובעים שהסקיל מכסה תרחיש מסוים.
- `references/transformation-cheatsheet.md`, מדריך מלא לפרמטרי טרנספורמציה בכתובות URL של Cloudinary כולל מצבי שינוי גודל/חיתוך, מיקום gravity, אפשרויות איכות/פורמט, אפקטים ויזואליים, פרמטרי שכבות/טקסט, עוזרים רספונסיביים, מתכונים נפוצים (תמונה ממוזערת, גיבור, אווטאר, מוצר, שיתוף חברתי, סימן מים), טרנספורמציות וידאו, מגבלות קצב לפי דרגת מנוי והגדרת סביבה. עיינו בו בעת בניית כתובות URL לטרנספורמציה או חיפוש תחביר פרמטרים ספציפי.

## מלכודות נפוצות

- מקודדים כל רווח בתוך רכיב טרנספורמציה. רווח גולמי (למשל `prompt_modern office`) הופך את ה-URL לפגום: `curl` דוחה אותו מקומית עם קוד יציאה 3 ואפילו לא שולח בקשה, ו-`requests` מתנהג אותו דבר. דפדפנים מסתירים את זה כי הם מקודדים בשקט. השתמשו ב-`%20` או ב-`urllib.parse.quote`.

- שכבות טקסט בעברית דורשות משפחת פונט ש-Cloudinary באמת מספק. נבדקו ועובדים: Heebo, Assistant, Rubik, Frank Ruhl Libre, Suez One, Secular One. השם לבדו של `David Libre` או `Noto Sans Hebrew` מחזיר HTTP 400 עם `Unsupported font family` (במקום זה משתמשים בסיומת `@google` עם משקל מספרי), כלומר שם לא מוכר מפיל את כל ה-URL ולא נופל חזרה לברירת מחדל. משפחה לטינית כמו Arial מתקבלת (HTTP 200) ולא נדחית, כלומר הכשל כאן טיפוגרפי ולא 400. בוחרים משפחה עברית לשליטה טיפוגרפית; אם בכל זאת משתמשים בלטינית, בודקים את התמונה המרונדרת בעיניים במקום לסמוך על ה-200. חובה לקודד את הטקסט ב-URL.
- המסלול החינמי כולל 25 קרדיטים בחודש. לפי דף המחירון, קרדיט אחד שווה ל-1,000 טרנספורמציות או 1 ג'יגה אחסון מנוהל או 1 ג'יגה רוחב פס תמונות. רוחב פס וידאו הוא 2 ג'יגה לקרדיט וזמין במסלולים בתשלום בלבד, כך שהגשת וידאו במסלול החינמי לא מקבלת את ההטבה. הקרדיטים הם מאגר משותף אחד שנצרך יחד על טרנספורמציות, אחסון ורוחב פס, ולא שלוש מכסות נפרדות. המעבר Free → Plus יקר (Plus במחירון 2026: 99 דולר לחודש בחיוב חודשי, 89 דולר לחודש בחיוב שנתי, עבור 225 קרדיטים בחודש), אז כדאי לתכנן מראש את הוריאנטים ב-Eager לפני העלאה לאוויר. טרנספורמציות וידאו נספרות לפי שנייה של פלט ולא לפי URL: ב-h264 שתיים לשנייה ב-SD וארבע לשנייה ב-HD (ב-AV1 שש עשרה ושלושים ושתיים), וחלק משנייה נספר כשנייה שלמה. רזולוציית HD של 60 שניות היא 240 טרנספורמציות. הזרמה אדפטיבית עם `sp_auto` יקרה יותר: שמונה לשנייה עד 1080p, שתים עשרה ב-1440p ועשרים וארבע ב-4K, בלי קשר למספר הרזולוציות, כך שאותו קליפ של 60 שניות דרך `sp_auto` עולה 480. כל העלאה, וכל דריסה של public ID קיים, נספרת גם היא כטרנספורמציה אחת.
- נקודות קצה של Upload API ו-Admin API דורשות אימות תקין. כתובות URL לדוגמה בתיעוד עלולות להחזיר שגיאות 401/404 כאשר נגישות אליהן ללא פרטי התחברות תקינים.
- כתובות URL חתומות ומצבי `auth_token` / Strict Transformations: כתובות URL נגזרות עלולות להיחסם אם לא חתומות. מפעילים את "Strict transformations" ב-Settings, Security, וחותמים את כתובות ה-URL להגשה עם `s--{signature}--` או משתמשים ב-`auth_token` לגישה מוגבלת בזמן.
- דריסת נכס (`overwrite=true` עם אותו public ID) משאירה את הגרסה הישנה ב-CDN עד 30 ימים. מעבירים גם `invalidate=true` בהעלאה, או מגישים עם רכיב הגרסה מתשובת ההעלאה (`v<version>/` ב-URL), שנכנס לתוקף מיד.
- Eager לעומת Lazy: ברירת המחדל היא Lazy, כלומר Cloudinary בונה את הגרסה הנגזרת בפעם הראשונה שמבקשים אותה (פגיעה ראשונה איטית) ושומר במטמון. Eager בונה בזמן ההעלאה (פגיעה ראשונה מהירה, אבל צורך קרדיטים בעלייה). שווה Eager לוריאנטים צפויים כמו תמונות ממוזערות וכרטיסי שיתוף; את כל השאר אפשר להשאיר Lazy.
- Named transformations: מגדירים טרנספורמציה לשימוש חוזר (למשל `t_product_card`) ב-Settings, Transformations. כתובות ה-URL הופכות ל-`.../t_product_card/{public_id}` במקום שרשרת ארוכה של פרמטרים, ואפשר לשנות את המתכון מרכזית בלי לערוך כתובות URL בקוד.
- שגיאת "blocked by CORS policy" בהעלאה ישירה מהדפדפן: הפתרון המתועד הוא preset לא חתום או חתימה שנוצרת בשרת (שלב 3), ולא הגדרת מקורות בקונסול.
- לעבודת שרת עדיף SDK רשמי על פני חתימה ידנית. החבילה `cloudinary` ב-npm (2.x) וב-PyPI (1.x) מממשת חתימה, ניסיונות חוזרים ואת פרמטרי מצבי התיקיות במקומכם; הסקריפט המצורף `scripts/upload_asset.py` חותם SHA-1 בעצמו כדי להישאר קל תלויות לשימוש חד-פעמי מה-CLI, וזו לא סיבה לחתום ידנית בתוך אפליקציה.

- `upload_preset` במצב Unsigned: presets לא חתומים מאפשרים העלאה מהדפדפן בלי לחשוף את ה-API secret. אבל כל מי שמכיר את שם ה-preset יכול להשתמש בו. מקשיחים כל preset עם `allowed_formats`, `disallow_public_id` וטרנספורמציות incoming שמנרמלות מידות. ל-presets אין מגבלת גודל קובץ לכל preset, ולכן אוכפים גודל בצד הלקוח (האפשרות `maxFileSize` של Upload Widget). אף פעם לא שמים `f_auto` בטרנספורמציה incoming: הפורמט נבחר לכל בקשה בזמן ההגשה. בתוכן שמשתמשים מעלים כדאי גם להגדיר `moderation` (תור ידני או תוסף מודרציה מבוסס AI) כדי ששום דבר לא יפורסם בלי בדיקה.
- `notification_url`: מעבירים את הפרמטר בזמן ההעלאה (או מגדירים גלובלית) כדי לקבל POST callback כשעבודות אסינכרוניות מסתיימות (טרנספורמציות eager, קידוד וידאו, מודרציה). Cloudinary חותם על הגוף, לכן מאמתים את הכותרת `X-Cld-Signature` לפני שסומכים על התוכן. החתימה היא `SHA-1(body + timestamp + api_secret)` כשה-timestamp מגיע מהכותרת `X-Cld-Timestamp`, כלומר האימות הוא `hashlib.sha1((raw_body + ts + api_secret).encode()).hexdigest()` בהשוואה עם `hmac.compare_digest`. דוחים כל בקשה ישנה מכשעתיים בערך. חשוב להשתמש בגוף הבקשה הגולמי ולא ב-JSON שסידרתם מחדש, אחרת ה-digest לא יתאים. ה-digest יכול להיות גם SHA-256, ופונקציות העזר של ה-SDK (`cloudinary.utils.verify_notification_signature` ב-Python, `cloudinary.utils.verifyNotificationSignature` ב-Node) עושות את זה בשבילכם. טריגרים שנוצרו עם `auth_scheme` מסוג `eddsa_v2` שולחים רק `X-Cld-Signature_v2` (Ed25519) בלי הכותרת הישנה, ולכן בדיקת ה-SHA-1 שלמעלה לא יכולה לאמת אותם.

## פתרון בעיות

### שגיאה: "401 Unauthorized"
סיבה: מפתח API או סוד לא תקינים, או פרטי התחברות חסרים
פתרון: אמתו את CLOUDINARY_URL או את משתני הסביבה הנפרדים. ודאו שמפתח ה-API פעיל בלוח הבקרה של Cloudinary.

### שגיאה: "File too large"
סיבה: חריגה מגודל הקובץ המרבי של התוכנית שלכם. לפי עמוד Compare Plans של Cloudinary: ב-Free עד 10 MB לתמונה, 100 MB לוידאו ו-10 MB לקובץ raw; ב-Plus עד 20 MB, 2 GB ו-20 MB; ב-Advanced עד 40 MB, 4 GB ו-40 MB; ב-Enterprise לפי הסכם. בנפרד, כל קובץ מעל 100 MB חייב להישלח בהעלאה במקטעים (`upload_large`), אבל העלאה במקטעים לא מגדילה את מגבלת התוכנית.
פתרון: כווצו או הקטינו לפני ההעלאה (תמונה מעל 10 MB במסלול החינמי תידחה בכל דרך שבה תישלח), השתמשו ב-`upload_large` עם ה-`resource_type` הנכון לכל קובץ מעל 100 MB, או שדרגו את התוכנית.

### שגיאה: "Resource not found"
סיבה: public_id לא תקין או שהנכס נמחק
פתרון: אמתו את ה-public_id עם רשימת Admin API. בדקו שנתיבי התיקיות כלולים ב-public_id.

### שגיאה: "Invalid Signature" או חוסר התאמה בחתימה בהעלאה
סיבה: סדר פרמטרים לא נכון, API secret שגוי, או חותמת זמן שסטתה (Cloudinary דוחה חותמות זמן עם פער של מעל שעה).
פתרון: חותמים על הפרמטרים ממויינים אלפביתית ומחוברים ב-`&` (ללא `file`, `cloud_name`, `api_key`, `resource_type` והחתימה עצמה, וכולל כל פרמטר אחר שאתם שולחים, גם `tags` וגם `asset_folder`), מצרפים את ה-API secret בסוף ומריצים SHA-1. מסנכרנים את שעון השרת (NTP). במקרה של ספק, מדפיסים את `params_to_sign` המדויק ומשווים לתיעוד. ברירת המחדל של Cloudinary היא SHA-1, והיא מקבלת גם SHA-256. ב-SDK זה פרמטר התצורה `signature_algorithm=sha256` ולא שדה בבקשת ההעלאה; ב-REST גולמי פשוט מחשבים SHA-256. הקוד עם SHA-1 עדיין עובד.

### שגיאה: "Rate limit exceeded" / 420 / 429
הגבלת הקצב של Admin API מתועדת כ-HTTP **420** ונושאת את הכותרות `X-FeatureRateLimit-Limit`, `X-FeatureRateLimit-Remaining` ו-`X-FeatureRateLimit-Reset`; כדאי לקרוא את `Remaining` ולהאט לפני שנחסמים. גם ה-SDKs הרשמיים העדכניים מתייחסים ל-**429** כהגבלת קצב, ולכן מטפלים בשני הקודים. ל-Upload API אין מגבלה שעתית, אבל העלאות מקבילות רבות (הגירה בכמות) עדיין יכולות לקבל 420: מתחילים בכעשר העלאות במקביל וחוזרים עם exponential backoff.

סיבה: המסלול החינמי מוגבל ל-500 קריאות Admin API בשעה ונותן 25 קרדיטים בחודש שנצרכים במשותף על טרנספורמציות, אחסון ורוחב פס. אסור לקרוא את זה כ-25,000 טרנספורמציות בחודש: המספר הזה מושג רק אם אחסון ורוחב פס צורכים אפס קרדיטים, וזה לא קורה ברגע שיש נכסים בחשבון.
פתרון: שומרים תשובות של list/metadata במטמון, מקבצים פעולות, או משדרגים את המסלול. שומרים במטמון את תשובות Admin API באפליקציה שלכם; ה-CDN (שיכול לשמור נכסים מוגשים עד 30 ימים) מגיש כתובות להגשה בלבד ולא קריאות מטא-דאטה של Admin API.

### שגיאה: "Invalid transformation" / 400 על URL נגזר
סיבה: פרמטר לא ידוע, פרמטרים סותרים (למשל `c_fit` עם `g_face` לא הגיוניים יחד), או שרשרת טרנספורמציות בלי לוכסן מפריד.
פתרון: בודקים את ה-URL חלק-חלק ב-Media Explorer של Cloudinary. בין טרנספורמציות בשרשרת מפרידים ב-`/`, ובין פרמטרים בתוך אותה טרנספורמציה ב-`,`.

### AVIF/WebP לא נטענים בדפדפנים ישנים
סיבה: `f_auto` בוחר AVIF לדפדפנים מודרניים, אבל יש דפדפנים ישנים או middleboxes שמסירים את הכותרת `Accept` כך ש-Cloudinary לא מזהה את היכולות.
פתרון: Cloudinary נופל אוטומטית ל-JPEG/PNG. אם רואים תמונות שבורות, כופים נפילה בטוחה: `f_auto:image,q_auto` או נועלים `f_jpg` למקטע הבעייתי. בודקים עם `curl -H "Accept: image/avif" {url}` ו-`curl -H "Accept: */*" {url}`.

## קישורי עזר

- בית התיעוד של Cloudinary, https://cloudinary.com/documentation
- URL Gen SDK ב-GitHub, https://github.com/cloudinary/js-url-gen
- מדריך פרמטרים לטרנספורמציות, https://cloudinary.com/documentation/transformation_reference
- סקירה של פיצ'רי ה-AI הגנרטיבי, https://cloudinary.com/documentation/generative_ai_transformations
- כתובות URL חתומות והגשה מאומתת, https://cloudinary.com/documentation/control_access_to_media
- הזרמה אדפטיבית, https://cloudinary.com/documentation/adaptive_bitrate_streaming
- העלאה מצד הלקוח (דפדפן), https://cloudinary.com/documentation/client_side_uploading
- ה-SDK ל-Next.js (next-cloudinary), https://cloudinary.com/documentation/nextjs_integration