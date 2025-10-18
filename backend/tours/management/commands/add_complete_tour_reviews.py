from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from tours.models import Tour, TourReview
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "Add reviews for complete adventure tour"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Adding reviews for complete adventure tour...")
        
        tour = Tour.objects.filter(slug='complete-adventure-tour').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour not found!"))
            return
        
        # Get or create test users
        users = []
        for i in range(10):
            user, created = User.objects.get_or_create(
                username=f'adventure_reviewer_{i+1}',
                defaults={
                    'email': f'adventure{i+1}@example.com',
                    'first_name': f'Reviewer',
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
                'title': 'Amazing Adventure Experience!',
                'comment': 'This tour exceeded all my expectations! The mountain views were breathtaking, the guide was knowledgeable, and the whole experience was perfectly organized. Highly recommended!',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 15
            },
            {
                'rating': 5,
                'title': 'تجربه‌ای فوق‌العاده!',
                'comment': 'این تور واقعاً عالی بود! مناظر کوهستانی خیره‌کننده، راهنمای حرفه‌ای و سازماندهی بی‌نقص. حتماً دوباره شرکت می‌کنم.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 12
            },
            {
                'rating': 5,
                'title': 'Mükemmel Macera!',
                'comment': 'Harika bir deneyimdi! Dağ manzaraları muhteşemdi, rehber çok bilgiliydi ve her şey mükemmel organize edilmişti.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 10
            },
            {
                'rating': 4,
                'title': 'Great Value for Money',
                'comment': 'Excellent tour with good value. The only minor issue was the lunch could have been better, but overall a fantastic experience.',
                'category': 'price',
                'is_verified': True,
                'is_helpful': 8
            },
            {
                'rating': 5,
                'title': 'خدمات عالی',
                'comment': 'کیفیت خدمات بسیار بالا بود. حمل و نقل راحت، غذای خوشمزه و راهنمای دوستانه. ارزش هر ریالش را دارد.',
                'category': 'quality',
                'is_verified': True,
                'is_helpful': 11
            },
            {
                'rating': 4,
                'title': 'Harika Organizasyon',
                'comment': 'Çok iyi organize edilmiş bir tur. Rehber çok yardımcı oldu ve grup küçük olduğu için herkes rahat etti.',
                'category': 'service',
                'is_verified': True,
                'is_helpful': 7
            },
            {
                'rating': 5,
                'title': 'Perfect for Nature Lovers',
                'comment': 'If you love nature and adventure, this is the perfect tour! The hiking was challenging but rewarding, and the sunset view was unforgettable.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 13
            },
            {
                'rating': 4,
                'title': 'تجربه فرهنگی عمیق',
                'comment': 'علاوه بر طبیعت زیبا، تجربه فرهنگی با مردم محلی بسیار جالب بود. فقط کمی زمان بیشتر برای عکاسی نیاز بود.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 9
            },
            {
                'rating': 5,
                'title': 'Profesyonel Rehber',
                'comment': 'Rehberimiz çok profesyoneldi. Hem güvenliğimizi sağladı hem de bölge hakkında çok şey öğretti. Teşekkürler!',
                'category': 'service',
                'is_verified': True,
                'is_helpful': 10
            },
            {
                'rating': 5,
                'title': 'Unforgettable Memories',
                'comment': 'This tour created memories that will last a lifetime. From the mountain summit to the cultural experiences, everything was perfect!',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 14
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
        self.stdout.write(f"Languages: English, Persian, Turkish")
        self.stdout.write(self.style.SUCCESS("\n✅ Reviews added successfully!"))
