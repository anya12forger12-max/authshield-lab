"""AI assistant service — deterministic suggestions, analysis, and audit."""

from __future__ import annotations

import hashlib
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.ai_assistant import (
    AIGenerationAudit,
    AuthoringSuggestion,
    ContentConsistencyResult,
    ConsistencyIssue,
    CurriculumMappingSuggestion,
    GlossaryTerm,
    MetadataSuggestion,
    ReadingLevelAnalysis,
    SuggestionType,
)
from ..domain.events.optimization_events import AIGenerationRequested, ContentReviewCompleted
from ..domain.interfaces.optimization_interfaces import IAIAssistantRepository

logger = logging.getLogger(__name__)


def _count_syllables(word: str) -> int:
    """Estimate syllable count for a single English word."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


class AIAssistantService:
    """Deterministic AI assistant — generates suggestions using rule-based logic."""

    def __init__(self, repo: IAIAssistantRepository) -> None:
        self._repo = repo

    # ------------------------------------------------------------------
    # Suggestions
    # ------------------------------------------------------------------

    def generate_suggestion(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate an authoring suggestion from source material."""
        suggestion_type_str = data.get("suggestion_type", "outline")
        try:
            suggestion_type = SuggestionType(suggestion_type_str)
        except ValueError:
            suggestion_type = SuggestionType.OUTLINE

        source_material = data.get("source_material", "")

        if suggestion_type == SuggestionType.READING_LEVEL:
            content = self._generate_reading_level_suggestion(source_material)
        elif suggestion_type == SuggestionType.GLOSSARY:
            content = self._generate_glossary_suggestion(source_material)
        elif suggestion_type == SuggestionType.OBJECTIVES:
            content = self._generate_objectives_suggestion(source_material)
        elif suggestion_type == SuggestionType.TAGS:
            content = self._generate_tags_suggestion(source_material)
        elif suggestion_type == SuggestionType.QUIZ_QUESTION:
            content = self._generate_quiz_suggestion(source_material)
        elif suggestion_type == SuggestionType.OUTLINE:
            content = self._generate_outline_suggestion(source_material)
        else:
            content = f"AI suggestion for {suggestion_type.value}: review the source material for improvements."

        suggestion = AuthoringSuggestion(
            suggestion_type=suggestion_type,
            content=content,
            source_material=source_material[:500],
            confidence=round(min(0.95, 0.5 + len(source_material) / 2000.0), 2),
        )

        event = AIGenerationRequested(
            content_id=suggestion.id,
            ai_type=suggestion_type.value,
        )
        logger.info(
            "ai_suggestion_generated",
            extra={"suggestion_id": suggestion.id, "event_id": event.event_id},
        )
        result = self._repo.create_suggestion(suggestion.to_dict())
        return result

    def get_suggestion(self, suggestion_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_suggestion_by_id(suggestion_id)

    def list_suggestions(
        self,
        page: int = 1,
        per_page: int = 20,
        suggestion_type: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._repo.get_all_suggestions(
            page=page, per_page=per_page, suggestion_type=suggestion_type
        )

    def review_suggestion(self, suggestion_id: str, accepted: bool) -> Optional[dict[str, Any]]:
        """Review and accept/reject a suggestion."""
        suggestion = self._repo.get_suggestion_by_id(suggestion_id)
        if not suggestion:
            return None
        updates = {
            "reviewed": True,
            "accepted": accepted,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        result = self._repo.update_suggestion(suggestion_id, updates)
        event = ContentReviewCompleted(
            audit_id=suggestion_id,
            content_id=suggestion.get("source_material", ""),
            approved=accepted,
        )
        logger.info(
            "suggestion_reviewed",
            extra={"suggestion_id": suggestion_id, "event_id": event.event_id},
        )
        return result

    def delete_suggestion(self, suggestion_id: str) -> bool:
        return self._repo.delete_suggestion(suggestion_id)

    # ------------------------------------------------------------------
    # Reading Level Analysis
    # ------------------------------------------------------------------

    def analyze_reading_level(self, text: str) -> ReadingLevelAnalysis:
        """Perform Flesch-Kincaid, Gunning Fog, and Coleman-Liau analysis."""
        words = [w for w in re.split(r"\s+", text.strip()) if w]
        word_count = len(words)
        sentences = re.split(r"[.!?]+", text.strip())
        sentences = [s for s in sentences if s.strip()]
        sentence_count = max(1, len(sentences))
        syllable_count = sum(_count_syllables(w) for w in words)

        avg_syllables = syllable_count / max(1, word_count)
        avg_words_per_sentence = word_count / sentence_count

        flesch_kincaid = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables) - 15.59
        gunning_fog = 0.4 * (avg_words_per_sentence + 100.0 * (sum(1 for w in words if _count_syllables(w) >= 3) / max(1, word_count)))

        complex_words = sum(1 for w in words if _count_syllables(w) >= 3)
        coleman_liau = (0.0588 * (word_count / sentence_count * 100.0)) - (0.296 * (complex_words / max(1, word_count) * 100.0)) - 15.8

        analysis = ReadingLevelAnalysis(
            text=text[:2000],
            flesch_kincaid=round(max(0.0, flesch_kincaid), 2),
            gunning_fog=round(max(0.0, gunning_fog), 2),
            coleman_liau=round(max(0.0, coleman_liau), 2),
            word_count=word_count,
            sentence_count=sentence_count,
            syllable_count=syllable_count,
        )
        analysis.classify_grade()
        return analysis

    # ------------------------------------------------------------------
    # Glossary Extraction
    # ------------------------------------------------------------------

    def extract_glossary(self, text: str) -> list[dict[str, Any]]:
        """Extract potential glossary terms from text using simple heuristics."""
        terms: list[GlossaryTerm] = []
        sentences = re.split(r"[.!?]+", text)
        for sentence in sentences:
            matches = re.findall(
                r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s*(?:is|are|refers to|means)\s+(.+?)(?:\.|$)",
                sentence.strip(),
            )
            for term_text, definition in matches:
                term = GlossaryTerm(
                    term=term_text.strip(),
                    definition=definition.strip()[:200],
                    category="extracted",
                    source="text_analysis",
                    confidence=round(min(0.9, 0.4 + len(term_text) / 50.0), 2),
                )
                terms.append(term)
        return [t.to_dict() for t in terms]

    # ------------------------------------------------------------------
    # Consistency Check
    # ------------------------------------------------------------------

    def check_consistency(self, contents: list[str]) -> dict[str, Any]:
        """Check multiple content blocks for consistency issues."""
        issues: list[ConsistencyIssue] = []

        all_terms: dict[str, list[int]] = {}
        for idx, content in enumerate(contents):
            words = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", content)
            for w in words:
                all_terms.setdefault(w, []).append(idx)

        seen_terms: dict[str, list[str]] = {}
        for idx, content in enumerate(contents):
            definitions = re.findall(
                r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s*(?:is|are|refers to)\s+(.+?)(?:\.|,)",
                content,
            )
            for term, defn in definitions:
                norm_def = defn.strip().lower()[:80]
                if term in seen_terms and norm_def not in seen_terms[term]:
                    issues.append(ConsistencyIssue(
                        location=f"content_block_{idx}",
                        issue_type="definition_mismatch",
                        description=f"'{term}' has inconsistent definitions across content blocks.",
                        suggestion=f"Review and unify the definition of '{term}'.",
                        severity="warning",
                    ))
                seen_terms.setdefault(term, []).append(norm_def)

        for term_text, locations in all_terms.items():
            if len(set(locations)) > 1:
                short = term_text[:50]
                for loc in locations[1:]:
                    issues.append(ConsistencyIssue(
                        location=f"content_block_{loc}",
                        issue_type="terminology_variation",
                        description=f"Term '{short}' appears in multiple blocks — ensure consistent usage.",
                        suggestion=f"Standardize '{short}' across all content.",
                        severity="info",
                    ))

        result = ContentConsistencyResult(issues=issues)
        result.calculate_score()
        return result.to_dict()

    # ------------------------------------------------------------------
    # Curriculum Mapping
    # ------------------------------------------------------------------

    def suggest_mapping(
        self, source_id: str, source_type: str, target_id: str, target_type: str
    ) -> dict[str, Any]:
        """Suggest a curriculum mapping between two entities."""
        confidence = 0.65
        if source_type == target_type:
            confidence = 0.85
        relationship = f"{source_type}_to_{target_type}"
        suggestion = CurriculumMappingSuggestion(
            source_id=source_id,
            source_type=source_type,
            target_id=target_id,
            target_type=target_type,
            relationship=relationship,
            confidence=confidence,
        )
        return suggestion.to_dict()

    # ------------------------------------------------------------------
    # Metadata Suggestions
    # ------------------------------------------------------------------

    def suggest_metadata(self, content_id: str, text: str) -> dict[str, Any]:
        """Generate metadata suggestions based on content analysis."""
        word_count = len(text.split())
        suggestions: dict[str, float] = {}

        if word_count > 500:
            suggestions["detailed"] = 0.8
        elif word_count > 100:
            suggestions["moderate"] = 0.7
        else:
            suggestions["brief"] = 0.75

        lower_text = text.lower()
        if any(w in lower_text for w in ("security", "authentication", "encryption")):
            suggestions["security"] = 0.9
        if any(w in lower_text for w in ("performance", "latency", "optimization")):
            suggestions["performance"] = 0.85
        if any(w in lower_text for w in ("beginner", "introduction", "getting started")):
            suggestions["difficulty_beginner"] = 0.8
        elif any(w in lower_text for w in ("advanced", "expert", "deep dive")):
            suggestions["difficulty_advanced"] = 0.8

        meta = MetadataSuggestion(
            content_id=content_id,
            metadata_type="auto_generated",
            suggestions=suggestions,
        )
        return meta.to_dict()

    # ------------------------------------------------------------------
    # Audit Trail
    # ------------------------------------------------------------------

    def record_generation(
        self, content_id: str, ai_type: str, input_text: str, output_text: str, model_version: str = "rule-based-1.0"
    ) -> dict[str, Any]:
        """Create an audit trail entry for an AI generation."""
        audit = AIGenerationAudit(
            content_id=content_id,
            ai_type=ai_type,
            input_hash=hashlib.sha256(input_text.encode()).hexdigest(),
            output_hash=hashlib.sha256(output_text.encode()).hexdigest(),
            model_version=model_version,
        )
        result = self._repo.create_audit(audit.to_dict())
        logger.info("ai_generation_audited", extra={"audit_id": result["id"], "content_id": content_id})
        return result

    def get_audit(self, audit_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_audit_by_id(audit_id)

    def get_audits_for_content(self, content_id: str) -> list[dict[str, Any]]:
        return self._repo.get_audits_for_content(content_id)

    def review_audit(self, audit_id: str, approved: bool) -> Optional[dict[str, Any]]:
        """Mark an audit record as instructor-reviewed."""
        audit = self._repo.get_audit_by_id(audit_id)
        if not audit:
            return None
        updates = {
            "instructor_reviewed": approved,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._repo.update_audit(audit_id, updates)

    # ------------------------------------------------------------------
    # Private suggestion generators
    # ------------------------------------------------------------------

    def _generate_reading_level_suggestion(self, source: str) -> str:
        analysis = self.analyze_reading_level(source)
        if analysis.flesch_kincaid > 12:
            return (
                f"The text reads at grade level {analysis.flesch_kincaid:.1f}, "
                "which may be too complex for a general audience. Consider simplifying "
                "sentences and using shorter words."
            )
        return (
            f"The text reads at grade level {analysis.flesch_kincaid:.1f}, "
            "which is accessible for most audiences."
        )

    def _generate_glossary_suggestion(self, source: str) -> str:
        terms = self.extract_glossary(source)
        if terms:
            names = [t["term"] for t in terms[:5]]
            return f"Consider adding glossary entries for: {', '.join(names)}."
        return "No prominent technical terms detected — review manually for potential glossary entries."

    def _generate_objectives_suggestion(self, source: str) -> str:
        sentences = [s.strip() for s in re.split(r"[.!?]+", source) if s.strip() and len(s.strip()) > 15]
        if sentences:
            first = sentences[0][:80]
            return f"Consider adding learning objectives. A good starting point might relate to: \"{first}...\"."
        return "Add clear learning objectives at the beginning of the content."

    def _generate_tags_suggestion(self, source: str) -> str:
        lower = source.lower()
        tags: list[str] = []
        tag_keywords = {
            "security": ["security", "authentication", "encryption", "firewall"],
            "performance": ["performance", "latency", "optimization", "caching"],
            "networking": ["network", "tcp", "http", "dns", "routing"],
            "database": ["database", "sql", "query", "index"],
            "cloud": ["cloud", "aws", "azure", "gcp", "deploy"],
        }
        for tag, keywords in tag_keywords.items():
            if any(kw in lower for kw in keywords):
                tags.append(tag)
        if tags:
            return f"Suggested tags: {', '.join(tags)}."
        return "Consider adding descriptive tags based on the content topics."

    def _generate_quiz_suggestion(self, source: str) -> str:
        sentences = [s.strip() for s in re.split(r"[.!?]+", source) if s.strip() and len(s.strip()) > 20]
        if sentences:
            key_fact = sentences[0][:100]
            return f"Create a quiz question about: \"{key_fact}...\". Example: 'What is the primary purpose of {key_fact.split()[0] if key_fact.split() else 'this concept'}?'"
        return "Generate quiz questions from the key concepts in this content."

    def _generate_outline_suggestion(self, source: str) -> str:
        headings = re.findall(r"^#+\s+(.+)$", source, re.MULTILINE)
        if headings:
            return f"Current outline has {len(headings)} sections. Consider adding an introduction, summary, and practice section."
        return "Structure the content with clear headings and subheadings for better navigation."
