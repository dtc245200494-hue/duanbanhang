"""AI-powered dynamic discounting API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_optional
from app.models.batch import ProductBatch
from app.models.user import User
from app.schemas.ai import AIDiscountRequest, AIDiscountResponse
from app.services.ai_discount_service import AIDiscountService
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/ai-discount", tags=["AI Discount"])


@router.post("/evaluate", response_model=AIDiscountResponse)
def evaluate_discount(
    req: AIDiscountRequest,
    prompt_version: Optional[str] = Query(None, description="Tùy chọn phiên bản prompt: v1, v2"),
    record_proposal: bool = Query(True, description="Tự động ghi nhận vào ai_discount_recommendations (pending)"),
    db: Session = Depends(get_db),
) -> AIDiscountResponse:
    """Evaluate batch for clearance and return AI-recommended discount rate and reasoning."""
    try:
        recommendation = AIDiscountService.evaluate_batch_discount(
            db=db,
            batch_id=req.batch_id,
            average_daily_sales=req.average_daily_sales,
            competitor_price=req.competitor_price,
            custom_instruction=req.custom_instruction,
            prompt_version=prompt_version,
        )

        # Automatically record recommendation into ai_discount_recommendations table
        if record_proposal:
            RecommendationService.create_recommendation(
                db=db,
                batch_id=req.batch_id,
                recommended_discount=recommendation.suggested_discount_rate,
                reason=recommendation.reasoning,
            )

        return recommendation
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi đánh giá chiết khấu AI: {str(exc)}",
        )


@router.post("/{batch_id}/apply", response_model=AIDiscountResponse)
def evaluate_and_apply_discount(
    batch_id: int,
    prompt_version: Optional[str] = Query(None, description="v1 hoặc v2"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> AIDiscountResponse:
    """Evaluate with AI and immediately apply the proposed discount rate to the batch."""
    try:
        rec = AIDiscountService.evaluate_batch_discount(
            db=db,
            batch_id=batch_id,
            prompt_version=prompt_version,
        )

        # Update batch discount_rate
        batch = db.query(ProductBatch).filter(ProductBatch.id == batch_id).first()
        if batch:
            batch.discount_rate = rec.suggested_discount_rate
            db.commit()

        # Record recommendation as approved
        rec_entry = RecommendationService.create_recommendation(
            db=db,
            batch_id=batch_id,
            recommended_discount=rec.suggested_discount_rate,
            reason=rec.reasoning,
        )
        user_id = current_user.id if current_user else None
        if user_id:
            RecommendationService.approve_recommendation(
                db=db, recommendation_id=rec_entry.id, user_id=user_id
            )

        return rec
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
