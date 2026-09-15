"""Main FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.api.v1 import api_router
from app.services.inventory_service import InventoryService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smart_retail")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager replacing deprecated on_event handlers."""
    logger.info("Khởi động hệ thống Smart Retail...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.models.role import Role
        if db.query(Role).count() == 0:
            logger.info("Cơ sở dữ liệu chưa có dữ liệu, đang tự động nạp dữ liệu mẫu ban đầu...")
            from app.scripts.seed_data import seed_database
            seed_database()
        else:
            updated = InventoryService.refresh_batch_statuses(db)
            logger.info(f"Đã cập nhật trạng thái hạn dùng cho {updated} lô hàng.")
    except Exception as exc:
        logger.error(f"Lỗi khi khởi tạo / cập nhật dữ liệu lúc khởi động: {exc}")
    finally:
        db.close()
    yield
    logger.info("Đang tắt hệ thống Smart Retail...")


# Initialize FastAPI application with modern lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Hệ thống Quản lý Bán hàng, Lô hàng Cận date (FEFO) và Đề xuất Chiết khấu AI Thông minh.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static files setup
static_dir = Path(__file__).resolve().parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", include_in_schema=False)
def serve_web_gui():
    """Serve the modern Web GUI Single Page Application."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Welcome to Smart Retail API. Web GUI is being assembled."}


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
