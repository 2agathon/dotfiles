# page-types.schema 契约说明（v1）

读者：工程师（含外部智能程序员）
目的：把 `page-types.schema.json`、命名空间下的 `page-types.data.json` / `page-types.tree.json` 与当前代码消费方式放到同一份契约里，作为后续讨论类型字段新增、流程门禁落点、taxonomy 演进策略的共同基线。

## 1. 文档定位

这份文档回答 4 件事：

1. `page-types.schema.json` 当前定义了什么。
2. `page-types.data.json` 与 `page-types.tree.json` 分别承载什么。
3. 当前代码实际读取了哪些字段、没读取哪些字段。
4. 后续若要在 type 层扩字段，应该放在哪里、会影响哪些代码。

本文件是团队契约说明，不替代运行时 schema 文件本身。

## 2. 文件与载荷关系

### 2.1 机器真相

- schema：`src/module/material/data/medical-material-specs/meta/v1/page-types.schema.json`
- 运行时全量 taxonomy：`src/module/material/data/medical-material-specs/parser/v1/namespaces/<namespace>/page-types.data.json`
- 运行时轻量 tree：`src/module/material/data/medical-material-specs/parser/v1/namespaces/<namespace>/page-types.tree.json`

### 2.2 两份载荷的职责区分

1. `page-types.data.json`
   - 用于完整类型定义
   - 可带 `schema_meta`、`sources`、更完整的 type 字段
2. `page-types.tree.json`
   - 用于快速枚举 category/type 树
   - 适合分类 prompt、选项构建、检索树展示

一句话：`data` 偏完整事实，`tree` 偏轻量视图。

## 3. 当前代码如何消费它

### 3.1 入口与路由

- `src/module/material/config.py:89`
  - 固定 meta schema 文件名：`page-types.schema.json`
- `src/module/material/catalog/page_type_definition_catalog.py:85`
  - `get_schema()` 读取 schema
- `src/module/material/catalog/page_type_definition_catalog.py:81`
  - `get_data()` 读取 namespace 下的 `page-types.data.json`
- `src/module/material/catalog/page_type_definition_catalog.py:77`
  - `get_tree()` 读取 namespace 下的 `page-types.tree.json`

### 3.2 当前消费字段

1. `src/module/material/ai/page_ai.py:113`
   - 从 `tree` 中读取：
   - `categories[].id/name/description`
   - `types[].id/name/description/aliases`
   - 用于页分类 prompt 与标题兜底校验
2. `src/module/material/catalog/page_type_definition_catalog.py:89`
   - 从 `data` 中读取：
   - `categories[].id/name`
   - `types[].id/name`
   - 用于 `get_type_detail()` / `get_type_display_names()` / `get_type_to_category_mapping()`
3. `src/module/material/service/material_review_service.py:2061`
   - 从 `tree` 中读取：
   - `category.id`
   - `type.id/name/aliases`
   - 用于页类型审核下拉项

### 3.3 当前未做的事

1. 当前 catalog 同样只是读取 JSON，没有在读取时自动执行 schema 校验。
2. `deprecated/replaced_by`、`source_keys` 等治理字段，当前绝大多数业务代码尚未消费。
3. 当前锚点流程门禁并不是从 type schema 推导，而是写在 material 流水线逻辑里。

## 4. 顶层结构总览

根对象要求：

- `type=object`
- `required=[version, description, last_updated, categories]`
- `additionalProperties=false`

| 路径 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `version` | string | 是 | taxonomy 版本。 |
| `description` | string | 是 | taxonomy 整体说明。 |
| `last_updated` | string | 是 | 最近更新日期，`format=date`。 |
| `schema_meta` | object | 否 | schema 元信息。 |
| `sources` | array | 否 | 规范来源引用。 |
| `categories` | array | 是 | 分类树根。 |

## 5. 顶层辅助结构

### 5.1 `schema_meta`

| 路径 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `schema_meta.owner` | string | 否 | owner。 |
| `schema_meta.maintainers` | string[] | 否 | 维护人列表。 |
| `schema_meta.change_log` | array | 否 | 变更记录。 |

`change_log[]`：

| 路径 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `date` | string | 是 | 日期。 |
| `summary` | string | 是 | 摘要。 |
| `details` | string | 否 | 详情。 |

当前代码状态：

- 当前业务代码基本不消费 `schema_meta`。
- 该结构主要用于人工治理、版本追溯、review 说明。

### 5.2 `sources`

| 路径 | 类型 | 必填 | 约束/枚举 | 说明 |
|---|---|---|---|---|
| `sources[].key` | string | 是 | source key pattern | 供 `source_keys` 引用。 |
| `sources[].title` | string | 是 | - | 来源标题。 |
| `sources[].authority_level` | string | 是 | `NATIONAL_STANDARD/INDUSTRY_STANDARD/REGULATORY_NORM/TEXTBOOK/HOSPITAL_TEMPLATE/OTHER` | 权威等级。 |
| `sources[].publisher` | string | 否 | - | 发布机构。 |
| `sources[].year` | integer | 否 | `1900-2100` | 年份。 |
| `sources[].doc_number` | string | 否 | - | 文号/标准号。 |
| `sources[].effective_date` | string | 否 | `format=date` | 生效日期。 |
| `sources[].url` | string | 否 | `format=uri` | 链接。 |
| `sources[].notes` | string | 否 | - | 备注。 |

当前代码状态：

- 当前业务代码基本不消费 `sources`。
- 它的价值主要在知识追溯与规范裁决，不在当前流程主链。

## 6. `categories[]` 契约

每个 category 要求：

- `required=[id, name, description, types]`
- `additionalProperties=false`

| 路径 | 类型 | 必填 | 约束 | 说明 |
|---|---|---|---|---|
| `categories[].id` | string | 是 | `ID` | 分类 ID。 |
| `categories[].name` | string | 是 | `HumanName` | 分类名。 |
| `categories[].description` | string | 是 | `minLength=1` | 分类说明。 |
| `categories[].order` | integer | 否 | `>=0` | 展示排序。 |
| `categories[].deprecated` | boolean | 否 | default `false` | 分类是否废弃。 |
| `categories[].replaced_by` | string | 否 | `ID` | 替代 category。 |
| `categories[].source_keys` | string[] | 否 | unique | 引用顶层 `sources[].key`。 |
| `categories[].types` | array | 是 | - | 当前分类下的 type 列表。 |

当前代码消费：

1. `page_ai` 消费 `id/name/description/types`。
2. `PageTypeDefinitionCatalog` 消费 `id/name/types` 做 type -> category 映射。
3. `order/deprecated/replaced_by/source_keys` 当前基本未被业务代码消费。

## 7. `types[]` 契约

每个 type 要求：

- `required=[id, name]`
- `additionalProperties=false`

| 路径 | 类型 | 必填 | 约束/枚举 | 说明 |
|---|---|---|---|---|
| `types[].id` | string | 是 | `ID` | 类型 ID。 |
| `types[].name` | string | 是 | `HumanName` | 类型名。 |
| `types[].description` | string | 否 | - | 类型边界说明。 |
| `types[].aliases` | string[] | 否 | unique | 常见标题/别名。 |
| `types[].deprecated` | boolean | 否 | default `false` | type 是否废弃。 |
| `types[].replaced_by` | string | 否 | `ID` | 替代 type。 |
| `types[].source_keys` | string[] | 否 | unique | 引用顶层 `sources[].key`。 |

## 8. 当前代码实际消费矩阵

| 字段 | 主要消费者 | 当前是否已消费 | 用途 |
|---|---|---|---|
| `version/description/last_updated` | catalog 读取 | 弱消费 | 自描述、治理。 |
| `schema_meta.*` | 无主链消费 | 否 | 治理元信息。 |
| `sources.*` | 无主链消费 | 否 | 规范追溯。 |
| `categories[].id/name/description` | `page_ai`、catalog | 是 | 分类 prompt、映射、展示。 |
| `categories[].types` | `page_ai`、catalog | 是 | 类型枚举。 |
| `categories[].order` | 无主链消费 | 否 | 预留展示排序。 |
| `categories[].deprecated/replaced_by/source_keys` | 无主链消费 | 否 | 演进治理。 |
| `types[].id/name` | `page_ai`、catalog、审核页 | 是 | 类型识别、显示、映射。 |
| `types[].description` | `page_ai` | 是 | 分类提示。 |
| `types[].aliases` | `page_ai`、审核页 | 是 | 标题校验、下拉辅助。 |
| `types[].deprecated/replaced_by/source_keys` | 无主链消费 | 否 | 演进治理。 |

## 9. `data` 与 `tree` 的关系约束

schema 本身允许 `tree` 作为 `data` 的轻量子集使用，但团队侧需要额外遵守这些不变量：

1. 同一 namespace 下，`tree` 与 `data` 的 `category.id` / `type.id` 必须同源。
2. `tree` 可以缺少 `schema_meta`、`sources` 等扩展字段，但不能出现 `data` 中不存在的新 type。
3. `page_ai`、审核页选项、类型映射若混用 `tree` 和 `data`，必须保证同一 `type_id` 的 `name/aliases` 不出现冲突。

## 10. 当前 schema 与代码之间的缺口

1. schema 已允许表达很多治理字段，但主链代码当前只吃 `id/name/description/aliases` 这一小部分。
2. 类型级流程门禁（例如某类页面是否必须经过锚点索引）当前不在 schema 中，而在 pipeline/service 里默认写死。
3. 这意味着：未来要把流程策略上移到 schema，最佳落点应在 `types[]`，而不是散落到 service 常量。

## 11. 变更影响矩阵

| 变更位置 | 影响代码 | 风险 |
|---|---|---|
| 根级 required/additionalProperties | `PageTypeDefinitionCatalog` 读取层 | schema 与载荷漂移。 |
| `categories[].id/name` | `page_ai`、type->category 映射 | 分类/展示错误。 |
| `types[].id` | 全链路 | 识别、审核、路由映射断裂。 |
| `types[].name` | 展示、prompt、审核页 | UI 与提示语漂移。 |
| `types[].description` | `page_ai` | 分类质量波动。 |
| `types[].aliases` | `page_ai`、审核页 | 标题兜底与候选展示错误。 |
| `deprecated/replaced_by` | 当前未消费 | 主要影响治理与未来迁移逻辑。 |
| 新增 type 级流程字段 | query/review/pipeline/understanding service | 需要同步改门禁逻辑。 |

## 12. 评审清单

每次改 `page-types.schema.json`、`page-types.data.json` 或 `page-types.tree.json` 前后，都要过这几条：

1. 这是 taxonomy 描述字段，还是运行时流程字段？
2. 若字段会被 prompt 使用，`page_ai` 是否同步评审？
3. 若字段会影响 type -> category 映射，`PageTypeDefinitionCatalog` 相关调用是否同步评审？
4. 若字段会影响理解流水线门禁，是否明确写出要改哪些 service？
5. `tree` 和 `data` 是否仍保持同源 ID 集合？

## 13. 推荐的后续扩展落点

如果团队后续决定把“某 type 是否必须进入锚点流程”提升为 schema 真相，推荐落点是：

- `$defs.Type.properties.<新字段>`

理由：

1. 这是 type 级流程策略，不属于 category 级。
2. 当前所有按 type 判断的代码都以 `type_id` 为中心。
3. 放在 `Type` 上，后续 `query/review/pipeline/understanding` 四条链都能围绕同一字段收敛。

## 14. 状态

- 版本：v1
- 状态：讨论中；本文件先冻结“当前 schema + 当前代码消费”的共同认知，再讨论新增字段

## 15. 当前阶段结论（与试点策略对齐）

本轮以 `TYPE_LAB_REPORT` 做“标签级锚点结构”试点，`page-types` 侧先不引入新流程字段。

### 15.1 本轮不新增的字段

1. 不新增 `types[].anchor_required`。
2. 不新增 `types[].anchor_review_required`。
3. 不新增 type 级锚点窗口、策略版本等字段。

### 15.2 为什么先不动 page-types

1. 当前待验证核心是“标签级锚点定义是否足以承载规则与审核”，该问题属于 `page-semantic`。
   - 包括 `page_window` 统一 object 结构与默认 `mode=within_type_run` 的验证。
2. 若试点有效，再决定是否把 type 级门禁抽到 schema；避免一次引入两层新变量导致归因困难。

### 15.3 回看触发条件

满足以下任一条件，再进入 `page-types` 字段扩展讨论：

1. `TYPE_LAB_REPORT` 试点完成后，出现“同 type 内大量标签无需锚点流程”且现有全局门禁不合适。
2. 多个 type 迁移后，需要在 taxonomy 层表达稳定的流程分流策略。
