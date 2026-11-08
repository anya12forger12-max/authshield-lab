"""Multimedia service — asset management and validation."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..domain.entities.multimedia import (
    AssetCollection,
    AssetType,
    AssetValidationResult,
    MultimediaAsset,
)
from ..domain.interfaces.content_studio_interfaces import (
    IAssetCollectionRepository,
    IMultimediaAssetRepository,
)

logger = logging.getLogger(__name__)


class MultimediaService:
    """Service for managing multimedia assets and collections."""

    def __init__(
        self,
        asset_repo: IMultimediaAssetRepository,
        collection_repo: IAssetCollectionRepository,
    ) -> None:
        self._asset_repo = asset_repo
        self._collection_repo = collection_repo

    def create_asset(self, data: dict[str, Any]) -> dict[str, Any]:
        asset = MultimediaAsset(
            name=data.get("name", ""),
            asset_type=AssetType(data.get("asset_type", "image")),
            description=data.get("description", ""),
            file_path=data.get("file_path", ""),
            alt_text=data.get("alt_text", ""),
            caption=data.get("caption", ""),
            transcript=data.get("transcript", ""),
            accessible=data.get("accessible", True),
            metadata=data.get("metadata", {}),
        )
        result = self._asset_repo.create({
            "id": asset.id,
            "name": asset.name,
            "asset_type": asset.asset_type.value,
            "description": asset.description,
            "file_path": asset.file_path,
            "alt_text": asset.alt_text,
            "caption": asset.caption,
            "transcript": asset.transcript,
            "accessible": asset.accessible,
            "metadata": asset.metadata,
            "version": asset.version,
        })
        logger.info("multimedia_asset_created", extra={"asset_id": result["id"]})
        return result

    def get_asset(self, asset_id: str) -> Optional[dict[str, Any]]:
        return self._asset_repo.get_by_id(asset_id)

    def list_assets(
        self, page: int = 1, per_page: int = 20, asset_type: Optional[str] = None
    ) -> dict[str, Any]:
        return self._asset_repo.get_all(page=page, per_page=per_page, asset_type=asset_type)

    def update_asset(self, asset_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        existing = self._asset_repo.get_by_id(asset_id)
        if not existing:
            raise ValueError(f"Asset '{asset_id}' not found.")
        existing_version = existing.get("version", 1)
        data["version"] = existing_version + 1
        return self._asset_repo.update(asset_id, data)

    def delete_asset(self, asset_id: str) -> bool:
        if not self._asset_repo.get_by_id(asset_id):
            raise ValueError(f"Asset '{asset_id}' not found.")
        return self._asset_repo.delete(asset_id)

    def search_assets(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        return self._asset_repo.search(query, page=page, per_page=per_page)

    def validate_asset(self, asset_id: str) -> dict[str, Any]:
        asset = self._asset_repo.get_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset '{asset_id}' not found.")

        vr = AssetValidationResult(asset_id=asset_id)
        asset_type = asset.get("asset_type", "")

        if not asset.get("name"):
            vr.add_issue("Asset name is missing")

        if not asset.get("file_path"):
            vr.add_issue("File path is missing")

        if asset_type in ("image", "svg", "icon"):
            if not asset.get("alt_text"):
                vr.add_issue("Alt text is required for image assets")

        if asset_type == "audio":
            if not asset.get("transcript"):
                vr.add_issue("Transcript is required for audio assets")

        if asset_type == "pdf":
            if not asset.get("alt_text"):
                vr.add_issue("Alt text / description is required for PDF assets")

        if not asset.get("accessible", True):
            vr.add_issue("Asset is marked as not accessible")

        return vr.to_dict()

    def create_collection(self, data: dict[str, Any]) -> dict[str, Any]:
        collection = AssetCollection(
            name=data.get("name", ""),
            description=data.get("description", ""),
            asset_ids=data.get("asset_ids", []),
        )
        result = self._collection_repo.create({
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "asset_ids": collection.asset_ids,
        })
        logger.info("asset_collection_created", extra={"collection_id": result["id"]})
        return result

    def get_collection(self, collection_id: str) -> Optional[dict[str, Any]]:
        return self._collection_repo.get_by_id(collection_id)

    def list_collections(self) -> list[dict[str, Any]]:
        return self._collection_repo.get_all()

    def update_collection(
        self, collection_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        existing = self._collection_repo.get_by_id(collection_id)
        if not existing:
            raise ValueError(f"Collection '{collection_id}' not found.")
        return self._collection_repo.update(collection_id, data)

    def delete_collection(self, collection_id: str) -> bool:
        if not self._collection_repo.get_by_id(collection_id):
            raise ValueError(f"Collection '{collection_id}' not found.")
        return self._collection_repo.delete(collection_id)

    def add_asset_to_collection(self, collection_id: str, asset_id: str) -> dict[str, Any]:
        collection = self._collection_repo.get_by_id(collection_id)
        if not collection:
            raise ValueError(f"Collection '{collection_id}' not found.")

        if not self._asset_repo.get_by_id(asset_id):
            raise ValueError(f"Asset '{asset_id}' not found.")

        asset_ids = collection.get("asset_ids", [])
        if asset_id not in asset_ids:
            asset_ids.append(asset_id)
            self._collection_repo.update(collection_id, {"asset_ids": asset_ids})

        return {"collection_id": collection_id, "asset_id": asset_id, "added": True}

    def remove_asset_from_collection(self, collection_id: str, asset_id: str) -> bool:
        collection = self._collection_repo.get_by_id(collection_id)
        if not collection:
            raise ValueError(f"Collection '{collection_id}' not found.")

        asset_ids = collection.get("asset_ids", [])
        if asset_id in asset_ids:
            asset_ids.remove(asset_id)
            self._collection_repo.update(collection_id, {"asset_ids": asset_ids})
            return True
        return False

    def validate_collection_assets(self, collection_id: str) -> dict[str, Any]:
        collection = self._collection_repo.get_by_id(collection_id)
        if not collection:
            raise ValueError(f"Collection '{collection_id}' not found.")

        results: list[dict[str, Any]] = []
        for asset_id in collection.get("asset_ids", []):
            try:
                vr = self.validate_asset(asset_id)
                results.append(vr)
            except ValueError:
                results.append({"asset_id": asset_id, "valid": False, "issues": ["Asset not found"]})

        total = len(results)
        valid_count = sum(1 for r in results if r.get("valid", False))
        return {
            "collection_id": collection_id,
            "total_assets": total,
            "valid_assets": valid_count,
            "invalid_assets": total - valid_count,
            "results": results,
        }
