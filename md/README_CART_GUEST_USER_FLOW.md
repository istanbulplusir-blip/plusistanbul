Guest → Checkout → Login/Register flow

1. Guest adds items: stored in backend session cart via cookies (withCredentials=true).
2. When proceeding to checkout and redirected to login/register, after successful auth:
   - Frontend calls POST `/cart/merge/` with empty body. Backend merges previous session cart into user cart.
   - Frontend then reloads cart via GET `/cart/` and returns user to `/[locale]/cart`.
3. Guest vs User carts time limit: backend `CartItem.create_reservation()` sets `reservation_expires_at` and `Cart.clear_expired_items()` removes expired items on each cart fetch.

Implementation notes

- Frontend context exposes `mergeGuestCartIntoUser()` to be used in auth success handlers.
- Backend merge accepts missing `session_key` and uses current session by default.
