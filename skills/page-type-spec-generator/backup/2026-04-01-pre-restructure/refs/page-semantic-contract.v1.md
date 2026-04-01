# page-semantic.schema 契约说明（v1）

读者：工程师（含外部智能程序员）
目的：把 `page-semantic.schema.json`、各类型 `page-semantic-spec.json` 与当前代码消费方式放到同一份契约里，作为后续讨论字段新增、结构调整、代码落地的共同基线。

## 1. 文档定位

这份文档回答 4 件事：

1. `page-semantic.schema.json` 当前定义了什么。
2. 各类型 `page-semantic-spec.json` 运行时承载什么。
3. 当前代码实际读取了哪些字段、没读取哪些字段。
4. 后续若要在该 schema 上扩字段，应该落在哪一层、会影响哪些代码。

本文件是团队契约说明，不替代运行时 schema 文件本身。

## 2. 文件与载荷关系

### 2.1 机器真相

- schema：`src/module/material/data/medical-material-specs/meta/v1/page-semantic.schema.json`
- 数据载荷：`src/module/material/data/medical-material-specs/parser/v1/namespaces/<namespace>/types/<type_id>/page-semantic-spec.json`

### 2.2 它在系统里的职责

`page-semantic-spec.json` 定义某个 `type_id` 下：

1. 该页有哪些标签（`tags[]`）。
2. 这些标签给模型看的提示是什么（`value_hint/context_hint`）。
3. 该页能生成哪些块（`block_types[]`）。
4. 这些块如何挂到业务 action path（`action_paths[]`）。

一句话：它是“页类型语义规格”，不是运行时结果，也不是规则引擎输出。

## 3. 当前代码如何消费它

### 3.1 入口与路由

- `src/module/material/config.py:80`
  - 固定 meta schema 文件名：`page-semantic.schema.json`
- `src/module/material/catalog/page_type_parser_catalog.py:180`
  - `read_semantic_schema()` 读取 schema 文件
- `src/module/material/catalog/page_type_parser_catalog.py:216`
  - `get_page_semantic_spec()` 读取某个 type 的 `page-semantic-spec.json`
- `src/module/material/catalog/page_type_parser_catalog.py:277`
  - `get_tags_for_type()` 直接返回 `tags[]`
- `src/module/material/catalog/page_type_parser_catalog.py:295`
  - `get_block_types_for_type()` 直接返回 `block_types[]`
- `src/module/material/catalog/page_type_parser_catalog.py:313`
  - `get_action_paths_for_type()` 直接返回 `action_paths[]`

### 3.2 当前消费字段

1. `src/module/material/ai/segment_ai.py:31`
  - `tags_from_semantic_spec()` 当前只取：
  - `id`
  - `name`
  - `value_hint`
  - `context_hint`
2. `src/module/material/service/material_understanding_service.py:886`
  - 组装块时读取：
  - `block_types[].id/name/description/tags`
  - `action_paths[]`
3. `src/module/material/service/material_review_service.py:2082`
  - 构造审核页 tag spec 时读取：
  - `id/name/value_hint/context_hint`
4. `src/module/material/ai/common.py:153`
  - `get_tag_names_by_ids()` 只读取 `tags[].id/name`

### 3.3 当前未做的事

1. 当前 catalog 只是“读取 JSON”，没有在读取时自动执行 schema 校验。
2. 当前 LLM prompt 只消费标签提示，不消费块定义和 action path。
3. 当前代码已为 `tags[]` 预留 `anchor_binding` 的 TypedDict/Keys 常量，并在锚点重索引、审核链路中消费该结构。

这个现状很重要：后续新增字段时，默认不会自动生效，必须显式补 catalog/specs/service 使用点。

## 4. 顶层结构总览

根对象要求：

- `type=object`
- `required=[version, page_type, block_types, tags]`
- `additionalProperties=false`


| 路径             | 类型     | 必填  | 说明             |
| -------------- | ------ | --- | -------------- |
| `version`      | string | 是   | 语义规格版本，SemVer。 |
| `page_type`    | object | 是   | 当前规格绑定的页类型。    |
| `action_paths` | array  | 否   | 业务动作路径到块类型的映射。 |
| `block_types`  | array  | 是   | 本页可生成的块定义。     |
| `tags`         | array  | 是   | 本页标签定义。        |


## 5. `page_type` 契约


| 路径               | 类型     | 必填  | 约束                  | 说明                                     |
| ---------------- | ------ | --- | ------------------- | -------------------------------------- |
| `page_type.id`   | string | 是   | `^TYPE_[A-Z0-9_]+$` | 页类型 ID，必须与目录名和 taxonomy 中的 type_id 对齐。 |
| `page_type.name` | string | 是   | `minLength=1`       | 页类型展示名。                                |


代码关系：

1. 当前 catalog 会把整个 `page_type` 原样读出，但业务侧很少直接消费它。
2. 实际运行时，type 主标识更多来自外层 page classification 结果与 type 目录名。
3. 因此 `page_type.id` 的价值主要在于契约自校验和人工 review，而不是运行时路由主键。

## 6. `action_paths[]` 契约

### 6.1 结构

每个元素要求：

- `required=[context, phase, action, block_type_ids]`
- `additionalProperties=false`


| 路径                              | 类型       | 必填  | 约束                   | 说明                       |
| ------------------------------- | -------- | --- | -------------------- | ------------------------ |
| `action_paths[].context`        | object   | 是   | `IdName`             | 业务情景。                    |
| `action_paths[].phase`          | object   | 是   | `IdName`             | 业务阶段。                    |
| `action_paths[].action`         | object   | 是   | `IdName`             | 业务动作。                    |
| `action_paths[].block_type_ids` | string[] | 是   | `^BLOCK_[A-Z0-9_]+$` | 该 action path 可生成的块类型列表。 |


`IdName` 子结构：


| 路径       | 类型     | 必填  | 约束                  | 说明     |
| -------- | ------ | --- | ------------------- | ------ |
| `*.id`   | string | 是   | `^[A-Z][A-Z0-9_]*$` | 稳定 ID。 |
| `*.name` | string | 是   | `minLength=1`       | 展示名。   |


### 6.2 当前代码消费

1. `material_understanding_service` 在块组装时读取 `action_paths`，将其与 `block_types` 一起传给 `_assemble_blocks_one_page()`。
2. 当前代码不在 catalog 层对 `block_type_ids` 是否真的引用了存在的 `block_types[].id` 做额外检查；这个约束仍主要由人工维护和 schema review 保障。

### 6.3 不变量

1. `block_type_ids` 中每个值都应能在同文件 `block_types[].id` 中找到定义。
2. 同一个 `block_type_id` 可以出现在多个 action path 中，但语义必须明确，不可出现“同块在不同动作下意义相反”的情况。

## 7. `block_types[]` 契约

### 7.1 结构

每个元素要求：

- `required=[id, name, tags]`
- `additionalProperties=false`


| 路径                          | 类型     | 必填  | 约束                   | 说明          |
| --------------------------- | ------ | --- | -------------------- | ----------- |
| `block_types[].id`          | string | 是   | `^BLOCK_[A-Z0-9_]+$` | 块类型 ID。     |
| `block_types[].name`        | string | 是   | `minLength=1`        | 块展示名。       |
| `block_types[].description` | string | 否   | -                    | 块语义说明。      |
| `block_types[].tags`        | array  | 是   | -                    | 块内可引用的标签集合。 |


`block_types[].tags[]` 子结构：


| 路径                                 | 类型     | 必填  | 约束                 | 说明                |
| ---------------------------------- | ------ | --- | ------------------ | ----------------- |
| `block_types[].tags[].tag_id`      | string | 是   | `^TAG_[A-Z0-9_]+$` | 引用根级 `tags[].id`。 |
| `block_types[].tags[].role`        | string | 否   | -                  | 该 tag 在块内的角色。     |
| `block_types[].tags[].description` | string | 否   | -                  | 仅在块内生效的局部说明。      |


### 7.2 当前代码消费

1. `material_understanding_service` 当前显式消费：
  - `id`
  - `name`
  - `description`
  - `tags`
2. 对 `block_types[].tags[]`，当前代码更多是把原始结构继续向下传，不会在 catalog 层做复杂解释。

### 7.3 不变量

1. `block_types[].tags[].tag_id` 应在根级 `tags[]` 中存在。
2. `role` 是块内语义，不应被误当成运行时审核状态或锚点状态。
3. `description` 是给人和 prompt 看的补充说明，不应承载代码必须解析的隐藏规则。

## 8. `tags[]` 契约

### 8.1 结构

每个元素要求：

- `required=[id, name, value_hint]`
- `additionalProperties=false`


| 路径                    | 类型     | 必填  | 约束                 | 说明                   |
| --------------------- | ------ | --- | ------------------ | -------------------- |
| `tags[].id`           | string | 是   | `^TAG_[A-Z0-9_]+$` | 标签 ID。               |
| `tags[].name`         | string | 是   | `minLength=1`      | 标签展示名。               |
| `tags[].value_hint`   | string | 是   | `minLength=1`      | 值提示：可打什么、如何取值。       |
| `tags[].context_hint` | string | 否   | -                  | `tag_context` 的书写提示。 |



### 8.2 当前代码消费

1. LLM 段打标 prompt 当前直接消费 `value_hint/context_hint`。
2. 审核页 spec 展示当前也直接消费这些字段。
3. v1 已实现：段打标输出除 `tag_value/tag_context` 外，承载 tag-instance 的段内顺序信号（`segment_position_order`、`position_confidence`），用于同段多锚点判别；该信号不是 `tags[]` 配置字段，而是段打标运行时产物。

### 8.3 不变量

1. `value_hint` 负责说明“值怎么取”，不应夹带流程状态。
2. `context_hint` 负责引导 `tag_context` 书写，不应承担运行时锚点绑定真相。

### 8.4 `tag_context` 语义契约（冻结）

`tag_context` 的定义不绑定当前页类型树，也不绑定某一种载体形态。它面向的是“各种文字信息载体上的标签实例”。

冻结定义：

> tag_context 是对 (tag_id, tag_value) 对子的语义补足。模型应充分利用当前载体中所有可感知的原始信息，遵循以下原则，为每条标签实例尽可能完整地补足断言边界。
感知边界：tag_context 的信息来源限于当前载体的原始内容。不得引用其他标签的抽取结论作为事实依据；不得在载体已有信息之外进行外推。
应补足的内容：断言成立所必需但未被 (tag_id, tag_value) 显式表达的对象、语义角色、成立方式，以及时间/范围/条件等边界；必要时，可极简带入构成命题本身所需的字段名、表头、条款主语等来源性语义。
结果而非过程：模型应通过推断确定断言边界，但 tag_context 只记录推断结果——以事实性陈述表达，不记录推断步骤，不解释判断依据。此原则约束的是输出形式，不是感知范围；推断得出的事实必须进入结果，"过程不入结果"不等于"推断结论不可使用"。
硬约束：不得使用 tag_context 合理化错误命中；不得填入证据原文转录、位置定位、归组/绑定说明或领域外推。

#### 8.4.1 `tag_context` 回答什么问题

`tag_context` 只回答：**这条标签实例在断言什么。**

它不回答：

1. 为什么命中这个标签。
2. 它在原载体的什么位置。
3. 它和哪些实例归为同一组。
4. 从业务或领域上还能进一步推出什么。

#### 8.4.2 应覆盖的最小语义缺口

仅当缺失会导致断言不完整或产生歧义时，`tag_context` 才补足以下内容：

1. **所指对象**：该值指向谁、什么、哪一项、哪一角色、哪一条目。
2. **语义角色**：该值在此处表示什么，而不只是字面字符串。
3. **成立方式**：肯定/否定、当前/既往、已发生/拟定、要求/承诺/建议/结论等。
4. **成立边界**：时间点、阶段、范围、条件、段内局部范围等。
5. **最小来源性语义**：仅当字段名、表头、条款主语、局部标题本身已构成命题必要部分时，允许极简带入。

#### 8.4.3 明确不应进入 `tag_context` 的内容

以下内容应由其他字段或流程承载，不得写入 `tag_context`：

1. 原文证据片段或大段转录（应由 evidence span 承载）。
2. “因为什么所以判成这个标签”的推理过程（应由 reasoning 承载）。
3. 页码、坐标、表格列号、章节路径、区域定位等结构定位信息（应由 source locator 承载）。
4. 锚点、归组、绑定、聚合、实体归属等下游流程决策。
5. 超出断言本身的领域解释、业务外推、下游用途说明。

#### 8.4.4 验收句

只看 `(tag_id, tag_value, tag_context)`，不看原页面时，应能准确说出“这条实例在断言什么”；但不应从中读出“它为什么这样判、位于哪里、如何归组、还能额外推出什么”。

## 9. 字段消费矩阵


| 路径                                       | 主要消费者                            | 当前是否已消费 | 用途                  |
| ---------------------------------------- | -------------------------------- | ------- | ------------------- |
| `version`                                | catalog 读取                       | 否       | 主要用于契约标识。           |
| `page_type.id/name`                      | catalog 读取                       | 弱消费     | 人工对齐、自描述。           |
| `action_paths[]`                         | `material_understanding_service` | 是       | 块组装业务路径。            |
| `block_types[].id/name/description/tags` | `material_understanding_service` | 是       | 块组装输入。              |
| `tags[].id/name`                         | `segment_ai`、`common.py`、审核页     | 是       | 标签识别、展示映射。          |
| `tags[].value_hint`                      | `segment_ai`、审核页                 | 是       | LLM 取值提示。           |
| `tags[].context_hint`                    | `segment_ai`、审核页                 | 是       | LLM 语义提示。           |



## 10. 当前 schema 与代码之间的缺口

1. schema 已经定义了完整 tag/block/action 结构，但 catalog 没有在读取时做 schema validate。
2. 代码把 `description/value_hint/context_hint` 等文本字段作为“提示”消费，但没有把它们当结构化规则解析。
3. 这意味着：未来若要新增锚点类字段，不应继续塞进自由文本，而应放进 schema 的显式字段里。
4. 但“tag-instance 段内顺序信号”不属于 `page-semantic-spec.tags[]` 的静态配置，而属于段打标输出契约与存储契约，不能误放到 `anchor_binding` 中。

## 11. 变更影响矩阵


| 变更位置                                   | 影响代码                             | 风险                      |
| -------------------------------------- | -------------------------------- | ----------------------- |
| 根级 required/additionalProperties       | 所有读取该 spec 的路径                   | schema 与数据文件不一致会导致规范漂移。 |
| `action_paths` 结构                      | `material_understanding_service` | 块组装路径错误。                |
| `block_types` 结构                       | `material_understanding_service` | 块组装缺块、错块。               |
| `tags.id/name`                         | `segment_ai`、审核页、名称映射            | tag 无法识别或展示错乱。          |
| `value_hint/context_hint` | `segment_ai`                     | LLM 输出质量波动。             |


## 12. 评审清单

每次改 `page-semantic.schema.json` 或某个 `page-semantic-spec.json` 前后，都要过这几条：

1. 新字段是给模型看的提示，还是给代码吃的结构？
2. 若是给代码吃的结构，是否已在 `catalog/specs.py` 增加常量与类型定义？
3. 若变更 `block_types/action_paths`，块组装链路是否同步评审？
4. 若变更 `tags[]`，`segment_ai` 与审核页展示是否同步评审？
5. 是否把“必须结构化的信息”错误地继续留在自然语言字段里？

## 13. 推荐的后续扩展落点

如果团队后续决定把“锚点取自哪里”显式写进 page-semantic，推荐落点仍然是：

- `tags[].<新字段>`

理由：

1. 锚点来源本质上是 tag 级约束，不是 block 级说明。
2. 当前代码已经把 `tags[]` 当成段打标与审核的统一标签源。
3. 把结构放在 `tags[]`，后续规则引擎、审核页、门禁都能围绕同一份 tag spec 扩展。

## 14. 状态

- 版本：v1
- 状态：讨论中；本文件先冻结“当前 schema + 当前代码消费”的共同认知，再讨论新增字段

## 15. 已确认的试点契约（TYPE_LAB_REPORT）

本节为当前已确认的团队口径，优先级高于“推荐落点”描述。

### 15.1 标签级锚点结构（冻结）

在 `tags[]` 下新增字段 `anchor_binding`，其最小结构固定如下：


| 路径                                       | 类型       | 必填  | 约束                                           | 说明                                        |
| ---------------------------------------- | -------- | --- | -------------------------------------------- | ----------------------------------------- |
| `tags[].anchor_binding`                  | object   | 否   | `additionalProperties=false`                 | 标签级锚点定义；仅对需要锚点的标签填写。                      |
| `tags[].anchor_binding.target_tag_ids`   | string[] | 是   | `minItems=1`，元素匹配 `^TAG_[A-Z0-9_]+$`         | 允许作为锚点来源的标签 ID，按优先级排序。                    |
| `tags[].anchor_binding.page_window`      | object   | 是   | `additionalProperties=false`                 | 候选页窗口。                                    |
| `tags[].anchor_binding.page_window.mode` | string   | 是   | `enum=[within_type_run, bounded]`            | 搜索窗口模式；默认 `within_type_run`。              |
| `tags[].anchor_binding.page_window.prev` | integer  | 否   | `minimum=0`                                  | 仅 `mode=bounded` 时必填，向前可搜索页数。             |
| `tags[].anchor_binding.page_window.next` | integer  | 否   | `minimum=0`                                  | 仅 `mode=bounded` 时必填，向后可搜索页数。             |
| `tags[].anchor_binding.direction`        | string   | 是   | `enum=[before, after, same_segment, nearby]` | 候选方向范围（仅约束“他项”候选，见下）。                     |
| `tags[].anchor_binding.required`         | boolean  | 是   | -                                            | 是否要求该标签产生锚点结果。                            |
| `tags[].anchor_binding.self_resolution`  | string   | 否   | 见下                                           | 同类型候选时“自身”与“他项”的选择策略；默认 `direction_only`。 |


`**self_resolution` 枚举与默认**：


| 值                 | 含义                                    |
| ----------------- | ------------------------------------- |
| `self_only`       | 只能取自身（当前 segment 内同 tag 的自身实例）作为锚点参照。 |
| `self_first`      | 先取自身，失败再按 direction 取他项。              |
| `direction_first` | 先按 direction 取他项，失败再取自身。              |
| `direction_only`  | 只能按 direction 取他项（默认）。                |


**语义约束**：

1. `direction` 仅约束“他项”候选（其他 segment 上的同 target_tag 实例）；不约束“自身”是否可被选。
2. 当策略包含“自身可选”（`self_only` / `self_first` / `direction_first`）时，自身候选不受 `direction` 限制。
3. 多候选时仍按现有排序与 gap 判定；优势不足降级 `ambiguous`，不盲选。
4. 该策略为通用“同类型参照策略”，不局限于目录等单一场景。

`page_window` 语义：

1. `mode=within_type_run`：在“同一 `page_type_id` 的连续页段”内持续搜索候选；这是默认模式。
2. `mode=bounded`：只在当前页前后显式窗口内搜索，窗口由 `prev/next` 指定。
3. 为降低配置成本，不要求每个标签都显式填写 `prev/next`；仅在确需收窄范围时使用 `bounded`。

#### 15.1.1 参数逐项说明（配置者视角）

> 这一节只回答三件事：每个参数在算法里什么时候生效、配错会出现什么状态、应该怎么选。


| 参数                      | 算法生效点                                                     | 错配时常见现象                                                                 | 实战建议                                        |
| ----------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------- |
| `target_tag_ids`        | 候选池第一步：只保留 `tag_id` 命中的候选；按数组顺序尝试。                        | 全部 `unresolved`（候选池为空）或大量 `invalid`（有基础候选但被后续规则排光）。                     | 只放“真正可作为锚点”的 tag，优先级高的放前面。                  |
| `page_window.mode`      | 候选页过滤。`within_type_run` 用同类型连续页段；`bounded` 用 `prev/next`。 | `bounded` 过窄时大量 `invalid/unresolved`。                                   | 默认 `within_type_run`；只有误绑太多时再收窄到 `bounded`。 |
| `page_window.prev/next` | 仅 `mode=bounded` 时生效。                                     | `prev/next` 太小：找不到正确锚点；太大：`ambiguous` 上升。                               | 先小窗口起步，再按误召回调大。                             |
| `direction`             | 仅过滤“他项候选”（不是自身候选）。`before=同段或前段`，`after=同段或后段`。           | 配 `after` 但数据多在前页且无同段候选，会 `invalid`；配 `same_segment` 但跨段取值，会 `invalid`。 | 不确定先用 `nearby`；稳定后再收紧。                      |
| `required`              | 审核门禁生效。                                                   | `required=true` 且无可用锚点会阻断段打标审核。                                         | 真正必需锚点才设 `true`。                            |
| `self_resolution`       | 决定“自身实例”能否进入候选池。                                          | 该自锚点却用 `direction_only` 时常见 `invalid`。                                  | 自锚点场景用 `self_only`；想保底回退用 `self_first`。     |


#### 15.1.2 `direction` 的精确定义（避免歧义）

1. `same_segment`：候选必须与当前标签实例 `segment_code` 相同。
2. `before`：候选范围为“同段或当前之前的段”（先判同段，再比 `page_no`，同页再比 `material_segment_no`）。
3. `after`：候选范围为“同段或当前之后的段”（先判同段，再比 `page_no`，同页再比 `material_segment_no`）。
4. `nearby`：不按前后硬限制，只要在页窗内即可参与排序；同段、前段、后段都可进入候选。
5. `direction` 只约束“他项候选”；当 `self_resolution` 允许自身时，自身不受 `direction` 影响。

#### 15.1.3 `self_resolution` 怎么选


| 值                 | 什么时候用                                                    | 风险                    |
| ----------------- | -------------------------------------------------------- | --------------------- |
| `self_only`       | 标签定义就是“自己就是锚点”（如 `TAG_RECORD_TIME` / `TAG_REPORT_TIME`）。 | 自身缺失时不会回退他项。          |
| `self_first`      | 优先自身，但允许在自身缺失时回退到他项。                                     | 容易引入跨段误绑，需要配合窗口/方向收紧。 |
| `direction_first` | 业务上优先找外部锚点，但允许兜底自身。                                      | 规则复杂，建议仅在明确需求时使用。     |
| `direction_only`  | 明确禁止自锚点。                                                 | 自锚点业务会产生大量 `invalid`。 |


#### 15.1.4 参数组合的推荐模板

1. **自锚点模板（记录时间/报告时间）**
  - `target_tag_ids=[自身 tag]`
  - `self_resolution=self_only`
  - `direction=same_segment`（可读性更强）
2. **随事项字段模板（条码号/项目名）**
  - `target_tag_ids=[TAG_REPORT_TIME]`
  - `self_resolution=direction_only`
  - `direction=after` 或 `nearby`（按版式；`after` 语义为“同段或后段”）
  - `page_window=bounded(prev=0,next=1)` 或 `within_type_run`
3. **高噪声场景模板**
  - 先用 `nearby + bounded` 控召回
  - 观测 `ambiguous` 后再收紧 `direction`

#### 15.1.5 状态判定速查（你看到状态时该看什么）

1. `located`：已自动选出锚点。
2. `ambiguous`：候选不止一个且优势不足；可带 top1 建议锚点，仍需人工确认。
3. `invalid`：有基础候选，但被结构规则（页窗/方向/same_segment）全部排除。
4. `unresolved`：基础候选本来就不存在（`target_tag_ids` 对不上或数据缺失）。

### 15.2 迁移策略（已确认）

1. 不做双轨过渡：不保留“结构化锚点 + 文案锚点并行”的长期状态。
2. `TYPE_LAB_REPORT` 作为首个试点，直接切到结构化锚点定义。
3. 与 `anchor_binding` 同步，LLM 相关提示词必须改造：
  - 不再要求模型在 `tag_context` 中表达锚点决策。
  - `tag_context` 只保留语义解释，不承载锚点真相。
4. 块组装与审核继续只消费结构化锚点结果。

### 15.5 审核与放行口径（冻结）

1. 段打标完成后自动计算锚点并入库，锚点审核并入“段打标审核”，不再单设“锚点索引审核”节点。
2. `ambiguous/invalid` 默认作为提醒信号；在段打标审核页人工确认后，该条按 `located` 处理。
3. `ambiguous` 允许写入建议最优锚点（top1）到 `anchor_segment_tag_id`，用于人工审核预填；状态仍是 `ambiguous`，不等价于自动放行。
4. 审核唯一硬阻断：标签 `anchor_binding.required=true` 且无可用锚点（一个都没有）时，段打标审核不可通过。
5. `anchor_binding.required=false` 或未配置锚点规则的标签，不因锚点状态阻断段打标审核。

### 15.6 块组装输入口径（冻结）

块组装可用标签实例集合应满足：

1. 当前页新锚点实体下可归属该实体的标签实例（可跨页）；
2. 暂未归属实体的候选标签实例（供块边界补充）。

说明：

1. 块组装主归组依据是结构化锚点实体（由 `anchor_segment_tag_id` 派生），不是相邻页窗口启发式。
2. `tag_context` 只作语义补充，不承担锚点判定职责。
3. 块组装阶段默认锚点归属已定；不向模型暴露 `anchor_status` / `has_anchor_rule` 等锚点质量字段。
4. 旧的“三页窗口 + 缺 tag 就近补页”实现不再代表冻结口径；若代码仍保留该路径，应视为待收敛遗留实现，而不是文档认可的目标行为。

### 15.3 试点范围约束

1. 本轮只对 `TYPE_LAB_REPORT` 的标签做结构化锚点定义，不扩到其他 type。
2. 本轮不引入 `anchor_key`、`forbidden_tag_ids`、`group_scope`、阈值字段。
3. 本轮不在 `page-types` 增加复杂策略字段，先验证标签级结构是否足够承载。

### 15.4 多候选自动判定口径（冻结）

1. 单个合法候选：直接 `located`。
2. 多个合法候选：按距离排序后仅在优势充分时自动 `located`，否则降级 `ambiguous`。
3. 自动流程不主动选择更远候选；仅当最近候选被结构规则排除时，才会考虑下一候选。
4. `ambiguous` 场景由人工审核确认，不因“有候选”而强行自动落锚。

### 15.7 TYPE_LAB_REPORT 自锚点约束（冻结）

1. `TAG_RECORD_TIME` 与 `TAG_REPORT_TIME` 的 `anchor_binding.target_tag_ids` 指向自身类型。
2. 两者 `self_resolution` 应显式配置为 `self_only`，含义是“仅允许自身候选”。
3. 该配置用于表达“记录时间/报告时间就是本事项主锚点本身”，避免被他项候选干扰。
