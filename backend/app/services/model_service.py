import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root and ml/src to sys.path so we can import ml.src and unpickle custom transformers
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'ml' / 'src'))

from ml.src.predict import ReviewPredictor

class ModelService:
    _predictor: Optional[ReviewPredictor] = None

    @classmethod
    def get_predictor(cls) -> ReviewPredictor:
        if cls._predictor is None:
            # Construct absolute paths to artifacts
            model_path = str(project_root / 'ml' / 'models' / 'model.joblib')
            metadata_path = str(project_root / 'ml' / 'models' / 'model_metadata.json')
            
            # The ReviewPredictor relies on ml/src internally for unpickling custom functions.
            # Adding root to sys.path earlier helps with this.
            cls._predictor = ReviewPredictor(model_path=model_path, metadata_path=metadata_path)
            
        return cls._predictor

    @classmethod
    def predict(cls, review_text: str, rating: int) -> Dict[str, Any]:
        predictor = cls.get_predictor()
        # metadata structure for predict_review
        meta = {
            'review_rating': rating,
            'number_of_helpful': 0,
            'number_of_photos': 0
        }
        return predictor.predict_review(review_text, meta)

model_service = ModelService()
