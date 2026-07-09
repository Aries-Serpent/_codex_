"""Data Pipeline for ML-based Pattern Recognition.

This module extracts, transforms, and prepares data from various sources
for training ML models that recognize patterns and suggest resolutions.

Data Sources:
- Pattern learning store (patterns, outcomes)
- Session logs (symptoms, resolutions)
- CI/CD logs (failure patterns)
- Git history (fix patterns)

Author: GitHub Copilot Coding Agent
Date: 2026-02-05
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class DataSourceType(Enum):
    """Types of data sources for the ML pipeline."""

    PATTERN_STORE = "pattern_store"
    SESSION_LOGS = "session_logs"
    ACTION_LOG = "action_log"
    GIT_HISTORY = "git_history"
    COGNITIVE_STATE = "cognitive_state"


@dataclass
class RawDataRecord:
    """A raw data record extracted from a data source."""

    source_type: DataSourceType
    timestamp: datetime
    content: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_type": self.source_type.value,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RawDataRecord:
        """Create from dictionary representation."""
        return cls(
            source_type=DataSourceType(data["source_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class PatternSample:
    """A single training sample for pattern recognition."""

    pattern_id: str
    category: str
    symptoms: list[str]
    resolution: str
    success: bool
    context: dict[str, Any] = field(default_factory=dict)
    features: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pattern_id": self.pattern_id,
            "category": self.category,
            "symptoms": self.symptoms,
            "resolution": self.resolution,
            "success": self.success,
            "context": self.context,
            "features": self.features,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatternSample:
        """Create from dictionary representation."""
        return cls(
            pattern_id=data["pattern_id"],
            category=data["category"],
            symptoms=data["symptoms"],
            resolution=data["resolution"],
            success=data["success"],
            context=data.get("context", {}),
            features=data.get("features", {}),
        )


class FeatureExtractor:
    """Extract features from raw data for ML models."""

    # Symptom keywords for feature extraction
    CATEGORY_KEYWORDS: dict[str, list[str]] = {
        "testing": ["test", "pytest", "unittest", "coverage", "assert", "mock"],
        "ci_cd": ["workflow", "action", "ci", "cd", "pipeline", "build", "deploy"],
        "security": ["codeql", "vulnerability", "security", "sarif", "alert", "cve"],
        "documentation": ["doc", "readme", "markdown", "link", "reference"],
        "version_control": ["git", "commit", "merge", "branch", "conflict"],
        "workflow": ["session", "context", "handoff", "continuation"],
        "collaboration": ["agent", "handoff", "orchestration", "chain"],
    }

    # Error pattern keywords
    ERROR_KEYWORDS = [
        "error",
        "exception",
        "failed",
        "failure",
        "traceback",
        "importerror",
        "modulenotfounderror",
        "attributeerror",
        "typeerror",
        "valueerror",
        "keyerror",
        "indexerror",
    ]

    def __init__(self) -> None:
        """Initialize the feature extractor."""
        self._category_patterns = {
            category: re.compile("|".join(keywords), re.IGNORECASE)
            for category, keywords in self.CATEGORY_KEYWORDS.items()
        }
        self._error_pattern = re.compile("|".join(self.ERROR_KEYWORDS), re.IGNORECASE)

    def extract_text_features(self, text: str) -> dict[str, float]:
        """Extract features from text content.

        Args:
            text: The text to extract features from.

        Returns:
            Dictionary of feature names to values.
        """
        features: dict[str, float] = {}
        text_lower = text.lower()

        # Category keyword frequency
        for category, pattern in self._category_patterns.items():
            matches = pattern.findall(text_lower)
            features[f"category_{category}_count"] = float(len(matches))
            features[f"category_{category}_present"] = 1.0 if matches else 0.0

        # Error keyword frequency
        error_matches = self._error_pattern.findall(text_lower)
        features["error_keyword_count"] = float(len(error_matches))
        features["has_error_keywords"] = 1.0 if error_matches else 0.0

        # Text statistics
        features["text_length"] = float(len(text))
        features["word_count"] = float(len(text.split()))
        features["line_count"] = float(text.count("\n") + 1)

        # Code indicators (text pattern matching for error detection, not URL validation)
        features["has_python_traceback"] = (
            1.0 if "Traceback (most recent call last)" in text else 0.0
        )  # nosec
        features["has_file_path"] = 1.0 if re.search(r"[\w/]+\.py", text) else 0.0
        features["has_line_number"] = 1.0 if re.search(r"line \d+", text, re.IGNORECASE) else 0.0

        return features

    def extract_pattern_features(self, pattern: dict[str, Any]) -> dict[str, float]:
        """Extract features from a pattern entry.

        Args:
            pattern: Pattern dictionary from pattern store.

        Returns:
            Dictionary of feature names to values.
        """
        features: dict[str, float] = {}

        # Basic pattern stats
        features["symptom_count"] = float(len(pattern.get("symptoms", [])))
        features["solution_count"] = float(len(pattern.get("solutions", [])))
        features["diagnosis_step_count"] = float(len(pattern.get("diagnosis_steps", [])))

        # Success metrics
        features["success_rate"] = float(pattern.get("success_rate", 0.5))
        features["times_applied"] = float(pattern.get("times_applied", 0))

        # Extract text features from symptoms
        symptoms_text = " ".join(pattern.get("symptoms", []))
        text_features = self.extract_text_features(symptoms_text)
        features.update({f"symptom_{k}": v for k, v in text_features.items()})

        # Extract text features from solutions
        solutions_text = " ".join(pattern.get("solutions", []))
        solution_features = self.extract_text_features(solutions_text)
        features.update({f"solution_{k}": v for k, v in solution_features.items()})

        return features

    def categorize_symptoms(self, symptoms: list[str]) -> str:
        """Determine the most likely category for a set of symptoms.

        Args:
            symptoms: List of symptom strings.

        Returns:
            Best matching category name.
        """
        symptoms_text = " ".join(symptoms)
        category_scores: dict[str, int] = {}

        for category, pattern in self._category_patterns.items():
            matches = pattern.findall(symptoms_text.lower())
            category_scores[category] = len(matches)

        if not category_scores or max(category_scores.values()) == 0:
            return "unknown"

        return max(category_scores, key=lambda k: category_scores[k])


class DataPipeline:
    """Main data pipeline for ML training data preparation.

    This pipeline extracts data from multiple sources, transforms it,
    and generates training samples for pattern recognition models.
    """

    def __init__(
        self,
        pattern_store_path: str | Path | None = None,
        action_log_path: str | Path | None = None,
        session_db_path: str | Path | None = None,
    ) -> None:
        """Initialize the data pipeline.

        Args:
            pattern_store_path: Path to pattern learning store JSON.
            action_log_path: Path to action log NDJSON.
            session_db_path: Path to session logs SQLite database.
        """
        self._pattern_store_path = Path(pattern_store_path) if pattern_store_path else None
        self._action_log_path = Path(action_log_path) if action_log_path else None
        self._session_db_path = Path(session_db_path) if session_db_path else None

        self._feature_extractor = FeatureExtractor()
        self._raw_data: list[RawDataRecord] = []
        self._samples: list[PatternSample] = []

    def load_pattern_store(self, path: str | Path | None = None) -> list[RawDataRecord]:
        """Load data from pattern learning store.

        Args:
            path: Optional path override for pattern store.

        Returns:
            List of raw data records extracted.
        """
        store_path = Path(path) if path else self._pattern_store_path
        if not store_path or not store_path.exists():
            return []

        records: list[RawDataRecord] = []

        with open(store_path) as f:
            data = json.load(f)

        # Extract patterns
        patterns = data.get("patterns", {})
        for pattern_name, pattern_data in patterns.items():
            records.append(
                RawDataRecord(
                    source_type=DataSourceType.PATTERN_STORE,
                    timestamp=datetime.fromisoformat(
                        pattern_data.get("last_used", datetime.now(timezone.utc).isoformat())
                    ),
                    content={"name": pattern_name, **pattern_data},
                    metadata={"source_file": str(store_path)},
                )
            )

        # Extract learning log entries
        learning_log = data.get("learning_log", [])
        for entry in learning_log:
            records.append(
                RawDataRecord(
                    source_type=DataSourceType.PATTERN_STORE,
                    timestamp=datetime.fromisoformat(
                        entry.get("timestamp", datetime.now(timezone.utc).isoformat())
                    ),
                    content=entry,
                    metadata={"type": "learning_log", "source_file": str(store_path)},
                )
            )

        self._raw_data.extend(records)
        return records

    def load_action_log(self, path: str | Path | None = None) -> list[RawDataRecord]:
        """Load data from action log.

        Args:
            path: Optional path override for action log.

        Returns:
            List of raw data records extracted.
        """
        log_path = Path(path) if path else self._action_log_path
        if not log_path or not log_path.exists():
            return []

        records: list[RawDataRecord] = []

        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    records.append(
                        RawDataRecord(
                            source_type=DataSourceType.ACTION_LOG,
                            timestamp=datetime.fromisoformat(
                                entry.get("timestamp", datetime.now(timezone.utc).isoformat())
                            ),
                            content=entry,
                            metadata={"source_file": str(log_path)},
                        )
                    )
                except json.JSONDecodeError:
                    continue

        self._raw_data.extend(records)
        return records

    def extract_all_data(self) -> list[RawDataRecord]:
        """Extract data from all configured sources.

        Returns:
            List of all extracted raw data records.
        """
        self._raw_data = []

        if self._pattern_store_path:
            self.load_pattern_store()

        if self._action_log_path:
            self.load_action_log()

        return self._raw_data

    def generate_training_samples(self) -> list[PatternSample]:
        """Generate training samples from raw data.

        Returns:
            List of training samples ready for ML models.
        """
        self._samples = []

        # Group pattern store records
        pattern_records = [
            r
            for r in self._raw_data
            if r.source_type == DataSourceType.PATTERN_STORE
            and r.metadata.get("type") != "learning_log"
        ]

        for record in pattern_records:
            content = record.content
            pattern_id = content.get("id", content.get("name", "unknown"))

            symptoms = content.get("symptoms", [])
            solutions = content.get("solutions", [])
            category = content.get(
                "category", self._feature_extractor.categorize_symptoms(symptoms)
            )

            # Create sample for each solution
            for solution in solutions:
                sample = PatternSample(
                    pattern_id=pattern_id,
                    category=category,
                    symptoms=symptoms,
                    resolution=solution,
                    success=content.get("success_rate", 0.5) >= 0.5,
                    context={
                        "diagnosis_steps": content.get("diagnosis_steps", []),
                        "times_applied": content.get("times_applied", 0),
                        "related_prs": content.get("related_prs", []),
                    },
                    features=self._feature_extractor.extract_pattern_features(content),
                )
                self._samples.append(sample)

        return self._samples

    def split_dataset(
        self,
        train_ratio: float = 0.8,
        validation_ratio: float = 0.1,
    ) -> tuple[list[PatternSample], list[PatternSample], list[PatternSample]]:
        """Split samples into train/validation/test sets.

        Args:
            train_ratio: Fraction for training set.
            validation_ratio: Fraction for validation set.

        Returns:
            Tuple of (train_samples, validation_samples, test_samples).
        """
        import random

        samples = self._samples.copy()
        random.shuffle(samples)

        n_samples = len(samples)
        n_train = int(n_samples * train_ratio)
        n_val = int(n_samples * validation_ratio)

        train_samples = samples[:n_train]
        val_samples = samples[n_train : n_train + n_val]
        test_samples = samples[n_train + n_val :]

        return train_samples, val_samples, test_samples

    def export_samples(
        self, output_path: str | Path, samples: list[PatternSample] | None = None
    ) -> None:
        """Export samples to a JSON file.

        Args:
            output_path: Path to write samples to.
            samples: Samples to export (default: all samples).
        """
        export_samples = samples if samples is not None else self._samples
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w") as f:
            json.dump(
                [s.to_dict() for s in export_samples],
                f,
                indent=2,
                default=str,
            )

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the extracted data.

        Returns:
            Dictionary of statistics.
        """
        category_counts: dict[str, int] = {}
        for sample in self._samples:
            category_counts[sample.category] = category_counts.get(sample.category, 0) + 1

        return {
            "total_raw_records": len(self._raw_data),
            "total_samples": len(self._samples),
            "samples_by_category": category_counts,
            "data_sources": list({r.source_type.value for r in self._raw_data}),
            "unique_patterns": len({s.pattern_id for s in self._samples}),
            "success_samples": sum(1 for s in self._samples if s.success),
            "failure_samples": sum(1 for s in self._samples if not s.success),
        }


class TrainingDataGenerator:
    """Generate training data for different ML models."""

    def __init__(self, samples: list[PatternSample]) -> None:
        """Initialize the generator with samples.

        Args:
            samples: List of pattern samples to use.
        """
        self._samples = samples

    def generate_classification_data(self) -> tuple[list[str], list[str]]:
        """Generate data for symptom classification.

        Returns:
            Tuple of (texts, labels) for classification.
        """
        texts: list[str] = []
        labels: list[str] = []

        for sample in self._samples:
            # Combine symptoms into a single text
            text = " ".join(sample.symptoms)
            texts.append(text)
            labels.append(sample.category)

        return texts, labels

    def generate_recommendation_data(self) -> tuple[list[str], list[str]]:
        """Generate data for resolution recommendation.

        Returns:
            Tuple of (symptoms, resolutions) for recommendation.
        """
        symptoms: list[str] = []
        resolutions: list[str] = []

        for sample in self._samples:
            symptom_text = " ".join(sample.symptoms)
            symptoms.append(symptom_text)
            resolutions.append(sample.resolution)

        return symptoms, resolutions

    def generate_success_prediction_data(
        self,
    ) -> tuple[list[dict[str, float]], list[bool]]:
        """Generate data for success prediction.

        Returns:
            Tuple of (features, labels) for prediction.
        """
        features: list[dict[str, float]] = []
        labels: list[bool] = []

        for sample in self._samples:
            features.append(sample.features)
            labels.append(sample.success)

        return features, labels

    def to_feature_matrix(
        self,
        feature_names: list[str] | None = None,
    ) -> tuple[list[list[float]], list[str]]:
        """Convert samples to a feature matrix.

        Args:
            feature_names: Optional list of feature names to include.

        Returns:
            Tuple of (feature_matrix, feature_names).
        """
        if not self._samples:
            return [], []

        # Collect all feature names if not provided
        if feature_names is None:
            all_features: set[str] = set()
            for sample in self._samples:
                all_features.update(sample.features.keys())
            feature_names = sorted(all_features)

        # Build matrix
        matrix: list[list[float]] = []
        for sample in self._samples:
            row = [sample.features.get(f, 0.0) for f in feature_names]
            matrix.append(row)

        return matrix, feature_names


class PatternDataset:
    """A dataset of pattern samples for ML training."""

    def __init__(self, samples: list[PatternSample]) -> None:
        """Initialize the dataset.

        Args:
            samples: List of pattern samples.
        """
        self._samples = samples

    def __len__(self) -> int:
        """Return number of samples."""
        return len(self._samples)

    def __getitem__(self, idx: int) -> PatternSample:
        """Get sample by index."""
        return self._samples[idx]

    def __iter__(self) -> None:
        """Iterate over samples."""
        return iter(self._samples)

    @property
    def samples(self) -> list[PatternSample]:
        """Get all samples."""
        return self._samples

    def filter_by_category(self, category: str) -> PatternDataset:
        """Filter samples by category.

        Args:
            category: Category to filter by.

        Returns:
            New dataset with filtered samples.
        """
        filtered = [s for s in self._samples if s.category == category]
        return PatternDataset(filtered)

    def filter_by_success(self, success: bool = True) -> PatternDataset:
        """Filter samples by success status.

        Args:
            success: Success status to filter by.

        Returns:
            New dataset with filtered samples.
        """
        filtered = [s for s in self._samples if s.success == success]
        return PatternDataset(filtered)

    def get_categories(self) -> list[str]:
        """Get list of unique categories."""
        return list({s.category for s in self._samples})

    def get_category_distribution(self) -> dict[str, int]:
        """Get distribution of categories."""
        distribution: dict[str, int] = {}
        for sample in self._samples:
            distribution[sample.category] = distribution.get(sample.category, 0) + 1
        return distribution

    def save(self, path: str | Path) -> None:
        """Save dataset to JSON file.

        Args:
            path: Path to save to.
        """
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w") as f:
            json.dump(
                [s.to_dict() for s in self._samples],
                f,
                indent=2,
                default=str,
            )

    @classmethod
    def load(cls, path: str | Path) -> PatternDataset:
        """Load dataset from JSON file.

        Args:
            path: Path to load from.

        Returns:
            Loaded dataset.
        """
        with open(path) as f:
            data = json.load(f)

        samples = [PatternSample.from_dict(d) for d in data]
        return cls(samples)


def create_pipeline_from_defaults() -> DataPipeline:
    """Create a data pipeline with default paths.

    Returns:
        Configured DataPipeline instance.
    """
    # Default paths relative to repository root
    repo_root = Path(__file__).parent.parent.parent.parent.parent

    pattern_store = repo_root / ".codex" / "cognitive_brain" / "pattern_learning_store.json"
    action_log = repo_root / ".codex" / "action_log.ndjson"

    return DataPipeline(
        pattern_store_path=pattern_store if pattern_store.exists() else None,
        action_log_path=action_log if action_log.exists() else None,
    )
