# workbook 解析规则

## 目标

把输入 xlsx 读取为 `workbook.raw.json`。

本阶段只负责读取原始内容，不负责解释语义。

## 输入

1. xlsx 文件
2. `run-manifest.json`

## 输出

1. `workbook.raw.json`

## 必须读取的内容

1. workbook 路径
2. sheet 列表
3. 每个 sheet 的原始行号
4. 每行的原始列号或列标签
5. 每个单元格的原始值

## 推荐保留的内容

1. 合并单元格信息
2. 隐藏行信息
3. 公式显示值
4. 原始 sheet 顺序

## 读取规则

### 1. 逐 sheet 读取

1. 必须保留 sheet 名称
2. 必须保留 sheet 顺序

### 2. 逐行读取

1. 必须保留原始 `row_index`
2. 空行可以跳过，但若跳过，必须保证后续仍能回溯原始行号
3. 必须区分 `declared_max_row` 与 `effective_max_row`
4. 只要一行在当前 stage 没有任何非空单元格，就不得把该行展开为一个带全 `null` cells 的稠密行对象

### 3. 逐单元格读取

1. 必须保留原始 `col_index`
2. 推荐保留 `col_label`
3. 必须保留原始值
4. 若存在显示值与底层值差异，推荐同时保留
5. 默认只记录非空单元格；不得为每个空单元格显式写出 `raw_value: null`

### 4. 稀疏表示

1. `workbook.raw.json` 必须使用稀疏表示。
2. 必须同时记录：
   1. `declared_max_row`
   2. `declared_max_column`
   3. `effective_max_row`
   4. `effective_max_column`
   5. `non_empty_cell_count`
   6. `skipped_empty_row_count`
3. 若 sheet 存在巨大 declared range 但有效数据很少，必须只保留有效行和非空 cell。
4. 不得因为“Excel 认为这些行列已使用”就把空白区域全部序列化进 JSON。

## `workbook.raw.json` 最小结构

```json
{
  "workbook": {
    "path": "string",
    "sheet_names": ["Sheet1"]
  },
  "sheets": [
    {
      "name": "Sheet1",
      "declared_max_row": 1000,
      "declared_max_column": 30,
      "effective_max_row": 120,
      "effective_max_column": 28,
      "non_empty_cell_count": 650,
      "skipped_empty_row_count": 880,
      "rows": [
        {
          "row_index": 1,
          "cells": [
            {
              "col_index": 1,
              "col_label": "A",
              "raw_value": "string or null"
            }
          ]
        }
      ]
    }
  ]
}
```

## 禁止

1. 不得在本阶段修正文义
2. 不得在本阶段修正表头
3. 不得在本阶段继承填充空值
4. 不得在本阶段判定 block / tag / type 身份
5. 不得在本阶段生成最终 ID
6. 不得把 declared range 中的空白单元格批量展开成稠密 JSON 矩阵

## 失败信号

以下情况说明本阶段未完成：

1. 无法回溯原始行号
2. 无法知道 workbook 中有哪些 sheet
3. 单元格值被直接替换成推断结果
4. 原始输入与输出之间失去一一回溯关系
5. `workbook.raw.json` 的主体由大量 `null` 单元格构成，而不是稀疏非空 cell 集合
