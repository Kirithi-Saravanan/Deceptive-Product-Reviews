from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any

from app.db.session import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Total reviews analyzed
    total_reviews = db.query(Prediction).filter(Prediction.user_id == current_user.id).count()
    
    # Deceptive reviews
    deceptive_reviews = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.predicted_class == 1
    ).count()
    
    # Genuine reviews
    genuine_reviews = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.predicted_class == 0
    ).count()
    
    # Average rating
    avg_rating = db.query(func.avg(Prediction.rating)).filter(Prediction.user_id == current_user.id).scalar()
    
    # Recent analyses
    recent = db.query(Prediction).filter(Prediction.user_id == current_user.id).order_by(Prediction.created_at.desc()).limit(5).all()

    return {
        "total_reviews": total_reviews,
        "deceptive_reviews": deceptive_reviews,
        "genuine_reviews": genuine_reviews,
        "average_rating": float(avg_rating) if avg_rating else 0.0,
        "recent_analyses": [
            {
                "id": p.id,
                "product_name": p.product_name,
                "rating": p.rating,
                "predicted_label": p.predicted_label,
                "created_at": p.created_at
            } for p in recent
        ]
    }

@router.get("/trends")
def get_dashboard_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Ratings distribution (ensure 1-5 all present)
    ratings_map = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    ratings_dist = (
        db.query(Prediction.rating, func.count(Prediction.id))
        .filter(Prediction.user_id == current_user.id)
        .group_by(Prediction.rating)
        .all()
    )
    for r, count in ratings_dist:
        if r in ratings_map:
            ratings_map[r] = count

    ratings_distribution = [
        {"rating": f"{k}★", "count": v} for k, v in sorted(ratings_map.items())
    ]

    # Daily prediction trends
    daily_rows = (
        db.query(
            func.date(Prediction.created_at).label("day"),
            Prediction.predicted_class,
            func.count(Prediction.id)
        )
        .filter(Prediction.user_id == current_user.id)
        .group_by(func.date(Prediction.created_at), Prediction.predicted_class)
        .order_by(func.date(Prediction.created_at).asc())
        .all()
    )
    
    trends_map = {}
    for day, pred_class, count in daily_rows:
        day_str = str(day) if day else "Recent"
        if day_str not in trends_map:
            trends_map[day_str] = {"date": day_str, "total": 0, "deceptive": 0, "genuine": 0}
        trends_map[day_str]["total"] += count
        if pred_class == 1:
            trends_map[day_str]["deceptive"] += count
        else:
            trends_map[day_str]["genuine"] += count

    return {
        "ratings_distribution": ratings_distribution,
        "prediction_trends": list(trends_map.values())
    }
