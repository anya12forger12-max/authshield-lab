from __future__ import annotations

from datetime import datetime, timezone

from app.quality.domain.entities.accessibility_a11y import (
    A11yAudit,
    A11yAuditResult,
    A11yFeature,
    A11yProfile,
    A11yScorecard,
    KeyboardShortcut,
)
from app.quality.domain.interfaces.repositories import (
    A11yAuditRepository,
    A11yProfileRepository,
    A11yScorecardRepository,
    KeyboardShortcutRepository,
)


class AccessibilityService:
    def __init__(
        self,
        profile_repo: A11yProfileRepository,
        audit_repo: A11yAuditRepository,
        scorecard_repo: A11yScorecardRepository,
        shortcut_repo: KeyboardShortcutRepository,
    ) -> None:
        self._profile_repo = profile_repo
        self._audit_repo = audit_repo
        self._scorecard_repo = scorecard_repo
        self._shortcut_repo = shortcut_repo

    def create_profile(self, profile: A11yProfile) -> A11yProfile:
        return self._profile_repo.save(profile)

    def get_profile(self, name: str) -> A11yProfile | None:
        return self._profile_repo.find_by_name(name)

    def get_all_profiles(self) -> list[A11yProfile]:
        return self._profile_repo.find_all()

    def run_audit(self, audit: A11yAudit) -> A11yAudit:
        violations = 0
        passed = 0
        na = 0
        for r in audit.results:
            if r.status == "fail":
                violations += 1
            elif r.status == "pass":
                passed += 1
            else:
                na += 1
        audit.violations_count = violations
        audit.passed_count = passed
        audit.na_count = na
        total = len(audit.results)
        audit.overall_score = ((passed / total) * 100.0) if total > 0 else 0.0
        audit.generated_at = datetime.now(timezone.utc)
        return self._audit_repo.save(audit)

    def get_audit(self, audit_id: str) -> A11yAudit | None:
        return self._audit_repo.find_by_id(audit_id)

    def get_all_audits(self) -> list[A11yAudit]:
        return self._audit_repo.find_all()

    def create_scorecard(self, scorecard: A11yScorecard) -> A11yScorecard:
        return self._scorecard_repo.save(scorecard)

    def get_scorecards_by_category(self, category: str) -> list[A11yScorecard]:
        return self._scorecard_repo.find_by_category(category)

    def add_shortcut(self, shortcut: KeyboardShortcut) -> KeyboardShortcut:
        return self._shortcut_repo.save(shortcut)

    def get_shortcut(self, action: str) -> KeyboardShortcut | None:
        return self._shortcut_repo.find_by_action(action)

    def get_all_shortcuts(self) -> list[KeyboardShortcut]:
        return self._shortcut_repo.find_all()
