import joblib
import pandas as pd
import json


class ReviewPredictor:
    def __init__(
        self,
        model_path: str = 'ml/models/model.joblib',
        metadata_path: str = 'ml/models/model_metadata.json'
    ):
        self.pipeline = joblib.load(model_path)
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        # Use the threshold selected during validation-based optimisation.
        # Falls back to 0.5 if the field is absent (e.g. legacy model files).
        self.threshold = float(self.metadata.get('selected_threshold', 0.5))

    def predict_review(self, review_text: str, metadata: dict = None) -> dict:
        """
        Predicts whether a review is Deceptive or Genuine.

        Returns
        -------
        dict with keys:
            predicted_class       – int (1 = Deceptive, 0 = Genuine)
            predicted_label       – str
            probability_deceptive – float | None  (None for non-probabilistic models)
            probability_genuine   – float | None
            threshold_used        – float (the decision threshold applied)
        """
        if metadata is None:
            metadata = {}

        # Build a 1-row DataFrame matching the training schema.
        input_data = {
            'review_text': [review_text],
            'review_rating': [metadata.get('review_rating', 0)],
            'number_of_helpful': [metadata.get('number_of_helpful', 0)],
            'number_of_photos': [metadata.get('number_of_photos', 0)],
        }
        df = pd.DataFrame(input_data)

        # Combined pipelines expect a DataFrame; text-only pipelines expect a Series.
        X_input = df if 'Combined' in self.metadata.get('selected_model', '') else df['review_text']

        if hasattr(self.pipeline, 'predict_proba'):
            probs = self.pipeline.predict_proba(X_input)[0]
            prob_genuine   = float(probs[0])
            prob_deceptive = float(probs[1])
            # Apply the validated, locked threshold explicitly.
            prediction = 1 if prob_deceptive >= self.threshold else 0
        else:
            # LinearSVC or similar — no probability output; use hard boundary.
            prediction     = int(self.pipeline.predict(X_input)[0])
            prob_deceptive = None
            prob_genuine   = None

        return {
            'predicted_class':       prediction,
            'predicted_label':       'Deceptive' if prediction == 1 else 'Genuine',
            'probability_deceptive': prob_deceptive,
            'probability_genuine':   prob_genuine,
            'threshold_used':        self.threshold,
        }

