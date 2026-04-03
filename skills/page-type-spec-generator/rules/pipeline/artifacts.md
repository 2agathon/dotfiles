# 产物协议

## 总规则

1. 每个阶段都必须产生对应产物。
2. 同名产物必须覆盖本次运行结果，不得混入上次运行内容。
3. 所有产物都必须可被后续阶段直接读取。
4. 产物中必须保留回溯信息，不得只保留最终结论。
5. 最终 review-ready 产物允许保留统一占位符，但必须显式列入报告。
6. 报告层产物必须忠实反映最终层事实；“看起来更完整”的表述不能覆盖真实 pending、warning 或高风险自动决策。
7. 运行目录中若存在 `tools/`、helper script 或等价程序文件，只能服务 Stage 0-6 的机械步骤；Stage 7-9 不得产出、保存或依赖这类程序文件。

## `run-manifest.json`

### 必含内容

1. `run_id`
2. 运行模式
3. 输入文件列表
4. 是否提供 `page-types.data.json`
5. 是否提供 `page-types.tree.json`
6. 当前选中的 `type`
7. 当前阶段
8. 目标验证层级
9. `stage_history[]`

### 用途

1. 后续阶段读取运行模式
2. 后续阶段读取本次处理范围

### `stage_history[]`

每个元素至少包含：

1. `stage`
2. `status`
3. `outputs`

规则：

1. 每个阶段完成后必须追加一条 checkpoint。
2. 阶段顺序必须单调递增。
3. `outputs` 必须引用该阶段真实落盘产物。

## `workbook.raw.json`

### 必含内容

1. sheet 列表
2. 原始行号
3. 原始列号或列名
4. 原始单元格值
5. `declared_max_row` / `declared_max_column`
6. `effective_max_row` / `effective_max_column`
7. `non_empty_cell_count`
8. `skipped_empty_row_count`

### 用途

1. 为 `workbook.normalized.json` 提供原始来源
2. 供后续审计回看原始输入
3. 证明 Stage 1 采用的是稀疏表示而不是稠密空矩阵

## `workbook.normalized.json`

### 必含内容

1. 规范化后的表头
2. 每行的规范化字段值
3. 行号
4. 表头修复记录
5. 继承填充记录
6. 行级初步分类结果
7. `block_start` 行是否承载首标签的标记
8. 参与 normalize 的有效行集范围

### 用途

1. 为 `identity-map.json` 提供稳定输入
2. 供 `normalization-report.md` 生成摘要
3. 证明 Stage 2 没有在大量空行上继续展开稠密结构

## `normalization-report.md`

### 必含内容

1. 表头修复摘要
2. 继承填充摘要
3. 文本清洗摘要
4. 行分类摘要

### 用途

1. 向用户说明规范化阶段做了哪些自动修复

## `identity-map.json`

### 必含内容

1. namespace
2. category 身份
3. type 身份
4. block 身份
5. tag 身份
6. block 与 tag 的引用关系
7. 空 `tag编码` 行的分类结果
8. 每个身份对象的终态
9. 当前选中 type 的对象边界
10. `block_start` 首标签处理结果
11. `resolved_recovered` 的恢复来源

### 用途

1. 为骨架生成提供唯一身份来源
2. 为身份问题报告提供依据

## `identity-issues.md`

### 必含内容

1. 空 `tag编码` 行处理记录
2. 身份冲突记录
3. 未决身份问题
4. 占位符生成记录
5. 具名空 `tag编码` 行被阻断或占位的原因
6. `block_start` 首标签处理记录

### 用途

1. 向用户暴露身份层的高风险点

## `slot-manifest.json`

### 必含内容

1. 每个槽位所属文件
2. 稳定 `slot_key`
3. 每个槽位的路径
4. 槽位类型
5. 来源规则
6. 来源列与来源行
7. 当前槽位状态
8. 占位符值
9. 是否待语义生成
10. 是否待人工复核
11. `stage_records`

### 用途

1. 作为 `skeleton/` 与 `semantic-draft/` 的真相索引
2. 防止 Stage 7 退化为黑箱整包生成
3. 为 Final Review 输出人工待补清单
4. 为 Final Review 提供 final 视角的真实 pending 列表
5. 为报告诚实性检查提供唯一索引依据

## `semantic-unit-log.json`

### 必含内容

1. `run_id`
2. `selected_type_id`
3. `units[]`

### 用途

1. 证明 Stage 7 是否按单元执行
2. 为 Final Review 的过程合规检查提供证据
3. 为 `slot-manifest.json` 的 Stage 7 回写提供交叉索引
4. 不得被程序化 helper script 事后批量伪造

## `skeleton/`

### 必含内容

1. `page-types.data.json`
2. `page-types.tree.json`
3. `page-semantic-spec.json`
4. 五个 hint 文件骨架

说明：

1. `page-semantic-spec.json.version` 在 review schema 中是可见治理字段，不是阻断必填字段。

### 用途

1. 为 semantic draft 提供结构闭合底座
2. 为人工或 AI 暴露完整可维护槽位

### 约束

1. `skeleton/` 中的内容只承担结构闭合、模板展开和占位显影职责
2. 高自由度语义内容不得在此层定稿
3. 所有按字段规则应显式可见的字段都必须显式出现，不得因“可选”而省略；只有字段规则明确允许无字段时，才可保持无字段

## `semantic-draft/`

### 必含内容

1. `page-types.data.json`
2. `page-types.tree.json`
3. `page-semantic-spec.json`
4. 各 hint 文件

### 用途

1. 作为 review-ready 最终内容的直接上游
2. 为校验和审计提供输入

### 约束

1. `semantic-draft/` 必须从 `skeleton/` 复制派生
2. 若后续要输出正式结果，应从本层派生，而不是跳过本层重生一份
3. Stage 7 的内容生成单位必须是单个顶层 description、单个 type description、单个 block description、单个 tag 字段、单个 hint 章节或单个 block-summary 槽位
4. 每个 unit 都必须先读取目标文件当前内容，再只改当前槽位或章节
5. 允许在同一连续编辑批次内先顺畅处理多个 unit；但该批次完成后，必须立即回写 `slot-manifest.json` 与 `semantic-unit-log.json`
6. hint 文件必须保留 Stage 6 已给出的章节或 block 骨架；不得整文件压缩成一段总说明
7. 脚本可以复制、排队、分发和回写状态；不得批量改写多个同类槽位的内容，更不得直接写业务正文
8. 必须同时产出 `semantic-unit-log.json`，否则不得宣称 Stage 7 已合规完成
9. 运行目录不得包含任何 Stage 7 helper script 或等价程序文件

## `final-review/`

### 必含内容

1. 从 `semantic-draft/` 派生出的完整 review-ready 目录
2. 所有仍残留的显式占位字段
3. 与 `slot-manifest.json` 一致的槽位状态
4. 以 final 视角统计出的人工待补槽位
5. 与 `semantic-unit-log.json` 一致的 Stage 7 执行证据

### 用途

1. 作为最终 review-ready 交付包
2. 作为人工复核直接修改的起点

### 约束

1. 不得绕过 `semantic-draft/` 直接另写一份最终结果
2. 不得包含空字符串 ID
3. 不得包含 `blocked` 对象
4. 不得包含未选中 type 的对象
5. `final-review/` 中的业务文件必须与 `semantic-draft/` 对应文件一致
6. Stage 8 只允许生成 `validation-report.json`、`audit-report.md` 和 final 视角状态记录；不得改写业务文件正文
7. `pending_slots` 必须从 `slot-manifest.json` 的 final 视角完整推导，不得遗漏 `section_path` 槽位
8. 运行目录不得包含任何 Stage 8 helper script 或等价程序文件

## `validation-report.json`

### 必含内容

1. `structure_status`
2. `semantic_status`
3. `review_readiness_status`
4. `blocking`
5. `warnings`
6. `pass`
7. `pending_slots`
8. 最终 `status`
9. `pending_slots` 的统计层级
10. `high_risk_auto_decisions`
11. `stage7_compliance_status`
12. `report_scope`

### 用途

1. 为 `audit-report.md` 提供结构化检查结果
2. 为最终收口提供阻塞信息与人工待补项
3. 明确告诉用户最终层到底还剩什么问题，而不是只给一个 `passed`

### 字段约束

1. `pending_slots_scope` 必须明确写出统计口径，如 `final-review` 或 `final-delivery`。
2. `stage7_compliance_status` 只能表达 Stage 7 过程合规状态，不得被目录结构完整性替代。
3. `report_scope` 必须明确最终报告是否只覆盖 `final-review` / 最终交付层。
4. `pending_slots` 必须完整覆盖 `slot-manifest.json` 中 final 视角的所有 pending 槽位，包括 markdown section。
5. `stage7_compliance_status` 不得仅因 unit 数量非空或 unit 日志存在就写成 `passed`。

## `audit-report.md`

### 必含内容

1. 输入摘要
2. 自动修复摘要
3. 身份问题摘要
4. 结构校验摘要
5. 语义质量摘要
6. 未决问题摘要
7. 占位符摘要
8. 类型污染检查摘要
9. 人工待补清单摘要
10. 首标签缺失检查摘要
11. 空编码伪恢复 ID 检查摘要
12. 报告诚实性检查摘要
13. 高风险自动决策摘要
14. Stage 7 执行证据摘要

### 用途

1. 向用户说明本次转换有哪些风险、默认决策与仍待补项

### 约束

1. `audit-report.md` 可以引用 intermediate 层问题，但必须明确标注其作用域。
2. intermediate-only 的问题不得伪装成 final-review 或最终交付层问题。

## 最终交付目录

### 必含内容

1. `{namespace}/page-types.data.json`
2. `{namespace}/page-types.tree.json`
3. `{namespace}/types/{TYPE_ID}/page-semantic-spec.json`
4. `{namespace}/types/{TYPE_ID}/*.md`

### 用途

1. 作为最终 review-ready 交付结果目录

### 约束

1. 最终交付目录必须从 `final-review/` 派生
2. 不得绕过 `semantic-draft/` 或 `final-review/` 直接另写一份最终结果
3. 不得包含空字符串 ID
4. 不得包含 `blocked` 对象
5. 不得包含未选中 type 的对象
6. 最终交付目录中的业务文件必须与 `final-review/` 对应文件一致
7. Stage 9 只允许复制业务文件并生成 `final-report.md`，不得改写业务文件正文
8. 运行目录不得包含任何 Stage 9 helper script 或等价程序文件

## `final-report.md`

### 必含内容

1. 处理了哪些 `type`
2. 生成了哪些文件
3. 做了哪些自动决策
4. 剩余风险有哪些
5. 仍有哪些显式占位字段
6. 人工还需补哪些槽位
7. validation 的最终状态
8. 高风险自动决策有哪些
9. Stage 7 是否有合规执行证据

### 用途

1. 作为最终对用户的收口说明

### 约束

1. 若最终层仍有 pending、warning 或高风险自动决策，不得写 `none`。
2. `final-report.md` 只允许报告 `final-review/` 与最终交付层中真实存在的问题。
3. 未选中 type 或 intermediate-only 的问题不得写入 `剩余风险`。
4. 中间层问题只能出现在 `audit-report.md`。
