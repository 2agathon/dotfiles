---
name: chat-parser
description: >
  解析聊天导出文件，提炼成标准会话数据对象，供后续任务调用。当用户提到聊天记录、群聊分析、想生成海报/报告/图谱、或上传了 JSONL/JSON/TXT/HTML 聊天导出文件时触发。这是所有聊天数据任务的入口，后续任何任务（海报、关系图谱、记忆系统）都必须先经过本 skill 拿到数据对象。
metadata:
  collection: 2agathon-dotfiles
  layer: 领域专项
  domain: chat-data
  pipeline_stage: ingest
  invocation: user-request
---

# chat-parser

## 触发条件

用户提到以下任意一种情况时进入本 skill：
- 上传了聊天导出文件（JSONL / JSON / TXT / HTML）
- 提到「分析群聊」「分析聊天记录」「生成海报」「生成报告」
- 明确说要处理某个群或某段私聊数据

---

## AI 行为规格

### Step 1. 拿到文件路径

如果用户已上传文件或提供了路径，直接进入 Step 2。

如果没有，询问：
> 请提供聊天导出文件的路径，或直接上传文件。目前支持 WeFlow 导出的 JSONL 格式。

### Step 2. 询问时间范围（必填）

**在执行解析之前，必须向用户确认时间范围。**

原因：导出文件的首尾可能存在沉默期，代码只能算出「第一条消息到最后一条消息」的跨度，无法知道用户的真实意图（比如「我导出了整个3月，但3月前5天没人说话」）。

询问：
> 这份导出记录覆盖的时间范围是？
> - 起始日期（如果不确定，可跳过）
> - **结束日期**（必填，例如：2026-03-31）
>
> 这对海报标题和时间跨度计算非常重要。

拿到时间范围后，把用户声明的 `declaredStart` 和 `declaredEnd` 作为参数传给解析脚本。

### Step 3. 执行解析

确认依赖已安装（只需一次）：
```bash
pip install jieba
```

执行解析（带用户声明的时间范围）：
```bash
# 只有结束日期
python <skill_path>/scripts/parse.py <path/to/export.jsonl> --end 2026-03-31

# 同时有起始和结束日期
python <skill_path>/scripts/parse.py <path/to/export.jsonl> --start 2026-03-01 --end 2026-03-31
```

### Step 4. 读取结果

从 stdout 提取分隔符之间的内容：

```
---CHAT_PARSER_RESULT---
{ ... }
---CHAT_PARSER_RESULT_END---
```

将其解析为 JSON，得到标准会话数据对象，用于驱动后续任务。

> 落盘文件（`chat-parser/<文件名>_parsed.json`）是调试副产物，AI 不需要主动读取。

### Step 5. 衔接下游

拿到数据对象后，AI 应主动告知用户解析结果摘要，并询问下一步：

```
✓ 解析完成
  会话：{name}（{type}）
  时间：{start} ~ {end}（{days} 天）
  消息：{totalMessages} 条，活跃成员 {activeMembers} 人
  最活跃时段：{peakHourLabel}
  高频词：{topWords 前 5 个}

你想接下来做什么？
- 生成群聊海报（发回群内）
- 生成数据报告
- 分析关系图谱
- 其他
```

用户选择后，将数据对象传递给对应的下游 skill。

---

## 失效处理

| 情况 | 处理方式 |
|------|----------|
| 消息量 < 50 条 | 告知用户数据量不足，统计结果可能失真，询问是否继续 |
| 时间跨度 < 1 天 | 告知时段分布无意义，其他数据正常输出 |
| 纯媒体群（文本 < 10%） | 告知词频分析已跳过，只输出基础统计 |
| 文件格式不支持 | 告知当前只支持 WeFlow JSONL，引导用户重新导出 |
| 脚本执行报错 | 输出错误信息，询问用户是否需要排查 |

---

## 输出规格

完整 schema 见 `references/output-schema.md`。

输出包含八个字段：

| 字段 | 内容 | 用途 |
|------|------|------|
| meta | 基础元数据 | 时间范围、消息总量 |
| members | 活跃度排行（含头像） | 可视化排行 |
| activity | 时段/每日/类型分布 | 图表渲染 |
| interactions | @提及记录 | 互动分析 |
| memberStats | 每人行为特征 | AI 判断成员角色，无需心算 |
| conversationSessions | 对话自然段落 | AI 理解话题节奏 |
| silenceGaps | 沉默间隔排行 | AI 理解群作息 |
| messages | 完整原始消息 | AI 深度分析、金句提取、群画像 |

下游 skill 从此对象按需取材，chat-parser 不决定数据用途。

---

## 已知限制

- 当前只支持 WeFlow JSONL 格式，其他平台适配器待添加
- 群名有时是 chatroom ID，非真实群名
- WeFlow 强依赖：换平台需重写适配层（计划在 chat-render 跑通后重构）
