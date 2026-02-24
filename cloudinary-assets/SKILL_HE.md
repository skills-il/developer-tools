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
1. הירשמו בכתובת https://cloudinary.com (מסלול חינמי: 25 קרדיטים/חודש)
2. מצאו את פרטי ההתחברות ב-Dashboard, לאחר מכן ב-Programmable Media, ואז ב-API Keys
3. הגדירו CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME

### שלב 2: בחירת פעולה

| פעולה | API | שיטה | מתי |
|-------|-----|-------|------|
| העלאת תמונה | Upload API | POST /image/upload | תמונה חדשה לאחסון |
| העלאת וידאו | Upload API | POST /video/upload | וידאו חדש לאחסון |
| שינוי תמונה | מבוסס URL | GET (URL) | שינוי גודל, חיתוך, אפקטים |
| מיטוב הגשה | מבוסס URL | GET (URL) | שיפור ביצועים |
| רשימת נכסים | Admin API | GET /resources | עיון בספריית המדיה |
| מחיקת נכס | Upload API | POST /image/destroy | הסרת מדיה |
| פרטי נכס | Admin API | GET /resources/{id} | בדיקת מטא-דאטה |

### שלב 3: העלאת מדיה

**העלאת תמונה:**
```python
import requests
import hashlib
import time

def upload_image(file_path, cloud_name, api_key, api_secret,
                 folder="", tags=None):
    """Upload image to Cloudinary."""
    timestamp = str(int(time.time()))
    params_to_sign = f"timestamp={timestamp}"
    if folder:
        params_to_sign = f"folder={folder}&{params_to_sign}"

    signature = hashlib.sha1(
        f"{params_to_sign}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    data = {"api_key": api_key, "timestamp": timestamp, "signature": signature}
    if folder:
        data["folder"] = folder
    if tags:
        data["tags"] = ",".join(tags)

    with open(file_path, "rb") as f:
        response = requests.post(url, data=data, files={"file": f})
    return response.json()
```

### שלב 4: טרנספורמציות תמונה באמצעות URL

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
| סימן מים | l_watermark,w_200,o_50,g_south_east | סימן מים שקוף למחצה |

### שלב 5: מיטוב ביצועים

**החלת מיטוב אוטומטי:**
```
# הוסיפו f_auto (פורמט) ו-q_auto (איכות) לכל URL
https://res.cloudinary.com/{cloud}/image/upload/f_auto,q_auto/{public_id}
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
        urls[w] = f"{base}/w_{w},q_auto,f_auto/{public_id}"

    srcset = ", ".join(f"{url} {w}w" for w, url in urls.items())
    return urls, srcset
```

**תגית HTML לתמונה רספונסיבית:**
```html
<img
  src="https://res.cloudinary.com/{cloud}/image/upload/w_800,q_auto,f_auto/{id}"
  srcset="{generated_srcset}"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Description"
  loading="lazy"
/>
```

### שלב 6: ניהול נכסים

**רשימת כל הנכסים:**
```python
def list_assets(cloud_name, api_key, api_secret, resource_type="image", max_results=30):
    """List assets in Cloudinary media library."""
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/{resource_type}"
    response = requests.get(url, params={"max_results": max_results},
                            auth=(api_key, api_secret))
    return response.json()
```

**מחיקת נכס:**
```python
def delete_asset(public_id, cloud_name, api_key, api_secret):
    """Delete an asset from Cloudinary."""
    timestamp = str(int(time.time()))
    signature = hashlib.sha1(
        f"public_id={public_id}&timestamp={timestamp}{api_secret}".encode()
    ).hexdigest()

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/destroy"
    response = requests.post(url, data={
        "public_id": public_id, "api_key": api_key,
        "timestamp": timestamp, "signature": signature
    })
    return response.json()
```

## דוגמאות

### דוגמה 1: העלאה ומיטוב
המשתמש אומר: "העלו תמונת מוצר וצרו כתובות URL ממוטבות"
פעולות:
1. העלאה דרך Upload API עם תיקייה ותגיות
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
1. העלאה דרך endpoint של /video/upload
2. יצירת כתובת URL להזרמה אדפטיבית עם q_auto
3. מתן כתובת URL לתמונת פוסטר (טרנספורמציה של הפריים הראשון)
תוצאה: כתובת URL לוידאו עם הגשה ממוטבת ותמונת פוסטר.

## משאבים מצורפים

### סקריפטים
- `scripts/upload_asset.py` — לקוח לניהול נכסי Cloudinary התומך בהעלאת תמונות/וידאו עם ארגון לפי תיקיות ותגיות, יצירת כתובות URL לטרנספורמציות, יצירת סט תמונות רספונסיביות עם srcset ופלט HTML, רשימת נכסים ומחיקת נכסים. קורא פרטי התחברות מ-CLOUDINARY_URL או ממשתני סביבה נפרדים. הרצה: `python scripts/upload_asset.py --help`

### חומרי עזר
- `references/optimization-guide.md` — מדריך מיטוב ביצועים ל-Cloudinary הכולל מיטוב אוטומטי עם f_auto/q_auto, breakpoints לתמונות רספונסיביות עם תבניות HTML srcset, טיפול ב-DPR למסכי רטינה, אסטרטגיות טעינה עצלה כולל placeholders מטושטשים (LQIP), וטרנספורמציות eager בזמן ההעלאה. עיינו בו בעת בניית צינורות הגשת תמונות בעלי ביצועים גבוהים או מיטוב זמני טעינת עמודים.
- `references/transformation-cheatsheet.md` — מדריך מלא לפרמטרי טרנספורמציה בכתובות URL של Cloudinary כולל מצבי שינוי גודל/חיתוך, מיקום gravity, אפשרויות איכות/פורמט, אפקטים ויזואליים, פרמטרי שכבות/טקסט, עוזרים רספונסיביים, מתכונים נפוצים (תמונה ממוזערת, גיבור, אווטאר, מוצר, שיתוף חברתי, סימן מים), טרנספורמציות וידאו, מגבלות קצב לפי דרגת מנוי והגדרת סביבה. עיינו בו בעת בניית כתובות URL לטרנספורמציה או חיפוש תחביר פרמטרים ספציפי.

## פתרון בעיות

### שגיאה: "401 Unauthorized"
סיבה: מפתח API או סוד לא תקינים, או פרטי התחברות חסרים
פתרון: אמתו את CLOUDINARY_URL או את משתני הסביבה הנפרדים. ודאו שמפתח ה-API פעיל בלוח הבקרה של Cloudinary.

### שגיאה: "File too large"
סיבה: חריגה ממגבלות ההעלאה של התוכנית (חינמי: 10MB תמונה, 100MB וידאו)
פתרון: כווצו לפני ההעלאה, או שדרגו את תוכנית Cloudinary. השתמשו בטרנספורמציות eager ליצירת גרסאות קטנות יותר בזמן ההעלאה.

### שגיאה: "Resource not found"
סיבה: public_id לא תקין או שהנכס נמחק
פתרון: אמתו את ה-public_id עם רשימת Admin API. בדקו שנתיבי התיקיות כלולים ב-public_id.
