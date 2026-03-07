---
name: gen-agents
description: Use when starting work on any project, when no AGENTS.md exists, when the user needs to set up project-level AI context, or when joining a project with existing rules. Guides identification of where Layer 0 default behavior needs adjustment for this project, and where that adjustment should live based on ownership.
---

## 这个 skill 做什么

找出 Layer 0 在这个项目里哪里不够用，把缺口表达成行为指令。

判断标准：AGENTS.md 里每一句话，都应该能回答——
**在什么情况下，AI 应该做什么不同于 Layer 0 默认行为的事？**

回答不了这个问题的，不属于这里。

---

## 第一个问题，也是唯一的分叉点

**你在这个项目里有没有所有权？**

有 → Layer 2，进仓库
没有 → Layer 3，不进仓库

所有权判断标准：你能不能决定这个项目的工程规范，并且让其他人遵守。

---

## Layer 2 路径：有所有权

**引导识别缺口，不是收集项目信息**

按顺序问这四个问题，从对话或文件里能提取的直接提取，不重复问：

**1. 语言约定是什么？**
Layer 0 没有语言约定，这是必须在项目层定义的变量。
注释、日志、commit message 用什么语言，必须明确。

**2. Layer 0 的哪些规则在这个项目里不成立？**
比如：原型阶段允许返回 dict，进迭代前用 DEVIATION 标注替代立刻处理。
没有例外就不写。

**3. 这个项目有什么 Layer 0 没覆盖的硬约束？**
外部合规要求、接口安全边界、领域特有规则——不是项目描述，是行为约束。
比如："任何 SQL 在执行前必须通过 AST 级 guardrail 检查"，不是"这个项目用了 DuckDB"。

**4. 技术栈是什么？**
不是元数据，是 principles 的翻译参数。
"不用 Map 作为返回类型"在 Python 里是"不用 dict"，在 Java 里是"不用 HashMap"。
技术栈决定 principles 如何落地，不需要写进 AGENTS.md，但生成时用来校准措辞。

**输出结构**

只有内容才有节，没有内容不生成空节。
```
# AGENTS.md · [项目名]

## 语言约定
代码注释：
日志输出：
表注释 / 字段注释：
错误码描述：
Git commit message：

## Layer 0 在这里的例外
[每条说明原因]
[DEVIATION: 原因]

## 这个项目独有的行为约束
[每条是行为指令，说明在什么情况下做什么，说明 why]
```

**自检**
- [ ] 每一条能否回答"在什么情况下，AI 做什么不同于 Layer 0 的事"？
- [ ] 有没有把项目描述（技术栈、架构、端口）写进来？

---

## Layer 3 路径：没有所有权

**情况 A：有团队规范，打补丁**
```
# AGENTS.local.md · [项目名] · 个人补丁

## 我覆盖了团队规范的哪些地方
[每条说明原因]
// DEVIATION: 原因

## 团队规范没说但我需要的行为约束
[每条是行为指令，说明 why]
```

**情况 B：没有规范，也没权建**
```
# AGENTS.local.md · [项目名] · 个人工作层

[临时文件，等正式规范建立后迁移废弃]

## 我在这个项目里的工作方式
[不是项目规范，是 Layer 0 在这个项目里的个人具体化]
```

**两种情况都适用**
临时妥协表不在初始生成物里。项目进行中遇到"违反 principles 但改不动"时，手动追加：
```
## 临时妥协表
| 位置 | 违反了什么 | 原因 | 计划 |
|------|-----------|------|------|
```

**Layer 3 的硬约束**
不进仓库。进了仓库就变成 Layer 2，性质完全不同。

---

## 生成完成后

**Layer 2：**
> 复制到项目根目录 `AGENTS.md` 并提交。
> `[OPEN QUESTION]` 和 `[ASSUMPTION]` 就近挂在对应条目下，解决了就地删。

**Layer 3：**
> 放项目根目录，文件名 `AGENTS.local.md`，确认已加进 `.gitignore`。