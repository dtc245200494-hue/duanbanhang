import re
import time
from collections import deque
from typing import Dict, List

import openai

from app.config import (
    AI_MAX_CALLS_PER_MINUTE,
    AI_TIMEOUT_SECONDS,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    PROMPTS_DIR,
)

SYSTEM_PROMPT = (
    "Bạn là trợ lý AI cho hệ thống quản lý bán hàng. "
    "Chỉ tư vấn dựa trên dữ liệu sản phẩm và dữ liệu bán hàng được cung cấp. "
    "Nếu thiếu dữ liệu, hãy nói rõ."
)


class AIServiceError(Exception):
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


_call_times: deque = deque()
_PHONE_RE = re.compile(r"(?:\+84|84|0)\d{8,10}")
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+")


def load_prompt(filename: str, **variables) -> str:
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise AIServiceError(f"Không tìm thấy prompt template: {filename}", 500)
    text = path.read_text(encoding="utf-8")
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def mask_sensitive(text: str) -> str:
    text = _EMAIL_RE.sub("[email-da-an]", text)
    text = _PHONE_RE.sub(lambda m: m.group(0)[:3] + "*****" + m.group(0)[-2:], text)
    return text


def _check_rate_limit() -> None:
    now = time.time()
    while _call_times and now - _call_times[0] > 60:
        _call_times.popleft()
    if len(_call_times) >= AI_MAX_CALLS_PER_MINUTE:
        raise AIServiceError(
            "Quá nhiều yêu cầu AI trong một phút. Vui lòng thử lại sau.", 429
        )
    _call_times.append(now)


def generate(prompt: str) -> str:
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_api_key_here":
        raise AIServiceError("OPENAI_API_KEY chưa được cấu hình trong file .env")
    _check_rate_limit()
    client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        timeout=AI_TIMEOUT_SECONDS,
        max_retries=0,
    )
    last_error = None
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=800,
            )
            content = ""
            if response.choices:
                content = (response.choices[0].message.content or "").strip()
            if len(content) < 2:
                raise AIServiceError(
                    "AI trả về phản hồi rỗng hoặc sai định dạng.", 502
                )
            return content
        except openai.RateLimitError as exc:
            last_error = AIServiceError(
                "AI đang quá tải (rate limit). Vui lòng thử lại sau.", 429
            )
            time.sleep(1)
            if attempt == 1:
                raise last_error from exc
        except openai.APITimeoutError as exc:
            raise AIServiceError(
                "AI phản hồi quá thời gian chờ (timeout).", 504
            ) from exc
        except openai.AuthenticationError as exc:
            raise AIServiceError("API key AI không hợp lệ.", 502) from exc
        except openai.OpenAIError as exc:
            raise AIServiceError(
                f"Lỗi khi gọi AI API: {type(exc).__name__}", 502
            ) from exc
    raise last_error or AIServiceError("Lỗi gọi AI không xác định.", 502)
