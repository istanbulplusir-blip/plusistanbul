from events.models import Event, EventSection, Seat

e = Event.objects.get(slug='complete-concert-2025')
p = e.performances.first()

print('=== EVENT DETAILS ===')
print(f'Title (FA): {e.title}')
e.set_current_language('en')
print(f'Title (EN): {e.title}')
e.set_current_language('ar')
print(f'Title (AR): {e.title}')
print(f'Ticket Types: {e.ticket_types.count()}')
print(f'Options: {e.options.count()}')
print(f'Artists: {e.artists.count()}')
print()

print('=== PERFORMANCE ===')
print(f'Date: {p.date}')
print(f'Sections: {p.sections.count()}')
print()

print('=== SECTIONS ===')
for s in p.sections.all():
    print(f'{s.name}: {s.total_capacity} seats, ${s.base_price}')
print()

print('=== SEATS ===')
for s in p.sections.all():
    seats = Seat.objects.filter(performance=p, section=s.name)
    print(f'{s.name}: {seats.count()} seats')
    for seat in seats[:3]:
        print(f'  - {seat.row_number}{seat.seat_number}: ${seat.price} ({seat.status})')
