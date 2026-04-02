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
   6. `notes`
3. Stage 6 至少记录 skeleton 层
4. Stage 7 至少记录 semantic-draft 层
5. Stage 8 至少记录 final-review 层或明确声明该槽位未进入 final-review

## 使用约束

1. `slot-manifest.json` 不得替代结果文件本身。
2. 结果文件仍必须显式保留字段与章节。
3. `slot-manifest.json` 的职责是显影与索引，不是代替内容。
4. `pending_slots` 必须从 `stage_records` 中的 `final-review` 视角推导，不得只看 skeleton 视角。

## 失败信号

以下情况说明 `slot-manifest.json` 失效：

1. 结果文件里有显式字段，但 `slot-manifest.json` 不知道它存在
2. `slot-manifest.json` 声称某字段已语义化，但结果文件仍是骨架模板态
3. `slot-manifest.json` 未能区分待语义生成与待人工补写
4. `final-review` 中存在显式占位，但 `slot-manifest.json` 没有在 final 视角记录该槽位
