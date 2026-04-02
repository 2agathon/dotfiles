# action_paths 生成规则

## 目标

生成 `page-semantic-spec.json` 中的 `action_paths[]`。

运行时消费方主要是：

1. `src/module/material/service/material_understanding_service.py`
2. `src/module/material/catalog/specs.py`

当前业务允许该字段为空，因此这里的核心原则是：不要臆造动作路径。

## 总规则

1. review-ready 结果里，`action_paths[]` 必须显式可见。
2. 没有稳定三元组时，优先输出空数组，不要发明 `context/phase/action`。
3. 只有在 xlsx 明确提供稳定的 `情景/阶段/动作` 三元组时，才生成正式条目。

## Stage 6：Skeleton

1. 若没有稳定三元组，输出空数组 `[]`。
2. 若存在不完整三元组，允许输出占位结构并标记待人工确认。

## Stage 7：Semantic Draft

1. 仅当 `情景/阶段/动作` 与 `block_type_ids` 都稳定时，生成正式 `action_paths[]` 项。
2. `block_type_ids` 只能引用当前 type 的 block 集合。

## 禁止

1. 不得因为 schema 可选就静默省略整个字段。
2. 不得凭 block 名称反推出业务动作路径。

## 失败信号

1. `action_paths[]` 被静默省略。
2. 生成了引用不存在 block 的路径。
3. 在无明确来源时臆造了业务三元组。
