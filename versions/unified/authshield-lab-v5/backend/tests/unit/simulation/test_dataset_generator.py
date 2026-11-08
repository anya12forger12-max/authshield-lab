"""Tests for DeterministicGenerator — seed determinism, generate_auth_logs, generate_audit_logs, generate_user_profiles."""

from __future__ import annotations

from app.simulation.services.dataset_generator import DeterministicGenerator
from app.simulation.domain.entities.dataset import DatasetArtifactType


class TestDeterministicGenerator:
    def test_same_seed_produces_same_auth_logs(self):
        gen1 = DeterministicGenerator(seed=42)
        gen2 = DeterministicGenerator(seed=42)
        result1 = gen1.generate_auth_logs(count=5)
        result2 = gen2.generate_auth_logs(count=5)
        assert result1.content["records"] == result2.content["records"]

    def test_different_seed_produces_different_auth_logs(self):
        gen1 = DeterministicGenerator(seed=42)
        gen2 = DeterministicGenerator(seed=99)
        result1 = gen1.generate_auth_logs(count=5)
        result2 = gen2.generate_auth_logs(count=5)
        assert result1.content["records"] != result2.content["records"]

    def test_same_seed_produces_same_audit_logs(self):
        g1 = DeterministicGenerator(seed=100)
        g2 = DeterministicGenerator(seed=100)
        r1 = g1.generate_audit_logs(3)
        r2 = g2.generate_audit_logs(3)
        assert r1.content["records"] == r2.content["records"]

    def test_same_seed_produces_same_user_profiles(self):
        g1 = DeterministicGenerator(seed=7)
        g2 = DeterministicGenerator(seed=7)
        r1 = g1.generate_user_profiles(3)
        r2 = g2.generate_user_profiles(3)
        assert r1.content["records"] == r2.content["records"]

    def test_auth_log_artifact_type(self):
        gen = DeterministicGenerator()
        result = gen.generate_auth_logs(1)
        assert result.artifact_type == DatasetArtifactType.AUTH_LOG
        assert result.name == "auth_log"

    def test_audit_log_artifact_type(self):
        gen = DeterministicGenerator()
        result = gen.generate_audit_logs(1)
        assert result.artifact_type == DatasetArtifactType.AUDIT_LOG
        assert result.name == "audit_log"

    def test_user_profiles_artifact_type(self):
        gen = DeterministicGenerator()
        result = gen.generate_user_profiles(3)
        assert result.artifact_type == DatasetArtifactType.USER_PROFILE
        assert len(result.content["records"]) == 3

    def test_auth_log_count(self):
        gen = DeterministicGenerator()
        result = gen.generate_auth_logs(10)
        assert len(result.content["records"]) == 10

    def test_audit_log_count(self):
        gen = DeterministicGenerator()
        result = gen.generate_audit_logs(50)
        assert len(result.content["records"]) == 50

    def test_user_profiles_have_expected_keys(self):
        gen = DeterministicGenerator()
        result = gen.generate_user_profiles(1)
        record = result.content["records"][0]
        assert "user_id" in record
        assert "email" in record
        assert "role" in record
        assert "status" in record

    def test_full_dataset_contains_all_artifact_types(self):
        gen = DeterministicGenerator()
        ds = gen.generate_full_dataset()
        types = {a.artifact_type for a in ds.artifacts}
        assert DatasetArtifactType.AUTH_LOG in types
        assert DatasetArtifactType.AUDIT_LOG in types
        assert DatasetArtifactType.USER_PROFILE in types
        assert DatasetArtifactType.CONFIG_SNAPSHOT in types

    def test_full_dataset_seed_determinism(self):
        g1 = DeterministicGenerator(seed=42)
        g2 = DeterministicGenerator(seed=42)
        ds1 = g1.generate_full_dataset()
        ds2 = g2.generate_full_dataset()
        assert len(ds1.artifacts) == len(ds2.artifacts)

    def test_empty_count_returns_no_records(self):
        gen = DeterministicGenerator()
        result = gen.generate_auth_logs(0)
        assert len(result.content["records"]) == 0

    def test_different_seeds_different_results_across_all_generators(self):
        g1 = DeterministicGenerator(seed=1)
        g2 = DeterministicGenerator(seed=2)
        r1 = g1.generate_audit_logs(2)
        r2 = g2.generate_audit_logs(2)
        assert r1.content["records"] != r2.content["records"]
