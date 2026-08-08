# Events Page — UI/UX Suggested Modifications for Improved Human Interactions

> **Role:** UI/UX Design Audit — Royal Priesthood Website  
> **Scope:** Events list page (`/events`) & Event detail page (`/events/[id]`)  
> **Modes audited:** Light mode & Dark mode  
> **Status:** Recommendations only — no implementation

---

## 1. Events List Page (`/events`)

### 1.1 — Add visual event-type badges (category tags)

**Current state:**  
The `EventView` interface includes a `category` field (`"service" | "special" | "outreach" | "training"`), but it is never surfaced on the EventCard. Users see only the title, date, and location — no immediate hint about the nature of the event.

**Suggested modification:**  
Render a small badge on each card (e.g., above the date or overlaid on the image corner) that labels the category — `Worship Night`, `Outreach`, `Training`, etc.

**Reasoning:**  
- Reduces cognitive load: visitors can scan categories at a glance instead of reading every title.
- Helps prioritisation: someone looking specifically for outreach events can filter visually.
- Aids accessibility: screen readers can announce the category early in the card.
- Works equally in light/dark mode with the existing `glass-*` badge patterns.

---

### 1.2 — Add a month/day separator or calendar-chip on the image

**Current state:**  
The date is shown only as plain text below the image (`<p class="text-sm text-muted-foreground">`). On a grid of cards, dates blend visually into the text stack.

**Suggested modification:**  
Overlay a styled "calendar chip" at the top-right (or bottom-left) corner of the image showing the month abbreviation and day number in large type, similar to common event-card patterns.

**Reasoning:**  
- Visual hierarchy: dates become scannable without reading full text.
- Emotional cue: a prominent calendar chip signals "this is an event" even before reading.
- Works in dark mode: the chip can use `glass-dark` or solid gold background with high-contrast text.
- Improves glanceability on mobile where the grid collapses to single column.

---

### 1.3 — Show location icon + time alongside the date

**Current state:**  
Only the date is shown in the metadata line; time is omitted from the card (it only appears on the detail page). Location is shown but as plain text without an icon.

**Suggested modification:**  
Concatenate `time` into the metadata line and add a small map-pin icon before the location text.

**Reasoning:**  
- Reduces friction: users can tell at a glance whether an event conflicts with their schedule without clicking through.
- Consistency: the detail page hero already shows `date · time · location` — the card should preview the same trio.
- Icon recognition: a map-pin icon is universally understood and aids visual scanning.
- Accessibility: screen readers can announce time + location alongside date.

---

### 1.4 — Empty state for "No upcoming events" should be more inviting

**Current state:**  
When `upcoming.length === 0`, a plain `<p>` tag reads: _"No upcoming events at this time."_ — no icon, no CTA, no visual weight.

**Suggested modification:**  
Replace with a centred "empty state" block containing:
- A subdued icon (e.g., calendar outline)
- The message in slightly larger / softer text
- A secondary CTA: "Check back soon or browse our past events below."

**Reasoning:**  
- Emotional design: a sparse empty state feels abandoned. An illustrated or icon-supported message feels intentional.
- Guides behaviour: the secondary link encourages users to scroll to past events rather than bounce.
- Light/dark: use `text-muted-foreground` for the icon/message — already themed.

---

### 1.5 — "Ongoing" badge should also show on the event detail hero

**Current state:**  
On the list page, an "Ongoing" badge is rendered on the EventCard image. On the detail page (`[id].astro`), no status badge is shown in the hero or anywhere on the page.

**Suggested modification:**  
Add the same `bg-fire-500` "Ongoing" pill to the detail page hero, positioned similarly (top-left or top-right of the featured image).

**Reasoning:**  
- Consistency: users who land directly on a detail page (e.g., from a shared link) should see the same status signal.
- Urgency: "Ongoing" implies active registration — useful for time-sensitive decision-making.
- Visual continuity: reinforces the mental model that the card and detail page represent the same object.

---

### 1.6 — Add a subtle "past events" collapse / toggle

**Current state:**  
Past events are rendered in full below upcoming ones, with no way to hide them. If there are many past events, the page becomes very long.

**Suggested modification:**  
Add a "Show past events" toggle button with a chevron icon that collapses/expands the past events section. The section could default to collapsed on mobile, expanded on desktop.

**Reasoning:**  
- Information prioritisation: upcoming events are primary — past events are secondary reference.
- Scroll ergonomics: reduces vertical scroll length, especially on mobile.
- Pattern familiarity: expand/collapse sections are widely understood.
- Light/dark: reuse the existing `btn-primary-gold` or `glass-*` styling for the toggle.

---

## 2. Event Detail Page (`/events/[id]`)

### 2.1 — Add breadcrumb navigation

**Current state:**  
There is no breadcrumb. Users land on the detail page with no visible link back to `/events` except the browser's back button or the site nav.

**Suggested modification:**  
Insert a breadcrumb row above the hero (or inside the hero) such as:
`Home → Events → [Event Title]`

**Reasoning:**  
- Wayfinding: breadcrumbs provide a clear path back to the list, reducing disorientation.
- SEO: breadcrumb structured data can improve search result snippets.
- Accessibility: screen reader users can quickly understand their location in the site hierarchy.
- Works in both themes: use `text-muted-foreground` with gold accent for the current page.

---

### 2.2 — Richer glass-frost info card layout

**Current state:**  
The glass-frost card at the bottom of the detail page stacks Date, Time, and Location in a 2-column grid with plain key-value labels. It feels functional but flat.

**Suggested modification:**  
Add small line icons (calendar, clock, map-pin) next to each label, and increase the font-weight of the values. Consider a subtle background tint (e.g., `glass-gold` for upcoming, `glass-ember` for ongoing) to visually differentiate the event's status.

**Reasoning:**  
- Visual polish: icons break up text monotony and add personality.
- Status cue: the card's tint reinforces the event's timeline state without extra badges.
- Scannability: bold values + icons create clear visual zones for each data point.
- Dark mode: glass variants already have dark-appropriate opacity and border colours.

---

### 2.3 — Add "Share" button or social links

**Current state:**  
There is no mechanism to share an event URL. Users must manually copy the browser address.

**Suggested modification:**  
Add a small "Share" button (inline with the CTA or in the info card footer) that opens the native Web Share API, falling back to a "Link copied" toast.

**Reasoning:**  
- Viral loop: makes it trivially easy for attendees to share events with friends.
- Mobile-first: the Web Share API is well-supported on mobile and feels native.
- Low friction: no external social widgets, no tracking — just a simple share action.
- Light/dark: reuse the existing `Button` component with a secondary/ghost variant.

---

### 2.4 — Registration CTA should be more prominent when applicable

**Current state:**  
The `EventView` interface has `registrationRequired` and `registrationUrl` fields, but the detail page always shows the same "Plan Your Visit" button — it doesn't differentiate between events that require registration and those that don't.

**Suggested modification:**  
- If `registrationRequired === true`: show a gold "Register Now →" button (primary) with an inline note: "Space is limited."
- If `registrationRequired === false`: keep "Plan Your Visit" as a secondary/ghost button.
- If the event is past: hide the CTA entirely and show "This event has ended" in subdued text.

**Reasoning:**  
- Decision clarity: users immediately know whether they need to act or can just show up.
- Urgency framing: "Register Now" + "Space is limited" creates appropriate FOMO for registered events.
- Context-appropriate: hiding CTAs on past events prevents confusion and broken links.

---

### 2.5 — Add event end time / duration

**Current state:**  
The `Event` backend model has `start_date_time` and `end_date_time`, but the detail page only displays a single `time` field. Users cannot tell how long the event lasts.

**Suggested modification:**  
Display time as a range: `7:00 PM – 9:00 PM` (or `start – end`), rather than a single time string.

**Reasoning:**  
- Practical planning: knowing the duration helps users decide if they can attend given their schedule.
- Transparency: single-time events may leave users wondering "when does it end?"
- Light/dark: no visual changes needed — just a string format update.

---

### 2.6 — Add "Related / Upcoming Events" sidebar or bottom section

**Current state:**  
After reading an event detail, users reach the bottom of the page with no next step except "Plan Your Visit" or navigating away.

**Suggested modification:**  
Add a "More Events" section at the bottom showing 2–3 upcoming events (Excluding the current one). Use the same `EventCard` or a compact horizontal card variant.

**Reasoning:**  
- Engagement loop: keeps users browsing rather than leaving the site.
- Discovery: surfaces events the user might not have seen on the list page.
- Cross-sell: if they liked this event, they may like similar ones.
- Light/dark: reuse existing card component — zero new theme work.

---

### 2.7 — Image caption or alt text improvements

**Current state:**  
The event image on the detail page uses `alt={event.title}`. The card image does the same.

**Suggested modification:**  
Append event type or "Event banner" context to the alt text, e.g.: `"${event.title} — ${event.category} event banner"`.

**Reasoning:**  
- Accessibility: more descriptive alt text helps screen reader users understand the image's role.
- SEO: richer alt attributes can improve image search relevance.
- No visual impact: purely an HTML attribute change.

---

## 3. Global / Cross-Page Usability

### 3.1 — Add a subtle hover state to the "Ongoing" badge

**Current state:**  
The "Ongoing" badge (`bg-fire-500`) is purely static. It does not respond to hover.

**Suggested modification:**  
Add a `hover:brightness-110` or `hover:scale-105` transition to the badge so it subtly responds.

**Reasoning:**  
- Micro-interaction delight: small motion feedback makes the page feel alive.
- Consistency with the card's existing `group-hover:scale-105` on images.
- No cost to dark mode — brightness works uniformly.

---

### 3.2 — Ensure all text meets WCAG contrast ratios in dark mode

**Current state (audit finding):**  
Dark mode uses `--rp-text-secondary: #d9c9a8` (light gold/tan) on `--rp-bg-primary: #271f14` (dark brown). The contrast ratio of `#d9c9a8` on `#271f14` is approximately 4.3:1 — which passes AA for normal text but may be borderline for smaller text like the date/location lines on EventCard.

**Suggested modification:**  
Lighten `--rp-text-secondary` in dark mode to `#e8dcc8` or similar, achieving ~5.5:1 contrast. Alternatively, keep the current value but ensure metadata text is always `text-sm` weighted with `font-medium` for readability.

**Reasoning:**  
- Accessibility compliance: WCAG AA requires 4.5:1 for small text. Borderline values risk failing audits.
- Readability: users in dark environments (night mode) benefit from slightly brighter secondary text.
- Brand alignment: the ivory family (`--color-ivory-25` through `400`) can be used to pick a safer value.

---

### 3.3 — Add a "Loading" or "Skeleton" state for events

**Current state:**  
`getEvents()` is awaited at the top of the page with no fallback UI. If the API is slow or fails, the page blocks entirely or shows nothing.

**Suggested modification:**  
Wrap the events fetch in a try/catch and render skeleton cards (using the existing `.skeleton` CSS class) while loading, or gracefully degrade to a "Could not load events" message with a retry prompt.

**Reasoning:**  
- Perceived performance: skeleton screens feel faster than blank/loading spinners.
- Error resilience: users see a friendly message instead of a broken page.
- Light/dark: `.skeleton` already uses themed background tokens — no extra work.

---

## 4. Implementation Priority Matrix

| Priority | Section | Modification | Effort | Impact |
|----------|---------|-------------|--------|--------|
| P0 | Card | 1.2 — Calendar chip on image | Medium | High |
| P0 | Detail | 2.4 — Smart CTA based on registration | Low | High |
| P0 | Detail | 2.5 — Show end time / duration | Low | High |
| P1 | Card | 1.1 — Event-type badges | Low | Medium |
| P1 | Card | 1.3 — Location icon + time | Low | Medium |
| P1 | Detail | 2.1 — Breadcrumb | Low | Medium |
| P1 | Global | 3.2 — Dark mode contrast fix | Low | Medium |
| P2 | List | 1.4 — Inviting empty state | Low | Low |
| P2 | List | 1.6 — Past events toggle | Medium | Medium |
| P2 | Detail | 2.2 — Richer info card | Medium | Medium |
| P2 | Detail | 2.6 — Related events | Medium | Medium |
| P3 | Card | 1.5 — Ongoing badge on detail | Low | Low |
| P3 | Detail | 2.3 — Share button | Low | Low |
| P3 | Detail | 2.7 — Alt text improvement | Low | Low |
| P3 | Card | 3.1 — Badge hover state | Low | Low |
| P3 | Global | 3.3 — Skeleton loading | Medium | Low |

---

## 5. Summary

The events page has a solid structural foundation — clear sections, responsive grid, and a well-defined theme system. The suggestions above focus on:

1. **Scanability** (badges, calendar chips, icons) — helping users find relevant events faster.
2. **Decision support** (time ranges, registration state, duration) — giving users what they need to commit to attending.
3. **Wayfinding** (breadcrumbs, past events toggle, related events) — keeping users engaged and oriented.
4. **Accessibility & resilience** (contrast, alt text, skeleton states) — ensuring the page works for everyone, everywhere.

None of these modifications require a redesign of the theme system; they all layer onto existing CSS custom properties and component patterns.