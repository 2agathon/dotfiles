---
name: gen-agents
description: Use when starting a new project, when no AGENTS.md exists in the project root, or when the user asks to generate project-level rules. Guides the generation of a project-specific AGENTS.md based on project context.
---

## 这个 skill 做什么

根据项目特性生成 AGENTS.md 的项目层内容（Layer 2）。
只写这个项目独有的上下文和约定，不重复全局规范（identity + principles）。

## 触发判断

以下情况主动提示用户是否需要生成：
- 项目根目录没有 AGENTS.md
- 用户说"新项目"、"从零开始"、"刚克隆"

## 信息收集

**我需要什么信息**
项目阶段、业务域、技术栈、我的角色、语言约定、特殊约束。

**信息从哪里来**
- 你提供 → 你了解项目，直接描述
- 读文件 → 提供 pom.xml / package.json / README / tree 输出，从文件推断，推断内容用 `[INFERRED]` 标注
- 从对话提取 → 你描述了项目背景，直接从描述里提取，不重复问

**信息缺口怎么处理**

信息缺口分两类，处理方式不同：

| 缺口类型       | 处理方式                                           |
| -------------- | -------------------------------------------------- |
| 项目阶段不明确 | 必须问——这个影响生成意图声明还是现状描述，方向不同 |
| 其余字段缺失   | 用 `[OPEN QUESTION]` 占位，生成骨架，边做边补      |
| 完全不了解项目 | 直接进模式 B，只问项目阶段，其余全部占位           |

**只问一个问题**：信息不足时，只问最影响方向的那一个。通常是项目阶段。其余用 `[ASSUMPTION]` 或 `[OPEN QUESTION]` 标注，不列问题清单让用户逐一回答。

## 三种模式

**模式 A：我了解项目**
从对话或你的描述里提取所有可用信息，缺口用标注占位，直接生成。不需要走确认流程。

**模式 B：我不了解项目 / 没时间描述**
只需知道项目阶段。其余全部用 `[OPEN QUESTION]` 占位，生成可用骨架，边做项目边填。

**模式 C：有文件让我读**
提供 pom.xml / package.json / README / tree 输出，从文件推断技术栈、业务域、目录结构。推断内容用 `[INFERRED]` 标注，无法确定的用 `[OPEN QUESTION]` 标注。

## 生成规则

**这套规则在保护什么**
保护 Layer 2 的纯粹性。项目 AGENTS.md 只有写项目独有的内容才有价值——重复全局规范只是噪音，会稀释真正需要关注的项目特有约定。

1. 只写项目独有的上下文和约定，不重复全局规范
2. 每个约定说明 why，不只是 what
3. 无法确定的内容用 `[OPEN QUESTION: 具体问题]` 标注
4. 推断的内容用 `[INFERRED: 推断内容]` 或 `[ASSUMPTION: 推断内容]` 标注
5. 输出纯 Markdown，直接可用

**自检**
- [ ] 生成的内容里有没有和 identity / principles 重复的规则？
- [ ] 每条约定是否说明了 why，而不只是 what？

## 输出结构
```
# AGENTS.md · [项目名]

## 项目上下文
项目阶段：
业务域：
技术栈：
我的角色：

## 语言约定
代码注释：
日志输出：
表注释 / 字段注释：
错误码描述：
Git commit message：

## 项目特有约定
[只写这个项目独有的规则，每条说明 why]

## 已知约束
[特殊限制、外部依赖、合规要求]

## 待确认
[OPEN QUESTION] ...
[ASSUMPTION] ...
```

## 生成完成后

提示用户：
> 复制到项目根目录的 AGENTS.md。
> `[OPEN QUESTION]` 和 `[INFERRED]` 是待确认项，边做项目边填。