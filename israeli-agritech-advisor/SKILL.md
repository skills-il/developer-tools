---
name: israeli-agritech-advisor
description: >-
  Guide developers in integrating Israeli agritech tools and precision agriculture
  platforms including CropX (soil monitoring), Netafim GrowSphere (IoT irrigation),
  Taranis (crop intelligence), and 750+ Israeli agritech companies. Use when user
  asks about agritech APIs, precision agriculture, smart irrigation, "hashkaya
  cham", crop monitoring, pest detection, Israeli agriculture tech, or needs to
  build farm management software. Covers irrigation optimization, pest detection,
  climate data integration, and Israeli agricultural context. Do NOT use for
  general gardening advice or non-agricultural IoT projects.
license: MIT
allowed-tools: "Bash(python:*) Bash(pip:*) Bash(curl:*)"
compatibility: "Network required for API calls. Python recommended for data processing. Works with Claude Code, Claude.ai."
metadata:
  author: skills-il
  version: 1.0.0
  category: developer-tools
  tags: [agritech, agriculture, irrigation, cropx, netafim, taranis, iot, israel]
---

# Israeli Agritech Advisor

## Instructions

### Step 1: Identify the Agritech Use Case
| Use Case | Key Platforms | Data Types | Goal |
|----------|--------------|------------|------|
| Irrigation optimization | CropX, Netafim, Manna | Soil moisture, weather, ET0 | Reduce water use 20-40% |
| Pest/disease detection | Taranis, AgroScout | Aerial imagery, NDVI | Early detection, targeted treatment |
| Greenhouse monitoring | Prospera/Valmont | Climate, imagery | Optimal growing conditions |
| Pollination management | BeeHero | Hive sensors, GPS | Maximize pollination efficiency |
| Farm data platform | Multiple | All sensor data | Unified decision dashboard |
| Water compliance | Mekorot data, sensors | Water flow, quotas | Meet Water Authority regulations |

### Step 2: Connect to Agritech APIs

**CropX -- Soil Monitoring Integration:**
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

**Netafim GrowSphere -- Irrigation Control Integration:**
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

**Taranis -- Crop Intelligence Integration:**
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

### Step 3: Implement Irrigation Optimization

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

### Step 4: Israeli Agricultural Climate Zones

| Zone | Region | Avg Rainfall (mm/yr) | Key Crops | Irrigation Need |
|------|--------|---------------------|-----------|----------------|
| Mediterranean | Coastal plain, Galilee | 500-700 | Citrus, avocado, vegetables | Moderate (summer) |
| Semi-arid | Northern Negev, Shephelah | 250-400 | Wheat, olives, grapes | High |
| Arid | Central Negev | 50-200 | Limited rainfed | Very high (full irrigation) |
| Hyper-arid | Arava Valley | less than 50 | Dates, peppers, tomatoes | Full irrigation year-round |
| Subtropical | Jordan Valley, Beit Shean | 300-400 | Dates, bananas, fish ponds | High (extreme heat) |

### Step 5: Israeli Agritech Ecosystem Overview
Key companies beyond the main platforms:
- **Phytec:** Plant-based sensors for water stress detection
- **Manna Irrigation:** Satellite-based irrigation, no ground sensors
- **BeeHero:** IoT beehive monitoring for pollination
- **AgroScout:** Drone-based crop scouting and disease detection
- **Supplant:** Stem water potential sensors for irrigation timing
- **SupPlant:** AI-driven irrigation for smallholder farmers
- **Groundwork BioAg:** Mycorrhizal inoculants for nutrient uptake

Israel-specific agricultural context:
- Israel recycles 85%+ of wastewater for agriculture (highest rate globally)
- Water sources: Mekorot (national), recycled wastewater, desalinated, local wells
- Data formats: GeoJSON for field boundaries, GeoTIFF for satellite imagery, CSV/JSON for sensors

## Examples

### Example 1: Smart Irrigation Setup
User says: "I need to set up smart irrigation for an avocado orchard in the Galilee"
Result: Guide CropX sensor placement (2 per management zone), connect to Netafim controller, configure Kc values for avocado, set MAD at 50%, implement weather-adjusted scheduling.

### Example 2: Pest Detection Pipeline
User says: "How do I integrate Taranis for pest detection in our pepper fields?"
Result: Set up Taranis field boundaries, configure scan schedule (weekly during growing season), implement detection webhook handler, create alert pipeline for high-severity threats.

### Example 3: Water Compliance Dashboard
User says: "Build a dashboard tracking water usage against our Water Authority quota"
Result: Connect flow meters via GrowSphere API, aggregate daily/weekly/monthly usage, compare against quota allocation, generate compliance reports, alert at 80% and 95% thresholds.

## Troubleshooting

### Error: "Sensor readings seem inaccurate"
Cause: Soil sensor calibration issue or installation depth mismatch
Solution: CropX sensors need soil-specific calibration. Verify installation depth matches crop root zone. Israeli soils vary dramatically -- coastal sand vs. Negev loess vs. basalt in Golan.

### Error: "Irrigation recommendation overwatering"
Cause: ET0 calculation using wrong climate zone or outdated Kc values
Solution: Verify weather station is local (Israel's microclimates vary over short distances). Use Volcani Institute Kc values for Israeli conditions. Check soil type matches sensor calibration.
