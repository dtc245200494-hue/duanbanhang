"""Unit tests for AI discount recommendation and rule-based fallback."""

from app.models.batch import ProductBatch
from app.services.ai_discount_service import AIDiscountService


def test_ai_discount_rule_based_fallback(db_session):
    """Test AI discount service generates sensible recommendation via rule-based engine."""
    b1 = db_session.query(ProductBatch).filter(ProductBatch.batch_code == "B1").first()
    assert b1 is not None
    # B1 expires in 2 days

    rec = AIDiscountService.evaluate_batch_discount(
        db=db_session,
        batch_id=b1.id,
        average_daily_sales=2.0,
    )

    assert rec.batch_id == b1.id
    assert rec.days_until_expiry == 2
    assert rec.urgency_level == "critical"
    assert rec.suggested_discount_rate >= 50
    assert rec.engine_used in ["rule_based_fallback", "openai_gpt"]
    assert len(rec.reasoning) > 10


def test_prompt_template_loader():
    """Test that versioned prompt templates load properly."""
    content_v1 = AIDiscountService._load_prompt_template("v1")
    assert "{product_name}" in content_v1
    assert "QUY TẮC ĐỊNH GIÁ" in content_v1

    content_v2 = AIDiscountService._load_prompt_template("v2")
    assert "{product_name}" in content_v2
    assert "MỤC TIÊU" in content_v2
