"""ApiEndpoint, ApiParameter, ApiSchema, and ApiDocumentation entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


class ApiParameter:
    """Describes a single request parameter for an API endpoint."""

    def __init__(
        self,
        name: str = "",
        in_: str = "query",
        required: bool = False,
        type: str = "string",
        description: str = "",
        default: str = "",
    ) -> None:
        self.name: str = name
        self.in_: str = in_
        self.required: bool = required
        self.type: str = type
        self.description: str = description
        self.default: str = default

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "name": self.name,
            "in": self.in_,
            "required": self.required,
            "type": self.type,
            "description": self.description,
            "default": self.default,
        }


class ApiEndpoint:
    """Represents a single documented API endpoint."""

    def __init__(
        self,
        id: str | None = None,
        path: str = "",
        method: str = "GET",
        description: str = "",
        parameters: list[ApiParameter] | None = None,
        response_schema: dict | None = None,
        category: str = "general",
        version: str = "1.0",
        deprecated: bool = False,
        auth_required: bool = True,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.path: str = path
        self.method: str = method.upper()
        self.description: str = description
        self.parameters: list[ApiParameter] = parameters if parameters is not None else []
        self.response_schema: dict = response_schema if response_schema is not None else {}
        self.category: str = category
        self.version: str = version
        self.deprecated: bool = deprecated
        self.auth_required: bool = auth_required

    def add_parameter(self, param: ApiParameter) -> None:
        """Add a parameter definition to this endpoint."""
        self.parameters.append(param)

    def remove_parameter(self, name: str) -> None:
        """Remove a parameter by name."""
        self.parameters = [p for p in self.parameters if p.name != name]

    def get_parameter(self, name: str) -> ApiParameter | None:
        """Look up a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def required_parameters(self) -> list[ApiParameter]:
        """Return only the required parameters."""
        return [p for p in self.parameters if p.required]

    def deprecate(self) -> None:
        """Mark this endpoint as deprecated."""
        self.deprecated = True

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "path": self.path,
            "method": self.method,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "response_schema": dict(self.response_schema),
            "category": self.category,
            "version": self.version,
            "deprecated": self.deprecated,
            "auth_required": self.auth_required,
        }


class ApiSchema:
    """A reusable JSON-like schema definition for API payloads."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        properties: dict | None = None,
        required: list[str] | None = None,
        version: str = "1.0",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.properties: dict = properties if properties is not None else {}
        self.required: list[str] = required if required is not None else []
        self.version: str = version

    def add_property(self, name: str, schema: dict) -> None:
        """Register a property on this schema."""
        self.properties[name] = schema

    def remove_property(self, name: str) -> None:
        """Remove a property from this schema."""
        self.properties.pop(name, None)
        if name in self.required:
            self.required.remove(name)

    def mark_required(self, property_name: str) -> None:
        """Mark a property as required."""
        if property_name not in self.required:
            self.required.append(property_name)

    def unmark_required(self, property_name: str) -> None:
        """Remove a property from the required list."""
        if property_name in self.required:
            self.required.remove(property_name)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "properties": dict(self.properties),
            "required": list(self.required),
            "version": self.version,
        }


class ApiDocumentation:
    """Human-readable documentation attached to an API endpoint."""

    def __init__(
        self,
        id: str | None = None,
        endpoint_id: str = "",
        content: str = "",
        examples: list[dict] | None = None,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.endpoint_id: str = endpoint_id
        self.content: str = content
        self.examples: list[dict] = examples if examples is not None else []

    def append_content(self, text: str) -> None:
        """Append additional text to the documentation body."""
        if self.content:
            self.content += "\n\n" + text
        else:
            self.content = text

    def add_example(self, title: str, request: dict, response: dict) -> None:
        """Add a request/response example."""
        self.examples.append({
            "title": title,
            "request": request,
            "response": response,
        })

    def remove_example(self, title: str) -> None:
        """Remove an example by its title."""
        self.examples = [e for e in self.examples if e.get("title") != title]

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "endpoint_id": self.endpoint_id,
            "content": self.content,
            "examples": list(self.examples),
        }
