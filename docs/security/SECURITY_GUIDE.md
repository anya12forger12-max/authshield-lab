# Security Implementation Guide

This document describes the security architecture and implementation details of AuthShield Lab.

## Overview

AuthShield Lab is designed with security as a fundamental principle. The platform operates in a completely isolated local environment with no external network dependencies.

## Network Security

### Localhost-Only Binding

All network communication is restricted to the loopback interface (127.0.0.1). This is enforced at multiple levels:

**Application Level**:

```python
# backend/app/main.py
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Never 0.0.0.0
        port=settings.PORT,
        # ...
    )
```

**Middleware Level**:

```python
# backend/app/middleware/security.py
class LocalhostOnlyMiddleware:
    async def __call__(self, scope, receive, send):
        client = scope.get("client")
        if client and client[0] not in ("127.0.0.1", "::1", "localhost"):
            # Reject non-localhost connections
            response = JSONResponse(
                status_code=403,
                content={"error": "Access denied: localhost only"}
            )
            return await response(scope, receive, send)
        return await self.app(scope, receive, send)
```

**Configuration Level**:

```python
# backend/app/config/settings.py
class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    
    @validator("HOST")
    def validate_host(cls, v):
        allowed = {"127.0.0.1", "localhost", "::1"}
        if v not in allowed:
            raise ValueError(f"Host must be one of {allowed}")
        return v
```

### No External Connections

The application makes zero outbound network requests:

- No telemetry collection
- No analytics services
- No cloud API calls
- No CDN dependencies
- No phone-home mechanisms
- No update checks over the network

All assets are bundled locally and all functionality operates against local data.

### CORS Configuration

Cross-Origin Resource Sharing is restricted to local origins:

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Security Headers

The following security headers are applied:

```python
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

## Authentication

### Password Hashing

Passwords are hashed using bcrypt with a configurable work factor:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Work factor
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

**Key Properties**:
- Salt is automatically generated per-password (16 bytes)
- Work factor of 12 (configurable, minimum 10)
- bcrypt is resistant to rainbow table attacks
- Slow hashing defeats brute force attempts

### Password Policy

```python
class PasswordPolicy:
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    HISTORY_SIZE = 12
    
    @classmethod
    def validate(cls, password: str) -> list[str]:
        errors = []
        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters")
        if len(password) > cls.MAX_LENGTH:
            errors.append(f"Password must be at most {cls.MAX_LENGTH} characters")
        if cls.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            errors.append("Password must contain an uppercase letter")
        if cls.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            errors.append("Password must contain a lowercase letter")
        if cls.REQUIRE_DIGIT and not re.search(r"\d", password):
            errors.append("Password must contain a digit")
        if cls.REQUIRE_SPECIAL and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain a special character")
        return errors
```

### JWT Token Management

**Token Generation**:

```python
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE
    payload = {**data, "exp": expire, "type": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    expire = datetime.utcnow() + REFRESH_TOKEN_EXPIRE
    payload = {**data, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

**Token Validation**:

```python
from jose import JWTError

def verify_token(token: str, token_type: str = "access") -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None
```

**Token Security Properties**:
- Short-lived access tokens (15 minutes)
- Refresh tokens with rotation (7 days)
- Token type validation (access vs refresh)
- Device fingerprint binding
- Revocation support via token blacklist

### Session Management

```python
class SessionManager:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_session(self, user_id: int, device_info: dict) -> Session:
        # Invalidate existing sessions if single-session mode
        if settings.SINGLE_SESSION:
            await self.invalidate_all(user_id)
        
        # Create new session
        session = Session(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            device_fingerprint=hash_device(device_info),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow()
        )
        self.db.add(session)
        await self.db.commit()
        return session
    
    async def validate_session(self, token: str) -> bool:
        session = await self.db.query(Session).filter_by(token=token).first()
        if not session:
            return False
        if session.expires_at < datetime.utcnow():
            await self.invalidate(token)
            return False
        return True
    
    async def invalidate(self, token: str) -> None:
        await self.db.query(Session).filter_by(token=token).delete()
        await self.db.commit()
```

## Rate Limiting

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Remove expired requests
        self.requests[key] = [
            t for t in self.requests[key] if t > cutoff
        ]
        
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        self.requests[key].append(now)
        return True

# Per-endpoint limiters
login_limiter = RateLimiter(max_requests=5, window_seconds=60)
api_limiter = RateLimiter(max_requests=100, window_seconds=60)
```

### Account Lockout

```python
class AccountLockout:
    LOCKOUT_THRESHOLD = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    RESET_DURATION = timedelta(minutes=30)
    
    def __init__(self, db: Session):
        self.db = db
    
    async def check_and_record(self, user_id: int, success: bool) -> bool:
        """Returns True if login is allowed."""
        record = await self.db.query(LockoutRecord).filter_by(
            user_id=user_id
        ).first()
        
        if not record:
            record = LockoutRecord(user_id=user_id)
            self.db.add(record)
        
        # Check if currently locked out
        if record.locked_until and record.locked_until > datetime.utcnow():
            return False
        
        if success:
            # Reset on successful login
            record.failed_attempts = 0
            record.locked_until = None
        else:
            record.failed_attempts += 1
            record.last_failed = datetime.utcnow()
            
            if record.failed_attempts >= self.LOCKOUT_THRESHOLD:
                record.locked_until = datetime.utcnow() + self.LOCKOUT_DURATION
        
        await self.db.commit()
        return True
```

## Input Validation

### Pydantic Models

All inputs are validated using Pydantic:

```python
from pydantic import BaseModel, EmailStr, Field, validator

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    role: Role = Role.STUDENT
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator("name")
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-Z\s'-]+$", v):
            raise ValueError("Name contains invalid characters")
        return v.strip()
    
    @validator("password")
    def validate_password(cls, v):
        errors = PasswordPolicy.validate(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v
```

### SQL Injection Prevention

SQLAlchemy parameterized queries prevent SQL injection:

```python
# Safe - parameterized query
user = await db.query(User).filter(User.email == email).first()

# Unsafe - never do this
# user = await db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### XSS Prevention

React automatically escapes content in JSX:

```tsx
// Safe - React escapes automatically
<div>{userInput}</div>

// Safe - explicit escaping for rich content
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(richContent)}} />
```

### Content Security Policy

```python
CSP_DIRECTIVES = {
    "default-src": "'self'",
    "script-src": "'self'",
    "style-src": "'self' 'unsafe-inline'",
    "img-src": "'self' data:",
    "font-src": "'self'",
    "connect-src": "'self' ws://localhost:8000",
    "frame-ancestors": "'none'",
    "base-uri": "'self'",
    "form-action": "'self'",
}
```

## Data Encryption

### At Rest

Sensitive configuration values are encrypted:

```python
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

### Database Security

- SQLite database stored in application data directory
- Sensitive columns encrypted at the application layer
- WAL mode for better concurrency
- Regular integrity checks via PRAGMA

## Audit Logging

All significant actions are logged:

```python
class AuditLogger:
    def __init__(self, db: Session):
        self.db = db
    
    async def log(
        self,
        action: str,
        user_id: int,
        resource_type: str = None,
        resource_id: int = None,
        details: dict = None
    ) -> AuditEvent:
        event = AuditEvent(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            timestamp=datetime.utcnow(),
            ip_address=get_client_ip(),
            integrity_hash=self._compute_hash(action, user_id, timestamp)
        )
        self.db.add(event)
        await self.db.commit()
        return event
    
    def _compute_hash(self, *args) -> str:
        data = "|".join(str(a) for a in args)
        return hashlib.sha256(data.encode()).hexdigest()
```

### Audit Event Types

| Category | Events |
|----------|--------|
| Authentication | login, logout, login_failed, password_change, password_reset |
| User Management | user_created, user_updated, user_deactivated, role_changed |
| Session | session_created, session_expired, session_revoked |
| Attack | attack_started, attack_completed, attack_aborted |
| Defense | defense_triggered, defense_configured, rule_added |
| System | config_changed, backup_created, database_migrated |

## Rate Limiting Response

When rate limited, the API returns:

```json
{
    "error": "rate_limit_exceeded",
    "message": "Too many requests. Please try again later.",
    "retry_after": 45
}
```

With headers:

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705312800
```

## Security Checklist

### Before Deployment

- [ ] SECRET_KEY is a random 256-bit value
- [ ] Database is not accessible from external networks
- [ ] All CORS origins are localhost only
- [ ] Rate limiting is enabled
- [ ] Account lockout is configured
- [ ] Audit logging is active
- [ ] Password policy is enforced
- [ ] Session timeout is reasonable (15-30 minutes)
- [ ] Security headers are applied
- [ ] Input validation is comprehensive
- [ ] Error messages don't leak sensitive information

### Regular Maintenance

- [ ] Rotate SECRET_KEY periodically
- [ ] Review audit logs weekly
- [ ] Check for failed login patterns
- [ ] Update dependencies regularly
- [ ] Verify database integrity
- [ ] Test backup restoration
- [ ] Review user access levels
