# GitHub 上传步骤

## 方法一：手动创建仓库

### 1. 在 GitHub 上创建仓库
1. 访问 https://github.com/new
2. 仓库名称: `test-bench-dashboard`
3. 描述: `智能测试台架工厂数字孪生看板`
4. 选择 **Public**
5. **不要**勾选 "Add a README file"
6. 点击 **Create repository**

### 2. 推送代码
创建仓库后，在本地执行：

```bash
cd test_bench_dashboard
git remote add origin git@github.com:zhang57zhang/test-bench-dashboard.git
git push -u origin master
```

---

## 方法二：使用 GitHub CLI (gh)

如果你安装了 GitHub CLI：

```bash
cd test_bench_dashboard
gh repo create test-bench-dashboard --public --source=. --push --description "智能测试台架工厂数字孪生看板"
```

---

## 当前状态

✅ 代码已提交到本地 Git 仓库
✅ 共 44 个文件，11671 行代码
⏳ 等待推送到 GitHub

### 提交信息
```
feat: 智能测试台架工厂数字孪生看板 v1.0.0

功能特性:
- 6种台架类型支持: HIL/系统/总成/硬件/软件/其他
- 5种状态监控: 运行中/离线/维护/告警/空闲
- 拖拽式布局设计
- 实时状态监控(心跳机制)
- 智能告警系统
- 维护模式管理
- 多实验室支持
- Windows一键部署

技术栈:
- 后端: FastAPI + SQLite + SQLAlchemy
- 前端: Next.js 14 + TypeScript + Tailwind CSS + Zustand
```
