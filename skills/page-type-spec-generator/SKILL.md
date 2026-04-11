---
name: page-type-spec-generator
description: >
  从业务 xlsx 设计稿生成页类型配置文件。
  触发：用户提供 xlsx 并要求生成 spec、转成配置、新建或维护页类型。
metadata:
  collection: 2agathon-dotfiles
  layer: 领域专项
  domain: page-type-spec-from-xlsx
  invocation: user-request
---

# page-type-spec-generator

## 目标

把输入 xlsx 转换为一套 review-ready 的完整规格包：

1. 中间产物
2. `skeleton/`
3. `semantic-draft/`
4. `final-review/`
5. `page-types.data.json`
6. `page-types.tree.json`
7. `types/{TYPE_ID}/page-semantic-spec.json`
8. 各类 hint 文件
9. `slot-manifest.json`

## 默认读取范围

只允许读取：

1. `rules/`
2. `schema/`

路径约束：

1. 本 skill 中出现的 `rules/` 与 `schema/`，都指当前 skill 目录下的相对路径。
2. 必须在 `skills/page-type-spec-generator/rules/` 与 `skills/page-type-spec-generator/schema/` 下读取。
3. 不得去当前工作目录、项目根目录或其他同名目录下寻找 `rules/` 或 `schema/`。

默认不读取：

1. `refs/`（即使它位于当前 skill 根目录下，也只可作为存档参考，不得作为默认执行输入或执行入口）

## 执行入口

开始执行时，按以下顺序读取：

说明：以下路径均相对当前 skill 目录解析。

1. `rules/field-source-matrix.md`
2. `rules/pipeline/stages.md`
3. `rules/pipeline/artifacts.md`
4. `rules/pipeline/interaction-points.md`
5. `rules/pipeline/validation-checklist.md`
6. `rules/pipeline/state-and-placeholder-policy.md`
7. `rules/pipeline/slot-manifest-contract.md`
8. `rules/pipeline/stage7-unit-log-contract.md`

## 执行规则

1. 必须按 `rules/pipeline/stages.md` 的阶段顺序执行。
2. 必须按 `rules/field-source-matrix.md` 限制每个对象可读取的规则文件。
3. 生成内容时只使用 `rules/*`。
4. 结构校验时只使用 `schema/*`。
5. 若某对象无法仅凭指定 `rules/*` 生成，停止扩展读取范围，改为记录问题并等待补 rule。
6. 若任一必填 ID 为空或任一对象进入 `blocked`，必须停止后续阶段。
7. 若当前选中 type 之外的对象混入结果，必须视为失败。
8. review-ready 结果必须显式保留所有必填字段与按字段规则要求显式可见的可选字段；不得靠物理省略隐藏缺口。只有字段规则明确允许无字段时，才可保持无字段。
9. 当流程闭环与 skill 边界冲突时，优先守边界；宁可输出带 pending 的 review-ready 结果，也不得扩大解释、伪恢复或伪通过。
10. 当规则存在解释空间时，默认选择更保守路径：`resolved_placeholder`、`pending_human`、`blocked` 或显式风险暴露，而不是直接放行。
11. 每个 stage 都必须先落盘当前阶段产物并留下 checkpoint，再允许进入下一阶段。
12. 除非 `rules/pipeline/interaction-points.md` 明确要求交互、需要用户选择 `type`、遇到 blocking、或规则缺口/风险需要用户决策，否则不得逐 stage 向用户索要继续执行许可。
13. 默认应在当前 stage 产物真实落盘后，直接进入下一 stage；“等待用户再次同意”不是默认流程控制方式。
14. Stage 1 与 Stage 2 必须使用稀疏表示。不得把工作表声明范围中的海量空行、空列、空单元格按稠密矩阵逐个落入 JSON。
15. 一旦用户已完成必要决策（例如选定 `type`），后续默认连续推进；不得在 Stage 7 中逐 block、逐 tag、逐 hint 文件反复询问“是否继续”。

## 不可协商执行方式

1. 必须一步一步做。一次只能执行一个 stage，不得一口气把 Stage 0-9 全部跑完。
2. 当前 stage 的产物未落盘、`run-manifest.json` 未写入 checkpoint 前，不得进入下一 stage。
3. 严禁编写、运行或依赖任何覆盖多个 stage 的统一总控脚本、`run_all` 脚本、`pipeline.py`、`main.py` 或等价入口。即使它会顺序写出中间目录，也视为违规。
4. 严禁以内存中直接传递跨阶段对象来绕过阶段产物落盘。
5. 下一 stage 的唯一合法输入来源，是前一 stage 已落盘产物、当前允许读取的 `rules/*` 与 `schema/*`。不得使用“脚本里还留着上一步对象”“函数返回值继续传下去”“内存缓存对象继续加工”等方式替代阶段输入。
6. Stage 7 开始时，必须先复制 `skeleton/` 到 `semantic-draft/`。此后只允许在 `semantic-draft/` 上逐单元处理。
7. Stage 7 的单次内容生成只能服务一个 unit。unit 只允许是：
   1. 一个 `page-types.data.json` 或 `page-types.tree.json` 的 `$.description`
   2. 一个 `types[].description`
   3. 一个 `block_types[].description`
   4. 一个 `tags[].value_hint`
   5. 一个 `tags[].context_hint`
   6. 一个 `tags[].anchor_binding`
   7. 一个 hint 单章节
   8. 一个 `block-summary-hint.md` 中的单个 block 槽位
8. 严禁脚本或单次模型调用直接批量生成、批量替换或批量润色多个 `value_hint`、多个 `context_hint`、多个 block description、多个 hint 章节或多个 block-summary 槽位内容。
9. Stage 7 处理每个 unit 时，必须先读取目标文件当前内容，只改当前槽位或章节。直接执行时允许连续处理多个 unit，不必逐 unit 向用户汇报；已完成 unit 的 `slot-manifest.json` 与 `semantic-unit-log.json` 最迟必须在当前连续编辑批次结束、离开 Stage 7、向用户汇报、或遇到 blocking 前诚实回写。
10. Stage 7 的语义内容应直接改写 `semantic-draft/` 中对应文件，像逐处写代码一样逐单元修改；不要为了省事把 prose 生成再外包给脚本模板替换。
11. Stage 7 中，脚本只允许做：复制、排队、分发单元任务、回写 `slot-manifest.json`、回写 `semantic-unit-log.json`。脚本不得直接写业务正文。
12. `semantic-unit-log.json` 是 Stage 7 合规证据。没有逐单元日志，就视为 Stage 7 不合规。
13. `slot-manifest.json` 与 `semantic-unit-log.json` 只能记录真实发生的处理，不得把模板态、占位态或未处理对象记成已完成，不得在整文件改完后批量倒填执行证据。
14. Stage 7、Stage 8、Stage 9 不是要编写程序去执行的阶段，而是要直接执行的阶段。严禁为这三个阶段编写、保存、运行或依赖 `stage7_*`、`stage8_*`、`stage9_*`、`semantic_draft.py`、`final_review.py`、`final_handoff.py`、`tools/stage7_*`、`tools/stage8_*`、`tools/stage9_*` 或等价 helper script。
15. 不得把“禁止脚本写正文”误解成逐 unit 向用户询问是否继续；一旦必要决策已经完成，Stage 7-9 默认必须连续推进，直到遇到 blocking、规则缺口、真实歧义或用户决策点。
16. 不得把阶段内进度播报包装成“如果你要，我继续”式伪交互；对默认应继续的 Stage 7-9，不得用进度消息重新向用户索要继续许可。
17. `final-review` 只做检查、派生、报告。严禁在 `final-review` 阶段继续生成、润色、补写任何业务内容；`final-review/` 中的业务文件必须与 `semantic-draft/` 对应文件一致。
18. `final-delivery` 只允许从 `final-review/` 复制派生；不得在 Stage 9 再改业务正文。
19. 若你发现自己想“先跑通再回头修”，立即停止；这属于违规倾向，不得继续推进。
20. 若你不能证明某动作被允许，默认禁止，停在当前阶段并显式记录问题。

## 阶段调度

### Stage 0-3

按 `rules/pipeline/stages.md` 执行：

1. `run-manifest`
2. `raw parse`
3. `normalize`
4. `identity map`

要求：

1. 身份未稳定前，不得生成语义字段。
2. 空 `tag编码` 行必须进入身份解析流程，不得静默丢弃。
3. 任一 canonical id 为空时，视为 Stage 3 失败。
4. `block_start` 行若同时承载首标签定义，必须进入 tag 身份解析，不得只建 block 不建 tag。

### Stage 4-5

执行：

1. `type selection`
2. `existence check`

要求：

1. 交互行为服从 `rules/pipeline/interaction-points.md`。
2. 不得在类型枚举前询问用户选择 `type`。

### Stage 6-7

执行：

1. `skeleton`
2. `semantic draft`

要求：

1. `identity-map.json` 是身份真相。
2. `skeleton/` 负责结构闭合、模板展开和占位显影，不负责最终 prose。
3. 若 `identity-map.json` 与 `skeleton/` 冲突，必须以 `identity-map.json` 为准。
4. 生成字段时，只读取该字段在 `field-source-matrix.md` 中指定的 rule。
5. Stage 7 只允许在骨架既有槽位上逐项语义化，不得混入其他 type。
6. Stage 7 的生成单位只允许是：单个顶层 description、单个 type description、单个 block description、单个 tag 字段、单个 hint 章节或单个 block-summary 槽位。
7. Stage 7 脚本只允许复制、排队、分发单元任务与回写状态；不得一次生成多个同类槽位内容。
8. 不得因为想尽快形成一套完整产物，就把 Stage 7 解释成“允许批量生成 prose”。
9. 若无法提供逐单元执行证据，不得宣称 Stage 7 合规。
10. Stage 7 不是“给人工留待处理”的形式性过场，而是必须真实完成语义裁决的阶段。对于进入 Stage 7 的 unit，必须逐个给出实际结果：`materialized`、`pending_human`、`missing_required_source`、`optional_visible_empty` 或 `blocked`。
11. 严禁用“整体保留 Stage 6 输出供人工复核”“conservative pass”“先不改语义”之类理由，把所有或大部分 Stage 7 unit 统一标记为 skip。
12. 只要某个槽位被标记为 `needs_semantic_generation=true`，Stage 7 就必须真实处理它；不允许以复制 `skeleton/` 后原样保留模板文本来替代 Stage 7 语义化职责。
13. Stage 7 进入后，默认连续处理所有 unit；除非遇到 blocking、规则缺口、真实歧义或必须由用户决策的风险，不得逐 unit 打断用户。
14. Stage 7 不得先在内存或脚本中整包生成整份 `semantic-draft/`，再事后按 path 回填 unit 记录。

### Stage 8-9

执行：

1. `final review`
2. `final handoff`

要求：

1. 校验只负责检查，不负责继续补写正式内容。
2. `final-review/` 必须从 `semantic-draft/` 派生。
3. 最终交付目录必须从 `final-review/` 派生。
4. 不得绕过 `semantic-draft/` 或 `final-review/` 另写一份最终结果。
5. 只要存在 blocking，不得输出正式最终结果。
6. 最终层存在显式占位、模板残留或高风险自动决策时，不得报“无风险”或“无待补项”。
7. `final-review` 与 `final-report` 只能对最终层和当前选中 type 负责；中间层问题不得伪装成最终层风险。
8. Stage 8 与 Stage 9 只允许派生目录、生成报告和回写审计状态；不得改写业务文件正文。

## 字段与 hint 路由

### 字段生成

1. `page-types.data.json` / `page-types.tree.json` 顶层字段 -> `rules/fields/page-types-top-level-generation.md`
2. `types[].description` -> `rules/fields/type-description-generation.md`
3. `types[].aliases` -> `rules/fields/type-aliases-generation.md`
4. `action_paths[]` -> `rules/fields/action-paths-generation.md`
5. `block_types[].description` -> `rules/fields/block-description-generation.md`
6. `block_types[].answerable_question` -> `rules/fields/block-answerable-question-generation.md`
7. `tags[].value_hint` -> `rules/fields/value-hint-generation.md`
8. `tags[].context_hint` -> `rules/fields/context-hint-generation.md`
9. `tags[].anchor_binding` -> `rules/fields/anchor-binding-parsing.md`

### hint 生成

1. `tagging-hint.md` -> `rules/hints/tagging-hint-generation.md`
2. `assembly-hint.md` -> `rules/hints/assembly-hint-generation.md`
3. `block-summary-hint.md` -> `rules/hints/block-summary-hint-generation.md`
4. `page-summary-hint.md` -> `rules/hints/page-summary-hint-generation.md`
5. `continuation-hint.md` -> `rules/hints/continuation-hint-generation.md`

## 硬约束

1. 不得阶段倒置。
2. 不得读取未授权材料补足生成内容。
3. 不得把结构校验材料当成生成依据。
4. 不得把人类说明文档当成默认执行输入。
5. 不得隐藏自动决策和剩余风险。
6. 不得用规则外私有模板替代字段生成规则。
7. 允许使用脚本执行单阶段的机械工作；禁止使用单个黑箱脚本跨越多个阶段并直接产出最终结果。
8. 脚本只处理当前阶段允许处理的对象，并真实产出该阶段规定的中间结果。
9. 遇到 blocking 条件时，脚本必须停止，不得继续生成 final。
10. 不得用泛化模板句批量替代字段或 hint 的专属规则执行。
11. 不得在 Stage 7 删除 Stage 6 已显式生成的字段或文件。
12. 不得把空编码具名 tag 伪恢复成 `TAG_U...` 一类正式 id；无显式恢复源时必须走 placeholder 或 blocked。
13. Final Review 的待补项必须以 `final-review/` 或最终交付层为准，不得只引用 `skeleton/`。
14. 不得把既有输出、既有报告、既有生成脚本当作这次生成内容的默认依据；它们只可作为反例、审计证据或回归样本。
15. 不得因为想减少 pending / blocked，就扩大 `resolved_recovered` 的适用范围。
16. 不得在最终报告中用 `none`、`passed`、`无额外风险` 掩盖最终层仍可见的 pending、warning 或高风险自动决策。
17. 不得把“目录分层存在”“保留 pending”“报告诚实”当作 Stage 7 过程合规的替代证据。
18. 不得编写、运行或依赖覆盖多个 stage 的统一总控脚本、`run_all` 式脚本或等价入口；即使它会顺序落下中间目录，也不视为合规。
19. 不得以内存中直接传递跨阶段对象绕过阶段产物落盘与 checkpoint。
20. 严禁把 `worksheet.max_row * max_column` 的 declared range 直接当成 raw/normalized 的落盘范围；必须只围绕有效非空单元格和有效行集落盘。
21. 严禁为了“完整可回溯”把数十万到数百万个 `null` 单元格逐个写入 `workbook.raw.json` 或 `workbook.normalized.json`。
22. 严禁以“已经复制到 semantic-draft/”或“已经生成 semantic-unit-log.json”作为 Stage 7 已完成的替代证据；真正的证据只能是逐 unit 的语义处理结果。
23. 严禁在 Stage 7 中把多章节 hint 文件或多 block 槽位文件压缩成一段总说明，以此替代逐章节 / 逐槽位语义化。
24. 严禁在 Stage 8 / Stage 9 通过脚本继续改写 `page-types.data.json`、`page-types.tree.json`、`page-semantic-spec.json` 或 hint 文件正文。
25. 严禁把当前 skill 编译成一个会自我执行、自我验收、自我出报告的 Stage 7-9 程序系统；这类 helper script 体系一律视为越界实现。

## 输出要求

最终必须输出：

1. 中间产物目录
2. `skeleton/`
3. `semantic-draft/`
4. `final-review/`
5. 最终交付目录
6. `slot-manifest.json`
7. `semantic-unit-log.json`
8. `validation-report.json`
9. `audit-report.md`
10. `final-report.md`
