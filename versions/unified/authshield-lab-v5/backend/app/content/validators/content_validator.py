"""Content validators for the Content Studio module."""

from __future__ import annotations

from ...shared.validation.validator import ValidationResult


class ContentValidator:
    """Validates content entities against business rules."""

    def validate_title(self, title: str, max_length: int = 200) -> ValidationResult:
        """Validate that a title is non-empty and within the length limit."""
        result = ValidationResult()
        if not title or not title.strip():
            result.add_error("title", "Title is required.", "REQUIRED")
            return result
        title = title.strip()
        if len(title) > max_length:
            result.add_error(
                "title",
                f"Title must be {max_length} characters or fewer (got {len(title)}).",
                "MAX_LENGTH",
            )
        if len(title) < 3:
            result.add_error("title", "Title must be at least 3 characters.", "MIN_LENGTH")
        return result

    def validate_description(self, description: str, max_length: int = 5000) -> ValidationResult:
        """Validate description content and length."""
        result = ValidationResult()
        if not description or not description.strip():
            result.add_error("description", "Description is required.", "REQUIRED")
            return result
        if len(description) > max_length:
            result.add_error(
                "description",
                f"Description must be {max_length} characters or fewer (got {len(description)}).",
                "MAX_LENGTH",
            )
        return result

    def validate_learning_objectives(self, objectives: list[str]) -> ValidationResult:
        """Validate that at least one learning objective is provided."""
        result = ValidationResult()
        if not objectives:
            result.add_error(
                "learning_objectives",
                "At least one learning objective is required.",
                "REQUIRED",
            )
            return result
        for idx, obj in enumerate(objectives):
            if not obj or not obj.strip():
                result.add_error(
                    "learning_objectives",
                    f"Learning objective at index {idx} is empty.",
                    "EMPTY_ITEM",
                )
            elif len(obj) > 500:
                result.add_error(
                    "learning_objectives",
                    f"Learning objective at index {idx} exceeds 500 characters.",
                    "MAX_LENGTH",
                )
        return result

    def validate_quiz_questions(self, questions: list[dict]) -> ValidationResult:
        """Validate quiz questions have required fields and valid structure."""
        result = ValidationResult()
        if not questions:
            result.add_error("questions", "Quiz must have at least one question.", "REQUIRED")
            return result
        valid_types = {"mcq", "true_false", "short_answer", "matching"}
        total_points = 0.0
        for idx, q in enumerate(questions):
            q_text = q.get("question_text", "")
            if not q_text or not q_text.strip():
                result.add_error(
                    "questions",
                    f"Question at index {idx} is missing question_text.",
                    "MISSING_FIELD",
                )
            q_type = q.get("question_type", "")
            if q_type not in valid_types:
                result.add_error(
                    "questions",
                    f"Question at index {idx} has invalid type '{q_type}'.",
                    "INVALID_TYPE",
                )
            if q_type == "mcq":
                choices = q.get("choices", [])
                if len(choices) < 2:
                    result.add_error(
                        "questions",
                        f"MCQ at index {idx} must have at least 2 choices.",
                        "INVALID_CHOICES",
                    )
                correct = q.get("correct_answer", "")
                if correct not in choices:
                    result.add_error(
                        "questions",
                        f"MCQ at index {idx}: correct_answer must be one of the choices.",
                        "INVALID_ANSWER",
                    )
            correct_answer = q.get("correct_answer", "")
            if not correct_answer:
                result.add_error(
                    "questions",
                    f"Question at index {idx} is missing correct_answer.",
                    "MISSING_FIELD",
                )
            points = q.get("points", 1.0)
            if isinstance(points, (int, float)) and points > 0:
                total_points += float(points)
        if total_points <= 0:
            result.add_warning("questions", "Total quiz points should be greater than zero.")
        return result

    def validate_media_metadata(self, asset: dict) -> ValidationResult:
        """Validate media asset metadata fields."""
        result = ValidationResult()
        title = asset.get("title", "")
        if not title or not title.strip():
            result.add_error("title", "Media asset title is required.", "REQUIRED")
        media_type = asset.get("media_type", "")
        valid_types = {"image", "video", "audio", "document"}
        if media_type not in valid_types:
            result.add_error(
                "media_type",
                f"Invalid media_type '{media_type}'. Must be one of: {', '.join(sorted(valid_types))}",
                "INVALID_TYPE",
            )
        uri = asset.get("uri", "")
        if not uri or not uri.strip():
            result.add_error("uri", "Media asset URI is required.", "REQUIRED")
        alt_text = asset.get("alt_text", "")
        if media_type == "image" and (not alt_text or not alt_text.strip()):
            result.add_warning("alt_text", "Image assets should have alt_text for accessibility.")
        return result

    def validate_course_structure(self, course_data: dict) -> ValidationResult:
        """Validate overall course structure and required fields."""
        result = ValidationResult()
        title = course_data.get("title", "")
        title_result = self.validate_title(title)
        result.merge(title_result)
        description = course_data.get("description", "")
        desc_result = self.validate_description(description)
        result.merge(desc_result)
        objectives = course_data.get("learning_objectives", [])
        obj_result = self.validate_learning_objectives(objectives)
        result.merge(obj_result)
        diff_result = self.validate_difficulty(course_data.get("difficulty", ""))
        result.merge(diff_result)
        tags = course_data.get("tags", [])
        if tags:
            tag_result = self.validate_tags(tags)
            result.merge(tag_result)
        estimated_hours = course_data.get("estimated_hours", 0)
        if isinstance(estimated_hours, (int, float)) and estimated_hours < 0:
            result.add_error(
                "estimated_hours",
                "Estimated hours must be non-negative.",
                "INVALID_VALUE",
            )
        return result

    def validate_difficulty(self, difficulty: str) -> ValidationResult:
        """Validate difficulty level against allowed values."""
        result = ValidationResult()
        valid = {"beginner", "intermediate", "advanced", "expert"}
        if difficulty not in valid:
            result.add_error(
                "difficulty",
                f"Invalid difficulty '{difficulty}'. Must be one of: {', '.join(sorted(valid))}",
                "INVALID_VALUE",
            )
        return result

    def validate_tags(self, tags: list[str]) -> ValidationResult:
        """Validate tags: non-empty, unique, within length limits."""
        result = ValidationResult()
        if not tags:
            return result
        seen: set[str] = set()
        for idx, tag in enumerate(tags):
            tag_stripped = tag.strip() if isinstance(tag, str) else ""
            if not tag_stripped:
                result.add_error("tags", f"Tag at index {idx} is empty.", "EMPTY_ITEM")
                continue
            if len(tag_stripped) > 50:
                result.add_error(
                    "tags",
                    f"Tag at index {idx} exceeds 50 characters.",
                    "MAX_LENGTH",
                )
            tag_lower = tag_stripped.lower()
            if tag_lower in seen:
                result.add_warning("tags", f"Duplicate tag: '{tag_stripped}'.")
            seen.add(tag_lower)
        return result
