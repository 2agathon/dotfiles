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

### 3. 逐单元格读取

1. 必须保留原始 `col_index`
2. 推荐保留 `col_label`
3. 必须保留原始值
4. 若存在显示值与底层值差异，推荐同时保留

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

## 失败信号

以下情况说明本阶段未完成：

1. 无法回溯原始行号
2. 无法知道 workbook 中有哪些 sheet
3. 单元格值被直接替换成推断结果
4. 原始输入与输出之间失去一一回溯关系
