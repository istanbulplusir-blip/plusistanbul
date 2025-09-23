# Events Seat Map Implementation – Phased TODO (Specialist Plan)

Purpose: Deliver a production-grade events ticketing experience with venue-accurate seat maps, real-time seat status, holds, pricing, and cart/checkout integration. Seatless flow remains as a fallback when no seats exist.

Guiding principles

- Keep seatless flow working at all times (section + ticket type + quantity)
- Minimize breaking changes; migrate in phases
- Optimize for concurrency and prevent overselling (DB-level guarantees)
- Keep APIs consistent with existing Next.js/Django integration; maintain AllowAny for browse/holds until checkout

Status snapshot

- [x] Section + ticket-type API for performance (with pricing and capacity)
- [x] Frontend seatless flow (performance → section → ticket_type → quantity → pricing → cart)
- [x] Pricing endpoint open for guests (AllowAny)
- [ ] Full seat-map (venue geometry, row/seat coordinates, real-time)

---

Phase 1 — Data model & migrations

- [ ] Add model: `VenueSeat`
  - Fields: `id (uuid)`, `venue`, `section (FK: EventSection or VenueSection)`, `row_name`, `seat_number`, `type` (normal/premium/wheelchair), `x`, `y`, `width`, `height`, `rotation`, `svg_id`, `created_at`, `updated_at`
  - Acceptance: Can import seats for a venue; unique `(section, row_name, seat_number)`
- [ ] Add model: `PerformanceSeat`
  - Fields: `id (uuid)`, `performance (FK: EventPerformance)`, `venue_seat (FK)`, `status` (available/reserved/sold/blocked), `reservation_id`, `reservation_expires_at`, `price_override (Decimal?)`, `created_at`, `updated_at`
  - Index: `(performance, venue_seat)` unique; index on `status`, `reservation_expires_at`
  - Acceptance: Can mark seats reserved/sold atomically per performance
- [ ] Optional: `VenueMap` for SVG meta and scaling
  - Fields: `venue (FK)`, `svg_file`, `width`, `height`, `scale`, `viewBox`
  - Acceptance: SVG uploaded and accessible for front-end rendering
- [ ] Extend `EventSection`
  - [ ] Add `polygon_svg_id` and/or simple geometry JSON (optional)
  - Acceptance: Front-end can highlight section shapes
- [ ] Migrations
  - Generate migrations; ensure no downtime for existing flows
  - Backfill `PerformanceSeat` if seats are imported (optional script)

Phase 2 — Admin & tooling

- [ ] Admin: CSV importer for `VenueSeat`
  - CSV columns: venue, section, row_name, seat_number, type, x, y[, width, height, rotation]
  - Acceptance: Seats import with validation and duplicates prevented
- [ ] Admin: SVG upload & mapping
  - Map `EventSection` to SVG path ids; basic UI to store `polygon_svg_id`
  - Acceptance: Section paths persisted and previewable
- [ ] Admin: Performance seat generation
  - Action to generate `PerformanceSeat` for a performance from `VenueSeat`
  - Acceptance: All seats for a performance created and set to `available`
- [ ] Admin list/displays
  - Show seat counts per performance/section; quick filters for `status`

Phase 3 — API (seat-centric)

- [ ] GET `/events/events/{event_id}/performances/{performance_id}/seat-map`
  - Returns: `svg_url`/inline SVG meta, sections (with shape id), rows, and seats with geometry `{id,x,y,type,status,price}`
  - Acceptance: Front-end can draw entire map with statuses
- [ ] GET `/events/performances/{performance_id}/available-seats` (tabular)
  - Filters: `section`, `ticket_type_id`
  - Acceptance: Supports list/grid fallback and admin diagnostics
- [ ] POST `/events/performances/{performance_id}/hold`
  - Input: `seat_ids[]`, `ticket_type_id`
  - Behavior: Atomically set status=reserved, set `reservation_id` and `expires_at`
  - Acceptance: Returns `{reservation_id, expires_at}`; idempotent on re-requests
- [ ] POST `/events/performances/{performance_id}/release`
  - Input: `reservation_id` or `seat_ids[]`
  - Acceptance: Seats revert to available if they match current reservation
- [ ] POST `/events/events/{event_id}/calculate_pricing` [extend]
  - Accept `seat_ids[]` OR `section_name + ticket_type_id + quantity`
  - Acceptance: Produces consistent `pricing_breakdown`
- [ ] POST `/cart/events/seats` [extend semantics]
  - If `seat_ids` provided, convert held seats → cart line; assert ownership/reservation
  - Acceptance: Cart line created; `reservation_expires_at` surfaced
- [ ] WebSocket `/ws/events/performances/{performance_id}`
  - Messages: `seat_status_changed`, `capacity_changed`, `reservation_expired`
  - Acceptance: Front-end syncs status without full refetch

Phase 4 — Front-end seat-map (SVG with fallback)

- [ ] Map Viewer component
  - Render SVG background; show selectable section shapes; zoom/pan; hit-testing
  - Virtualize seats if large count; color by `status` and `type`
  - Acceptance: Interaction at 60fps on desktop; graceful mobile experience
- [ ] Selection & holds
  - Click to select; batch POST `/hold`; on failure, refetch delta
  - Show hold timer per reservation; auto-release on expiry or back navigation
  - Acceptance: Seats cannot be double-held; UI error states clear
- [ ] Best-available flow
  - If user chooses N seats without map, call server for suggested adjacent seats; auto-hold
  - Acceptance: Reasonable adjacency; overrideable by user with map
- [ ] Seatless fallback (already)
  - If no `seat-map`, keep section+ticket_type+quantity flow
  - Acceptance: No regressions to current behavior

Phase 5 — Capacity & locking

- [ ] DB-level atomicity
  - Use `SELECT ... FOR UPDATE` or unique constraints to protect `(performance, venue_seat)` transitions
  - Acceptance: Simulate concurrent holds; no oversell
- [ ] Expiration job
  - Periodic task to release expired holds (`reservation_expires_at`)
  - Acceptance: Expired reservations free within SLA (< 1 min)

Phase 6 — Pricing, fees, discounts

- [ ] Seat-level pricing (optional)
  - Use `final_price` from SectionTicketType; allow seat premium via `price_override`
  - Acceptance: Premium rows/seats price correctly in UI/Cart
- [ ] Fees/taxes/discounts integration
  - Keep compatibility with existing pricing service and breakdown schema

Phase 7 — Testing & QA

- [ ] Unit tests
  - Model transitions: available → reserved → sold; expiry; migration integrity
  - API: seat-map, holds, releases, pricing, cart add
- [ ] Integration tests
  - E2E: select seats → hold → price → add to cart → checkout
- [ ] Load tests
  - Concurrency on holds and seat-map fetch
- [ ] Accessibility tests
  - Keyboard nav for seats, ARIA labels, color contrast

Phase 8 — Rollout & Monitoring

- [ ] Feature flag `seat_map_enabled` per event/venue
  - Roll out venue-by-venue
- [ ] Observability
  - Metrics: holds/sec, expiries, failed holds, checkout conversion
  - Logging structured events for disputes

Admin UX backlog (nice-to-have)

- [ ] Visual seat editor in admin (drag/drop, batch numbering)
- [ ] Import/Export seats JSON (backup & migration)
- [ ] Bulk block/unblock rows/sections per performance

Data contracts (samples)

- GET seat-map (sketch)

```
{
  "svg_url": "/media/venues/test-hall.svg",
  "sections": [{ "name": "A", "shape_id": "section-A", "base_price": 100 }],
  "seats": [{
    "id": "...", "section": "A", "row": "1", "number": "12",
    "x": 123, "y": 456, "type": "normal", "status": "available", "price": 120
  }]
}
```

- POST hold

```
{ "seat_ids": ["..."], "ticket_type_id": "..." } → { "reservation_id": "...", "expires_at": "..." }
```

Notes

- Keep existing section-only flow operational; only enable seat-map where data exists
- Ensure CORS and withCredentials remain enabled for guest flows

---

## Transfers/Tours/Events Production Hardening Checklist

### Transfer

- [ ] Currency end-to-end: return `currency` from pricing and use it in cart responses; set cart item currency to `pricing.currency`.
- [ ] Enforce option `max_quantity` and validate option IDs; filter options by `route_id` and `vehicle_type`.
- [ ] Timezone-aware validations (use aware datetimes consistently); align client/server TZ (prefer UTC).
- [ ] Add unit/integration tests for time rules (now+2h, return+2h, max 12 days), capacity, and options.
- [ ] Remove legacy API functions from `frontend/lib/api/transfers.ts`.

### Tours

- [ ] Enforce schedule/variant capacity on add-to-cart; temporary holds and release on item removal/expiry.
- [ ] Tests for capacity overbooking prevention and infant exclusion in capacity.

### Events

- [ ] Add hold expiry worker and atomic seat reservation to avoid oversell; optionally introduce optimistic locking.
- [ ] Polling or WebSocket updates for seat availability.
- [ ] Standardize pricing response fields across products (taxes/fees/currency).

### Platform

- [ ] Use `NEXT_PUBLIC_API_URL` in frontend (already supported) and configure per-env.
- [ ] Configure CORS/CSRF and cookie security for production domains.
- [ ] Structured logging and error tracking (e.g., Sentry); correlation IDs.
