"""Simulation Studio module for AuthShieldLab.

Provides offline, local-only cybersecurity training scenarios with
deterministic synthetic data generation, timeline management, exercise
tracking, and comprehensive assessment capabilities.
"""

from __future__ import annotations

from .domain.entities.scenario import Scenario, ScenarioDifficulty, ScenarioStatus, ScenarioType
from .domain.entities.dataset import SyntheticDataset, DatasetArtifact, DatasetArtifactType, DatasetMetadata
from .domain.entities.timeline import Timeline, TimelineEvent, BranchPath
from .domain.entities.exercise import Exercise, ExerciseStatus
from .domain.entities.assessment_sim import AssessmentMapper, CompletionRule
from .domain.entities.console import InstructorSession, LearnerSession, Submission, SessionStatus
from .domain.entities.results import ExerciseResult, ImprovementRecommendation
from .services.dataset_generator import DeterministicGenerator
from .services.scenario_service import ScenarioService
from .services.timeline_service import TimelineService
from .services.exercise_service import ExerciseService
from .services.instructor_console import InstructorConsoleService
from .services.learner_console import LearnerConsoleService
from .services.replay_service import ReplayService
from .services.results_service import ResultsService
from .services.export_service import ExportService
from .validators.simulation_validator import SimulationValidator

__all__ = [
    "Scenario",
    "ScenarioDifficulty",
    "ScenarioStatus",
    "ScenarioType",
    "SyntheticDataset",
    "DatasetArtifact",
    "DatasetArtifactType",
    "DatasetMetadata",
    "Timeline",
    "TimelineEvent",
    "BranchPath",
    "Exercise",
    "ExerciseStatus",
    "AssessmentMapper",
    "CompletionRule",
    "InstructorSession",
    "LearnerSession",
    "Submission",
    "SessionStatus",
    "ExerciseResult",
    "ImprovementRecommendation",
    "DeterministicGenerator",
    "ScenarioService",
    "TimelineService",
    "ExerciseService",
    "InstructorConsoleService",
    "LearnerConsoleService",
    "ReplayService",
    "ResultsService",
    "ExportService",
    "SimulationValidator",
]
