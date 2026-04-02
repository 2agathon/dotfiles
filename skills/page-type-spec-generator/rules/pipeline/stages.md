# 阶段协议

## 总规则

1. 必须按阶段顺序执行。
2. 不得跳过前置阶段直接进入后置阶段。
3. 不得在身份未稳定前生成语义字段。
4. 不得在类型未枚举前询问用户选择类型。
5. 每个阶段完成后，必须产出对应中间结果。
6. `skeleton/`、`semantic-draft/`、`final-review/` 是三个显式阶段结果，不得塌缩成一个黑箱输出。
7. 所有必填字段与业务上可维护的可选字段都必须显式生成；缺值时使用统一占位，而不是物理省略。

## Stage 0：Run Manifest

### 输入

1. 用户提供的输入文件列表
2. 当前运行模式

### 动作

1. 创建本次运行标识
2. 记录输入文件信息
3. 记录当前运行模式
4. 初始化当前阶段、处理范围、目标产物层级

### 输出

1. `run-manifest.json`

### 禁止

1. 未生成 `run-manifest.json` 前进入后续阶段

## Stage 1：Raw Parse

### 输入

1. `run-manifest.json`
2. xlsx 文件
3. `rules/parsing/workbook-parsing.md`

### 动作

1. 读取 workbook 基本结构
2. 读取 sheet
3. 读取原始单元格值
4. 保留原始行号和列号

### 输出

1. `workbook.raw.json`

### 禁止

1. 不得在本阶段修正文义
2. 不得在本阶段判定标签身份
3. 不得在本阶段生成最终 ID

## Stage 2：Normalize

### 输入

1. `workbook.raw.json`
2. `rules/parsing/header-normalization.md`
3. `rules/parsing/row-classification.md`

### 动作

1. 表头映射
2. 空值标准化
3. 继承填充
4. 文本轻清洗
5. 行级初步分类
6. 标记 `block_start` 行是否同时承载首标签定义
7. 记录修复痕迹

### 输出

1. `workbook.normalized.json`
2. `normalization-report.md`

### 禁止

1. 不得在本阶段决定空编码行最终身份
2. 不得在本阶段生成 hint 或语义字段

## Stage 3：Identity Map

### 输入

1. `workbook.normalized.json`
2. `rules/parsing/identity-resolution.md`
3. `rules/parsing/row-classification.md`
4. `rules/parsing/id-normalization.md`
5. `rules/pipeline/state-and-placeholder-policy.md`

### 动作

1. 抽取 namespace
2. 抽取 category
3. 抽取 type
4. 抽取 block
5. 抽取 tag 候选
6. 处理 `block_start` 行上的首标签
7. 建立 block 与 tag 引用关系
8. 处理重复标签去重
9. 处理空 `tag编码` 行分类

### 输出

1. `identity-map.json`
2. `identity-issues.md`

### 禁止

1. 不得在身份未稳定前生成 `value_hint`
2. 不得在身份未稳定前生成 `context_hint`
3. 不得在身份未稳定前生成 `anchor_binding`
4. 若存在 `blocked` 或空 canonical id，不得进入后续阶段
5. 不得把空编码具名 tag 伪恢复成 `TAG_U...` 一类正式 id

## Stage 4：Type Selection

### 输入

1. `identity-map.json`
2. `run-manifest.json`
3. `rules/pipeline/interaction-points.md`

### 动作

1. 枚举检测到的 `type`
2. 在允许交互的模式下询问用户要处理哪些 `type`
3. 在不允许交互的模式下记录默认决策

### 输出

1. 更新后的 `run-manifest.json`

### 禁止

1. 不得在类型枚举前询问用户选 type
2. 不得在可交互模式下默认处理全部 type

## Stage 5：Existence Check

### 输入

1. `run-manifest.json`
2. 用户提供的 `page-types.data.json`
3. 用户提供的 `page-types.tree.json`

### 动作

1. 检查已有 type 是否存在
2. 检查 category 是否存在
3. 决定追加、跳过或新建
4. 记录 review-ready 与 publish-ready 的校验目标

### 输出

1. `existence-check.json`
2. 更新后的 `run-manifest.json`

### 禁止

1. 不得只更新 `data.json` 不更新 `tree.json`

## Stage 6：Skeleton

### 输入

1. `identity-map.json`
2. `run-manifest.json`
3. `rules/pipeline/artifacts.md`
4. `rules/pipeline/state-and-placeholder-policy.md`
5. `rules/pipeline/slot-manifest-contract.md`

### 动作

1. 生成 taxonomy 骨架
2. 生成 `page-semantic-spec.json` 骨架
3. 生成五个 hint 文件骨架
4. 生成 `slot-manifest.json`
5. 为所有必填字段与业务上可维护的可选字段显式落槽
6. 将每个槽位标记为：机械转移值、模板展开值或统一占位值
7. 若某个 block 的首标签来自 `block_start` 行，必须在骨架中显式落槽

### 输出

1. `skeleton/`
2. `slot-manifest.json`

### 禁止

1. 不得在本阶段生成润色后的自然语言成品
2. 不得绕过 `identity-map` 临场新增根级标签
3. `skeleton/` 不得反向改写 `identity-map` 中已确定的身份结果
4. 不得因为字段可选就省略槽位
5. 不得把占位内容伪装成最终语义结果

## Stage 7：Semantic Draft

### 输入

1. `skeleton/`
2. `slot-manifest.json`
3. `identity-map.json`
4. 各字段和 hint 对应的 `rules/fields/*` 与 `rules/hints/*`

### 动作

1. 复制 `skeleton/` 到 `semantic-draft/`
2. 生成待处理槽位或文件清单
3. 按单个 block 逐项语义化 `block_types[].description`
4. 按单个 tag 逐项语义化 `tags[].value_hint`
5. 按单个 tag 逐项语义化 `tags[].context_hint`
6. 按单个 tag 解析并补全 `tags[].anchor_binding`
7. 按单个 hint 文件逐项语义化各 hint 文件
8. 回写槽位状态

### 输出

1. `semantic-draft/`
2. 更新后的 `slot-manifest.json`

### 禁止

1. 不得重写 tag / block 身份
2. 不得读取未在字段来源矩阵中指定的规则文件
3. 若 `identity-map.json` 与 `skeleton/` 出现冲突，必须以 `identity-map.json` 为准
4. 不得新增字段
5. 不得删除骨架阶段已显式生成的字段
6. 不得整包黑箱生成整份最终文件
7. 不得一次性批量替换多个 `value_hint`
8. 不得一次性批量替换多个 `context_hint`
9. 不得一次性批量替换多个 block description
10. 不得用单个脚本步骤整包生成多个 hint 文件内容
11. 脚本只允许复制、排队、分发单元任务与回写状态，不得跨多个槽位直接生成内容

## Stage 8：Final Review

### 输入

1. `skeleton/`
2. `semantic-draft/`
3. `slot-manifest.json`
4. `schema/review/page-semantic.schema.json`
5. `schema/review/page-types.schema.json`
6. `rules/pipeline/validation-checklist.md`
7. `rules/pipeline/state-and-placeholder-policy.md`

### 动作

1. 结构校验
2. 引用闭合检查
3. 骨架与语义草稿的槽位对比
4. 占位残留检查
5. 模板化残留检查
6. 首标签缺失检查
7. 空编码伪恢复 ID 检查
8. 以 `final-review/` 视角生成问题清单与人工待补清单
9. 从 `semantic-draft/` 派生 `final-review/`

### 输出

1. `final-review/`
2. `validation-report.json`
3. `audit-report.md`

### 禁止

1. 不得在本阶段继续补写正式内容
2. 不得删除占位符来假装完成
3. 不得把“结构通过”写成“质量通过”
4. 不得用 `skeleton/` 视角替代 `final-review/` 视角统计待补项

## Stage 9：Final Handoff

### 输入

1. `final-review/`
2. `validation-report.json`
3. `audit-report.md`
4. `rules/pipeline/artifacts.md`
5. `rules/pipeline/state-and-placeholder-policy.md`

### 动作

1. 输出最终结果目录
2. 输出最终摘要
3. 列出自动决策、剩余风险、占位残留与人工待补项

### 输出

1. 最终交付目录
2. `final-report.md`

### 禁止

1. 不得隐藏自动决策
2. 不得隐藏剩余风险
3. 不得隐藏仍残留的占位字段
4. 若 `validation-report.json` 存在 blocking，不得宣称转换完成
