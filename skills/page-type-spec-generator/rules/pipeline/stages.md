# 阶段协议

## 总规则

1. 必须按阶段顺序执行。
2. 不得跳过前置阶段直接进入后置阶段。
3. 不得在身份未稳定前生成语义字段。
4. 不得在类型未枚举前询问用户选择类型。
5. 每个阶段完成后，必须产出对应中间结果。

## Stage 0：Run Manifest

### 输入

1. 用户提供的输入文件列表
2. 当前运行模式

### 动作

1. 创建本次运行标识
2. 记录输入文件信息
3. 记录当前运行模式

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
6. 记录修复痕迹

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

### 动作

1. 抽取 namespace
2. 抽取 category
3. 抽取 type
4. 抽取 block
5. 抽取 tag 候选
6. 建立 block 与 tag 引用关系
7. 处理重复标签去重
8. 处理空 `tag编码` 行分类

### 输出

1. `identity-map.json`
2. `identity-issues.md`

### 禁止

1. 不得在身份未稳定前生成 `value_hint`
2. 不得在身份未稳定前生成 `context_hint`
3. 不得在身份未稳定前生成 `anchor_binding`

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

### 输出

1. 存在性检查结果

### 禁止

1. 不得只更新 `data.json` 不更新 `tree.json`

## Stage 6：Skeleton

### 输入

1. `identity-map.json`
2. `run-manifest.json`
3. `rules/pipeline/artifacts.md`

### 动作

1. 生成 taxonomy 骨架
2. 生成 `page-semantic-spec.json` 骨架
3. 生成空 hint 模板

### 输出

1. `skeleton/`

### 禁止

1. 不得在本阶段生成高自由度语义字段
2. 不得绕过 `identity-map` 临场新增根级标签
3. `skeleton/` 不得反向改写 `identity-map` 中已确定的身份结果

## Stage 7：Semantic Draft

### 输入

1. `skeleton/`
2. `identity-map.json`
3. 各字段和 hint 对应的 `rules/fields/*` 与 `rules/hints/*`

### 动作

1. 生成 `block_types[].description`
2. 生成 `tags[].value_hint`
3. 生成 `tags[].context_hint`
4. 生成 `tags[].anchor_binding`
5. 生成各 hint 文件

### 输出

1. `semantic-draft/`

### 禁止

1. 不得重写 tag / block 身份
2. 不得读取未在字段来源矩阵中指定的规则文件
3. 若 `identity-map.json` 与 `skeleton/` 出现冲突，必须以 `identity-map.json` 为准

## Stage 8：Validation

### 输入

1. `semantic-draft/`
2. `schema/page-semantic.schema.json`
3. `schema/page-types.schema.json`
4. `rules/pipeline/validation-checklist.md`

### 动作

1. 结构校验
2. 引用闭合检查
3. 中间结果完整性检查
4. 生成问题清单

### 输出

1. `validation-report.json`
2. `audit-report.md`

### 禁止

1. 不得在本阶段继续补写正式内容

## Stage 9：Final Handoff

### 输入

1. `semantic-draft/`
2. `validation-report.json`
3. `audit-report.md`
4. `rules/pipeline/artifacts.md`

### 动作

1. 输出最终结果目录
2. 输出最终摘要
3. 列出自动决策与剩余风险

### 输出

1. 最终交付目录
2. `final-report.md`

### 禁止

1. 不得隐藏自动决策
2. 不得隐藏剩余风险
