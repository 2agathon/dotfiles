# EVOLUTION.md · 体系演进规则

这套规范不是一次性的文档，是会随着你的认知一起生长的东西。
这里定义：什么时候更新，更新什么，怎么更新。

---

## 什么时候应该回来更新

**触发更新的信号，不是计划，是事件。**

遇到以下情况就回来：

- 你在某个项目里做了一个决策，发现 `skills/principles` 里没有覆盖到
- 你发现自己在多个项目里重复做同一个临时妥协，说明这个妥协应该被正式承认或者消灭
- 你的工作方式发生了真实的改变（不是"我觉得应该改"，是"我已经在这样做了"）
- 你回头看某条原则，发现它是教条而不是真实认知
- AI 在某个地方反复出错，说明你的规范在那里表达得不清楚

**不应该触发更新的情况：**

- 读了一篇好文章，觉得"这个也应该加进去"——先在项目里验证，再加
- 想让规范看起来更完整——完整不是目标，真实才是

---

## 更新哪个文件

| 你发现的问题                                            | 更新哪里                                 |
| ------------------------------------------------------- | ---------------------------------------- |
| 我的工作习惯变了                                        | `skills/identity/SKILL.md`               |
| 某条工程原则我真的在用，但没写进去                      | `skills/principles/SKILL.md`             |
| 某条工程原则我写了但实际上没在用                        | `skills/principles/SKILL.md`，删掉或降权 |
| 新功能开始前对齐文档总漏边界或 task 太粗                | `skills/vibe-plan/SKILL.md`              |
| 生成的 AGENTS.md 总是缺某类内容                         | `skills/gen-agents/SKILL.md`             |
| 新建文件总放错位置或命名含糊                            | `skills/file-creation/SKILL.md`          |
| 改代码时范围失控、顺手重构过多                          | `skills/code-modify/SKILL.md`            |
| 写的测试测实现、Mock 过大或虚假绿                       | `skills/code-test/SKILL.md`              |
| 提交前检查、拆分单元或 message 规则不顺手               | `skills/git-commit/SKILL.md`             |
| 交接信格式、加载或收工回流总对不上                      | `skills/code-relay/SKILL.md`             |
| 多轮迭代停不下来或止损信号不准                          | `skills/bail-out/SKILL.md`               |
| 文档生成没有针对性                                      | `skills/docs/SKILL.md`                   |
| 决策记录生成总是跑偏                                    | `skills/decision-record/SKILL.md`        |
| TM 头字段或版本链操作不符合预期                         | `skills/tension-manifest/SKILL.md`       |
| 前提审计识别不准或过于泛滥                              | `skills/assumption-audit/SKILL.md`       |
| 对话收敛时机判断不准                                    | `skills/conversation-to-spec/SKILL.md`   |
| 笔记捕捉不到认识变化                                    | `skills/notes-protocol/SKILL.md`         |
| Notion 操作出错或归类不准                               | `skills/notion-manager/SKILL.md`         |
| 知识塑形输出质量不稳定                                  | `skills/knowledge-shaping/SKILL.md`      |
| 漂移检测误报或漏报                                      | `skills/drift-detector/SKILL.md`         |
| 透镜识别不准或挑战透镜冲突性不足                        | `skills/role-lens/SKILL.md`              |
| 自我叙述改写过早固化或重入机制失效                      | `skills/self-rewrite/SKILL.md`           |
| 聊天解析或下游渲染管线不稳                              | `skills/chat-parser` / `chat-render`     |
| 表格类任务 skill 边界不清                               | `skills/xlsx/SKILL.md`                   |
| 页类型 spec 生成规则漂移                                | `skills/page-type-spec-generator`        |
| 全局入口需要调整（触发表、分层说明、路径约定）          | `AGENTS.md`                              |
| 对外说明与目录索引和 AGENTS 不一致                      | `README.md`                              |
| 演进规则本身需要改                                      | `EVOLUTION.md`（本文件）                 |
| 安装方式、本地路径写入方式或全局 skill 安装方式需要调整 | `install.sh` / `install.ps1`             |

---

## 怎么更新

**改之前先问自己：**

- 这是我已经在做的，还是我觉得应该做的？
- 这条在三个不同项目里都成立，还是只在某个项目里成立？
- 如果只在某个项目里成立，它应该在那个项目的 `AGENTS.md` 里，不在这里

**改的时候：**

- 说明 why，不只改 what
- 删除和新增同等重要——腐化的规范比没有规范更危险
- 一次只改一件事，不要攒着一起改
- 如果改动影响 skill 加载机制、路径机制或项目自包含方式，必须同时检查 `AGENTS.md`、`EVOLUTION.md`、`skills/gen-agents/SKILL.md`、`install.sh`、`install.ps1`、`README.md` 是否仍然一致

**改完之后：**

- 检查是否需要同步更新其他 skill
- 检查现有项目的 Layer 3 是否需要对应调整

---

## 定期回顾

不强制定期，但以下时机自然适合回顾：

- 一个项目结束，开始下一个之前
- 你感觉 AI 越来越不理解你的意图的时候
- 距离上次更新超过三个月

回顾时只问一个问题：**这套东西描述的还是真实的我吗？**

---

## 版本记录

> 每次重大更新在这里留一行记录，不需要写详细，一句话说清楚改了什么。

| 日期    | 改了什么                                                     |
| ------- | ------------------------------------------------------------ |
| 2026-03 | 初始版本，基于与 Claude 的对话建立                           |
| 2026-03 | 新增 assumption-audit、conversation-to-spec、decision-record；skill 体系按层分组；docs 与 decision-record 边界重新划定 |
| 2026-03 | 为适配仓库私有化，skill 加载从远程 raw URL 迁移为本地优先：全局 AGENTS 改为本地路径引用，项目级 AGENTS 改为复制 skill 到项目内并使用相对路径 |
| 2026-03 | 新增 knowledge-shaping、drift-detector、role-lens、self-rewrite 四个认识校准 skill；修复 11 个 skill 的 upstream 字段；补全 notion-manager / notes-protocol / gen-agents / drift-detector 的保护节；修复 self-rewrite frontmatter 格式 |
| 2026-04 | 补齐代码生命周期与止损链：`file-creation`、`code-modify`、`code-test`、`git-commit`、`code-relay`、`bail-out`；`AGENTS.md` 按责任分层重写索引并纳入领域专项与 `.system`；`README.md` 与之一致；`EVOLUTION.md` 扩展「更新哪个文件」映射 |
| 2026-04 | 废弃独立「目录结构」skill，全仓库清理引用；新建与目录边界由 `file-creation` 承接 |
