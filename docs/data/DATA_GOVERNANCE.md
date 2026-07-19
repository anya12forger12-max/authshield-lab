# Data Governance Handbook — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

This handbook defines data governance policies, standards, and procedures for
AuthShield Lab. It covers data ownership, quality, lifecycle, retention,
disposal, privacy, and cross-domain data sharing.

### 1.1 Governance Principles

| Principle | Description |
|---|---|
| Accountability | Every data domain has a designated owner |
| Quality | Data must be accurate, complete, consistent, timely |
| Lifecycle | Data has defined beginning, middle, and end |
| Compliance | Regulatory requirements are mapped to controls |
| Transparency | Data policies are documented and accessible |

---

## 2. Data Ownership Model

### 2.1 Ownership RACI Matrix

| Data Domain | Accountable | Responsible | Consulted | Informed |
|---|---|---|---|---|
| Identity (users, credentials) | Security Admin | Identity Service | Legal | All Users |
| Authorization (roles, permissions) | Security Admin | Auth Service | — | Users with admin roles |
| Organizations | Org Admin | Organization Service | — | Org Members |
| Institutions | Institution Admin | Institution Service | Legal, Compliance | Students, Instructors |
| Courses | Course Author | Learning Service | — | Students |
| Lessons | Course Author | Learning Service | — | Students |
| Assessments | Assessment Designer | Assessment Service | Course Author | Students |
| Competencies | Curriculum Admin | Learning Service | Assessment Designer | Students |
| Certificates | Platform Admin | Learning Service | — | Certificate Holders |
| Plugins | Platform Admin | Extension Service | — | Plugin Authors |
| Configuration | Platform Admin | Platform Service | — | All Users |
| Themes | UI/UX Admin | Presentation Service | — | All Users |
| Localization | i18n Admin | Platform Service | — | All Users |
| Accessibility | A11y Admin | Presentation Service | Users with Disabilities | All Users |
| Notifications | Platform Admin | Platform Service | — | Users |
| Audit Logs | Security Admin | Security Service | Legal | — |
| Security Events | Security Admin | Security Service | Legal | Affected Users |
| Backups | Platform Admin | Platform Service | Security Admin | — |
| Diagnostics | Platform Admin | Platform Service | — | — |
| Assets/Content | Content Manager | Content Service | — | Content Consumers |

### 2.2 Ownership Responsibilities

```python
class DataOwner:
    """Represents a data domain owner with responsibilities."""

    RESPONSIBILITIES = {
        "define_schema": "Define and maintain data schema for the domain",
        "approve_changes": "Review and approve schema changes",
        "set_retention": "Define retention and archival policies",
        "manage_access": "Control access to domain data",
        "ensure_quality": "Monitor and enforce data quality",
        "handle_requests": "Respond to data access/deletion requests",
        "audit_usage": "Review data access patterns",
        "document_policies": "Maintain domain-specific policies",
    }
```

---

## 3. Data Quality Standards

### 3.1 Quality Dimensions

| Dimension | Definition | Measurement | Target |
|---|---|---|---|
| **Accuracy** | Data correctly represents real-world entity | Validation rules pass | 99.9% |
| **Completeness** | Required fields are populated | NULL checks on required fields | 100% |
| **Consistency** | Data is uniform across the system | Cross-reference checks | 99.9% |
| **Timeliness** | Data is up-to-date | Timestamp freshness | < 24h for critical |
| **Uniqueness** | No duplicate records | Unique constraint violations | 0 duplicates |
| **Validity** | Data conforms to defined formats | Regex/format validation | 100% |

### 3.2 Quality Rules

```python
class DataQualityRules:
    """Enforces data quality standards."""

    RULES = {
        "users": {
            "email": {
                "format": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "unique": True,
                "not_null": True,
                "max_length": 255,
            },
            "display_name": {
                "not_null": True,
                "min_length": 1,
                "max_length": 100,
            },
            "password_hash": {
                "not_null": True,
                "format": r"^\$argon2",  # Must be Argon2id
            },
            "status": {
                "not_null": True,
                "allowed_values": ["active", "inactive", "suspended", "pending"],
            },
        },
        "courses": {
            "title": {
                "not_null": True,
                "min_length": 1,
                "max_length": 200,
            },
            "slug": {
                "unique": True,
                "format": r"^[a-z0-9-]+$",
                "not_null": True,
            },
            "status": {
                "not_null": True,
                "allowed_values": ["draft", "published", "archived"],
            },
        },
        "assessments": {
            "passing_score": {
                "not_null": True,
                "min_value": 0,
                "max_value": 100,
                "less_than": "max_score",
            },
            "max_score": {
                "not_null": True,
                "min_value": 1,
            },
        },
    }

    async def validate_entity(
        self,
        entity_type: str,
        entity_data: dict,
        session: AsyncSession,
    ) -> QualityResult:
        """Validate entity against quality rules."""
        rules = self.RULES.get(entity_type, {})
        result = QualityResult()

        for field_name, field_rules in rules.items():
            value = entity_data.get(field_name)

            # Not null check
            if field_rules.get("not_null") and value is None:
                result.add_violation(
                    field_name, "not_null", f"{field_name} is required"
                )
                continue

            if value is None:
                continue

            # Format check
            if "format" in field_rules:
                import re
                if not re.match(field_rules["format"], str(value)):
                    result.add_violation(
                        field_name, "format", f"{field_name} format invalid"
                    )

            # Length checks
            if "min_length" in field_rules and len(str(value)) < field_rules["min_length"]:
                result.add_violation(
                    field_name, "min_length",
                    f"{field_name} too short (min {field_rules['min_length']})"
                )

            if "max_length" in field_rules and len(str(value)) > field_rules["max_length"]:
                result.add_violation(
                    field_name, "max_length",
                    f"{field_name} too long (max {field_rules['max_length']})"
                )

            # Value range
            if "min_value" in field_rules and value < field_rules["min_value"]:
                result.add_violation(
                    field_name, "min_value",
                    f"{field_name} below minimum ({field_rules['min_value']})"
                )

            if "max_value" in field_rules and value > field_rules["max_value"]:
                result.add_violation(
                    field_name, "max_value",
                    f"{field_name} above maximum ({field_rules['max_value']})"
                )

            # Allowed values
            if "allowed_values" in field_rules:
                if value not in field_rules["allowed_values"]:
                    result.add_violation(
                        field_name, "enum",
                        f"{field_name} must be one of {field_rules['allowed_values']}"
                    )

            # Uniqueness
            if field_rules.get("unique"):
                exists = await self._check_unique(
                    session, entity_type, field_name, value
                )
                if exists:
                    result.add_violation(
                        field_name, "unique", f"{field_name} already exists"
                    )

        return result
```

### 3.3 Quality Monitoring

```python
class DataQualityMonitor:
    """Monitors data quality metrics."""

    async def run_quality_checks(
        self,
        session: AsyncSession,
    ) -> QualityReport:
        """Run all quality checks."""
        report = QualityReport()

        # Users quality
        user_quality = await self._check_users_quality(session)
        report.add_domain("users", user_quality)

        # Course quality
        course_quality = await self._check_courses_quality(session)
        report.add_domain("courses", course_quality)

        # Assessment quality
        assessment_quality = await self._check_assessments_quality(session)
        report.add_domain("assessments", assessment_quality)

        # Referential integrity
        integrity = await self._check_referential_integrity(session)
        report.add_domain("integrity", integrity)

        return report

    async def _check_users_quality(self, session: AsyncSession) -> DomainQuality:
        """Check user data quality."""
        checks = {}

        # Completeness: required fields
        result = await session.execute(
            text(
                "SELECT COUNT(*) FROM users "
                "WHERE is_deleted = 0 "
                "AND (email IS NULL OR display_name IS NULL OR password_hash IS NULL)"
            )
        )
        incomplete = result.scalar()
        checks["completeness"] = QualityCheck(
            name="required_fields_complete",
            total=await self._count_active(session, "users"),
            passed=await self._count_active(session, "users") - incomplete,
            failed=incomplete,
        )

        # Uniqueness: email
        result = await session.execute(
            text(
                "SELECT email, COUNT(*) as cnt FROM users "
                "WHERE is_deleted = 0 "
                "GROUP BY email HAVING cnt > 1"
            )
        )
        duplicates = len(result.fetchall())
        checks["uniqueness"] = QualityCheck(
            name="email_unique",
            total=1,
            passed=0 if duplicates > 0 else 1,
            failed=duplicates,
        )

        # Validity: status values
        result = await session.execute(
            text(
                "SELECT COUNT(*) FROM users "
                "WHERE is_deleted = 0 "
                "AND status NOT IN ('active', 'inactive', 'suspended', 'pending')"
            )
        )
        invalid_status = result.scalar()
        checks["validity"] = QualityCheck(
            name="status_valid",
            total=await self._count_active(session, "users"),
            passed=await self._count_active(session, "users") - invalid_status,
            failed=invalid_status,
        )

        return DomainQuality(domain="users", checks=checks)
```

---

## 4. Data Lifecycle Management

### 4.1 Lifecycle States

```
┌────────────────────────────────────────────────────────────────┐
│                    Data Lifecycle States                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CREATE ──► ACTIVE ──► ARCHIVED ──► RETIRED ──► PURGED          │
│    │          │           │            │           │             │
│    │          │           │            │           │             │
│  Draft     Published   Inactive    Past        Deleted          │
│  Pending   Live        Compressed  Retention   Irrecoverable    │
│                                                                 │
│  ──────── Retention Period ────────►                            │
│  ├──── Active ────┤── Archived ──┤── Retired ──┤               │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 Lifecycle Policies

```python
LIFECYCLE_POLICIES = {
    "users": {
        "states": ["pending", "active", "inactive", "suspended"],
        "transitions": {
            "pending": ["active", "inactive"],  # After verification
            "active": ["inactive", "suspended"],
            "inactive": ["active", "suspended"],  # Reactivation
            "suspended": ["active", "inactive"],  # After review
        },
        "retention": {
            "active": "indefinite",
            "inactive": "2 years then archive",
            "suspended": "1 year then review",
        },
        "archival": "Compress and archive after 2 years inactive",
        "purge": "GDPR erasure on request (with audit trail)",
    },
    "courses": {
        "states": ["draft", "published", "archived"],
        "transitions": {
            "draft": ["published"],
            "published": ["archived", "draft"],  # Unpublish
            "archived": ["published"],  # Republish
        },
        "retention": {
            "draft": "1 year then review",
            "published": "indefinite",
            "archived": "5 years",
        },
        "archival": "SCORM export before archival",
        "purge": "Soft delete only, keep for audit",
    },
    "assessments": {
        "states": ["draft", "published", "archived"],
        "transitions": {
            "draft": ["published"],
            "published": ["archived"],
            "archived": [],  # Terminal
        },
        "retention": {
            "draft": "1 year",
            "published": "indefinite",
            "archived": "5 years for results",
        },
    },
    "audit_entries": {
        "states": ["active", "archived"],
        "transitions": {
            "active": ["archived"],
        },
        "retention": {
            "active": "1 year",
            "archived": "7 years",
        },
        "purge": "Never — encrypted archive only",
    },
    "notifications": {
        "states": ["unread", "read", "archived"],
        "retention": {
            "unread": "90 days",
            "read": "90 days",
        },
        "purge": "Hard delete after 2 years",
    },
    "backups": {
        "states": ["active", "expired"],
        "retention": {
            "active": "Per rotation policy (3-2-1)",
        },
        "purge": "Secure delete (overwrite + delete)",
    },
}
```

### 4.3 Automated Lifecycle Management

```python
class LifecycleManager:
    """Automates data lifecycle transitions."""

    async def run_lifecycle_maintenance(
        self,
        session: AsyncSession,
    ) -> LifecycleReport:
        """Run all lifecycle maintenance tasks."""
        report = LifecycleReport()

        # Archive inactive users
        archived_users = await self._archive_inactive_users(session)
        report.add_metric("archived_users", archived_users)

        # Archive old courses
        archived_courses = await self._archive_old_courses(session)
        report.add_metric("archived_courses", archived_courses)

        # Purge expired notifications
        purged_notifications = await self._purge_old_notifications(session)
        report.add_metric("purged_notifications", purged_notifications)

        # Archive audit entries
        archived_audit = await self._archive_old_audit_entries(session)
        report.add_metric("archived_audit_entries", archived_audit)

        # Clean expired backups
        cleaned_backups = await self._cleanup_expired_backups(session)
        report.add_metric("cleaned_backups", cleaned_backups)

        return report

    async def _archive_inactive_users(
        self,
        session: AsyncSession,
        inactive_days: int = 730,
    ) -> int:
        """Archive users inactive for more than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=inactive_days)

        result = await session.execute(
            update(User)
            .where(User.status == "active")
            .where(User.last_login_at < cutoff)
            .where(User.is_deleted == False)
            .values(
                status="inactive",
                updated_at=datetime.utcnow(),
                metadata=sa.func.json_set(
                    User.metadata,
                    "$.archived_reason",
                    "auto_archive_inactive",
                ),
            )
        )

        return result.rowcount
```

---

## 5. Data Retention Schedule

### 5.1 Retention Matrix

| Data Type | Active | Archived | Total Retention | Legal Basis |
|---|---|---|---|---|
| User accounts | Indefinite | 2 years inactive | Account lifetime + 2y | Contract |
| User credentials | Active only | — | Account lifetime | Security |
| Course content | Indefinite | 5 years | Indefinite | Business |
| Course enrollments | Active | 5 years | Account lifetime | Business |
| Learning progress | 2 years | 5 years | 7 years | Educational records |
| Assessment attempts | 2 years | 5 years | 7 years | Educational records |
| Assessment results | 5 years | 5 years | 10 years | FERPA compliance |
| Competency records | Indefinite | 5 years | Account lifetime + 5y | Business |
| Certificates | Indefinite | Never expire | Permanent | Credential integrity |
| Audit logs | 1 year | 7 years | 8 years | Security/compliance |
| Security events | 2 years | 10 years | 12 years | Security compliance |
| Notifications | 90 days | 1 year | 1.25 years | Business |
| Backups | Per rotation | 3-2-1 rule | Variable | DR policy |
| System config | Indefinite | 2 years | Indefinite | Operations |
| Plugin data | Indefinite | 2 years deprecated | Indefinite | Operations |
| Diagnostic logs | 30 days | 1 year | 1.25 years | Operations |
| Import/export logs | 1 year | 2 years | 3 years | Operations |
| Accessibility profiles | Account lifetime | — | Account lifetime | Privacy (PII) |
| Localization packs | Indefinite | 2 years deprecated | Indefinite | Operations |

### 5.2 Retention Enforcement

```python
class RetentionEnforcer:
    """Enforces data retention schedules."""

    async def enforce_all(self, session: AsyncSession) -> RetentionResult:
        """Run all retention enforcement tasks."""
        result = RetentionResult()

        for data_type, policy in RETENTION_SCHEDULE.items():
            type_result = await self._enforce_retention(
                session, data_type, policy
            )
            result.add_type_result(data_type, type_result)

        return result

    async def _enforce_retention(
        self,
        session: AsyncSession,
        data_type: str,
        policy: dict,
    ) -> TypeRetentionPolicy:
        """Enforce retention for a specific data type."""
        active_days = policy.get("active_days")
        archived_days = policy.get("archived_days")

        if active_days:
            # Move to archive
            archived = await self._archive_old_records(
                session, data_type, active_days
            )
        else:
            archived = 0

        if archived_days:
            # Delete archived records past total retention
            deleted = await self._delete_expired_archived(
                session, data_type, archived_days
            )
        else:
            deleted = 0

        return TypeRetentionPolicy(
            archived=archived,
            deleted=deleted,
        )
```

---

## 6. Data Disposal Procedures

### 6.1 Secure Disposal

```python
class DataDisposalManager:
    """Handles secure data disposal."""

    async def gdpr_erasure(
        self,
        user_id: UUID,
        actor_id: UUID,
        session: AsyncSession,
    ) -> ErasureResult:
        """GDPR Article 17 right to erasure."""
        result = ErasureResult()

        # 1. Verify request is legitimate
        if not await self._verify_erasure_request(user_id, actor_id):
            raise UnauthorizedErasureError()

        # 2. Check for legal hold
        if await self._check_legal_hold(user_id):
            raise LegalHoldError("User data under legal hold")

        # 3. Export user data before erasure (for audit)
        export_path = await self._export_user_data(user_id, session)
        result.export_path = str(export_path)

        # 4. Anonymize user data (preserves referential integrity)
        anonymized = await self._anonymize_user_data(user_id, session)
        result.anonymized_fields = anonymized

        # 5. Delete user account
        await self._hard_delete_user(user_id, session)

        # 6. Audit the erasure
        await self._audit_erasure(user_id, actor_id, session)

        result.status = "completed"
        return result

    async def _anonymize_user_data(
        self,
        user_id: UUID,
        session: AsyncSession,
    ) -> list[str]:
        """Anonymize user data while preserving referential integrity."""
        import hashlib

        anonymized_hash = hashlib.sha256(str(user_id).encode()).hexdigest()[:12]
        anonymized_fields = []

        # Anonymize user record
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                email=f"erased_{anonymized_hash}@redacted.local",
                display_name=f"Erased User {anonymized_hash}",
                password_hash="ERASED",
                mfa_secret=None,
                mfa_enabled=False,
                avatar_url=None,
                metadata=None,
                status="inactive",
            )
        )
        anonymized_fields.extend([
            "email", "display_name", "password_hash",
            "mfa_secret", "avatar_url",
        ])

        # Anonymize audit entries (keep action, anonymize user)
        await session.execute(
            update(AuditEntry)
            .where(AuditEntry.user_id == user_id)
            .values(user_id=None, ip_address=None, user_agent=None)
        )

        return anonymized_fields

    async def secure_delete_file(self, file_path: Path, passes: int = 3):
        """Securely delete a file by overwriting."""
        if not file_path.exists():
            return

        file_size = file_path.stat().st_size

        with open(file_path, "r+b") as f:
            for pass_num in range(passes):
                f.seek(0)
                # Overwrite with random data
                f.write(secrets.token_bytes(file_size))
                f.flush()
                os.fsync(f.fileno())

        file_path.unlink()
```

### 6.2 Disposal Audit Trail

```python
class DisposalAudit:
    """Audits all data disposal operations."""

    async def log_disposal(
        self,
        disposal_type: str,
        entity_type: str,
        entity_id: UUID,
        actor_id: UUID,
        reason: str,
        session: AsyncSession,
    ):
        """Log a data disposal event."""
        entry = AuditEntry(
            action=f"disposal.{disposal_type}",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=actor_id,
            metadata=json.dumps({
                "disposal_type": disposal_type,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "gdpr_compliant": True,
            }),
        )

        session.add(entry)
```

---

## 7. Data Classification Enforcement

### 7.1 Classification Rules

```python
class ClassificationEnforcer:
    """Enforces data classification rules."""

    RULES = {
        "SECRET": {
            "encryption": "required",
            "access_log": "required",
            "sharing": "prohibited",
            "backup": "encrypted_only",
            "display": "masked_by_default",
        },
        "RESTRICTED": {
            "encryption": "required",
            "access_log": "required",
            "sharing": "owner_approval_required",
            "backup": "encrypted_required",
            "display": "masked_by_default",
        },
        "CONFIDENTIAL": {
            "encryption": "recommended",
            "access_log": "recommended",
            "sharing": "internal_only",
            "backup": "encrypted_recommended",
            "display": "visible_to_authorized",
        },
        "INTERNAL": {
            "encryption": "optional",
            "access_log": "optional",
            "sharing": "internal_only",
            "backup": "standard",
            "display": "visible_to_authorized",
        },
        "PUBLIC": {
            "encryption": "not_required",
            "access_log": "not_required",
            "sharing": "unrestricted",
            "backup": "standard",
            "display": "visible_to_all",
        },
    }

    async def validate_access(
        self,
        entity_type: str,
        field_name: str,
        operation: str,
        user_clearance: str,
    ) -> bool:
        """Validate access based on classification."""
        classification = SensitiveFieldClassifier.classify(field_name)
        rules = self.RULES.get(classification, {})

        clearance_levels = ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED", "SECRET"]
        user_level = clearance_levels.index(user_clearance)
        required_level = clearance_levels.index(classification)

        return user_level >= required_level
```

---

## 8. Privacy Impact Assessment

### 8.1 PIA Framework

```python
class PrivacyImpactAssessment:
    """Framework for privacy impact assessments."""

    PIA_QUESTIONS = {
        "data_collection": [
            "What personal data is being collected?",
            "What is the legal basis for collection?",
            "Is consent required and obtained?",
            "Is data collection necessary for the purpose?",
        ],
        "data_use": [
            "How will the data be used?",
            "Is the use compatible with the original purpose?",
            "Will data be shared with third parties?",
            "Will data be used for automated decision-making?",
        ],
        "data_storage": [
            "Where is the data stored?",
            "How long will the data be retained?",
            "What security measures are in place?",
            "Is encryption applied?",
        ],
        "data_sharing": [
            "Who has access to the data?",
            "Is cross-border transfer involved?",
            "What data processing agreements are in place?",
        ],
        "data_subject_rights": [
            "Can data subjects access their data?",
            "Can data subjects rectify their data?",
            "Can data subjects delete their data?",
            "Can data subjects port their data?",
        ],
    }

    async def conduct_pia(
        self,
        feature_name: str,
        data_flows: list[DataFlow],
    ) -> PIAReport:
        """Conduct a privacy impact assessment."""
        report = PIAReport(feature_name=feature_name)

        for flow in data_flows:
            flow_assessment = self._assess_data_flow(flow)
            report.add_flow_assessment(flow_assessment)

        report.risk_level = self._calculate_risk_level(report)
        report.recommendations = self._generate_recommendations(report)

        return report
```

---

## 9. Data Access Request Handling

### 9.1 Access Request Types

| Request Type | GDPR Article | Response Time | Process |
|---|---|---|---|
| **Right of Access** | Article 15 | 30 days | Export all user data |
| **Right to Rectification** | Article 16 | 30 days | Update user data |
| **Right to Erasure** | Article 17 | 30 days | Anonymize/delete user data |
| **Right to Restriction** | Article 18 | 30 days | Restrict data processing |
| **Right to Data Portability** | Article 20 | 30 days | Export in machine-readable format |
| **Right to Object** | Article 21 | 30 days | Stop processing data |

### 9.2 Request Processing

```python
class DataAccessRequestHandler:
    """Handles data access requests."""

    async def handle_access_request(
        self,
        user_id: UUID,
        request_type: str,
        session: AsyncSession,
    ) -> RequestResult:
        """Process a data access request."""
        # 1. Log the request
        await self._log_request(user_id, request_type, session)

        # 2. Verify identity
        if not await self._verify_identity(user_id, session):
            raise IdentityVerificationError()

        # 3. Process based on type
        if request_type == "access":
            return await self._handle_access(user_id, session)
        elif request_type == "rectification":
            return await self._handle_rectification(user_id, session)
        elif request_type == "erasure":
            return await self._handle_erasure(user_id, session)
        elif request_type == "portability":
            return await self._handle_portability(user_id, session)
        elif request_type == "restriction":
            return await self._handle_restriction(user_id, session)
        elif request_type == "objection":
            return await self._handle_objection(user_id, session)
        else:
            raise UnsupportedRequestTypeError(request_type)

    async def _handle_access(
        self,
        user_id: UUID,
        session: AsyncSession,
    ) -> RequestResult:
        """Handle right of access request."""
        # Collect all user data
        data = {
            "profile": await self._get_user_profile(user_id, session),
            "enrollments": await self._get_user_enrollments(user_id, session),
            "progress": await self._get_user_progress(user_id, session),
            "assessments": await self._get_user_assessments(user_id, session),
            "certificates": await self._get_user_certificates(user_id, session),
            "notifications": await self._get_user_notifications(user_id, session),
            "accessibility": await self._get_user_accessibility(user_id, session),
            "settings": await self._get_user_settings(user_id, session),
        }

        # Export as JSON
        export_path = await self._export_user_data_json(data, user_id)

        return RequestResult(
            status="completed",
            export_path=str(export_path),
            message="Your data export is ready for download.",
        )

    async def _handle_portability(
        self,
        user_id: UUID,
        session: AsyncSession,
    ) -> RequestResult:
        """Handle data portability request."""
        # Export in machine-readable format (JSON)
        data = await self._collect_all_user_data(user_id, session)

        export_path = await self._export_machine_readable(data, user_id)

        return RequestResult(
            status="completed",
            export_path=str(export_path),
            format="json",
            message="Your data is ready for transfer in JSON format.",
        )
```

---

## 10. Cross-Domain Data Sharing Rules

### 10.1 Sharing Matrix

| Source Domain | Target Domain | Allowed? | Conditions |
|---|---|---|---|
| Identity | Authorization | Yes | User ID only |
| Identity | Learning | Yes | User ID, display_name |
| Learning | Assessment | Yes | User ID, course context |
| Assessment | Learning | Yes | Results for progress |
| Learning | Analytics | Yes | Aggregated/anonymized |
| Audit | Any | No | Audit data never shared |
| Security | Admin | Yes | Security admin only |
| Configuration | Any | Read-only | Internal use |
| Plugin | Platform | Yes | Sandboxed access |

### 10.2 Data Sharing Gateway

```python
class DataSharingGateway:
    """Controls cross-domain data sharing."""

    SHARING_MATRIX = {
        ("identity", "authorization"): {
            "allowed_fields": ["id", "email"],
            "conditions": ["user_id_must_match"],
        },
        ("identity", "learning"): {
            "allowed_fields": ["id", "display_name", "email"],
            "conditions": ["enrollment_required"],
        },
        ("learning", "assessment"): {
            "allowed_fields": ["id", "course_id", "module_id"],
            "conditions": ["enrollment_required"],
        },
        ("assessment", "learning"): {
            "allowed_fields": ["score", "passed", "completed_at"],
            "conditions": ["same_user"],
        },
        ("learning", "analytics"): {
            "allowed_fields": ["enrollment_count", "completion_rate", "avg_score"],
            "conditions": ["aggregated_only"],
        },
    }

    def check_sharing(
        self,
        source_domain: str,
        target_domain: str,
        requested_fields: list[str],
    ) -> SharingDecision:
        """Check if data sharing is allowed."""
        matrix_key = (source_domain, target_domain)
        rules = self.SHARING_MATRIX.get(matrix_key)

        if rules is None:
            return SharingDecision(
                allowed=False,
                reason=f"No sharing rule defined for {source_domain} → {target_domain}",
            )

        allowed_fields = set(rules["allowed_fields"])
        requested = set(requested_fields)

        if requested.issubset(allowed_fields):
            return SharingDecision(
                allowed=True,
                fields=list(requested),
                conditions=rules["conditions"],
            )

        disallowed = requested - allowed_fields
        return SharingDecision(
            allowed=False,
            reason=f"Fields not allowed: {disallowed}",
            allowed_subset=list(requested & allowed_fields),
        )
```

---

## 11. Governance Reporting

### 11.1 Governance Dashboard Metrics

```python
GOVERNANCE_METRICS = {
    "data_quality": {
        "overall_score": "Weighted average of all quality dimensions",
        "accuracy_rate": "Percentage of valid records",
        "completeness_rate": "Percentage of required fields populated",
        "freshness_score": "Average age of records vs retention policy",
    },
    "compliance": {
        "access_requests_pending": "Number of pending data access requests",
        "erasure_requests_pending": "Number of pending erasure requests",
        "retention_violations": "Records past retention period",
        "classification_coverage": "Percentage of data classified",
    },
    "security": {
        "encryption_coverage": "Percentage of sensitive data encrypted",
        "access_audit_coverage": "Percentage of data access audited",
        "key_rotation_status": "Days since last key rotation",
        "backup_freshness": "Hours since last successful backup",
    },
    "lifecycle": {
        "archived_records": "Total archived records",
        "pending_purge": "Records pending purge",
        "active_lifecycle_violations": "Records in wrong lifecycle state",
    },
}
```

### 11.2 Governance Report

```python
class GovernanceReport:
    """Generates governance compliance reports."""

    async def generate(
        self,
        session: AsyncSession,
        period_days: int = 30,
    ) -> Report:
        """Generate governance report."""
        report = Report(
            title="Data Governance Report",
            period_days=period_days,
            generated_at=datetime.utcnow(),
        )

        # Data quality metrics
        quality = await self.quality_monitor.run_quality_checks(session)
        report.add_section("Data Quality", quality.to_dict())

        # Compliance metrics
        compliance = await self._assess_compliance(session)
        report.add_section("Compliance", compliance)

        # Retention status
        retention = await self._assess_retention(session)
        report.add_section("Retention", retention)

        # Security posture
        security = await self._assess_security(session)
        report.add_section("Security", security)

        # Recommendations
        report.recommendations = self._generate_recommendations(report)

        return report
```

---

## 12. Policy Review Schedule

| Policy | Review Frequency | Owner | Last Reviewed |
|---|---|---|---|
| Data Classification | Quarterly | Security Admin | 2026-07-01 |
| Retention Schedule | Semi-annually | Platform Admin | 2026-06-01 |
| Privacy Controls | Quarterly | Legal/Admin | 2026-07-01 |
| Security Standards | Quarterly | Security Admin | 2026-07-01 |
| Access Controls | Monthly | Security Admin | 2026-07-15 |
| Quality Standards | Semi-annually | Data Owners | 2026-06-01 |
| Disposal Procedures | Annually | Legal/Admin | 2026-01-01 |
| Sharing Rules | Quarterly | Platform Admin | 2026-07-01 |

---

*This handbook defines the complete data governance framework for AuthShield Lab.*
