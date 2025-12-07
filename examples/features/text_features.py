"""Example text feature definitions."""
from datetime import datetime

from codex_ml.features.feature_store import Feature, FeatureGroup, FeatureMetadata


def create_text_features() -> FeatureGroup:
    """Create text processing feature group."""
    
    now = datetime.now().isoformat()
    
    # Token count feature
    token_count = Feature(
        name="token_count",
        transform_fn=lambda inputs: len(inputs["text"].split()),
        metadata=FeatureMetadata(
            name="token_count",
            version="1.0.0",
            dtype="int",
            description="Number of tokens (words) in text",
            created_at=now,
            updated_at=now,
            tags={"category": "text_stats", "unit": "count"},
        ),
    )
    
    # Character count feature
    char_count = Feature(
        name="char_count",
        transform_fn=lambda inputs: len(inputs["text"]),
        metadata=FeatureMetadata(
            name="char_count",
            version="1.0.0",
            dtype="int",
            description="Number of characters in text",
            created_at=now,
            updated_at=now,
            tags={"category": "text_stats", "unit": "count"},
        ),
    )
    
    # Average word length feature
    def avg_word_len(inputs):
        words = inputs["text"].split()
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)
    
    avg_word_length = Feature(
        name="avg_word_length",
        transform_fn=avg_word_len,
        dependencies=["token_count"],
        metadata=FeatureMetadata(
            name="avg_word_length",
            version="1.0.0",
            dtype="float",
            description="Average word length in characters",
            created_at=now,
            updated_at=now,
            tags={"category": "text_stats", "unit": "characters"},
        ),
    )
    
    # Uppercase ratio feature
    def uppercase_ratio(inputs):
        text = inputs["text"]
        if not text:
            return 0.0
        uppercase = sum(1 for c in text if c.isupper())
        return uppercase / len(text)
    
    uppercase_ratio_feature = Feature(
        name="uppercase_ratio",
        transform_fn=uppercase_ratio,
        metadata=FeatureMetadata(
            name="uppercase_ratio",
            version="1.0.0",
            dtype="float",
            description="Ratio of uppercase characters to total characters",
            created_at=now,
            updated_at=now,
            tags={"category": "text_style", "range": "[0, 1]"},
        ),
    )
    
    return FeatureGroup(
        name="text_features",
        features=[token_count, char_count, avg_word_length, uppercase_ratio_feature],
        version="1.0.0",
        description="Basic text processing and statistics features",
    )


if __name__ == "__main__":
    # Example usage
    from codex_ml.features.feature_store import FeatureStore
    
    store = FeatureStore(".codex/feature_store")
    group = create_text_features()
    store.register_feature_group(group)
    
    # Test feature materialization
    test_input = {"text": "Hello World! This is a TEST."}
    features = store.materialize_features(
        ["token_count", "char_count", "avg_word_length", "uppercase_ratio"],
        test_input
    )
    
    print("Text:", test_input["text"])
    print("Features:", features)
