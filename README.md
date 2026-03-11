# 智能测试台架工厂数字孪生看板

**Test Bench Factory Digital Twin Dashboard**

一个专为新能源汽车测试台架设计的数字孪生看板系统，支持实时监控、智能告警、维护管理和可视化布局。

---

## 🎯 功能特性

### 台架类型支持
- 🖥️ HIL测试台架
- 🔧 系统测试台架
- ⚙️ 总成测试台架
- 🔌 硬件测试台架
- 💻 软件长稳测试台架
- 📦 其他测试台架

### 状态监控
- 🟢 运行中 - 台架正在执行测试任务
- ⚪ 离线 - 台架网络断开或关机
- 🟡 维护中 - 台架处于维护状态
- 🔴 告警 - 台架出现异常
- 🔵 空闲 - 台架在线但无任务

### 核心功能
- ✅ 拖拽式布局设计
- ✅ 实时状态监控（心跳机制）
- ✅ 智能告警系统
- ✅ 维护模式管理
- ✅ 多实验室支持
- ✅ 统计面板

---

## 🚀 快速开始

### 环境要求
- **Windows 10/11**
- **Python 3.10+**
- **Node.js 18+**

### 一键启动

```bash
# 双击运行
start.bat
```

或手动启动：

#### 1. 启动后端

```bash
cd backend
start.bat
```

#### 2. 启动前端

```bash
cd frontend
start.bat
```

### 访问地址
- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 📖 使用指南

### 编辑模式
1. 点击右上角「编辑模式」按钮
2. 从左侧台架库拖拽台架到画布
3. 双击台架可编辑属性
4. 右键台架可删除
5. 拖动台架调整位置

### 看板模式
1. 查看台架实时状态
2. 点击台架查看详情
3. 查看告警信息
4. 切换实验室

### 维护管理
1. 在编辑模式下点击台架菜单
2. 选择「设为维护」
3. 输入维护原因和人员
4. 维护完成后点击「退出维护」

---

## 🏗️ 项目结构

```
test_bench_dashboard/
├── backend/                # 后端服务
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # 数据验证
│   │   └── core/          # 核心配置
│   ├── data/              # SQLite 数据库
│   ├── requirements.txt
│   └── start.bat
├── frontend/              # 前端服务
│   ├── src/
│   │   ├── app/          # 页面
│   │   ├── components/   # 组件
│   │   ├── store/        # 状态管理
│   │   ├── types/        # 类型定义
│   │   └── lib/          # 工具函数
│   ├── package.json
│   └── start.bat
├── docs/                  # 文档
│   └── REQUIREMENTS.md
└── start.bat             # 一键启动
```

---

## 📡 API 接口

### 台架管理
- `GET /api/v1/benches` - 获取台架列表
- `POST /api/v1/benches` - 创建台架
- `PUT /api/v1/benches/{id}` - 更新台架
- `DELETE /api/v1/benches/{id}` - 删除台架
- `PUT /api/v1/benches/{id}/position` - 更新位置
- `POST /api/v1/benches/{id}/heartbeat` - 提交心跳
- `PUT /api/v1/benches/{id}/maintenance` - 设置维护

### 实验室管理
- `GET /api/v1/laboratories` - 获取实验室列表
- `POST /api/v1/laboratories` - 创建实验室
- `PUT /api/v1/laboratories/{id}` - 更新实验室
- `DELETE /api/v1/laboratories/{id}` - 删除实验室

### 告警管理
- `GET /api/v1/alarms` - 获取告警列表
- `POST /api/v1/alarms` - 创建告警
- `PUT /api/v1/alarms/{id}/acknowledge` - 确认告警

### 统计数据
- `GET /api/v1/statistics/overview` - 获取总览统计
- `GET /api/v1/statistics/laboratory/{id}` - 获取实验室统计

---

## 🔧 技术栈

### 后端
- FastAPI - 高性能 Python Web 框架
- SQLite - 轻量级数据库（无需安装）
- SQLAlchemy - ORM
- WebSocket - 实时通信

### 前端
- Next.js 14 - React 框架
- TypeScript - 类型安全
- Tailwind CSS - 样式
- Zustand - 状态管理
- @dnd-kit - 拖拽功能

---

## 📊 数据模型

### TestBench（测试台架）
```typescript
{
  id: string;
  name: string;
  type: BenchType;
  ipAddress: string;
  port: number;
  position: { x: number; y: number };
  status: BenchStatus;
  currentTask: string | null;
  isUnderMaintenance: boolean;
  hasAlarm: boolean;
}
```

### Laboratory（实验室）
```typescript
{
  id: string;
  name: string;
  backgroundImage: string | null;
  canvasSize: { width: number; height: number };
}
```

---

## 📝 开发日志

### v1.0.0 (2026-03-11)
- ✅ 完成基础架构
- ✅ 实现台架 CRUD
- ✅ 实现拖拽布局
- ✅ 实现状态监控
- ✅ 实现告警系统
- ✅ 实现维护管理
- ✅ Windows 一键部署

---

## 📄 许可证

MIT License

---

**构建时间**: 2026-03-11  
**当前版本**: v1.0.0
