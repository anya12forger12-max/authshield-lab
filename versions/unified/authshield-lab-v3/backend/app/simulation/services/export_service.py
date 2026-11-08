"""Export service for JSON, CSV, and Markdown output."""

from __future__ import annotations

import csv
import io
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from ..domain.entities.scenario import Scenario
from ..domain.entities.exercise import Exercise
from ..domain.entities.dataset import SyntheticDataset
from ..domain.entities.timeline import Timeline
from ..domain.entities.results import ExerciseResult


class ExportService:
    """Service for exporting simulation data in multiple formats.

    Supports JSON, CSV, and Markdown output for scenarios, exercises,
    datasets, timelines, and results.
    """

    @staticmethod
    def _enum_value(val: Any) -> str:
        """Safely extract .value from an enum or return the string directly."""
        return val.value if hasattr(val, "value") else str(val)

    def export_scenario_json(self, scenario: Scenario) -> str:
        """Export a scenario to JSON string."""
        return json.dumps(scenario.to_dict(), indent=2, default=str)

    def export_scenario_markdown(self, scenario: Scenario) -> str:
        """Export a scenario to Markdown format."""
        lines = [
            f"# {scenario.title}",
            "",
            f"**Status:** {self._enum_value(scenario.status)}  ",
            f"**Difficulty:** {self._enum_value(scenario.difficulty)}  ",
            f"**Type:** {self._enum_value(scenario.scenario_type)}  ",
            f"**Duration:** {scenario.estimated_duration_minutes} minutes  ",
            f"**Version:** {scenario.version}",
            "",
            "## Description",
            "",
            scenario.description,
            "",
            "## Learning Objectives",
            "",
        ]
        for obj in scenario.learning_objectives:
            lines.append(f"- {obj}")
        lines.append("")

        if scenario.prerequisites:
            lines.append("## Prerequisites")
            lines.append("")
            for prereq in scenario.prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")

        if scenario.required_competencies:
            lines.append("## Required Competencies")
            lines.append("")
            for comp in scenario.required_competencies:
                lines.append(f"- {comp}")
            lines.append("")

        if scenario.tags:
            lines.append(f"**Tags:** {', '.join(scenario.tags)}")
            lines.append("")

        lines.append(f"**Target Audience:** {scenario.target_audience}")
        lines.append("")
        lines.append(f"*Created: {scenario.created_at.isoformat() if scenario.created_at else 'N/A'}*")
        return "\n".join(lines)

    def export_exercise_json(self, exercise: Exercise) -> str:
        """Export an exercise to JSON string."""
        return json.dumps(exercise.to_dict(), indent=2, default=str)

    def export_exercise_markdown(self, exercise: Exercise) -> str:
        """Export an exercise to Markdown format."""
        lines = [
            f"# {exercise.title}",
            "",
            f"**Status:** {self._enum_value(exercise.status)}  ",
            f"**Difficulty:** {exercise.difficulty}/10  ",
            f"**Category:** {exercise.category}  ",
            f"**Estimated Time:** {exercise.estimated_completion_minutes} minutes  ",
            f"**Version:** {exercise.version}  ",
            f"**Favorite:** {'Yes' if exercise.favorite else 'No'}",
            "",
            "## Description",
            "",
            exercise.description,
            "",
            "## Learning Outcomes",
            "",
        ]
        for outcome in exercise.learning_outcomes:
            lines.append(f"- {outcome}")
        lines.append("")

        if exercise.tags:
            lines.append(f"**Tags:** {', '.join(exercise.tags)}")
            lines.append("")

        lines.append(f"*Created: {exercise.created_at.isoformat() if exercise.created_at else 'N/A'}*")
        return "\n".join(lines)

    def export_dataset_json(self, dataset: SyntheticDataset) -> str:
        """Export a dataset to JSON string."""
        return json.dumps(dataset.to_dict(), indent=2, default=str)

    def export_dataset_csv(self, dataset: SyntheticDataset) -> str:
        """Export dataset records to CSV format.

        Exports records from all artifacts into a single CSV with
        a 'type' column to distinguish source artifact type.
        """
        output = io.StringIO()
        all_rows: list[dict[str, Any]] = []

        for artifact in dataset.artifacts:
            records = artifact.content.get("records", [])
            for record in records:
                flat_record: dict[str, Any] = {"artifact_type": artifact.artifact_type.value}
                for key, value in record.items():
                    if isinstance(value, (dict, list)):
                        flat_record[key] = json.dumps(value)
                    else:
                        flat_record[key] = value
                all_rows.append(flat_record)

        if not all_rows:
            return ""

        fieldnames = list(all_rows[0].keys())
        for row in all_rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

        return output.getvalue()

    def export_timeline_json(self, timeline: Timeline) -> str:
        """Export a timeline to JSON string."""
        return json.dumps(timeline.to_dict(), indent=2, default=str)

    def export_timeline_markdown(self, timeline: Timeline) -> str:
        """Export a timeline to Markdown format."""
        lines = [
            f"# Timeline: {timeline.name}",
            "",
            f"**Scenario ID:** {timeline.scenario_id}  ",
            f"**Total Duration:** {timeline.total_duration_ms}ms  ",
            f"**Events:** {len(timeline.events)}  ",
            f"**Branches:** {len(timeline.branches)}",
            "",
            "## Events",
            "",
        ]

        for event in timeline.events:
            milestone_marker = " *[MILESTONE]*" if event.milestone else ""
            checkpoint_marker = " *[CHECKPOINT]*" if event.learner_checkpoint else ""
            lines.append(
                f"### {event.order + 1}. {event.event_type}{milestone_marker}{checkpoint_marker}"
            )
            lines.append(f"- **Offset:** {event.timestamp_offset_ms}ms")
            if event.instructor_annotation:
                lines.append(f"- **Annotation:** {event.instructor_annotation}")
            if event.data:
                lines.append(f"- **Data:** `{json.dumps(event.data, default=str)}`")
            lines.append("")

        if timeline.branches:
            lines.append("## Branches")
            lines.append("")
            for branch in timeline.branches:
                lines.append(
                    f"- `{branch.source_event_id[:8]}` -> `{branch.target_event_id[:8]}` "
                    f"(condition: {branch.condition})"
                )
            lines.append("")

        lines.append(f"*Created: {timeline.created_at.isoformat()}*")
        return "\n".join(lines)

    def export_results_json(self, result: ExerciseResult) -> str:
        """Export results to JSON string."""
        return json.dumps(result.to_dict(), indent=2, default=str)

    def export_results_markdown(self, result: ExerciseResult) -> str:
        """Export results to Markdown format."""
        overall_score = result.calculate_overall_score()
        lines = [
            "# Exercise Results",
            "",
            f"**Exercise ID:** {result.exercise_id}  ",
            f"**Session ID:** {result.session_id}  ",
            f"**Status:** {result.completion_status}  ",
            f"**Overall Score:** {overall_score:.1%}  ",
            f"**Time on Task:** {result.time_on_task_seconds} seconds",
            "",
            "## Assessment Scores",
            "",
        ]

        for criterion, score in result.assessment_scores.items():
            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            lines.append(f"- **{criterion}:** {bar} {score:.1%}")
        lines.append("")

        if result.competency_progress:
            lines.append("## Competency Progress")
            lines.append("")
            for competency, progress in result.competency_progress.items():
                bar_length = int(progress * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                lines.append(f"- **{competency}:** {bar} {progress:.1%}")
            lines.append("")

        if result.instructor_feedback:
            lines.append("## Instructor Feedback")
            lines.append("")
            lines.append(result.instructor_feedback)
            lines.append("")

        if result.improvement_recommendations:
            lines.append("## Improvement Recommendations")
            lines.append("")
            for rec in result.improvement_recommendations:
                priority_marker = "!" if rec.priority == "high" else "-" if rec.priority == "medium" else " "
                lines.append(f"- [{priority_marker}] **{rec.category}:** {rec.recommendation}")
                lines.append(f"  Rationale: {rec.rationale}")
            lines.append("")

        if result.reflection_responses:
            lines.append("## Reflections")
            lines.append("")
            for idx, reflection in enumerate(result.reflection_responses, 1):
                lines.append(f"{idx}. {reflection}")
            lines.append("")

        return "\n".join(lines)

    def export_batch_json(
        self, items: list[Any], item_type: str
    ) -> str:
        """Export a batch of items to JSON."""
        data = {
            "type": item_type,
            "count": len(items),
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "items": [
                item.to_dict() if hasattr(item, "to_dict") else str(item)
                for item in items
            ],
        }
        return json.dumps(data, indent=2, default=str)

    def export_batch_csv(
        self, items: list[Any], item_type: str
    ) -> str:
        """Export a batch of items to CSV."""
        if not items:
            return ""

        output = io.StringIO()
        first = items[0]
        if hasattr(first, "to_dict"):
            all_rows = [item.to_dict() for item in items]
        else:
            return ""

        if not all_rows:
            return ""

        fieldnames = list(all_rows[0].keys())
        for row in all_rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            flat_row: dict[str, Any] = {}
            for key, value in row.items():
                if isinstance(value, (dict, list)):
                    flat_row[key] = json.dumps(value, default=str)
                else:
                    flat_row[key] = value
            writer.writerow(flat_row)

        return output.getvalue()
