# B4.3H — Homepage Admin Grouping Strategy

## Objective
Create a clean, logically grouped admin interface for managing homepage content, enabling administrators to easily locate and edit all homepage-related settings without navigating across multiple unrelated sections.

## Current State
Presently, homepage-related admin models are scattered across the Django admin interface:
- `HomepageSettings` → "Content" section
- `SystemConfig` (heroImage) → "System Configuration" 
- `ServiceTime` → "Content" section
- `HomepageSection` → "Content" section
- `PastorProfile` → "Content" section  
- `WebsiteTestimonial` → "Content" section

This scattering makes it difficult for administrators to find all homepage-related controls in one place.

## Proposed Grouping Strategy

### Option 1: Custom Admin Site Grouping
Create a specialized admin site that overrides the default grouping mechanism to cluster homepage-related models under a dedicated "Homepage" section.

**Implementation Steps:**
1. Subclass `AdminSite` to create `HomepageAdminSite`
2. Register homepage-related models with this custom site
3. Override `index_template` to present a unified homepage admin dashboard
4. Optionally add a custom dashboard view showing shortcuts to each section

```python
# In rpwebsite/RP/backend/backend/apps/content/admin.py
from django.contrib.admin import AdminSite
from .models import HomepageSettings, SystemConfig, ServiceTime, HomepageSection, 
                            ChurchProfile, PastorProfile, ContentBlock, HomepageSection

class HomepageAdminSite(AdminSite):
    site_title = "Homepage Administration"
    site_header = "Homepage Content Management"
    
    def each_context(self):
        context = super().each_context()
        context['app_labels'] = OrderedDict([
            'Homepage Settings': ['homepagesettings.HomepageSettings', 'homepagesettings.HomepageSettingsAdmin'],
            'Hero Content': ['homepagesettings.HomepageSettings', 'homepagesettings.HomepageSettingsAdmin'],
            'Service Times': ['content.ServiceTime', 'content.ServiceTimeAdmin'],
            'Events & Testimonials': ['content.PublicSermon', 'content.WebsiteTestimonial', 'content.WebsiteLeader'],
            'Pastor & CTA': ['content.PastorProfile', 'content.PastorProfileAdmin'],
            'Section Headings': ['content.HomepageSection', 'content.HomepageSectionAdmin'],
        ])
        return context
```

### Option 2: Verbose Name Customization
Modify `verbose_name` and `verbose_name_plural` for each model to reflect their functional grouping:
- `HomepageSettings` → "Homepage Settings"
- `SystemConfig` (hero image) → "Hero Configuration" 
- `ServiceTime` → "Service Times"
- `HomepageSection` → "Section Layout"
- etc.

### Recommended Approach
Given that models belong to different apps, **Option 1** (custom AdminSite) provides the cleanest separation while preserving existing model definitions. This approach:
- Maintains all existing model registrations
- Provides a dedicated URL for homepage admin (`/admin/homepage/`)
- Allows creation of a custom dashboard view for administrators
- Requires minimal changes to existing code

## Implementation Plan

1. **Create Custom Admin Site** (`HomepageAdminSite`)
2. **Register Homepage Models** with appropriate field organization
3. **Customize Fieldsets** for better readability
4. **Add Dashboard View** for quick navigation
5. **Update URL Configuration** to expose the new admin section

### Sample Registration Pattern
```python
# In rpwebsite/RP/backend/backend/apps/content/admin.py
from django.contrib import admin
from .models import HomepageSettings, SystemConfig, ServiceTime, 
                HomepageSection, ChurchProfile, PastorProfile, ContentBlock
from django.contrib.admin import csrf_exempt

# Register with custom labels
admin.site.register(HomepageSettings, HomepageSettingsAdmin)
admin.site.register(SystemConfig, SystemConfigAdmin)  # For hero image config
admin.site.register(ServiceTime, ServiceTimeAdmin)
admin.site.register(HomepageSection, HomepageSectionAdmin)
admin.site.register(ChurchProfile, ChurchProfileAdmin)
admin.site.register(PastorProfile, PastorProfileAdmin)
admin.site.register(ContentBlock, ContentBlockAdmin)
```

## Expected Outcome
- All homepage content management tools consolidated under a single "Homepage" section in Django admin
- Clear visual categorization of related settings
- Improved administrator experience with reduced navigation overhead
- Complete preservation of existing functionality and dataintegrity

## Next Steps
Proceed with implementation of custom admin site and dashboard in Phase 4.