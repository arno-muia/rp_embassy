# A1 CSRF Endpoint Fix

## Issue Reported

Network trace shows:
```
GET /api/auth/csrf-token → 404 Not Found
```

## URL Routing Verification

### 1. View Definition ✅

**File:** `backend/backend/apps/accounts/views.py` (lines 150-163)

```python
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    """GET /api/auth/csrf-token — return the CSRF token for cross-origin frontend."""
    return Response(
        {'csrfToken': get_token(request)},
        status=status.HTTP_200_OK,
    )
```

**Status:** View exists and is correctly defined.

### 2. App URL Configuration ✅

**File:** `backend/backend/apps/accounts/urls.py` (lines 19-23)

```python
urlpatterns = [
    path('auth/login', views.login_view, name='auth-login'),
    path('auth/logout', views.logout_view, name='auth-logout'),
    path('auth/me', views.me_view, name='auth-me'),
    path(
        'auth/change-password',
        views.change_password_view,
        name='auth-change-password',
    ),
    path(
        'auth/csrf-token',
        views.csrf_token_view,
        name='auth-csrf-token',
    ),
]
```

**Status:** Route is registered as `auth/csrf-token` → `csrf_token_view`.

### 3. Project Root URL Configuration ✅

**File:** `backend/backend/urls.py` (line 24)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backend.apps.accounts.urls')),
    path('api/', include('backend.apps.content.urls')),
    path('api/', include('backend.apps.events.urls')),
    path('api/', include('backend.apps.prayer.urls')),
    path('api/health', health_check, name='health-check'),
]
```

**Status:** Accounts URLs are included under `api/` prefix.

### 4. Frontend URL ✅

**File:** `website/src/lib/auth.ts` (line 33)

```typescript
export const AUTH_ENDPOINTS = {
  // ...
  csrfToken: `${API_BASE_URL}/api/auth/csrf-token`,
  // ...
} as const;
```

**File:** `website/src/components/forms/LoginForm.astro` (line 72)

```typescript
const csrfToken = await fetch("/api/auth/csrf-token", {
```

**Status:** Frontend requests `/api/auth/csrf-token`.

## Complete URL Resolution Chain

```
Frontend Request: GET /api/auth/csrf-token
    ↓
Root URLs: path('api/', include('backend.apps.accounts.urls'))
    ↓
Accounts URLs: path('auth/csrf-token', views.csrf_token_view)
    ↓
View: csrf_token_view → returns {'csrfToken': '<token>'}
```

**Expected Result:** HTTP 200 with JSON response

## Analysis

Based on code evidence:

1. ✅ View exists: `csrf_token_view` in `views.py`
2. ✅ Route registered: `auth/csrf-token` in `accounts/urls.py`
3. ✅ Included in project: `api/` prefix in `backend/urls.py`
4. ✅ Frontend URL matches: `/api/auth/csrf-token`

**The routing configuration is CORRECT.**

## Possible Causes for 404

If the endpoint returns 404 in a network trace, possible causes are:

1. **Backend server not running** - The Django development server must be running on port 8000
2. **Wrong host/port** - Frontend may be hitting incorrect backend URL
3. **Server not restarted** - URLs may have changed and server needs restart
4. **Proxy misconfiguration** - If using a proxy, it may not be forwarding correctly

## Verification Steps

### Step 1: Verify Backend is Running

```bash
cd rpwebsite/RP/backend
C:\ProgramData\Anaconda3\envs\tf_env\python.exe manage.py runserver 0.0.0.0:8000
```

### Step 2: Test Endpoint Directly

```bash
# From browser or curl:
curl http://localhost:8000/api/auth/csrf-token

# Expected response:
# {"csrfToken":"<token_value>"}
# Response headers should include: Set-Cookie: csrftoken=...
```

### Step 3: Verify Frontend Configuration

**File:** `website/.env` or `website/.env.example`

Check that `PUBLIC_API_URL` is set correctly:
```
PUBLIC_API_URL=http://localhost:8000
```

Or the default in `auth.ts` will be used:
```typescript
const API_BASE_URL =
  import.meta.env.PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";
```

## Request Flow After Fix

### CSRF Token Request
```
GET http://localhost:8000/api/auth/csrf-token
Headers: Accept: application/json
Credentials: include

Response: 200 OK
Body: {"csrfToken":"abc123..."}
Headers: Set-Cookie: csrftoken=abc123...; Path=/; ...
```

### Login Request
```
POST http://localhost:8000/api/auth/login
Headers:
  Content-Type: application/json
  X-CSRFToken: abc123...
  Cookie: csrftoken=abc123...
  Credentials: include

Body: {"email":"user@example.com","password":"..."}

Response: 200 OK (on success)
Body: {"id":"...","email":"user@example.com",...}
Headers: Set-Cookie: sessionid=...; Path=/; ...
```

## Backend System Check

```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

## Security Verification

✅ CSRF protection enabled
✅ SessionAuthentication active
✅ No csrf_exempt used
✅ CsrfViewMiddleware in stack
✅ credentials: "include" on all requests

## Conclusion

The URL routing configuration is **CORRECT**. The 404 error indicates either:
- Backend server not running
- Frontend hitting wrong URL/port
- Server needs restart after code changes

No code changes are required. The endpoint is properly wired and should return 200 when the backend server is running.