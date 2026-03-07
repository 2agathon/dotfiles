# Global AGENTS · 2agathon

## 用户是谁

全栈工程师，AI Vibe Coding 为主要工作方式。
跨语言跨岗位，不被技术栈定义。
一个人扛项目，在信息不完整的情况下做决策是常态。

## 最核心的约定
- 没搞清楚目标之前不动手，先问
- 先骨架后展开，关键节点停下来交还控制权
- 每一步交付可以独立回滚、可以被验证
- 命名是边界声明，用业务词不用技术词
- 规范是默认行为，不是教条，偏离时说明原因
- [ASSUMPTION] 标注假设，[OPEN QUESTION] 标注未解决问题

## 完整规范

skills/identity         用户的工作方式，开始任何任务时加载
skills/principles       工程原则，写代码时加载
skills/project-structure 目录和文件结构，生成文件前加载
skills/gen-agents       生成项目 AGENTS.md
skills/vibe-plan        新功能开始前的技术对齐

## 项目规范
每个项目根目录有自己的 AGENTS.md，只写偏离全局规范的部分。
没有项目 AGENTS.md 时，触发 skills/gen-agents。