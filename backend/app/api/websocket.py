"""
WebSocket Routes
WebSocket 路由 - 全局 WebSocket 端点
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from app.core.websocket_manager import ws_manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 连接端点

    接收和推送消息格式:
    {
        "event": "event_name",
        "data": { ... }
    }

    推送事件类型:
    - bench_status_update: 台架状态更新
    - bench_created: 新台架创建
    - bench_updated: 台架信息更新
    - bench_deleted: 台架删除
    - bench_moved: 台架位置移动
    - bench_heartbeat: 台架心跳
    - bench_maintenance_changed: 维护状态变化
    - bench_alarm_cleared: 告警清除
    - alarm_created: 新告警
    - alarm_acknowledged: 告警确认
    - statistics_update: 统计数据更新
    - device_status_update: 设备状态更新（监控服务）
    """
    await ws_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                event = message.get("event", "unknown")

                if event == "ping":
                    await ws_manager.send_to(websocket, {"event": "pong", "data": {}})

                elif event == "subscribe":
                    channels = message.get("data", {}).get("channels", [])
                    await ws_manager.send_to(
                        websocket,
                        {"event": "subscribed", "data": {"channels": channels}},
                    )

                else:
                    await ws_manager.send_to(
                        websocket, {"event": "echo", "data": message}
                    )

            except json.JSONDecodeError:
                await ws_manager.send_to(
                    websocket, {"event": "error", "data": {"message": "Invalid JSON"}}
                )

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        await ws_manager.disconnect(websocket)
