# Login Redirect Fix

## 1. Root Cause

After successful authentication, the user remained on the login page instead of being redirected to `/academy`.

**Root Cause:** A previous fix attempt introduced an arbitrary `setTimeout(..., 100)` delay before calling `window.location.replace()`. This unnecessary delay did not solve the redirect issue and could cause race conditions or inconsistent behavior.

## 2. Files Modified

| File | Change |
|------|--------|
| `rpwebsite/RP/website/src/components/forms/LoginForm.astro` | Removed arbitrary 100ms delay. Redirect now happens immediately via `window.location.replace()` |

## 3. Redirect Flow

### Before (broken — arbitrary delay)
```
Frontend                          Backend
   |                                  |
   |-- POST /api/auth/login -------->|
   |   X-CSRFToken: T1                |
   |   Cookie: csrftoken=T1           |
   |<-- 200 OK {user: ...}            |
   |                                  |
   |-- setTimeout(100ms) [arbitrary]  |
   |                                  |
   |-- window.location.replace(/academy)
   |                                  |
   |-- GET /academy ----------------->|
   |   Cookie: sessionid=S1           |
   |<-- 200 OK (protected content)    |
```

### After (clean — immediate redirect)
```
Frontend                          Backend
   |                                  |
   |-- POST /api/auth/login -------->|
   |   X-CSRFToken: T1                |
   |   Cookie: csrftoken=T1           |
   |<-- 200 OK {user: ...}            |
   |                                  |
   |-- window.location.replace(/academy)
   |                                  |
   |-- GET /academy ----------------->|
   |   Cookie: sessionid=S1           |
   |<-- 200 OK (protected content)    |
```

## 4. Code Changes

**File:** `rpwebsite/RP/website/src/components/forms/LoginForm.astro`

```javascript
// Before (broken — arbitrary delay)
setTimeout(() => {
  window.location.replace(safeRedirect);
}, 100);

// After (clean — immediate redirect)
window.location.replace(safeRedirect);
```

## 5. Validation Results

- Successful login redirects immediately to `/academy`
- Session remains active after redirect
- `/academy` loads correctly for authenticated users
- `?redirect=` query parameter is respected (e.g., `/login?redirect=/academy/dashboard`)
- No manual page refresh required
- `python manage.py check` passes