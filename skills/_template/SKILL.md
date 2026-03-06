---
name: template
description: Use this as a starting point when creating a new skill. Copy this file to the new skill directory and fill in the fields.
---

## 这个 skill 做什么

[一句话说清楚这个 skill 的职责]

## 触发判断

以下情况触发：
- [场景一]
- [场景二]

## 信息收集

在执行之前，先走一遍信息盘点：

**我需要什么信息**
- [执行这个 skill 必须知道的信息]

**信息从哪里来**
- 你提供 → [什么情况下你来提供]
- 读文件 → [什么文件可以推断出需要的信息]
- 从对话提取 → [什么情况下可以从当前对话里提取]

**信息缺口怎么处理**
- 缺关键信息 → 只问最影响方向的一个问题，不列问题清单
- 可以推断的 → 用 [ASSUMPTION: 推断内容] 标注，继续推进
- 无法推断的 → 用 [OPEN QUESTION: 具体问题] 标注，生成占位内容

## 核心内容

[skill 的主要内容放这里]
[形式由知识本质决定——规则、示例、决策树、对比表都可以]
[不套模板，有什么写什么]

## 注意

[边界、例外、不应该做的事]

---

## 新建 skill 的检查清单

- [ ] description 里有 "Use when..."，触发条件具体
- [ ] 信息收集部分说清楚了来源和缺口处理
- [ ] 内容说明了 why，不只是 what
- [ ] 边界清楚：这个 skill 不处理什么
- [ ] 长度合适：能说清楚就够，不追求完整