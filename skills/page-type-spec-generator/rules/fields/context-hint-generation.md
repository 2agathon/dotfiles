# context_hint 生成规则

## 目标

从 xlsx 输入生成 `tags[].context_hint`。

`context_hint` 会直接进入段打标 prompt，被以下模块消费：

1. `src/module/material/ai/segment_ai.py`
2. `src/module/material/ai/common.py`
3. `src/module/material/ai/prompts.py` 中的段打标 prompt

它的职责很窄：只告诉模型当前 tag 的 `tag_context` 还需要补哪些最小语义缺口。

## 输入

1. `tag定义`
2. `正例`
3. `反例`
4. 当前 tag 所属 block 名称
5. 当前 tag 所属 block 的语义说明
6. 当前 tag 的 `value_hint`

## 总规则

1. Skeleton 阶段必须显式生成 `context_hint` 槽位。
2. Semantic Draft 阶段才允许判断是否真的需要写 `context_hint` 内容。
3. `context_hint` 只补当前 tag 专属的歧义轴，不重复系统 prompt 已经定义的 `tag_context` 总规则。
4. `context_hint` 不解释为什么命中，不写定位，不写锚点，不写组装。

## Stage 6：Skeleton

1. 必须显式生成 `context_hint` 字段。
2. 默认值为 `__PTSG_PENDING__`。
3. 不得因为“看起来不需要”就把字段省略掉。

## Stage 7：Semantic Draft

### 目标形态

1. 一个短句或两句以内的短提示。
2. 只覆盖真实存在的语义缺口。
3. 若暂时无法安全确定专属缺口，可保留 `__PTSG_PENDING__` 进入人工确认。

### 判断步骤

#### Step 1：先看 `value_hint` 是否已经足够自说明

1. 若 `(tag_id, tag_value)` 与 `value_hint` 组合后已经能独立成立，一般不需要再补充长句。
2. 仅当不补 `tag_context` 会导致断言歧义时，才生成 `context_hint`。

#### Step 2：逐轴判断是否需要补足

只允许判断以下四类缺口：

1. 所指对象
2. 语义角色
3. 成立方式
4. 成立边界

#### Step 3：写最小补充语义

优先写成以下形式之一：

1. `说明该值对应的对象或条目。`
2. `写明该值表示当前、既往、拟定或否定状态。`
3. `区分该值所指的项目、检查项或诊断角色。`
4. `补充该值成立的时间点、范围或条件。`

## 写法要求

1. 结果应像给模型的短提示，不像给人的解释文。
2. 只写该 tag 特有的歧义，不要把 block 总语义抄进来。
3. 如果所有 tag 都能套用同一句，说明写错了。

## 禁止

1. 不得写成“限定为 X 中与 Y 直接对应的表述”这种同义反复。
2. 不得重复 `value_hint` 里已经说明的取值边界。
3. 不得写来源位置、判读依据、OCR 过程、锚点规则、组装说明。
4. 不得因为字段显式存在，就强行写一条没有信息量的泛句。

## 失败信号

1. Skeleton 阶段缺少 `context_hint` 字段。
2. Semantic Draft 在无歧义时仍写长句。
3. 最终 `context_hint` 主要是在重复 tag 名称或 block 名称。
4. 最终文本写入了锚点、定位、组装或判读过程。
