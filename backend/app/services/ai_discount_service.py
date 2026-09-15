"""AI and Rule-Based Dynamic Discount Recommendation Service."""

import json
import logging
import time
from collections import deque
from decimal import Decimal
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from sqlalchemy.orm import Session
from app.config import settings
from app.models.batch import ProductBatch
from app.schemas.ai import AIDiscountResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self, max_requests_per_minute: int = 30) -> None:
        self.max_requests = max_requests_per_minute
        self.timestamps: deque = deque()

    def allow_request(self) -> bool:
        """Check whether another request is allowed within the window."""
        now = time.time()
        # Remove timestamps older than 60 seconds
        while self.timestamps and now - self.timestamps[0] > 60:
            self.timestamps.popleft()

        if len(self.timestamps) < self.max_requests:
            self.timestamps.append(now)
            return True
        return False


rate_limiter = RateLimiter(settings.AI_RATE_LIMIT_PER_MINUTE)


class AIDiscountService:
    """Service providing intelligent dynamic discount proposals with versioned prompts and resilient fallback."""

    @staticmethod
    def _load_prompt_template(version: str) -> str:
        """Load prompt template for a specific version from prompts directory."""
        prompt_path = (
            settings.BASE_DIR
            / "prompts"
            / "versions"
            / f"{version}_discount_recommendation.txt"
        )
        if not prompt_path.exists():
            # Fallback to v1
            prompt_path = (
                settings.BASE_DIR
                / "prompts"
                / "versions"
                / "v1_discount_recommendation.txt"
            )
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

        # In-code ultimate fallback prompt
        return (
            "Phân tích lô hàng {product_name}, giá {original_price}, còn {days_until_expiry} ngày, "
            "tồn kho {stock_quantity}. Đề xuất phần trăm giảm giá dưới dạng JSON."
        )

    @classmethod
    def evaluate_batch_discount(
        cls,
        db: Session,
        batch_id: int,
        average_daily_sales: Optional[float] = None,
        competitor_price: Optional[Decimal] = None,
        custom_instruction: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> AIDiscountResponse:
        """Evaluate a product batch and generate an optimal discount recommendation."""
        batch = db.query(ProductBatch).filter(ProductBatch.id == batch_id).first()
        if not batch:
            raise ValueError(f"Không tìm thấy lô hàng với ID: {batch_id}")

        product = batch.product
        days_left = batch.days_until_expiry
        original_price = Decimal(str(product.original_price))
        version = prompt_version or settings.PROMPT_VERSION

        # Default estimated sales if not provided
        est_daily_sales = average_daily_sales if average_daily_sales is not None else 2.5
        comp_price = competitor_price if competitor_price is not None else original_price

        # Check rate limiter
        if not rate_limiter.allow_request():
            logger.warning("AI Rate limit reached. Falling back to Rule-Based Engine.")
            return cls._rule_based_fallback(
                batch=batch,
                days_left=days_left,
                original_price=original_price,
                average_daily_sales=est_daily_sales,
                competitor_price=comp_price,
                reason_prefix="[Hệ thống kích hoạt Rule do đạt giới hạn Request AI] ",
                version=version,
            )

        # Attempt OpenAI API call if key is configured
        if settings.OPENAI_API_KEY:
            try:
                template = cls._load_prompt_template(version)
                prompt = template.format(
                    product_name=product.name,
                    original_price=float(original_price),
                    stock_quantity=batch.stock_quantity,
                    days_until_expiry=days_left,
                    average_daily_sales=est_daily_sales,
                    competitor_price=float(comp_price),
                    custom_instruction=custom_instruction or "Không có",
                )

                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.OPENAI_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional retail pricing engine. Output strictly JSON.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.2,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=settings.AI_TIMEOUT_SECONDS,
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)

                    discount_rate = int(parsed.get("suggested_discount_rate", 0))
                    discount_rate = max(0, min(100, discount_rate))
                    suggested_price = round(
                        original_price * (Decimal("1.00") - Decimal(str(discount_rate)) / Decimal("100")),
                        2,
                    )

                    return AIDiscountResponse(
                        batch_id=batch.id,
                        batch_code=batch.batch_code,
                        product_name=product.name,
                        original_price=original_price,
                        days_until_expiry=days_left,
                        stock_quantity=batch.stock_quantity,
                        suggested_discount_rate=discount_rate,
                        suggested_price=suggested_price,
                        urgency_level=parsed.get("urgency_level", "moderate"),
                        reasoning=parsed.get("reasoning", "Đề xuất tối ưu hóa doanh thu bởi OpenAI."),
                        confidence_score=float(parsed.get("confidence_score", 0.9)),
                        engine_used="openai_gpt",
                        prompt_version=version,
                    )
            except Exception as exc:
                logger.warning(f"OpenAI call failed or timed out: {exc}. Using Rule-Based Engine.")

        # Fallback to Rule-Based Engine
        return cls._rule_based_fallback(
            batch=batch,
            days_left=days_left,
            original_price=original_price,
            average_daily_sales=est_daily_sales,
            competitor_price=comp_price,
            reason_prefix="",
            version=version,
        )

    @staticmethod
    def _rule_based_fallback(
        batch: ProductBatch,
        days_left: int,
        original_price: Decimal,
        average_daily_sales: float,
        competitor_price: Decimal,
        reason_prefix: str,
        version: str,
    ) -> AIDiscountResponse:
        """Heuristic rule-based clearance engine guaranteeing 100% uptime."""
        # Calculate days needed to clear stock at current sales rate
        stock = batch.stock_quantity
        days_to_clear = stock / (average_daily_sales if average_daily_sales > 0 else 1.0)

        if days_left <= 0:
            discount_rate = 100
            urgency = "critical"
            reason = "Lô hàng đã hết hạn sử dụng. Cần ngừng bán và chuyển xử lý hủy."
            confidence = 1.0
        elif days_left <= 2:
            discount_rate = 70
            urgency = "critical"
            reason = f"Chỉ còn {days_left} ngày đến hạn sử dụng! Cần xả hàng cấp tốc giảm 70% để thu hồi vốn tối thiểu."
            confidence = 0.95
        elif days_left <= 4:
            discount_rate = 50
            urgency = "critical"
            reason = f"Còn {days_left} ngày đến hạn. Tồn kho {stock} hộp trong khi cần ~{days_to_clear:.1f} ngày để bán hết. Đề xuất giảm 50%."
            confidence = 0.92
        elif days_left <= 7:
            discount_rate = 35 if days_to_clear > days_left else 25
            urgency = "high"
            reason = f"Hạn sử dụng còn 1 tuần ({days_left} ngày). Áp dụng chiết khấu {discount_rate}% nhằm kích cầu tiêu dùng nhanh."
            confidence = 0.88
        elif days_left <= 14:
            discount_rate = 20 if days_to_clear > days_left else 10
            urgency = "moderate"
            reason = f"Còn {days_left} ngày đến hạn. Đề xuất giảm nhẹ {discount_rate}% để duy trì tốc độ xuất kho ổn định."
            confidence = 0.85
        else:
            discount_rate = 10 if days_to_clear > days_left * 1.5 else 0
            urgency = "low"
            reason = f"Lô hàng an toàn ({days_left} ngày đến hạn). {'Đề xuất kích cầu 10% do tồn kho cao.' if discount_rate > 0 else 'Giữ nguyên giá niêm yết.'}"
            confidence = 0.80

        suggested_price = round(
            original_price * (Decimal("1.00") - Decimal(str(discount_rate)) / Decimal("100")),
            2,
        )

        return AIDiscountResponse(
            batch_id=batch.id,
            batch_code=batch.batch_code,
            product_name=batch.product.name,
            original_price=original_price,
            days_until_expiry=days_left,
            stock_quantity=batch.stock_quantity,
            suggested_discount_rate=discount_rate,
            suggested_price=suggested_price,
            urgency_level=urgency,
            reasoning=f"{reason_prefix}{reason}",
            confidence_score=confidence,
            engine_used="rule_based_fallback",
            prompt_version=version,
        )
