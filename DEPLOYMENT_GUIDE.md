# 部署指南 - 局域网访问配置

## 📋 问题修复

### ✅ 问题1：局域网无法访问网页
**原因：** 前端配置的 API 地址是 `http://localhost:8000`，局域网其他用户访问时浏览器会尝试连接他们本地的 localhost。

**解决方案：** 已将 API 地址改为服务器的局域网 IP `http://192.168.1.100:8000`

### ✅ 问题2：设备显示离线
**原因：** 系统依赖设备主动发送心跳，没有主动检测机制。

**解决方案：** 已添加后台监控服务，定期 ping 所有设备，自动判断在线状态。

---

## 🚀 部署步骤

### 1. 后端服务（已修改）

后端已添加设备监控功能，会每 30 秒自动检测所有设备状态。

**启动后端：**
```bash
cd backend
start.bat
```

后端将运行在：`http://192.168.1.100:8000`

**特性：**
- ✅ 自动 ping 检测设备在线状态
- ✅ 维护中的设备不会改变状态
- ✅ 有告警的设备不会改变状态
- ✅ 可 ping 通的设备自动设为在线（IDLE）
- ✅ 不可 ping 通的设备自动设为离线（OFFLINE）

---

### 2. 前端服务（需要重新构建）

#### 方案A：开发模式（推荐测试）

**优点：** 简单快速，支持热重载
**缺点：** 性能较低，不适合生产环境

```bash
cd frontend
npm run dev -- -H 0.0.0.0
```

前端将运行在：`http://192.168.1.100:3000`

#### 方案B：生产模式（推荐部署）

**步骤1：构建静态文件**
```bash
cd frontend
npm run build
```

**步骤2：使用静态服务器提供服务**

选项1 - 使用 serve（推荐）：
```bash
npm install -g serve
serve -s out -l 3000
```

选项2 - 使用 Python：
```bash
cd out
python -m http.server 3000 --bind 0.0.0.0
```

选项3 - 使用 Nginx（Windows 版本）：
将 `out` 目录内容复制到 Nginx 的 `html` 目录

前端将运行在：`http://192.168.1.100:3000`

---

## 📝 配置文件

### 后端配置
- **文件：** `backend/app/main.py`
- **监控间隔：** 30 秒（可在 `device_monitor.py` 中修改 `check_interval`）
- **绑定地址：** `0.0.0.0:8000`（允许局域网访问）

### 前端配置
- **文件：** `frontend/.env.local`
- **API 地址：** `http://192.168.1.100:8000/api/v1`

---

## 🔧 自定义配置

### 修改服务器 IP 地址

如果服务器 IP 变化，需要修改以下文件：

**1. 前端配置**
```bash
# 编辑 frontend/.env.local
NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:8000/api/v1
```

**2. 重新构建前端**
```bash
cd frontend
npm run build
```

### 修改监控参数

**编辑 `backend/app/core/device_monitor.py`：**

```python
class DeviceMonitor:
    def __init__(self):
        self.is_running = False
        self.check_interval = 30  # 检测间隔（秒）
        self.offline_threshold = 90  # 离线阈值（秒）
```

---

## ✅ 验证部署

### 1. 检查后端
```bash
# 在服务器上访问
curl http://localhost:8000/health

# 在其他设备上访问
curl http://192.168.1.100:8000/health
```

预期响应：`{"status": "healthy"}`

### 2. 检查前端
在局域网其他设备上访问：`http://192.168.1.100:3000`

### 3. 检查设备监控
查看后端控制台输出，应该看到：
```
[INFO] Device monitor started
[UPDATE] DeviceName (192.168.1.XXX): 在线/离线
[INFO] Updated N device(s)
```

---

## 🐛 故障排查

### 问题：前端无法连接后端
**检查：**
1. 后端是否正常运行在 8000 端口
2. 防火墙是否允许 8000 端口访问
3. `.env.local` 中的 IP 地址是否正确

**解决：**
```bash
# Windows 防火墙开放端口
netsh advfirewall firewall add rule name="TestBench API" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="TestBench Frontend" dir=in action=allow protocol=TCP localport=3000
```

### 问题：设备仍显示离线
**检查：**
1. 设备 IP 地址是否正确
2. 设备是否允许 ping（ICMP 协议）
3. 网络是否连通

**测试：**
```bash
# 在服务器上手动 ping 设备
ping 192.168.1.XXX
```

---

## 📊 性能优化建议

1. **使用生产模式部署前端**（静态文件 + Nginx/serve）
2. **调整监控间隔**（根据实际需求，默认 30 秒）
3. **使用 PM2 管理后端进程**（自动重启、日志管理）
4. **配置 Nginx 反向代理**（统一入口、SSL 支持）

---

## 📞 技术支持

如有问题，请检查：
1. 后端日志：查看控制台输出
2. 前端日志：浏览器开发者工具 Console 和 Network 面板
3. 网络连通性：ping 测试、端口测试

---

**最后更新：** 2026-03-12
**版本：** 1.0.0
