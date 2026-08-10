# Project Guidelines

## S&T Showcase Interactive Web App

**Vision + Developer Discussion Guide**

A simple, mobile-first digital companion that helps attendees answer three questions quickly: What is happening? What do I want to see?

> **North Star:** An attendee should be able to pull out their phone, find what they need in seconds, know exactly where to go

### 1. Overall Experience

- Mobile-first web app - no complicated navigation or unnecessary features.
- Fast and visual - designed to be used before attendees get to the event and while walking around the event.
- One reliable source for the agenda, locations.
- Simple navigation: Home | Map | Agenda | Info | Explore
    - Home is simple event information (title/date)
    - Map includes south campus and must be very clean
    - Agenda is arranged as a vertical timeline
    - Info has things like speaker bios, faq, parking map
    - Explore has list of neighborhoods (poster domains), then drill down to > poster titles > author and info
- Buttons at the bottom for navigation

### 2. The Interactive Map - The Main Feature

The map should be the centerpiece of the experience, not just a static floor plan.

- Interactive locations
    - Map elements required:
        - Neighborhoods
        - Posters
        - Demos
        - Food/Drink
        - Restrooms
        - Rooms
        - Help locations (attendees will be available to answer questions and help navigate)
- Tap a location to see title/description/relevant times (Navigate to explore page from here)
- Every agenda item or showcase listing should include a clear “Show on Map” action.
- Allow useful filters so attendees can quickly simplify the map.

> **Priority feature: Search -> Map Highlight**
>
> An attendee searches for a demo, topic, session, room, or destination. The matching location should immediately light up/highlight on the map, and the other locations should visually fade back.

### 3. What Should Be on the Site

| Section | Purpose |
|---|---|
| Home | Happening Now, Up Next, quick access to Map and Agenda. |
| Map | Interactive venue map, searchable destinations, filters, highlighted search result. Links to explore page posters/neighborhoods, SCTs |
| Agenda | Simple schedule by time; tap an item for details and its map location. |
| Explore | Browse/search showcase demos, posters, neighborhoods, or SCTs; connect each result to the map. |
| Info | Arrival/check-in, event hours, parking map/directions as appropriate, accessibility, help/contact information, FAQs. |
### 4. Festapp - Primary Inspiration

Festapp is the closest reference for the feel and simplicity I want. It brings the program, interactive map, notifications, and event information into one attendee experience.

- What to borrow: simple mobile experience, map-forward navigation, schedule + map connection, and live updates.
- What to make our own: a stronger search-to-location experience where a search result visibly highlights exactly where the attendee needs to go.

### 5. Developer Expectations / Questions

- Can our team easily update the agenda and locations without changing code?

### 6. Priority for Version 1

| Must Have | Nice to Have | Later / Stretch |
|---|---|---|
| Interactive map<br>Search -> highlighted map location<br>Agenda<br>Show on Map<br>Event info<br>Easy content updates | Filters<br>Favorites / My Schedule<br>QR codes that open a specific location| Advanced discovery paths<br>Other enhancements after core UX is proven |

If an attendee says, “I want to see _____,” the site should quickly answer: Here it is. Here is when it is happening. Here is exactly where you need to go.

## Constraints/considerations
- The agenda includes two different periods of the event, one in the morning, and one in the afternoon. We will need to swap out maps/posters/speakers for those times, so there should be a very modular way of inserting map data/poster data/speaker data

## Data
- Refer to data/ for all event related data currently available

## Code
### Stack
- Vue/Quasar
- Leaflet

### Testing:
- No testing needed. The human developer will do that for you.

### Installing and running servers
- Do not install packages for the developer
- Do not keep servers running after you run them to do appropriate checks

### Design guidelines:
- Never include extra words or descriptions that pertain to **how** to use the interface, where to click, or what information to enter into a field
- Minimalist at all times