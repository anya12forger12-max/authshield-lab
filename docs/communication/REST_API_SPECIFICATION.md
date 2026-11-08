# REST API Specification

## Document Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | Authoritative |
| Last Updated | 2026-07-19 |
| Owner | Architecture Team |
| Classification | Internal |

---

## 1. Overview

AuthShield Lab exposes an optional local REST API for advanced integration scenarios. This API is disabled by default and must be explicitly enabled by an administrator. When enabled, it binds exclusively to `localhost` (127.0.0.1) to prevent external network access.

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| Localhost Only | API binds to 127.0.0.1; no external network exposure |
| Disabled by Default | Must be explicitly enabled in configuration |
| Admin Only | All endpoints require admin authentication |
| RESTful | Standard REST conventions (resources, HTTP methods, status codes) |
| Self-Documenting | OpenAPI 3.1 specification auto-generated from code |
| RFC 7807 Errors | Problem Details format for all error responses |
| Cursor Pagination | Efficient pagination using cursors, not offsets |

### 1.2 Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (auto-generates OpenAPI) |
| Validation | Pydantic v2 |
| Documentation | Swagger UI + ReDoc |
| Authentication | Bearer token (local generation) |
| CORS | Restricted to localhost origins |

---

## 2. Authentication

### 2.1 Local Token-Based Authentication

The REST API uses bearer token authentication. Tokens are generated locally and stored securely.

**Token Generation:**

```python
# Tokens are generated via the admin interface
# Format: Random 256-bit token, hex-encoded
# Example: a1b2c3d4e5f6... (64 hex characters)
```

**Token Usage:**

```http
GET /api/v1/users HTTP/1.1
Host: localhost:8000
Authorization: Bearer <token>
```

**Token Lifecycle:**

| Property | Value |
|----------|-------|
| Length | 256 bits (64 hex characters) |
| Expiration | Configurable (default: 24 hours) |
| Storage | Encrypted in platform configuration |
| Revocation | Supported via admin endpoint |
| Rotation | Manual; automatic rotation optional |

### 2.2 Token Validation Flow

```
1. Receive request with Authorization header
2. Extract bearer token
3. Look up token in secure store
4. Check expiration
5. Check revocation status
6. Load associated admin role
7. Attach user context to request
8. Proceed to endpoint handler
```

### 2.3 Authentication Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 401 | `AUTH-AUTH-001` | Missing or malformed Authorization header |
| 401 | `AUTH-AUTH-004` | Token expired |
| 401 | `AUTH-AUTH-005` | Token revoked |
| 401 | `AUTH-AUTH-006` | Token invalid |

---

## 3. Authorization

### 3.1 Admin Role Required

All REST API endpoints require the `admin` role. Non-admin users cannot access the REST API even if they have valid session tokens from the main application.

### 3.2 Authorization Header Format

```
Authorization: Bearer <api-token>
```

---

## 4. Versioning

### 4.1 URL-Based Versioning

All API endpoints are versioned using URL path prefix:

```
/api/v1/{resource}
/api/v2/{resource}
```

### 4.2 Version Lifecycle

| Phase | Duration | Description |
|-------|----------|-------------|
| Current | Ongoing | Actively maintained and recommended |
| Deprecated | 6 months | Still functional, warnings logged |
| Sunset | 3 months | Returns deprecation headers, functionality limited |
| Removed | After sunset | Returns 410 Gone |

### 4.3 Deprecation Headers

Deprecated endpoints include these response headers:

```http
Deprecation: Sat, 01 Jan 2027 00:00:00 GMT
Sunset: Mon, 01 Jul 2027 00:00:00 GMT
Link: </api/v2/resource>; rel="successor-version"
```

---

## 5. Resource Naming

### 5.1 Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Resources | Plural nouns | `/api/v1/users`, `/api/v1/courses` |
| Sub-resources | Nested under parent | `/api/v1/courses/{id}/lessons` |
| Actions | Not as resources | Use POST with action field |
| IDs | UUIDs in path | `/api/v1/users/550e8400-e29b-41d4-a716-446655440000` |
| Query params | snake_case | `?page_size=20&sort=-created_at` |
| Headers | Title-Case | `X-Request-ID` |

### 5.2 HTTP Method Mapping

| Method | Purpose | Idempotent | Request Body |
|--------|---------|------------|-------------|
| `GET` | Read resource(s) | Yes | No |
| `POST` | Create resource | No | Yes |
| `PUT` | Replace resource | Yes | Yes |
| `PATCH` | Partial update | Yes | Yes |
| `DELETE` | Remove resource | Yes | No |

### 5.3 Resource URL Patterns

```
/api/v1/users                        GET (list), POST (create)
/api/v1/users/{id}                   GET (read), PUT (replace), PATCH (update), DELETE
/api/v1/users/{id}/sessions          GET (list), DELETE (revoke all)
/api/v1/users/{id}/sessions/{sid}    GET (read), DELETE (revoke)
/api/v1/courses                      GET (list), POST (create)
/api/v1/courses/{id}                 GET (read), PUT (replace), PATCH (update), DELETE
/api/v1/courses/{id}/lessons         GET (list), POST (create)
/api/v1/courses/{id}/lessons/{lid}   GET (read), PUT (replace), PATCH (update), DELETE
/api/v1/courses/{id}/publish         POST (action)
/api/v1/courses/{id}/archive         POST (action)
/api/v1/assessments                  GET (list)
/api/v1/assessments/{id}             GET (read)
/api/v1/assessments/{id}/results     GET (list)
/api/v1/certificates                 GET (list)
/api/v1/certificates/{id}            GET (read)
/api/v1/plugins                      GET (list)
/api/v1/plugins/{id}                 GET (read), DELETE (uninstall)
/api/v1/plugins/{id}/enable          POST (action)
/api/v1/plugins/{id}/disable         POST (action)
/api/v1/config                       GET (list), PUT (replace all), PATCH (update)
/api/v1/config/{key}                 GET (read), PUT (replace), DELETE (reset)
/api/v1/audit-logs                   GET (list)
/api/v1/backups                      GET (list), POST (create)
/api/v1/backups/{id}                 GET (read), POST (restore), DELETE
/api/v1/analytics/dashboard          GET (read)
/api/v1/analytics/metrics            GET (list)
/api/v1/reports                      GET (list)
/api/v1/reports/{id}                 GET (read)
/api/v1/reports/generate             POST (action)
/api/v1/notifications                GET (list)
/api/v1/diagnostics                  GET (read)
/api/v1/diagnostics/run              POST (action)
/api/v1/health                       GET (health check)
/api/v1/openapi.json                 GET (OpenAPI spec)
```

---

## 6. Error Handling

### 6.1 RFC 7807 Problem Details

All error responses follow the RFC 7807 format:

```json
{
  "type": "https://authshield.lab/errors/authorization",
  "title": "Forbidden",
  "status": 403,
  "detail": "Insufficient permissions to access this resource",
  "instance": "/api/v1/users/550e8400-e29b-41d4-a716-446655440000",
  "code": "AUTHZ-AUTH-001",
  "correlation_id": "req-abc-123",
  "timestamp": "2026-07-19T12:00:00Z"
}
```

### 6.2 Error Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | URI | Yes | URI reference identifying the error type |
| `title` | string | Yes | Short human-readable error title |
| `status` | integer | Yes | HTTP status code |
| `detail` | string | Yes | Human-readable error description |
| `instance` | URI | Yes | URI reference identifying the specific occurrence |
| `code` | string | Yes | Application error code (MODULE-CATEGORY-NNN) |
| `correlation_id` | string | Yes | Request correlation ID |
| `timestamp` | string | Yes | ISO 8601 timestamp |
| `errors` | array | No | Validation error details |
| `retry_after` | number | No | Seconds to wait before retrying |

### 6.3 HTTP Status Code Mapping

| Status | Meaning | When Used |
|--------|---------|-----------|
| 200 | OK | Successful read/update |
| 201 | Created | Successful resource creation |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Authentication required/failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource state conflict |
| 410 | Gone | Resource permanently removed |
| 422 | Unprocessable Entity | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## 7. Pagination

### 7.1 Cursor-Based Pagination

All list endpoints use cursor-based pagination for efficient, consistent traversal.

**Request Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cursor` | string | null | Pagination cursor from previous response |
| `page_size` | integer | 20 | Items per page (1-100) |

**Response Format:**

```json
{
  "items": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6IjU1MGU4NDAw...",
    "has_more": true,
    "page_size": 20,
    "total_count": 150
  }
}
```

### 7.2 Link Headers

Responses include Link headers for discoverability:

```http
Link: </api/v1/users?cursor=eyJpZCI6IjU1MGU4NDAw...&page_size=20>; rel="next"
Link: </api/v1/users?page_size=20>; rel="first"
```

### 7.3 Pagination Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `next_cursor` | string \| null | Cursor for next page; null if no more pages |
| `has_more` | boolean | Whether more pages exist |
| `page_size` | integer | Requested page size |
| `total_count` | integer | Total matching items (optional, expensive for large datasets) |

---

## 8. Filtering

### 8.1 Query Parameter Filtering

Resources support filtering via query parameters:

```
GET /api/v1/users?role=admin&status=active&created_after=2026-01-01
GET /api/v1/courses?category=cybersecurity&difficulty=intermediate&published=true
```

### 8.2 Filter Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Equals | `field=value` | `?role=admin` |
| Not equals | `field!=value` | `?status!=archived` |
| Greater than | `field>value` | `?score>80` |
| Less than | `field<value` | `?created_at<2026-06-01` |
| Contains | `field~value` | `?title~security` |
| In | `field=val1,val2` | `?status=active,pending` |
| Date range | `field_after=X&field_before=Y` | `?created_after=2026-01-01&created_before=2026-06-30` |

---

## 9. Sorting

### 9.1 Sort Parameter

```
GET /api/v1/users?sort=created_at          # Ascending
GET /api/v1/users?sort=-created_at         # Descending (prefix with -)
GET /api/v1/users?sort=name,-created_at    # Multiple sort fields
```

### 9.2 Sortable Fields

Each resource documents its sortable fields. Default sort is typically by `created_at` descending.

---

## 10. Rate Limiting

### 10.1 Configuration

Rate limiting is configurable per admin token:

| Setting | Default | Description |
|---------|---------|-------------|
| `rate_limit.enabled` | `false` | Enable/disable rate limiting |
| `rate_limit.requests_per_second` | 100 | Maximum requests per second |
| `rate_limit.burst_size` | 200 | Maximum burst size |
| `rate_limit.window_seconds` | 60 | Sliding window size |

### 10.2 Rate Limit Headers

When rate limiting is enabled:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1696000000
Retry-After: 1
```

### 10.3 Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 1

{
  "type": "https://authshield.lab/errors/rate-limit",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Retry after 1 seconds.",
  "retry_after": 1,
  "code": "SYS-RATE-001"
}
```

---

## 11. OpenAPI Specification

### 11.1 Auto-Generated

The OpenAPI 3.1 specification is auto-generated from FastAPI route definitions and Pydantic models.

### 11.2 Access Points

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/openapi.json` | Raw OpenAPI JSON specification |
| `GET /api/v1/docs` | Swagger UI interactive documentation |
| `GET /api/v1/redoc` | ReDoc alternative documentation |

### 11.3 Specification Structure

```yaml
openapi: 3.1.0
info:
  title: AuthShield Lab REST API
  version: 1.0.0
  description: Local REST API for AuthShield Lab platform administration
  contact:
    name: AuthShield Lab Team
servers:
  - url: http://localhost:8000/api/v1
    description: Local development server
security:
  - BearerAuth: []
paths:
  /users:
    get:
      summary: List all users
      tags: [Users]
      parameters:
        - $ref: '#/components/parameters/Cursor'
        - $ref: '#/components/parameters/PageSize'
        - $ref: '#/components/parameters/Sort'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        username:
          type: string
        email:
          type: string
          format: email
        roles:
          type: array
          items:
            type: string
        created_at:
          type: string
          format: date-time
```

---

## 12. Security Controls

### 12.1 Network Binding

| Control | Configuration |
|---------|--------------|
| Bind Address | `127.0.0.1` only (configurable) |
| Port | `8000` (configurable) |
| TLS | Disabled (localhost only) |
| CORS | `http://localhost:*` origins only |

### 12.2 CORS Configuration

```python
CORS_SETTINGS = {
    "allow_origins": ["http://localhost:*"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
    "allow_headers": ["Authorization", "Content-Type", "X-Request-ID"],
    "expose_headers": ["X-Request-ID", "X-RateLimit-*"],
    "max_age": 600,
}
```

### 12.3 Security Headers

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
```

### 12.4 Request Validation

| Check | Description |
|-------|-------------|
| Content-Type | Must be `application/json` for request bodies |
| Content-Length | Maximum 10 MB |
| Request ID | Optional `X-Request-ID` header; generated if absent |
| Body Schema | Validated against Pydantic models |
| Path Parameters | Validated (UUID format, integer ranges) |
| Query Parameters | Validated (types, ranges) |

---

## 13. Endpoints by Module

### 13.1 Authentication Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/tokens` | Generate a new API token |
| DELETE | `/api/v1/auth/tokens/{id}` | Revoke an API token |
| GET | `/api/v1/auth/tokens` | List active tokens |

### 13.2 Users Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users` | List users |
| POST | `/api/v1/users` | Create user |
| GET | `/api/v1/users/{id}` | Get user |
| PUT | `/api/v1/users/{id}` | Replace user |
| PATCH | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |

### 13.3 Courses Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/courses` | List courses |
| POST | `/api/v1/courses` | Create course |
| GET | `/api/v1/courses/{id}` | Get course |
| PUT | `/api/v1/courses/{id}` | Replace course |
| PATCH | `/api/v1/courses/{id}` | Update course |
| DELETE | `/api/v1/courses/{id}` | Delete course |
| POST | `/api/v1/courses/{id}/publish` | Publish course |
| POST | `/api/v1/courses/{id}/archive` | Archive course |
| GET | `/api/v1/courses/{id}/lessons` | List lessons |
| POST | `/api/v1/courses/{id}/lessons` | Create lesson |

### 13.4 Assessments Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/assessments` | List assessments |
| GET | `/api/v1/assessments/{id}` | Get assessment |
| GET | `/api/v1/assessments/{id}/results` | List assessment results |

### 13.5 Certificates Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/certificates` | List certificates |
| GET | `/api/v1/certificates/{id}` | Get certificate |

### 13.6 Plugins Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/plugins` | List plugins |
| GET | `/api/v1/plugins/{id}` | Get plugin |
| POST | `/api/v1/plugins/{id}/enable` | Enable plugin |
| POST | `/api/v1/plugins/{id}/disable` | Disable plugin |
| DELETE | `/api/v1/plugins/{id}` | Uninstall plugin |

### 13.7 Configuration Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/config` | List configuration |
| GET | `/api/v1/config/{key}` | Get configuration value |
| PUT | `/api/v1/config/{key}` | Set configuration value |
| PATCH | `/api/v1/config` | Batch update configuration |
| DELETE | `/api/v1/config/{key}` | Reset configuration |

### 13.8 Audit Logs Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audit-logs` | Query audit logs |

### 13.9 Backups Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/backups` | List backups |
| POST | `/api/v1/backups` | Create backup |
| GET | `/api/v1/backups/{id}` | Get backup info |
| POST | `/api/v1/backups/{id}/restore` | Restore backup |
| DELETE | `/api/v1/backups/{id}` | Delete backup |

### 13.10 Analytics Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/dashboard` | Get dashboard data |
| GET | `/api/v1/analytics/metrics` | List metrics |

### 13.11 Reports Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/reports` | List reports |
| GET | `/api/v1/reports/{id}` | Get report |
| POST | `/api/v1/reports/generate` | Generate report |

### 13.12 Notifications Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications` | List notifications |

### 13.13 Diagnostics Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/diagnostics` | Get diagnostic info |
| POST | `/api/v1/diagnostics/run` | Run diagnostics |

### 13.14 System Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/openapi.json` | OpenAPI specification |
| GET | `/api/v1/docs` | Swagger UI |
| GET | `/api/v1/redoc` | ReDoc documentation |

---

## 14. Health Check Endpoint

### 14.1 Response Format

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "services": {
    "database": { "status": "healthy", "latency_ms": 2 },
    "event_bus": { "status": "healthy", "latency_ms": 0.5 },
    "authentication": { "status": "healthy", "latency_ms": 1 },
    "authorization": { "status": "healthy", "latency_ms": 1 },
    "plugin_runtime": { "status": "healthy", "latency_ms": 3 }
  },
  "checked_at": "2026-07-19T12:00:00Z"
}
```

### 14.2 Health Status Values

| Status | Meaning |
|--------|---------|
| `healthy` | All services operational |
| `degraded` | One or more services degraded |
| `unhealthy` | Critical service unavailable |

---

## 15. Example Request/Response

### 15.1 List Courses

**Request:**

```http
GET /api/v1/courses?category=cybersecurity&sort=-published_at&page_size=5 HTTP/1.1
Host: localhost:8000
Authorization: Bearer abc123...
Content-Type: application/json
```

**Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: req-abc-123
Link: </api/v1/courses?cursor=eyJpZCI6IjU1MGU4NDAw...&page_size=5&category=cybersecurity&sort=-published_at>; rel="next"

{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Network Security Fundamentals",
      "description": "Introduction to network security concepts",
      "category": "cybersecurity",
      "difficulty_level": "beginner",
      "status": "published",
      "lesson_count": 12,
      "enrollment_count": 45,
      "created_at": "2026-01-15T10:30:00Z",
      "published_at": "2026-01-20T14:00:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6IjU1MGU4NDAw...",
    "has_more": true,
    "page_size": 5,
    "total_count": 23
  }
}
```

### 15.2 Error Response

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
X-Request-ID: req-def-456

{
  "type": "https://authshield.lab/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "Course with ID 'invalid-id' was not found",
  "instance": "/api/v1/courses/invalid-id",
  "code": "COURSE-VAL-010",
  "correlation_id": "req-def-456",
  "timestamp": "2026-07-19T12:00:00Z"
}
```
