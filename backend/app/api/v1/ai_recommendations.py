"""AI Discount Recommendation audit and approval API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.ai_recommendation import AIDiscountRecommendation
from app.schemas.ai_recommendation import AIRecommendationOut
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/ai-recommendations", tags=["AI Recommendations"])


@router.get("", response_model=List[AIRecommendationOut])
def list_ai_recommendations(
    status_filter: Optional[str] = Query(None, alias="status", description="pending, approved, rejected"),
    batch_id: Optional[int] = Query(None, description="Lọc theo lô hàng"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[AIRecommendationOut]:
    """List historical AI discount proposals and their approval status."""
    recs = RecommendationService.list_recommendations(
        db=db, status=status_filter, batch_id=batch_id, skip=skip, limit=limit
    )

    results: List[AIRecommendationOut] = []
    for r in recs:
        results.append(
            AIRecommendationOut(
                id=r.id,
                batch_id=r.batch_id,
                recommended_discount=r.recommended_discount,
                reason=r.reason,
                status=r.status,
                approved_by=r.approved_by,
                approver_name=r.approver.full_name if r.approver else None,
                created_at=r.created_at,
                batch_code=r.batch.batch_code if r.batch else None,
                product_name=r.batch.product.name if (r.batch and r.batch.product) else None,
            )
        )
    return results


@router.post("/{recommendation_id}/approve", response_model=AIRecommendationOut)
def approve_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "store_manager"])),
) -> AIRecommendationOut:
    """Approve an AI recommendation and apply the proposed discount to the batch."""
    try:
        rec = RecommendationService.approve_recommendation(
            db=db, recommendation_id=recommendation_id, user_id=current_user.id
        )
        return AIRecommendationOut(
            id=rec.id,
            batch_id=rec.batch_id,
            recommended_discount=rec.recommended_discount,
            reason=rec.reason,
            status=rec.status,
            approved_by=rec.approved_by,
            approver_name=current_user.full_name,
            created_at=rec.created_at,
            batch_code=rec.batch.batch_code if rec.batch else None,
            product_name=rec.batch.product.name if (rec.batch and rec.batch.product) else None,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )


@router.post("/{recommendation_id}/reject", response_model=AIRecommendationOut)
def reject_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "store_manager"])),
) -> AIRecommendationOut:
    """Reject an AI recommendation."""
    try:
        rec = RecommendationService.reject_recommendation(
            db=db, recommendation_id=recommendation_id, user_id=current_user.id
        )
        return AIRecommendationOut(
            id=rec.id,
            batch_id=rec.batch_id,
            recommended_discount=rec.recommended_discount,
            reason=rec.reason,
            status=rec.status,
            approved_by=rec.approved_by,
            approver_name=current_user.full_name,
            created_at=rec.created_at,
            batch_code=rec.batch.batch_code if rec.batch else None,
            product_name=rec.batch.product.name if (rec.batch and rec.batch.product) else None,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
