"""
Comprehensive Event Test Data Creation Script
Creates complete Event products with all booking and cart scenarios
"""

import uuid
from datetime import datetime, timedelta, time
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile

# Event models
from events.models import (
    Event, EventCategory, EventPerformance, TicketType, Venue, Artist,
    EventOption, EventSection, SectionTicketType, EventDiscount, EventFee,
    EventPricingRule, Seat
)

# Other models
from users.models import User
from cart.models import Cart, CartItem

User = get_user_model()


def clear_event_data():
    """Clear all existing Event-related data"""
    print("🧹 Clearing existing Event data...")
    
    # Clear in correct order to avoid foreign key constraints
    EventPricingRule.objects.all().delete()
    EventFee.objects.all().delete()
    EventDiscount.objects.all().delete()
    Seat.objects.all().delete()
    SectionTicketType.objects.all().delete()
    EventSection.objects.all().delete()
    EventOption.objects.all().delete()
    TicketType.objects.all().delete()
    EventPerformance.objects.all().delete()
    Event.objects.all().delete()
    Artist.objects.all().delete()
    Venue.objects.all().delete()
    EventCategory.objects.all().delete()
    
    # Clear Event-related cart items
    CartItem.objects.filter(product_type='event').delete()
    
    print("✅ Event data cleared successfully")


def create_event_categories():
    """Create comprehensive Event categories with translations"""
    print("📂 Creating Event categories...")
    
    categories_data = {
        'music': {
            'name_en': 'Music Concerts',
            'name_fa': 'کنسرت موسیقی',
            'name_tr': 'Müzik Konserleri',
            'description_en': 'Live music performances and concerts',
            'description_fa': 'اجرای موسیقی زنده و کنسرت',
            'description_tr': 'Canlı müzik performansları ve konserler',
            'icon': 'music-note',
            'color': '#E91E63'
        },
        'theater': {
            'name_en': 'Theater Shows',
            'name_fa': 'نمایش‌های تئاتر',
            'name_tr': 'Tiyatro Gösterileri',
            'description_en': 'Dramatic performances and theater shows',
            'description_fa': 'اجرای نمایشی و نمایش‌های تئاتر',
            'description_tr': 'Dramatik performanslar ve tiyatro gösterileri',
            'icon': 'theater-masks',
            'color': '#9C27B0'
        },
        'sports': {
            'name_en': 'Sports Events',
            'name_fa': 'رویدادهای ورزشی',
            'name_tr': 'Spor Etkinlikleri',
            'description_en': 'Live sports events and competitions',
            'description_fa': 'رویدادهای ورزشی زنده و مسابقات',
            'description_tr': 'Canlı spor etkinlikleri ve yarışmaları',
            'icon': 'sports-soccer',
            'color': '#FF9800'
        },
        'festival': {
            'name_en': 'Festivals',
            'name_fa': 'جشنواره‌ها',
            'name_tr': 'Festivaller',
            'description_en': 'Cultural festivals and celebrations',
            'description_fa': 'جشنواره‌ها و جشن‌های فرهنگی',
            'description_tr': 'Kültürel festivaller ve kutlamalar',
            'icon': 'festival',
            'color': '#4CAF50'
        },
        'conference': {
            'name_en': 'Conferences',
            'name_fa': 'کنفرانس‌ها',
            'name_tr': 'Konferanslar',
            'description_en': 'Professional conferences and seminars',
            'description_fa': 'کنفرانس‌ها و سمینارهای حرفه‌ای',
            'description_tr': 'Profesyonel konferanslar ve seminerler',
            'icon': 'conference',
            'color': '#2196F3'
        }
    }
    
    categories = {}
    for slug, data in categories_data.items():
        category, created = EventCategory.objects.get_or_create(slug=slug)
        category.icon = data['icon']
        category.color = data['color']
        
        # Set translations
        category.set_current_language('en')
        category.name = data['name_en']
        category.description = data['description_en']
        category.save()
        
        category.set_current_language('fa')
        category.name = data['name_fa']
        category.description = data['description_fa']
        category.save()
        
        category.set_current_language('tr')
        category.name = data['name_tr']
        category.description = data['description_tr']
        category.save()
        
        categories[slug] = category
        print(f"  ✅ Created category: {data['name_en']}")
    
    return categories


def create_venues():
    """Create comprehensive Venues with proper data"""
    print("🏢 Creating Venues...")
    
    venues_data = [
        {
            'slug': 'grand-theater-tehran',
            'name_en': 'Grand Theater Tehran',
            'name_fa': 'تئاتر بزرگ تهران',
            'name_tr': 'Büyük Tiyatro Tahran',
            'description_en': 'Premier theater venue in the heart of Tehran',
            'description_fa': 'مهم‌ترین سالن تئاتر در قلب تهران',
            'description_tr': 'Tahran\'ın kalbindeki premier tiyatro mekanı',
            'address_en': '123 Theater Street, Tehran, Iran',
            'address_fa': 'تهران، خیابان تئاتر، ۱۲۳',
            'address_tr': '123 Tiyatro Caddesi, Tahran, İran',
            'city': 'Tehran',
            'country': 'Iran',
            'total_capacity': 2000,
            'coordinates': {'lat': 35.6892, 'lng': 51.3890},
            'facilities': ['parking', 'wheelchair_access', 'restaurant', 'bar']
        },
        {
            'slug': 'music-hall-isfahan',
            'name_en': 'Music Hall Isfahan',
            'name_fa': 'سالن موسیقی اصفهان',
            'name_tr': 'Müzik Salonu İsfahan',
            'description_en': 'Modern music venue with excellent acoustics',
            'description_fa': 'سالن موسیقی مدرن با آکوستیک عالی',
            'description_tr': 'Mükemmel akustik özellikli modern müzik mekanı',
            'address_en': '456 Music Avenue, Isfahan, Iran',
            'address_fa': 'اصفهان، خیابان موسیقی، ۴۵۶',
            'address_tr': '456 Müzik Caddesi, İsfahan, İran',
            'city': 'Isfahan',
            'country': 'Iran',
            'total_capacity': 1500,
            'coordinates': {'lat': 32.6546, 'lng': 51.6680},
            'facilities': ['parking', 'restaurant', 'sound_system']
        },
        {
            'slug': 'sports-complex-shiraz',
            'name_en': 'Sports Complex Shiraz',
            'name_fa': 'مجموعه ورزشی شیراز',
            'name_tr': 'Spor Kompleksi Şiraz',
            'description_en': 'Multi-purpose sports and events complex',
            'description_fa': 'مجموعه چند منظوره ورزشی و رویدادها',
            'description_tr': 'Çok amaçlı spor ve etkinlik kompleksi',
            'address_en': '789 Sports Boulevard, Shiraz, Iran',
            'address_fa': 'شیراز، بلوار ورزش، ۷۸۹',
            'address_tr': '789 Spor Bulvarı, Şiraz, İran',
            'city': 'Shiraz',
            'country': 'Iran',
            'total_capacity': 5000,
            'coordinates': {'lat': 29.5918, 'lng': 52.5837},
            'facilities': ['parking', 'wheelchair_access', 'food_court', 'merchandise']
        }
    ]
    
    venues = []
    for data in venues_data:
        venue, created = Venue.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'city': data['city'],
                'country': data['country'],
                'total_capacity': data['total_capacity'],
                'coordinates': data['coordinates'],
                'facilities': data['facilities']
            }
        )
        
        # Set translations
        venue.set_current_language('en')
        venue.name = data['name_en']
        venue.description = data['description_en']
        venue.address = data['address_en']
        venue.save()
        
        venue.set_current_language('fa')
        venue.name = data['name_fa']
        venue.description = data['description_fa']
        venue.address = data['address_fa']
        venue.save()
        
        venue.set_current_language('tr')
        venue.name = data['name_tr']
        venue.description = data['description_tr']
        venue.address = data['address_tr']
        venue.save()
        
        venues.append(venue)
        print(f"  ✅ Created venue: {data['name_en']}")
    
    return venues


def create_artists():
    """Create Artists with proper data"""
    print("🎭 Creating Artists...")
    
    artists_data = [
        {
            'slug': 'persian-orchestra',
            'name_en': 'Persian National Orchestra',
            'name_fa': 'ارکستر ملی ایران',
            'name_tr': 'İran Ulusal Orkestrası',
            'bio_en': 'Premier classical music orchestra specializing in Persian traditional music',
            'bio_fa': 'ارکستر موسیقی کلاسیک برتر متخصص در موسیقی سنتی ایرانی',
            'bio_tr': 'İran geleneksel müziğinde uzmanlaşmış premier klasik müzik orkestrası',
            'social_media': {
                'instagram': '@persian_orchestra',
                'twitter': '@persian_music',
                'website': 'www.persian-orchestra.com'
            }
        },
        {
            'slug': 'shakespeare-company',
            'name_en': 'Tehran Shakespeare Company',
            'name_fa': 'گروه نمایش شکسپیر تهران',
            'name_tr': 'Tahran Shakespeare Topluluğu',
            'bio_en': 'Professional theater company performing classic and contemporary works',
            'bio_fa': 'گروه حرفه‌ای نمایش با اجرای آثار کلاسیک و معاصر',
            'bio_tr': 'Klasik ve çağdaş eserleri sergileyen profesyonel tiyatro topluluğu',
            'social_media': {
                'instagram': '@tehran_shakespeare',
                'facebook': 'TehranShakespeare',
                'website': 'www.tehran-shakespeare.com'
            }
        },
        {
            'slug': 'festival-organizers',
            'name_en': 'Cultural Festival Organizers',
            'name_fa': 'برگزارکنندگان جشنواره فرهنگی',
            'name_tr': 'Kültürel Festival Organizatörleri',
            'bio_en': 'Experienced team organizing cultural festivals and celebrations',
            'bio_fa': 'تیم با تجربه برگزاری جشنواره‌ها و جشن‌های فرهنگی',
            'bio_tr': 'Kültürel festivaller ve kutlamalar düzenleyen deneyimli ekip',
            'social_media': {
                'instagram': '@cultural_festivals',
                'website': 'www.cultural-festivals.com'
            }
        }
    ]
    
    artists = []
    for data in artists_data:
        artist, created = Artist.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'social_media': data['social_media']
            }
        )
        
        # Set translations
        artist.set_current_language('en')
        artist.name = data['name_en']
        artist.bio = data['bio_en']
        artist.save()
        
        artist.set_current_language('fa')
        artist.name = data['name_fa']
        artist.bio = data['bio_fa']
        artist.save()
        
        artist.set_current_language('tr')
        artist.name = data['name_tr']
        artist.bio = data['bio_tr']
        artist.save()
        
        artists.append(artist)
        print(f"  ✅ Created artist: {data['name_en']}")
    
    return artists


def create_comprehensive_events(categories, venues, artists):
    """Create comprehensive Event products with all features"""
    print("🎪 Creating comprehensive Event products...")
    
    events_data = [
        {
            'slug': 'persian-classical-concert-2024',
            'title_en': 'Persian Classical Concert 2024',
            'title_fa': 'کنسرت کلاسیک ایرانی ۲۰۲۴',
            'title_tr': 'İran Klasik Konseri 2024',
            'description_en': 'An enchanting evening of traditional Persian music featuring the Persian National Orchestra',
            'description_fa': 'شبی جذاب از موسیقی سنتی ایرانی با حضور ارکستر ملی ایران',
            'description_tr': 'İran Ulusal Orkestrası ile geleneksel İran müziğinin büyüleyici bir akşamı',
            'short_description_en': 'Traditional Persian music concert',
            'short_description_fa': 'کنسرت موسیقی سنتی ایرانی',
            'short_description_tr': 'Geleneksel İran müzik konseri',
            'highlights_en': '• Live performance by Persian National Orchestra\n• Traditional Persian instruments\n• Classic repertoire\n• VIP meet & greet available',
            'highlights_fa': '• اجرای زنده ارکستر ملی ایران\n• سازهای سنتی ایرانی\n• رپرتوار کلاسیک\n• ملاقات VIP موجود',
            'highlights_tr': '• İran Ulusal Orkestrası canlı performans\n• Geleneksel İran enstrümanları\n• Klasik repertuvar\n• VIP karşılaşma mevcut',
            'category': 'music',
            'venue': 'music-hall-isfahan',
            'artists': ['persian-orchestra'],
            'style': 'music',
            'door_open_time': '18:00',
            'start_time': '19:30',
            'end_time': '22:00',
            'age_restriction': None,
            'gallery': ['concert1.jpg', 'concert2.jpg'],
            'base_price': 120.00
        },
        {
            'slug': 'hamlet-shakespeare-theater',
            'title_en': 'Hamlet - Shakespeare Theater',
            'title_fa': 'هملت - تئاتر شکسپیر',
            'title_tr': 'Hamlet - Shakespeare Tiyatrosu',
            'description_en': 'A masterful interpretation of Shakespeare\'s greatest tragedy, performed by Tehran Shakespeare Company',
            'description_fa': 'تفسیری استادانه از بزرگترین تراژدی شکسپیر، اجرا شده توسط گروه شکسپیر تهران',
            'description_tr': 'Tahran Shakespeare Topluluğu tarafından sergilenen Shakespeare\'in en büyük trajedisinin ustaca yorumu',
            'short_description_en': 'Shakespeare\'s Hamlet performed in Persian',
            'short_description_fa': 'هملت شکسپیر به زبان فارسی',
            'short_description_tr': 'Farsça sahnelenen Shakespeare\'in Hamlet\'i',
            'highlights_en': '• Professional theater company\n• Classic Shakespeare play\n• Persian translation\n• 3-hour performance with intermission',
            'highlights_fa': '• گروه حرفه‌ای نمایش\n• نمایش کلاسیک شکسپیر\n• ترجمه فارسی\n• اجرای ۳ ساعته با فاصله',
            'highlights_tr': '• Profesyonel tiyatro topluluğu\n• Klasik Shakespeare oyunu\n• Farsça çeviri\n• Ara ile 3 saatlik performans',
            'category': 'theater',
            'venue': 'grand-theater-tehran',
            'artists': ['shakespeare-company'],
            'style': 'theater',
            'door_open_time': '17:30',
            'start_time': '18:00',
            'end_time': '21:30',
            'age_restriction': 12,
            'gallery': ['hamlet1.jpg', 'hamlet2.jpg'],
            'base_price': 80.00
        },
        {
            'slug': 'spring-cultural-festival',
            'title_en': 'Spring Cultural Festival 2024',
            'title_fa': 'جشنواره فرهنگی بهار ۲۰۲۴',
            'title_tr': 'Bahar Kültür Festivali 2024',
            'description_en': 'A vibrant celebration of spring with music, dance, food, and cultural exhibitions',
            'description_fa': 'جشنی پر نشاط از بهار با موسیقی، رقص، غذا و نمایشگاه‌های فرهنگی',
            'description_tr': 'Müzik, dans, yemek ve kültürel sergilerle baharın canlı kutlaması',
            'short_description_en': 'Multi-day cultural festival celebrating spring',
            'short_description_fa': 'جشنواره فرهنگی چند روزه جشن بهار',
            'short_description_tr': 'Baharı kutlayan çok günlük kültürel festival',
            'highlights_en': '• Multiple stages and performances\n• Food and craft vendors\n• Family-friendly activities\n• Cultural exhibitions',
            'highlights_fa': '• چندین صحنه و اجرا\n• غذا و صنایع دستی\n• فعالیت‌های خانوادگی\n• نمایشگاه‌های فرهنگی',
            'highlights_tr': '• Çoklu sahne ve performanslar\n• Yemek ve el sanatları satıcıları\n• Aile dostu aktiviteler\n• Kültürel sergiler',
            'category': 'festival',
            'venue': 'sports-complex-shiraz',
            'artists': ['festival-organizers'],
            'style': 'festival',
            'door_open_time': '10:00',
            'start_time': '11:00',
            'end_time': '23:00',
            'age_restriction': None,
            'gallery': ['festival1.jpg', 'festival2.jpg', 'festival3.jpg'],
            'base_price': 50.00
        }
    ]
    
    events = []
    for data in events_data:
        event, created = Event.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'category': categories[data['category']],
                'venue': venues[next(i for i, v in enumerate(venues) if v.slug == data['venue'])],
                'style': data['style'],
                'door_open_time': data['door_open_time'],
                'start_time': data['start_time'],
                'end_time': data['end_time'],
                'age_restriction': data['age_restriction'],
                'gallery': data['gallery'],
                'is_active': True,
                'price': data['base_price']
            }
        )
        
        # Set translations
        event.set_current_language('en')
        event.title = data['title_en']
        event.description = data['description_en']
        event.short_description = data['short_description_en']
        event.highlights = data['highlights_en']
        event.save()
        
        event.set_current_language('fa')
        event.title = data['title_fa']
        event.description = data['description_fa']
        event.short_description = data['short_description_fa']
        event.highlights = data['highlights_fa']
        event.save()
        
        event.set_current_language('tr')
        event.title = data['title_tr']
        event.description = data['description_tr']
        event.short_description = data['short_description_tr']
        event.highlights = data['highlights_tr']
        event.save()
        
        # Add artists
        for artist_slug in data['artists']:
            artist = next(a for a in artists if a.slug == artist_slug)
            event.artists.add(artist)
        
        events.append(event)
        print(f"  ✅ Created event: {data['title_en']}")
    
    return events


def create_ticket_types(events):
    """Create diverse ticket types for events"""
    print("🎫 Creating ticket types...")
    
    ticket_types_data = [
        {
            'name': 'VIP',
            'ticket_type': 'vip',
            'description': 'Premium seating with exclusive benefits',
            'price_modifier': 1.5,
            'benefits': ['Premium seating', 'Complimentary drinks', 'Meet & greet', 'Exclusive merchandise'],
            'age_min': None,
            'age_max': None
        },
        {
            'name': 'Premium',
            'ticket_type': 'normal',
            'description': 'Good seating with standard amenities',
            'price_modifier': 1.2,
            'benefits': ['Good seating', 'Standard amenities'],
            'age_min': None,
            'age_max': None
        },
        {
            'name': 'Standard',
            'ticket_type': 'normal',
            'description': 'Standard seating',
            'price_modifier': 1.0,
            'benefits': ['Standard seating'],
            'age_min': None,
            'age_max': None
        },
        {
            'name': 'Economy',
            'ticket_type': 'eco',
            'description': 'Budget-friendly option',
            'price_modifier': 0.7,
            'benefits': ['Basic seating'],
            'age_min': None,
            'age_max': None
        },
        {
            'name': 'Student',
            'ticket_type': 'student',
            'description': 'Special pricing for students',
            'price_modifier': 0.5,
            'benefits': ['Student discount', 'Valid student ID required'],
            'age_min': 16,
            'age_max': 35
        },
        {
            'name': 'Senior',
            'ticket_type': 'senior',
            'description': 'Special pricing for seniors',
            'price_modifier': 0.6,
            'benefits': ['Senior discount', 'Easy access seating'],
            'age_min': 60,
            'age_max': None
        },
        {
            'name': 'Wheelchair',
            'ticket_type': 'wheelchair',
            'description': 'Wheelchair accessible seating',
            'price_modifier': 1.0,
            'benefits': ['Wheelchair accessible', 'Companion seating'],
            'age_min': None,
            'age_max': None
        }
    ]
    
    all_ticket_types = []
    for event in events:
        print(f"  Creating ticket types for: {event.title}")
        
        for ticket_data in ticket_types_data:
            ticket_type, created = TicketType.objects.get_or_create(
                event=event,
                name=ticket_data['name'],
                defaults={
                    'ticket_type': ticket_data['ticket_type'],
                    'description': ticket_data['description'],
                    'price_modifier': ticket_data['price_modifier'],
                    'capacity': event.venue.total_capacity,  # Set capacity field
                    'benefits': ticket_data['benefits'],
                    'age_min': ticket_data['age_min'],
                    'age_max': ticket_data['age_max'],
                    'is_active': True
                }
            )
            all_ticket_types.append(ticket_type)
            if created:
                print(f"    ✅ Created ticket type: {ticket_data['name']}")
    
    return all_ticket_types


def create_performances_with_capacity(events, ticket_types):
    """Create performances with comprehensive capacity structure"""
    print("📅 Creating performances with capacity structure...")
    
    performances = []
    sections = []
    
    for event in events:
        print(f"  Creating performances for: {event.title}")
        
        # Create 5 performances over the next 2 weeks
        for i in range(5):
            performance_date = timezone.now().date() + timedelta(days=i+2)
            
            performance, created = EventPerformance.objects.get_or_create(
                event=event,
                date=performance_date,
                defaults={
                    'start_date': performance_date,
                    'end_date': performance_date,
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'is_available': True,
                    'is_active': True,
                    'max_capacity': event.venue.total_capacity,
                    'current_capacity': 0,
                    'is_special': i == 0,  # First performance is special
                    'ticket_capacities': {}
                }
            )
            
            if created:
                print(f"    ✅ Created performance: {performance_date}")
                
                # Create sections for this performance
                if event.style == 'music':
                    sections_data = [
                        {'name': 'VIP', 'capacity': 200, 'base_price': 180.00, 'is_premium': True},
                        {'name': 'Premium', 'capacity': 400, 'base_price': 144.00, 'is_premium': False},
                        {'name': 'Standard', 'capacity': 700, 'base_price': 120.00, 'is_premium': False},
                        {'name': 'Economy', 'capacity': 200, 'base_price': 84.00, 'is_premium': False}
                    ]
                elif event.style == 'theater':
                    sections_data = [
                        {'name': 'Orchestra', 'capacity': 300, 'base_price': 120.00, 'is_premium': True},
                        {'name': 'Mezzanine', 'capacity': 400, 'base_price': 96.00, 'is_premium': False},
                        {'name': 'Balcony', 'capacity': 600, 'base_price': 80.00, 'is_premium': False},
                        {'name': 'Gallery', 'capacity': 700, 'base_price': 64.00, 'is_premium': False}
                    ]
                elif event.style == 'festival':
                    sections_data = [
                        {'name': 'VIP Area', 'capacity': 500, 'base_price': 75.00, 'is_premium': True},
                        {'name': 'Premium Zone', 'capacity': 1000, 'base_price': 60.00, 'is_premium': False},
                        {'name': 'General Admission', 'capacity': 2500, 'base_price': 50.00, 'is_premium': False},
                        {'name': 'Student Zone', 'capacity': 1000, 'base_price': 25.00, 'is_premium': False}
                    ]
                
                # Create sections
                for section_data in sections_data:
                    section = EventSection.objects.create(
                        performance=performance,
                        name=section_data['name'],
                        total_capacity=section_data['capacity'],
                        available_capacity=section_data['capacity'],
                        base_price=section_data['base_price'],
                        is_premium=section_data['is_premium'],
                        is_wheelchair_accessible=section_data['name'] in ['Standard', 'General Admission']
                    )
                    sections.append(section)
                    
                    # Create ticket type allocations for this section
                    event_ticket_types = [tt for tt in ticket_types if tt.event == event]
                    
                    for ticket_type in event_ticket_types:
                        # Allocate capacity based on ticket type
                        if ticket_type.name == 'VIP' and section_data['is_premium']:
                            allocated = int(section_data['capacity'] * 0.3)
                        elif ticket_type.name == 'Premium' and not section_data['is_premium']:
                            allocated = int(section_data['capacity'] * 0.2)
                        elif ticket_type.name == 'Standard':
                            allocated = int(section_data['capacity'] * 0.4)
                        elif ticket_type.name == 'Economy':
                            allocated = int(section_data['capacity'] * 0.3)
                        elif ticket_type.name == 'Student' and 'Student' in section_data['name']:
                            allocated = int(section_data['capacity'] * 0.8)
                        elif ticket_type.name == 'Senior':
                            allocated = int(section_data['capacity'] * 0.1)
                        elif ticket_type.name == 'Wheelchair':
                            allocated = int(section_data['capacity'] * 0.05) if section.is_wheelchair_accessible else 0
                        else:
                            allocated = int(section_data['capacity'] * 0.1)
                        
                        if allocated > 0:
                            SectionTicketType.objects.create(
                                section=section,
                                ticket_type=ticket_type,
                                allocated_capacity=allocated,
                                available_capacity=allocated,
                                price_modifier=ticket_type.price_modifier
                            )
                
                performances.append(performance)
    
    print(f"  ✅ Created {len(performances)} performances with {len(sections)} sections")
    return performances, sections


def create_event_options(events):
    """Create comprehensive Event options"""
    print("🎯 Creating Event options...")
    
    options_data = [
        {
            'name': 'Premium Parking',
            'description': 'Reserved parking spot close to venue',
            'option_type': 'parking',
            'price': 15.00,
            'max_quantity': 1
        },
        {
            'name': 'Valet Parking',
            'description': 'Valet parking service',
            'option_type': 'parking',
            'price': 25.00,
            'max_quantity': 1
        },
        {
            'name': 'Pre-Show Dinner',
            'description': 'Three-course dinner before the show',
            'option_type': 'food',
            'price': 45.00,
            'max_quantity': 4
        },
        {
            'name': 'Intermission Refreshments',
            'description': 'Drinks and light snacks during intermission',
            'option_type': 'food',
            'price': 20.00,
            'max_quantity': 4
        },
        {
            'name': 'Audio Guide',
            'description': 'Personal audio guide device',
            'option_type': 'equipment',
            'price': 10.00,
            'max_quantity': 4
        },
        {
            'name': 'Program Book',
            'description': 'Commemorative program book',
            'option_type': 'service',
            'price': 8.00,
            'max_quantity': 4
        },
        {
            'name': 'Merchandise Package',
            'description': 'T-shirt and poster set',
            'option_type': 'service',
            'price': 30.00,
            'max_quantity': 2
        },
        {
            'name': 'Transportation',
            'description': 'Round-trip transportation to venue',
            'option_type': 'transport',
            'price': 20.00,
            'max_quantity': 4
        }
    ]
    
    all_options = []
    for event in events:
        print(f"  Creating options for: {event.title}")
        
        for option_data in options_data:
            option, created = EventOption.objects.get_or_create(
                event=event,
                name=option_data['name'],
                defaults={
                    'description': option_data['description'],
                    'option_type': option_data['option_type'],
                    'price': option_data['price'],
                    'max_quantity': option_data['max_quantity'],
                    'is_available': True
                }
            )
            all_options.append(option)
            if created:
                print(f"    ✅ Created option: {option_data['name']}")
    
    return all_options


def create_pricing_discounts_fees(events):
    """Create pricing rules, discounts, and fees"""
    print("💰 Creating pricing rules, discounts, and fees...")
    
    discounts = []
    fees = []
    pricing_rules = []
    
    for event in events:
        print(f"  Creating pricing elements for: {event.title}")
        
        # Create discounts
        discount_data = [
            {
                'code': f'EARLY{event.id}',
                'name': 'Early Bird Discount',
                'description': '20% off for early bookings',
                'discount_type': 'percentage',
                'discount_value': 20.00,
                'min_amount': 50.00,
                'max_uses': 100,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=30)
            },
            {
                'code': f'GROUP{event.id}',
                'name': 'Group Discount',
                'description': '15% off for groups of 4+',
                'discount_type': 'percentage',
                'discount_value': 15.00,
                'min_amount': 200.00,
                'max_uses': 50,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=60)
            },
            {
                'code': f'STUDENT{event.id}',
                'name': 'Student Discount',
                'description': '$10 off for students',
                'discount_type': 'fixed',
                'discount_value': 10.00,
                'min_amount': 30.00,
                'max_uses': 200,
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=90)
            }
        ]
        
        for discount_info in discount_data:
            discount, created = EventDiscount.objects.get_or_create(
                event=event,
                code=discount_info['code'],
                defaults={
                    'name': discount_info['name'],
                    'description': discount_info['description'],
                    'discount_type': discount_info['discount_type'],
                    'discount_value': discount_info['discount_value'],
                    'min_amount': discount_info['min_amount'],
                    'max_uses': discount_info['max_uses'],
                    'valid_from': discount_info['valid_from'],
                    'valid_until': discount_info['valid_until'],
                    'is_active': True
                }
            )
            discounts.append(discount)
            if created:
                print(f"    ✅ Created discount: {discount_info['name']}")
        
        # Create fees
        fee_data = [
            {
                'name': 'Service Fee',
                'description': 'Booking service fee',
                'fee_type': 'service',
                'calculation_type': 'percentage',
                'fee_value': 5.00,
                'min_amount': 0.00,
                'max_fee': 20.00,
                'is_mandatory': True
            },
            {
                'name': 'Processing Fee',
                'description': 'Payment processing fee',
                'fee_type': 'processing',
                'calculation_type': 'per_booking',
                'fee_value': 2.50,
                'min_amount': 0.00,
                'is_mandatory': True
            },
            {
                'name': 'Convenience Fee',
                'description': 'Online booking convenience fee',
                'fee_type': 'convenience',
                'calculation_type': 'per_ticket',
                'fee_value': 1.50,
                'min_amount': 0.00,
                'is_mandatory': False
            }
        ]
        
        for fee_info in fee_data:
            fee, created = EventFee.objects.get_or_create(
                event=event,
                name=fee_info['name'],
                defaults={
                    'description': fee_info['description'],
                    'fee_type': fee_info['fee_type'],
                    'calculation_type': fee_info['calculation_type'],
                    'fee_value': fee_info['fee_value'],
                    'min_amount': fee_info['min_amount'],
                    'max_fee': fee_info.get('max_fee'),
                    'is_mandatory': fee_info['is_mandatory'],
                    'is_active': True
                }
            )
            fees.append(fee)
            if created:
                print(f"    ✅ Created fee: {fee_info['name']}")
        
        # Create pricing rules
        rule_data = [
            {
                'name': 'Early Bird Pricing',
                'description': '15% discount for bookings made 30+ days in advance',
                'rule_type': 'early_bird',
                'adjustment_type': 'percentage',
                'adjustment_value': -15.00,
                'conditions': {'days_in_advance': 30},
                'priority': 3
            },
            {
                'name': 'Last Minute Pricing',
                'description': '10% surcharge for bookings made within 24 hours',
                'rule_type': 'last_minute',
                'adjustment_type': 'percentage',
                'adjustment_value': 10.00,
                'conditions': {'hours_before': 24},
                'priority': 2
            },
            {
                'name': 'Weekend Premium',
                'description': '20% premium for weekend performances',
                'rule_type': 'weekend',
                'adjustment_type': 'percentage',
                'adjustment_value': 20.00,
                'conditions': {'days_of_week': [5, 6]},
                'priority': 1
            }
        ]
        
        for rule_info in rule_data:
            rule, created = EventPricingRule.objects.get_or_create(
                event=event,
                name=rule_info['name'],
                defaults={
                    'description': rule_info['description'],
                    'rule_type': rule_info['rule_type'],
                    'adjustment_type': rule_info['adjustment_type'],
                    'adjustment_value': rule_info['adjustment_value'],
                    'conditions': rule_info['conditions'],
                    'priority': rule_info['priority'],
                    'is_active': True
                }
            )
            pricing_rules.append(rule)
            if created:
                print(f"    ✅ Created pricing rule: {rule_info['name']}")
    
    return discounts, fees, pricing_rules


def run_comprehensive_event_test_data():
    """Main function to create comprehensive Event test data"""
    print("🚀 Starting comprehensive Event test data creation...")
    
    with transaction.atomic():
        # Step 1: Clear existing data
        clear_event_data()
        
        # Step 2: Create categories
        categories = create_event_categories()
        
        # Step 3: Create venues
        venues = create_venues()
        
        # Step 4: Create artists
        artists = create_artists()
        
        # Step 5: Create events
        events = create_comprehensive_events(categories, venues, artists)
        
        # Step 6: Create ticket types
        ticket_types = create_ticket_types(events)
        
        # Step 7: Create performances with capacity structure
        performances, sections = create_performances_with_capacity(events, ticket_types)
        
        # Step 8: Create event options
        options = create_event_options(events)
        
        # Step 9: Create pricing, discounts, and fees
        discounts, fees, pricing_rules = create_pricing_discounts_fees(events)
        
        print("✅ Comprehensive Event test data created successfully!")
        print(f"   - {len(categories)} Categories created")
        print(f"   - {len(venues)} Venues created")
        print(f"   - {len(artists)} Artists created")
        print(f"   - {len(events)} Events created")
        print(f"   - {len(ticket_types)} Ticket types created")
        print(f"   - {len(performances)} Performances created")
        print(f"   - {len(sections)} Sections created")
        print(f"   - {len(options)} Options created")
        print(f"   - {len(discounts)} Discounts created")
        print(f"   - {len(fees)} Fees created")
        print(f"   - {len(pricing_rules)} Pricing rules created")
        
        return {
            'categories': categories,
            'venues': venues,
            'artists': artists,
            'events': events,
            'ticket_types': ticket_types,
            'performances': performances,
            'sections': sections,
            'options': options,
            'discounts': discounts,
            'fees': fees,
            'pricing_rules': pricing_rules
        }


if __name__ == '__main__':
    import os
    import sys
    import django
    
    # Add the backend directory to the Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
    django.setup()
    
    # Run the test data creation
    result = run_comprehensive_event_test_data()
    print("\n🎉 Comprehensive Event test data creation completed!") 