# anchor_binding 解析规则

## 目标

从 xlsx 中的 `tag anchor binding` 输入生成结构化 `tags[].anchor_binding`。

## 输入

1. `tag anchor binding`

## 输出

1. 结构化 `anchor_binding` 对象

## 总规则

1. `anchor_binding` 必须输出为结构化对象，不得保留为自然语言。
2. 允许做有限语法修复。
3. 关键字段缺失时不得静默编造。
4. 每次修复都必须记录。
5. 若整列为空，则直接省略 `anchor_binding` 字段。

## 目标结构

`anchor_binding` 只允许包含：

1. `target_tag_ids`
2. `page_window`
3. `direction`
4. `required`
5. `self_resolution`

## 允许值

### `page_window.mode`

1. `within_type_run`
2. `bounded`

### `direction`

1. `before`
2. `after`
3. `same_segment`
4. `nearby`

### `self_resolution`

1. `self_only`
2. `self_first`
3. `direction_first`
4. `direction_only`

## 解析步骤

### Step 1：文本读取

动作：

1. 读取原始 `tag anchor binding` 文本
2. 保留原文本用于后续修复记录

规则：

1. 若原始文本为空，直接省略该字段并结束本阶段

### Step 2：结构提取

动作：

1. 提取 `target_tag_ids`
2. 提取 `page_window.mode`
3. 提取 `direction`
4. 提取 `required`
5. 提取 `self_resolution`

要求：

1. 能提多少提多少
2. 未提取到的字段进入缺失处理，不得直接跳过整个对象

### Step 3：语法修复

允许修复：

1. 已知拼写别名
2. 引号缺失
3. 轻微括号不闭合
4. 轻微分隔符问题

已知允许自动修复的示例：

1. `with_type_run` -> `within_type_run`

### Step 4：默认值补齐

只允许对以下字段补默认值：

1. `page_window.mode` 默认 `within_type_run`
2. `required` 默认 `true`
3. `self_resolution` 默认 `direction_only`

## 缺失字段处理表

| 字段 | 处理 |
|---|---|
| `target_tag_ids` 缺失 | 记录问题；不得静默编造 |
| `page_window.mode` 缺失 | 补默认值 `within_type_run` |
| `direction` 缺失 | 记录问题；不得静默补值 |
| `required` 缺失 | 补默认值 `true` |
| `self_resolution` 缺失 | 补默认值 `direction_only` |
| `mode=bounded` 且 `prev/next` 缺失 | 记录问题；不得当作完整对象通过 |

### Step 5：完整性检查

必须检查：

1. `target_tag_ids` 是否存在
2. `direction` 是否存在
3. `page_window.mode` 是否存在
4. `required` 是否存在
5. 若 `mode=bounded`，`prev/next` 是否存在

## 字段规则

### 1. `target_tag_ids`

规则：

1. 必须是数组
2. 数组项必须是 tag id
3. 缺失时不得静默编造

### 2. `page_window.mode`

规则：

1. 允许值必须来自当前规则允许集合
2. 缺失时可补默认值
3. 若值为 `bounded`，则必须同时检查 `prev/next`

### 3. `direction`

规则：

1. 必须存在
2. 不得因缺失而静默补一个任意方向

### 4. `required`

规则：

1. 必须为布尔值
2. 缺失时可补默认值

### 5. `self_resolution`

规则：

1. 允许值必须来自当前规则允许集合
2. 缺失时可补默认值

## 修复记录要求

每次修复都必须至少记录：

1. 原始值
2. 修复后值
3. 修复类型

## 问题记录要求

以下情况必须写入问题记录：

1. `target_tag_ids` 缺失
2. `direction` 缺失
3. `mode=bounded` 但 `prev/next` 缺失

## 禁止

1. 不得把 `anchor_binding` 留成自然语言说明
2. 不得因为缺少 `direction` 就随意补一个值
3. 不得因为缺少 `target_tag_ids` 就静默填入猜测结果
4. 不得在无记录的情况下自动修复
5. 不得把缺关键字段的对象当作完整结果通过

## 质量检查

生成后必须检查：

1. 是否是结构化对象
2. 是否包含关键字段
3. 是否存在未记录的自动修复
4. 是否存在关键字段缺失却仍被当作完整对象输出
5. 若原列为空，是否正确省略该字段

## 失败信号

以下情况说明生成失败：

1. 最终仍是自然语言文本
2. `direction` 缺失却没有报错
3. `target_tag_ids` 缺失却没有报错
4. 修复发生但没有记录
5. 原列为空却仍然生成了 `anchor_binding`
