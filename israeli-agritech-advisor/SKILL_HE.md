# יועץ אגריטק ישראלי

## הוראות

### שלב 1: זיהוי תרחיש השימוש באגריטק
| תרחיש שימוש | פלטפורמות מרכזיות | סוגי נתונים | מטרה |
|-------------|-------------------|-------------|------|
| מיטוב השקיה | CropX, נטפים, Manna | לחות קרקע, מזג אוויר, ET0 | הפחתת צריכת מים ב-20-40% |
| זיהוי מזיקים/מחלות | Taranis, AgroScout | הדמייה אווירית, NDVI | זיהוי מוקדם, טיפול ממוקד |
| ניטור חממות | Prospera/Valmont | אקלים, הדמייה | תנאי גידול מיטביים |
| ניהול האבקה | BeeHero | חיישני כוורת, GPS | מיקסום יעילות האבקה |
| פלטפורמת נתוני חקלאות | מרובות | כל נתוני החיישנים | לוח בקרה אחוד לקבלת החלטות |
| עמידה בתקני מים | נתוני מקורות, חיישנים | זרימת מים, מכסות | עמידה בתקנות רשות המים |

### שלב 2: התחברות ל-API של אגריטק

**CropX -- שילוב ניטור קרקע:**
```python
import requests

class CropXClient:
    """Client for CropX soil monitoring API."""

    BASE_URL = "https://api.cropx.com/v2"

    def __init__(self, client_id, client_secret):
        self.token = self._authenticate(client_id, client_secret)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def _authenticate(self, client_id, client_secret):
        response = requests.post(f"{self.BASE_URL}/auth/token", json={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        })
        return response.json()["access_token"]

    def get_sites(self):
        """List all monitored field sites."""
        return requests.get(f"{self.BASE_URL}/sites", headers=self.headers).json()

    def get_soil_readings(self, device_id, start_date, end_date):
        """Get soil sensor readings for a device."""
        return requests.get(
            f"{self.BASE_URL}/devices/{device_id}/measurements",
            headers=self.headers,
            params={"from": start_date.isoformat(), "to": end_date.isoformat(),
                    "metrics": "moisture,temperature,ec"}
        ).json()

    def get_irrigation_recommendation(self, site_id):
        """Get AI-driven irrigation recommendation for a site."""
        return requests.get(
            f"{self.BASE_URL}/sites/{site_id}/recommendations",
            headers=self.headers
        ).json()
```

**Netafim GrowSphere -- שילוב בקרת השקיה:**
```python
class GrowSphereClient:
    """Client for Netafim GrowSphere irrigation platform."""

    BASE_URL = "https://api.growsphere.netafim.com/v1"

    def __init__(self, api_key):
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    def get_controllers(self):
        """List all irrigation controllers."""
        return requests.get(f"{self.BASE_URL}/controllers", headers=self.headers).json()

    def create_irrigation_schedule(self, controller_id, zone_id, schedule):
        """Set irrigation schedule for a zone."""
        return requests.post(
            f"{self.BASE_URL}/controllers/{controller_id}/zones/{zone_id}/schedules",
            headers=self.headers, json=schedule
        ).json()

    def get_flow_data(self, controller_id, start_date, end_date):
        """Get water flow data for compliance tracking."""
        return requests.get(
            f"{self.BASE_URL}/controllers/{controller_id}/flow",
            headers=self.headers,
            params={"from": start_date.isoformat(), "to": end_date.isoformat()}
        ).json()
```

**Taranis -- שילוב מודיעין גידולים:**
```python
class TaranisClient:
    """Client for Taranis crop intelligence platform."""

    BASE_URL = "https://api.taranis.com/v1"

    def __init__(self, api_key):
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_fields(self):
        """List monitored fields."""
        return requests.get(f"{self.BASE_URL}/fields", headers=self.headers).json()

    def get_detections(self, field_id, scan_id=None):
        """Get pest/disease detections for a field."""
        params = {}
        if scan_id:
            params["scan_id"] = scan_id
        return requests.get(
            f"{self.BASE_URL}/fields/{field_id}/detections",
            headers=self.headers, params=params
        ).json()

    def request_scan(self, field_id, scan_type="full"):
        """Request a new aerial scan of a field."""
        return requests.post(
            f"{self.BASE_URL}/fields/{field_id}/scans",
            headers=self.headers, json={"type": scan_type}
        ).json()
```

### שלב 3: מימוש מיטוב השקיה

```python
def calculate_irrigation_need(soil_data, crop_type, weather_data):
    """Calculate irrigation need based on soil, crop, and weather data.
    Uses water balance approach common in Israeli precision agriculture.
    """
    # Crop coefficients (Kc) -- Israeli Volcani Institute values
    CROP_KC = {
        "citrus": {"initial": 0.65, "mid": 0.70, "late": 0.65},
        "avocado": {"initial": 0.60, "mid": 0.85, "late": 0.75},
        "tomato": {"initial": 0.60, "mid": 1.15, "late": 0.80},
        "pepper": {"initial": 0.60, "mid": 1.05, "late": 0.90},
        "date_palm": {"initial": 0.90, "mid": 0.95, "late": 0.95},
        "table_grape": {"initial": 0.30, "mid": 0.85, "late": 0.45},
    }
    kc = CROP_KC.get(crop_type, {"initial": 0.6, "mid": 1.0, "late": 0.8})
    et_crop = weather_data["et0"] * kc["mid"]
    effective_rain = max(0, weather_data.get("precipitation", 0) * 0.8)
    net_need = max(0, et_crop - effective_rain)

    current_moisture = soil_data["moisture_percent"]
    field_capacity = soil_data.get("field_capacity", 35)
    wilting_point = soil_data.get("wilting_point", 15)
    mad = 0.50
    threshold = field_capacity - (field_capacity - wilting_point) * mad

    if current_moisture > threshold:
        return {"irrigate": False, "reason": "Soil moisture adequate",
                "current": current_moisture, "threshold": threshold}

    efficiency = 0.92  # Drip irrigation: 90-95% in Israel
    gross_need = net_need / efficiency
    return {
        "irrigate": True,
        "net_need_mm": round(net_need, 1),
        "gross_need_mm": round(gross_need, 1),
        "current_moisture": current_moisture,
        "threshold": threshold,
        "et_crop": round(et_crop, 1)
    }
```

### שלב 4: אזורי אקלים חקלאיים בישראל

| אזור | מיקום | משקעים ממוצעים (מ"מ/שנה) | גידולים עיקריים | צורך בהשקיה |
|------|-------|--------------------------|----------------|-------------|
| ים תיכוני | מישור החוף, גליל | 500-700 | הדרים, אבוקדו, ירקות | בינוני (קיץ) |
| חצי-יבש | צפון הנגב, שפלה | 250-400 | חיטה, זיתים, גפנים | גבוה |
| יבש | מרכז הנגב | 50-200 | גידולי בעל מוגבלים | גבוה מאוד (השקיה מלאה) |
| קיצוני-יבש | ערבה | פחות מ-50 | תמרים, פלפלים, עגבניות | השקיה מלאה כל השנה |
| סובטרופי | בקעת הירדן, בית שאן | 300-400 | תמרים, בננות, בריכות דגים | גבוה (חום קיצוני) |

### שלב 5: סקירת מערכת האגריטק הישראלית
חברות מרכזיות מעבר לפלטפורמות הראשיות:
- **Phytec:** חיישנים מבוססי צמחים לזיהוי עקות מים
- **Manna Irrigation:** השקיה מבוססת לוויין, ללא חיישנים בקרקע
- **BeeHero:** ניטור IoT לכוורות לצורך האבקה
- **AgroScout:** סיור גידולים באמצעות רחפנים וזיהוי מחלות
- **Supplant:** חיישני פוטנציאל מים בגבעול לתזמון השקיה
- **SupPlant:** השקיה מונחית AI לחקלאים קטנים
- **Groundwork BioAg:** תרכובות מיקוריזה לשיפור קליטת חומרי הזנה

הקשר חקלאי ישראלי:
- ישראל ממחזרת מעל 85% ממי השפכים לחקלאות (השיעור הגבוה בעולם)
- מקורות מים: מקורות (ארצי), מי שפכים ממוחזרים, מים מותפלים, בארות מקומיות
- פורמטי נתונים: GeoJSON לגבולות שדות, GeoTIFF לתמונות לוויין, CSV/JSON לחיישנים

## דוגמאות

### דוגמה 1: הקמת מערכת השקיה חכמה
המשתמש אומר: "אני צריך להקים השקיה חכמה למטע אבוקדו בגליל"
תוצאה: הנחיית פריסת חיישני CropX (2 לכל אזור ניהול), חיבור לבקר נטפים, הגדרת ערכי Kc לאבוקדו, קביעת MAD על 50%, הטמעת תזמון מותאם מזג אוויר.

### דוגמה 2: צינור זיהוי מזיקים
המשתמש אומר: "איך אני משלב את Taranis לזיהוי מזיקים בשדות הפלפל שלנו?"
תוצאה: הגדרת גבולות שדות ב-Taranis, קביעת לוח סריקות (שבועי בעונת הגידול), מימוש webhook handler לזיהויים, יצירת צינור התראות לאיומים בחומרה גבוהה.

### דוגמה 3: לוח בקרה לעמידה בתקנות מים
המשתמש אומר: "בנו לוח בקרה שעוקב אחרי צריכת המים מול המכסה של רשות המים"
תוצאה: חיבור מדי זרימה דרך GrowSphere API, צבירת נתונים יומית/שבועית/חודשית, השוואה למכסה שהוקצתה, הפקת דוחות עמידה, התראה ב-80% וב-95%.

## משאבים מצורפים

### חומרי עזר
- `references/agritech-ecosystem.md` — מדריך לפלטפורמות ו-API של אגריטק ישראלי (CropX, Netafim GrowSphere, Taranis) עם פרטי endpoints, בנוסף לספריית חברות המכסה השקיה, ניטור גידולים, האבקה ומגזרים ביולוגיים. כולל פורמטי נתונים סטנדרטיים (GeoJSON, GeoTIFF, CSV/JSON), נתוני משקעים ומקורות מים לפי אזורים חקלאיים, ומקדמי גידול (Kc) של מכון וולקני לתנאים ישראליים. עיינו בו בעת בחירת פלטפורמות, הגדרת שילובי API, או חיפוש פרמטרי השקיה ספציפיים לגידולים.

## פתרון בעיות

### שגיאה: "קריאות חיישן נראות לא מדויקות"
סיבה: בעיית כיול חיישן קרקע או אי-התאמה בעומק ההתקנה
פתרון: חיישני CropX דורשים כיול ספציפי לסוג הקרקע. וודאו שעומק ההתקנה תואם לאזור השורשים של הגידול. סוגי הקרקע בישראל משתנים מאוד -- חול חופי לעומת לס בנגב לעומת בזלת בגולן.

### שגיאה: "המלצת ההשקיה גורמת להשקיית יתר"
סיבה: חישוב ET0 משתמש באזור אקלים שגוי או ערכי Kc מיושנים
פתרון: ודאו שתחנת מזג האוויר מקומית (מיקרו-אקלימים בישראל משתנים במרחקים קצרים). השתמשו בערכי Kc של מכון וולקני לתנאים ישראליים. בדקו שסוג הקרקע תואם את כיול החיישן.
