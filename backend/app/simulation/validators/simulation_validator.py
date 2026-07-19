"""Simulation entity validator."""

from __future__ import annotations

from typing import Any

from ..domain.entities.scenario import Scenario
from ..domain.entities.exercise import Exercise
from ..domain.entities.dataset import SyntheticDataset, DatasetArtifact
from ..domain.entities.timeline import Timeline, TimelineEvent, BranchPath
from ..domain.entities.console import InstructorSession, LearnerSession
from ..domain.entities.results import ExerciseResult, ImprovementRecommendation
from ..domain.entities.assessment_sim import AssessmentMapper


class SimulationValidator:
    """Centralized validator for all simulation domain entities.

    Provides static validation methods for each entity type,
    returning lists of error messages. An empty list indicates validity.
    """

    @staticmethod
    def validate_scenario(scenario: Scenario) -> list[str]:
        """Validate a Scenario entity."""
        return scenario.validate()

    @staticmethod
    def validate_exercise(exercise: Exercise) -> list[str]:
        """Validate an Exercise entity."""
        return exercise.validate()

    @staticmethod
    def validate_assessment_mapper(mapper: AssessmentMapper) -> list[str]:
        """Validate an AssessmentMapper entity."""
        return mapper.validate()

    @staticmethod
    def validate_dataset(dataset: SyntheticDataset) -> list[str]:
        """Validate a SyntheticDataset entity."""
        errors: list[str] = []

        if not dataset.name or not dataset.name.strip():
            errors.append("Dataset name is required")

        if not dataset.description or not dataset.description.strip():
            errors.append("Dataset description is required")

        if dataset.seed < 0:
            errors.append("Seed must be a non-negative integer")

        if not dataset.artifacts:
            errors.append("Dataset must contain at least one artifact")

        for idx, artifact in enumerate(dataset.artifacts):
            artifact_errors = SimulationValidator.validate_artifact(artifact)
            for err in artifact_errors:
                errors.append(f"Artifact[{idx}] ({artifact.name}): {err}")

        return errors

    @staticmethod
    def validate_artifact(artifact: DatasetArtifact) -> list[str]:
        """Validate a DatasetArtifact entity."""
        errors: list[str] = []

        if not artifact.name or not artifact.name.strip():
            errors.append("Artifact name is required")

        if not artifact.artifact_type:
            errors.append("Artifact type is required")

        if not isinstance(artifact.content, dict):
            errors.append("Artifact content must be a dictionary")

        return errors

    @staticmethod
    def validate_timeline(timeline: Timeline) -> list[str]:
        """Validate a Timeline entity."""
        errors: list[str] = []

        if not timeline.name or not timeline.name.strip():
            errors.append("Timeline name is required")

        if not timeline.scenario_id:
            errors.append("Scenario ID is required")

        if not timeline.events:
            errors.append("Timeline must contain at least one event")

        event_ids = {e.id for e in timeline.events}
        for branch in timeline.branches:
            if branch.source_event_id not in event_ids:
                errors.append(
                    f"Branch source event {branch.source_event_id} not found in timeline events"
                )
            if branch.target_event_id not in event_ids:
                errors.append(
                    f"Branch target event {branch.target_event_id} not found in timeline events"
                )

        offsets = [e.timestamp_offset_ms for e in timeline.events]
        if offsets and offsets != sorted(offsets):
            errors.append("Timeline events are not in chronological order")

        return errors

    @staticmethod
    def validate_timeline_event(event: TimelineEvent) -> list[str]:
        """Validate a TimelineEvent entity."""
        errors: list[str] = []

        if not event.event_type or not event.event_type.strip():
            errors.append("Event type is required")

        if event.timestamp_offset_ms < 0:
            errors.append("Timestamp offset must be non-negative")

        return errors

    @staticmethod
    def validate_branch_path(branch: BranchPath) -> list[str]:
        """Validate a BranchPath entity."""
        errors: list[str] = []

        if not branch.source_event_id:
            errors.append("Source event ID is required")

        if not branch.target_event_id:
            errors.append("Target event ID is required")

        if branch.source_event_id == branch.target_event_id:
            errors.append("Branch cannot connect an event to itself")

        return errors

    @staticmethod
    def validate_instructor_session(session: InstructorSession) -> list[str]:
        """Validate an InstructorSession entity."""
        errors: list[str] = []

        if not session.instructor_id:
            errors.append("Instructor ID is required")

        if not session.exercise_id:
            errors.append("Exercise ID is required")

        if session.status.value == "active" and session.started_at is None:
            errors.append("Active session must have a start time")

        if session.status.value == "completed" and session.ended_at is None:
            errors.append("Completed session must have an end time")

        return errors

    @staticmethod
    def validate_learner_session(session: LearnerSession) -> list[str]:
        """Validate a LearnerSession entity."""
        errors: list[str] = []

        if not session.learner_id:
            errors.append("Learner ID is required")

        if not session.exercise_id:
            errors.append("Exercise ID is required")

        if session.progress < 0.0 or session.progress > 1.0:
            errors.append("Progress must be between 0.0 and 1.0")

        if session.status.value == "active" and session.started_at is None:
            errors.append("Active session must have a start time")

        for idx, sub in enumerate(session.submissions):
            if not sub.content:
                errors.append(f"Submission[{idx}] content is required")

        return errors

    @staticmethod
    def validate_exercise_result(result: ExerciseResult) -> list[str]:
        """Validate an ExerciseResult entity."""
        errors: list[str] = []

        if not result.session_id:
            errors.append("Session ID is required")

        if not result.exercise_id:
            errors.append("Exercise ID is required")

        for criterion, score in result.assessment_scores.items():
            if score < 0.0 or score > 1.0:
                errors.append(f"Score for '{criterion}' must be between 0.0 and 1.0")

        for competency, progress in result.competency_progress.items():
            if progress < 0.0 or progress > 1.0:
                errors.append(
                    f"Competency progress for '{competency}' must be between 0.0 and 1.0"
                )

        if result.time_on_task_seconds < 0:
            errors.append("Time on task must be non-negative")

        return errors

    @staticmethod
    def validate_improvement_recommendation(
        rec: ImprovementRecommendation,
    ) -> list[str]:
        """Validate an ImprovementRecommendation."""
        errors: list[str] = []

        if not rec.category:
            errors.append("Recommendation category is required")

        if rec.priority not in ("high", "medium", "low"):
            errors.append("Priority must be 'high', 'medium', or 'low'")

        if not rec.recommendation:
            errors.append("Recommendation text is required")

        if not rec.rationale:
            errors.append("Rationale is required")

        return errors
