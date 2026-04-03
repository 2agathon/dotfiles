# action_paths 生成规则

## 目标对象

生成 `page-semantic-spec.json` 中的 `action_paths[]`。

## 输入

1. `情景`
2. `情景id`
3. `阶段`
4. `阶段id`
5. `动作`
6. `动作id`
7. 当前 type 的 `block_type_ids`

## Stage 6：Skeleton

1. 只有当当前 type 的 block 集合都能按稳定 triad 完整、唯一分组时，才允许生成 `action_paths[]`。
2. 若没有稳定 triad，输出空数组 `[]`。
3. 若 triad 不完整，输出空数组 `[]`。
4. 若只覆盖了部分 block，也输出空数组 `[]`；不得输出部分覆盖的 `action_paths[]`。
5. 同一 `block_type_id` 在 Skeleton 阶段只允许归入一个 triad；无法唯一归组时输出空数组 `[]`。
6. 不得通过“子字段全部 pending”的对象来填满 `action_paths[]`。
7. 若 triad 缺失但后续仍需人工确认，在 `slot-manifest.json` 中记录 `pending_human` 或 `missing_required_source`。

## Stage 7：Semantic Draft

1. 仅当 `情景/阶段/动作` 与 `block_type_ids` 都稳定，且覆盖关系完整唯一时，生成正式条目。
2. `block_type_ids` 只能引用当前 type 的 block 集合。
3. `action_paths[]` 非空时，当前 type 的每个 block_type_id 都必须且只能出现在一个条目中。
4. 若 triad 仍不稳定，保持空数组并记录原因。

## 禁止

1. 不得因为 schema 可选就静默省略整个字段。
2. 不得凭 block 名称反推出业务动作路径。
3. 不得在最终层保留任何 `__PTSG_PENDING__` 的 action path 子字段。
4. 不得输出只覆盖部分 block 的 `action_paths[]`。
5. 不得让同一 `block_type_id` 同时出现在多个 action path 中。

## 失败信号

1. `action_paths[]` 被静默省略。
2. 生成了引用不存在 block 的路径。
3. 在无明确来源时臆造了业务三元组。
4. 最终层仍有带 `__PTSG_PENDING__` 子字段的 action path 对象。
5. `action_paths[]` 非空，但存在 block 未被任何 path 覆盖。
6. 同一 `block_type_id` 出现在多个 path 中。
