# 🐛 错误修复指南

## 报错：cannot find model './vendor-chunks/axios.js'

### 问题描述
构建时出现模块找不到错误，通常是缓存问题导致。

---

## ✅ 解决方案

### 方案1：一键清理和重新构建（推荐）

**Windows:**
```bash
双击运行：clean_and_rebuild.bat
```

这将自动执行：
1. 清理前端缓存
2. 清理后端缓存
3. 重新安装依赖
4. 重新构建前端
5. 验证构建结果

---

### 方案2：手动清理

#### 步骤1：清理前端缓存
```bash
cd frontend
Remove-Item -Path .next,out,node_modules/.cache -Recurse -Force -ErrorAction SilentlyContinue
```

#### 步骤2：重新安装依赖
```bash
npm install
```

#### 步骤3：重新构建
```bash
npm run build
```

---

### 方案3：完全重置

**如果上述方案无效：**

#### 步骤1：删除node_modules
```bash
cd frontend
Remove-Item -Path node_modules -Recurse -Force
```

#### 步骤2：删除package-lock.json
```bash
Remove-Item package-lock.json -Force
```

#### 步骤3：重新安装
```bash
npm install
```

#### 步骤4：重新构建
```bash
npm run build
```

---

## 🔍 常见错误和解决方案

### 错误1：Module not found

**原因：** 缓存问题或依赖未正确安装

**解决：**
```bash
# 清理缓存
npm cache clean --force

# 重新安装
npm install
```

---

### 错误2：Cannot find module './vendor-chunks/*'

**原因：** Next.js构建缓存问题

**解决：**
```bash
# 清理.next目录
Remove-Item -Path .next -Recurse -Force

# 重新构建
npm run build
```

---

### 错误3：TypeScript类型错误

**原因：** 类型定义缺失

**解决：**
```bash
# 安装缺失的类型定义
npm install --save-dev @types/node @types/react @types/react-dom

# 重新构建
npm run build
```

---

### 错误4：Out of memory

**原因：** Node.js内存不足

**解决：**
```bash
# 增加内存限制
set NODE_OPTIONS=--max-old-space-size=4096
npm run build
```

---

## 🛠️ 预防措施

### 1. 定期清理缓存

创建定期清理脚本：
```bash
# 每周运行一次
clean_and_rebuild.bat
```

### 2. 使用正确的Node版本

**推荐版本：** Node.js 18.x 或更高

```bash
# 检查版本
node --version

# 如果版本过低，使用nvm切换
nvm install 18
nvm use 18
```

### 3. 保持依赖更新

```bash
# 检查过时的包
npm outdated

# 更新所有包
npm update
```

---

## 📊 验证构建成功

### 检查输出目录

```bash
# 检查out目录是否存在
Test-Path frontend\out\index.html

# 检查文件数量
(Get-ChildItem frontend\out -Recurse -File).Count
```

### 验证构建产物

应该包含：
- ✅ `out/index.html` - 主页面
- ✅ `out/_next/` - Next.js资源
- ✅ `out/404.html` - 404页面

---

## 🚀 构建后启动

### 开发模式
```bash
cd frontend
npm run dev
```

### 生产模式
```bash
cd frontend
npm install -g serve
serve -s out -l 3000
```

---

## 📝 构建日志分析

### 成功标志
```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages
✓ Finalizing page optimization
```

### 失败标志
```
✖ Compiled with errors
Module not found
Type error
```

---

## 🔄 完整重置流程

如果所有方法都无效，执行完整重置：

```bash
# 1. 停止所有服务
# 按 Ctrl+C 停止运行的服务

# 2. 清理所有缓存
cd frontend
Remove-Item -Path .next,out,node_modules,package-lock.json -Recurse -Force -ErrorAction SilentlyContinue

# 3. 清理npm缓存
npm cache clean --force

# 4. 重新安装
npm install

# 5. 重新构建
npm run build

# 6. 验证
Test-Path out\index.html
```

---

## 📞 获取帮助

如果问题仍然存在：

1. **检查错误日志**
   - 查看完整错误信息
   - 记录错误代码和描述

2. **检查环境**
   ```bash
   node --version
   npm --version
   ```

3. **检查依赖**
   ```bash
   npm list
   ```

4. **提交Issue**
   - 包含完整错误日志
   - 包含环境信息
   - 包含复现步骤

---

## ✅ 当前状态

**最后构建时间：** 2026-03-13
**构建状态：** ✅ 成功
**输出目录：** frontend\out
**文件数量：** 正常

**如果有任何问题，请运行：**
```bash
clean_and_rebuild.bat
```

---

**维护团队：** OpenClaw AI Assistant  
**最后更新：** 2026-03-13
