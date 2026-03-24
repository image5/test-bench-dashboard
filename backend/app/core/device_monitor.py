"""
Device Monitor Service
设备监控服务 - 定期检测设备在线状态和心跳超时
"""

import asyncio
import platform
import subprocess
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.bench import TestBench, BenchStatus


class DeviceMonitor:
    """设备监控器"""

    def __init__(self):
        self.is_running = False
        self.check_interval = 30  # 检测间隔（秒）- 30秒
        self.heartbeat_timeout = 30  # 心跳超时阈值（秒）
        self._ws_manager: Optional[any] = None

    def set_ws_manager(self, manager):
        """设置 WebSocket 管理器用于广播状态变化"""
        self._ws_manager = manager

    @staticmethod
    def ping_device(ip_address: str, timeout: int = 2) -> bool:
        """
        Ping 设备检测是否在线

        Args:
            ip_address: 设备 IP 地址
            timeout: 超时时间（秒）

        Returns:
            bool: 设备是否在线
        """
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "1", "-w", str(timeout * 1000), ip_address]
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout + 1,
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            print(f"[ERROR] Ping {ip_address} failed: {e}")
            return False

    def check_heartbeat_timeout(self, bench: TestBench) -> bool:
        """
        检查心跳是否超时

        Args:
            bench: 台架对象

        Returns:
            bool: 是否心跳超时
        """
        if bench.last_heartbeat is None:
            return True

        elapsed = (datetime.utcnow() - bench.last_heartbeat).total_seconds()
        return elapsed > self.heartbeat_timeout

    def check_device_status(self, bench: TestBench) -> tuple[BenchStatus, bool, str]:
        """
        检查设备状态

        Args:
            bench: 台架对象

        Returns:
            tuple: (新状态, 是否有变化, 变化原因)
        """
        if bench.is_under_maintenance:
            return bench.status, False, ""

        if bench.has_alarm:
            return bench.status, False, ""

        heartbeat_timeout = self.check_heartbeat_timeout(bench)

        if heartbeat_timeout:
            if bench.status != BenchStatus.OFFLINE:
                return BenchStatus.OFFLINE, True, "heartbeat_timeout"
            return bench.status, False, ""

        is_online = self.ping_device(bench.ip_address)

        if is_online:
            if bench.status == BenchStatus.OFFLINE:
                return BenchStatus.IDLE, True, "device_online"
            return bench.status, False, ""
        else:
            if bench.status != BenchStatus.OFFLINE:
                return BenchStatus.OFFLINE, True, "ping_failed"
            return bench.status, False, ""

    async def monitor_devices(self):
        """监控所有设备"""
        print("[INFO] Device monitor started")

        while self.is_running:
            try:
                db: Session = SessionLocal()

                try:
                    benches: List[TestBench] = db.query(TestBench).all()

                    updates = []
                    for bench in benches:
                        new_status, changed, reason = self.check_device_status(bench)

                        if changed:
                            bench.status = new_status
                            bench.updated_at = datetime.utcnow()
                            updates.append(
                                {
                                    "id": bench.id,
                                    "status": new_status.value,
                                    "reason": reason,
                                }
                            )

                            status_str = (
                                "在线" if new_status != BenchStatus.OFFLINE else "离线"
                            )
                            print(
                                f"[UPDATE] {bench.name} ({bench.ip_address}): {status_str} ({reason})"
                            )

                    if updates:
                        db.commit()
                        print(f"[INFO] Updated {len(updates)} device(s)")

                        if self._ws_manager:
                            await self._ws_manager.broadcast(
                                {"event": "device_status_update", "data": updates}
                            )

                except Exception as e:
                    print(f"[ERROR] Monitor error: {e}")
                    db.rollback()
                finally:
                    db.close()

            except Exception as e:
                print(f"[ERROR] Monitor loop error: {e}")

            await asyncio.sleep(self.check_interval)

    def start(self):
        """启动监控"""
        if not self.is_running:
            self.is_running = True
            print("[INFO] Starting device monitor...")

    def stop(self):
        """停止监控"""
        self.is_running = False
        print("[INFO] Device monitor stopped")


device_monitor = DeviceMonitor()
