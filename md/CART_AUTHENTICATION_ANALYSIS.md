# Cart Authentication & Session Consistency Analysis

## Critical Issues Identified

### 1. **Inconsistent API Client Usage**

**Problem**: The frontend uses both centralized API client (`apiClient`) and direct `fetch` calls, leading to inconsistent authentication handling.

**Locations**:
- `frontend/lib/api/client.ts` - Centralized axios client with automatic token injection
- `frontend/lib/api/cart.ts` - Uses centralized client but requires manual token passing
- `frontend/app/[locale]/cart/page.tsx` - Uses direct fetch calls with manual token handling
- `frontend/app/[locale]/tours/[slug]/page.tsx` - Uses direct fetch calls with manual token handling

**Impact**: 
- Direct fetch calls bypass the centralized authentication interceptor
- Manual token handling is error-prone and inconsistent
- No automatic token refresh or error handling for direct fetch calls

### 2. **Race Condition in Cart Loading**

**Problem**: The `useCart` hook has a race condition between authentication state and cart loading.

**Location**: `frontend/lib/hooks/useCart.ts:84-87`
```typescript
useEffect(() => {
  setIsClient(true);
  loadCartFromBackend();
}, [isAuthenticated]);
```

**Issues**:
- `loadCartFromBackend()` is called immediately when `isAuthenticated` changes
- No dependency on `user` object, only `isAuthenticated` boolean
- The `AuthContext` may not have fully loaded the user data when this runs
- This can cause the cart to load before the user context is fully established

### 3. **Token Persistence Issues**

**Problem**: Token retrieval is inconsistent across components.

**Locations**:
- `frontend/app/[locale]/cart/page.tsx:67` - `localStorage.getItem('access_token')`
- `frontend/app/[locale]/tours/[slug]/page.tsx:360` - `localStorage.getItem('access_token')`
- `frontend/lib/hooks/useCart.ts:108` - `localStorage.getItem('access_token')`

**Issues**:
- No centralized token management
- No token validation or expiration checking
- No fallback mechanism when token is missing
- Direct localStorage access scattered throughout codebase

### 4. **Missing Error Handling for Authentication Failures**

**Problem**: When API calls fail due to authentication issues, the frontend doesn't handle them consistently.

**Locations**:
- `frontend/lib/api/client.ts:40-50` - Only handles 401 errors globally
- Individual components don't handle auth failures gracefully
- No automatic redirect to login on auth failures

### 5. **Inconsistent Cart State Management**

**Problem**: The cart state is managed both locally and on the backend, leading to synchronization issues.

**Location**: `frontend/lib/hooks/useCart.ts:175-180`
```typescript
useEffect(() => {
  if (isClient) {
    localStorage.setItem('cart', JSON.stringify({ items }));
  }
}, [items, isClient]);
```

**Issues**:
- Local cart state is saved to localStorage on every change
- This can overwrite backend data with stale local data
- No conflict resolution between local and backend cart states

### 6. **Missing Authentication State Synchronization**

**Problem**: The `AuthContext` doesn't verify token validity with the backend.

**Location**: `frontend/lib/contexts/AuthContext.tsx:25-45`
```typescript
const checkAuthStatus = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      setIsAuthenticated(true);
      // Token verification is commented out!
    }
  }
}
```

**Issues**:
- Token verification with backend is commented out
- No token expiration checking
- Stale tokens can cause authentication issues

## Recommended Fixes

### 1. **Centralize API Calls**

**Solution**: Use the centralized `apiClient` for all cart operations.

**Files to modify**:
- `frontend/app/[locale]/cart/page.tsx`
- `frontend/app/[locale]/tours/[slug]/page.tsx`
- `frontend/lib/hooks/useCart.ts`

### 2. **Fix Race Condition**

**Solution**: Add proper dependencies and loading states.

**Modification needed in `useCart.ts`**:
```typescript
useEffect(() => {
  setIsClient(true);
  if (isAuthenticated && user) {
    loadCartFromBackend();
  } else if (!isAuthenticated) {
    loadCartFromLocalStorage();
  }
}, [isAuthenticated, user]);
```

### 3. **Implement Token Management Service**

**Solution**: Create a centralized token management service.

**New file needed**: `frontend/lib/services/tokenService.ts`

### 4. **Add Authentication Error Handling**

**Solution**: Implement consistent error handling for auth failures.

**Modification needed**: Update `apiClient` interceptors and individual components.

### 5. **Fix Cart State Synchronization**

**Solution**: Implement proper cart state management with backend as source of truth.

**Modification needed**: Update `useCart` hook to prioritize backend data.

### 6. **Enable Token Verification**

**Solution**: Uncomment and implement token verification in `AuthContext`.

**Modification needed**: Update `checkAuthStatus` function in `AuthContext.tsx`.

## Immediate Action Items

1. **High Priority**: Fix the race condition in `useCart` hook
2. **High Priority**: Replace direct fetch calls with centralized `apiClient`
3. **Medium Priority**: Implement token verification in `AuthContext`
4. **Medium Priority**: Add proper error handling for auth failures
5. **Low Priority**: Create centralized token management service

## Testing Recommendations

1. Test cart operations immediately after login
2. Test cart operations after page refresh
3. Test cart operations with expired tokens
4. Test cart operations with network failures
5. Test cart operations with multiple browser tabs 