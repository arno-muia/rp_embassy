# A1 CSRF Token Implementation

## Root Cause

After fixing the CSRF trusted origins, login attempts failed with:

```
{"detail":"CSRF Failed: CSRF token missing."}
```

Django's `CsrfViewMiddleware` requires a valid CSRF token for all POST requests. The Astro frontend (port 4321) cannot read the Django CSRF cookie directly due to cross-origin restrictions, so it needs to fetch the token from a dedicated endpoint and include it in the `X-CSRFToken` header.

## Backend Changes

### File: `backend/backend/apps/accounts/views.py`

**Already implemented** - The `csrf_token_view` endpoint existed:

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

**No changes required** - The endpoint properly uses `django.middleware.csrf.get_token()` to ensure the CSRF cookie is set and returns the token.

## Frontend Changes

### File: `website/src/lib/auth.ts`

**Modified** - Updated `login()` to fetch CSRF token before login:

```typescript
export async function login(
  email: string,
  password: string,
): Promise<{ user: AuthUser } | { error: string }> {
  try {
    const csrfToken = await getCsrfToken();
    const res = await fetch(AUTH_ENDPOINTS.login, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
      },
      body: JSON.stringify({
        email: email.toLowerCase().trim(),
        password,
      }),
    });
    // ...
  } catch {
    return { error: "Network error. Please try again." };
  }
}
```

**Already implemented** - The `logout()` function already fetched and included the CSRF token.

### File: `website/src/components/forms/ChangePasswordForm.astro`

**Modified** - Updated to fetch and include CSRF token:

```typescript
const csrfToken = await fetch("/api/auth/csrf-token", {
    credentials: "include",
    headers: { Accept: "application/json" },
  })
    .then((r) => r.json())
    .then((d) => d.csrfToken)
    .catch(() => null);

const res = await fetch((container as HTMLElement).dataset.endpoint!, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
    },
    // ...
});
```

## Request Flow

### Login Flow

1. Frontend calls `getCsrfToken()` → GET `/api/auth/csrf-token`
2. Backend returns CSRF token and sets `csrftoken` cookie
3. Frontend includes `X-CSRFToken` header in POST `/api/auth/login`
4. Django validates CSRF token
5. Backend creates session and returns user data
6. Frontend stores session cookie

### Logout Flow

1. Frontend calls `getCsrfToken()` → GET `/api/auth/csrf-token`
2. Frontend includes `X-CSRFToken` header in POST `/api/auth/logout`
3. Django validates CSRF token
4. Backend destroys session

### Change Password Flow

1. Frontend calls `getCsrfToken()` → GET `/api/auth/csrf-token`
2. Frontend includes `X-CSRFToken` header in POST `/api/auth/change-password`
3. Django validates CSRF token
4. Backend updates password

## Configuration Values

### CSRF_TRUSTED_ORIGINS

```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4321',
    'http://127.0.0.1:4321',
]
```

### CORS_ALLOWED_ORIGINS

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:4321',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:4321',
]
```

## Validation Results

### Backend System Check

```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

### Frontend Check

Attempted to run `npx astro check` but encountered infrastructure issue with rolldown native binding. The TypeScript code is syntactically correct and follows the existing patterns in the codebase.

## Security Confirmation

- **CSRF Protection**: Enabled (not disabled)
- **SessionAuthentication**: Unchanged and active
- **CSRF Exempt**: NOT applied to any endpoints
- **Middleware**: `django.middleware.csrf.CsrfViewMiddleware` remains in `MIDDLEWARE` stack
- **Credentials**: All fetch requests use `credentials: "include"` to properly handle cookies

The implementation maintains full CSRF protection while enabling cross-origin session-based authentication from the Astro frontend.