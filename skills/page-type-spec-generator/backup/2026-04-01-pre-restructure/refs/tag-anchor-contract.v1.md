# 标签锚点重索引契约（v1）

读者：工程师（含外部智能程序员）
目的：冻结锚点重索引的数据契约，保证“模型语义上下文”和“代码锚点定位”分层清晰且可追溯。

## 1. 边界

1. 本契约只定义“标签实例如何关联锚点实例”。
2. 本契约不定义模型如何生成 `tag_context` 文本。
3. 本契约不定义最终块组装算法细节（细节见 rulebook）。

## 2. 核心对象

1. 标签实例：`welp_mt_material_tag_segment.id`（简称 `segment_tag_id`）。
2. 锚点实例：同样来自 `welp_mt_material_tag_segment.id`，但被选为他人锚点。
3. 锚点绑定：某个标签实例到某个锚点实例的结构化关系。

## 2.1 与 tag-instance 段内顺序信号的关系

1. 本契约不新增“同段内前后方向”的独立主字段。
2. 同段多锚点判别所需的细粒度顺序信号，来自 tag instance 本身，而不是 anchor relation。
3. 因此 `anchor_direction` 继续只表达当前标签实例与最终锚点实例的主相对位置：`before|after|same_segment|nearby`。
4. 同段内的 before/after 比较只作为引擎内部证据，不在本契约中新增 `same_segment_relative_direction`。

## 3. 表契约（建议新增）

表名建议：`welp_mt_material_tag_anchor`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | bigint | 是 | 主键 |
| segment_tag_id | bigint | 是 | 被绑定标签实例 id，唯一 |
| material_code | varchar(64) | 是 | 冗余索引字段 |
| page_no | int | 是 | 被绑定标签所在页 |
| page_type_id | varchar(64) | 否 | 冗余字段 |
| anchor_status | varchar(16) | 是 | `located\|unresolved\|ambiguous\|invalid` |
| anchor_tag_id | varchar(64) | 否 | 锚点类型（spec 的 tag_id） |
| anchor_segment_tag_id | bigint | 否 | 锚点实例 id |
| anchor_direction | varchar(16) | 否 | `before\|after\|same_segment\|nearby` |
| anchor_strategy | varchar(32) | 否 | `exact_match\|nearest_line\|nearest_char\|rule_infer` |
| line_distance | int | 否 | 行距离，非负 |
| char_distance | int | 否 | 字符距离，非负 |
| segment_distance | int | 否 | 段序距离，非负 |
| anchor_source_page_no | int | 否 | 锚点实例所在页 |
| anchor_source_segment_code | varchar(64) | 否 | 锚点实例所在段 |
| reason_code | varchar(64) | 否 | 规则命中码 |
| reason_detail | text | 否 | 规则解释 |
| reindex_run_id | varchar(36) | 是 | 本次重索引批次 id |
| indexed_at | datetime | 是 | 重索引时间 |
| indexed_by | varchar(64) | 是 | 默认 `SYSTEM` |

索引建议：

1. `uniq(segment_tag_id)`
2. `idx_material_page(material_code, page_no)`
3. `idx_anchor_instance(anchor_segment_tag_id)`
4. `idx_material_anchor_tag(material_code, anchor_tag_id, anchor_status)`
5. `idx_reindex_run(reindex_run_id)`

## 4. 语义约束

1. `anchor_status=located` 时，`anchor_segment_tag_id` 必填。
2. `anchor_status=unresolved` 时，`anchor_segment_tag_id` 必为空。
3. `anchor_status=ambiguous` 时，`reason_code` 必填；`anchor_segment_tag_id` 可选：
   - 可为空：表示仅提示冲突，不给预选；
   - 可为 top1：表示“建议最优锚点”，用于人工审核预填，不代表自动放行。
4. `line_distance/char_distance/segment_distance` 只允许非负整数或 `null`。
5. `anchor_tag_id` 是锚点类型；真正绑定关系以 `anchor_segment_tag_id` 为准。

### 4.1 方向与来源字段解释

1. `anchor_direction` 描述“当前标签实例与最终锚点实例”的相对位置。
2. 判定顺序：先判 `segment_code` 是否相同（相同则 `same_segment`），否则先比 `page_no`，再同页比 `material_segment_no`。
3. `line_distance`/`char_distance`/`segment_distance` 是距离证据，不单独决定方向。
4. 同段内若存在更细的实例级顺序信号，也只用于内部筛选与排序，不改变 `anchor_direction` 主字段语义。

### 4.2 `same_segment` 定义（冻结）

1. `same_segment` 的判定条件是 `segment_code` 相同。
2. `same_segment` 不是“行距为 0”的同义词。
3. 当规则配置 `direction=same_segment` 时，仅允许同段候选参与排序。

### 4.3 `direction` 与 `anchor_direction` 不是一回事（冻结）

1. `direction` 是配置在 `anchor_binding` 上的候选范围约束，只影响“哪些他项候选能参与排序”。
2. 其中：
   - `before` = 同段或前段；
   - `after` = 同段或后段；
   - `same_segment` = 仅同段；
   - `nearby` = 同段及前后段。
3. `anchor_direction` 是最终命中的真实相对位置；即使规则配置为 `after`，若最终命中的是同段候选，输出也必须是 `same_segment`。

## 5. 运行时 JSON 契约

重索引步骤输出（单页示意）：

```json
{
  "material_code": "MAT-001",
  "page_no": 5,
  "reindex_run_id": "7f82e5fa-7d7b-4f70-8c52-c2f1f3f96ef8",
  "anchors": [
    {
      "segment_tag_id": 12031,
      "anchor_status": "located",
      "anchor_tag_id": "TAG_RECORD_TIME",
      "anchor_segment_tag_id": 11980,
      "anchor_direction": "before",
      "anchor_strategy": "nearest_line",
      "line_distance": 1,
      "char_distance": 26,
      "segment_distance": 2,
      "anchor_source_page_no": 4,
      "anchor_source_segment_code": "SEGMENT-4-11",
      "reason_code": "NEAREST_VALID_BY_LINE",
      "reason_detail": "同 run 内最近有效锚点"
    }
  ]
}
```

Schema 见：`src/module/material/docs/contracts/tag-anchor-contract.v1.schema.json`

## 6. 与段打标、块组装的边界

1. 段打标仍输出 `tag_context`，并保留入库。
2. 块组装的锚点主依据改为结构化锚点字段，不再从自由文本反推锚点。
3. `tag_context` 在块组装中仅作为语义说明辅助，不作为锚点唯一依据。
4. 块组装候选收集应围绕结构化锚点结果展开，不再以“三页窗口 + 缺 tag 就近补页”作为默认输入口径。
5. 块组装阶段默认锚点归属已完成；模型输入不再携带 `anchor_status` 等锚点质量字段。

## 7. 状态

- 版本：v1
- 状态：已冻结（字段可增，不允许改写既有语义）
