"""Disaster recovery service: validate backups, test restores, archive recovery, readiness reports."""

from __future__ import annotations

from typing import Optional

from ..domain.entities.disaster_recovery import (
    ArchiveRecovery,
    BackupValidation,
    RecoveryReadinessReport,
    RestoreTest,
)
from ..domain.interfaces import (
    ArchiveRecoveryRepository,
    BackupValidationRepository,
    RecoveryReadinessRepository,
    RestoreTestRepository,
)


class DisasterRecoveryService:
    """Validates backups, tests restores, manages archive recovery, and produces readiness reports."""

    def __init__(
        self,
        backup_repo: BackupValidationRepository,
        restore_repo: RestoreTestRepository,
        archive_repo: ArchiveRecoveryRepository,
        readiness_repo: RecoveryReadinessRepository,
    ) -> None:
        self._backup_repo = backup_repo
        self._restore_repo = restore_repo
        self._archive_repo = archive_repo
        self._readiness_repo = readiness_repo

    # ── Backup Validation ───────────────────────────────────────────

    async def validate_backup(
        self,
        backup_id: str,
        backup_type: str = "",
        size_bytes: int = 0,
        integrity: bool = True,
        restorable: bool = True,
    ) -> BackupValidation:
        """Create a new backup validation record."""
        validation = BackupValidation(
            backup_id=backup_id,
            backup_type=backup_type,
            size_bytes=size_bytes,
            integrity=integrity,
            restorable=restorable,
        )
        return self._backup_repo.save(validation)

    async def get_backup_validation(self, val_id: str) -> Optional[BackupValidation]:
        """Retrieve a backup validation by ID."""
        return self._backup_repo.find_by_id(val_id)

    async def get_validations_for_backup(self, backup_id: str) -> list[BackupValidation]:
        """Return all validations for a specific backup."""
        return self._backup_repo.find_by_backup_id(backup_id)

    async def list_backup_validations(self) -> list[BackupValidation]:
        """Return all backup validations."""
        return self._backup_repo.find_all()

    # ── Restore Tests ───────────────────────────────────────────────

    async def create_restore_test(
        self,
        backup_id: str,
    ) -> RestoreTest:
        """Create a new restore test record."""
        test = RestoreTest(backup_id=backup_id)
        return self._restore_repo.save(test)

    async def complete_restore_test(
        self,
        test_id: str,
        success: bool,
        duration_ms: int = 0,
        data_integrity: bool = True,
    ) -> Optional[RestoreTest]:
        """Mark a restore test as complete."""
        test = self._restore_repo.find_by_id(test_id)
        if test is None:
            return None
        if success:
            test.mark_success(duration_ms)
        else:
            test.mark_failure(duration_ms, data_integrity)
        return self._restore_repo.save(test)

    async def get_restore_test(self, test_id: str) -> Optional[RestoreTest]:
        """Retrieve a restore test by ID."""
        return self._restore_repo.find_by_id(test_id)

    async def get_restore_tests_for_backup(self, backup_id: str) -> list[RestoreTest]:
        """Return all restore tests for a specific backup."""
        return self._restore_repo.find_by_backup_id(backup_id)

    async def list_restore_tests(self) -> list[RestoreTest]:
        """Return all restore tests."""
        return self._restore_repo.find_all()

    # ── Archive Recovery ────────────────────────────────────────────

    async def start_archive_recovery(
        self,
        archive_id: str,
    ) -> ArchiveRecovery:
        """Create a new archive recovery record."""
        recovery = ArchiveRecovery(archive_id=archive_id)
        return self._archive_repo.save(recovery)

    async def complete_archive_recovery(
        self,
        recovery_id: str,
        items_recovered: int,
        total_items: int,
    ) -> Optional[ArchiveRecovery]:
        """Mark an archive recovery as complete."""
        recovery = self._archive_repo.find_by_id(recovery_id)
        if recovery is None:
            return None
        recovery.mark_complete(items_recovered, total_items)
        return self._archive_repo.save(recovery)

    async def fail_archive_recovery(self, recovery_id: str) -> Optional[ArchiveRecovery]:
        """Mark an archive recovery as failed."""
        recovery = self._archive_repo.find_by_id(recovery_id)
        if recovery is None:
            return None
        recovery.mark_failed()
        return self._archive_repo.save(recovery)

    async def get_archive_recovery(self, recovery_id: str) -> Optional[ArchiveRecovery]:
        """Retrieve an archive recovery by ID."""
        return self._archive_repo.find_by_id(recovery_id)

    async def list_archive_recoveries(self) -> list[ArchiveRecovery]:
        """Return all archive recoveries."""
        return self._archive_repo.find_all()

    # ── Readiness Report ────────────────────────────────────────────

    async def generate_readiness_report(self) -> RecoveryReadinessReport:
        """Assemble a readiness report from existing backup / restore / archive data."""
        backups = self._backup_repo.find_all()
        restores = self._restore_repo.find_all()
        archives = self._archive_repo.find_all()

        backup_health = 0.0
        if backups:
            healthy = sum(1 for b in backups if b.is_healthy())
            backup_health = (healthy / len(backups)) * 100.0

        restore_rate = 0.0
        if restores:
            successes = sum(1 for r in restores if r.status == "success")
            restore_rate = (successes / len(restores)) * 100.0

        archive_score = 0.0
        if archives:
            completed = [a for a in archives if a.status == "complete"]
            if completed:
                archive_score = sum(a.completeness for a in completed) / len(completed)

        report = RecoveryReadinessReport(
            backup_health=backup_health,
            restore_success_rate=restore_rate,
            archive_recovery=archive_score,
            config_recovery=backup_health,
            doc_recovery=backup_health,
        )
        report.compute_overall()
        return self._readiness_repo.save(report)

    async def get_latest_readiness(self) -> Optional[RecoveryReadinessReport]:
        """Return the most recent readiness report."""
        return self._readiness_repo.find_latest()

    async def list_readiness_reports(self) -> list[RecoveryReadinessReport]:
        """Return all readiness reports."""
        return self._readiness_repo.find_all()
