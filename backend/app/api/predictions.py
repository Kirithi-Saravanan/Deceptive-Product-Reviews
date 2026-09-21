from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.session import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionResponse
from app.api.auth import get_current_user
from app.services.model_service import model_service

router = APIRouter()

@router.post("/", response_model=PredictionResponse)
def analyze_review(
    *,
    db: Session = Depends(get_db),
    prediction_in: PredictionCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Analyze a new review and save the prediction.
    """
    try:
        # Run ML inference
        result = model_service.predict(prediction_in.review_text, prediction_in.rating)
        
        # Save to DB
        prediction = Prediction(
            user_id=current_user.id,
            product_name=prediction_in.product_name,
            rating=prediction_in.rating,
            review_title=prediction_in.review_title,
            review_text=prediction_in.review_text,
            predicted_class=result['predicted_class'],
            predicted_label=result['predicted_label'],
            probability_deceptive=result['probability_deceptive'],
            probability_genuine=result['probability_genuine'],
            threshold_used=result['threshold_used']
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[PredictionResponse])
def get_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve predictions for the current user.
    """
    predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    return predictions

@router.get("/{id}", response_model=PredictionResponse)
def get_prediction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific prediction by id.
    """
    prediction = db.query(Prediction).filter(Prediction.id == id, Prediction.user_id == current_user.id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction

@router.delete("/{id}", response_model=PredictionResponse)
def delete_prediction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete a specific prediction.
    """
    prediction = db.query(Prediction).filter(Prediction.id == id, Prediction.user_id == current_user.id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    db.delete(prediction)
    db.commit()
    return prediction
