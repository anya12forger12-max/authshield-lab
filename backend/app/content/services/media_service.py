"""Media asset management service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.content import MediaAsset
from ..domain.events.content_events import MediaUploaded, AccessibilityReviewCompleted
from ..domain.interfaces.content_repository import MediaRepository
from ..validators.content_validator import ContentValidator


class MediaService:
    """Service for registering, searching, and validating media assets.

    Parameters
    ----------
    repo:
        Repository for media asset persistence.
    validator:
        Content validation rules.
    """

    def __init__(self, repo: MediaRepository, validator: ContentValidator | None = None) -> None:
        self._repo = repo
        self._validator = validator or ContentValidator()
        self._events: list[Any] = []

    def _record_event(self, event: Any) -> None:
        self._events.append(event)

    async def register_asset(
        self,
        title: str,
        media_type: str,
        uri: str,
        alt_text: str = "",
        caption: str = "",
        transcript: str = "",
        accessible: bool = True,
    ) -> MediaAsset:
        """Register a new media asset."""
        meta_result = self._validator.validate_media_metadata(
            {
                "title": title,
                "media_type": media_type,
                "uri": uri,
                "alt_text": alt_text,
            }
        )
        if not meta_result.is_valid:
            error_messages = [e.message for e in meta_result.errors]
            raise ValueError(f"Media validation failed: {'; '.join(error_messages)}")
        asset = MediaAsset(
            title=title,
            media_type=media_type,
            uri=uri,
            alt_text=alt_text,
            caption=caption,
            transcript=transcript,
            accessible=accessible,
        )
        await self._repo.save(asset)
        event = MediaUploaded(
            asset_id=asset.id,
            media_type=asset.media_type,
            title=asset.title,
            correlation_id=asset.id,
            message=f"Media asset '{asset.title}' registered ({asset.media_type}).",
        )
        self._record_event(event)
        return asset

    async def get_asset(self, asset_id: str) -> Optional[MediaAsset]:
        """Retrieve a media asset by ID."""
        return await self._repo.find_by_id(asset_id)

    async def list_assets(
        self, offset: int = 0, limit: int = 20
    ) -> list[MediaAsset]:
        """List all media assets with pagination."""
        return await self._repo.find_all(offset=offset, limit=limit)

    async def search_assets(self, query: str) -> list[MediaAsset]:
        """Search media assets by title or caption substring."""
        all_assets = await self._repo.find_all(offset=0, limit=10000)
        query_lower = query.lower()
        return [
            a
            for a in all_assets
            if query_lower in a.title.lower() or query_lower in a.caption.lower()
        ]

    async def categorize(self, media_type: str) -> dict[str, Any]:
        """Return a summary of assets grouped by the given media type."""
        assets = await self._repo.search_by_type(media_type)
        return {
            "media_type": media_type,
            "count": len(assets),
            "assets": [
                {
                    "id": a.id,
                    "title": a.title,
                    "uri": a.uri,
                    "accessible": a.accessible,
                }
                for a in assets
            ],
        }

    async def validate_accessibility(self, asset_id: str) -> dict[str, Any]:
        """Run accessibility checks on a media asset."""
        asset = await self._repo.find_by_id(asset_id)
        if asset is None:
            raise ValueError(f"Media asset {asset_id} not found.")
        issues: list[str] = []
        if asset.media_type == "image" and not asset.alt_text:
            issues.append("Missing alt_text for image asset.")
        if asset.media_type == "video" and not asset.transcript:
            issues.append("Missing transcript for video asset.")
        if asset.media_type == "audio" and not asset.transcript:
            issues.append("Missing transcript for audio asset.")
        if not asset.caption:
            issues.append("Missing caption.")
        passed = len(issues) == 0
        event = AccessibilityReviewCompleted(
            content_id=asset.id,
            content_type="media_asset",
            issues_found=len(issues),
            passed=passed,
            correlation_id=asset.id,
            message=f"Accessibility review for '{asset.title}': {'PASSED' if passed else f'{len(issues)} issues found'}.",
        )
        self._record_event(event)
        return {
            "asset_id": asset.id,
            "accessible": passed,
            "issues": issues,
            "issues_count": len(issues),
        }

    async def get_assets_by_type(self, media_type: str) -> list[MediaAsset]:
        """Return all assets of a specific media type."""
        return await self._repo.search_by_type(media_type)
