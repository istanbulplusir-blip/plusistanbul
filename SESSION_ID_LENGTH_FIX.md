# Session ID Length Bug Fix

## Problem

After implementing the guest cart merge fix, users were experiencing 500 errors when:
1. Trying to retrieve their cart after login (`GET /api/v1/cart/`)
2. Trying to merge guest cart with user cart (`POST /api/v1/cart/merge/`)

## Root Cause

The error was:
```
django.db.utils.DataError: value too long for type character varying(40)
```

The Cart model's `session_id` field is defined as `varchar(40)`, but the collision handling code was creating session IDs longer than 40 characters:

```python
# WRONG - Creates 41+ character strings
unique_session_id = f"{session_id}_{uuid.uuid4().hex[:8]}"
# Example: "exjplmvvptmb5981a2mno79rfq4qfvzh_b0c596d6" = 41 chars
```

## Solution

Fixed all 3 locations in `plusistanbul/backend/cart/models.py` where unique session IDs are generated:

```python
# CORRECT - Max 40 characters (31 + 1 + 8 = 40)
unique_session_id = f"{session_id[:31]}_{uuid.uuid4().hex[:8]}"
```

### Changes Made

1. **Line ~559** - Authenticated user cart creation with collision handling
2. **Line ~598** - Guest cart creation when user field exists
3. **Line ~609** - Guest cart creation on DoesNotExist exception

## Deployment

1. Built new backend image: `docker-compose -f docker-compose.production-secure.yml build backend`
2. Removed old container: `docker-compose -f docker-compose.production-secure.yml rm -f backend`
3. Started new container: `docker-compose -f docker-compose.production-secure.yml up -d backend`

## Testing

Users should now be able to:
- ✅ Add items to cart as guest
- ✅ Login with Google OAuth or OTP
- ✅ See their cart items after authentication
- ✅ Merge guest cart with user cart successfully

## Date

Fixed: October 25, 2025 (23:40 UTC)
