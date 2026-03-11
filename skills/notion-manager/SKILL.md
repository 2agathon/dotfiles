---
name: notion-manager
description: >
  查询 Notion 工作区结构、容器边界词表、追溯认识版本链、归类内容时使用。
  用户说"看看我的工作区"、"这个放哪里"、"这条认识从哪来"、
  "有哪些容器"、"帮我记一下"时触发。
---

## 这个 skill 做什么

理解用户的认识地图，帮用户在知识库里导航、归类、追溯。
写入是偶发的辅助动作，查询和推理是主路径。

---

## Token 获取（必须在任何操作前完成）

**执行任何操作前，先确认 token 可用。按以下顺序检查：**

### 1. 环境变量（优先）

```bash
echo $NOTION_TOKEN        # Linux / macOS
echo $env:NOTION_TOKEN    # Windows PowerShell
```

变量名：**`NOTION_TOKEN`**

脚本自动读取：
```bash
python scripts/notion_ops.py snapshot  # 不需要 --token，自动从环境变量读
```

### 2. 对话中提供

用户在对话里直接提供 token，AI 在当次对话中使用，用完即走，不存储。

### 3. 都没有时

**停下来，不往下走。** 告知用户：

> "需要 Notion Integration Token 才能继续。有两种方式提供：
>
> **方式一（推荐）：设置环境变量，避免每次提供**
> ```bash
> # Linux / macOS（加入 ~/.bashrc 或 ~/.zshrc 永久生效）
> export NOTION_TOKEN=your_token_here
>
> # Windows PowerShell（加入 $PROFILE 永久生效）
> $env:NOTION_TOKEN = 'your_token_here'
> ```
>
> **方式二：直接在对话里提供**
> 把 token 粘贴进来，我用完即走，不会存储。
>
> Token 在 Notion → Settings → Connections → Develop or manage integrations 里创建。
> 创建后需要把目标页面共享给该 Integration（页面右上角 → Connect to → 选择你的 Integration）。"

获取到 token 后再继续，不能假设 token 存在后静默失败。

---

## 意图澄清

收到模糊请求时，先用一句话确认意图，不猜，不展开：

> "你是想——
> 1. 看工作区树结构
> 2. 看容器边界词表
> 3. 归类某个内容（判断放哪里、新建还是迭代）
> 4. 追溯某条认识的版本链
> 5. 写入（创建页面 / 追加内容 / 移动）
> 选哪个？"

用户选完立刻执行，不再确认。

---

## 功能表

| 用户说的 | AI 执行的 |
|----------|-----------|
| 看结构 / 树 / 工作区 | 输出工作区树结构 |
| 边界 / 词表 / 容器有哪些 | 输出所有容器页的不可替代性和边界 |
| 这个放哪里 / 归类 | 对照词表推理归属，判断新建还是迭代 |
| 这条认识从哪来 / 追溯 / 版本 | 沿前驱链往前遍历版本 |
| 帮我记 / 新建 / 创建 / 追加 | 写入操作，执行前确认 |

---

## 主路径：查询与推理

**不需要用户确认，直接执行。**

### 工作区树结构

输出所有页面的层级关系，容器页标注 📌，显示 depth。
默认输出到 depth=3，更深层需用户明确要求。

### 容器边界词表

输出所有含 📌 Callout 的容器页：

```
## [容器名]
不可替代性：[内容]
边界：[内容]
子容器：[如有]
```

### 归类推理

对照词表逐一检查，输出：

```
归属分析：
  ✓ 属于「XX」
    理由：[对应不可替代性]
    不违反边界：[说明]

  ✗ 不属于「YY」
    原因：[触碰边界 / 不可替代性对不上]

判断：[新建内容页 | 迭代已有认识（找到前驱：[页面名]）]
```

**新建还是迭代的判断逻辑：**
- 工作区里已有同一张力的认识 → 迭代，找到前驱页面，不新建
- 没有 → 新建内容页
- 现有容器装不下 → 提议新容器（见写入路径）

### 版本链追溯

给定主题或关键词，沿 Tension Manifest 的前驱字段往前遍历：

```
版本链：[主题]

v3  [页面名]  [外化时间]
    张力：[演化摘要里"现在看见的张力是___"]
    触发：[触发字段]

v2  [页面名]  [外化时间]
    张力：[演化摘要里"现在看见的张力是___"]
    触发：[触发字段]

v1  [页面名]  [外化时间]
    起点张力：[起点张力字段]
```

读不到 Tension Manifest 字段时，标注 `[无 Tension Manifest]`。

---

## 次路径：写入

**执行前必须向用户确认：操作类型 + 目标页面 + 内容摘要。**

### 创建内容页

```bash
python scripts/notion_ops.py create \
  --parent-id "父页面" --title "标题" \
  [--content "..." | --content-file path]
```

### 创建容器页

现有容器装不下时，提议新容器：

```
建议新建容器页：「[名称]」
  父级：[挂在哪个骨架下]
  不可替代性：[没有它会少掉什么]
  边界：[什么内容不该进来]
```

确认后执行：

```bash
python scripts/notion_ops.py create \
  --parent-id "父页面" --title "标题" \
  --container \
  --indispensable "..." \
  --boundary "..."
```

`--container` 自动在页面顶部插入标准 📌 Callout。

### 追加 / 移动

```bash
python scripts/notion_ops.py append \
  --page-id "目标页面" [--content "..." | --content-file path]

python scripts/notion_ops.py move \
  --page-id "源页面" --target-parent-id "目标父页面"
```

长内容（>200字）先写临时文件：

```bash
cat > /tmp/notion_content.md << 'EOF'
内容...
EOF
```

---

## 基础设施：执行方式

按环境自动降级，不需要用户选择：

**有 Python** → 脚本自动读取 `$NOTION_TOKEN`，无需每次传 `--token`

**有 HTTP 工具，无 Python** → 直调 Notion API

```
POST https://api.notion.com/v1/search
GET  https://api.notion.com/v1/blocks/{id}/children
GET  https://api.notion.com/v1/pages/{id}
POST https://api.notion.com/v1/pages
PATCH https://api.notion.com/v1/blocks/{id}/children

Headers:
  Authorization: Bearer {token}
  Notion-Version: 2022-06-28
```

**Claude.ai Web / 网络受限环境** → 只执行归类推理和版本追溯。
用户提供快照 JSON 或页面内容，AI 在本地推理，不发网络请求。
写入操作告知用户需要在本地环境执行。

---

## 快照

快照 = 工作区结构索引，含标题→ID 映射 + 容器页词表。

```bash
python scripts/notion_ops.py snapshot     # 全量爬取
python scripts/notion_ops.py snapshot-info  # 查看状态
python scripts/notion_ops.py wordlist     # 输出词表
```

`create` / `move` 完成后自动增量更新，无需重跑。
用户说"结构变了"或"快照可能过期"时重跑 snapshot。

---

## 通用约定

- 不支持删除，引导用户去 Notion 界面操作
- 不支持 Database 类型页面
- 权限错误优先提示用户检查页面是否已共享给 Integration
- Token 不在对话里明文保留，用完即走