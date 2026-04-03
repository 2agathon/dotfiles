# anchor_binding 解析规则

## 目标对象

生成结构化 `tags[].anchor_binding`。

## 输入

1. `tag anchor binding`

## Stage 6：Skeleton

1. 若原始文本为空，不生成 `anchor_binding` 字段。
2. 若原始文本非空，先做语法容错。
3. 只允许对原始文本非空且结构已基本成立的配置补以下默认值：
   1. `page_window.mode = within_type_run`
   2. `required = true`
   3. `self_resolution = direction_only`
4. 若原始文本非空，但 `target_tag_ids` 或 `direction` 无法稳定提取，保留占位对象并记录问题。
5. 空列表示当前 tag 未声明锚点规则，不得用占位对象代替“无规则”。

## Stage 7：Semantic Draft

1. 若 Stage 6 因空列而未生成 `anchor_binding`，本阶段保持无字段，不得补出结构对象。
2. 若 Skeleton 已得到完整结构，直接沿用。
3. 若 Skeleton 仍是占位对象，只有在原文里能明确恢复时才补成正式结构。
4. 若原文只是语法坏，不是语义缺失，可以在本阶段完成修正。
5. `target_tag_ids` 必须是稳定 spec tag id；看不懂时保留占位，不要猜。

## 禁止

1. 不得把字段改写成自然语言提示。
2. 不得仅凭 tag 名称或中文显示名猜出 `target_tag_ids`。
3. 不得因为缺少 `direction` 就随意补一个值。
4. 不得把缺失原文的配置伪装成已确认事实。
5. 不得把空列解释成“有锚点规则但待补细节”。
6. 不得用占位对象代替“当前 tag 无 anchor_binding”。

## 失败信号

1. 最终仍是自然语言文本。
2. 原列为空，但结果中仍生成了 `anchor_binding` 对象。
3. 原列非空且明显在声明锚点规则，但结果文件中既没有正式结构，也没有占位对象。
4. 关键字段缺失却没有占位或问题记录。
5. `target_tag_ids` 来自猜测而非原文或稳定契约。
