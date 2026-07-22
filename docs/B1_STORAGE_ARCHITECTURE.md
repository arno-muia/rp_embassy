# B1 Storage Architecture

**Phase:** B1.5 — Final Architecture Validation
**Date:** 2026-07-20
**Status:** Approved
**Related:** `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md`

---

## Purpose

This document defines the media storage architecture for `MediaAsset` and all uploaded content. It eliminates storage ambiguity and prevents redesign during B2/B4.

---

## Requirements

| Requirement | Description |
|-------------|-------------|
| Development | Fast local iteration; no cloud dependency |
| Production | Durable, CDN-backed, cost-effective |
| Access control | Public assets served widely; draft assets restricted |
| Backups | Regular backups with retention |
| Cost | Minimize egress and storage costs for expected traffic |
| Performance | Low-latency delivery globally |

---

## Storage Locations

### Development

**Local filesystem**

- `MEDIA_ROOT = BASE_DIR / 'media'`
- `MEDIA_URL = '/media/'`
- Served by Django `static()` in development only.
- No CDN.
- No optimization pipeline.
- Acceptable for local development and testing.

### Production

Three options evaluated:

---

### Option A — AWS S3

**Pros**
- Industry standard; widely documented.
- Integrated with Django `storages`.
- Fine-grained access control (bucket policies, signed URLs).
- Versioning and lifecycle policies.

**Cons**
- Cost: storage + egress fees can grow with traffic.
- Additional AWS account/config required.
- Egress costs for neighboring countries (Africa) can be high without CloudFront.

**Cost Estimate (small site)**
- Storage: ~$0.023/GB/month
- Egress: ~$0.09/GB (first 10TB)
- Requests: ~$0.005/1000 GET

**Verdict:** Viable, but egress cost concern for African traffic without CloudFront.

---

### Option B — Cloudflare R2

**Pros**
- Zero egress fees (key differentiator).
- S3-compatible API.
- Built-in CDN via Cloudflare (if domain uses Cloudflare).
- Cost-effective for high-read public media.

**Cons**
- Newer service; smaller community/docs.
- No versioning (manual workaround).
- Requires Cloudflare account; R2 + Workers optional.

**Cost Estimate (small site)**
- Storage: ~$0.015/GB/month
- Egress: $0
- Operations: ~$0.36/million reads

**Verdict:** Recommended. Zero egress aligns with African traffic patterns; S3-compatible eases migration.

---

### Option C — Local VPS Storage

**Pros**
- No external dependency.
- Fast local access.
- Simple backup (rsync).

**Cons**
- Single point of failure.
- No CDN; latency increases with distance.
- Scaling requires manual disk management.
- Backup complexity.

**Cost Estimate**
- Additional disk: ~$10–20/month per 100GB.
- Bandwidth: subject to VPS plan limits.

**Verdict:** Not recommended for production. Acceptable only for MVP/testing.

---

## Recommendation

### Development
- **Local filesystem** (`MEDIA_ROOT`).

### Production
- **Cloudflare R2** with Django `storages` (`S3 compatible`).
  - Bucket: `rp-media`
  - Region: automatic (R2)
  - CDN: Cloudflare cache (if domain on Cloudflare)
  - Backend: Django `storages.backends.s3boto3.S3Boto3Storage` with R2 endpoint override.

### Fallback
- If R2 setup is too complex for B4, use **AWS S3 + CloudFront** as alternative.

---

## Configuration

### Django Settings (production)

```python
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = env('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'rp-media'
AWS_S3_ENDPOINT_URL = 'https://<account_id>.r2.cloudflarestorage.com'
AWS_S3_REGION_NAME = 'auto'
AWS_S3_CUSTOM_DOMAIN = 'media.rp-website.org'  # optional custom domain
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False  # public URLs
```

### Caching Headers

```
Cache-Control: public, max-age=31536000, immutable
```
for immutable assets (uploaded once, rarely changed).

For mutable assets (draft/updates):
```
Cache-Control: public, max-age=300
```

---

## Media Organization

### Directory Structure

```
/media/
  /sermons/
    /thumbnails/{uuid}-thumb.jpg
    /audio/{uuid}-audio.mp3
  /events/
    /posters/{uuid}-poster.jpg
  /leaders/
    /photos/{uuid}.jpg
  /testimonials/
    /photos/{uuid}.jpg
  /academy/
    /images/{uuid}.jpg
  /announcements/
    /images/{uuid}.jpg
  /pastor/
    /image/{uuid}.jpg
  /service-times/
    /posters/{uuid}.jpg
  /content-blocks/
    /images/{uuid}.jpg
```

### Naming Convention
- `{uuid}` = `MediaAsset.uuid`
- Suffix indicates type/use.
- No user-provided filenames (prevents injection, collisions).

---

## Upload Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Max file size | 10 MB | Prevents abuse; fits sermon thumbnails, posters, photos. |
| Allowed MIME types | image/jpeg, image/png, image/webp | Browser-compatible; WebP for size. |
| Required fields | `file`, `alt_text` | Accessibility; no empty images. |
| Max dimensions | 4096 x 4096 | Prevent massive originals; resize on upload. |
| Responsive variants | thumb (300px), large (1200px) | Performance; srcset delivery. |

---

## Access Control

| Asset State | Public Access | Admin Access |
|-------------|---------------|--------------|
| `is_public=True` | Yes (via CDN) | Yes |
| `is_public=False` | No (403) | Yes (uploader + admins) |

Draft assets (uploaded but not published) should set `is_public=False` until associated content is published.

---

## Backup & Retention

- **R2 backups**: Cloudflare retains data across multiple locations; no additional backup needed for durability.
- **Audit/archive**: Old unreferenced media should be flagged by `usage_count=0` cleanup job (B8).
- **Retention**: No automatic deletion. Admin review required for bulk deletion.

---

## Cleanup Strategy

| Trigger | Action |
|---------|--------|
| `MediaAsset.usage_count` drops to 0 | Flag for review; no automatic delete. |
| Associated content deleted | Decrement `usage_count`; if 0, flag. |
| Unused for >90 days | Admin notification; bulk delete option. |

---

## Migration Notes

- **B7 (Backfill)**: Copy static images from `apps/web/public/images/*` and `RP/website/public/*` to R2 bucket. Create `MediaAsset` records. Update Prisma/Django references to point to R2 URLs.
- **Rollback**: If R2 fails, revert to local `MEDIA_ROOT` or previous storage by changing Django storage backend. URLs may change; frontend must use `MEDIA_URL` dynamically.

---

## Security

- Signed upload URLs for admin upload (optional): prevents client-side credential exposure.
- Virus scanning: Out of scope for B2; add in B4 via ClamAV or external service.
- Hotlink protection: Use Cloudflare/R2 referrer restrictions if needed.

---

## Monitoring

- Storage usage dashboard (R2 analytics).
- Egress tracking (should be near zero with R2 + CDN).
- Upload error rate.
- Cleanup job execution logs.

---

## Decision Lock

This document locks the storage decision. Changing storage backend after B4 requires:

1. Migrating existing media blobs.
2. Updating `MediaAsset.url` records.
3. Frontend `MEDIA_URL` update.
4. Cache invalidation globally.

Resist changing storage architecture during B2/B3.