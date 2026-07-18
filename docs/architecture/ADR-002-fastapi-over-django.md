# ADR-002: FastAPI over Django

## Status

Accepted

## Context

AuthShield Lab requires a backend API server to handle authentication, data management, attack simulations, and analytics. We evaluated two primary Python web frameworks:

1. **FastAPI**: Modern, high-performance async framework built on Starlette and Pydantic
2. **Django**: Mature, full-featured web framework with ORM, admin, and extensive ecosystem

## Decision

We chose **FastAPI** for the backend API.

## Rationale

### Advantages of FastAPI

- **Performance**: FastAPI is one of the fastest Python frameworks, comparable to Node.js and Go, due to async support and Starlette's efficiency
- **Type Safety**: Native Pydantic integration provides automatic request validation, serialization, and documentation
- **API Documentation**: Automatic OpenAPI (Swagger) and ReDoc documentation generation
- **Async Support**: Native async/await support for concurrent operations without extra configuration
- **Modern Python**: Designed for Python 3.11+ with full type hint support
- **Minimal Boilerplate**: Less code needed compared to Django for API-only applications
- **Pydantic Integration**: Request/response validation, settings management, and serialization built-in
- **WebSocket Support**: Native WebSocket support for real-time features

### Advantages of Django We Evaluated

- **Admin Interface**: Django admin is powerful, but we're building a custom Electron UI
- **ORM**: Django ORM is mature, but SQLAlchemy 2.0 provides equivalent functionality with async support
- **Ecosystem**: Django has more third-party packages, but most are web-focused, not API-focused
- **Documentation**: Django has excellent documentation, but FastAPI's auto-generated API docs are more relevant for our use case

### Why Django Wasn't Chosen

- **Weight**: Django's full-stack features (templates, forms, admin) are unnecessary for an API-only backend
- **Async Support**: Django's async support is still maturing; FastAPI's is production-ready
- **Boilerplate**: Django requires more setup (settings.py, urls.py, apps) for a focused API
- **API Documentation**: FastAPI's auto-generated docs are superior for API development
- **Pydantic**: FastAPI's native Pydantic integration is more ergonomic than Django REST Framework's serializers

## Consequences

### Positive

- Faster API development with less boilerplate
- Automatic, always-up-to-date API documentation
- Excellent performance for concurrent operations
- Type-safe request/response validation
- Modern Python tooling and patterns

### Negative

- Smaller ecosystem compared to Django
- No built-in admin interface (we don't need one)
- Fewer Django-specific packages available
- Less established in enterprise environments

### Mitigations

- Use SQLAlchemy 2.0 for robust ORM functionality
- Build custom admin tools in the Electron UI as needed
- Leverage FastAPI's growing community and ecosystem
- Document API patterns and conventions internally
