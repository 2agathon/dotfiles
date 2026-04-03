# 校验门禁

## 总规则

1. 本阶段负责门禁，不负责继续补写正式内容。
2. 每项检查结果必须归入：`blocking`、`warning`、`pass`。
3. 存在任一 `blocking` 时，不得通过到最终交付。
4. 校验必须区分结构状态、语义状态与 review-ready 状态。
5. 最终层真实问题必须真实反映到报告；报告失真本身是校验失败，而不是文风问题。
6. 若无法证明 Stage 7 是逐单元执行，则不得宣称 Stage 7 合规。

## Blocking Gates

### 1. review schema 失败

以下任一失败，记为 `blocking`：

1. `page-types.data.json` 不符合 `schema/review/page-types.schema.json`
2. `page-types.tree.json` 不符合 `schema/review/page-types.schema.json`
3. `page-semantic-spec.json` 不符合 `schema/review/page-semantic.schema.json`

### 2. 必填 ID 为空

以下任一为空字符串，记为 `blocking`：

1. `page_type.id`
2. `block_types[].id`
3. 根级 `tags[].id`
4. `block_types[].tags[].tag_id`
5. `categories[].id`
6. `types[].id`

### 3. 身份阻断未被拦截

以下任一出现，记为 `blocking`：

1. `identity-map.json` 中存在 `blocked`
2. `helper_only`、`invalid_or_noise` 被写入最终根级对象集合
3. `identity-map.json` 与最终结果中的对象 id 不一致

### 4. 引用闭合失败

以下任一失败，记为 `blocking`：

1. `block_types[].tags[].tag_id` 在根级 `tags[]` 中找不到
2. block/tag 存在重复 ID 冲突且未收敛
3. `action_paths[].block_type_ids` 中的值在 `block_types[].id` 中找不到
4. `action_paths[]` 非空，但存在 `block_types[].id` 未被任何 action path 覆盖
5. 同一 `block_types[].id` 出现在多个 action path 中

### 5. 最终结果绕过 semantic draft / final review

以下任一失败，记为 `blocking`：

1. 最终交付目录不是从 `final-review/` 派生
2. `final-review/` 不是从 `semantic-draft/` 派生
3. 最终交付目录与 `semantic-draft/` 的核心对象集合不一致

### 6. type 污染

以下任一失败，记为 `blocking`：

1. `page-semantic-spec.json` 中的 `block_types[].id` 不属于当前选中 type 的 identity-map block 集合
2. `page-semantic-spec.json` 中的根级 `tags[].id` 不属于当前选中 type 的 identity-map tag 集合
3. 最终结果混入未选中 type 的对象

### 7. block 首标签缺失

以下任一失败，记为 `blocking`：

1. `workbook.normalized.json` 中 `block_start` 行携带首标签定义信号，但 `identity-map.json` 中没有对应 tag 身份
2. `identity-map.json` 中存在来自 `block_start` 首标签行的 tag，但最终 `page-semantic-spec.json` 未包含该 tag

### 8. 空编码伪恢复 ID

以下任一失败，记为 `blocking`：

1. `raw_id` 为空的具名 tag 被标记为 `resolved_recovered`，但没有 `recovery_source`
2. 缺失原始 ID 的 tag 最终使用 `TAG_U...` 一类非占位 canonical id

### 9. 槽位清单失真

以下任一失败，记为 `blocking`：

1. `slot-manifest.json` 缺失
2. 结果文件中的显式槽位与 `slot-manifest.json` 记录不一致
3. 某个必填字段存在于结果文件但未出现在 `slot-manifest.json`
4. `final-review/` 中存在显式占位，但 `pending_slots` 未列出该槽位
5. `final-review/` 中仍是 `__PTSG_PENDING__`，但对应 final 视角 `slot_status` 为 `transferred` 或 `materialized`

### 10. 报告失真

以下任一失败，记为 `blocking`：

1. `final-review/` 或最终交付层仍有显式占位，但 `validation-report.json` 声称 `pending_slots=[]`
2. `warnings=[]`，但最终层仍存在显式占位、模板残留或高风险自动决策
3. `final-report.md` 写 `remaining_risks: none`，但 `validation-report.json` 中仍有 warning、pending 或高风险自动决策

### 11. Stage 7 执行证据缺失

以下任一失败，记为 `blocking`：

1. `semantic-unit-log.json` 缺失
2. `slot-manifest.json` 中 `needs_semantic_generation=true` 的槽位，没有对应 Stage 7 unit 记录，也没有显式 skip 记录
3. Stage 7 记录声称 `materialized`，但没有对应 `unit_id`
4. `needs_semantic_generation=true` 的大量槽位在 Stage 7 中被统一标记为 `handled=false`
5. `skip_reason` 使用 `preserved_stage6_output_for_human_review`、`conservative_stage7_pass`、`kept_skeleton_content_visible` 或等价表述
6. Stage 7 结束后，`semantic-draft/` 与 `skeleton/` 在需要语义化的对象上只剩路径复制，没有真实语义裁决痕迹

### 12. 最终报告范围泄漏

以下任一失败，记为 `blocking`：

1. `final-report.md` 报告了只存在于 intermediate 的问题，却未出现在 `final-review/` 或最终交付层
2. `final-report.md` 报告了未选中 type 的问题
3. `final-report.md` 使用 `final set` 等表述指向并未进入最终层的对象

### 13. Stage checkpoint 缺失或越权执行

以下任一失败，记为 `blocking`：

1. `run-manifest.json` 缺少按阶段递增的 `stage_history[]`
2. 某阶段产物已存在，但 `stage_history[]` 中没有对应 checkpoint
3. 存在覆盖多个 stage 的统一总控脚本、`run_all` 式入口或等价执行痕迹
4. 无法证明当前结果是按 stage 顺序落盘推进，而不是事后回填目录

### 14. Raw / Normalize 稠密空矩阵膨胀

以下任一失败，记为 `blocking`：

1. `workbook.raw.json` 以 declared range 为主，把大量空白单元格逐个展开成 JSON
2. `workbook.raw.json` 缺少 `declared_max_*`、`effective_max_*`、`non_empty_cell_count` 等稀疏统计字段
3. `workbook.normalized.json` 继续在大量空行上展开规范化结果，而不是仅围绕有效行集

## Warning Gates

### 8. 显式占位进入最终结果

以下情况记为 `warning`：

1. 存在 `resolved_placeholder` 对象进入最终结果
2. 存在 `__PTSG_PENDING__` 残留
3. `pending_slots` 统计层级不是 `final-review` 或最终交付层

### 9. `value_hint` 仍为骨架模板态

以下情况记为 `warning`：

1. 多个不同 tag 的 `value_hint` 仍保留完全相同的骨架模板结构
2. `value_hint` 只剩字段头拼接而缺少语义收束
3. 主识别句主要由通用模板构成，缺少当前 tag 的专属识别信号
4. 大量 `value_hint` 仍以“优先依据关键词匹配”“保留与当前标签语义直接对应的值”等通用句开头
5. 大量 `value_hint` 复用同一条“依据当前语义片段中能指向对象的表述进行识别”式主句
6. 出现 `。。`、重复句尾或“重点参考优先依据...”这类明显模板残渣

### 10. `context_hint` 异常稀少或异常泛化

以下情况记为 `warning`：

1. 当前 type 存在明显时间类或角色类标签，但 `context_hint` 全部保留占位或全部泛化
2. 明显低歧义标签被错误补写长句
3. 多个不相关 tag 共享同一句 `context_hint` 主句
4. 大量 `context_hint` 只是“补充该值对应的时间点 / 对象 / 范围”这类抽象短句，而没有 tag 专属差异
5. 会在多个 block 中复用的 tag，被写成单一 block 视角的 `context_hint`

### 11. hint 贫血或模板化

以下情况记为 `warning`：

1. `tagging-hint.md`、`assembly-hint.md`、`block-summary-hint.md` 只有极少量泛化内容
2. 同一句泛化提醒被换名后批量套用
3. hint 文件仍停留在 skeleton 模板态
4. `tagging-hint.md` 主要是一标签一句提醒，未形成标签对或标签家族边界
5. `assembly-hint.md` 主要在写 tag 级取值，而非 block 级组装决策
6. `block-summary-hint.md` 主要在列 tag 槽位，未形成摘要组织原则

### 12. block description 模板化

以下情况记为 `warning`：

1. 多个 block description 共享明显统一尾句或统一收束段
2. 不同 block 的 description 出现可互换的大段复用
3. description 中出现明显错位复用，导致块语义与尾句不一致
4. description 大量复用同一类统一收束句，导致不同 block 之间的语义主轴难以区分

### 13. `aliases` 异常

以下情况记为 `warning`：

1. `types[].aliases` 被静默省略
2. `types[].aliases` 出现明显由 `type_name` 拆词、Block 名称挪用或 description 改写得到的推断别名
3. 在没有稳定来源的情况下，`types[].aliases` 输出了非空数组

### 15. placeholder 收束不足

以下情况记为 `warning`：

1. 同一 selected type 内出现多个显示名相同、角色相同、结构功能相同的 placeholder tag，但没有显式区分理由
2. 同一语义功能的 placeholder 被拆成大量 `DUP` 变体进入最终根级 tag 集合

### 16. 规则替代

以下情况记为 `warning`：

1. 某阶段结果明显由通用私有模板生成，而非对应 rule 约束的结果形态

### 17. 人工待补项较多

以下情况记为 `warning`：

1. `pending_slots` 达到当前 type 可见槽位的一定比例
2. 关键说明型字段仍大面积保留占位

## Pass Gates

### 18. 合法显式占位

以下情况可记为 `pass`：

1. `context_hint` 在 skeleton 与 final-review 中显式保留占位，且已被标记为 `pending_human`
2. 明显不需要额外 `context_hint` 的 tag，在 final-review 中显式收束为空字符串
3. `page-summary-hint.md` 无素材时输出显式空模板
4. `continuation-hint.md` 无素材时输出显式空模板
5. schema 要求但 Excel 无来源的字段已显式占位并进入待补清单

## 报告要求

### `validation-report.json`

必须包含：

1. `structure_status`
2. `semantic_status`
3. `review_readiness_status`
4. `blocking`
5. `warnings`
6. `pass`
7. `pending_slots`
8. `status`
9. `pending_slots_scope`
10. `high_risk_auto_decisions`
11. `stage7_compliance_status`
12. `report_scope`

### `audit-report.md`

必须写入：

1. 所有自动修复
2. 所有占位符生成
3. 所有 warning
4. 所有 blocking
5. 所有人工待补项
6. 所有高风险自动决策

## 最终状态规则

1. 若 `blocking` 非空，最终状态必须失败。
2. 若 `blocking` 为空但 `warnings` 非空，最终状态为通过但有风险。
3. 只有 `blocking` 为空时，才允许生成最终交付目录。
4. `pending_slots` 非空时，不得把 `remaining_risks` 写成 `none`。
5. `stage7_compliance_status` 不是 `passed` 时，不得在任何最终报告文本中暗示“严格按阶段执行完成”。
