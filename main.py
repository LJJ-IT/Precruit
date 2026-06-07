"""Precruit API 启动入口"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=9000,
        workers=1,
    )
