"""WebSocket 连接管理器 —— 广播通知、多客户端管理"""

import json
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """管理所有活跃的 WebSocket 连接"""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """接受连接并注册到用户"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """移除断开的连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                ws for ws in self.active_connections[user_id] if ws != websocket
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_to_user(self, user_id: int, message: dict):
        """向指定用户的所有连接发送消息"""
        if user_id in self.active_connections:
            payload = json.dumps(message, ensure_ascii=False)
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_text(payload)
                except Exception:
                    pass

    async def broadcast(self, message: dict):
        """向所有连接广播消息"""
        payload = json.dumps(message, ensure_ascii=False)
        for connections in self.active_connections.values():
            for ws in connections:
                try:
                    await ws.send_text(payload)
                except Exception:
                    pass


manager = ConnectionManager()
