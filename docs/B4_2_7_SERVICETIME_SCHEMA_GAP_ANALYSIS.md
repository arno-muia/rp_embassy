# B4.2.7 — ServiceTime Schema Gap Analysis

## Current Model Fields
| Field | Type | Notes |
|---|---|---|
| day | CharField(12) | DayOfWeek choices |
| time | TimeField | Single time value |
| label | CharField(128) | Service name |
| display_order | IntegerField | Sort order |

## Frontend Source of Truth Fields
| Field | Type | Required |
|---|---|---|
| name | string | yes |
| day | string | yes |
| time | string | yes |
| platform | "physical" \| "online" | yes |
| location | string | no |
| link | string | no |
| description | string | no |
| image | string | no |

## Missing Fields in CMS Model
- **platform**: indicates physical or online service
- **location**: service location/address
- **link**: external link (e.g., Google Meet)
- **description**: additional service description
- **image**: service image/thumbnail
- **time range support**: model stores single `TimeField`, homepage uses time ranges like `"6:00 AM – 8:00 AM"`

## Impact on Homepage Migration
- Admin and API cannot capture or expose `platform`, `location`, `link`, `description`, or `image`
- Time ranges cannot be represented; only single time values can be stored and returned
- Frontend must continue using fallback/homepage source-of-truth data for these missing fields until schema is extended

## Recommended Schema Additions
1. `platform` — CharField with choices `["physical", "online"]`
2. `location` — CharField(512), nullable
3. `link` — URLField(512), nullable
4. `description` — TextField, nullable
5. `image` — CharField(512), nullable or URLField
6. Consider `time_end` — TimeField, nullable, to represent time ranges

No schema changes should be implemented until approved. Frontend currently relies on the homepage JavaScript source-of-truth object for the missing fields.