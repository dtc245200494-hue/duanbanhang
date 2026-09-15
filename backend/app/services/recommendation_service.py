"""AI Discount Recommendation audit and manager approval workflow service."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ai_recommendation import AIDiscountRecommendation
from app.models.batch import ProductBatch


class RecommendationService:
    """Service managing AI discount proposals and manager review/approval workflow."""

    @staticmethod
    def create_recommendation(
        db: Session, batch_id: int, recommended_discount: int, reason: str
    ) -> AIDiscountRecommendation:
        """Record an AI-generated clearance proposal awaiting manager approval."""
        rec = AIDiscountRecommendation(
            batch_id=batch_id,
            recommended_discount=recommended_discount,
            reason=reason,
            status="pending",
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

    @staticmethod
    def approve_recommendation(
        db: Session, recommendation_id: int, user_id: int
    ) -> AIDiscountRecommendation:
        """Approve an AI recommendation and apply the discount rate to the batch."""
        rec = (
            db.query(AIDiscountRecommendation)
            .filter(AIDiscountRecommendation.id == recommendation_id)
            .first()
        )
        if not rec:
            raise ValueError(f"Không tìm thấy đề xuất AI với ID: {recommendation_id}")

        if rec.status == "approved":
            return rec

        rec.status = "approved"
        rec.approved_by = user_id

        # Automatically update batch's discount_rate
        if rec.batch:
            rec.batch.discount_rate = rec.recommended_discount

        db.commit()
        db.refresh(rec)
        return rec

    @staticmethod
    def reject_recommendation(
        db: Session, recommendation_id: int, user_id: int
    ) -> AIDiscountRecommendation:
        """Reject an AI proposal without altering batch discount."""
        rec = (
            db.query(AIDiscountRecommendation)
            .filter(AIDiscountRecommendation.id == recommendation_id)
            .first()
        )
        if not rec:
            raise ValueError(f"Không tìm thấy đề xuất AI với ID: {recommendation_id}")

        rec.status = "rejected"
        rec.approved_by = user_id
        db.commit()
        db.refresh(rec)
        return rec

    @staticmethod
    def list_recommendations(
        db: Session,
        status: Optional[str] = None,
        batch_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AIDiscountRecommendation]:
        """Fetch audit log of AI clearance proposals."""
        query = db.query(AIDiscountRecommendation)
        if status:
            query = query.filter(AIDiscountRecommendation.status == status)
        if batch_id:
            query = query.filter(AIDiscountRecommendation.batch_id == batch_id)
        return query.order_by(AIDiscountRecommendation.created_at.desc()).offset(skip).limit(limit).all()
