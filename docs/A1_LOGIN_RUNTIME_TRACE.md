# A1 Login Runtime Trace

> **Status:** Instrumentation added — awaiting runtime data
> **Date:** 2026-08-02
> **Scope:** Runtime diagnosis of login failure

---

## 1. Instrumentation Added

Temporary debug logging was added to `backend/apps/accounts/views.py::login_view` to capture:

1. Incoming email
2. Whether `User.objects.filter(email=email).exists()`
3. User primary key if found
4. Database name from `connection.settings_dict["NAME"]`
5. Result of `authenticate()`
6. `AUTH_USER_MODEL`
7. `AUTHENTICATION_BACKENDS`
8. Whether `login(request, user)` executes
9. Whether the response returned is 200 or 401

### Code Changes

```python
import logging
from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """POST /api/auth/login — authenticate and create a session."""
    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("=== LOGIN VIEW CALLED ===")
    logger.info("AUTH_USER_MODEL: %s", settings.AUTH_USER_MODEL)
    logger.info("AUTHENTICATION_BACKENDS: %s", settings.AUTHENTICATION_BACKENDS)
    logger.info("Database: %s", connection.settings_dict.get("NAME"))
    # END TEMP

    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("Incoming email: %s", email)
    user_exists = User.objects.filter(email=email).exists()
    logger.info("User.objects.filter(email=email).exists(): %s", user_exists)
    if user_exists:
        temp_user = User.objects.filter(email=email).first()
        logger.info("User PK if found: %s", temp_user.id if temp_user else None)
    # END TEMP

    user = authenticate(request, username=email, password=password)
    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("authenticate() result: %s", user)
    # END TEMP

    if user is None:
        # TEMP: Runtime trace logging — remove after diagnosis
        logger.info("Response: 401 UNAUTHORIZED")
        logger.info("=== LOGIN VIEW END ===")
        # END TEMP
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        # TEMP: Runtime trace logging — remove after diagnosis
        logger.info("Response: 403 FORBIDDEN (inactive)")
        logger.info("=== LOGIN VIEW END ===")
        # END TEMP
        return Response(
            {'error': 'This account is inactive.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    login(request, user)
    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("login(request, user) executed for user pk=%s", user.id)
    # END TEMP

    # Update last_login and reset failed attempts
    user.last_login = timezone.now()
    user.failed_login_attempts = 0
    user.save(update_fields=['last_login', 'failed_login_attempts'])

    _write_audit(user, AuditAction.LOGIN, request)

    # TEMP: Runtime trace logging — remove after diagnosis
    logger.info("Response: 200 OK")
    logger.info("=== LOGIN VIEW END ===")
    # END TEMP
    return Response(AuthUserSerializer(user).data, status=status.HTTP_200_OK)
```

---

## 2. How to Collect Runtime Trace

### Step 1: Ensure Django is Running

```bash
cd rpwebsite/RP/backend
C:\ProgramData\Anaconda3\envs\tf_env\python.exe manage.py runserver 127.0.0.1:8000
```

### Step 2: Ensure Frontend is Running

```bash
cd rpwebsite/RP/website
npm run dev
```

### Step 3: Attempt Login

1. Open browser to `http://localhost:4321/login`
2. Open Developer Tools → Network tab
3. Enter credentials and submit
4. Observe the request to `/api/auth/login`

### Step 4: Collect Django Logs

Check the Django console output. You should see log entries like:

```
=== LOGIN VIEW CALLED ===
AUTH_USER_MODEL: accounts.User
AUTHENTICATION_BACKENDS: ['django.contrib.auth.backends.ModelBackend']
Database: RP
Incoming email: user@example.com
User.objects.filter(email=email).exists(): True/False
User PK if found: 123
authenticate() result: <User: user@example.com> or None
Response: 200 OK or 401 UNAUTHORIZED
=== LOGIN VIEW END ===
```

### Step 5: Collect Browser Network Data

In Developer Tools → Network tab:
- Find the request to `/api/auth/login`
- Check **Status Code** (200, 401, etc.)
- Check **Response Headers** for `Set-Cookie`
- Check **Request Headers** for `Cookie`

---

## 3. Expected Log Patterns

### Pattern A: authenticate() returns None
```
Incoming email: user@example.com
User.objects.filter(email=email).exists(): True
User PK if found: 123
authenticate() result: None
Response: 401 UNAUTHORIZED
```
**Interpretation:** User exists but password is wrong, or backend is not checking password correctly.

### Pattern B: User not found in database
```
Incoming email: user@example.com
User.objects.filter(email=email).exists(): False
authenticate() result: None
Response: 401 UNAUTHORIZED
```
**Interpretation:** Email does not exist in database. Check database seeding or user creation.

### Pattern C: authenticate() succeeds but login fails
```
Incoming email: user@example.com
User.objects.filter(email=email).exists(): True
User PK if found: 123
authenticate() result: <User: user@example.com>
login(request, user) executed for user pk=123
Response: 200 OK
```
**Interpretation:** Backend succeeds. If frontend still shows error, issue is:
- Session cookie not stored (SameSite/CORS)
- Frontend not reading response correctly
- Redirect after login failing

### Pattern D: Wrong database
```
Database: wrong_db_name
```
**Interpretation:** Django is connecting to the wrong database. Check `settings.py` DATABASES config.

### Pattern E: Wrong AUTH_USER_MODEL or backends
```
AUTH_USER_MODEL: wrong.model
AUTHENTICATION_BACKENDS: ['wrong.backend']
```
**Interpretation:** Authentication configuration is incorrect. Check `settings.py`.

---

## 4. Next Steps After Log Collection

1. Copy the full Django console output for the login attempt
2. Copy the Network tab details (status, headers, cookies)
3. Compare against patterns above
4. Identify the exact failing step
5. Apply targeted fix
6. Remove temporary logging
7. Update this document with actual findings

---

## 5. Cleanup Instructions

After diagnosis is complete, remove all TEMP blocks from `login_view`:

```bash
# Remove these sections:
# - logger imports and setup
# - All lines between # TEMP and # END TEMP
# - Any unused imports (settings, connection)
```

Restore `views.py` to clean production state.

---

**Note:** This document is a placeholder until runtime data is collected. The actual root cause will be documented here after log analysis.