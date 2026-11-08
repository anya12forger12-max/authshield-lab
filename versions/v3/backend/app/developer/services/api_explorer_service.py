"""API Explorer service."""

from __future__ import annotations

from app.developer.domain.entities.api_explorer import (
    ApiDocumentation,
    ApiEndpoint,
    ApiParameter,
    ApiSchema,
)


class ApiExplorerService:
    """Register, document, search, and validate API endpoints."""

    def __init__(self) -> None:
        self._endpoints: dict[str, ApiEndpoint] = {}
        self._schemas: dict[str, ApiSchema] = {}
        self._docs: dict[str, ApiDocumentation] = {}

    # -- Endpoint management -------------------------------------------------

    def register_endpoint(
        self,
        path: str,
        method: str = "GET",
        description: str = "",
        parameters: list[ApiParameter] | None = None,
        response_schema: dict | None = None,
        category: str = "general",
        version: str = "1.0",
        deprecated: bool = False,
        auth_required: bool = True,
    ) -> ApiEndpoint:
        """Register a new API endpoint."""
        endpoint = ApiEndpoint(
            path=path,
            method=method,
            description=description,
            parameters=parameters,
            response_schema=response_schema,
            category=category,
            version=version,
            deprecated=deprecated,
            auth_required=auth_required,
        )
        self._endpoints[endpoint.id] = endpoint
        return endpoint

    def get_endpoint(self, endpoint_id: str) -> ApiEndpoint | None:
        """Retrieve an endpoint by ID."""
        return self._endpoints.get(endpoint_id)

    def get_endpoint_by_path(self, path: str, method: str = "GET") -> ApiEndpoint | None:
        """Look up an endpoint by path and HTTP method."""
        for ep in self._endpoints.values():
            if ep.path == path and ep.method == method.upper():
                return ep
        return None

    def list_endpoints(self) -> list[ApiEndpoint]:
        """Return all registered endpoints."""
        return list(self._endpoints.values())

    def list_by_category(self, category: str) -> list[ApiEndpoint]:
        """Return endpoints filtered by category."""
        return [ep for ep in self._endpoints.values() if ep.category == category]

    def list_deprecated(self) -> list[ApiEndpoint]:
        """Return all deprecated endpoints."""
        return [ep for ep in self._endpoints.values() if ep.deprecated]

    def search_endpoints(self, query: str) -> list[ApiEndpoint]:
        """Search endpoints by path or description."""
        q = query.lower()
        return [
            ep
            for ep in self._endpoints.values()
            if q in ep.path.lower() or q in ep.description.lower()
        ]

    def update_endpoint(
        self,
        endpoint_id: str,
        description: str | None = None,
        category: str | None = None,
    ) -> ApiEndpoint | None:
        """Update mutable fields on an endpoint."""
        ep = self._endpoints.get(endpoint_id)
        if ep is None:
            return None
        if description is not None:
            ep.description = description
        if category is not None:
            ep.category = category
        return ep

    def deprecate_endpoint(self, endpoint_id: str) -> bool:
        """Mark an endpoint as deprecated."""
        ep = self._endpoints.get(endpoint_id)
        if ep is None:
            return False
        ep.deprecate()
        return True

    def delete_endpoint(self, endpoint_id: str) -> bool:
        """Remove an endpoint."""
        if endpoint_id in self._endpoints:
            del self._endpoints[endpoint_id]
            return True
        return False

    # -- Schema management ---------------------------------------------------

    def create_schema(
        self,
        name: str,
        properties: dict | None = None,
        required: list[str] | None = None,
        version: str = "1.0",
    ) -> ApiSchema:
        """Create a reusable API schema."""
        schema = ApiSchema(name=name, properties=properties, required=required, version=version)
        self._schemas[schema.id] = schema
        return schema

    def get_schema(self, schema_id: str) -> ApiSchema | None:
        """Retrieve a schema by ID."""
        return self._schemas.get(schema_id)

    def get_schema_by_name(self, name: str) -> ApiSchema | None:
        """Retrieve a schema by name."""
        for s in self._schemas.values():
            if s.name == name:
                return s
        return None

    def list_schemas(self) -> list[ApiSchema]:
        """Return all schemas."""
        return list(self._schemas.values())

    def update_schema(self, schema_id: str, properties: dict) -> ApiSchema | None:
        """Replace properties on a schema."""
        schema = self._schemas.get(schema_id)
        if schema is None:
            return None
        schema.properties = dict(properties)
        return schema

    def delete_schema(self, schema_id: str) -> bool:
        """Remove a schema."""
        if schema_id in self._schemas:
            del self._schemas[schema_id]
            return True
        return False

    # -- Documentation management --------------------------------------------

    def attach_documentation(
        self,
        endpoint_id: str,
        content: str,
        examples: list[dict] | None = None,
    ) -> ApiDocumentation | None:
        """Attach documentation to an endpoint."""
        if endpoint_id not in self._endpoints:
            return None
        existing = self.get_doc_by_endpoint(endpoint_id)
        if existing is not None:
            existing.append_content(content)
            return existing
        doc = ApiDocumentation(
            endpoint_id=endpoint_id,
            content=content,
            examples=examples,
        )
        self._docs[doc.id] = doc
        return doc

    def get_doc(self, doc_id: str) -> ApiDocumentation | None:
        """Retrieve a documentation record by ID."""
        return self._docs.get(doc_id)

    def get_doc_by_endpoint(self, endpoint_id: str) -> ApiDocumentation | None:
        """Retrieve documentation attached to a specific endpoint."""
        for doc in self._docs.values():
            if doc.endpoint_id == endpoint_id:
                return doc
        return None

    def add_example(
        self, doc_id: str, title: str, request: dict, response: dict
    ) -> bool:
        """Add an example to an existing documentation record."""
        doc = self._docs.get(doc_id)
        if doc is None:
            return False
        doc.add_example(title=title, request=request, response=response)
        return True

    def delete_doc(self, doc_id: str) -> bool:
        """Remove a documentation record."""
        if doc_id in self._docs:
            del self._docs[doc_id]
            return True
        return False

    # -- Validation ----------------------------------------------------------

    def validate_endpoint(self, endpoint_id: str) -> dict:
        """Run basic validation on a registered endpoint."""
        ep = self._endpoints.get(endpoint_id)
        if ep is None:
            return {"valid": False, "errors": ["Endpoint not found"]}
        errors: list[str] = []
        if not ep.path:
            errors.append("Path is required")
        if not ep.method:
            errors.append("Method is required")
        if not ep.path.startswith("/"):
            errors.append("Path must start with /")
        return {"valid": len(errors) == 0, "errors": errors}

    def get_api_summary(self) -> dict:
        """Return a high-level summary of all registered endpoints."""
        total = len(self._endpoints)
        deprecated = sum(1 for ep in self._endpoints.values() if ep.deprecated)
        categories: dict[str, int] = {}
        methods: dict[str, int] = {}
        for ep in self._endpoints.values():
            categories[ep.category] = categories.get(ep.category, 0) + 1
            methods[ep.method] = methods.get(ep.method, 0) + 1
        return {
            "total_endpoints": total,
            "deprecated": deprecated,
            "active": total - deprecated,
            "by_category": categories,
            "by_method": methods,
        }
