"""FastAPI 主入口 —— 应用启动、路由注册、中间件、生命周期管理"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import init_db, async_session_factory
from models import User
from auth import get_current_user
from websocket import manager
from routers import users_router, items_router

settings = get_settings()


# ============ 应用生命周期 ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时创建数据库表，关闭时清理资源"""
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============ CORS 中间件 ============

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 全局异常处理 ============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"},
    )


# ============ 注册路由 ============

app.include_router(users_router)
app.include_router(items_router)


# ============ WebSocket 端点 ============

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...),
):
    """WebSocket 连接 —— 需要 JWT Token 认证"""
    # 简化版 Token 验证：从 Query 参数获取 Token
    from jose import jwt as jose_jwt, JWTError

    try:
        payload = jose_jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_user_id = int(payload.get("sub", 0))
        if token_user_id != user_id:
            await websocket.close(code=4003, reason="Token 与用户不匹配")
            return
    except (JWTError, ValueError):
        await websocket.close(code=4001, reason="无效的 Token")
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            # 保持连接，接收客户端消息
            data = await websocket.receive_text()
            # 广播消息给同一用户的所有连接
            await manager.send_to_user(user_id, {
                "type": "echo",
                "message": f"服务器收到: {data}",
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


# ============ 健康检查 ============

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
