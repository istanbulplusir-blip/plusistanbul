#!/usr/bin/env python
"""
Verify Tour X reviews and ratings
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from tours.models import Tour, TourReview

def verify_tour_x_reviews():
    """Verify Tour X reviews and ratings"""
    print("🔍 Verifying Tour X Reviews and Ratings")
    print("=" * 60)
    
    # Find Tour X
    tour = Tour.objects.filter(slug='tour-x').first()
    if not tour:
        print("❌ Tour X not found!")
        return False
    
    print(f"✅ Found Tour X: {tour.title}")
    
    # Get reviews
    reviews = tour.reviews.all().order_by('-created_at')
    
    if reviews.count() == 0:
        print("❌ No reviews found for Tour X!")
        return False
    
    print(f"✅ Found {reviews.count()} reviews")
    
    # Basic review information
    print("\n📋 Review Information:")
    print(f"   Total Reviews: {reviews.count()}")
    
    # Calculate average rating
    total_rating = sum(review.rating for review in reviews)
    average_rating = total_rating / reviews.count()
    print(f"   Average Rating: {average_rating:.1f}⭐")
    
    # Verified reviews
    verified_count = sum(1 for review in reviews if review.is_verified)
    print(f"   Verified Reviews: {verified_count}")
    
    # Rating distribution
    rating_counts = {}
    for review in reviews:
        rating_counts[review.rating] = rating_counts.get(review.rating, 0) + 1
    
    print("\n📈 Rating Distribution:")
    for rating in sorted(rating_counts.keys()):
        count = rating_counts[rating]
        percentage = (count / reviews.count()) * 100
        stars = "⭐" * rating
        print(f"   {stars} ({rating}): {count} reviews ({percentage:.1f}%)")
    
    # Category distribution
    category_counts = {}
    for review in reviews:
        category_counts[review.category] = category_counts.get(review.category, 0) + 1
    
    print("\n📋 Category Distribution:")
    for category, count in category_counts.items():
        percentage = (count / reviews.count()) * 100
        print(f"   {category}: {count} reviews ({percentage:.1f}%)")
    
    # Language distribution (check titles)
    persian_count = 0
    english_count = 0
    
    for review in reviews:
        # Simple check for Persian characters
        if any('\u0600' <= char <= '\u06FF' for char in review.title):
            persian_count += 1
        else:
            english_count += 1
    
    print("\n🌐 Language Distribution:")
    print(f"   Persian Reviews: {persian_count}")
    print(f"   English Reviews: {english_count}")
    
    # Review details
    print("\n📝 Review Details:")
    for i, review in enumerate(reviews[:5], 1):  # Show first 5 reviews
        print(f"   {i}. {review.title}")
        print(f"      Rating: {review.rating}⭐")
        print(f"      Category: {review.category}")
        print(f"      Verified: {'✅' if review.is_verified else '❌'}")
        print(f"      Helpful: {review.is_helpful} votes")
        print(f"      User: {review.user.username}")
        print(f"      Date: {review.created_at.strftime('%Y-%m-%d')}")
        print()
    
    # Helpful votes summary
    total_helpful = sum(review.is_helpful for review in reviews)
    print(f"📊 Total Helpful Votes: {total_helpful}")
    
    # Status summary
    status_counts = {}
    for review in reviews:
        status_counts[review.status] = status_counts.get(review.status, 0) + 1
    
    print("\n📋 Status Distribution:")
    for status, count in status_counts.items():
        percentage = (count / reviews.count()) * 100
        print(f"   {status}: {count} reviews ({percentage:.1f}%)")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 REVIEW VERIFICATION SUMMARY")
    print("=" * 60)
    
    checks = [
        ("Reviews Created", reviews.count() >= 5),
        ("Average Rating", average_rating >= 3.5),
        ("Verified Reviews", verified_count >= 5),
        ("Mixed Languages", persian_count > 0 and english_count > 0),
        ("Rating Range", min(rating_counts.keys()) <= 3 and max(rating_counts.keys()) >= 5),
        ("Multiple Categories", len(category_counts) >= 3),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    print(f"\n{'🎉 ALL CHECKS PASSED!' if all_passed else '⚠️ SOME CHECKS FAILED'}")
    
    if all_passed:
        print("\n✅ Tour X reviews are complete and ready!")
        print("   - Good mix of ratings (3-5 stars)")
        print("   - Persian and English content")
        print("   - Various categories covered")
        print("   - Verified reviews with helpful votes")
        print("   - Realistic average rating")
    
    return all_passed

if __name__ == "__main__":
    verify_tour_x_reviews()
