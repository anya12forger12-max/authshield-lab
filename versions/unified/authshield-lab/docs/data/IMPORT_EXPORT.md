# Import/Export Framework — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

AuthShield Lab supports importing and exporting data in multiple formats for
portability, interoperability, and backup purposes. The framework includes
validation, compatibility checking, version detection, and dry-run mode.

### 1.1 Supported Formats

| Format | Extension | Use Case | Encoding |
|---|---|---|---|
| JSON | `.json` | Primary interchange format | UTF-8 |
| CSV | `.csv` | Spreadsheet-compatible export | UTF-8 with BOM |
| QTI | `.xml` | Assessment interchange (QTI 2.1) | UTF-8 |
| SCORM | `.zip` | Course packaging (SCORM 1.2/2004) | UTF-8 |

---

## 2. Import Framework

### 2.1 Import Architecture

```python
class ImportManager:
    """Manages data import operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.validators = ValidatorRegistry()
        self.parsers = ParserRegistry()
        self.migrators = FormatMigratorRegistry()

    async def import_data(
        self,
        file_path: Path,
        import_type: str,
        options: ImportOptions,
    ) -> ImportResult:
        """Execute import operation."""
        # Step 1: Detect format version
        format_info = await self._detect_format(file_path, import_type)

        # Step 2: Migrate if needed
        if format_info.version < CURRENT_VERSION:
            data = await self._migrate_format(
                file_path, format_info, import_type
            )
        else:
            data = await self._parse_file(file_path, format_info)

        # Step 3: Validate
        validation = await self._validate(data, import_type, options)

        if not validation.is_valid and not options.force:
            return ImportResult(
                status="validation_failed",
                errors=validation.errors,
                warnings=validation.warnings,
            )

        # Step 4: Dry run
        if options.dry_run:
            return ImportResult(
                status="dry_run",
                preview=self._generate_preview(data, import_type),
                validation=validation,
            )

        # Step 5: Execute import
        result = await self._execute_import(data, import_type, options)

        # Step 6: Post-import validation
        post_validation = await self._post_import_validate(result)

        return ImportResult(
            status="success",
            imported_count=result.imported_count,
            updated_count=result.updated_count,
            skipped_count=result.skipped_count,
            errors=result.errors,
            warnings=validation.warnings + post_validation.warnings,
        )

    async def _detect_format(self, file_path: Path, import_type: str) -> FormatInfo:
        """Auto-detect import format and version."""
        suffix = file_path.suffix.lower()

        if suffix == ".json":
            return await self._detect_json_format(file_path, import_type)
        elif suffix == ".csv":
            return FormatInfo(format="csv", version="1.0", encoding="utf-8")
        elif suffix == ".xml":
            return await self._detect_qti_format(file_path)
        elif suffix == ".zip":
            return await self._detect_scorm_format(file_path)
        else:
            raise UnsupportedFormatError(suffix)

    async def _detect_json_format(
        self, file_path: Path, import_type: str
    ) -> FormatInfo:
        """Detect JSON format version from metadata."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        version = data.get("version", "1.0.0")
        format_type = data.get("format", import_type)

        return FormatInfo(
            format=format_type,
            version=version,
            encoding="utf-8",
            metadata=data.get("metadata", {}),
        )
```

### 2.2 Import Types

| Type | Description | Key Entities | Validation Rules |
|---|---|---|---|
| `course` | Import course with modules, lessons, assessments | courses, modules, lessons, assessments, questions | Referential integrity, required fields |
| `assessment` | Import assessment with questions (QTI) | assessments, questions, options | QTI schema compliance |
| `configuration` | Import system settings | configurations, settings, feature_flags | Key uniqueness, type validation |
| `localization` | Import translation pack | localization_keys, translations | Key format, language code |
| `accessibility` | Import accessibility profile | accessibility_profiles, a11y_settings | Value ranges, enum validation |
| `plugin` | Import plugin package | plugins, plugin_versions, plugin_configs | Dependency check, version compat |
| `report_template` | Import report template | report_templates, report_data_sources | Schema validation |
| `backup` | Import full backup archive | All entities | Integrity check, version compat |
| `institution` | Import institution data | institutions, courses, enrollments | Org hierarchy, referential integrity |

### 2.3 Import Options

```python
@dataclass
class ImportOptions:
    """Configuration options for import operations."""
    
    dry_run: bool = False           # Validate without importing
    force: bool = False             # Skip non-critical validation errors
    overwrite_existing: bool = False # Overwrite existing entities
    merge_strategy: str = "skip"    # skip, overwrite, merge
    skip_validation: bool = False   # Skip validation (dangerous)
    create_missing: bool = True     # Create referenced entities that don't exist
    batch_size: int = 100           # Batch size for bulk operations
    notify_user: bool = True        # Send notification on completion
    archive_overwritten: bool = True # Archive existing before overwrite
    preserve_ids: bool = False      # Keep original IDs (for restore)
    id_mapping: dict = None         # Custom ID mapping
```

---

## 3. Export Framework

### 3.1 Export Architecture

```python
class ExportManager:
    """Manages data export operations."""

    async def export_data(
        self,
        export_type: str,
        options: ExportOptions,
    ) -> ExportResult:
        """Execute export operation."""
        # Step 1: Gather data
        data = await self._gather_export_data(export_type, options)

        # Step 2: Transform
        transformed = await self._transform_export(data, export_type, options)

        # Step 3: Serialize
        output_path = await self._serialize(
            transformed, export_type, options.format, options.output_path
        )

        # Step 4: Compute checksum
        checksum = IntegrityChecker.compute_file_checksum(output_path)

        # Step 5: Create export manifest
        manifest = ExportManifest(
            export_type=export_type,
            format=options.format,
            version=CURRENT_VERSION,
            checksum=checksum,
            file_path=str(output_path),
            record_count=len(data),
            exported_at=datetime.utcnow(),
        )

        return ExportResult(manifest=manifest, output_path=output_path)
```

### 3.2 Export Options

```python
@dataclass
class ExportOptions:
    """Configuration options for export operations."""
    
    format: str = "json"           # json, csv, qti, scorm
    output_path: Optional[Path] = None  # Auto-generated if None
    include_deleted: bool = False   # Include soft-deleted records
    include_metadata: bool = True   # Include export metadata
    compress: bool = True           # Compress output
    encrypt: bool = False           # Encrypt output
    anonymize: bool = False         # Anonymize PII fields
    date_range: Optional[tuple] = None  # (start, end) date filter
    entity_filter: Optional[list] = None  # Specific entity IDs
    pretty_print: bool = True       # Pretty-print JSON
    encoding: str = "utf-8"         # Output encoding
```

### 3.3 Export Categories

| Category | Description | Includes |
|---|---|---|
| `full_backup` | Complete database export | All entities, all data |
| `course` | Single course export | Course, modules, lessons, assessments, questions |
| `user_data` | User data package (GDPR) | User profile, enrollments, progress, certificates, results |
| `assessment` | Assessment with questions | Assessment, questions, options, rubrics |
| `configuration` | System settings | Configs, settings, feature flags, themes |
| `localization` | Translation pack | Localization keys, translations |
| `analytics` | Analytics data | Reports, analytics snapshots, dashboards |
| `audit_log` | Audit trail export | Audit entries with chain |
| `plugin_data` | Plugin data | Plugin configs, hook registrations |

---

## 4. Validation Framework

### 4.1 Schema Validation

```python
class SchemaValidator:
    """Validates import data against expected schema."""

    SCHEMAS = {
        "course": {
            "required": ["version", "format", "course"],
            "course": {
                "required": ["title", "status"],
                "optional": [
                    "description", "short_description", "slug",
                    "difficulty", "estimated_hours", "language",
                    "tags", "metadata",
                ],
            },
        },
        "assessment": {
            "required": ["version", "format", "assessment"],
            "assessment": {
                "required": ["title", "assessment_type", "questions"],
                "questions": {
                    "required": ["content", "question_type"],
                    "optional": [
                        "explanation", "points", "difficulty",
                        "options", "hint",
                    ],
                },
            },
        },
        "configuration": {
            "required": ["version", "format", "configurations"],
            "configurations": {
                "required": ["config_key", "config_value", "value_type"],
            },
        },
        "localization": {
            "required": ["version", "format", "language_code", "translations"],
            "translations": {
                "required": ["key", "value"],
                "optional": ["context", "description"],
            },
        },
    }

    def validate(self, data: dict, import_type: str) -> ValidationResult:
        """Validate data against schema."""
        schema = self.SCHEMAS.get(import_type)
        if schema is None:
            raise UnsupportedImportTypeError(import_type)

        errors = []
        warnings = []

        # Check required top-level fields
        for field in schema.get("required", []):
            if field not in data:
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field missing: {field}",
                    severity="error",
                ))

        # Validate nested structures
        for field, field_schema in schema.items():
            if field in ("required", "optional"):
                continue
            if field in data:
                field_errors = self._validate_field(
                    data[field], field_schema, field
                )
                errors.extend(field_errors)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
```

### 4.2 Referential Integrity Validation

```python
class ReferentialValidator:
    """Validates foreign key relationships in import data."""

    async def validate(
        self,
        data: dict,
        import_type: str,
        session: AsyncSession,
    ) -> ValidationResult:
        """Check referential integrity."""
        errors = []

        if import_type == "course":
            # Check module references
            for module in data.get("modules", []):
                if "course_id" in module:
                    exists = await self._check_entity_exists(
                        session, "courses", module["course_id"]
                    )
                    if not exists:
                        errors.append(ValidationError(
                            field=f"modules[{module.get('title')}].course_id",
                            message=f"Referenced course not found: {module['course_id']}",
                        ))

            # Check lesson references
            for lesson in data.get("lessons", []):
                if "module_id" in lesson:
                    exists = await self._check_entity_exists(
                        session, "course_modules", lesson["module_id"]
                    )
                    if not exists:
                        errors.append(ValidationError(
                            field=f"lessons[{lesson.get('title')}].module_id",
                            message=f"Referenced module not found: {lesson['module_id']}",
                        ))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
        )

    async def _check_entity_exists(
        self, session: AsyncSession, table: str, entity_id: str
    ) -> bool:
        """Check if entity exists in database."""
        result = await session.execute(
            text(f"SELECT 1 FROM {table} WHERE id = :id AND is_deleted = 0"),
            {"id": entity_id},
        )
        return result.scalar() is not None
```

### 4.3 Business Rules Validation

```python
class BusinessRuleValidator:
    """Validates business rules for import data."""

    RULES = {
        "course": [
            "course_title_not_empty",
            "course_status_valid",
            "modules_sorted_correctly",
            "lessons_have_content",
            "assessments_have_questions",
            "no_circular_prerequisites",
        ],
        "assessment": [
            "assessment_has_questions",
            "questions_have_options",
            "correct_options_exist",
            "score_totals_match_max",
            "passing_score_valid",
        ],
        "configuration": [
            "config_keys_unique",
            "config_values_type_match",
            "sensitive_configs_encrypted",
        ],
    }

    def validate(self, data: dict, import_type: str) -> ValidationResult:
        """Run business rule validations."""
        rules = self.RULES.get(import_type, [])
        errors = []
        warnings = []

        for rule_name in rules:
            rule_method = getattr(self, f"_rule_{rule_name}", None)
            if rule_method:
                result = rule_method(data)
                errors.extend(result.errors)
                warnings.extend(result.warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _rule_course_title_not_empty(self, data: dict) -> ValidationResult:
        course = data.get("course", {})
        title = course.get("title", "").strip()
        if not title:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    field="course.title",
                    message="Course title cannot be empty",
                )],
            )
        return ValidationResult(is_valid=True)

    def _rule_modules_sorted_correctly(self, data: dict) -> ValidationResult:
        modules = data.get("modules", [])
        sort_orders = [m.get("sort_order", 0) for m in modules]
        if sort_orders != sorted(sort_orders):
            return ValidationResult(
                is_valid=True,
                warnings=[ValidationWarning(
                    field="modules",
                    message="Module sort orders are not sequential, will be renumbered",
                )],
            )
        return ValidationResult(is_valid=True)

    def _rule_assessments_have_questions(self, data: dict) -> ValidationResult:
        assessments = data.get("assessments", [])
        for assessment in assessments:
            questions = assessment.get("questions", [])
            if not questions:
                return ValidationResult(
                    is_valid=False,
                    errors=[ValidationError(
                        field=f"assessment[{assessment.get('title')}].questions",
                        message="Assessment must have at least one question",
                    )],
                )
        return ValidationResult(is_valid=True)
```

---

## 5. Compatibility Rules

### 5.1 Version Compatibility Matrix

```python
COMPATIBILITY_MATRIX = {
    "course": {
        "1.0": {"min_platform": "1.0.0", "max_platform": "2.0.0"},
        "1.1": {"min_platform": "1.1.0", "max_platform": "2.0.0"},
        "2.0": {"min_platform": "2.0.0", "max_platform": None},
    },
    "assessment": {
        "1.0": {"min_platform": "1.0.0", "max_platform": "2.0.0"},
        "2.0": {"min_platform": "2.0.0", "max_platform": None},
    },
    "configuration": {
        "1.0": {"min_platform": "1.0.0", "max_platform": "2.0.0"},
        "2.0": {"min_platform": "2.0.0", "max_platform": None},
    },
    "localization": {
        "1.0": {"min_platform": "1.0.0", "max_platform": None},
    },
}

class CompatibilityChecker:
    """Checks version compatibility for imports."""

    def check(
        self,
        import_type: str,
        format_version: str,
        platform_version: str,
    ) -> CompatibilityResult:
        """Check if import is compatible with current platform."""
        matrix = COMPATIBILITY_MATRIX.get(import_type, {})
        version_info = matrix.get(format_version)

        if version_info is None:
            return CompatibilityResult(
                status="unknown_version",
                message=f"Unknown format version: {format_version}",
                compatible=False,
            )

        min_platform = version_info.get("min_platform")
        max_platform = version_info.get("max_platform")

        if min_platform and platform_version < min_platform:
            return CompatibilityResult(
                status="platform_too_old",
                message=f"Platform version {platform_version} < minimum {min_platform}",
                compatible=False,
            )

        if max_platform and platform_version > max_platform:
            return CompatibilityResult(
                status="format_too_old",
                message=f"Format version {format_version} deprecated for platform {platform_version}",
                compatible=True,
                warnings=["Format may need migration. Auto-migration will be attempted."],
            )

        return CompatibilityResult(
            status="compatible",
            message="Import is compatible",
            compatible=True,
        )
```

---

## 6. Version Detection & Migration

### 6.1 Auto-Version Detection

```python
class FormatDetector:
    """Auto-detects import format version."""

    VERSION_MARKERS = {
        "course": {
            "1.0": ["course", "modules"],
            "1.1": ["course", "modules", "prerequisites"],
            "2.0": ["version", "format", "course", "modules", "assessments"],
        },
        "assessment": {
            "1.0": ["assessment", "questions"],
            "2.0": ["version", "format", "assessment", "questions", "rubrics"],
        },
    }

    def detect_version(self, data: dict, import_type: str) -> str:
        """Detect format version from data structure."""
        # Explicit version field
        if "version" in data:
            return data["version"]

        # Heuristic detection based on fields present
        markers = self.VERSION_MARKERS.get(import_type, {})

        for version, required_fields in sorted(markers.items(), reverse=True):
            if all(field in data for field in required_fields):
                return version

        return "1.0"  # Default to earliest version
```

### 6.2 Format Migration

```python
class FormatMigrator:
    """Migrates older import formats to current version."""

    MIGRATIONS = {
        ("course", "1.0", "2.0"): "migrate_course_1_0_to_2_0",
        ("course", "1.1", "2.0"): "migrate_course_1_1_to_2_0",
        ("assessment", "1.0", "2.0"): "migrate_assessment_1_0_to_2_0",
        ("configuration", "1.0", "2.0"): "migrate_config_1_0_to_2_0",
    }

    async def migrate(
        self,
        data: dict,
        import_type: str,
        from_version: str,
        to_version: str,
    ) -> dict:
        """Migrate data from one version to another."""
        migration_key = (import_type, from_version, to_version)
        migration_func_name = self.MIGRATIONS.get(migration_key)

        if migration_func_name is None:
            raise UnsupportedMigrationError(import_type, from_version, to_version)

        migration_func = getattr(self, migration_func_name)
        return await migration_func(data)

    async def migrate_course_1_0_to_2_0(self, data: dict) -> dict:
        """Migrate course format from 1.0 to 2.0."""
        migrated = {
            "version": "2.0",
            "format": "authshield-course",
            "exported_at": data.get("exported_at", datetime.utcnow().isoformat()),
            "course": {
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "status": data.get("status", "draft"),
                "difficulty": data.get("difficulty", "beginner"),
                "language": data.get("language", "en"),
            },
            "modules": [],
            "lessons": [],
            "assessments": [],
            "questions": [],
        }

        # Migrate modules
        for idx, module_data in enumerate(data.get("modules", [])):
            module_id = str(uuid.uuid4())
            migrated["modules"].append({
                "id": module_id,
                "title": module_data.get("title", f"Module {idx + 1}"),
                "description": module_data.get("description", ""),
                "sort_order": idx,
            })

            # Migrate lessons
            for lesson_idx, lesson_data in enumerate(module_data.get("lessons", [])):
                migrated["lessons"].append({
                    "id": str(uuid.uuid4()),
                    "module_id": module_id,
                    "title": lesson_data.get("title", f"Lesson {lesson_idx + 1}"),
                    "content_type": lesson_data.get("type", "text"),
                    "content": lesson_data.get("content", ""),
                    "sort_order": lesson_idx,
                })

        return migrated
```

---

## 7. Error Reporting

### 7.1 Import Error Log

```python
class ImportErrorLogger:
    """Detailed import error logging."""

    def __init__(self):
        self.errors: list[ImportError] = []
        self.warnings: list[ImportWarning] = []
        self.info: list[ImportInfo] = []

    def log_error(
        self,
        field: str,
        message: str,
        severity: str,
        row_number: Optional[int] = None,
        value: Optional[Any] = None,
    ):
        """Log an import error."""
        self.errors.append(ImportError(
            field=field,
            message=message,
            severity=severity,
            row_number=row_number,
            value=value,
            timestamp=datetime.utcnow(),
        ))

    def log_warning(self, field: str, message: str, row_number: Optional[int] = None):
        """Log an import warning."""
        self.warnings.append(ImportWarning(
            field=field,
            message=message,
            row_number=row_number,
            timestamp=datetime.utcnow(),
        ))

    def generate_report(self) -> ImportErrorReport:
        """Generate comprehensive error report."""
        return ImportErrorReport(
            total_errors=len(self.errors),
            total_warnings=len(self.warnings),
            errors=self.errors,
            warnings=self.warnings,
            summary=self._generate_summary(),
        )

    def _generate_summary(self) -> dict:
        """Generate error summary by category."""
        summary = {}
        for error in self.errors:
            category = error.field.split("[")[0]
            if category not in summary:
                summary[category] = {"errors": 0, "warnings": 0}
            summary[category]["errors"] += 1

        for warning in self.warnings:
            category = warning.field.split("[")[0]
            if category not in summary:
                summary[category] = {"errors": 0, "warnings": 0}
            summary[category]["warnings"] += 1

        return summary
```

### 7.2 Dry-Run Mode

```python
class DryRunProcessor:
    """Preview import without making changes."""

    async def preview(
        self,
        data: dict,
        import_type: str,
        session: AsyncSession,
    ) -> DryRunPreview:
        """Generate preview of import changes."""
        preview = DryRunPreview()

        # Simulate import
        for entity_type, entities in data.items():
            if entity_type in ("version", "format", "metadata"):
                continue

            type_preview = EntityTypePreview(name=entity_type)

            for entity in entities:
                entity_preview = await self._preview_entity(
                    entity_type, entity, session
                )
                type_preview.entities.append(entity_preview)

            preview.entity_types.append(type_preview)

        # Generate summary
        preview.summary = {
            "total_entities": sum(
                len(ep.entities) for ep in preview.entity_types
            ),
            "creates": sum(
                ep.creates for ep in preview.entity_types
            ),
            "updates": sum(
                ep.updates for ep in preview.entity_types
            ),
            "skips": sum(
                ep.skips for ep in preview.entity_types
            ),
            "conflicts": sum(
                ep.conflicts for ep in preview.entity_types
            ),
        }

        return preview

    async def _preview_entity(
        self,
        entity_type: str,
        entity: dict,
        session: AsyncSession,
    ) -> EntityPreview:
        """Preview what will happen to a single entity."""
        entity_id = entity.get("id")

        if entity_id:
            # Check if exists
            exists = await self._check_exists(entity_type, entity_id, session)
            if exists:
                return EntityPreview(
                    id=entity_id,
                    action="update",
                    changes=self._compute_changes(entity, exists),
                )
            else:
                return EntityPreview(
                    id=entity_id,
                    action="create",
                    data=entity,
                )
        else:
            return EntityPreview(
                action="create",
                data=entity,
            )
```

---

## 8. Import Progress Tracking

### 8.1 Progress Reporting

```python
class ImportProgressTracker:
    """Tracks and reports import progress."""

    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = datetime.utcnow()
        self.step_details: list[StepDetail] = []

    def update(self, step: int, message: str, details: Optional[dict] = None):
        """Update progress."""
        self.current_step = step
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()

        self.step_details.append(StepDetail(
            step=step,
            message=message,
            details=details,
            timestamp=datetime.utcnow(),
            elapsed_seconds=elapsed,
        ))

    @property
    def percentage(self) -> float:
        return (self.current_step / self.total_steps * 100) if self.total_steps > 0 else 0

    @property
    def eta_seconds(self) -> Optional[float]:
        if self.current_step == 0:
            return None
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        rate = self.current_step / elapsed
        remaining = self.total_steps - self.current_step
        return remaining / rate if rate > 0 else None

    def to_dict(self) -> dict:
        return {
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "percentage": round(self.percentage, 1),
            "elapsed_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "eta_seconds": self.eta_seconds,
            "latest_message": self.step_details[-1].message if self.step_details else None,
        }
```

---

## 9. CSV Import/Export

### 9.1 CSV Export

```python
class CSVExporter:
    """Export data to CSV format."""

    async def export(
        self,
        data: list[dict],
        output_path: Path,
        columns: Optional[list[str]] = None,
    ) -> Path:
        """Export data to CSV."""
        if not data:
            raise EmptyExportError("No data to export")

        # Auto-detect columns if not specified
        if columns is None:
            columns = list(data[0].keys())

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data)

        return output_path
```

### 9.2 CSV Import

```python
class CSVImporter:
    """Import data from CSV format."""

    async def import_csv(
        self,
        file_path: Path,
        import_type: str,
        options: ImportOptions,
    ) -> ImportResult:
        """Import from CSV file."""
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Convert CSV rows to structured data
        data = self._csv_to_structured(rows, import_type)

        # Use standard import pipeline
        return await self.import_manager.import_data_from_dict(
            data, import_type, options
        )

    def _csv_to_structured(self, rows: list[dict], import_type: str) -> dict:
        """Convert flat CSV rows to structured import format."""
        if import_type == "localization":
            return {
                "version": "1.0",
                "format": "authshield-localization",
                "language_code": rows[0].get("language_code", "en") if rows else "en",
                "translations": [
                    {
                        "key": row.get("key", ""),
                        "value": row.get("value", ""),
                        "context": row.get("context", ""),
                    }
                    for row in rows
                ],
            }

        elif import_type == "configuration":
            return {
                "version": "2.0",
                "format": "authshield-configuration",
                "configurations": [
                    {
                        "config_key": row.get("key", ""),
                        "config_value": row.get("value", ""),
                        "value_type": row.get("type", "string"),
                    }
                    for row in rows
                ],
            }

        return {"version": "1.0", "data": rows}
```

---

## 10. QTI Import (Assessments)

### 10.1 QTI 2.1 Support

```python
class QTIImporter:
    """Import assessments in QTI 2.1 format."""

    async def import_qti(
        self,
        file_path: Path,
        options: ImportOptions,
    ) -> ImportResult:
        """Import QTI assessment package."""
        import xml.etree.ElementTree as ET

        tree = ET.parse(file_path)
        root = tree.getroot()

        # Parse QTI assessment
        assessment_data = self._parse_assessment(root)

        # Convert to AuthShield format
        authshield_data = self._qti_to_authshield(assessment_data)

        # Use standard import pipeline
        return await self.import_manager.import_data_from_dict(
            authshield_data, "assessment", options
        )

    def _parse_assessment(self, root: ET.Element) -> dict:
        """Parse QTI assessment element."""
        assessment = root.find(".//{http://www.imsglobal.org/xsd/ims_qtiasiv1p2}assessment")
        if assessment is None:
            raise InvalidQTIError("No assessment element found")

        return {
            "title": assessment.get("title", ""),
            "ident": assessment.get("ident", ""),
            "sections": self._parse_sections(assessment),
        }

    def _qti_to_authshield(self, qti_data: dict) -> dict:
        """Convert QTI format to AuthShield format."""
        questions = []
        for section in qti_data.get("sections", []):
            for item in section.get("items", []):
                question = {
                    "content": item.get("title", ""),
                    "question_type": self._map_qti_type(item.get("type", "")),
                    "options": [],
                    "points": 1.0,
                }

                for response in item.get("responses", []):
                    question["options"].append({
                        "content": response.get("text", ""),
                        "is_correct": response.get("score", 0) > 0,
                    })

                questions.append(question)

        return {
            "version": "2.0",
            "format": "authshield-assessment",
            "assessment": {
                "title": qti_data["title"],
                "assessment_type": "quiz",
                "questions": questions,
            },
        }
```

---

## 11. SCORM Import (Courses)

### 11.1 SCORM 1.2/2004 Support

```python
class SCORMImporter:
    """Import courses in SCORM format."""

    async def import_scorm(
        self,
        file_path: Path,
        options: ImportOptions,
    ) -> ImportResult:
        """Import SCORM course package."""
        import zipfile

        with zipfile.ZipFile(file_path, "r") as zf:
            # Parse IMS manifest
            manifest = self._parse_manifest(zf)

            # Extract course content
            content = self._extract_content(zf, manifest)

            # Convert to AuthShield format
            authshield_data = self._scorm_to_authshield(content)

            # Use standard import pipeline
            return await self.import_manager.import_data_from_dict(
                authshield_data, "course", options
            )

    def _parse_manifest(self, zf: zipfile.ZipFile) -> dict:
        """Parse imsmanifest.xml."""
        if "imsmanifest.xml" not in zf.namelist():
            raise InvalidSCORMError("No imsmanifest.xml found")

        with zf.open("imsmanifest.xml") as f:
            tree = ET.parse(f)

        root = tree.getroot()
        organizations = root.find(".//organizations")
        resources = root.find(".//resources")

        return {
            "organizations": self._parse_organizations(organizations),
            "resources": self._parse_resources(resources),
        }

    def _scorm_to_authshield(self, content: dict) -> dict:
        """Convert SCORM format to AuthShield format."""
        modules = []
        lessons = []

        for org in content.get("organizations", []):
            for item in org.get("items", []):
                module_id = str(uuid.uuid4())
                modules.append({
                    "id": module_id,
                    "title": item.get("title", ""),
                    "sort_order": len(modules),
                })

                for sub_item in item.get("children", []):
                    lessons.append({
                        "id": str(uuid.uuid4()),
                        "module_id": module_id,
                        "title": sub_item.get("title", ""),
                        "content_type": "interactive",
                        "sort_order": len(lessons),
                    })

        return {
            "version": "2.0",
            "format": "authshield-course",
            "course": {
                "title": content.get("title", "Imported Course"),
                "status": "draft",
                "difficulty": "beginner",
            },
            "modules": modules,
            "lessons": lessons,
        }
```

---

*This document defines the complete import/export framework for AuthShield Lab.*
