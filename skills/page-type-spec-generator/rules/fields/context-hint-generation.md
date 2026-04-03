# context_hint 生成规则

## 目标对象

生成 `tags[].context_hint`。

## 输入

1. `tag定义`
2. `正例`
3. `反例`
4. 当前 tag 在当前 type 中的 block 集合
5. 若当前 tag 只属于一个 block，可参考该 block 的语义说明
6. 当前 tag 的 `value_hint`

## Stage 6：Skeleton

1. 必须显式生成 `context_hint` 字段。
2. 默认值为 `__PTSG_PENDING__`。
3. 不得因为“看起来不需要”就把字段省略掉。

## Stage 7：Semantic Draft

1. 只有在不补 `tag_context` 会导致断言歧义时，才生成内容；否则输出空字符串 `""`。
2. 只允许补以下四类缺口：
   1. 所指对象
   2. 语义角色
   3. 成立方式
   4. 成立边界
3. 若当前 tag 在多个 block 中复用，生成内容时必须保持根级 tag 视角，不得绑定单一 block 语义。
4. 只有当当前 tag 稳定只属于一个 block 时，才可弱参考该 block 的语义说明。
5. 输出一个短句、两句以内短提示或空字符串。
6. 若明显存在专属缺口，但当前无法安全确定，可保留 `__PTSG_PENDING__` 进入人工确认。

## 禁止

1. 不得写成同义反复。
2. 不得重复 `value_hint` 里已经说明的取值边界。
3. 不得写来源位置、判读依据、OCR 过程、锚点规则、组装说明。
4. 不得因为字段显式存在，就强行写一条没有信息量的泛句。
5. 不得把抽象短句当成大量标签的默认主句。
6. 不得把某个 block 的局部语义写成根级 tag 的默认 `context_hint`。
7. 对无额外语义缺口的 tag，不得保留 `__PTSG_PENDING__` 或强造泛句；应输出空字符串。

## 失败信号

1. Skeleton 阶段缺少 `context_hint` 字段。
2. Semantic Draft 在无歧义时仍写长句。
3. 最终 `context_hint` 主要是在重复 tag 名称或 block 名称。
4. 最终文本写入了锚点、定位、组装或判读过程。
5. 多个不相关 tag 共享完全相同的 `context_hint` 主句。
6. 大量 `context_hint` 仅由抽象短句构成，没有 tag 专属差异。
7. 一个会在多个 block 中复用的 tag，被写成单一 block 视角的 `context_hint`。
8. 明显不需要额外 `context_hint` 的 tag 仍保留 `__PTSG_PENDING__`。
