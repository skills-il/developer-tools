# Israeli Agritech Advisor Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a skill that guides developers in using Israeli agritech tools and precision agriculture platforms — CropX soil monitoring, Netafim GrowSphere IoT, Taranis crop intelligence, and other Israeli agritech APIs — for irrigation optimization, pest detection, and climate-smart farming.

**Architecture:** Domain-Specific Intelligence skill. Embeds knowledge of the Israeli agritech ecosystem (750+ companies), key platform APIs, precision agriculture best practices, and Israel-specific agricultural context.

**Tech Stack:** SKILL.md, API integration references, agricultural data processing scripts.

---

## Research

### Israeli Agritech Ecosystem
- Israel is a global leader in agritech with 750+ active companies
- Key factors: Water scarcity drives innovation, strong R&D ecosystem, military tech transfer
- Total investment: $1B+ in Israeli agritech startups (cumulative)
- Key verticals: Irrigation (drip invented here), crop monitoring, livestock tech, post-harvest, alternative protein

### CropX — Soil Monitoring API
- **What:** IoT soil sensors + cloud analytics platform for precision irrigation and fertilization
- **Sensors:** Measure soil moisture, temperature, EC (electrical conductivity), and VWC (volumetric water content) at multiple depths
- **API:** RESTful API with OAuth2 authentication
  - Endpoints: `/sites`, `/devices`, `/measurements`, `/recommendations`
  - Data: Real-time soil readings, historical trends, irrigation recommendations
  - Webhooks: Alerts for threshold breaches (too dry, too wet, salinity)
- **Integration:** Works with common irrigation controllers (Netafim, Jain, Valley, Lindsay)
- **Use case:** Optimize irrigation scheduling based on actual soil conditions, not timers

### Netafim GrowSphere — IoT Irrigation Platform
- **What:** Cloud-based precision irrigation management platform by Netafim (inventors of drip irrigation)
- **Features:** Real-time monitoring, automated fertigation, crop-specific irrigation programs
- **API/Integration:**
  - SCADA integration for irrigation controllers
  - REST API for reading sensor data and controlling valves
  - Endpoints: `/controllers`, `/zones`, `/schedules`, `/sensors`, `/alerts`
  - Supports: Flow meters, soil sensors, weather stations, valve control
- **Protocols:** MQTT for real-time sensor data, REST for management
- **Use case:** Automated fertigation scheduling, water use optimization, leak detection

### Taranis — Crop Intelligence Platform
- **What:** AI-powered crop monitoring using aerial imagery (drones, satellites, planes)
- **Features:** Sub-millimeter resolution imagery, pest/disease detection, weed mapping, stand count
- **API:**
  - Image upload and analysis endpoints
  - Field boundary management
  - Scouting report generation
  - Detection results: pest type, severity, location coordinates
- **AI models:** Detect 300+ crop threats including insects, diseases, nutrient deficiencies, weeds
- **Use case:** Early pest detection, targeted spraying maps, yield prediction

### Other Key Israeli Agritech Companies
- **Phytec:** Plant-based sensors measuring stem diameter for water stress detection
- **Manna Irrigation:** Satellite-based irrigation management, no ground sensors needed
- **Prospera (acquired by Valmont):** Computer vision for greenhouse monitoring
- **BeeHero:** IoT beehive monitoring for pollination optimization
- **Trellis:** AI crop advisor for agronomic decisions
- **AgroScout:** Drone-based crop scouting and disease detection
- **Supplant (formerly Saturas):** Stem water potential sensors for irrigation timing
- **SupPlant:** AI-driven growth and irrigation management for smallholder farmers
- **Groundwork BioAg:** Mycorrhizal inoculants for improved nutrient uptake

### Precision Agriculture Data Patterns
- **Soil data:** Moisture (%), temperature (C), EC (dS/m), VWC (m3/m3), depth layers (15/30/45/60cm)
- **Weather data:** Temperature, humidity, wind speed, precipitation, ET0 (reference evapotranspiration)
- **Crop data:** NDVI (vegetation index), leaf area index, chlorophyll content, canopy cover
- **Irrigation data:** Flow rate (m3/h), application amount (mm), uniformity (%), runtime (min)
- **Data formats:** GeoJSON for field boundaries, GeoTIFF for satellite imagery, CSV/JSON for sensor time series

### Israel-Specific Agricultural Context
- **Water:** Israel recycles 85%+ of wastewater for agriculture — highest rate globally
- **Climate zones:** Mediterranean coast, semi-arid Negev, arid Arava, subtropical Jordan Valley
- **Key crops:** Citrus, avocado, dates, peppers, tomatoes, herbs, flowers (export)
- **Growing seasons:** Year-round in south (Arava), dual season in center/north
- **Irrigation water sources:** Mekorot (national water company), recycled wastewater (shfachim), desalinated water, local wells
- **Regulations:** Water Authority quotas, Volcani Institute research standards

### Use Cases
1. **Irrigation optimization** — Connect soil sensors to scheduling logic for water savings
2. **Pest detection pipeline** — Set up aerial imagery processing for early threat detection
3. **Farm dashboard** — Aggregate data from multiple sensors/platforms into unified view
4. **Climate adaptation** — Use weather + soil data for climate-smart farming decisions
5. **Water compliance** — Track water usage against Israeli Water Authority quotas

---

## Build Steps

### Task 1: Create SKILL.md

```markdown
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

**CropX — Soil Monitoring Integration:**
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
        response = requests.get(
            f"{self.BASE_URL}/sites",
            headers=self.headers
        )
        return response.json()

    def get_soil_readings(self, device_id, start_date, end_date):
        """Get soil sensor readings for a device."""
        response = requests.get(
            f"{self.BASE_URL}/devices/{device_id}/measurements",
            headers=self.headers,
            params={
                "from": start_date.isoformat(),
                "to": end_date.isoformat(),
                "metrics": "moisture,temperature,ec"
            }
        )
        return response.json()

    def get_irrigation_recommendation(self, site_id):
        """Get AI-driven irrigation recommendation for a site."""
        response = requests.get(
            f"{self.BASE_URL}/sites/{site_id}/recommendations",
            headers=self.headers
        )
        return response.json()
```

**Netafim GrowSphere — Irrigation Control Integration:**
```python
class GrowSphereClient:
    """Client for Netafim GrowSphere irrigation platform."""

    BASE_URL = "https://api.growsphere.netafim.com/v1"

    def __init__(self, api_key):
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    def get_controllers(self):
        """List all irrigation controllers."""
        response = requests.get(
            f"{self.BASE_URL}/controllers",
            headers=self.headers
        )
        return response.json()

    def get_zone_status(self, controller_id, zone_id):
        """Get current status of an irrigation zone."""
        response = requests.get(
            f"{self.BASE_URL}/controllers/{controller_id}/zones/{zone_id}",
            headers=self.headers
        )
        return response.json()

    def create_irrigation_schedule(self, controller_id, zone_id, schedule):
        """Set irrigation schedule for a zone.

        schedule = {
            "start_time": "05:30",
            "duration_minutes": 45,
            "days": ["sun", "tue", "thu"],
            "fertigation": {"ec_target": 2.0, "ph_target": 6.5}
        }
        """
        response = requests.post(
            f"{self.BASE_URL}/controllers/{controller_id}/zones/{zone_id}/schedules",
            headers=self.headers,
            json=schedule
        )
        return response.json()

    def get_flow_data(self, controller_id, start_date, end_date):
        """Get water flow data for compliance tracking."""
        response = requests.get(
            f"{self.BASE_URL}/controllers/{controller_id}/flow",
            headers=self.headers,
            params={"from": start_date.isoformat(), "to": end_date.isoformat()}
        )
        return response.json()
```

**Taranis — Crop Intelligence Integration:**
```python
class TaranisClient:
    """Client for Taranis crop intelligence platform."""

    BASE_URL = "https://api.taranis.com/v1"

    def __init__(self, api_key):
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_fields(self):
        """List monitored fields."""
        response = requests.get(
            f"{self.BASE_URL}/fields",
            headers=self.headers
        )
        return response.json()

    def get_detections(self, field_id, scan_id=None):
        """Get pest/disease detections for a field.

        Returns list of detections with:
        - threat_type: 'pest', 'disease', 'weed', 'nutrient_deficiency'
        - name: specific threat name
        - severity: 'low', 'medium', 'high', 'critical'
        - location: GPS coordinates within field
        - confidence: detection confidence score
        """
        params = {}
        if scan_id:
            params["scan_id"] = scan_id

        response = requests.get(
            f"{self.BASE_URL}/fields/{field_id}/detections",
            headers=self.headers,
            params=params
        )
        return response.json()

    def request_scan(self, field_id, scan_type="full"):
        """Request a new aerial scan of a field."""
        response = requests.post(
            f"{self.BASE_URL}/fields/{field_id}/scans",
            headers=self.headers,
            json={"type": scan_type}
        )
        return response.json()
```

### Step 3: Implement Irrigation Optimization

```python
def calculate_irrigation_need(soil_data, crop_type, weather_data):
    """Calculate irrigation need based on soil, crop, and weather data.

    Uses water balance approach common in Israeli precision agriculture.
    """
    # Crop coefficients (Kc) — Israeli Volcani Institute values
    CROP_KC = {
        "citrus": {"initial": 0.65, "mid": 0.70, "late": 0.65},
        "avocado": {"initial": 0.60, "mid": 0.85, "late": 0.75},
        "tomato": {"initial": 0.60, "mid": 1.15, "late": 0.80},
        "pepper": {"initial": 0.60, "mid": 1.05, "late": 0.90},
        "date_palm": {"initial": 0.90, "mid": 0.95, "late": 0.95},
        "table_grape": {"initial": 0.30, "mid": 0.85, "late": 0.45},
    }

    kc = CROP_KC.get(crop_type, {"initial": 0.6, "mid": 1.0, "late": 0.8})

    # ET crop = ET0 * Kc (Penman-Monteith reference * crop coefficient)
    et_crop = weather_data["et0"] * kc["mid"]

    # Effective rainfall (Israeli climate: mostly winter rain, dry summers)
    effective_rain = max(0, weather_data.get("precipitation", 0) * 0.8)

    # Net irrigation need
    net_need = max(0, et_crop - effective_rain)

    # Adjust for soil moisture status
    current_moisture = soil_data["moisture_percent"]
    field_capacity = soil_data.get("field_capacity", 35)  # % for typical Israeli soil
    wilting_point = soil_data.get("wilting_point", 15)

    # Managed Allowable Depletion (MAD) — typically 50% for Israeli crops
    mad = 0.50
    threshold = field_capacity - (field_capacity - wilting_point) * mad

    if current_moisture > threshold:
        # Soil still has adequate moisture
        return {"irrigate": False, "reason": "Soil moisture adequate",
                "current": current_moisture, "threshold": threshold}

    # Application efficiency (drip irrigation: 90-95% in Israel)
    efficiency = 0.92
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

### Step 4: Pest Detection Pipeline

```python
def analyze_crop_threats(detections, field_area_hectares):
    """Analyze Taranis detections and create treatment recommendations."""

    threat_summary = {}
    for d in detections:
        key = f"{d['threat_type']}:{d['name']}"
        if key not in threat_summary:
            threat_summary[key] = {
                "type": d["threat_type"],
                "name": d["name"],
                "count": 0,
                "max_severity": "low",
                "locations": []
            }
        threat_summary[key]["count"] += 1
        threat_summary[key]["locations"].append(d["location"])

        severity_order = ["low", "medium", "high", "critical"]
        current = severity_order.index(threat_summary[key]["max_severity"])
        new = severity_order.index(d["severity"])
        if new > current:
            threat_summary[key]["max_severity"] = d["severity"]

    # Generate recommendations
    recommendations = []
    for key, threat in threat_summary.items():
        affected_pct = (threat["count"] / (field_area_hectares * 100)) * 100

        rec = {
            "threat": threat["name"],
            "type": threat["type"],
            "severity": threat["max_severity"],
            "affected_area_pct": round(affected_pct, 1),
            "action": "monitor"  # default
        }

        if threat["max_severity"] in ["high", "critical"]:
            rec["action"] = "treat_immediately"
            rec["method"] = "targeted_spray"  # Precision application
        elif threat["max_severity"] == "medium" and affected_pct > 10:
            rec["action"] = "treat_scheduled"
            rec["method"] = "spot_treatment"

        recommendations.append(rec)

    return sorted(recommendations,
                  key=lambda r: ["low", "medium", "high", "critical"].index(r["severity"]),
                  reverse=True)
```

### Step 5: Israeli Agricultural Climate Zones

| Zone | Region | Avg Rainfall (mm/yr) | Key Crops | Irrigation Need |
|------|--------|---------------------|-----------|----------------|
| Mediterranean | Coastal plain, Galilee | 500-700 | Citrus, avocado, vegetables | Moderate (summer) |
| Semi-arid | Northern Negev, Shephelah | 250-400 | Wheat, olives, grapes | High |
| Arid | Central Negev | 50-200 | Limited rainfed | Very high (full irrigation) |
| Hyper-arid | Arava Valley | <50 | Dates, peppers, tomatoes | Full irrigation year-round |
| Subtropical | Jordan Valley, Beit She'an | 300-400 | Dates, bananas, fish ponds | High (extreme heat) |

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
Solution: CropX sensors need soil-specific calibration. Verify installation depth matches crop root zone. Israeli soils vary dramatically — coastal sand vs. Negev loess vs. basalt in Golan.

### Error: "Irrigation recommendation overwatering"
Cause: ET0 calculation using wrong climate zone or outdated Kc values
Solution: Verify weather station is local (Israel's microclimates vary over short distances). Use Volcani Institute Kc values for Israeli conditions. Check soil type matches sensor calibration.
```
