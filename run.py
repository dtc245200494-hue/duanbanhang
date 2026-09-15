import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Khởi chạy Hệ thống Bán hàng Thông minh & AI Dynamic Clearance...")
    print("📍 URL Giao diện Web SPA: http://127.0.0.1:8000")
    print("📖 API Swagger Docs:       http://127.0.0.1:8000/docs\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)