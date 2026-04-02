# type description 生成规则

## 目标

生成 `page-types.data.json` 与 `page-types.tree.json` 中的 `types[].description`。

这个字段会被页分类 prompt 直接读取，主要服务于：

1. `src/module/material/ai/page_ai.py`
2. `src/module/material/ai/common.py` 中的 `_build_type_descriptions`

因此它不是普通介绍文，而是页分类的核心识别信号。

## 必须覆盖的信息

1. 这是什么文书
2. 典型内容或外观特征是什么
3. 与最容易混淆的相邻类型如何区分

## 输入

1. `type_name`
2. `category_name`
3. 当前 type 的 block 名称集合
4. 与相邻 type 的已知边界信息

## Stage 6：Skeleton

输出固定模板：

```text
类型名：{type_name}
所属分类：{category_name}
典型块：{block_names_joined 或 __PTSG_PENDING__}
识别边界：__PTSG_PENDING__
```

## Stage 7：Semantic Draft

### 目标形态

1. 1-3 句自然语言。
2. 第一句定义文书类型。
3. 第二句补典型信号。
4. 第三句只在必要时写相邻边界。

### 写法要求

1. 尽量让页分类模型能用这段文字把它和近邻类型区分开。
2. 典型块列表需要转成有解释力的内容特征，不是简单逗号串。
3. 优先写“结构化编码表 / 叙事性病程记录 / 检查结果单 / 诊疗计划页”这类识别强信号。
4. 描述对象必须是原始业务文书本身，不得把“页面语义规格 / parser / review-ready 产物”写成类型定义。

## 禁止

1. 不得输出 `Generated from workbook type ...` 一类弱模板句。
2. 不得只写“这是一个 X 文书”，没有任何边界。
3. 不得把所有 block 名字原样拼成最终 description。
4. 不得写成“用于承接页面语义规格”“用于当前转换流程”这类描述生成产物而非原始文书的句子。

## 失败信号

1. 最终仍是骨架模板句。
2. 完全缺少近邻区分点。
3. 对页分类模型没有识别价值，只剩泛泛介绍。
