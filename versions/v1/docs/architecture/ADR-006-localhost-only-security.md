# ADR-006: Localhost-Only Security Model

## Status

Accepted

## Context

AuthShield Lab is a cybersecurity training platform that simulates attack and defense scenarios. The platform handles:

- Simulated authentication credentials
- Attack simulation data
- User learning progress
- Audit logs

Since this is a training platform, we must ensure that no simulated attack data or user information is exposed to external networks.

## Decision

All network communication is restricted to localhost (127.0.0.1). The application makes zero external network connections.

## Rationale

### Security Benefits

- **Network Isolation**: No attack simulation traffic can leak to external networks
- **Data Sovereignty**: All data remains on the user's machine
- **No Telemetry**: No user data is collected or transmitted
- **Offline Operation**: Full functionality without internet connection
- **No Supply Chain Risk**: No external API calls means no risk of compromised third-party services
- **Compliance**: Meets strict data handling requirements for security training

### Training Environment Benefits

- **Realistic Simulations**: Attack simulations can be run without affecting real systems
- **Safe Environment**: Users can practice without risk to production systems
- **Predictable Behavior**: No network latency or external service dependencies
- **Reproducible Results**: Same results regardless of network conditions

### Why External Connections Were Considered

- **Auto-Updates**: Could check for updates externally, but adds complexity and attack surface
- **Telemetry**: Could collect usage data, but conflicts with privacy requirements
- **Cloud Sync**: Could sync data across devices, but conflicts with isolation requirements
- **External APIs**: Could integrate with threat intelligence feeds, but adds dependency

## Implementation

### Backend Binding

```python
# Always bind to localhost only
uvicorn.run(
    "app.main:app",
    host="127.0.0.1",  # Never 0.0.0.0
    port=8000,
)
```

### Configuration Validation

```python
from pydantic import validator

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    
    @validator("HOST")
    def validate_host(cls, v):
        allowed = {"127.0.0.1", "localhost", "::1"}
        if v not in allowed:
            raise ValueError(
                f"Host must be one of {allowed}. "
                "External binding is not allowed for security reasons."
            )
        return v
```

### Middleware Enforcement

```python
class LocalhostOnlyMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            client = scope.get("client", ("", 0))
            if client[0] not in ("127.0.0.1", "::1", ""):
                response = JSONResponse(
                    status_code=403,
                    content={"error": "Access denied: localhost only"}
                )
                return await response(scope, receive, send)
        return await self.app(scope, receive, send)
```

### CORS Restriction

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Electron Configuration

```typescript
// Electron main process - no external navigation
mainWindow.webContents.on('will-navigate', (event, url) => {
  if (!url.startsWith('http://localhost')) {
    event.preventDefault();
  }
});

// Block external window creation
mainWindow.webContents.setWindowOpenHandler(({ url }) => {
  if (url.startsWith('http://localhost')) {
    return { action: 'allow' };
  }
  return { action: 'deny' };
});
```

## Consequences

### Positive

- Complete network isolation ensures security training data stays local
- No external attack surface from network connections
- Full offline functionality
- Simple deployment with no network configuration
- User privacy preserved by default

### Negative

- No automatic updates (must be handled via separate mechanism)
- No cloud sync or multi-device support
- No integration with external threat intelligence feeds
- Larger initial download without CDN assets

### Mitigations

- Provide manual update mechanism via GitHub releases
- Support local file import/export for data portability
- Allow manual threat feed import from local files
- Bundle all assets locally for offline operation

## Consequences for Development

- All API testing uses localhost URLs
- No external service mocking needed in tests
- CORS debugging simplified with known origins
- Network-related issues are always local
