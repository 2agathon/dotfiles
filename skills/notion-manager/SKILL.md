---
name: notion-manager
description: >
  操作用户的 Notion 工作区：爬取并缓存工作区结构（快照）、提取容器页词表、
  执行 AI 归类协议、搜索页面、读取页面结构与内容、创建页面（含容器页 📌 Callout）、
  追加内容、移动页面。支持用页面标题代替 ID。当用户提到 Notion 页面的读取、搜索、
  整理、归类、搬移、推送内容、查看结构等操作时，必须使用这个 skill。
---

# Notion Manager Skill

---

## 层一：知识归类协议（无环境依赖）

**这一层与执行环境无关。任何能理解文字的 AI 均可执行。**

### 前提

用户需提供 Notion Integration Token，以及本次要归类的内容。

### Step 1：获取词表

通过任意可用方式获取容器页词表（见层二）。词表包含每个容器页的**不可替代性**和**边界**。

### Step 2：推理归属

逐一对照词表，输出以下格式：

```
归属分析：
  ✓ 属于「XX」
    理由：[内容对应该容器的不可替代性]
    不违反边界：[说明不触碰 XX 的边界]

  ✗ 不属于「YY」
    原因：[触碰了 YY 的边界，或不可替代性对不上]
```

### Step 3A：匹配现有容器

确认归属，等用户同意后执行写入操作。

### Step 3B：现有容器装不下 → 提议新容器

说明现有词条为什么装不下，然后给出：

```
建议新建容器页：「[名称]」
  父级：[挂在哪个骨架下]
  不可替代性：[没有它会少掉什么]
  边界：[什么内容不该进来]
```

等用户确认后执行创建。**容器页顶部必须放 📌 Callout，格式：**

```
📌
不可替代性：[填写]
边界：[填写]
```

📌 emoji 不可替换，否则脚本无法识别。

### 迭代约定

- 内容已有页面：不建新页，在原页追加，写元信息（什么触发了迭代、改变的是哪个前提）
- 新内容：按归属创建内容页

---

## 层二：Notion 操作（按环境选择执行方式）

**以下三种方式等价，按当前环境选最顺手的一种。**

---

### 方式 A：运行 Python 脚本（本地环境有 Python）

所有操作通过 `scripts/notion_ops.py` 执行：

```bash
# 快照
python scripts/notion_ops.py snapshot --token TOKEN
python scripts/notion_ops.py snapshot-info
python scripts/notion_ops.py wordlist                        # 输出词表，供层一使用

# 查询
python scripts/notion_ops.py resolve --query "标题"
python scripts/notion_ops.py search  --token TOKEN --query "关键词"
python scripts/notion_ops.py structure --token TOKEN --page-id "标题或ID"
python scripts/notion_ops.py read     --token TOKEN --page-id "标题或ID"

# 写入（执行前需用户确认）
python scripts/notion_ops.py create --token TOKEN \
  --parent-id "父页面" --title "标题" [--content "..." | --content-file path]

python scripts/notion_ops.py create --token TOKEN \
  --parent-id "父页面" --title "标题" \
  --container --indispensable "..." --boundary "..."         # 容器页

python scripts/notion_ops.py append --token TOKEN \
  --page-id "目标页面" [--content "..." | --content-file path]

python scripts/notion_ops.py move --token TOKEN \
  --page-id "源页面" --target-parent-id "目标父页面"
```

长内容（>200字）先写临时文件再用 `--content-file` 传入。

---

### 方式 B：AI 直接调用 Notion API（有 HTTP 工具，无 Python）

AI 按以下接口规范直接发请求，逻辑与脚本完全一致。

**通用请求头：**
```
Authorization: Bearer {token}
Notion-Version: 2022-06-28
Content-Type: application/json
```

**Page ID 格式：** 从 URL 中提取 32 位 hex，格式化为 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

#### 搜索页面
```
POST https://api.notion.com/v1/search
{"query": "关键词", "filter": {"value": "page", "property": "object"}, "page_size": 20}
```

#### 读取子块（分页）
```
GET https://api.notion.com/v1/blocks/{page_id}/children?page_size=100
# has_more=true 时用 next_cursor 继续翻页，直到完整获取
```

#### 读取页面属性
```
GET https://api.notion.com/v1/pages/{page_id}
```

#### 创建页面
```
POST https://api.notion.com/v1/pages
{
  "parent": {"page_id": "{parent_id}"},
  "properties": {"title": {"title": [{"type": "text", "text": {"content": "标题"}}]}},
  "children": [ ...blocks... ]   // 单次最多 100 块，超出分批 PATCH 追加
}
```

#### 追加内容
```
PATCH https://api.notion.com/v1/blocks/{page_id}/children
{"children": [ ...blocks... ]}   // 每批最多 100 块
```

#### 📌 Callout 块结构
```json
{
  "object": "block",
  "type": "callout",
  "callout": {
    "rich_text": [{"type": "text", "text": {"content": "不可替代性：...\n边界：..."}}],
    "icon": {"type": "emoji", "emoji": "📌"},
    "color": "gray_background"
  }
}
```

#### Markdown → Notion Blocks 对照
| Markdown | Notion block type |
|---|---|
| `# ` | heading_1 |
| `## ` | heading_2 |
| `### ` | heading_3 |
| `- ` | bulleted_list_item |
| `1. ` | numbered_list_item |
| `- [ ] ` / `- [x] ` | to_do |
| `> ` | quote |
| 普通行 | paragraph |

---

### 方式 C：仅理解协议，手动操作（无任何执行环境）

AI 读懂层一的归类协议，给出归属判断和建议。
用户自己去 Notion 界面完成实际操作。
适用于 ChatGPT Web 等网络请求受限的环境。

---

## 通用约定

- **不支持删除**，引导用户去 Notion 界面操作
- **不支持 Database 类型页面**
- structure 默认 3 层深度
- 写入操作（create / append / move）执行前必须向用户确认目标页面和内容摘要
- 权限错误优先提示用户检查页面是否共享给 Integration
