# Israeli Agritech Ecosystem Reference

## Key Platforms and APIs

### CropX - Soil Monitoring
- **Website:** cropx.com
- **Type:** IoT soil sensors + cloud analytics
- **API:** REST with OAuth2 (partnership-gated; canonical base URL https://api.cropx.com/v2)
- **Key Endpoints:**
  - /sites - List monitored fields
  - /devices/{id}/measurements - Soil readings
  - /sites/{id}/recommendations - Irrigation advice
- **Data:** Moisture, temperature, EC, VWC at multiple depths
- **Integration:** Works with Netafim, Jain, Valley, Lindsay controllers

### Netafim GrowSphere - Irrigation Control
- **Website:** netafim.com
- **Type:** Cloud irrigation management platform
- **API:** REST + MQTT for real-time data
- **Key Endpoints:**
  - /controllers - List controllers
  - /zones/{id}/schedules - Manage irrigation schedules
  - /controllers/{id}/flow - Water flow data
- **Features:** Fertigation, leak detection, remote valve control

### Taranis - Crop Intelligence
- **Website:** taranis.com
- **Type:** AI aerial imagery analysis
- **API:** REST (partnership-gated; canonical base URL https://api.taranis.com/v1)
- **Key Endpoints:**
  - /fields - Field management
  - /fields/{id}/detections - Pest/disease detections
  - /fields/{id}/scans - Request aerial scans
- **Capabilities:** 300+ crop threats, sub-mm resolution

## Israeli Agritech Companies Directory

### Irrigation and Water
| Company | Focus | Stage |
|---------|-------|-------|
| Netafim | Drip irrigation (inventor) | Enterprise |
| CropX | Soil monitoring + irrigation | Growth |
| Manna Irrigation | Satellite-based irrigation | Growth |
| SupPlant | AI irrigation for smallholders | Growth |

### Crop Monitoring and Protection
| Company | Focus | Stage |
|---------|-------|-------|
| Taranis | AI crop intelligence | Growth |
| AgroScout | Drone crop scouting | Growth |
| Prospera (Valmont) | Greenhouse CV monitoring | Acquired |
| Phytech | Plant-based water stress sensors | Growth |
| Tevel Aerobotics | Autonomous fruit-picking drones | Growth |
| Agropalette | Produce supply chain analytics | Early |

### Pollination and Biological
| Company | Focus | Stage |
|---------|-------|-------|
| BeeHero | IoT beehive monitoring | Growth |
| BeeWise | Robotic AI-managed beehives (Beehome) | Growth |
| Groundwork BioAg | Mycorrhizal inoculants | Growth |
| BioBee | Biological pest control | Enterprise |

## Israeli Ecosystem Context

- The Israeli agritech sector is estimated at approximately 600-750 active companies (Start-Up Nation Central agrifoodtech mapping). Treat any single number as a moving target.
- Many of the foundational technologies originated on **kibbutzim**: Netafim's drip irrigation was developed at Kibbutz Hatzerim in 1965; Volcani Institute (Agricultural Research Organization) supports much of the underlying agronomy science.
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

## Crop Coefficients (Kc) - Volcani Institute

| Crop | Initial | Mid-Season | Late |
|------|---------|-----------|------|
| Citrus | 0.65 | 0.70 | 0.65 |
| Avocado | 0.60 | 0.85 | 0.75 |
| Tomato | 0.60 | 1.15 | 0.80 |
| Pepper | 0.60 | 1.05 | 0.90 |
| Date Palm | 0.90 | 0.95 | 0.95 |
| Table Grape | 0.30 | 0.85 | 0.45 |
| Cotton | 0.35 | 1.20 | 0.60 |
| Wheat | 0.30 | 1.15 | 0.40 |
