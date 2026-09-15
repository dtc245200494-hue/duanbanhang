"""Unit tests for AI Discount Recommendations audit and approval workflow."""

from app.models.batch import ProductBatch
from app.models.user import User
from app.services.recommendation_service import RecommendationService


def test_ai_recommendation_approval_workflow(db_session):
    """Test AI proposal creation, approval, and automatic discount rate update."""
    b2 = db_session.query(ProductBatch).filter(ProductBatch.batch_code == "B2").first()
    assert b2.discount_rate == 0

    user = db_session.query(User).first()

    # 1. AI generates proposal
    rec = RecommendationService.create_recommendation(
        db=db_session,
        batch_id=b2.id,
        recommended_discount=35,
        reason="Lô hàng còn 10 ngày, tốc độ bán chậm, đề xuất giảm 35%.",
    )
    assert rec.id is not None
    assert rec.status == "pending"
    assert rec.approved_by is None

    # 2. Manager approves
    approved_rec = RecommendationService.approve_recommendation(
        db=db_session, recommendation_id=rec.id, user_id=user.id
    )
    assert approved_rec.status == "approved"
    assert approved_rec.approved_by == user.id

    # Verify batch discount_rate was updated
    db_session.refresh(b2)
    assert b2.discount_rate == 35


def test_ai_recommendation_rejection(db_session):
    """Test AI proposal rejection keeps batch discount unchanged."""
    b1 = db_session.query(ProductBatch).filter(ProductBatch.batch_code == "B1").first()
    initial_rate = b1.discount_rate
    user = db_session.query(User).first()

    rec = RecommendationService.create_recommendation(
        db=db_session,
        batch_id=b1.id,
        recommended_discount=90,
        reason="Quá cận date, đề xuất giảm 90%.",
    )

    rejected_rec = RecommendationService.reject_recommendation(
        db=db_session, recommendation_id=rec.id, user_id=user.id
    )
    assert rejected_rec.status == "rejected"

    db_session.refresh(b1)
    assert b1.discount_rate == initial_rate
