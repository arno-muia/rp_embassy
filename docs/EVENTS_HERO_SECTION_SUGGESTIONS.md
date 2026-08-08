# Events Page Hero Section — Suggested Modifications for Improved Sync and User Interactions

> **Scope:** Hero section on Events list page (`/events`) and Event detail page (`/events/[id]`)  
> **Goal:** Make the hero section appear more integrated with the enhanced events page (after E1 UX enhancements) and improve user engagement.  
> **Status:** Suggestions only — no implementation.

---

## Current State

### Events List Page (`/events.astro`)
```astro
<PageHero
  title="Events"
  subtitle="Join us for worship nights, outreach, fellowship, and Kingdom gatherings in Thika and beyond."
  register="warm"
/>
```

### Event Detail Page (`[id].astro`)
```astro
<PageHero
  title={event.title}
  subtitle={`${formatEventDate(event.date)} · ${displayTime} · ${event.location}`}
  register="warm"
/>
```

The hero section uses the existing `register="warm"` theme (dark obsidian gradient with ivory text) and provides basic contextual information.

---

## Suggested Modifications

### 1. **Dynamic Upcoming Event Highlight (List Page)**
**Suggestion:**  
Replace the static subtitle with a dynamic component that showcases the next upcoming event (or a rotating highlight of 2–3 events). Include:
- Event title (truncated if long)
- Date (using the same calendar chip format as event cards: month abbreviation + day)
- Category badge (e.g., "Worship Service", "Outreach")
- Optional: "Register Now" CTA button

**Example Subtitle Content:**  
> Next Up: **Kingdom Fellowship** • SEP 12 • [Worship Service badge]  
> [Button] Register Now

**Reasoning:**  
- Increases relevance: visitors immediately see what’s happening soon, reducing bounce rate.  
- Drives action: a prominent CTA in the hero section encourages immediate engagement.  
- Visual sync: mirrors the calendar chip and category badge design introduced in E1, creating consistency between hero and cards.  
- Improves scanability: users can grasp the timing and type of the next event at a glance.

### 2. **Add Category Badge to Detail Page Hero**
**Suggestion:**  
In the event detail hero, insert a small category badge (using the same `EVENT_CATEGORY_LABELS` and styling as on the event cards) next to the title or in the subtitle line.

**Example:**  
> `title={event.title}` with a badge: `<span class="badge">{event.categoryLabel}</span>`  
> Subtitle remains: `{date} · {time} · {location}`

**Reasoning:**  
- Reinforces event type context immediately upon landing on the detail page (important for users arriving via direct links or search).  
- Visual consistency: uses the same badge design as event cards, tying the hero to the card grid.  
- Low implementation effort: reuses existing logic and styles.

### 3. **Registration Status Indicator in Detail Page Hero**
**Suggestion:**  
Add a subtle visual indicator (e.g., a small icon or text treatment) in the hero section to signal whether registration is required, similar to the CTA logic but less prominent.

**Examples:**  
- If `registrationRequired`: show a lock icon 🔒 or text "Registration Required" in muted gold.  
- If not required: show an open door icon 🚪 or "Open to All" in ivory.  
- Alternatively, vary the CTA button style directly in the hero (though the current hero doesn’t have a button).

**Reasoning:**  
- Sets expectations early: users know before scrolling whether they need to register.  
- Complements the E1 registration-aware CTA further down the page, creating a cohesive experience.  
- Uses minimal space and aligns with the existing icon system (calendar, clock, map-pin).

### 4. **Unified Visual Language: Calendar Chip and Icons in Hero**
**Suggestion:**  
Apply the same calendar chip design (month abbreviation overlay + day number) used on event cards to the date display in both hero sections. Additionally, use the same icon set (calendar, clock, map-pin) for the date/time/location triplet in the detail page hero.

**Example for Detail Page Hero Subtitle:**  
> [Calendar chip: SEP 12] · [Clock icon] 7:00 PM – 9:00 PM · [Map pin icon] Thika, Kenya

**For List Page Dynamic Highlight:**  
> Use the calendar chip for the highlighted event’s date.

**Reasoning:**  
- Creates a strong visual language: the calendar chip becomes a recognizable event-date signature across the site.  
- Improves readability: icons help users quickly identify what each piece of information represents.  
- Ensures consistency: the hero now uses the same date/time/location treatment as the event cards.

### 5. **Engaging Background or Imagery (List Page)**
**Suggestion:**  
Enhance the `register="warm"` background on the list page hero with a subtle, semi-transparent overlay of a collage of past event photos (or a single evocative image) at low opacity (e.g., 10–15%). Ensure text remains legible via a dark overlay or text shadow.

**Reasoning:**  
- Adds warmth and community feel: shows real events and faces, reinforcing the sense of an active community.  
- Breaks the monotony of a flat gradient while keeping the design clean and performance-friendly (small, optimized image).  
- Aligns with the "Kingdom gatherings" messaging by visualizing the community in action.

### 6. **Clearer Call-to-Action (CTA) Hierarchy**
**Suggestion:**  
On the list page hero, add a primary CTA button (e.g., "View Upcoming Events" or "Find an Event") that links to the events list (or anchors to the upcoming section if the hero is above the fold). On the detail page, ensure the hero visually complements (but doesn’t duplicate) the primary CTA lower in the section.

**Reasoning:**  
- Provides a direct path for users ready to act, reducing friction.  
- Balances engagement: the hero inspires, the lower CTA converts.  
- Uses the existing `Button` component variants (e.g., `variant="primary"` or `variant="gold"`).

### 7. **Accessibility and Readability Enhancements**
**Suggestion:**  
Ensure all added elements (badges, chips, icons, buttons) meet WCAG contrast ratios in both light and dark modes. Use semantic HTML where possible (e.g., `<time>` for dates, `<nav>` for hero actions if expanded). Provide meaningful `aria-label`s for icon-only elements.

**Reasoning:**  
- Guarantees inclusivity: users with visual impairments can perceive and interact with the hero section.  
- Maintains the site’s commitment to accessibility, which is already a consideration in E1 (contrast fixes, icon labeling).  
- Future-proofs the design for audits and evolving standards.

### 8. **Dynamic Subtitle Based on Time of Year or Theme**
**Suggestion:**  
Optionally, rotate the list page hero subtitle based on liturgical seasons, monthly themes, or current sermon series (e.g., "December: Celebrating the Birth of Christ" or "Current Series: Kingdom Living").

**Reasoning:**  
- Keeps the hero section fresh and relevant to ongoing church activities.  
- Encourages repeat visits: users notice changes and feel informed about the church’s current focus.  
- Can be implemented via a simple contentful or CMS-driven string if desired, but even a static rotation schedule adds value.

---

## Prioritization (Low Effort, High Impact)

| Suggestion | Effort | Impact | Notes |
|------------|--------|--------|-------|
| 2. Category badge on detail hero | Low | High | Reuses existing data and styles; immediate visual sync. |
| 3. Registration indicator in detail hero | Low | Medium | Enhances clarity; low risk. |
| 4. Calendar chip and icons in hero | Low | High | Creates strong visual language; matches E1 cards. |
| 1. Dynamic upcoming event highlight | Medium | High | Requires fetching/sorting events; high engagement payoff. |
| 5. Background imagery | Low | Medium | Enhances emotion; ensure performance optimization. |
| 6. Clearer CTA hierarchy | Low | Medium | Improves conversion paths; uses existing button styles. |
| 7. Accessibility enhancements | Low | High (essential) | Should be applied to all suggestions. |
| 8. Dynamic thematic subtitle | Low | Low-Medium | Nice-to-have; depends on content availability. |

---

## Implementation Notes (For Future Reference)
- All suggestions can be implemented using existing data fields (`event.title`, `event.date`, `event.time`, `event.location`, `event.type`, `event.registrationRequired`) and the existing design system (badge styles, calendar chip CSS, icon set, `Button` component).
- No changes to the `PageHero` component API are required if we pass enhanced `subtitle` (as HTML string or Astro fragment) or if we modify the `PageHero` to accept additional props (e.g., `event`, `showCta`, `showCategoryBadge`). However, to minimize risk, we can achieve most goals by enhancing the `subtitle` prop passed to `PageHero`.
- Ensure any added interactive elements (buttons) have clear focus states and hit areas.
- Test in both light and dark modes to confirm contrast and aesthetics.

---

## Conclusion
These suggestions aim to make the events page hero section feel like a natural extension of the enhanced event cards and detail page (post-E1), while increasing user engagement through clearer calls to action, dynamic relevance, and consistent visual language. They preserve the existing theme system and component structure, focusing on enrichment rather than redesign.