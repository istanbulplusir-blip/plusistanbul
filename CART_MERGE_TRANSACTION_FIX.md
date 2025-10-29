# Cart Merge Transaction Fix

## مشکل (Problem)

خطای 500 در `/api/v1/cart/merge/` به دلیل استفاده از `select_for_update()` خارج از transaction:

```
TransactionManagementError: select_for_update cannot be used outside of a transaction.
```

The 500 error in `/api/v1/cart/merge/` was caused by using `select_for_update()` outside of a transaction.

## علت ریشه‌ای (Root Cause)

در `merge_cart_view`، کد سعی می‌کرد از `select_for_update()` برای lock کردن cart objects استفاده کند، اما این عملیات خارج از یک atomic transaction انجام می‌شد:

```python
# ❌ WRONG - select_for_update outside transaction
user_cart = Cart.objects.select_for_update().get(id=user_cart.id)
session_cart = Cart.objects.select_for_update().get(session_id=session_key, user__isnull=True)
```

In `merge_cart_view`, the code tried to use `select_for_update()` to lock cart objects, but this operation was performed outside of an atomic transaction.

## راه‌حل (Solution)

تمام عملیات `select_for_update()` را در یک `transaction.atomic()` قرار دادیم:

```python
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def merge_cart_view(request):
    """Merge session cart with user cart."""
    from django.db import transaction
    
    # ... validation code ...
    
    # ✅ CORRECT - Wrap all select_for_update in atomic transaction
    with transaction.atomic():
        # Get and lock user cart
        user_cart = CartService.get_or_create_cart(session_id=session_key, user=user)
        user_cart = Cart.objects.select_for_update().get(id=user_cart.id)
        
        # Get and lock session cart
        session_cart = Cart.objects.select_for_update().get(session_id=session_key, user__isnull=True)
        
        # ... merge logic ...
        
        # Delete session cart
        session_cart.delete()
    
    return Response({...})
```

### تغییرات اعمال شده (Changes Applied)

1. ✅ اضافه کردن `from django.db import transaction` در ابتدای function
2. ✅ قرار دادن تمام عملیات database در `with transaction.atomic():`
3. ✅ حذف `transaction.atomic()` دوم که قبلاً برای merge items استفاده می‌شد
4. ✅ اصلاح indentation برای تمام کدهای داخل transaction

## مشکلات دیگر (Other Issues)

### 1. URL Redirect Issue

کاربر پس از login به `/en/en/checkout/` redirect می‌شود که 404 می‌دهد (دوبار `/en/`).

این مشکل در frontend است و نیاز به بررسی دارد:
- بررسی redirect logic در authentication flow
- بررسی URL construction در Next.js routing

### 2. Frontend Cart Context

Frontend باید بررسی شود که:
- ✅ Session ID به درستی ذخیره و ارسال می‌شود
- ✅ پس از merge، cart state به‌روز می‌شود
- ❌ Redirect به صفحه مناسب انجام می‌شود (نیاز به اصلاح)

## تست (Testing)

کاربران اکنون باید بتوانند:
- ✅ محصولات را به سبد اضافه کنند (guest)
- ✅ با Google OAuth یا OTP لاگین کنند
- ✅ سبد خرید merge شود بدون خطای 500
- ❌ به صفحه مناسب redirect شوند (نیاز به اصلاح frontend)

Users should now be able to:
- ✅ Add products to cart (as guest)
- ✅ Login via Google OAuth or OTP
- ✅ Cart merges without 500 error
- ❌ Redirect to appropriate page (needs frontend fix)

## تاریخ (Date)

Fixed: October 26, 2025 (00:17 UTC)
