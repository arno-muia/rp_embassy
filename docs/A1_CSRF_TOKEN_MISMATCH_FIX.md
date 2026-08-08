# CSRF Token Mismatch — Root Cause & Fix

## 1. Root Cause

### Symptom
Django rejected login with:
```
CSRF token from the 'X-Csrftoken' HTTP header incorrect.
```

### Root Cause
In `backend/backend/apps/accounts/views.py`, the `csrf_token_view` endpoint returned
`get_token(request)` directly in the JSON response:

```python
return Response(
    {'csrfToken': get_token(request)},
    status=status.HTTP_200_OK,
)
```

`get_token()` **generates a new token on each call** (when no valid cookie exists).
If the frontend called `/api/auth/csrf-token` multiple times before a POST, each call
**rotated the `csrftoken` cookie**. The JSON body contained a *different* value than
what the browser stored in the cookie, causing:

```
cookie value  !==  X-CSRFToken header value
```

## 2. Code Evidence

### Before (mismatched)
**File:** `rpwebsite/RP/backend/backend/apps/accounts/views.py:152-163`
```python
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    return Response(
        {'csrfToken': get_token(request)},  # returns a NEW token each call
        status=status.HTTP_200_OK,
    )
```

**File:** `rpwebsite/RP/website/src/components/forms/LoginForm.astro:71-78`
```javascript
const csrfToken = await fetch("http://127.0.0.1:8000/api/auth/csrf-token", {
    credentials: "include",
    headers: { Accept: "application/json" },
})
    .then((r) => r.json())
    .then((d) => d.csrfToken)   // <-- stale JSON value
    .catch(() => null);
```

### After (consistent)
**File:** `rpwebsite/RP/backend/backend/apps/accounts/views.py:152-168`
```python
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    get_token(request)           # ensures cookie is set
    token = request.COOKIES.get('csrftoken', '')  # read from cookie
    return Response(
        {'csrfToken': token},
        status=status.HTTP_200_OK,
    )
```

**File:** `rpwebsite/RP/website/src/components/forms/LoginForm.astro:70-78`
```javascript
// Ensure csrftoken cookie exists
await fetch("http://127.0.0.1:8000/api/auth/csrf-token", {
    credentials: "include",
    headers: { Accept: "application/json" },
}).catch(() => {});

// Single source of truth: read the csrftoken cookie value directly.
const cookieMatch = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
const csrfToken = cookieMatch ? decodeURIComponent(cookieMatch[1]) : null;
```

## 3. Files Modified

| File | Change |
|------|--------|
| `rpwebsite/RP/backend/backend/apps/accounts/views.py` | `csrf_token_view` now reads `csrftoken` from `request.COOKIES` instead of `get_token()` return value |
| `rpwebsite/RP/website/src/lib/api.ts` | Added `getCsrfTokenFromCookie()` helper |
| `rpwebsite/RP/website/src/components/forms/LoginForm.astro` | Now reads CSRF token from cookie after ensuring it exists |
| `rpwebsite/RP/website/src/components/forms/ChangePasswordForm.astro` | Now reads CSRF token from cookie after ensuring it exists |
| `rpwebsite/RP/website/src/lib/auth.ts` | `getCsrfToken()` now reads from cookie, not JSON |

## 4. Before / After Flow

### Before (mismatched)
```
Frontend                          Backend
   |                                  |
   |-- GET /api/auth/csrf-token ----->|  (get_token returns T1)
   |                                  |-- Set-Cookie: csrftoken=T2
   |<-- {csrfToken: T1} -------------|
   |                                  |
   |-- GET /api/auth/csrf-token ----->|  (get_token returns T3)
   |                                  |-- Set-Cookie: csrftoken=T4
   |<-- {csrfToken: T3} -------------|
   |                                  |
   |-- POST /api/auth/login -------->|
   |   X-CSRFToken: T3                |
   |   Cookie: csrftoken=T4           |
   |                                  |-- 403 CSRF mismatch!
```

### After (consistent)
```
Frontend                          Backend
   |                                  |
   |-- GET /api/auth/csrf-token ----->|  (ensures cookie set)
   |                                  |-- Set-Cookie: csrftoken=T1
   |<-- {csrfToken: T1} -------------|
   |                                  |
   |-- POST /api/auth/login -------->|
   |   X-CSRFToken: T1                |
   |   Cookie: csrftoken=T1           |
   |                                  |-- 200 OK
```

## 5. Validation

The fix ensures:
- `document.cookie.match(/csrftoken=([^;]+)/)[1]` === value sent in `X-CSRFToken`
- Multiple calls to `/api/auth/csrf-token` cannot produce mismatched tokens
- The `csrftoken` cookie is the single source of truth
- If the cookie is absent, `null` is sent and Django will reject — this is correct behavior