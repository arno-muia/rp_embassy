# B4.2.8A — ServiceTime Content Audit

**Date:** 2025-07-24  
**Model:** `backend.apps.content.models.ServiceTime`  
**Audit Type:** READ-ONLY — No records created, modified, or deleted.

---

## 1. Record Count

| Metric | Value |
|--------|-------|
| Total ServiceTime records | **10** |
| Populated with meaningful content | **5** |
| Placeholder / default-only records | **5** |

---

## 2. Full Record Inventory (ordered by `display_order`)

| ID | name | day | time | platform | location | link | description | image | display_order | is_published |
|----|------|-----|------|----------|----------|------|-------------|-------|---------------|--------------|
| 6 | Service | SUNDAY | 06:00:00 | physical | null | null | null | null | 1 | true |
| 11 | Sunday Online Service | SUNDAY | 6:00 AM - 8:00 AM | online | Google Meet | https://www.youtube.com/@RoyalPriesthoodEmbassy | Early morning worship... | /images/events/sunday-online-service-poster-1.jpeg | 1 | true |
| 7 | Service | SATURDAY | 09:00:00 | physical | null | null | null | null | 2 | true |
| 12 | Saturday Physical Service | SATURDAY | 9:00 AM - 12:00 PM | physical | Voice of Grace, Behind Spoonzoom, Thika | null | Our primary worship gathering... | /images/services/kingdom-formation-2.jpg | 2 | true |
| 8 | Service | TUESDAY | 20:30:00 | physical | null | null | null | null | 3 | true |
| 13 | Kingdom Formation | TUESDAY | 8:30 PM | online | Google Meet | https://www.youtube.com/@RoyalPriesthoodEmbassy | Blueprint Tuesdays... | /images/events/kingdom-formation-poster.jpeg | 3 | true |
| 9 | Service | THURSDAY | 00:00:00 | physical | null | null | null | null | 4 | true |
| 14 | Thursday Partner's Meeting | THURSDAY | TBD | online | Voice of Grace, Behind Spoonzoom, Thika | null | Corporate prayer and intercession... | /images/services/kingdom-formation-3.jpg | 4 | true |
| 15 | Cell Group Meetings | WEDNESDAY | TBD | physical | Thika, Juja, Bypass, Kahawa Sukari, Kasarani, Kitengela | null |  | /images/services/kingdom-formation-3.jpg | 5 | true |
| 10 | Service | WEDNESDAY | 00:00:00 | physical | null | null | null | null | 5 | true |

---

## 3. Field-Level Population Analysis

### 3.1 Populated Fields

| Field | Count | Notes |
|-------|-------|-------|
| `id` | 10 | All records have IDs (integer PKs) |
| `name` | 10 | 5 are meaningful; 5 are generic placeholder `"Service"` |
| `day` | 10 | All days populated (SUNDAY through WEDNESDAY) |
| `time` | 10 | 5 with display strings; 5 with strict time format or `00:00:00` |
| `platform` | 10 | All set (`physical` or `online`) |
| `display_order` | 10 | All set (1–5) |
| `is_published` | 10 | All set to `true` |
| `location` | 5 | Populated only for records 11, 12, 13, 14, 15 |
| `link` | 3 | Populated for records 11, 13, 14 |
| `description` | 5 | Populated for records 11, 12, 13, 14; record 15 has empty string |
| `image` | 5 | Populated for records 11, 12, 13, 14, 15 |

### 3.2 Empty / Null Fields

| Field | Null Count | Empty String Count | Total Missing |
|-------|------------|-------------------|---------------|
| `location` | 5 | 0 | 5 |
| `link` | 7 | 0 | 7 |
| `description` | 5 | 1 | 6 |
| `image` | 5 | 0 | 5 |

### 3.3 Placeholder Values Detected

| Record ID | Field | Placeholder Value | Recommended Action |
|-----------|-------|-------------------|-------------------|
| 6, 7, 8, 9, 10 | `name` | `"Service"` | Replace with descriptive service names |
| 6, 7, 8 | `time` | `"06:00:00"`, `"09:00:00"`, `"20:30:00"` | Convert to display strings (e.g. `"6:00 AM"`, `"9:00 AM"`, `"8:30 PM"`) |
| 9, 10 | `time` | `"00:00:00"` | Replace with actual times or `"TBD"` |
| 6, 7, 8, 9, 10 | `location` | `null` | Populate physical locations or mark as online |
| 6, 7, 8, 9, 10 | `description` | `null` | Add descriptive text |
| 6, 7, 8, 9, 10 | `image` | `null` | Add image paths/URLs |
| 15 | `description` | `""` (empty string) | Add descriptive text |

---

## 4. Missing Fields Per Record

| ID | Missing Fields |
|----|----------------|
| 6 | location, link, description, image |
| 7 | location, link, description, image |
| 8 | location, link, description, image |
| 9 | location, link, description, image |
| 10 | location, link, description, image |
| 11 | *(none)* |
| 12 | link |
| 13 | *(none)* |
| 14 | link |
| 15 | link, description (empty) |

---

## 5. Recommendation

**PARTIAL POPULATION REQUIRED**

- **5 of 10 records** are placeholder stubs with generic names and missing content.
- **4 of 5 meaningful records** are missing `link`.
- **1 meaningful record** (ID 15) has an empty `description`.
- No records have `is_published = false`; all are live.

**Next Steps (Phase B4.2.8B):**
1. Replace placeholder `name` and `time` values for records 6–10.
2. Populate `location`, `description`, and `image` for records 6–10.
3. Add `link` values for records 12, 14, and 15 where applicable.
4. Fill empty `description` for record 15.

---

*Audit completed. No data modifications were made.*