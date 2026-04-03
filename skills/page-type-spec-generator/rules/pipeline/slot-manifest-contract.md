# slot-manifest 契约

## 目标

`slot-manifest.json` 是本 skill 的槽位真相。

它不描述业务身份；身份真相仍由 `identity-map.json` 承担。
它描述的是：在 review-ready 结果里，每个显式字段或章节当前处于什么状态、来自哪里、接下来该由谁处理。

## 总规则

1. 只要某个字段或章节被显式生成，就必须在 `slot-manifest.json` 中登记。
2. `slot-manifest.json` 必须能同时索引 `skeleton/` 与 `semantic-draft/` 中的槽位。
3. Skeleton 阶段必须初始化 `slot-manifest.json`。
4. Semantic Draft 阶段必须回写每个槽位的处理状态。
5. Final Review 阶段必须以 `slot-manifest.json` 为准生成待补清单。
6. `slot-manifest.json` 必须显式区分 Skeleton、Semantic Draft、Final Review 三层记录，不得只保留 skeleton 视角。
7. 所有在 `final-review/` 中显式可见的字段都必须进入 `slot-manifest.json`，不得只追踪“看起来重要”的一部分槽位。
8. 只要最终层可见值仍是 `__PTSG_PENDING__`，对应槽位在 final 视角不得标记为 `transferred` 或 `materialized`。

## 最小结构

`slot-manifest.json` 至少包含：

1. `run_id`
2. `selected_type_id`
3. `slots[]`

每个 `slots[]` 元素至少包含：

1. `file`
2. `slot_key`
3. `path_kind`
4. `path`
5. `slot_kind`
6. `source_rules`
7. `source_columns`
8. `source_rows`
9. `slot_status`
10. `placeholder_value`
11. `needs_semantic_generation`
12. `needs_human_review`
13. `notes`
14. `stage_records`

## 字段说明

### `file`

1. 指向结果文件相对路径
2. 必须落到具体文件，而不是目录

### `path_kind`

允许值：

1. `json_path`
2. `section_path`

说明：

1. JSON 文件使用 `json_path`
2. Markdown 文件使用 `section_path`

### `slot_key`

1. 指向逻辑槽位的稳定唯一键
2. 不得因阶段层级变化而改变
3. 推荐格式：`<logical-file>::<path>`

### `path`

1. 若 `path_kind=json_path`，使用稳定 JSON 路径
2. 若 `path_kind=section_path`，使用稳定章节路径或章节标题

### `slot_kind`

推荐值：

1. `required_id`
2. `required_text`
3. `optional_text`
4. `structured_object`
5. `markdown_section`
6. `markdown_file`
7. `governance_field`
8. `block_local_field`

### `source_rules`

1. 必须列出当前槽位允许读取的规则文件
2. 不得写入未授权规则

### `source_columns`

1. 记录当前槽位依赖的 xlsx 列
2. 若当前槽位无直接 Excel 列来源，也必须显式写空数组

### `source_rows`

1. 记录当前槽位对应的行号
2. 若为全局字段，可为空数组

### `slot_status`

只允许使用 `state-and-placeholder-policy.md` 中定义的槽位状态。

### `placeholder_value`

1. 若当前槽位无占位值，写 `null`
2. 若当前槽位使用统一占位，必须显式写 `__PTSG_PENDING__`

### `needs_semantic_generation`

1. Skeleton 阶段用于告诉 Stage 7 是否必须处理该槽位

### `needs_human_review`

1. 若 AI 当前不能安全完成，必须置为 `true`

### `notes`

1. 记录简短原因
2. 不得把结构真相藏在自由文本里；真相仍应由显式字段承担

### `stage_records`

1. 必须按阶段记录同一槽位的处理痕迹
2. 每个元素至少包含：
   1. `stage`
   2. `file`
   3. `slot_status`
   4. `placeholder_value`
   5. `handled`
   6. `unit_id`
   7. `notes`
3. Stage 6 至少记录 skeleton 层
4. Stage 7 至少记录 semantic-draft 层
5. Stage 8 至少记录 final-review 层或明确声明该槽位未进入 final-review
6. Stage 7 的 `unit_id` 必须可回溯到 `semantic-unit-log.json` 中的一个 unit
7. Stage 7 / Stage 8 回写时，`slot_status` 必须以目标文件当前可见值为准，不得只按执行意图填写
8. 若 Stage 6 已按章节或槽位落槽，Stage 7 / Stage 8 也必须保持同粒度记录；不得退回整文件级真相
9. Stage 7 可在一个连续编辑批次结束后集中回写本批次已完成槽位；但不得在整份文件、整个 Stage 7 或向用户汇报之后仍不回写

## 使用约束

1. `slot-manifest.json` 不得替代结果文件本身。
2. 结果文件仍必须显式保留按字段规则要求可见的字段与章节；字段规则明确允许无字段时可缺席。
3. `slot-manifest.json` 的职责是显影与索引，不是代替内容。
4. `pending_slots` 必须从 `stage_records` 中的 `final-review` 视角推导，不得只看 skeleton 视角。
5. `version`、`schema_meta.*`、`order`、`replaced_by`、`block_types[].tags[].role`、`block_types[].tags[].description` 等治理字段和块内子字段，若在最终层显式出现，也必须被当作正式槽位追踪。
6. `final-report.md` 与 `validation-report.json` 中出现的 pending，必须能回溯到 `final-review` 视角的 `slot-manifest` 记录。
7. 若最终层显式值已是非占位 prose、非空字符串或非空结构，`slot_status` 不得仍记为 `pending_human`、`missing_required_source` 或 `pending_semantic`。
8. 若字段规则允许空字符串或无字段，final 视角状态也必须与该合法形态一致；不得硬记成 pending。
9. `validation-report.json.pending_slots` 必须直接从 `slot-manifest.json` 的 final 视角投影得到，不得用单独的文件扫描逻辑替代。
10. `section_path` 与 `json_path` 槽位在 final 视角一律同等对待，不得因为是 markdown 章节就漏出 pending 清单。
11. 若当前执行向用户汇报 Stage 7 进度、请求决策或因 blocking 中断，`slot-manifest.json` 必须先刷新到该时刻的真实状态。

## 失败信号

以下情况说明 `slot-manifest.json` 失效：

1. 结果文件里有显式字段，但 `slot-manifest.json` 不知道它存在
2. `slot-manifest.json` 声称某字段已语义化，但结果文件仍是骨架模板态
3. `slot-manifest.json` 未能区分待语义生成与待人工补写
4. `final-review` 中存在显式占位，但 `slot-manifest.json` 没有在 final 视角记录该槽位
5. `final-review` 中存在显式可见的治理字段或块内子字段，但 `slot-manifest.json` 完全未追踪
6. `final-review` 中仍是 `__PTSG_PENDING__`，但对应 final 视角 `slot_status` 被记录为 `transferred` 或 `materialized`
7. Stage 7 记录声称某槽位已语义化，但没有对应 `semantic-unit-log.json.unit_id`
8. `semantic-draft/` 或 `final-review/` 中显式值已是 materialized prose 或非空结构，但 `slot_status` 仍停留在 pending
9. Stage 6 已按章节或槽位显式落槽的 hint，在 Stage 7 / Stage 8 被退化成单个整文件状态
10. `validation-report.json.pending_slots` 与 `slot-manifest.json` final 视角不一致，尤其遗漏 markdown section 槽位
11. 已向用户汇报 Stage 7 进度或离开 Stage 7，但本批次已完成槽位仍未写入 `slot-manifest.json`
