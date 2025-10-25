from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from tours.models import Tour, TourReview
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "Add reviews for Istanbul Bosphorus tour"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Adding reviews for Istanbul Bosphorus tour...")
        
        tour = Tour.objects.filter(slug='istanbul-bosphorus-cruise').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour not found!"))
            return
        
        # Get or create test users
        users = []
        for i in range(15):
            user, created = User.objects.get_or_create(
                username=f'bosphorus_reviewer_{i+1}',
                defaults={
                    'email': f'bosphorus{i+1}@example.com',
                    'first_name': f'Tourist',
                    'last_name': f'{i+1}',
                    'is_active': True,
                    'is_email_verified': True
                }
            )
            if created:
                user.set_password('Test@123456')
                user.save()
            users.append(user)
        
        # Clear existing reviews
        tour.reviews.all().delete()
        
        # Review data in 3 languages
        reviews_data = [
            {
                'rating': 5,
                'title': 'Absolutely Stunning Experience!',
                'comment': 'The Bosphorus cruise was the highlight of our Istanbul trip! The views were breathtaking, the guide was knowledgeable, and the lunch was delicious. Highly recommend!',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 24
            },
            {
                'rating': 5,
                'title': 'Muhteşem Bir Deneyim!',
                'comment': 'Boğaz turu İstanbul gezimizin en güzel anıydı! Manzaralar nefes kesiciydi, rehber çok bilgiliydi ve yemek harikaydı. Kesinlikle tavsiye ederim!',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 21
            },
            {
                'rating': 5,
                'title': 'تجربه‌ای فوق‌العاده!',
                'comment': 'کروز بسفر نقطه اوج سفر استانبول ما بود! مناظر خیره‌کننده، راهنمای دانا و ناهار خوشمزه. به شدت توصیه می‌کنم!',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 18
            },
            {
                'rating': 5,
                'title': 'Perfect Way to See Istanbul',
                'comment': 'Seeing Istanbul from the water gives you a completely different perspective. The palaces and mosques look even more magnificent from the Bosphorus. Our guide shared fascinating historical stories.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 19
            },
            {
                'rating': 4,
                'title': 'Great Tour, Minor Issues',
                'comment': 'Overall excellent tour! The cruise was beautiful and well-organized. Only complaint is that it was a bit crowded on the boat. Still worth it for the amazing views.',
                'category': 'quality',
                'is_verified': True,
                'is_helpful': 12
            },
            {
                'rating': 5,
                'title': 'İki Kıta Arasında Harika Yolculuk',
                'comment': 'Avrupa ve Asya arasında yolculuk yapmak inanılmaz bir deneyimdi. Dolmabahçe Sarayı muhteşemdi ve öğle yemeği çok lezzetliydi. Teşekkürler!',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 16
            },
            {
                'rating': 5,
                'title': 'بهترین تور استانبول',
                'comment': 'این تور واقعاً عالی بود! دیدن کاخ‌ها و مساجد از روی آب تجربه‌ای منحصر به فرد است. راهنما بسیار حرفه‌ای و دوستانه بود.',
                'category': 'service',
                'is_verified': True,
                'is_helpful': 15
            },
            {
                'rating': 5,
                'title': 'Unforgettable Memories',
                'comment': 'This tour created memories that will last forever! Crossing between continents, seeing the Maiden\'s Tower, and enjoying Turkish cuisine - everything was perfect!',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 20
            },
            {
                'rating': 4,
                'title': 'Excellent Value for Money',
                'comment': 'Great tour at a reasonable price. The boat was comfortable, the food was good, and we saw all the major sights. Would definitely recommend to friends.',
                'category': 'price',
                'is_verified': True,
                'is_helpful': 14
            },
            {
                'rating': 5,
                'title': 'Profesyonel ve Keyifli',
                'comment': 'Her şey mükemmel organize edilmişti. Rehberimiz çok bilgiliydi ve sürekli ilgilendi. Boğaz\'ın güzelliğini tam anlamıyla yaşadık.',
                'category': 'service',
                'is_verified': True,
                'is_helpful': 17
            },
            {
                'rating': 5,
                'title': 'سازماندهی عالی',
                'comment': 'همه چیز به خوبی سازماندهی شده بود. پیکاپ از هتل به موقع، قایق تمیز و راحت، و غذا خوشمزه. تجربه‌ای بی‌نقص!',
                'category': 'quality',
                'is_verified': True,
                'is_helpful': 13
            },
            {
                'rating': 5,
                'title': 'Best Tour in Istanbul!',
                'comment': 'We did several tours in Istanbul, but this was by far the best! The combination of boat cruise, palace visit, and delicious lunch made it perfect.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 22
            },
            {
                'rating': 4,
                'title': 'Harika Manzaralar',
                'comment': 'Boğaz manzaraları gerçekten muhteşemdi. Fotoğraf çekmek için harika fırsatlar. Sadece biraz daha fazla serbest zaman olsaydı daha iyi olurdu.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 11
            },
            {
                'rating': 5,
                'title': 'راهنمای عالی و دانا',
                'comment': 'راهنمای ما واقعاً استثنایی بود. داستان‌های تاریخی جذابی تعریف کرد و به همه سوالات ما پاسخ داد. از این تور لذت بردیم!',
                'category': 'service',
                'is_verified': True,
                'is_helpful': 16
            },
            {
                'rating': 5,
                'title': 'Perfect for Photography Lovers',
                'comment': 'As a photography enthusiast, this tour was a dream! So many beautiful shots of palaces, bridges, and the stunning Bosphorus. The guide gave us plenty of time for photos.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 19
            }
        ]
        
        created_reviews = []
        for i, review_info in enumerate(reviews_data):
            review = TourReview.objects.create(
                tour=tour,
                user=users[i],
                rating=review_info['rating'],
                title=review_info['title'],
                comment=review_info['comment'],
                category=review_info['category'],
                is_verified=review_info['is_verified'],
                is_helpful=review_info['is_helpful'],
                status='approved',
                created_at=timezone.now() - timedelta(days=i+1),
                updated_at=timezone.now() - timedelta(days=i+1)
            )
            created_reviews.append(review)
            self.stdout.write(f"✅ Created review: {review.rating}⭐ - {review.title[:50]}")
        
        # Calculate stats
        total_rating = sum(r.rating for r in created_reviews)
        avg_rating = total_rating / len(created_reviews)
        
        rating_counts = {}
        for review in created_reviews:
            rating_counts[review.rating] = rating_counts.get(review.rating, 0) + 1
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 REVIEWS SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Total Reviews: {len(created_reviews)}")
        self.stdout.write(f"Average Rating: {avg_rating:.1f}⭐")
        self.stdout.write(f"5-Star: {rating_counts.get(5, 0)} reviews")
        self.stdout.write(f"4-Star: {rating_counts.get(4, 0)} reviews")
        self.stdout.write(f"Languages: English, Turkish, Persian")
        self.stdout.write(self.style.SUCCESS("\n✅ Reviews added successfully!"))
