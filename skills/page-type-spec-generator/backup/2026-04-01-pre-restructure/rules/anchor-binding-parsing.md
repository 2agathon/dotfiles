# anchor_binding 解析规则

## 定位

`anchor_binding` 是 tag 级锚点定义，决定这个标签实例如何归属到一个块。
它是条件必填——仅对需要锚点归属的标签填写，不是所有 tag 都要写。

xlsx 里的 `tag anchor binding` 列是接近 JSON 的文本，可能有语法缺陷，需要容错解析。

Agent 的职责是**忠实转换**，不做业务逻辑校验，不覆盖业务人员写的内容。

---

## 目标结构

解析后应产出合法的 JSON 对象：

```json
{
  "target_tag_ids": ["TAG_RECORD_TIME"],
  "page_window": { "mode": "within_type_run" },
  "direction": "nearby",
  "required": true,
  "self_resolution": "direction_only"
}
```

五个字段的语义（来源：tag-anchor-contract.v1.md + page-semantic-contract.v1.md）：

| 字段 | 语义 | 合法值 |
|---|---|---|
| `target_tag_ids` | 允许作为锚点来源的标签 ID，按优先级排序 | TAG_XXX 数组，minItems=1 |
| `page_window.mode` | 搜索锚点的页范围模式 | `within_type_run`（默认）/ `bounded` |
| `page_window.prev/next` | 仅 mode=bounded 时填，向前/后可搜索页数 | 非负整数 |
| `direction` | 他项候选的方向范围约束（不是最终命中方向） | `before` / `after` / `same_segment` / `nearby` |
| `required` | 找不到锚点时是否阻断该标签的块归属 | boolean，本 skill 默认全部 true |
| `self_resolution` | 当前标签自身是否可作为候选锚点的策略 | `self_only` / `self_first` / `direction_first` / `direction_only`（默认） |

关键区分：`direction` 是候选范围约束，不等于最终命中的 `anchor_direction`（运行时字段）。

---

## 解析步骤

### 第一步：语法容错

xlsx 里常见的语法缺陷：
- 括号未闭合（如 `{"with_type_run"` 少了 `}`）
- key 缺失（如 `{"with_type_run"}` 漏了 `"mode":` ）
- 用了单引号而不是双引号
- 换行符混入

处理方式：尽力推断意图，提取出五个字段的值。

所有语法问题记录到输出摘要的"xlsx 语法问题"节，提示用户修正原始文件。

### 第二步：缺失字段处理

仅在字段**完全缺失**（原文里找不到）时才介入，不覆盖业务人员已经写的值。

| 字段 | 缺失时的处理 |
|---|---|
| `target_tag_ids` | 标注 `[OPEN QUESTION: target_tag_ids 缺失，请补充锚点来源标签]` |
| `page_window.mode` | 默认填 `within_type_run`，标注 `[ASSUMPTION: 默认 within_type_run]` |
| `page_window.prev/next` | 仅 mode=bounded 时必填，缺失则标注 `[OPEN QUESTION: mode=bounded 时需要填写 prev/next]` |
| `direction` | 标注 `[OPEN QUESTION: direction 缺失，请补充候选方向]`，该 tag 的 anchor_binding 暂留空 |
| `required` | 全部默认 `true`（启动时已告知用户，用户未否决则使用此默认值） |
| `self_resolution` | 默认 `direction_only`，标注 `[ASSUMPTION: 默认 direction_only]` |

---

## 何时不生成 anchor_binding

xlsx 里该 tag 的 `tag anchor binding` 列**完全为空**时，不生成 anchor_binding 字段。
直接省略，不做任何推断补填。

---

## 输出摘要里的语法问题报告格式

```
xlsx 语法问题（需修正原始文件）：
⚠️  第 X 行（TAG_XXX）anchor_binding：括号未闭合，已按推断解析
⚠️  第 X 行（TAG_XXX）anchor_binding：mode key 缺失，已补 "mode" 键名
⚠️  第 X 行（TAG_XXX）anchor_binding：direction 缺失，已标注 [OPEN QUESTION]
```
