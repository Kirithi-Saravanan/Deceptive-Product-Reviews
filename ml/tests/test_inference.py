import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from predict import ReviewPredictor

def test_inference_module():
    # Only run if model exists
    if not os.path.exists('ml/models/model.joblib'):
        pytest.skip("Model artifact not found. Run experiments first.")
        
    predictor = ReviewPredictor('ml/models/model.joblib', 'ml/models/model_metadata.json')
    
    # 1. Normal review
    res1 = predictor.predict_review("This product is completely fake and terrible.")
    assert 'predicted_class' in res1
    assert 'predicted_label' in res1
    assert res1['predicted_class'] in [0, 1]
    
    # 2. Empty input handling safely
    res2 = predictor.predict_review("")
    assert res2['predicted_class'] in [0, 1]
    
    # 3. With metadata
    res3 = predictor.predict_review("Good", {"review_rating": 5, "number_of_helpful": 10})
    assert res3['predicted_class'] in [0, 1]
    
    # 4. Check for proper score
    assert 'probability_deceptive' in res1
    assert 'threshold_used' in res1
    if hasattr(predictor.pipeline.named_steps['clf'], "predict_proba"):
        assert 'probability_deceptive' in res1
        assert 0.0 <= res1['probability_deceptive'] <= 1.0
