# ⚡ 快速开始指南

## 🎯 问题已解决

### ✅ 问题1：局域网其他用户无法访问网页
**已修复：** 前端 API 地址已更新为服务器局域网 IP `192.168.1.100`

### ✅ 问题2：设备显示离线
**已修复：** 添加了自动 ping 检测功能，可 ping 通的设备自动显示为在线

---

## 🚀 启动方式（二选一）

### 方式1：一键启动（推荐）

直接双击运行：
```
start_production.bat
```

这将自动启动：
- 后端服务（端口 8000）
- 前端服务（端口 3000）

### 方式2：手动启动

**步骤1：启动后端**
```bash
cd backend
start.bat
```

**步骤2：启动前端**
```bash
cd frontend
# 选项A - 开发模式
npm run dev -- -H 0.0.0.0

# 选项B - 生产模式
npm install -g serve
serve -s out -l 3000
```

---

## 📱 访问地址

### 局域网访问（其他设备）
- **前端看板：** http://192.168.1.100:3000
- **后端 API：** http://192.168.1.100:8000
- **API 文档：** http://192.168.1.100:8000/docs

### 本机访问
- **前端看板：** http://localhost:3000
- **后端 API：** http://localhost:8000
- **API 文档：** http://localhost:8000/docs

---

## 🔍 验证功能

### 1. 检查后端监控
查看后端控制台输出，应该看到：
```
[OK] Database initialized
[OK] Device monitor started
[INFO] Device monitor started
```

### 2. 检查设备状态
几秒钟后，应该看到设备状态更新：
```
[UPDATE] 设备名称 (192.168.1.XXX): 在线
[INFO] Updated 1 device(s)
```

### 3. 访问前端
在局域网其他设备浏览器中访问：`http://192.168.1.100:3000`

---

## ⚙️ 自定义配置

### 修改服务器 IP
如果服务器 IP 变化：

1. 编辑 `frontend/.env.local`：
   ```
   NEXT_PUBLIC_API_URL=http://新IP地址:8000/api/v1
   ```

2. 重新构建前端：
   ```bash
   cd frontend
   npm run build
   ```

### 修改监控间隔
编辑 `backend/app/core/device_monitor.py`：
```python
self.check_interval = 30  # 改为你需要的秒数
```

---

## 🛠️ 故障排查

### 问题：前端无法访问
**检查防火墙：**
```bash
# Windows 防火墙开放端口
netsh advfirewall firewall add rule name="TestBench API" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="TestBench Frontend" dir=in action=allow protocol=TCP localport=3000
```

### 问题：设备仍显示离线
**手动测试：**
```bash
# 在服务器上 ping 设备
ping 192.168.1.XXX
```

如果无法 ping 通，检查：
- 设备 IP 是否正确
- 设备防火墙是否允许 ICMP
- 网络是否连通

---

## 📚 详细文档

- **部署指南：** `DEPLOYMENT_GUIDE.md`
- **变更记录：** `CONFIG_CHANGELOG.md`

---

**最后更新：** 2026-03-12
