# B1 Permission Matrix

**Phase:** B1.5 — Final Architecture Validation
**Date:** 2026-07-20
**Status:** Approved
**Related:** `RP/docs/BACKEND_CONTENT_MANAGEMENT_DESIGN.md`

---

## Purpose

This document defines all permissions for each persona before B2 implementation. It eliminates role ambiguity and ensures no permission gaps exist.

---

## Personas

| Persona | Base Role | Description |
|---------|-----------|-------------|
| **Content Editor** | `CONTENT_EDITOR` | Creates and edits content drafts. Cannot publish without approval. |
| **Media Team** | `MEDIA_TEAM` | Uploads and manages media assets. Can edit media-related content. |
| **Pastor** | `LEADERSHIP` | Approves theological content. Can publish approved content. |
| **Church Administrator** | `ADMIN` | Manages settings, users, and operational content. Can publish. |
| **Super Admin** | `SUPER_ADMIN` | Full access. All transitions, role assignment, audit log access. |

---

## Permission Matrix

### Content Lifecycle

| Action | Content Editor | Media Team | Pastor | Church Administrator | Super Admin |
|--------|---------------|------------|--------|---------------------|-------------|
| Create Draft | YES (Sermons, Events, Testimonials, Announcements, ContentBlocks) | YES (Sermons, Events, Series, Announcements) | NO | NO | YES |
| Edit Own Draft | YES | YES | NO | NO | YES |
| Edit Any Draft | NO | NO | NO | NO | YES |
| Submit Review | YES (own drafts) | YES (own drafts) | NO | NO | YES |
| Approve (In Review → Approved) | NO | NO | YES | NO | YES |
| Reject (Approved → Draft) | NO | NO | YES | NO | YES |
| Publish (Approved → Published) | NO | NO | YES | YES | YES |
| Unpublish (Published → Approved) | NO | NO | YES | YES | YES |
| Archive (Published → Archived) | NO | NO | YES | YES | YES |
| Restore (Archived → Published) | NO | NO | YES | YES | YES |
| Delete Draft | YES (own) | YES (own) | NO | NO | YES |
| Delete Published | NO | NO | NO | NO | YES |

**Applies to:** Sermons, Events, Testimonials, Announcements, ContentBlocks (BELIEF, VALUE, FAQ)

**Exceptions:**
- Leadership, Academy Modules: No Pastor approval required (simple Draft → Published).
- GlobalSettings, HomepageSettings, ChurchProfile: Edit-only; no delete. Workflow applies.
- ServiceTime: No approval required; Church Administrator only.
- PrayerRequest: No create via admin; moderation only.

---

### Media Management

| Action | Content Editor | Media Team | Pastor | Church Administrator | Super Admin |
|--------|---------------|------------|--------|---------------------|-------------|
| Upload MediaAsset | YES | YES | NO | NO | YES |
| Edit Own MediaAsset | YES | YES | NO | NO | YES |
| Edit Any MediaAsset | NO | YES | NO | NO | YES |
| Delete MediaAsset (unused) | NO | YES | NO | YES | YES |
| Delete MediaAsset (used, usage_count>0) | NO | NO | NO | NO | YES |

**Validation:**
- `usage_count > 0` blocks deletion unless Super Admin.
- `is_public=False` assets only visible to uploader and admins.

---

### Settings Management

| Action | Content Editor | Media Team | Pastor | Church Administrator | Super Admin |
|--------|---------------|------------|--------|---------------------|-------------|
| Edit GlobalSettings | NO | NO | NO | YES | YES |
| Edit HomepageSettings (draft) | YES | NO | NO | NO | YES |
| Approve HomepageSettings | NO | NO | YES | NO | YES |
| Publish HomepageSettings | NO | NO | YES | YES | YES |
| Edit ChurchProfile (draft) | YES | NO | NO | NO | YES |
| Approve ChurchProfile | NO | NO | YES | NO | YES |
| Publish ChurchProfile | NO | NO | YES | YES | YES |

**Singleton protection:**
- All singleton edits are logged with `old_value` and `new_value`.
- Only one active version exists at a time.

---

### Administration

| Action | Content Editor | Media Team | Pastor | Church Administrator | Super Admin |
|--------|---------------|------------|--------|---------------------|-------------|
| List Users | NO | NO | NO | YES | YES |
| Invite User | NO | NO | NO | YES | YES |
| Deactivate User | NO | NO | NO | YES | YES |
| Change User Role | NO | NO | NO | NO | YES |
| View Audit Log | NO | NO | NO | NO | YES |
| Export Audit Log | NO | NO | NO | NO | YES |
| System Configuration | NO | NO | NO | NO | YES |

---

### Moderation

| Action | Content Editor | Media Team | Pastor | Church Administrator | Super Admin |
|--------|---------------|------------|--------|---------------------|-------------|
| View Prayer Requests | NO | NO | YES | NO | YES |
| Approve Prayer Request (public) | NO | NO | YES | NO | YES |
| Mark Prayer Answered | NO | NO | YES | NO | YES |
| Close Prayer Request | NO | NO | YES | NO | YES |
| View Contact Submissions | NO | NO | NO | YES | YES |
| View RSVPs | NO | NO | NO | YES | YES |
| Export Submissions | NO | NO | NO | YES | YES |

---

### Content Type Specific Rules

| Content Type | Special Permissions |
|--------------|---------------------|
| Sermons | Media Team can upload audio/video. Content Editor can edit metadata. Pastor must approve. |
| Events | Content Editor creates. Media Team uploads poster. Pastor approves. Administrator publishes. |
| Testimonials | Content Editor creates. Pastor approves. |
| Announcements | Content Editor creates draft. Administrator can publish directly (no Pastor approval required for operational content). |
| Beliefs/Values (ContentBlock) | Content Editor creates. Pastor approves. |
| FAQs (ContentBlock) | Content Editor creates. No Pastor approval required (operational). |
| ServiceTimes | Church Administrator only. No approval workflow. |
| PrayerRequests | Submissions public. Moderation by Pastor/Content Editor only. |

---

## Enforcement Mechanisms

### Django Admin
- `ModelAdmin.has_add_permission()`
- `ModelAdmin.has_change_permission()`
- `ModelAdmin.has_delete_permission()`
- `ModelAdmin.has_view_permission()`

### DRF Permissions
- Custom permission classes per role.
- `IsAuthenticated` base for all admin endpoints.
- Object-level permissions for draft edit (owner or admin).

### Signals
- `post_save` AuditLog entry for every mutating action.
- Workflow transitions logged with `old_value` (status) and `new_value` (status).

---

## Permission Combinations (Edge Cases)

| Scenario | Resolution |
|----------|------------|
| Content Editor is also Pastor | Highest role wins (Pastor). |
| Pastor creates own sermon draft | Pastor can submit own draft for approval; another Pastor must approve. |
| Administrator needs to bypass workflow | Super Admin only. Administrator cannot force-publish without approval. |
| Media Team uploads image for sermon they don't own | Allowed (media ownership separate from content ownership). |
| Content Editor edits published content | Blocked. Must unpublish first (requires Pastor/Admin). |

---

## Default Permissions

| Action | Authenticated User | Anonymous |
|--------|-------------------|-----------|
| Read public content | YES | YES |
| Read draft content | NO | NO |
| Create submission (contact/prayer/rsvp) | YES | YES |
| Access admin | NO | NO |

---

## Future Considerations

- **Multi-campus:** Add `campus` FK to User profile; permissions scope to campus.
- **Department-level:** Content Editor may only edit their assigned category.
- **Time-limited roles:** Temporary Media Team access for events (revoke after).
- **Delegation:** Pastor can delegate approval to designated elder.