# 配置变更日志

## 2026-03-12 - 局域网访问修复 & 设备监控增强

### 🔧 修改的文件

#### 1. `frontend/.env.local`
**变更前：**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**变更后：**
```
# 使用服务器局域网 IP，允许其他设备访问
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1
```

**原因：** 允许局域网内其他设备访问前端时，能正确连接到后端 API

---

#### 2. `backend/app/main.py` (新增功能)
**新增：** 设备监控服务启动

```python
from app.core.device_monitor import device_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动设备监控
    device_monitor.start()
    monitor_task = asyncio.create_task(device_monitor.monitor_devices())
    
    yield
    
    # 关闭时停止监控
    device_monitor.stop()
    monitor_task.cancel()
```

**功能：** 后端启动时自动运行设备监控服务

---

#### 3. `backend/app/core/device_monitor.py` (新增文件)
**功能：** 设备在线状态自动检测

**核心特性：**
- 每 30 秒自动 ping 所有设备
- 可 ping 通的设备自动设为在线（IDLE）
- 不可 ping 通的设备自动设为离线（OFFLINE）
- 维护中的设备状态不受影响
- 有告警的设备状态不受影响

**配置参数：**
```python
check_interval = 30  # 检测间隔（秒）
offline_threshold = 90  # 离线阈值（秒）
```

---

#### 4. `frontend/out/` (重新构建)
**操作：** 运行 `npm run build` 重新生成静态文件

**原因：** 使新的 API 地址配置生效

---

### 📝 新增文件

1. **`DEPLOYMENT_GUIDE.md`** - 完整的部署指南
2. **`start_production.bat`** - 一键启动生产环境脚本
3. **`CONFIG_CHANGELOG.md`** - 本文件（配置变更记录）

---

### 🎯 部署要求

#### 必需操作：
1. ✅ 重启后端服务（使监控功能生效）
2. ✅ 使用新的前端静态文件（已在 `frontend/out/` 目录）

#### 可选操作：
1. 配置防火墙开放 8000 和 3000 端口
2. 使用 Nginx 或其他 Web 服务器提供前端服务
3. 使用 PM2 管理后端进程

---

### ✅ 测试验证

#### 1. 后端健康检查
```bash
curl http://192.168.1.100:8000/health
# 预期响应: {"status": "healthy"}
```

#### 2. 设备监控日志
查看后端控制台，应该看到：
```
[INFO] Device monitor started
[UPDATE] DeviceName (192.168.1.XXX): 在线
[INFO] Updated 1 device(s)
```

#### 3. 前端访问
在局域网其他设备上访问：
```
http://192.168.1.100:3000
```

---

### 🔄 回滚方案

如需回滚到之前版本：

1. **回滚前端配置：**
   ```bash
   # 编辑 frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   
   # 重新构建
   cd frontend
   npm run build
   ```

2. **禁用设备监控：**
   编辑 `backend/app/main.py`，注释掉设备监控相关代码

---

**维护人员：** OpenClaw AI Assistant  
**更新日期：** 2026-03-12
