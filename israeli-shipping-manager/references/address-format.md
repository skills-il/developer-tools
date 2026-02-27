# Israeli Address Format Specification

## Standard Address Format

A complete Israeli shipping address contains the following fields, in order:

| Field | Hebrew | Required | Format | Example |
|-------|--------|----------|--------|---------|
| Street | רחוב | Yes | Hebrew text | הרצל |
| House number | מספר בית | Yes | Integer | 42 |
| Entrance | כניסה | No | Letter or number | א / 2 |
| Floor | קומה | No | Integer | 3 |
| Apartment | דירה | No | Integer | 7 |
| City | עיר | Yes | Hebrew text | תל אביב-יפו |
| Mikud (ZIP) | מיקוד | Yes | 7 digits | 6120001 |

### Formatted Output
```
רחוב הרצל 42, כניסה א, קומה 3, דירה 7
תל אביב-יפו, 6120001
```

## Mikud (ZIP Code) Validation

- Must be exactly **7 digits** (no letters, no hyphens)
- Old 5-digit codes are no longer valid — all were converted to 7 digits
- First 2 digits indicate general region:
  - 10-19: Jerusalem area
  - 20-29: Northern area (Haifa, Galilee)
  - 30-39: Haifa area
  - 40-49: Sharon area
  - 50-59: Central area
  - 60-69: Tel Aviv area
  - 70-79: Southern area
  - 80-89: Negev / Eilat
- Verify at: https://www.israelpost.co.il/mikud

## Special Address Formats

### Kibbutz / Moshav
No street names. Use settlement name and house number:
```
קיבוץ דגניה א, בית 15
מיקוד 1512000
```

### Military Address (APO)
IDF mail uses a military postal number (מספר דואר צבאי):
```
צה"ל דואר צבאי 01234
```
- Only Israel Post handles military mail
- No mikud required for military addresses

### Industrial Zone
Use zone name and building/company name:
```
אזור תעשייה הר טוב, בניין 8
בית שמש, 9906000
```

### PO Box (תא דואר)
```
ת.ד. 1234
ירושלים, 9100001
```

### Arab Localities
- Use the official Hebrew spelling as registered with Israel Post
- Some localities have both Arabic and Hebrew names — use Hebrew for carrier APIs
- Verify exact spelling in the carrier's city list to avoid rejection

## Hebrew Text Normalization for Carrier APIs

- **Encoding:** Always UTF-8
- **Final letters:** Carriers accept both forms (e.g., ם/מ) but prefer standard text
- **Geresh and gershayim:** Keep quotation marks in abbreviations (e.g., ת"א for Tel Aviv)
- **Hyphens in city names:** Keep them (e.g., תל אביב-יפו, ראשון לציון)
- **Niqqud (vowel marks):** Remove all diacritics before sending to carrier APIs

## Common Address Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| 5-digit mikud | Outdated format | Look up 7-digit equivalent at Israel Post |
| Missing entrance | Courier cannot find apartment | Add entrance letter/number |
| English street name | Most carriers require Hebrew | Transliterate to Hebrew |
| City abbreviation (ת"א) | May not match carrier database | Use full name: תל אביב-יפו |
| Missing apartment number | Courier leaves at building entrance | Add apartment and floor |
| Wrong mikud for city | Delivery routed to wrong area | Verify mikud matches city at Israel Post site |
