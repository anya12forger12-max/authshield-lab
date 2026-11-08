"""Service layer for curriculum mapping operations."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.standards.domain.entities.mapping import (
    CoverageReport,
    CurriculumMapping,
    MappingBulkResult,
    MappingEvidence,
    MappingGap,
)
from app.standards.domain.events.standards_events import BulkMappingCompleted, MappingCreated
from app.standards.domain.interfaces.standards_interfaces import (
    AbstractCoverageReportRepository,
    AbstractCurriculumMappingRepository,
    AbstractFrameworkRepository,
    AbstractMappingBulkResultRepository,
)
from app.standards.events.standards_event_handlers import get_event_bus
from app.standards.validators.standards_validator import StandardsValidator

logger = logging.getLogger(__name__)


class MappingService:
    """Manages curriculum mappings between frameworks."""

    def __init__(
        self,
        mapping_repo: AbstractCurriculumMappingRepository | None = None,
        coverage_repo: AbstractCoverageReportRepository | None = None,
        bulk_repo: AbstractMappingBulkResultRepository | None = None,
        framework_repo: AbstractFrameworkRepository | None = None,
    ) -> None:
        from app.standards.repositories.standards_repository_impl import (
            InMemoryCoverageReportRepository,
            InMemoryCurriculumMappingRepository,
            InMemoryFrameworkRepository,
            InMemoryMappingBulkResultRepository,
        )

        self._mappings = mapping_repo or InMemoryCurriculumMappingRepository()
        self._coverage = coverage_repo or InMemoryCoverageReportRepository()
        self._bulk_results = bulk_repo or InMemoryMappingBulkResultRepository()
        self._frameworks = framework_repo or InMemoryFrameworkRepository()
        self._validator = StandardsValidator()
        self._bus = get_event_bus()

    def create_mapping(
        self,
        source_id: str,
        source_type: str,
        target_id: str,
        target_type: str,
        coverage_level: str = "partial",
        confidence: float = 0.0,
        instructor_notes: str = "",
    ) -> CurriculumMapping:
        self._validator.validate_non_empty(source_id, "source_id")
        self._validator.validate_non_empty(target_id, "target_id")
        self._validator.validate_coverage_level(coverage_level)
        self._validator.validate_confidence(confidence)
        mapping = CurriculumMapping(
            source_id=source_id,
            source_type=source_type,
            target_id=target_id,
            target_type=target_type,
            coverage_level=coverage_level,
            confidence=confidence,
            instructor_notes=instructor_notes,
        )
        self._mappings.save(mapping)
        event = MappingCreated(
            mapping_id=mapping.id,
            source_id=source_id,
            target_id=target_id,
            coverage_level=coverage_level,
        )
        self._bus.dispatch(event)
        logger.info("Mapping created: id=%s source=%s target=%s", mapping.id, source_id, target_id)
        return mapping

    def get_mapping(self, mapping_id: str) -> CurriculumMapping | None:
        return self._mappings.get_by_id(mapping_id)

    def list_mappings(self) -> list[CurriculumMapping]:
        return self._mappings.list_all()

    def update_mapping(
        self,
        mapping_id: str,
        coverage_level: str | None = None,
        confidence: float | None = None,
        instructor_notes: str | None = None,
        review_status: str | None = None,
    ) -> CurriculumMapping | None:
        mapping = self._mappings.get_by_id(mapping_id)
        if mapping is None:
            return None
        if coverage_level is not None:
            self._validator.validate_coverage_level(coverage_level)
            mapping.coverage_level = coverage_level
        if confidence is not None:
            self._validator.validate_confidence(confidence)
            mapping.confidence = confidence
        if instructor_notes is not None:
            mapping.update_notes(instructor_notes)
        if review_status is not None:
            mapping.set_review_status(review_status)
        mapping.updated_at = datetime.now(timezone.utc)
        self._mappings.save(mapping)
        return mapping

    def delete_mapping(self, mapping_id: str) -> bool:
        return self._mappings.delete(mapping_id)

    def add_evidence(
        self,
        mapping_id: str,
        evidence_type: str,
        description: str,
        reference_id: str = "",
    ) -> MappingEvidence | None:
        mapping = self._mappings.get_by_id(mapping_id)
        if mapping is None:
            return None
        ev = MappingEvidence(
            evidence_type=evidence_type,
            description=description,
            reference_id=reference_id,
        )
        mapping.add_evidence(ev)
        self._mappings.save(mapping)
        return ev

    def list_mappings_by_source(self, source_id: str) -> list[CurriculumMapping]:
        return self._mappings.list_by_source(source_id)

    def list_mappings_by_target(self, target_id: str) -> list[CurriculumMapping]:
        return self._mappings.list_by_target(target_id)

    # ------------------------------------------------------------------
    # Bulk mapping
    # ------------------------------------------------------------------

    def bulk_map(
        self,
        source_ids: list[str],
        target_ids: list[str],
        source_type: str,
        target_type: str,
    ) -> MappingBulkResult:
        total = len(source_ids)
        mapped_count = 0
        unmapped: list[str] = []
        for sid in source_ids:
            if sid in target_ids:
                mapping = CurriculumMapping(
                    source_id=sid,
                    source_type=source_type,
                    target_id=sid,
                    target_type=target_type,
                    coverage_level="full",
                    confidence=1.0,
                )
                self._mappings.save(mapping)
                mapped_count += 1
            else:
                unmapped.append(sid)
        result = MappingBulkResult(
            total=total,
            mapped=mapped_count,
            unmapped=len(unmapped),
            gaps=unmapped,
        )
        self._bulk_results.save(result)
        event = BulkMappingCompleted(
            total=total,
            mapped=mapped_count,
            unmapped=len(unmapped),
            gaps=unmapped,
        )
        self._bus.dispatch(event)
        logger.info("Bulk mapping: total=%d mapped=%d unmapped=%d", total, mapped_count, len(unmapped))
        return result

    # ------------------------------------------------------------------
    # Coverage analysis
    # ------------------------------------------------------------------

    def compute_coverage(self, framework_id: str) -> CoverageReport:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            raise ValueError(f"Framework {framework_id} not found")
        total = len(fw.competencies) + len(fw.skills)
        mapped_ids: set[str] = set()
        for m in self._mappings.list_all():
            mapped_ids.add(m.source_id)
            mapped_ids.add(m.target_id)
        fw_item_ids = {c.id for c in fw.competencies} | {s.id for s in fw.skills}
        mapped_count = len(fw_item_ids & mapped_ids)
        gaps: list[MappingGap] = []
        for item_id in fw_item_ids - mapped_ids:
            item = fw.find_competency(item_id) or fw.find_skill(item_id)
            item_name = item.name if item else item_id
            gaps.append(MappingGap(
                item_id=item_id,
                item_name=item_name,
                gap_type="unmapped",
                severity="medium",
                recommendation=f"Map {item_name} to a target element",
            ))
        report = CoverageReport(
            framework_id=framework_id,
            total_items=total,
            mapped_items=mapped_count,
            gaps=gaps,
        )
        report.calculate_coverage()
        self._coverage.save(report)
        return report

    def identify_gaps(self, framework_id: str) -> list[MappingGap]:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            raise ValueError(f"Framework {framework_id} not found")
        mapped_ids: set[str] = set()
        for m in self._mappings.list_all():
            mapped_ids.add(m.source_id)
            mapped_ids.add(m.target_id)
        fw_item_ids = {c.id for c in fw.competencies} | {s.id for s in fw.skills}
        gaps: list[MappingGap] = []
        for item_id in fw_item_ids - mapped_ids:
            item = fw.find_competency(item_id) or fw.find_skill(item_id)
            item_name = item.name if item else item_id
            gaps.append(MappingGap(
                item_id=item_id,
                item_name=item_name,
                gap_type="unmapped",
                severity="medium",
                recommendation=f"Map {item_name} to a target element",
            ))
        for m in self._mappings.list_all():
            if m.confidence < 0.5:
                gaps.append(MappingGap(
                    item_id=m.id,
                    item_name=f"Low-confidence mapping {m.source_id} -> {m.target_id}",
                    gap_type="low_confidence",
                    severity="low",
                    recommendation="Review and increase confidence score",
                ))
        return gaps
