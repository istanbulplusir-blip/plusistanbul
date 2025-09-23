from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from tours.models import Tour, TourReview
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "Create reviews and ratings for Tour X with various ratings and Persian/English content"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating reviews and ratings for Tour X...")
        
        # Get Tour X
        tour = Tour.objects.filter(slug='tour-x').first()
        if not tour:
            self.stdout.write(self.style.ERROR("❌ Tour X not found! Please create it first."))
            return
        
        self.stdout.write(f"✅ Found Tour X: {tour.title}")
        
        # Get existing users for reviews
        users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)[:8]
        if users.count() < 5:
            self.stdout.write(self.style.WARNING("⚠️ Not enough users found. Creating additional test users..."))
            # Create additional test users if needed
            additional_users = []
            for i in range(5 - users.count()):
                user, created = User.objects.get_or_create(
                    username=f'reviewer_{i+1}',
                    defaults={
                        'email': f'reviewer{i+1}@example.com',
                        'first_name': f'Reviewer',
                        'last_name': f'{i+1}',
                        'is_active': True,
                        'is_email_verified': True
                    }
                )
                if created:
                    user.set_password('Test@123456')
                    user.save()
                    additional_users.append(user)
                    self.stdout.write(f"   ✅ Created user: {user.username}")
            
            users = list(users) + additional_users
        
        # Clear existing reviews for Tour X
        existing_reviews = TourReview.objects.filter(tour=tour)
        if existing_reviews.exists():
            count = existing_reviews.count()
            existing_reviews.delete()
            self.stdout.write(f"🗑️ Deleted {count} existing reviews")
        
        # Review data with various ratings and content
        review_data = [
            {
                'rating': 5,
                'title': 'تجربه فوق‌العاده فرهنگی',
                'comment': 'این تور واقعاً فوق‌العاده بود! راهنمای متخصص، مکان‌های دیدنی زیبا و تجربه فرهنگی عمیق. حتماً دوباره شرکت خواهم کرد.',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 12
            },
            {
                'rating': 5,
                'title': 'Amazing Cultural Experience',
                'comment': 'This tour exceeded all expectations! The expert guide, beautiful locations, and deep cultural immersion made it unforgettable. Highly recommended!',
                'category': 'experience',
                'is_verified': True,
                'is_helpful': 8
            },
            {
                'rating': 4,
                'title': 'کیفیت خدمات عالی',
                'comment': 'خدمات با کیفیت بالا، حمل و نقل راحت و وعده غذایی خوشمزه. فقط کمی بیشتر زمان برای بازدید از موزه نیاز بود.',
                'category': 'quality',
                'is_verified': True,
                'is_helpful': 6
            },
            {
                'rating': 4,
                'title': 'Excellent Service Quality',
                'comment': 'High-quality services, comfortable transportation, and delicious meals. Just needed a bit more time at the museum.',
                'category': 'quality',
                'is_verified': True,
                'is_helpful': 5
            },
            {
                'rating': 5,
                'title': 'قیمت مناسب برای ارزش دریافتی',
                'comment': 'با توجه به خدمات ارائه شده، قیمت کاملاً مناسب است. شامل همه چیز بود و هیچ هزینه اضافی نداشتیم.',
                'category': 'price',
                'is_verified': True,
                'is_helpful': 9
            },
            {
                'rating': 4,
                'title': 'Good Value for Money',
                'comment': 'The price is reasonable for the services provided. Everything was included with no hidden costs.',
                'category': 'price',
                'is_verified': True,
                'is_helpful': 7
            },
            {
                'rating': 3,
                'title': 'تجربه متوسط',
                'comment': 'تور خوب بود اما انتظار بیشتری داشتیم. راهنما کمی عجله داشت و زمان کافی برای عکاسی نبود.',
                'category': 'general',
                'is_verified': True,
                'is_helpful': 3
            },
            {
                'rating': 3,
                'title': 'Average Experience',
                'comment': 'The tour was okay but we expected more. The guide seemed rushed and there wasn\'t enough time for photography.',
                'category': 'general',
                'is_verified': True,
                'is_helpful': 2
            },
            {
                'rating': 5,
                'title': 'خدمات راهنمایی عالی',
                'comment': 'راهنمای تور بسیار متخصص و دوستانه بود. اطلاعات کامل و جالب ارائه داد و همه سوالات ما را پاسخ داد.',
                'category': 'service',
                'is_verified': True,
                'is_helpful': 11
            },
            {
                'rating': 4,
                'title': 'Great Guide Service',
                'comment': 'The tour guide was very professional and friendly. Provided comprehensive and interesting information.',
                'category': 'service',
                'is_verified': True,
                'is_helpful': 6
            }
        ]
        
        # Create reviews
        created_reviews = []
        for i, review_info in enumerate(review_data):
            if i < len(users):
                user = users[i]
                
                # Create review with different creation dates
                review = TourReview.objects.create(
                    tour=tour,
                    user=user,
                    rating=review_info['rating'],
                    title=review_info['title'],
                    comment=review_info['comment'],
                    category=review_info['category'],
                    is_verified=review_info['is_verified'],
                    is_helpful=review_info['is_helpful'],
                    status='approved',
                    created_at=timezone.now() - timedelta(days=i+1),  # Different dates
                    updated_at=timezone.now() - timedelta(days=i+1)
                )
                created_reviews.append(review)
                
                self.stdout.write(f"   ✅ Created review: {review.rating}⭐ - {review.title}")
        
        # Calculate average rating
        total_rating = sum(review.rating for review in created_reviews)
        average_rating = total_rating / len(created_reviews)
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📊 TOUR X REVIEWS SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Total Reviews: {len(created_reviews)}")
        self.stdout.write(f"Average Rating: {average_rating:.1f}⭐")
        self.stdout.write(f"Verified Reviews: {sum(1 for r in created_reviews if r.is_verified)}")
        
        # Rating distribution
        rating_counts = {}
        for review in created_reviews:
            rating_counts[review.rating] = rating_counts.get(review.rating, 0) + 1
        
        self.stdout.write("\n📈 Rating Distribution:")
        for rating in sorted(rating_counts.keys()):
            count = rating_counts[rating]
            percentage = (count / len(created_reviews)) * 100
            stars = "⭐" * rating
            self.stdout.write(f"   {stars} ({rating}): {count} reviews ({percentage:.1f}%)")
        
        # Category distribution
        category_counts = {}
        for review in created_reviews:
            category_counts[review.category] = category_counts.get(review.category, 0) + 1
        
        self.stdout.write("\n📋 Category Distribution:")
        for category, count in category_counts.items():
            percentage = (count / len(created_reviews)) * 100
            self.stdout.write(f"   {category}: {count} reviews ({percentage:.1f}%)")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Tour X reviews created successfully!"))
        self.stdout.write(f"   Average Rating: {average_rating:.1f}⭐")
        self.stdout.write(f"   Total Reviews: {len(created_reviews)}")
        self.stdout.write(f"   Mix of Persian and English content")
        self.stdout.write(f"   Various ratings (3-5 stars)")
        self.stdout.write(f"   Different categories and helpful votes")
