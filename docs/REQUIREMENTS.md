# 智能测试台架工厂数字孪生看板 - 需求规格说明

**项目代号**: TestBench Dashboard  
**版本**: v1.0.0  
**日期**: 2026-03-11  
**作者**: OpenClaw Agent

---

## 1. 项目概述

### 1.1 项目背景
新能源汽车行业测试台架数量众多，类型各异，管理复杂。需要一套数字孪生看板系统，实现测试台架的实时监控、智能告警、维护管理和数据分析。

### 1.2 项目目标
- 提供测试台架实时状态可视化
- 支持台架布局的灵活配置
- 实现智能告警和维护管理
- 支持多实验室场景切换
- Windows 直接部署，无需 Docker/Linux

### 1.3 目标用户
- 测试工程师
- 实验室管理员
- 维护工程师
- 项目经理

---

## 2. 功能需求

### 2.1 台架类型定义

| 台架类型 | 编码 | 说明 | 图标建议 |
|---------|------|------|---------|
| HIL测试台架 | `hil` | 硬件在环测试 | 🖥️ |
| 系统测试台架 | `system` | 系统级测试 | 🔧 |
| 总成测试台架 | `assembly` | 动力总成/底盘总成测试 | ⚙️ |
| 硬件测试台架 | `hardware` | 电子硬件测试 | 🔌 |
| 软件长稳测试台架 | `software` | 软件长期稳定性测试 | 💻 |
| 其他测试台架 | `other` | 其他类型测试 | 📦 |

### 2.2 设备状态定义

| 状态 | 编码 | 颜色 | 说明 |
|------|------|------|------|
| 运行中 | `running` | 🟢 绿色 `#22c55e` | 台架正在执行测试任务 |
| 离线 | `offline` | ⚪ 灰色 `#6b7280` | 台架网络断开或关机 |
| 维护 | `maintenance` | 🟡 黄色 `#f59e0b` | 台架处于维护状态，不可下发任务 |
| 告警 | `alarm` | 🔴 红色 `#ef4444` | 台架出现异常（超温、超转速等） |
| 空闲 | `idle` | 🔵 蓝色 `#3b82f6` | 台架在线但无任务 |

### 2.3 编辑态功能

#### 2.3.1 台架管理
- **新增台架**: 选择类型、输入名称、设置IP、初始位置
- **删除台架**: 确认后删除，同时清理相关数据
- **编辑台架**: 修改名称、类型、IP、端口等属性
- **批量导入**: 支持 Excel/CSV 批量导入台架

#### 2.3.2 布局管理
- **拖拽布局**: 鼠标拖动台架到目标位置
- **坐标编辑**: 手动输入精确坐标 (X, Y)
- **网格吸附**: 可选的网格对齐功能
- **缩放平移**: 支持画布缩放和平移
- **布局保存**: 自动保存布局到数据库

#### 2.3.3 实验室管理
- **新增实验室**: 设置名称、背景图
- **切换实验室**: 下拉选择切换
- **背景图设置**: 上传自定义背景图（PNG/JPG）
- **实验室删除**: 确认后删除（台架需先迁移）

### 2.4 看板态功能

#### 2.4.1 台架展示信息
```
┌─────────────────────────────────┐
│  🖥️ HIL-001                     │
│  ─────────────────────────────  │
│  状态: 🟢 运行中                 │
│  任务: BMS充电测试-循环#123      │
│  IP: 192.168.1.101              │
│  心跳: 2026-03-11 11:00:00      │
└─────────────────────────────────┘
```

#### 2.4.2 实时状态监控
- **心跳检测**: 定时（5秒）检测台架在线状态
- **状态推送**: WebSocket 实时推送状态变化
- **超时判定**: 超过30秒无心跳判定为离线

#### 2.4.3 告警管理
- **告警类型**:
  - 超温告警（温度 > 阈值）
  - 超转速告警（转速 > 阈值）
  - 超压告警（电压 > 阈值）
  - 通信异常（心跳超时）
  - 自定义告警
- **告警展示**: 台架标红 + 告警列表
- **告警确认**: 确认后清除红色标记
- **告警历史**: 记录所有告警事件

#### 2.4.4 维护模式
- **进入维护**: 点击台架 → 设置维护 → 输入原因/操作人
- **维护中状态**: 台架变黄，不可下发任务
- **退出维护**: 维护完成 → 恢复上线
- **维护记录**: 记录维护历史

### 2.5 总看板功能

#### 2.5.1 统计面板
```
┌─────────────────────────────────────────────┐
│  📊 实时统计                    2026-03-11  │
├─────────────────────────────────────────────┤
│  在线率: 87.5% (14/16)                      │
│  ────────────────────────────────────────  │
│  🟢 运行中: 10    ⚪ 离线: 2                │
│  🟡 维护中: 3     🔴 告警: 1                │
│  🔵 空闲: 0                                   │
└─────────────────────────────────────────────┘
```

#### 2.5.2 实验室切换
- 下拉选择实验室
- 快速切换按钮

#### 2.5.3 时间显示
- 当前时间（实时更新）
- 运行时长统计

### 2.6 数据采集接口

#### 2.6.1 心跳接口
```
POST /api/v1/benches/{bench_id}/heartbeat
Request:
{
  "timestamp": "2026-03-11T11:00:00Z",
  "status": "running",
  "current_task": "BMS充电测试-循环#123",
  "metrics": {
    "temperature": 45.2,
    "rpm": 3000,
    "voltage": 400.5
  }
}
```

#### 2.6.2 告警接口
```
POST /api/v1/benches/{bench_id}/alarms
Request:
{
  "type": "over_temperature",
  "severity": "high",
  "message": "温度超过阈值: 85°C > 80°C",
  "value": 85.0,
  "threshold": 80.0
}
```

---

## 3. 非功能需求

### 3.1 性能要求
- 页面加载时间 < 3秒
- 状态更新延迟 < 1秒
- 支持 100+ 台架同时监控
- WebSocket 连接稳定

### 3.2 部署要求
- Windows 10/11 直接部署
- 无需 Docker
- 无需 Linux 环境
- SQLite 数据库（无需安装）
- Python 3.10+
- Node.js 18+

### 3.3 安全要求
- 管理员密码保护
- API 访问控制
- 操作日志记录

### 3.4 可用性要求
- 界面简洁直观
- 支持中英文
- 响应式设计（支持大屏）
- 键盘快捷键支持

---

## 4. 数据模型

### 4.1 实验室 (Laboratory)
```python
class Laboratory:
    id: UUID
    name: str                    # 实验室名称
    background_image: str        # 背景图URL
    width: int                   # 画布宽度
    height: int                  # 画布高度
    created_at: datetime
    updated_at: datetime
```

### 4.2 测试台架 (TestBench)
```python
class TestBench:
    id: UUID
    laboratory_id: UUID          # 所属实验室
    name: str                    # 台架名称
    type: BenchType              # 台架类型
    ip_address: str              # IP地址
    port: int                    # 端口号
    
    # 位置信息
    position_x: float
    position_y: float
    rotation: int                # 旋转角度
    
    # 状态信息
    status: BenchStatus          # 当前状态
    last_heartbeat: datetime     # 最后心跳时间
    current_task: str            # 当前任务
    task_start_time: datetime    # 任务开始时间
    
    # 维护信息
    is_under_maintenance: bool
    maintenance_reason: str
    maintenance_start_time: datetime
    maintenance_operator: str
    
    # 告警信息
    has_alarm: bool
    alarm_message: str
    
    created_at: datetime
    updated_at: datetime
```

### 4.3 告警记录 (Alarm)
```python
class Alarm:
    id: UUID
    bench_id: UUID               # 关联台架
    type: str                    # 告警类型
    severity: str                # 严重程度
    message: str                 # 告警消息
    value: float                 # 触发值
    threshold: float             # 阈值
    acknowledged: bool           # 是否已确认
    acknowledged_by: str         # 确认人
    acknowledged_at: datetime    # 确认时间
    created_at: datetime
```

### 4.4 维护记录 (MaintenanceRecord)
```python
class MaintenanceRecord:
    id: UUID
    bench_id: UUID
    reason: str                  # 维护原因
    operator: str                # 维护人员
    notes: str                   # 备注
    start_time: datetime         # 开始时间
    end_time: datetime           # 结束时间
    created_at: datetime
```

---

## 5. API 设计

### 5.1 实验室管理
- `GET /api/v1/laboratories` - 获取实验室列表
- `POST /api/v1/laboratories` - 创建实验室
- `PUT /api/v1/laboratories/{id}` - 更新实验室
- `DELETE /api/v1/laboratories/{id}` - 删除实验室

### 5.2 台架管理
- `GET /api/v1/benches` - 获取台架列表
- `GET /api/v1/benches/{id}` - 获取台架详情
- `POST /api/v1/benches` - 创建台架
- `PUT /api/v1/benches/{id}` - 更新台架
- `DELETE /api/v1/benches/{id}` - 删除台架
- `PUT /api/v1/benches/{id}/position` - 更新位置

### 5.3 状态与心跳
- `POST /api/v1/benches/{id}/heartbeat` - 提交心跳
- `PUT /api/v1/benches/{id}/status` - 更新状态
- `PUT /api/v1/benches/{id}/maintenance` - 设置维护状态

### 5.4 告警管理
- `GET /api/v1/alarms` - 获取告警列表
- `POST /api/v1/alarms` - 创建告警
- `PUT /api/v1/alarms/{id}/acknowledge` - 确认告警

### 5.5 统计数据
- `GET /api/v1/statistics/overview` - 获取总览统计
- `GET /api/v1/statistics/laboratory/{id}` - 获取实验室统计

### 5.6 WebSocket
- `WS /ws` - WebSocket 连接
- 推送事件: `bench_status_update`, `alarm`, `statistics_update`

---

## 6. 技术选型

### 6.1 后端
- **框架**: FastAPI
- **数据库**: SQLite（Windows友好）
- **ORM**: SQLAlchemy
- **WebSocket**: 内置 WebSocket 支持
- **异步**: asyncio

### 6.2 前端
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **组件**: shadcn/ui
- **状态**: Zustand
- **拖拽**: @dnd-kit/core
- **HTTP**: Axios

---

## 7. 项目里程碑

### Phase 1: 基础框架 (Day 1)
- [x] 项目初始化
- [ ] 后端基础架构
- [ ] 前端基础架构
- [ ] 数据库模型

### Phase 2: 核心功能 (Day 2)
- [ ] 台架 CRUD
- [ ] 实验室管理
- [ ] 布局拖拽
- [ ] 状态展示

### Phase 3: 高级功能 (Day 3)
- [ ] 心跳机制
- [ ] 告警系统
- [ ] 维护模式
- [ ] 统计面板

### Phase 4: 优化完善 (Day 4)
- [ ] 性能优化
- [ ] UI 美化
- [ ] 测试用例
- [ ] 文档完善

---

## 8. 验收标准

### 8.1 功能验收
- ✅ 所有台架类型可正常添加
- ✅ 拖拽布局流畅
- ✅ 状态实时更新
- ✅ 告警正确触发和显示
- ✅ 维护模式正常工作
- ✅ 多实验室切换正常

### 8.2 性能验收
- ✅ 100 台架同时监控无卡顿
- ✅ 状态更新延迟 < 1秒
- ✅ 页面加载 < 3秒

### 8.3 部署验收
- ✅ Windows 直接运行
- ✅ 一键启动脚本
- ✅ 无需额外依赖

---

**文档版本**: v1.0  
**最后更新**: 2026-03-11
