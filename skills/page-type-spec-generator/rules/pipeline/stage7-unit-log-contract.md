# Stage 7 Unit Log 契约

## 目标

`semantic-unit-log.json` 是 Stage 7 逐单元执行的审计证据。

它不负责保存最终内容；它负责证明：

1. Stage 7 确实按单元执行
2. 每个需要语义化的对象是否被处理
3. 未处理的对象为何未处理

## 总规则

1. Stage 7 只要开始执行，就必须产出 `semantic-unit-log.json`。
2. 一个 unit 只允许对应一个逻辑生成对象。
3. 处理每个 unit 时，必须先改目标文件、真实落盘。直接执行时允许在同一连续编辑批次结束后集中记录该批次已完成 unit；但不得在整份文件、整份 `semantic-draft/` 或整个 Stage 7 完成后再统一倒填日志。
4. 不得用一个 unit 覆盖多个同类槽位。
5. 若某个槽位需要 Stage 7 处理但被保留占位，也必须有对应 unit 或显式 skip 记录。
6. 对于 `needs_semantic_generation=true` 的槽位，默认要求 `handled=true`；`handled=false` 只能用于当前运行在 Stage 7 内被中止、或被上游 blocking 阻断的情况。
7. “保留 Stage 6 输出供人工复核”“conservative pass”“保持 skeleton 可见”都不是合法 skip 理由。
8. 文本类 unit 不得只靠 `notes` 证明自己已处理；必须留下处理前后证据。
9. 不得编写、保存、运行或依赖任何 Stage 7 helper script 来生成 unit 正文；unit log 只能记录直接执行产生的处理痕迹。
10. 若当前执行需要向用户汇报进度、请求决策、或因 blocking 中断，必须先把已完成 batch 的 unit 日志刷新到磁盘。

## 单元类型

只允许以下 `unit_kind`：

1. `type_description`
2. `block_description`
3. `tag_value_hint`
4. `tag_context_hint`
5. `tag_anchor_binding`
6. `top_level_description`
7. `hint_section`
8. `block_summary_slot`

## 最小结构

`semantic-unit-log.json` 至少包含：

1. `run_id`
2. `selected_type_id`
3. `units[]`

每个 `units[]` 元素至少包含：

1. `unit_id`
2. `unit_kind`
3. `target_slot_key`
4. `target_file`
5. `source_rules`
6. `handled`
7. `result_status`
8. `skip_reason`
9. `notes`
10. `before_snapshot`
11. `after_snapshot`
12. `content_changed`

## 字段说明

### `unit_id`

1. Stage 7 单元的稳定唯一键。
2. 不得在同一次运行内重复。

### `unit_kind`

1. 必须来自本文件定义的白名单。

### `target_slot_key`

1. 必须能映射到 `slot-manifest.json` 中的一个稳定 `slot_key`。
2. `hint_section` 与 `block_summary_slot` 必须使用章节级或槽位级 `slot_key`，不得退回整文件级 key。

### `target_file`

1. 指向 `semantic-draft/` 中被处理的目标文件。
2. 不得指向 `skeleton/`、`final-review/` 或最终交付目录。

### `source_rules`

1. 必须列出当前 unit 真正允许读取的规则文件。
2. 不得把未授权规则写进来。

### `handled`

1. `true` 表示该单元已实际执行。
2. `false` 表示被显式跳过。
3. `handled=true` 不得只表示“批量脚本里路过了这个 path”。

### `result_status`

推荐值：

1. `materialized`
2. `pending_human`
3. `missing_required_source`
4. `optional_visible_empty`
5. `blocked`
6. `skipped`

### `before_snapshot` / `after_snapshot`

1. `json_path` 对象记录当前槽位值。
2. `section_path` 或 block-summary 槽位记录当前章节或当前槽位的紧凑摘录。
3. 不得用泛化说明代替真实前后内容。

### `content_changed`

1. `true` 表示当前 unit 导致目标文件的当前槽位或章节发生了真实变化。
2. `false` 只允许用于：
   1. `tag_anchor_binding` 在 Stage 6 已是正式结构，Stage 7 仅确认沿用
   2. `handled=false` 的显式 skip
3. `top_level_description`、`type_description`、`block_description`、`tag_value_hint`、`tag_context_hint`、`hint_section`、`block_summary_slot` 若 `result_status=materialized`，默认必须 `content_changed=true`。

### `skip_reason`

1. 若 `handled=false`，必须非空。
2. 若 `handled=true`，必须为 `null` 或空。
3. `preserved_stage6_output_for_human_review`、`conservative_stage7_pass`、`kept_skeleton_content_visible` 一类理由视为非法 skip 理由。

## 失败信号

以下情况说明 Stage 7 证据链失效：

1. `semantic-unit-log.json` 缺失
2. 一个 `unit_id` 覆盖多个 `target_slot_key`
3. 一个需要 Stage 7 处理的 `slot_key` 没有对应 unit 记录
4. `handled=false` 但没有 `skip_reason`
5. `unit_kind` 不在白名单内
6. 大量 `needs_semantic_generation=true` 的 unit 被统一标记为 `handled=false`
7. Stage 7 unit 的唯一动作只是保留 Stage 6 原文，没有给出语义裁决结果
8. `before_snapshot`、`after_snapshot` 或 `content_changed` 缺失
9. `unit_kind` 与 `target_slot_key` 对应对象类型不匹配
10. 文本类 `materialized` unit 被记录为 `content_changed=false`
11. 多个 unit 在整文件重写后被一次性补日志，导致前后快照无法证明逐 unit 执行
12. 运行目录或 `tools/` 下存在 `stage7_*`、`semantic_draft.py` 或等价 helper script
13. 已向用户汇报 Stage 7 进度或离开 Stage 7，但本批次已完成 unit 仍未写入日志
