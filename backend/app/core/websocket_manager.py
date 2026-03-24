"""
WebSocket Manager
WebSocket 连接管理器 - 用于实时推送状态变化
"""

import asyncio
from typing import List, Dict, Any, Optional
from fastapi import WebSocket
import json


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """广播消息到所有连接"""
        if not self.active_connections:
            return

        disconnected = []
        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"[WS] Error sending message: {e}")
                    disconnected.append(connection)

            for conn in disconnected:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)

    async def send_to(self, websocket: WebSocket, message: Dict[str, Any]):
        """发送消息到指定连接"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"[WS] Error sending message: {e}")
            await self.disconnect(websocket)

    @property
    def connection_count(self) -> int:
        """当前连接数"""
        return len(self.active_connections)


ws_manager = WebSocketManager()
