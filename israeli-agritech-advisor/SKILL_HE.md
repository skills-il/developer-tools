# יועץ אגריטק ישראלי

## הוראות

### שלב 1: זיהוי תרחיש השימוש באגריטק
| תרחיש שימוש | פלטפורמות מרכזיות | סוגי נתונים | מטרה |
|-------------|-------------------|-------------|------|
| מיטוב השקיה | CropX, נטפים, Phytech | לחות קרקע, מזג אוויר, ET0 | הפחתת צריכת מים ב-20-40% |
| זיהוי מזיקים/מחלות | Taranis, AgroScout | הדמייה אווירית, NDVI | זיהוי מוקדם, טיפול ממוקד |
| ניטור חממות | Prospera/Valmont | אקלים, הדמייה | תנאי גידול מיטביים |
| ניהול האבקה | BeeHero | חיישני כוורת, GPS | מיקסום יעילות האבקה |
| פלטפורמת נתוני חקלאות | מרובות | כל נתוני החיישנים | לוח בקרה אחוד לקבלת החלטות |
| עמידה בתקני מים | נתוני צריכה, חיישנים | זרימת מים, מכסות | עמידה בתקנות רשות המים |

### שלב 2: התחברות ל-API של אגריטק

**CropX -- שילוב ניטור קרקע:**

> **שימו לב:** כתובת ה-API והנתיבים למטה הם להמחשה בלבד. CropX לא מפרסמת תיעוד API ציבורי (אין דומיין developer או docs, ו-`api.cropx.com` מחזיר 404 בשורש), אז התייחסו לכתובת הבסיס, לנתיב `/auth/token` ולמבני התשובה כשלד להתאמה אחרי שתקבלו תיעוד אמיתי. פנו ל-CropX לגישת שותפים.
```python
import requests

class CropXClient:
    """Client for CropX soil monitoring API."""

    BASE_URL = "https://api.cropx.com/v2"  # API מבוסס שותפות, פנו ל-CropX לגישה

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

> **הערה:** כתובת ה-API של GrowSphere להמחשה בלבד. GrowSphere היא אפליקציית צרכנים ונטפים לא מפרסמת API ציבורי מתועד. פנו לנטפים ישירות לקבלת גישת API/שותפות.

```python
class GrowSphereClient:
    """Client for Netafim GrowSphere irrigation platform.
    NOTE: No documented public API exists. Contact Netafim for access."""

    BASE_URL = "https://growsphere.netafim.com/api/v1"  # לא מאומת, להמחשה בלבד

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

> **שימו לב:** כתובת ה-API למטה היא להמחשה בלבד והשרת שלה לא קיים כרגע (ל-`api.taranis.com` אין רשומת DNS נכון ל-2026-08-09). Taranis לא מפרסמת תיעוד API ציבורי. אל תכתבו קוד מול כתובת הבסיס הזו; פנו ל-Taranis לגישת שותפים והשתמשו בכתובת שהם ייתנו.
```python
class TaranisClient:
    """Client for Taranis crop intelligence platform."""

    BASE_URL = "https://api.taranis.com/v1"  # להמחשה בלבד; השרת לא קיים  # API מבוסס שותפות

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
def calculate_irrigation_need(soil_data, crop_type, weather_data,
                              growth_stage="mid", root_depth_mm=600,
                              ec_water_ds_m=None, ec_threshold_ds_m=None):
    """Decide whether to irrigate and by how much, using a soil water balance.

    UNITS ARE PART OF THE CONTRACT. Getting them wrong fails silently:
      soil_data["moisture_percent"]  volumetric water content, % by volume
                                     (this is what CropX reports as VWC).
                                     A gravimetric or percent-of-available
                                     reading here produces a confident wrong
                                     answer, so convert before calling.
      soil_data["field_capacity"]    %vol at field capacity
      soil_data["wilting_point"]     %vol at permanent wilting point
      weather_data["et0"]            mm/day, FAO Penman-Monteith reference ET.
                                     Kc values below are defined against FAO-PM
                                     specifically; pan-evaporation or Hargreaves
                                     ET0 biases the result by 10-20%.
      weather_data["precipitation"]  mm over the same one-day period
      root_depth_mm                  effective root-zone depth, mm. This is the
                                     term that converts a volumetric fraction
                                     into a depth of water; without it a field
                                     at wilting point and a field one point
                                     below threshold get the same answer.
      ec_water_ds_m                  irrigation water EC, dS/m (optional)
      ec_threshold_ds_m              crop salinity threshold ECe, dS/m (optional)

    There are no safe defaults for field capacity and wilting point. Israeli
    soils span coastal sand (FC roughly 10-14 %vol), Negev loess (roughly
    22-28) and Golan basaltic clay (roughly 40-48); one default is wrong for
    most of them. Measure or look up the values for the actual field.
    """
    # Crop coefficients (Kc) from FAO Irrigation and Drainage Paper 56, Table 12.
    # These are FAO standard values, NOT Volcani/ARO values. FAO-56 publishes
    # them for subhumid conditions (RHmin about 45%, wind about 2 m/s), so in
    # the Arava and the Jordan Valley they UNDER-predict ETc and need the
    # FAO-56 climate adjustment before use.
    CROP_KC = {
        # FAO-56 citrus is banded by canopy cover, and Kc_mid is LOWER than
        # Kc_ini because of stomatal closure at peak ET. This is the 50%-canopy
        # row; use 0.70/0.65/0.70 at 70% canopy and 0.50/0.45/0.55 at 20%.
        "citrus": {"initial": 0.65, "mid": 0.60, "late": 0.65},
        "avocado": {"initial": 0.60, "mid": 0.85, "late": 0.75},
        "tomato": {"initial": 0.60, "mid": 1.15, "late": 0.80},
        "pepper": {"initial": 0.60, "mid": 1.05, "late": 0.90},
        "date_palm": {"initial": 0.90, "mid": 0.95, "late": 0.95},
        "table_grape": {"initial": 0.30, "mid": 0.85, "late": 0.45},
    }
    if growth_stage not in ("initial", "mid", "late"):
        raise ValueError("growth_stage must be initial, mid or late")

    field_capacity = soil_data["field_capacity"]
    wilting_point = soil_data["wilting_point"]
    current_moisture = soil_data["moisture_percent"]
    if not wilting_point < field_capacity:
        raise ValueError("wilting_point must be below field_capacity (both %vol)")
    if not 0 <= current_moisture <= 100:
        raise ValueError("moisture_percent must be volumetric water content, 0-100")

    kc_row = CROP_KC.get(crop_type, {"initial": 0.6, "mid": 1.0, "late": 0.8})
    kc = kc_row[growth_stage]
    et_crop = weather_data["et0"] * kc
    # 0.8 is a coarse effective-rainfall factor. It is inert during the Israeli
    # irrigation season (May to October is essentially rainless) and unreliable
    # on crusting loess and vertisols under winter storms, so replace it with a
    # measured runoff fraction if you have one.
    effective_rain = max(0, weather_data.get("precipitation", 0) * 0.8)

    # Management allowed depletion: the share of plant-available water you let
    # the crop use before refilling. 0.50 comes from infrequent-application
    # scheduling. Israeli high-frequency drip typically runs 0.25-0.40, and
    # lower still for salt-sensitive or shallow-rooted crops, because keeping
    # the root zone near field capacity limits both matric and osmotic stress.
    mad = soil_data.get("mad", 0.35)
    threshold = field_capacity - (field_capacity - wilting_point) * mad

    # The actual soil water deficit, in mm: how much water it takes to bring the
    # root zone back to field capacity. This is the quantity a valve should act
    # on, and it depends on how dry the soil is, not only on yesterday's ET.
    deficit_mm = max(0.0, (field_capacity - current_moisture) / 100.0 * root_depth_mm)

    if current_moisture > threshold:
        return {
            "irrigate": False,
            "reason": "Soil moisture above the refill threshold",
            "current_moisture": current_moisture,
            "threshold": round(threshold, 1),
            "deficit_mm": round(deficit_mm, 1),
            "et_crop_mm": round(et_crop, 1),
            "net_need_mm": 0.0,
            "gross_need_mm": 0.0,
            "leaching_fraction": None,
        }

    # Refill the deficit, plus this period's crop demand net of effective rain.
    net_need = deficit_mm + max(0, et_crop - effective_rain)

    # Leaching requirement (FAO-29 / Ayers and Westcot). Israeli agriculture
    # runs heavily on reclaimed effluent and brackish well water, so salts
    # accumulate in the root zone unless a fraction of applied water pushes
    # them below it. Skipping this progressively salinizes an Arava or Jordan
    # Valley root zone with nothing in the system noticing. Avocado and citrus
    # are among the most salt-sensitive crops grown here.
    leaching_fraction = None
    if ec_water_ds_m and ec_threshold_ds_m:
        denom = 5 * ec_threshold_ds_m - ec_water_ds_m
        if denom <= 0:
            raise ValueError(
                "Water EC is too high for this crop: no leaching fraction can "
                "keep the root zone below its salinity threshold. Blend with a "
                "lower-EC source or change crop."
            )
        leaching_fraction = ec_water_ds_m / denom
        net_need = net_need / (1 - leaching_fraction)

    # Application efficiency stands in for distribution uniformity, which is a
    # measured and DRIFTING quantity: drip lines on reclaimed effluent biofoul
    # and clog, so a constant here hides the degradation. Measure emission
    # uniformity periodically and feed the real number in.
    efficiency = soil_data.get("application_efficiency", 0.90)
    gross_need = net_need / efficiency
    return {
        "irrigate": True,
        "reason": "Soil moisture at or below the refill threshold",
        "current_moisture": current_moisture,
        "threshold": round(threshold, 1),
        "deficit_mm": round(deficit_mm, 1),
        "et_crop_mm": round(et_crop, 1),
        "net_need_mm": round(net_need, 1),
        "gross_need_mm": round(gross_need, 1),
        "leaching_fraction": round(leaching_fraction, 3) if leaching_fraction else None,
    }
```

### שלב 4: אזורי אקלים חקלאיים בישראל

| אזור | מיקום | משקעים ממוצעים (מ"מ/שנה) | גידולים עיקריים | צורך בהשקיה |
|------|-------|--------------------------|----------------|-------------|
| ים תיכוני | מישור החוף, גליל | 500-700 | הדרים, אבוקדו, ירקות | בינוני (קיץ) |
| חצי-יבש | צפון הנגב | 250-400 | חיטה, זיתים, גפנים | גבוה |
| חצי-יבש עד ים תיכוני | שפלה | 400-500 | חיטה, זיתים, כרמים, מטעים | בינוני עד גבוה |
| יבש | מרכז הנגב | 50-200 | גידולי בעל מוגבלים | גבוה מאוד (השקיה מלאה) |
| קיצוני-יבש | ערבה | פחות מ-50, במדרג מצפון לדרום (הערבה הצפונית גשומה מהדרומית) | תמרים, פלפלים, עגבניות | השקיה מלאה כל השנה |
| סובטרופי | בית שאן ובקעת הירדן הצפונית. המשקעים יורדים בחדות דרומה לאורך הבקע, אז אל תחילו רצועה אחת על כל הבקעה | כ-300 בבית שאן, ופחות בהרבה דרומה | תמרים, בננות, בריכות דגים | גבוה (חום קיצוני) |

### שלב 5: סקירת מערכת האגריטק הישראלית

הסביבה הישראלית מונה כ-600 עד 750 חברות אגריטק ואגרי-פוד-טק (לפי הערכות Start-Up Nation Central), חלק נכבד מהן צמח מתוך קיבוצים ומכוני מחקר.

חברות מרכזיות מעבר לפלטפורמות הראשיות:
- **Phytech:** חיישנים מבוססי צמחים לזיהוי עקות מים. בלעה ב-2024 את פעילות Manna להשקיה מבוססת לוויין של Rivulis, ולכן Manna אינה עוד ספק נפרד להתממשק אליו.
- **BeeHero:** ניטור IoT לכוורות לצורך האבקה
- **BeeWise:** כוורות רובוטיות מנוהלות ב-AI ("Beehome") לניהול אוטונומי של מושבות דבורים
- **AgroScout:** סיור גידולים דרך רחפנים וזיהוי מחלות
- **Tevel Aerobotics:** רחפנים אוטונומיים לקטיף פירות, מחוברים בכבל ליחידת קרקע
- **SupPlant:** השקיה מונחית AI לחקלאים קטנים
- **Groundwork BioAg:** תרכובות מיקוריזה לשיפור קליטת חומרי הזנה
- **BioBee:** הדברה ביולוגית (biobee.com)

הטקסונומיה של האגריטק הישראלי רחבה בהרבה מפרוסת ההשקיה וניטור הגידולים שלמעלה. מגזרים שהסקיל הזה אינו מכסה, וכל אחד מהם קטגוריה מוגדרת במיפוי של Start-Up Nation Central, הם: חקלאות ימית, פוסט-הרוורסט (אחסון, אריזה, ציפויים), מערכות גידול חדשניות (חקלאות אנכית, הידרופוניקה, גידול בסביבה מבוקרת), בעלי חיים וטכנולוגיות משק חי, ביוטכנולוגיה והשבחת צמחים, טכנולוגיות פסולת, גידולים מיוחדים, פלטפורמות מסחר ישיר לצרכן, חלבון חלופי, ורובוטיקה חקלאית מעבר לקטיף פרי. אם שאלת המשתמש יושבת באחד מהם, אמרו זאת במקום לדחוס אותה למסגרת של השקיה או ניטור.

הקשר חקלאי ישראלי:
- ישראל מובילה בעולם בשיעור מיחזור המים. ה-EPA האמריקאי נוקב בקרוב ל-90 אחוז מהשפכים המטופלים שחוזרים להשקיה. רשות המים אינה מפרסמת אחוז מיחזור לאומי אחד, ולכן צטטו את הנתון יחד עם מקורו במקום לנקוב במספר לאומי חשוף.
- מקורות מים: מקורות (ארצי), מי שפכים ממוחזרים, מים מותפלים, בארות מקומיות.
- ההתפלה היא חלק מרכזי במערך: מתקני שורק, חדרה ואשקלון (בין היתר) מזרימים מים למקורות בכמויות גדולות, וישראל מובילה בעולם בהתפלת מי-ים בטכנולוגיית RO.
- חידוש מהקיבוצים נמצא בלב התעשייה: קיבוץ חצרים חתם עם שמחה בלאס והקים את נטפים ב-1965, וייצור הטפטפות החל בינואר 1966. הטפטוף נשאר סמל הייצוא הישראלי. נטפים בשליטת Orbia והוצעה למכירה, אז אל תקבעו את זהות החברה-האם בשום מקום קבוע.
- פורמטי נתונים: GeoJSON לגבולות שדות, GeoTIFF לתמונות לוויין, CSV/JSON לחיישנים.

## דוגמאות

### דוגמה 1: הקמת מערכת השקיה חכמה
המשתמש אומר: "אני צריך להקים השקיה חכמה למטע אבוקדו בגליל"
תוצאה: הנחיית פריסת חיישני CropX לפי אזורי שונות בקרקע (עומק ההתקנה חייב לשבת בתוך בצל ההרטבה של הטפטפת, וזו הסיבה הרגילה ל"הקריאות נראות שגויות"), חיבור לבקר נטפים, הגדרת מקדמי Kc של FAO-56 לאבוקדו לפי שלב גידול, קביעת MAD בקצה הנמוך לגידול רגיש-מלח בטפטוף בתדירות גבוהה, הזנת קיבול השדה ונקודת הכמישה שנמדדו בפועל במקום ברירות מחדל, והעברת מוליכות חשמלית של המים יחד עם סף המליחות של האבוקדו כדי שיוחל מקדם שטיפה.

### דוגמה 2: צינור זיהוי מזיקים
המשתמש אומר: "איך אני משלב את Taranis לזיהוי מזיקים בשדות הפלפל שלנו?"
תוצאה: הגדרת גבולות שדות ב-Taranis, קביעת לוח סריקות (שבועי בעונת הגידול), מימוש webhook handler לזיהויים, יצירת צינור התראות לאיומים בחומרה גבוהה.

### דוגמה 3: לוח בקרה לעמידה בתקנות מים
המשתמש אומר: "בנו לוח בקרה שעוקב אחרי צריכת המים מול המכסה של רשות המים"
תוצאה: חיבור מדי זרימה דרך GrowSphere API, צבירת נתונים יומית/שבועית/חודשית, השוואה למכסה שהוקצתה, הפקת דוחות עמידה, והתראה בשיעור הניצול שהמגדל בוחר (בדרך כלל התראה מקדימה ועוד התראה סמוך לתקרה; הספים הם החלטת עיצוב ולא דרישה רגולטורית).

## משאבים מצורפים

### חומרי עזר
- `references/agritech-ecosystem.md`, מדריך לפלטפורמות ו-API של אגריטק ישראלי (CropX, Netafim GrowSphere, Taranis) עם פרטי endpoints, בנוסף לספריית חברות המכסה השקיה, ניטור גידולים, האבקה ומגזרים ביולוגיים. כולל פורמטי נתונים סטנדרטיים (GeoJSON, GeoTIFF, CSV/JSON), נתוני משקעים ומקורות מים לפי אזורים חקלאיים, ומקדמי גידול (Kc) לפי FAO-56 טבלה 12. עיינו בו בעת בחירת פלטפורמות, הגדרת שילובי API, או חיפוש פרמטרי השקיה ספציפיים לגידולים.

## שרתי MCP מומלצים

אין כרגע MCP ייעודי לאגריטק בספרייה. עבור נתוני מזג אוויר שמזינים מודלי השקיה, [שרת ה-MCP של השירות המטאורולוגי הישראלי (`ims-weather`)](https://agentskills.co.il/he/mcp/ims-weather) מספק נתוני גשם, ET0 ותחנות מודדים דרך ה-API הרשמי של ה-IMS.

## קישורי עזר

| מקור | URL | מה לבדוק |
|------|-----|----------|
| מכון וולקני / מנהל המחקר החקלאי | https://www.agri.gov.il | מחקר אגרונומי בהקשר ישראלי ומחקרי כיול מקומיים |
| FAO Irrigation and Drainage Paper 56, טבלה 12 | https://www.fao.org/4/x0490e/x0490e0b.htm | מקדמי גידול (Kc התחלתי / אמצע / סוף). המקור לערכי ה-Kc שבסקיל הזה |
| משרד החקלאות וביטחון המזון | https://www.gov.il/he/departments/ministry_of_agriculture_and_food_security | תוכניות סבסוד, רגולציה ותעודות. המשרד שונה משמו הקודם "החקלאות ופיתוח הכפר", והכתובת הישנה מחזירה 404 |
| רשות המים | https://www.gov.il/he/departments/water_authority | מכסות מים, עדכוני תעריפי חקלאות, וכללי מים מושבים. זהו הרגולטור שמקצה, ולא מקורות |
| רשות החדשנות | https://innovationisrael.org.il | מענקי אגריטק ותוכניות פיילוט, כולל הקולות הקוראים המשותפים לחקלאות מתקדמת עם משרד החקלאות וביטחון המזון. האתר מוגן ב-Cloudflare: שליפות אוטומטיות נחסמות והוא עלול לדרוש CAPTCHA, אז פתחו אותו בדפדפן אמיתי |
| Start-Up Nation Central, AgriFoodTech | https://startupnationcentral.org/AgriTech/ | מדריך תעשייה ונתוני שלבי חברות לאקוסיסטם האגריטק הישראלי |

## מלכודות נפוצות

- מליחות היא אילוץ מסדר ראשון בהשקיה הישראלית ובדרך כלל מתעלמים ממנה. חלק ניכר מהמים הם קולחין או מים מליחים מבארות, ולכן מלחים מצטברים באזור השורשים אלא אם מקדם שטיפה דוחף אותם מתחתיו. אבוקדו והדרים, שני הגידולים שהסקיל הזה מציב בחזית, הם מהרגישים ביותר למלח מבין הגידולים כאן. סוכנים מדגמנים ETc ולחות קרקע, מבקשים EC מ-API החיישנים, ואז לא משתמשים בו כלל, ומייצרים בקר שממליח לאט את אזור השורשים בלי ששום רכיב במערכת מבחין. למים מותפלים יש בעיה הפוכה: הם דלים בסידן, במגנזיום ובסולפט וזקוקים להעשרה מחדש עבור הגידולים האלה.
- עונות החקלאות הישראליות שונות מדפוסי צפון אירופה/ארה"ב בגלל האקלים הים-תיכוני. סוכנים עלולים להמליץ על לוחות זריעה מבוססי אקלים ממוזג.
- הקצאת מים בחקלאות ישראלית נקבעת על ידי רשות המים ולא על ידי מקורות. מקורות היא חברת המים הלאומית שמספקת את המים, אך סמכות ההקצאה והאסדרה נתונה למנהל רשות המים מכוח תקנות הקצאת המים לחקלאות. סוכנים נוטים לנקוב במקורות כרגולטור, וגם להתעלם לחלוטין ממגבלות מכסה כשהם ממליצים על תוכנית השקיה.
- תעריפי המים לחקלאות מתעדכנים אחת לשנה בתוקף מ-1 בינואר, אחרי סבב שימוע ציבורי שמנהלת רשות המים. המבנה הנוכחי קושר את תעריף המים השפירים של הצרכן למדרגה שמשקפת כמה מים נחותים (קולחין, שפד"ן, מליחים) זמינים לו, עם מקדמים נפרדים למקורות מליחים וקולחין. כל נתון תעריף שבידיכם הוא לכן מתוארך: קראו את הטבלה העדכנית מרשות המים לפני שאתם נוקבים במחיר, ולעולם אל תקבעו תעריף בשקלים למ"ק בתוך מודל עלות.
- ההסמכה האורגנית בישראל פועלת מכוח חוק ותקנות האורגני הישראליים, בפיקוח השירותים להגנת הצומח ולביקורת (השג"ב) ובאמצעות גופי הסמכה מוכרים כמו אגריאור, IQC וסקאל ישראל. זה אינו אותו תקן כמו USDA Organic או EU Organic, ואין מסלול בשם "מקורי". סוכנים גם ממציאים שם למסלול וגם מניחים שכללי ארה"ב או האיחוד חלים.
- סבסוד טכנולוגיות חקלאיות ממשרד החקלאות וביטחון המזון משתנה מדי שנה. סוכנים עלולים להתייחס לתוכניות סבסוד מיושנות.
- שנת השמיטה משפיעה על פעילות חקלאית שומרת מצוות. היא נמשכת מראש השנה לראש השנה ולא לפי השנה הלועזית, ולכן היא אינה מתיישרת לא עם שנת ההקצאה ולא עם שנת התעריפים, ומערכת שמדגמנת גבול אחד תטעה בשני. שנת השמיטה הבאה היא תשפ"ט (סתיו 2028 עד סתיו 2029). המנגנונים המעשיים מייצרים התנהגות תוכנה שונה (היתר מכירה, אוצר בית דין, גידול במצע מנותק), ולפי רוב הפוסקים ההשקיה מוגבלת למה שדרוש כדי להחיות את הצמח, וזה שינוי במערכת כללי ההשקיה עצמה. סוכנים לרוב אינם יודעים שהמחזור קיים, וכשכן, הם עוגנים אותו לשנה קלנדרית.

## פתרון בעיות

### שגיאה: "קריאות חיישן נראות לא מדויקות"
סיבה: בעיית כיול חיישן קרקע או אי-התאמה בעומק ההתקנה
פתרון: חיישני CropX דורשים כיול ספציפי לסוג הקרקע. וודאו שעומק ההתקנה תואם לאזור השורשים של הגידול. סוגי הקרקע בישראל משתנים מאוד -- חול חופי לעומת לס בנגב לעומת בזלת בגולן.

### שגיאה: "המלצת ההשקיה גורמת להשקיית יתר"
סיבה: חישוב ET0 משתמש באזור אקלים שגוי או ערכי Kc מיושנים
פתרון: ודאו שתחנת מזג האוויר מקומית (מיקרו-אקלימים בישראל משתנים במרחקים קצרים). בדקו את מקור ה-Kc ואת שלב הגידול: הערכים בסקיל הזה הם תקני FAO-56 טבלה 12, וב-FAO-56 מקדם ה-Kc של הדרים באמצע העונה נמוך מזה שבתחילתה, ולכן מודל שמניח שאמצע העונה הוא תמיד השיא ישקה הדרים ביתר. ודאו שסוג הקרקע תואם את כיול החיישן.
