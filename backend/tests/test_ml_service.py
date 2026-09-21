from app.services.model_service import model_service


def test_model_service_loads_predictor():
    predictor = model_service.get_predictor()
    assert predictor is not None
    assert hasattr(predictor, "pipeline")
    assert hasattr(predictor, "threshold")
    # Verify selected threshold is exactly 0.40 as locked in Phase 3B
    assert predictor.threshold == 0.40


def test_model_service_predict_returns_probabilities():
    result = model_service.predict(
        review_text="I bought this laptop last week. Battery life lasts about 7 hours and display is clear.",
        rating=4
    )
    assert isinstance(result, dict)
    assert "predicted_class" in result
    assert result["predicted_class"] in (0, 1)
    assert "predicted_label" in result
    assert result["predicted_label"] in ("Genuine", "Deceptive")
    assert "probability_deceptive" in result
    assert "probability_genuine" in result
    assert result["probability_deceptive"] is not None
    assert result["probability_genuine"] is not None
    assert 0.0 <= result["probability_deceptive"] <= 1.0
    assert 0.0 <= result["probability_genuine"] <= 1.0
    # Probabilities should sum to approximately 1.0
    assert abs((result["probability_deceptive"] + result["probability_genuine"]) - 1.0) < 1e-4
    assert result["threshold_used"] == 0.40
