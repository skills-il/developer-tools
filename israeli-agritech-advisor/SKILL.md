---
name: israeli-agritech-advisor
description: Guide developers in integrating Israeli agritech tools and precision agriculture platforms including CropX (soil monitoring), Netafim GrowSphere (IoT irrigation), Taranis (crop intelligence), and the broader Israeli agritech ecosystem. Use when user asks about agritech APIs, precision agriculture, smart irrigation, "hashkaya cham", crop monitoring, pest detection, Israeli agriculture tech, or needs to build farm management software. Covers irrigation optimization, pest detection, climate data integration, and Israeli agricultural context. Do NOT use for general gardening advice or non-agricultural IoT projects.
license: MIT
allowed-tools: Bash(python:*) Bash(pip:*) Bash(curl:*)
compatibility: Network required for API calls. Python recommended for data processing. Works with Claude Code, Claude.ai.
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

> **Note:** The CropX API URL and routes below are illustrative. CropX publishes no public API documentation (there is no developer or docs subdomain, and `api.cropx.com` returns 404 at its root), so treat the base URL, the `/auth/token` route and the response shapes as a sketch to adapt once CropX gives you real integration docs. Contact CropX for partner API access.
```python
import requests

class CropXClient:
    """Client for CropX soil monitoring API."""

    BASE_URL = "https://api.cropx.com/v2"  # Unverified, illustrative only

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

> **Note:** The Taranis API URL below is illustrative and its host does not currently resolve (`api.taranis.com` has no DNS record as of 2026-08-09). Taranis publishes no public API documentation. Do not code against this base URL; contact Taranis for partner API access and use the base URL they supply.
```python
class TaranisClient:
    """Client for Taranis crop intelligence platform."""

    BASE_URL = "https://api.taranis.com/v1"  # Unverified, illustrative only; host does not resolve

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

### Step 4: Israeli Agricultural Climate Zones

| Zone | Region | Avg Rainfall (mm/yr) | Key Crops | Irrigation Need |
|------|--------|---------------------|-----------|----------------|
| Mediterranean | Coastal plain, Galilee | 500-700 | Citrus, avocado, vegetables | Moderate (summer) |
| Semi-arid | Northern Negev | 250-400 | Wheat, olives, grapes | High |
| Semi-arid to Mediterranean | Shephelah | 400-500 | Wheat, olives, vineyards, orchards | Moderate to high |
| Arid | Central Negev | 50-200 | Limited rainfed | Very high (full irrigation) |
| Hyper-arid | Arava Valley | under 50, on a north-to-south gradient (the northern Arava is wetter than the southern) | Dates, peppers, tomatoes | Full irrigation year-round |
| Subtropical | Beit Shean and the northern Jordan Valley. Rainfall drops steeply southward down the rift, so do not apply one band to the whole valley | roughly 300 at Beit Shean, far lower to the south | Dates, bananas, fish ponds | High (extreme heat) |

### Step 5: Israeli Agritech Ecosystem Overview
Key companies beyond the main platforms:
- **Phytech:** Plant-based sensors for water stress detection. Absorbed Rivulis's Manna satellite-irrigation business in 2024, so Manna is no longer a separate vendor to integrate against.
- **BeeHero:** IoT beehive monitoring for pollination
- **Beewise:** Robotic, AI-managed beehives ("Beehome") for autonomous hive management
- **AgroScout:** Drone-based crop scouting and disease detection (agro-scout.com)
- **Tevel Aerobotics:** Autonomous fruit-picking drones tethered to ground units
- **SupPlant:** Now a sensor-less WhatsApp irrigation advisor branded "Plant", not a sensor platform. Check the current product before designing an integration.
- **Groundwork BioAg:** Mycorrhizal inoculants, now positioned around soil carbon removal as well as nutrient uptake
- **BioBee:** Biological pest control (biobee.com)

The Israeli agritech taxonomy is broader than the irrigation and crop-monitoring
slice above. Segments this skill does not cover, each of which is a named
category in the Start-Up Nation Central mapping, are: aquaculture, post-harvest
(storage, packaging, coatings), novel farming systems (vertical farming,
hydroponics, controlled-environment agriculture), livestock and animal tech,
plant biotech and breeding, waste technologies, special crops, farm-to-consumer
trading platforms, alternative protein, and farm robotics beyond fruit picking.
If the user's question sits in one of those, say so rather than forcing it into
an irrigation or scouting frame.

Israel-specific agricultural context:
- Israel leads the world in the proportion of water it recycles. The US EPA puts it at nearly 90 percent of treated wastewater reused for irrigation. The Water Authority does not publish a single headline reuse percentage, so cite the figure with its source rather than stating a bare national number.
- Water sources: Mekorot (national), recycled wastewater, desalinated, local wells
- Desalination feeds the system at scale: the Sorek, Hadera, and Ashkelon plants (among others) supply Mekorot's potable and agricultural mix, making Israel a global leader in seawater reverse osmosis.
- Kibbutz innovation underpins much of the sector: Kibbutz Hatzerim signed an agreement with Simcha Blass and founded Netafim in 1965, with dripper manufacturing starting in January 1966. Drip irrigation remains a defining Israeli export. Netafim is currently majority-owned by Orbia and has been put up for sale, so avoid hardcoding its corporate parent into anything durable.
- Data formats: GeoJSON for field boundaries, GeoTIFF for satellite imagery, CSV/JSON for sensors

## Examples

### Example 1: Smart Irrigation Setup
User says: "I need to set up smart irrigation for an avocado orchard in the Galilee"
Result: Guide CropX sensor placement by soil-variability zone (installation depth must sit in the wetted bulb of a dripper, which is the usual cause of "readings look wrong"), connect to the Netafim controller, configure FAO-56 Kc for avocado BY GROWTH STAGE, set MAD toward the low end for a salt-sensitive crop on high-frequency drip, supply the field's measured field capacity and wilting point rather than defaults, and pass water EC plus avocado's salinity threshold so a leaching fraction is applied.

### Example 2: Pest Detection Pipeline
User says: "How do I integrate Taranis for pest detection in our pepper fields?"
Result: Set up Taranis field boundaries, configure scan schedule (weekly during growing season), implement detection webhook handler, create alert pipeline for high-severity threats.

### Example 3: Water Compliance Dashboard
User says: "Build a dashboard tracking water usage against our Water Authority quota"
Result: Connect flow meters via GrowSphere API, aggregate daily/weekly/monthly usage, compare against quota allocation, generate compliance reports, and alert at whatever share of quota the grower chooses (an early warning plus a near-limit warning is the usual shape; the thresholds are a design choice, not a regulatory requirement).

## Bundled Resources

### References
- `references/agritech-ecosystem.md` ,  Directory of Israeli agritech platforms and APIs (CropX, Netafim GrowSphere, Taranis) with endpoint details, plus a company directory covering irrigation, crop monitoring, pollination, and biological sectors. Includes standard data formats (GeoJSON, GeoTIFF, CSV/JSON), agricultural zone rainfall and water source data, and FAO-56 Table 12 crop coefficients (Kc) with notes on calibrating them for Israeli conditions. Consult when selecting platforms, configuring API integrations, or looking up crop-specific irrigation parameters.

## Recommended MCP Servers

No agritech-specific MCP server is currently in the directory. For weather data feeding irrigation models, the [Israel Meteorological Service MCP (`ims-weather`)](https://agentskills.co.il/he/mcp/ims-weather) provides rain, ET0, and station data via official IMS endpoints.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Volcani Institute / Agricultural Research Organization | https://www.agri.gov.il | Israeli-context agronomy research and local calibration studies |
| Israel Ministry of Agriculture and Food Security | https://www.gov.il/en/departments/ministry_of_agriculture_and_food_security | Subsidy programs, regulations, and certifications. The ministry was renamed from "Agriculture and Rural Development"; the old departmental URL now 404s |
| Israel Water Authority | https://www.gov.il/en/departments/water_authority | Water allocation quotas, agricultural-tariff updates, and reclaimed-water rules. This is the allocating regulator, not Mekorot |
| FAO Irrigation and Drainage Paper 56, Table 12 | https://www.fao.org/4/x0490e/x0490e0b.htm | Single-crop coefficients (Kc ini / mid / end). The source of the Kc values used in this skill |
| Israel Innovation Authority | https://innovationisrael.org.il/en | Agritech grants and pilot funding programs, including the joint advanced-agriculture (agritech) pilot calls run with the Ministry of Agriculture and Food Security. Cloudflare-protected: fetches are blocked and it may prompt a CAPTCHA, so open it in a real browser |
| Start-Up Nation Central -- AgriFoodTech | https://startupnationcentral.org/AgriTech/ | Industry directory and company-stage data for the Israeli agritech ecosystem |

## Gotchas

- Salinity is a first-order constraint in Israeli irrigation and is routinely ignored. Much of the water is reclaimed effluent (קולחין) or brackish well water (מליחים), so salts accumulate in the root zone unless a leaching fraction pushes them below it. Avocado and citrus, the two crops this skill foregrounds, are among the most salt-sensitive grown here. Agents model ETc and soil moisture, request EC from the sensor API, and then never use it, producing a controller that slowly salinizes the root zone with nothing in the system noticing. Desalinated water carries the opposite problem: it is calcium, magnesium and sulphate poor and needs remineralisation for these crops.
- Israeli agricultural seasons differ from Northern European/US patterns due to the Mediterranean climate. Agents may recommend planting schedules based on temperate-zone assumptions.
- Water allocation in Israeli agriculture is set by the Water Authority (רשות המים), NOT by Mekorot. Mekorot is the national water utility that supplies the water; the allocating and regulating power sits with the Water Authority director under the water-allocation regulations. Agents routinely name Mekorot as the regulator, and they also tend to ignore quota restrictions entirely when recommending an irrigation plan.
- Agricultural water tariffs are revised annually with effect from 1 January, after a public-comment round run by the Water Authority. The current structure keys a consumer's fresh-water (שפירים) tariff to a tier reflecting how much low-grade water (reclaimed, effluent, saline) is available to them, with separate coefficients for saline and effluent sources. Any tariff figure you hold is therefore dated: read the current table off the Water Authority before quoting a price, and never hardcode a shekel-per-cubic-metre rate into a cost model.
- Israeli organic certification runs under the Israeli organic law and its regulations, supervised by PPIS (the Plant Protection and Inspection Services) with accredited certifying bodies such as Agrior, IQC and Skal Israel. It is not the same standard as USDA Organic or EU Organic, and there is no scheme called "Mekori". Agents both invent a scheme name and assume USDA or EU rules apply.
- Agricultural technology subsidies from the Ministry of Agriculture and Food Security change annually. Agents may reference outdated subsidy programs or amounts.
- Shmita (the sabbatical year) affects observant agricultural operations. It runs Rosh Hashana to Rosh Hashana, NOT the Gregorian year, so it aligns with neither the water-allocation year nor the tariff year, and a system that models one boundary will get the other wrong. The next shmita year is 5789 (autumn 2028 to autumn 2029). The operative mechanisms produce different software behaviour (heter mechira, otzar beit din, detached-substrate growing), and under most rulings irrigation is limited to what keeps plants alive, which is a change to the irrigation rule set itself. Agents typically do not know the cycle exists, and when they do they anchor it to a calendar year.

## Troubleshooting

### Error: "Sensor readings seem inaccurate"
Cause: Soil sensor calibration issue or installation depth mismatch
Solution: CropX sensors need soil-specific calibration. Verify installation depth matches crop root zone. Israeli soils vary dramatically, coastal sand vs. Negev loess vs. basalt in Golan.

### Error: "Irrigation recommendation overwatering"
Cause: ET0 calculation using wrong climate zone or outdated Kc values
Solution: Verify the weather station is local (Israel's microclimates vary over short distances). Check the Kc source and growth stage: the values in this skill are FAO-56 Table 12 standards, and FAO-56 citrus Kc_mid is lower than Kc_ini, so a model that assumes mid-season is always the peak will over-irrigate citrus. Confirm the soil type matches the sensor calibration.