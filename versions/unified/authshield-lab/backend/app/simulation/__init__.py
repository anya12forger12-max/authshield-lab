"""Simulation Studio module for AuthShieldLab.

Provides offline, local-only cybersecurity training scenarios with
deterministic synthetic data generation, timeline management, exercise
tracking, and comprehensive assessment capabilities.
"""

from __future__ import annotations

from .domain.entities.assessment_sim import AssessmentMapper, CompletionRule
from .domain.entities.console import InstructorSession, LearnerSession, SessionStatus, Submission
from .domain.entities.dataset import (
    DatasetArtifact,
    DatasetArtifactType,
    DatasetMetadata,
    SyntheticDataset,
)
from .domain.entities.exercise import Exercise, ExerciseStatus
from .domain.entities.results import ExerciseResult, ImprovementRecommendation
from .domain.entities.scenario import Scenario, ScenarioDifficulty, ScenarioStatus, ScenarioType
from .domain.entities.timeline import BranchPath, Timeline, TimelineEvent
from .services.dataset_generator import DeterministicGenerator
from .services.exercise_service import ExerciseService
from .services.export_service import ExportService
from .services.instructor_console import InstructorConsoleService
from .services.learner_console import LearnerConsoleService
from .services.replay_service import ReplayService
from .services.results_service import ResultsService
from .services.scenario_service import ScenarioService
from .services.timeline_service import TimelineService
from .validators.simulation_validator import SimulationValidator

__all__ = [
    "AssessmentMapper",
    "BranchPath",
    "CompletionRule",
    "DatasetArtifact",
    "DatasetArtifactType",
    "DatasetMetadata",
    "DeterministicGenerator",
    "Exercise",
    "ExerciseResult",
    "ExerciseService",
    "ExerciseStatus",
    "ExportService",
    "ImprovementRecommendation",
    "InstructorConsoleService",
    "InstructorSession",
    "LearnerConsoleService",
    "LearnerSession",
    "ReplayService",
    "ResultsService",
    "Scenario",
    "ScenarioDifficulty",
    "ScenarioService",
    "ScenarioStatus",
    "ScenarioType",
    "SessionStatus",
    "SimulationValidator",
    "Submission",
    "SyntheticDataset",
    "Timeline",
    "TimelineEvent",
    "TimelineService",
]
