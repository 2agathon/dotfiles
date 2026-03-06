---
name: principles
description: Use when writing, reviewing, or refactoring code. Use when naming variables, methods, or modules. Use when designing interfaces, handling errors, writing logs, or adding comments. Core engineering principles that apply across all languages and projects.
---

## 一、命名是设计

命名不是标签，是边界声明。名字错了，边界就错了，之后所有东西都会往错的方向长。

用业务词，不用技术词。InsuranceClaimValidator 只能做一件事，ClaimManager 什么都能塞。
方法名描述意图，不描述实现。validateClaimAmount 告诉你发生了什么，processData 什么都没告诉你。
Magic string / magic number 必须具名。status == 2 不知道 2 是什么，status == ClaimStatus.UNDER_REVIEW 意图透明。
同一个概念只有一个名字。发现漂移立刻统一，不要让它蔓延。
避免布尔参数。process(true, false) 在调用处完全失去含义，用枚举或具名参数。

## 二、边界是架构

文件臃肿不是代码量的问题，是边界模糊的症状。

领域逻辑只在领域层。校验、计算、规则判断不属于 Controller，也不属于 DAO。
DTO 和领域对象不混用。DTO 是外部契约，领域对象是内部状态，两者变化原因不同。
IO 和外部依赖必须抽象成接口。写死就是把业务逻辑绑死在实现上。
不用 Map 作为返回类型。定义明确的类型，让编译器和 IDE 帮你守边界。
目录结构反映业务边界，不是技术分层的刻板复制。

## 三、可见性是质量

代码的行为、决策和不确定性，应该对人可见。

注释说 why，不说 what：
// ✗ 判断状态是否为2
// ✓ 状态2表示"人工复核中"，此时不允许用户撤销申请（防止审核资源浪费）

关键决策必须留痕。临时妥协必须注释原因和计划：
// FIXME: 暂时跳过签名校验，联调期间接口未稳定，上线前必须恢复
// TODO: 这里应该走消息队列，当前同步调用是临时方案

日志要有上下文，出了问题只看日志就能还原当时发生了什么。敏感字段进日志之前必须脱敏。
异常不能被吞，原始信息不能丢。包一层再抛时必须保留原始异常。
不确定的假设标注 [ASSUMPTION]，未解决的问题标注 [OPEN QUESTION]。

## 四、可验证性

每一步交付可以独立回滚、可以被验证、不留隐性副作用。

业务逻辑和 IO 分离，才能单独测试。
单元测试验证功能点，集成测试验证衔接，两者不能互相替代。
测试验证行为，不验证实现。
测试边界和异常，不只测 happy path。

## 五、AI Vibe Coding 特有规范

生成之前先对齐目录和边界。很多时候目录和文件名本身就是边界声明，比代码更重要。
发现命名漂移立刻指出。
规范是默认行为，不是刻板执行的脚本。偏离时说明原因。
关键节点停下来，不从头做到尾。