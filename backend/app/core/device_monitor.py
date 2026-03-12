"""
Device Monitor Service
设备监控服务 - 定期检测设备在线状态
"""

import asyncio
import platform
import subprocess
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.bench import TestBench, BenchStatus


class DeviceMonitor:
    """设备监控器"""
    
    def __init__(self):
        self.is_running = False
        self.check_interval = 300  # 检测间隔（秒）- 5分钟
        self.offline_threshold = 90  # 离线阈值（秒）
    
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
            # 根据操作系统选择 ping 命令参数
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            
            # 执行 ping 命令
            command = ['ping', param, '1', '-w', str(timeout * 1000), ip_address]
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout + 1
            )
            
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            print(f"[ERROR] Ping {ip_address} failed: {e}")
            return False
    
    def check_device_status(self, bench: TestBench) -> tuple[BenchStatus, bool]:
        """
        检查设备状态
        
        Args:
            bench: 台架对象
        
        Returns:
            tuple: (新状态, 是否有变化)
        """
        # 如果设备在维护中，不改变状态
        if bench.is_under_maintenance:
            return bench.status, False
        
        # 如果设备有告警，不改变状态
        if bench.has_alarm:
            return bench.status, False
        
        # Ping 设备
        is_online = self.ping_device(bench.ip_address)
        
        # 根据在线状态决定新状态
        if is_online:
            # 设备在线
            if bench.status == BenchStatus.OFFLINE:
                # 从离线变为在线，设置为空闲
                return BenchStatus.IDLE, True
            # 其他状态保持不变
            return bench.status, False
        else:
            # 设备离线
            if bench.status != BenchStatus.OFFLINE:
                # 从在线变为离线
                return BenchStatus.OFFLINE, True
            return bench.status, False
    
    async def monitor_devices(self):
        """监控所有设备"""
        print("[INFO] Device monitor started")
        
        while self.is_running:
            try:
                # 创建数据库会话
                db: Session = SessionLocal()
                
                try:
                    # 获取所有台架
                    benches: List[TestBench] = db.query(TestBench).all()
                    
                    updated_count = 0
                    for bench in benches:
                        new_status, changed = self.check_device_status(bench)
                        
                        if changed:
                            bench.status = new_status
                            bench.updated_at = datetime.utcnow()
                            updated_count += 1
                            
                            status_str = "在线" if new_status != BenchStatus.OFFLINE else "离线"
                            print(f"[UPDATE] {bench.name} ({bench.ip_address}): {status_str}")
                    
                    if updated_count > 0:
                        db.commit()
                        print(f"[INFO] Updated {updated_count} device(s)")
                    
                except Exception as e:
                    print(f"[ERROR] Monitor error: {e}")
                    db.rollback()
                finally:
                    db.close()
                
            except Exception as e:
                print(f"[ERROR] Monitor loop error: {e}")
            
            # 等待下一次检测
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


# 全局监控器实例
device_monitor = DeviceMonitor()
