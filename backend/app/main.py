"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="语联灵犀 API",
    description="基于大模型 Agent 与工具链框架的异构工具联动系统",
    version="1.0.0"
)

# 配置 CORS（跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "语联灵犀 API 服务",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





