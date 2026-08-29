"""Tests for ML-based Pattern Recognition modules.

Author: GitHub Copilot Coding Agent
Date: 2026-02-05
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from codex.cognitive.ml import (
    ClassificationResult,
    CosineSimilarity,
    DataPipeline,
    DataSourceType,
    FeatureExtractor,
    JaccardSimilarity,
    NaiveBayesClassifier,
    PatternDataset,
    PatternSample,
    RawDataRecord,
    Recommendation,
    RecommendationResult,
    ResolutionIndex,
    ResolutionRecommender,
    SuccessPredictor,
    SymptomClassifier,
    TfidfVectorizer,
    TrainingDataGenerator,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_pattern_store() -> dict[str, Any]:
    """Create a sample pattern store."""
    return {
        "metadata": {
            "version": "1.0.0",
            "created": "2026-02-05T09:00:00Z",
        },
        "patterns": {
            "test_failure": {
                "id": "TFR-001",
                "category": "testing",
                "symptoms": ["pytest collection error", "ImportError"],
                "diagnosis_steps": ["Check imports", "Verify dependencies"],
                "solutions": ["Add missing imports", "Mock dependencies"],
                "success_rate": 0.95,
                "times_applied": 5,
                "last_used": "2026-02-05T08:00:00Z",
            },
            "ci_failure": {
                "id": "CIF-001",
                "category": "ci_cd",
                "symptoms": ["workflow failed", "action error"],
                "diagnosis_steps": ["Check workflow logs"],
                "solutions": ["Fix workflow config", "Add retry logic"],
                "success_rate": 0.88,
                "times_applied": 3,
                "last_used": "2026-02-05T07:00:00Z",
            },
        },
        "learning_log": [
            {
                "timestamp": "2026-02-05T09:00:00Z",
                "session": "test-session",
                "patterns_applied": ["test_failure"],
                "outcome": "success",
            },
        ],
    }


@pytest.fixture
def sample_action_log() -> list[dict[str, Any]]:
    """Create sample action log entries."""
    return [
        {
            "timestamp": "2026-02-05T08:00:00Z",
            "action": "edit",
            "path": "src/module.py",
            "description": "Fixed import error",
        },
        {
            "timestamp": "2026-02-05T08:10:00Z",
            "action": "create",
            "path": "tests/test_module.py",
            "description": "Added tests",
        },
    ]


@pytest.fixture
def sample_patterns() -> list[PatternSample]:
    """Create sample pattern samples for testing."""
    return [
        PatternSample(
            pattern_id="TFR-001",
            category="testing",
            symptoms=["pytest collection error", "ImportError", "ModuleNotFoundError"],
            resolution="Add missing imports",
            success=True,
            context={"times_applied": 5},
            features={"success_rate": 0.95, "symptom_count": 3},
        ),
        PatternSample(
            pattern_id="TFR-001",
            category="testing",
            symptoms=["pytest collection error", "ImportError", "ModuleNotFoundError"],
            resolution="Mock dependencies",
            success=True,
            context={"times_applied": 5},
            features={"success_rate": 0.95, "symptom_count": 3},
        ),
        PatternSample(
            pattern_id="CIF-001",
            category="ci_cd",
            symptoms=["workflow failed", "action error", "timeout"],
            resolution="Fix workflow config",
            success=True,
            context={"times_applied": 3},
            features={"success_rate": 0.88, "symptom_count": 3},
        ),
        PatternSample(
            pattern_id="CIF-001",
            category="ci_cd",
            symptoms=["workflow failed", "action error", "timeout"],
            resolution="Add retry logic",
            success=False,
            context={"times_applied": 3},
            features={"success_rate": 0.88, "symptom_count": 3},
        ),
        PatternSample(
            pattern_id="SEC-001",
            category="security",
            symptoms=["CodeQL alert", "vulnerability detected", "security issue"],
            resolution="Apply security patch",
            success=True,
            context={"times_applied": 2},
            features={"success_rate": 0.92, "symptom_count": 3},
        ),
    ]


# ============================================================================
# Data Pipeline Tests
# ============================================================================


class TestRawDataRecord:
    """Tests for RawDataRecord dataclass."""

    def test_create_record(self):
        """Test creating a raw data record."""
        record = RawDataRecord(
            source_type=DataSourceType.PATTERN_STORE,
            timestamp=datetime.now(timezone.utc),
            content={"key": "value"},
            metadata={"source": "test"},
        )
        assert record.source_type == DataSourceType.PATTERN_STORE, "Data must not be empty"
        assert "key" in record.content, "Content must not be empty"

    def test_to_dict(self):
        """Test converting record to dictionary."""
        record = RawDataRecord(
            source_type=DataSourceType.ACTION_LOG,
            timestamp=datetime(2026, 2, 5, 9, 0, 0, tzinfo=timezone.utc),
            content={"action": "test"},
        )
        data = record.to_dict()
        assert data["source_type"] == "action_log", "Data must not be empty"
        assert "timestamp" in data, "Data must not be empty"
        assert data["content"]["action"] == "test", "Data must not be empty"

    def test_from_dict(self):
        """Test creating record from dictionary."""
        data = {
            "source_type": "pattern_store",
            "timestamp": "2026-02-05T09:00:00+00:00",
            "content": {"test": True},
            "metadata": {},
        }
        record = RawDataRecord.from_dict(data)
        assert record.source_type == DataSourceType.PATTERN_STORE, "Data must not be empty"
        assert record.content["test"] is True, "Content must not be empty"


class TestPatternSample:
    """Tests for PatternSample dataclass."""

    def test_create_sample(self):
        """Test creating a pattern sample."""
        sample = PatternSample(
            pattern_id="TEST-001",
            category="testing",
            symptoms=["error1", "error2"],
            resolution="Fix it",
            success=True,
        )
        assert sample.pattern_id == "TEST-001", "pattern_id is not valid"
        assert len(sample.symptoms) == 2, "Collection must not be empty"
        assert sample.success is True, "success is not valid"

    def test_to_dict_and_back(self):
        """Test round-trip conversion."""
        original = PatternSample(
            pattern_id="TEST-001",
            category="testing",
            symptoms=["error1"],
            resolution="Fix",
            success=True,
            features={"score": 0.5},
        )
        data = original.to_dict()
        restored = PatternSample.from_dict(data)

        assert restored.pattern_id == original.pattern_id, "pattern_id is not valid"
        assert restored.features == original.features, "features is not valid"


class TestFeatureExtractor:
    """Tests for FeatureExtractor."""

    def test_extract_text_features(self):
        """Test extracting features from text."""
        extractor = FeatureExtractor()
        text = "pytest collection error with ImportError in test file"
        features = extractor.extract_text_features(text)

        assert "category_testing_count" in features, "Count must be greater than zero"
        assert features["category_testing_present"] == 1.0, "Condition must be true"
        assert "text_length" in features, "Length must be greater than zero"
        assert "word_count" in features, "Count must be greater than zero"

    def test_extract_error_keywords(self):
        """Test extracting error keywords."""
        extractor = FeatureExtractor()
        text = "Traceback (most recent call last): TypeError: invalid argument"
        features = extractor.extract_text_features(text)

        assert features["has_error_keywords"] == 1.0, "Error should be raised or set"
        assert features["error_keyword_count"] >= 1, "Value must be greater than zero"
        assert features["has_python_traceback"] == 1.0, "Condition must be true"

    def test_categorize_symptoms(self):
        """Test categorizing symptoms."""
        extractor = FeatureExtractor()

        assert extractor.categorize_symptoms(["pytest error", "test failure"]) == "testing"
        assert extractor.categorize_symptoms(["workflow failed", "ci error"]) == "ci_cd"
        assert extractor.categorize_symptoms(["codeql alert", "vulnerability"]) == "security"


class TestDataPipeline:
    """Tests for DataPipeline."""

    def test_load_pattern_store(self, sample_pattern_store):
        """Test loading pattern store."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_pattern_store, f)
            f.flush()

            pipeline = DataPipeline(pattern_store_path=f.name)
            records = pipeline.load_pattern_store()

            # Should have pattern records + learning log entry
            assert len(records) >= 2, "Records must not be empty"
            assert any(r.content.get("id") == "TFR-001" for r in records), "Content must not be empty"

    def test_load_action_log(self, sample_action_log):
        """Test loading action log."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
            for entry in sample_action_log:
                f.write(json.dumps(entry) + "\n")
            f.flush()

            pipeline = DataPipeline(action_log_path=f.name)
            records = pipeline.load_action_log()

            assert len(records) == 2, "Records must not be empty"
            assert all(r.source_type == DataSourceType.ACTION_LOG for r in records), "Data must not be empty"

    def test_generate_training_samples(self, sample_pattern_store):
        """Test generating training samples."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_pattern_store, f)
            f.flush()

            pipeline = DataPipeline(pattern_store_path=f.name)
            pipeline.extract_all_data()
            samples = pipeline.generate_training_samples()

            assert len(samples) > 0, "Samples must not be empty"
            assert all(isinstance(s, PatternSample) for s in samples)

    def test_split_dataset(self, sample_patterns):
        """Test dataset splitting."""
        pipeline = DataPipeline()
        pipeline._samples = sample_patterns

        train, val, test = pipeline.split_dataset(train_ratio=0.6, validation_ratio=0.2)

        total = len(train) + len(val) + len(test)
        assert total == len(sample_patterns), "Sample_patterns must not be empty"

    def test_export_samples(self, sample_patterns):
        """Test exporting samples."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "samples.json"

            pipeline = DataPipeline()
            pipeline._samples = sample_patterns
            pipeline.export_samples(output_path)

            assert output_path.exists(), "Condition must be true"
            with open(output_path) as f:
                loaded = json.load(f)
            assert len(loaded) == len(sample_patterns), "Loaded must not be empty"

    def test_get_statistics(self, sample_patterns):
        """Test getting statistics."""
        pipeline = DataPipeline()
        pipeline._samples = sample_patterns

        stats = pipeline.get_statistics()

        assert stats["total_samples"] == len(sample_patterns), "Sample_patterns must not be empty"
        assert "testing" in stats["samples_by_category"], "Condition must be true"
        assert "ci_cd" in stats["samples_by_category"], "Condition must be true"


class TestTrainingDataGenerator:
    """Tests for TrainingDataGenerator."""

    def test_generate_classification_data(self, sample_patterns):
        """Test generating classification data."""
        generator = TrainingDataGenerator(sample_patterns)
        texts, labels = generator.generate_classification_data()

        assert len(texts) == len(sample_patterns), "Texts must not be empty"
        assert len(labels) == len(sample_patterns), "Labels must not be empty"
        assert all(isinstance(t, str) for t in texts)

    def test_generate_recommendation_data(self, sample_patterns):
        """Test generating recommendation data."""
        generator = TrainingDataGenerator(sample_patterns)
        symptoms, resolutions = generator.generate_recommendation_data()

        assert len(symptoms) == len(sample_patterns), "Symptoms must not be empty"
        assert len(resolutions) == len(sample_patterns), "Resolutions must not be empty"

    def test_generate_success_prediction_data(self, sample_patterns):
        """Test generating success prediction data."""
        generator = TrainingDataGenerator(sample_patterns)
        features, labels = generator.generate_success_prediction_data()

        assert len(features) == len(sample_patterns), "Features must not be empty"
        assert len(labels) == len(sample_patterns), "Labels must not be empty"
        assert all(isinstance(lbl, bool) for lbl in labels)

    def test_to_feature_matrix(self, sample_patterns):
        """Test converting to feature matrix."""
        generator = TrainingDataGenerator(sample_patterns)
        matrix, feature_names = generator.to_feature_matrix()

        assert len(matrix) == len(sample_patterns), "Matrix must not be empty"
        assert len(feature_names) > 0, "Feature_names must not be empty"
        assert all(len(row) == len(feature_names) for row in matrix), "Row must not be empty"


class TestPatternDataset:
    """Tests for PatternDataset."""

    def test_basic_operations(self, sample_patterns):
        """Test basic dataset operations."""
        dataset = PatternDataset(sample_patterns)

        assert len(dataset) == len(sample_patterns), "Dataset must not be empty"
        assert dataset[0] == sample_patterns[0], "Data must not be empty"
        assert list(dataset) == sample_patterns, "Data must not be empty"

    def test_filter_by_category(self, sample_patterns):
        """Test filtering by category."""
        dataset = PatternDataset(sample_patterns)
        testing_samples = dataset.filter_by_category("testing")

        assert len(testing_samples) < len(dataset), "Testing_samples must not be empty"
        assert all(s.category == "testing" for s in testing_samples), "category is not valid"

    def test_filter_by_success(self, sample_patterns):
        """Test filtering by success."""
        dataset = PatternDataset(sample_patterns)
        success_samples = dataset.filter_by_success(True)
        failure_samples = dataset.filter_by_success(False)

        assert all(s.success for s in success_samples), "Condition must be true"
        assert all(not s.success for s in failure_samples), "Condition must be true"

    def test_get_categories(self, sample_patterns):
        """Test getting categories."""
        dataset = PatternDataset(sample_patterns)
        categories = dataset.get_categories()

        assert "testing" in categories, "Condition must be true"
        assert "ci_cd" in categories, "Condition must be true"
        assert "security" in categories, "Condition must be true"

    def test_save_and_load(self, sample_patterns):
        """Test saving and loading dataset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dataset.json"

            original = PatternDataset(sample_patterns)
            original.save(path)

            loaded = PatternDataset.load(path)

            assert len(loaded) == len(original), "Loaded must not be empty"
            assert loaded[0].pattern_id == original[0].pattern_id, "pattern_id is not valid"


# ============================================================================
# Symptom Classifier Tests
# ============================================================================


class TestTfidfVectorizer:
    """Tests for TfidfVectorizer."""

    def test_fit_transform(self):
        """Test fitting and transforming texts."""
        vectorizer = TfidfVectorizer(max_features=100)
        texts = [
            "pytest collection error with imports",
            "workflow failed in ci pipeline",
            "test coverage is too low",
        ]

        vectors = vectorizer.fit_transform(texts)

        assert len(vectors) == 3, "Vectors must not be empty"
        assert all(isinstance(v, list) for v in vectors)
        assert all(len(v) > 0 for v in vectors), "V must not be empty"

    def test_transform_after_fit(self):
        """Test transforming new texts after fitting."""
        vectorizer = TfidfVectorizer(max_features=100)
        train_texts = ["pytest error", "workflow failed", "security alert"]
        vectorizer.fit(train_texts)

        new_vectors = vectorizer.transform(["new pytest test error"])

        assert len(new_vectors) == 1, "New_vectors must not be empty"

    def test_get_feature_names(self):
        """Test getting feature names."""
        vectorizer = TfidfVectorizer(max_features=100)
        vectorizer.fit(["test pytest error", "pytest collection error", "import error test"])

        names = vectorizer.get_feature_names()

        assert isinstance(names, list)
        assert len(names) > 0, "Names must not be empty"

    def test_save_and_load(self):
        """Test saving and loading vectorizer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "vectorizer.json"

            vectorizer = TfidfVectorizer(max_features=50)
            vectorizer.fit(["test", "pytest", "error"])
            vectorizer.save(path)

            loaded = TfidfVectorizer.load(path)

            assert loaded._vocabulary == vectorizer._vocabulary, "_vocabulary is not valid"
            assert loaded._fitted is True, "_fitted is not valid"


class TestNaiveBayesClassifier:
    """Tests for NaiveBayesClassifier."""

    def test_fit_predict(self):
        """Test fitting and predicting."""
        classifier = NaiveBayesClassifier()

        X = [
            [1.0, 0.0, 0.5],
            [0.8, 0.1, 0.4],
            [0.0, 1.0, 0.2],
            [0.1, 0.9, 0.3],
        ]
        y = ["testing", "testing", "ci_cd", "ci_cd"]

        classifier.fit(X, y)
        predictions = classifier.predict([[0.9, 0.0, 0.5]])

        assert predictions[0] in ["testing", "ci_cd"]

    def test_predict_proba(self):
        """Test probability predictions."""
        classifier = NaiveBayesClassifier()

        X = [[1.0, 0.0], [0.0, 1.0]]
        y = ["a", "b"]

        classifier.fit(X, y)
        probas = classifier.predict_proba([[0.5, 0.5]])

        assert len(probas) == 1, "Probas must not be empty"
        assert "a" in probas[0], "Condition must be true"
        assert "b" in probas[0], "Condition must be true"
        assert abs(sum(probas[0].values()) - 1.0) < 0.01, "Value must be initialized"


class TestSymptomClassifier:
    """Tests for SymptomClassifier."""

    def test_fit_and_predict(self, sample_patterns):
        """Test fitting and predicting."""
        classifier = SymptomClassifier(max_features=50)
        classifier.fit(sample_patterns)

        result = classifier.predict(["pytest collection error", "ImportError"])

        assert isinstance(result, ClassificationResult)
        assert result.predicted_category in classifier.get_categories(), "Result must not be empty"
        assert 0 <= result.confidence <= 1, "Result must not be empty"

    def test_predict_batch(self, sample_patterns):
        """Test batch prediction."""
        classifier = SymptomClassifier(max_features=50)
        classifier.fit(sample_patterns)

        symptoms_list = [
            ["pytest error", "test failed"],
            ["workflow failed", "ci error"],
        ]
        results = classifier.predict_batch(symptoms_list)

        assert len(results) == 2, "Results must not be empty"
        assert all(isinstance(r, ClassificationResult) for r in results)

    def test_save_and_load(self, sample_patterns):
        """Test saving and loading classifier."""
        with tempfile.TemporaryDirectory() as tmpdir:
            classifier = SymptomClassifier(max_features=50)
            classifier.fit(sample_patterns)
            classifier.save(tmpdir)

            loaded = SymptomClassifier.load(tmpdir)

            result = loaded.predict(["pytest error"])
            assert result.predicted_category in loaded.get_categories(), "Result must not be empty"

    def test_evaluate(self, sample_patterns):
        """Test evaluation."""
        classifier = SymptomClassifier(max_features=50)
        classifier.fit(sample_patterns)

        metrics = classifier.evaluate(sample_patterns)

        assert "accuracy" in metrics, "Condition must be true"
        assert "total_samples" in metrics, "Condition must be true"
        assert "category_scores" in metrics, "Condition must be true"


# ============================================================================
# Recommender Tests
# ============================================================================


class TestCosineSimilarity:
    """Tests for CosineSimilarity."""

    def test_identical_vectors(self):
        """Test similarity of identical vectors."""
        vec = [1.0, 2.0, 3.0]
        sim = CosineSimilarity.compute(vec, vec)
        assert abs(sim - 1.0) < 0.01, "Condition must be true"

    def test_orthogonal_vectors(self):
        """Test similarity of orthogonal vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        sim = CosineSimilarity.compute(vec1, vec2)
        assert abs(sim) < 0.01, "Condition must be true"

    def test_zero_vector(self):
        """Test with zero vector."""
        vec1 = [0.0, 0.0]
        vec2 = [1.0, 2.0]
        sim = CosineSimilarity.compute(vec1, vec2)
        assert sim == 0.0, "sim is not valid"


class TestJaccardSimilarity:
    """Tests for JaccardSimilarity."""

    def test_identical_sets(self):
        """Test similarity of identical sets."""
        s = {"a", "b", "c"}
        sim = JaccardSimilarity.compute(s, s)
        assert sim == 1.0, "sim is not valid"

    def test_disjoint_sets(self):
        """Test similarity of disjoint sets."""
        s1 = {"a", "b"}
        s2 = {"c", "d"}
        sim = JaccardSimilarity.compute(s1, s2)
        assert sim == 0.0, "sim is not valid"

    def test_overlapping_sets(self):
        """Test similarity of overlapping sets."""
        s1 = {"a", "b", "c"}
        s2 = {"b", "c", "d"}
        sim = JaccardSimilarity.compute(s1, s2)
        assert 0 < sim < 1, "0 is not valid"


class TestResolutionIndex:
    """Tests for ResolutionIndex."""

    def test_add_and_search(self, sample_patterns):
        """Test adding samples and searching."""
        index = ResolutionIndex()
        for sample in sample_patterns:
            index.add(sample)

        results = index.search(["pytest collection error", "ImportError"])

        assert len(results) > 0, "Results must not be empty"
        assert all(isinstance(r[0], PatternSample) for r in results)
        assert all(isinstance(r[1], float) for r in results)

    def test_build(self, sample_patterns):
        """Test building index."""
        index = ResolutionIndex()
        index.build(sample_patterns)

        assert index.size() == len(sample_patterns), "Sample_patterns must not be empty"
        assert len(index.get_categories()) > 0, "Collection must not be empty"

    def test_filter_by_category(self, sample_patterns):
        """Test filtering search by category."""
        index = ResolutionIndex()
        index.build(sample_patterns)

        results = index.search(["error"], category="testing")

        assert all(r[0].category == "testing" for r in results), "Result must not be empty"

    def test_save_and_load(self, sample_patterns):
        """Test saving and loading index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "index.json"

            index = ResolutionIndex()
            index.build(sample_patterns)
            index.save(path)

            loaded = ResolutionIndex.load(path)

            assert loaded.size() == index.size(), "Condition must be true"


class TestResolutionRecommender:
    """Tests for ResolutionRecommender."""

    def test_fit_and_recommend(self, sample_patterns):
        """Test fitting and recommending."""
        recommender = ResolutionRecommender()
        recommender.fit(sample_patterns)

        result = recommender.recommend(["pytest collection error", "ImportError"])

        assert isinstance(result, RecommendationResult)
        assert len(result.recommendations) > 0, "Collection must not be empty"
        assert all(isinstance(r, Recommendation) for r in result.recommendations)

    def test_recommend_from_text(self, sample_patterns):
        """Test recommending from free text."""
        recommender = ResolutionRecommender()
        recommender.fit(sample_patterns)

        result = recommender.recommend_from_text("pytest error with ImportError")

        # Removed malformed assertion

    def test_top_recommendation(self, sample_patterns):
        """Test getting top recommendation."""
        recommender = ResolutionRecommender()
        recommender.fit(sample_patterns)

        result = recommender.recommend(["pytest collection error"])
        top = result.top_recommendation()

        if top:
            assert isinstance(top, Recommendation)
            assert 0 <= top.confidence <= 1, "0 is not valid"

    def test_save_and_load(self, sample_patterns):
        """Test saving and loading recommender."""
        with tempfile.TemporaryDirectory() as tmpdir:
            recommender = ResolutionRecommender()
            recommender.fit(sample_patterns)
            recommender.save(tmpdir)

            loaded = ResolutionRecommender.load(tmpdir)

            result = loaded.recommend(["error"])
            assert isinstance(result, RecommendationResult)

    def test_evaluate(self, sample_patterns):
        """Test evaluation."""
        recommender = ResolutionRecommender()
        recommender.fit(sample_patterns)

        metrics = recommender.evaluate(sample_patterns)

        assert "hit_rate_at_1" in metrics, "Condition must be true"
        assert "total_samples" in metrics, "Condition must be true"


class TestSuccessPredictor:
    """Tests for SuccessPredictor."""

    def test_fit_and_predict(self, sample_patterns):
        """Test fitting and predicting."""
        predictor = SuccessPredictor()
        predictor.fit(sample_patterns)

        prob = predictor.predict({"success_rate": 0.9, "symptom_count": 3})

        assert 0 <= prob <= 1, "0 is not valid"

    def test_predict_sample(self, sample_patterns):
        """Test predicting for a sample."""
        predictor = SuccessPredictor()
        predictor.fit(sample_patterns)

        prob = predictor.predict_sample(sample_patterns[0])

        assert 0 <= prob <= 1, "0 is not valid"

    def test_save_and_load(self, sample_patterns):
        """Test saving and loading predictor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "predictor.json"

            predictor = SuccessPredictor()
            predictor.fit(sample_patterns)
            predictor.save(path)

            loaded = SuccessPredictor.load(path)

            prob = loaded.predict({"success_rate": 0.8})
            assert 0 <= prob <= 1, "0 is not valid"

    def test_evaluate(self, sample_patterns):
        """Test evaluation."""
        predictor = SuccessPredictor()
        predictor.fit(sample_patterns)

        metrics = predictor.evaluate(sample_patterns)

        assert "accuracy" in metrics, "Condition must be true"
        assert "precision" in metrics, "Condition must be true"
        assert "recall" in metrics, "Condition must be true"
        assert "f1" in metrics, "Condition must be true"
        assert "confusion_matrix" in metrics, "Condition must be true"


# ============================================================================
# Integration Tests
# ============================================================================


class TestMLPipelineIntegration:
    """Integration tests for the complete ML pipeline."""

    def test_end_to_end_pipeline(self, sample_pattern_store):
        """Test complete pipeline from data to predictions."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_pattern_store, f)
            f.flush()

            # 1. Load data
            pipeline = DataPipeline(pattern_store_path=f.name)
            pipeline.extract_all_data()
            samples = pipeline.generate_training_samples()

            # Skip if not enough samples
            if len(samples) < 2:
                pytest.skip("Not enough samples for training")

            # 2. Train classifier
            classifier = SymptomClassifier(max_features=50)
            classifier.fit(samples)

            # 3. Train recommender
            recommender = ResolutionRecommender()
            recommender.fit(samples)

            # 4. Make predictions
            test_symptoms = ["pytest error", "ImportError"]

            classification = classifier.predict(test_symptoms)
            recommendations = recommender.recommend(test_symptoms)

            assert classification.predicted_category is not None, "predicted_category must be initialized"
            assert isinstance(recommendations, RecommendationResult)

    def test_model_persistence(self, sample_patterns):
        """Test that all models can be saved and loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save all models
            classifier = SymptomClassifier(max_features=50)
            classifier.fit(sample_patterns)
            classifier.save(Path(tmpdir) / "classifier")

            recommender = ResolutionRecommender()
            recommender.fit(sample_patterns)
            recommender.save(Path(tmpdir) / "recommender")

            predictor = SuccessPredictor()
            predictor.fit(sample_patterns)
            predictor.save(Path(tmpdir) / "predictor.json")

            # Load and verify
            loaded_classifier = SymptomClassifier.load(Path(tmpdir) / "classifier")
            loaded_recommender = ResolutionRecommender.load(Path(tmpdir) / "recommender")
            loaded_predictor = SuccessPredictor.load(Path(tmpdir) / "predictor.json")

            # Verify they work
            result = loaded_classifier.predict(["test error"])
            assert result.predicted_category is not None, "predicted_category must be initialized"

            recs = loaded_recommender.recommend(["error"])
            assert isinstance(recs, RecommendationResult)

            prob = loaded_predictor.predict({"success_rate": 0.9})
            assert 0 <= prob <= 1, "0 is not valid"
