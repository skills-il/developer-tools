---
name: israeli-agritech-advisor
description: Guide developers in integrating Israeli agritech tools and precision agriculture platforms including CropX (soil monitoring), Netafim GrowSphere (IoT irrigation), Taranis (crop intelligence), and the broader Israeli agritech ecosystem (approximately 600-750 companies per Start-Up Nation Central agrifoodtech). Use when user asks about agritech APIs, precision agriculture, smart irrigation, "hashkaya cham", crop monitoring, pest detection, Israeli agriculture tech, or needs to build farm management software. Covers irrigation optimization, pest detection, climate data integration, and Israeli agricultural context. Do NOT use for general gardening advice or non-agricultural IoT projects.
license: MIT
allowed-tools: Bash(python:*) Bash(pip:*) Bash(curl:*)
compatibility: Network required for API calls. Python recommended for data processing. Works with Claude Code, Claude.ai.
version: 1.1.0
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

> **Note:** The GrowSphere API URL below is illustrative. GrowSphere is a consumer app and Netafim does not publish a documented public API. Contact Netafim directly for partnership/API access.

```python
class GrowSphereClient:
    """Client for Netafim GrowSphere irrigation platform.
    NOTE: No documented public API exists. Contact Netafim for access."""

    BASE_URL = "https://growsphere.netafim.com/api/v1"  # Unverified, illustrative only

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
- **Phytech:** Plant-based sensors for water stress detection
- **Manna Irrigation:** Satellite-based irrigation, no ground sensors
- **BeeHero:** IoT beehive monitoring for pollination
- **BeeWise:** Robotic, AI-managed beehives ("Beehome") for autonomous hive management
- **AgroScout:** Drone-based crop scouting and disease detection
- **Tevel Aerobotics:** Autonomous fruit-picking drones tethered to ground units
- **SupPlant:** AI-driven irrigation for smallholder farmers
- **Phytech:** Plant-based water stress sensors (acquired Saturas in 2023)
- **Groundwork BioAg:** Mycorrhizal inoculants for nutrient uptake
- **Agropalette:** Data and analytics for produce supply chains

Israel-specific agricultural context:
- Israel recycles 85%+ of wastewater for agriculture (highest rate globally)
- Water sources: Mekorot (national), recycled wastewater, desalinated, local wells
- Desalination feeds the system at scale: the Sorek, Hadera, and Ashkelon plants (among others) supply Mekorot's potable and agricultural mix, making Israel a global leader in seawater reverse osmosis.
- Kibbutz innovation underpins much of the sector: Netafim's drip irrigation originated at Kibbutz Hatzerim in 1965 and remains a defining export.
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

## Bundled Resources

### References
- `references/agritech-ecosystem.md` ,  Directory of Israeli agritech platforms and APIs (CropX, Netafim GrowSphere, Taranis) with endpoint details, plus a company directory covering irrigation, crop monitoring, pollination, and biological sectors. Includes standard data formats (GeoJSON, GeoTIFF, CSV/JSON), agricultural zone rainfall and water source data, and Volcani Institute crop coefficients (Kc) for Israeli conditions. Consult when selecting platforms, configuring API integrations, or looking up crop-specific irrigation parameters.

## Recommended MCP Servers

No agritech-specific MCP server is currently in the directory. For weather data feeding irrigation models, the [Israel Meteorological Service MCP (`ims-mcp`)](https://agentskills.co.il/he/mcps/government-services/ims-mcp) provides rain, ET0, and station data via official IMS endpoints.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Volcani Institute / Agricultural Research Organization | https://www.agri.gov.il | Crop coefficient (Kc) tables, Israeli-context agronomy research |
| Israel Ministry of Agriculture and Rural Development | https://www.gov.il/en/departments/ministry_of_agriculture_and_rural_development | Subsidy programs, regulations, and certifications |
| Israel Water Authority | https://www.gov.il/en/departments/water_authority | Water allocation quotas, agricultural-tariff updates, and reclaimed-water rules |
| Israel Innovation Authority | https://innovationisrael.org.il/en | Agritech grants and pilot funding programs |
| Start-Up Nation Central -- AgriFoodTech | https://www.startupnationcentral.org | Industry directory and company-stage data for the Israeli agritech ecosystem |

## Gotchas

- Israeli agricultural seasons differ from Northern European/US patterns due to the Mediterranean climate. Agents may recommend planting schedules based on temperate-zone assumptions.
- Water allocation in Israeli agriculture is regulated by Mekorot (the national water company). Agents may not account for water quota restrictions when recommending irrigation plans.
- Israeli organic certification ("Mekori") follows different standards than USDA Organic or EU Organic. Agents may cite incorrect certification requirements.
- Agricultural technology subsidies from the Israeli Ministry of Agriculture change annually. Agents may reference outdated subsidy programs or amounts.
- Shmita (sabbatical year) laws affect religious agricultural operations in Israel every 7 years. Agents may not be aware of this religious agricultural cycle and its implications.

## Troubleshooting

### Error: "Sensor readings seem inaccurate"
Cause: Soil sensor calibration issue or installation depth mismatch
Solution: CropX sensors need soil-specific calibration. Verify installation depth matches crop root zone. Israeli soils vary dramatically, coastal sand vs. Negev loess vs. basalt in Golan.

### Error: "Irrigation recommendation overwatering"
Cause: ET0 calculation using wrong climate zone or outdated Kc values
Solution: Verify weather station is local (Israel's microclimates vary over short distances). Use Volcani Institute Kc values for Israeli conditions. Check soil type matches sensor calibration.