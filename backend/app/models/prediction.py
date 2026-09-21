from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    product_name = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)
    review_title = Column(String(255), nullable=False)
    review_text = Column(Text, nullable=False)
    
    predicted_class = Column(Integer, nullable=False)
    predicted_label = Column(String(50), nullable=False)
    probability_deceptive = Column(Float, nullable=True)
    probability_genuine = Column(Float, nullable=True)
    threshold_used = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="predictions")
