# Israeli Agritech Ecosystem Reference

## Key Platforms and APIs

### CropX - Soil Monitoring
- **Website:** cropx.com
- **Type:** IoT soil sensors + cloud analytics
- **API:** partnership-gated. CropX publishes no public developer documentation (no developer or docs subdomain resolves, and api.cropx.com returns 404 at its root). The base URL and routes below are ILLUSTRATIVE placeholders used by this skill's code sample, not a documented interface. Contact CropX for real integration docs.
- **Key Endpoints:**
  - /sites - List monitored fields
  - /devices/{id}/measurements - Soil readings
  - /sites/{id}/recommendations - Irrigation advice
- **Data:** Moisture, temperature, EC, VWC at multiple depths
- **Integration:** Works with Netafim, Jain, Valley, Lindsay controllers

### Netafim GrowSphere - Irrigation Control
- **Website:** netafim.com
- **Type:** Cloud irrigation management platform
- **API:** no documented public API. GrowSphere is an operator-facing application; growsphere.netafim.com/api/v1 serves the web app, not a documented interface. The endpoints below are ILLUSTRATIVE. Contact Netafim for partner access.
- **Key Endpoints:**
  - /controllers - List controllers
  - /zones/{id}/schedules - Manage irrigation schedules
  - /controllers/{id}/flow - Water flow data
- **Features:** Fertigation, leak detection, remote valve control

### Taranis - Crop Intelligence
- **Website:** taranis.com
- **Type:** AI aerial imagery analysis
- **API:** partnership-gated, and api.taranis.com has NO DNS record as of 2026-08-19. Taranis publishes no public API documentation. The base URL and routes below are ILLUSTRATIVE placeholders. Do not code against them; use the base URL Taranis supplies.
- **Key Endpoints:**
  - /fields - Field management
  - /fields/{id}/detections - Pest/disease detections
  - /fields/{id}/scans - Request aerial scans
- **Capabilities:** 300+ crop threats, sub-mm resolution

## Israeli Agritech Companies Directory

### Irrigation and Water
| Company | Focus | Stage |
|---------|-------|-------|
| Netafim | Drip irrigation (inventor). Orbia-controlled and reportedly up for sale | Enterprise |
| CropX | Soil monitoring + irrigation. Acquired Acclym (formerly Agritask) in 2025 | Growth |
| SupPlant | Sensor-less WhatsApp irrigation advisor, now branded "Plant" | Growth |

### Crop Monitoring and Protection
| Company | Focus | Stage |
|---------|-------|-------|
| Taranis | AI crop intelligence | Growth |
| AgroScout | Drone crop scouting (agro-scout.com) | Growth |
| Prospera | Greenhouse CV monitoring. Acquired by Valmont in 2021; the standalone brand and site are retired, so treat it as a Valmont capability rather than a vendor you can contract with | Acquired |
| Phytech | Plant-based water stress sensors. Absorbed Rivulis's Manna satellite-irrigation business in 2024 | Growth |
| Tevel Aerobotics | Autonomous fruit-picking drones | Growth |

### Pollination and Biological
| Company | Focus | Stage |
|---------|-------|-------|
| BeeHero | IoT beehive monitoring | Growth |
| BeeWise | Robotic AI-managed beehives (Beehome) | Growth |
| Groundwork BioAg | Mycorrhizal inoculants | Growth |
| BioBee | Biological pest control (biobee.com) | Enterprise |

## Israeli Ecosystem Context

- The Israeli agritech sector is estimated at approximately 600-750 active companies (Start-Up Nation Central agrifoodtech mapping). Treat any single number as a moving target.
- Many of the foundational technologies originated on **kibbutzim**: Kibbutz Hatzerim signed with Simcha Blass and founded Netafim in 1965, with dripper manufacturing from January 1966; Volcani Institute (Agricultural Research Organization) supports much of the underlying agronomy science.
- **Desalination** plays a structural role in the water mix. Plants at Sorek, Hadera, and Ashkelon (alongside Palmachim and Ashdod) feed Mekorot and free up natural reserves for agricultural use.

## Data Formats

- **Field boundaries:** GeoJSON
- **Satellite imagery:** GeoTIFF
- **Sensor time series:** CSV or JSON
- **Soil data units:** Moisture (%), Temperature (C), EC (dS/m), VWC (m3/m3)
- **Weather data:** ET0 (mm/day), Temperature (C), Humidity (%), Wind (m/s)
- **Irrigation data:** Flow (m3/h), Application (mm), Uniformity (%)

## Israeli Agricultural Zones

| Zone | Rainfall | Water Source | Key Crops |
|------|----------|-------------|-----------|
| Mediterranean Coast | 500-700 mm | Mekorot + recycled | Citrus, avocado, vegetables |
| Northern Negev | 250-400 mm | Mekorot + wells | Wheat, olives, grapes |
| Central Negev | 50-200 mm | Mekorot | Limited |
| Arava Valley | Under 50 mm | Wells + desalinated | Dates, peppers, tomatoes |
| Jordan Valley | 300-400 mm | Jordan River + wells | Dates, bananas |
| Golan Heights | 500-1000 mm | Springs + rainfall | Apples, cherries, cattle |

## Crop Coefficients (Kc) - FAO-56 Table 12

These are the FAO Irrigation and Drainage Paper 56, Table 12 standard single-crop
coefficients (https://www.fao.org/4/x0490e/x0490e0b.htm). They are NOT Volcani/ARO
values: no published Volcani Kc table carries these triples, and an earlier version
of this file misattributed them. FAO-56 assumes a sub-humid reference climate, so
calibrate locally for Israeli conditions, especially in the Arava and Jordan Valley.

Two rows are easy to get wrong. FAO-56 citrus is banded by canopy cover and its
mid-season Kc is LOWER than the initial value because of stomatal closure at peak
ET. Winter wheat has separate frozen-soil and non-frozen-soil initial values;
Israel is the non-frozen case.

| Crop | Initial | Mid-Season | Late |
|------|---------|-----------|------|
| Citrus, 70% canopy | 0.70 | 0.65 | 0.70 |
| Citrus, 50% canopy | 0.65 | 0.60 | 0.65 |
| Citrus, 20% canopy | 0.50 | 0.45 | 0.55 |
| Avocado | 0.60 | 0.85 | 0.75 |
| Tomato | 0.60 | 1.15 | 0.80 |
| Pepper | 0.60 | 1.05 | 0.90 |
| Date Palm | 0.90 | 0.95 | 0.95 |
| Table Grape | 0.30 | 0.85 | 0.45 |
| Cotton | 0.35 | 1.20 | 0.60 |

FAO-56 publishes cotton late-season as a 0.70-0.50 range and tomato late-season as 0.70-0.90; the single values above are mid-range picks, not published point values.
| Winter wheat, non-frozen soils | 0.70 | 1.15 | 0.40 |
