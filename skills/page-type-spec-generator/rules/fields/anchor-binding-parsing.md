# anchor_binding 解析规则

## 目标

把 xlsx 中的 `tag anchor binding` 文本解析为结构化 `tags[].anchor_binding`。

它的运行时消费方不是段打标 LLM，而是锚点重索引与块组装链路，主要对应：

1. `src/module/material/anchor_reindex/*`
2. `src/module/material/service/material_understanding_service.py`
3. `backup/.../refs/tag-anchor-contract.v1.md`

因此这里的首要目标是：结构正确、语义稳定、不要擅自发明业务规则。

## 输入

1. `tag anchor binding`

## 总规则

1. `anchor_binding` 必须输出为结构化对象，不得保留为自然语言。
2. Skeleton 阶段优先做语法容错与机械转移。
3. Semantic Draft 阶段只允许在已有结构上补全明确缺项，不允许发明锚点语义。
4. 不得把中文显示名或自由文本猜成 `target_tag_ids`。

## 目标结构

合法结构至少包含：

1. `target_tag_ids`
2. `page_window.mode`
3. `direction`
4. `required`

可选：

1. `page_window.prev`
2. `page_window.next`
3. `self_resolution`

## Stage 6：Skeleton

### 规则

1. 若原始文本为空，输出占位对象：

```json
{
  "placeholder": "__PTSG_PENDING__"
}
```

2. 若原始文本非空，先做语法容错：
   1. 修正常见引号问题
   2. 修正常见 `mode` 写法问题
   3. 保留业务人员已经写明的字段值
3. 只允许补以下默认值：
   1. `page_window.mode = within_type_run`
   2. `required = true`
   3. `self_resolution = direction_only`
4. 若 `target_tag_ids` 或 `direction` 无法从原文稳定提取，保留占位对象并记录问题。

## Stage 7：Semantic Draft

1. 若 Skeleton 已得到完整结构，可直接沿用。
2. 若 Skeleton 仍是占位对象，只有在原文里能明确恢复时才补成正式结构。
3. 若原文只是语法坏，不是语义缺失，可以在本阶段完成修正。
4. `target_tag_ids` 必须是稳定 spec tag id；看不懂时保留占位，不要猜。

## 写法要求

1. 忠实转换优先于“看起来更合理”。
2. `direction` 是候选范围约束，不是最终命中的真实方向。
3. `self_resolution` 只在原文或契约能支持时才写具体值。

## 禁止

1. 不得把字段改写成自然语言提示。
2. 不得仅凭 tag 名称或中文显示名猜出 `target_tag_ids`。
3. 不得因为缺少 `direction` 就随意补一个方向。
4. 不得把缺失原文的配置伪装成已确认事实。

## 失败信号

1. 最终仍是自然语言文本。
2. 原列为空且结果文件中找不到显式槽位。
3. 关键字段缺失却没有占位或问题记录。
4. `target_tag_ids` 来自猜测而非原文或稳定契约。
