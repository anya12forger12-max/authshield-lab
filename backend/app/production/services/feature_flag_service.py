"""Feature flag, configuration profiles, and API versioning service."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger

logger = get_logger("production.feature_flag_service")


@dataclass
class FeatureFlag:
    """A toggle for enabling or disabling features at runtime."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    enabled: bool = False
    rollout_percentage: float = 0.0
    allowed_environments: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConfigProfile:
    """A named set of configuration values for an environment."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    environment: str = "development"
    values: dict[str, Any] = field(default_factory=dict)
    is_active: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ApiVersion:
    """Represents a versioned API endpoint."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = ""
    base_path: str = ""
    status: str = "active"
    deprecated_at: Optional[datetime] = None
    sunset_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ExperimentalFeature:
    """A feature in experimental/preview status."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    flag_id: str = ""
    min_version: str = ""
    required_roles: list[str] = field(default_factory=list)
    status: str = "preview"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class FeatureFlagService:
    """Manages feature flags, config profiles, API versioning, and experimental features."""

    def __init__(self) -> None:
        self._flags: dict[str, FeatureFlag] = {}
        self._profiles: dict[str, ConfigProfile] = {}
        self._api_versions: dict[str, ApiVersion] = {}
        self._experimental: dict[str, ExperimentalFeature] = {}

    # ------------------------------------------------------------------
    # Feature Flags
    # ------------------------------------------------------------------

    async def create_flag(
        self,
        name: str,
        description: str = "",
        enabled: bool = False,
        rollout_percentage: float = 0.0,
        allowed_environments: Optional[list[str]] = None,
        allowed_roles: Optional[list[str]] = None,
    ) -> FeatureFlag:
        """Create a new feature flag."""
        flag = FeatureFlag(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            enabled=enabled,
            rollout_percentage=rollout_percentage,
            allowed_environments=allowed_environments or [],
            allowed_roles=allowed_roles or [],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._flags[flag.id] = flag
        logger.info("feature_flag_created", flag_id=flag.id, name=name)
        return flag

    async def get_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Retrieve a feature flag by ID."""
        return copy.deepcopy(self._flags.get(flag_id))

    async def get_flag_by_name(self, name: str) -> Optional[FeatureFlag]:
        """Look up a feature flag by name."""
        for flag in self._flags.values():
            if flag.name == name:
                return copy.deepcopy(flag)
        return None

    async def list_flags(self) -> list[FeatureFlag]:
        """List all feature flags."""
        return [copy.deepcopy(f) for f in self._flags.values()]

    async def update_flag(
        self, flag_id: str, data: dict[str, Any]
    ) -> Optional[FeatureFlag]:
        """Update fields on a feature flag."""
        flag = self._flags.get(flag_id)
        if flag is None:
            return None
        for key, value in data.items():
            if hasattr(flag, key):
                setattr(flag, key, value)
        flag.updated_at = datetime.now(timezone.utc)
        return copy.deepcopy(flag)

    async def toggle_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Toggle a feature flag on or off."""
        flag = self._flags.get(flag_id)
        if flag is None:
            return None
        flag.enabled = not flag.enabled
        flag.updated_at = datetime.now(timezone.utc)
        logger.info(
            "feature_flag_toggled",
            flag_id=flag_id,
            enabled=flag.enabled,
        )
        return copy.deepcopy(flag)

    async def is_enabled(
        self,
        name: str,
        environment: str = "development",
        role: str = "",
    ) -> bool:
        """Check if a feature flag is enabled for the given context."""
        flag = await self.get_flag_by_name(name)
        if flag is None or not flag.enabled:
            return False
        if flag.allowed_environments and environment not in flag.allowed_environments:
            return False
        if flag.allowed_roles and role not in flag.allowed_roles:
            return False
        return True

    async def delete_flag(self, flag_id: str) -> bool:
        """Remove a feature flag."""
        if flag_id in self._flags:
            del self._flags[flag_id]
            logger.info("feature_flag_deleted", flag_id=flag_id)
            return True
        return False

    # ------------------------------------------------------------------
    # Configuration Profiles
    # ------------------------------------------------------------------

    async def create_profile(
        self,
        name: str,
        environment: str = "development",
        values: Optional[dict[str, Any]] = None,
        is_active: bool = False,
    ) -> ConfigProfile:
        """Create a configuration profile."""
        profile = ConfigProfile(
            id=str(uuid.uuid4()),
            name=name,
            environment=environment,
            values=values or {},
            is_active=is_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._profiles[profile.id] = profile
        logger.info("config_profile_created", profile_id=profile.id, name=name)
        return profile

    async def get_profile(self, profile_id: str) -> Optional[ConfigProfile]:
        """Retrieve a configuration profile by ID."""
        return copy.deepcopy(self._profiles.get(profile_id))

    async def get_active_profile(
        self, environment: str = "development"
    ) -> Optional[ConfigProfile]:
        """Get the active profile for an environment."""
        for profile in self._profiles.values():
            if profile.environment == environment and profile.is_active:
                return copy.deepcopy(profile)
        return None

    async def list_profiles(
        self, environment: Optional[str] = None
    ) -> list[ConfigProfile]:
        """List all profiles, optionally filtered by environment."""
        profiles = list(self._profiles.values())
        if environment:
            profiles = [p for p in profiles if p.environment == environment]
        return [copy.deepcopy(p) for p in profiles]

    async def update_profile(
        self, profile_id: str, data: dict[str, Any]
    ) -> Optional[ConfigProfile]:
        """Update fields on a configuration profile."""
        profile = self._profiles.get(profile_id)
        if profile is None:
            return None
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.updated_at = datetime.now(timezone.utc)
        return copy.deepcopy(profile)

    async def set_active_profile(self, profile_id: str) -> Optional[ConfigProfile]:
        """Activate a profile, deactivating others for the same environment."""
        profile = self._profiles.get(profile_id)
        if profile is None:
            return None
        for p in self._profiles.values():
            if p.environment == profile.environment:
                p.is_active = False
        profile.is_active = True
        profile.updated_at = datetime.now(timezone.utc)
        return copy.deepcopy(profile)

    async def delete_profile(self, profile_id: str) -> bool:
        """Remove a configuration profile."""
        if profile_id in self._profiles:
            del self._profiles[profile_id]
            return True
        return False

    # ------------------------------------------------------------------
    # API Versioning
    # ------------------------------------------------------------------

    async def register_api_version(
        self,
        version: str,
        base_path: str,
        status: str = "active",
    ) -> ApiVersion:
        """Register a new API version."""
        api_version = ApiVersion(
            id=str(uuid.uuid4()),
            version=version,
            base_path=base_path,
            status=status,
            created_at=datetime.now(timezone.utc),
        )
        self._api_versions[api_version.id] = api_version
        logger.info("api_version_registered", version=version, base_path=base_path)
        return api_version

    async def get_api_version(self, version_id: str) -> Optional[ApiVersion]:
        """Retrieve an API version by ID."""
        return copy.deepcopy(self._api_versions.get(version_id))

    async def list_api_versions(self) -> list[ApiVersion]:
        """List all registered API versions."""
        return [copy.deepcopy(v) for v in self._api_versions.values()]

    async def deprecate_api_version(
        self, version_id: str
    ) -> Optional[ApiVersion]:
        """Mark an API version as deprecated."""
        api_version = self._api_versions.get(version_id)
        if api_version is None:
            return None
        api_version.status = "deprecated"
        api_version.deprecated_at = datetime.now(timezone.utc)
        return copy.deepcopy(api_version)

    async def sunset_api_version(
        self, version_id: str
    ) -> Optional[ApiVersion]:
        """Mark an API version as sunset (end-of-life)."""
        api_version = self._api_versions.get(version_id)
        if api_version is None:
            return None
        api_version.status = "sunset"
        api_version.sunset_at = datetime.now(timezone.utc)
        return copy.deepcopy(api_version)

    async def delete_api_version(self, version_id: str) -> bool:
        """Remove an API version."""
        if version_id in self._api_versions:
            del self._api_versions[version_id]
            return True
        return False

    # ------------------------------------------------------------------
    # Experimental Features
    # ------------------------------------------------------------------

    async def create_experimental_feature(
        self,
        name: str,
        description: str,
        flag_id: str = "",
        min_version: str = "",
        required_roles: Optional[list[str]] = None,
    ) -> ExperimentalFeature:
        """Register an experimental feature."""
        feature = ExperimentalFeature(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            flag_id=flag_id,
            min_version=min_version,
            required_roles=required_roles or [],
            status="preview",
            created_at=datetime.now(timezone.utc),
        )
        self._experimental[feature.id] = feature
        logger.info("experimental_feature_created", feature_id=feature.id, name=name)
        return feature

    async def get_experimental_feature(
        self, feature_id: str
    ) -> Optional[ExperimentalFeature]:
        """Retrieve an experimental feature by ID."""
        return copy.deepcopy(self._experimental.get(feature_id))

    async def list_experimental_features(self) -> list[ExperimentalFeature]:
        """List all experimental features."""
        return [copy.deepcopy(f) for f in self._experimental.values()]

    async def promote_experimental_feature(
        self, feature_id: str
    ) -> Optional[ExperimentalFeature]:
        """Promote an experimental feature to stable status."""
        feature = self._experimental.get(feature_id)
        if feature is None:
            return None
        feature.status = "stable"
        return copy.deepcopy(feature)

    async def archive_experimental_feature(
        self, feature_id: str
    ) -> Optional[ExperimentalFeature]:
        """Archive an experimental feature."""
        feature = self._experimental.get(feature_id)
        if feature is None:
            return None
        feature.status = "archived"
        return copy.deepcopy(feature)

    async def delete_experimental_feature(self, feature_id: str) -> bool:
        """Remove an experimental feature."""
        if feature_id in self._experimental:
            del self._experimental[feature_id]
            return True
        return False
