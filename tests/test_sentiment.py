"""Unit tests for sentiment mapping (no model download in CI)."""

from src.sentiment import map_binary_to_three_way


def test_positive_high_confidence():
    pred = map_binary_to_three_way("POSITIVE", 0.92)
    assert pred.label == "positive"
    assert pred.confidence == 0.92
    assert pred.signed_score == 0.92


def test_negative_high_confidence():
    pred = map_binary_to_three_way("NEGATIVE", 0.88)
    assert pred.label == "negative"
    assert pred.signed_score == -0.88


def test_neutral_low_confidence():
    pred = map_binary_to_three_way("POSITIVE", 0.51)
    assert pred.label == "neutral"
    assert pred.signed_score == 0.0


def test_classify_texts_with_mock_classifier():
    from src.sentiment import classify_texts

    class MockClassifier:
        def __call__(self, texts):
            return [{"label": "POSITIVE", "score": 0.9} for _ in texts]

    preds = classify_texts(["great app", "love it"], classifier=MockClassifier())
    assert len(preds) == 2
    assert preds[0].label == "positive"
