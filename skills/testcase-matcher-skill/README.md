# 测试用例匹配器 (testcase-matcher-skill)

智能匹配客户测试用例与内部测试用例，支持多对多映射，大幅减少人工比对工作量。

## 功能特点

- **智能识别**：自动识别客户用例文件中的子表结构和列名
- **语义匹配**：基于语义相似度进行匹配，而非简单关键词
- **多对多映射**：支持一个客户用例对应多个内部用例，反之亦然
- **置信度分级**：高/中/低三级置信度，便于人工复核
- **多格式输出**：支持 Excel 和 Markdown 两种报告格式

## 安装

### Claude Code

```bash
git clone <repo-url> ~/.claude/skills/testcase-matcher-skill
```

### Cursor

```bash
git clone <repo-url> .cursor/rules/testcase-matcher-skill
```

### VS Code Copilot

```bash
git clone <repo-url> .github/skills/testcase-matcher-skill
```

### Universal (Codex CLI, Gemini CLI, etc.)

```bash
git clone <repo-url> ~/.agents/skills/testcase-matcher-skill
```

## 使用方法

在对话中输入：

```
/testcase-matcher-skill 客户用例.xlsx 内部用例.xlsx
```

或自然语言：

```
匹配这两个测试用例文件
对比客户用例和内部用例
```

## 文件要求

### 客户用例文件
- 格式：.xlsx 或 .xls
- 结构：自动识别子表和列名
- 支持多种列名格式（详见 references/matching-guide.md）

### 内部用例文件
- 格式：.xlsx 或 .xls
- 必需字段：用例_名称、用例_测试步骤
- 可选字段：用例_预置条件、用例_预期结果

## 输出示例

### Markdown 报告

```markdown
# 测试用例匹配报告

## 统计信息
| 指标 | 数值 |
|-----|------|
| 客户用例总数 | 50 |
| 内部用例总数 | 120 |
| 客户用例匹配率 | 90% |
| 高置信度匹配数 | 30 |

## 匹配汇总
| 客户用例 | 内部用例 | 置信度 | 匹配理由 |
|---------|---------|-------|---------|
| 登录功能测试 | TC_LOGIN_001 | 高 | 测试步骤高度相似 |
```

## 依赖

- Python 3.8+
- pandas
- openpyxl

安装依赖：

```bash
pip install pandas openpyxl
```

## 许可证

MIT License
