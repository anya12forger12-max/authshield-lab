from __future__ import annotations

from datetime import datetime, timezone

from app.quality.domain.entities.release import Release, ReleaseNote, ReleaseReadiness
from app.quality.domain.interfaces.repositories import (
    ReleaseNoteRepository,
    ReleaseReadinessRepository,
    ReleaseRepository,
)


class ReleaseService:
    def __init__(
        self,
        release_repo: ReleaseRepository,
        readiness_repo: ReleaseReadinessRepository,
        note_repo: ReleaseNoteRepository,
    ) -> None:
        self._release_repo = release_repo
        self._readiness_repo = readiness_repo
        self._note_repo = note_repo

    def create_release(self, release: Release) -> Release:
        return self._release_repo.save(release)

    def update_release(self, release: Release) -> Release:
        return self._release_repo.save(release)

    def get_release(self, release_id: str) -> Release | None:
        return self._release_repo.find_by_id(release_id)

    def get_release_by_version(self, version: str) -> Release | None:
        return self._release_repo.find_by_version(version)

    def get_all_releases(self) -> list[Release]:
        return self._release_repo.find_all()

    def check_readiness(self, release_id: str) -> ReleaseReadiness:
        release = self._release_repo.find_by_id(release_id)
        if not release:
            raise ValueError(f"Release {release_id} not found")
        existing = self._readiness_repo.find_by_release_id(release_id)
        if existing:
            existing.checked_at = datetime.now(timezone.utc)
            existing.overall_ready = (
                existing.functional_completeness
                and existing.a11y_compliance
                and existing.doc_coverage
                and existing.localization_completeness
                and existing.performance_targets
                and existing.security_checks
                and existing.backup_verification
                and existing.extension_compatibility
                and existing.sdk_stability
            )
            return self._readiness_repo.save(existing)
        return self._readiness_repo.save(
            ReleaseReadiness(release_id=release_id, overall_ready=False)
        )

    def update_readiness(self, readiness: ReleaseReadiness) -> ReleaseReadiness:
        readiness.checked_at = datetime.now(timezone.utc)
        readiness.overall_ready = (
            readiness.functional_completeness
            and readiness.a11y_compliance
            and readiness.doc_coverage
            and readiness.localization_completeness
            and readiness.performance_targets
            and readiness.security_checks
            and readiness.backup_verification
            and readiness.extension_compatibility
            and readiness.sdk_stability
        )
        return self._readiness_repo.save(readiness)

    def get_release_readiness(self, release_id: str) -> ReleaseReadiness | None:
        return self._readiness_repo.find_by_release_id(release_id)

    def add_note(self, note: ReleaseNote) -> ReleaseNote:
        return self._note_repo.save(note)

    def get_notes_for_release(self, release_id: str) -> list[ReleaseNote]:
        return self._note_repo.find_by_release_id(release_id)
