---
name: code-test
description: >
  约束 AI 写测试时的质量，防止废测试给用户虚假的安全感。
  用户说"写测试"、"加测试"、"补测试"、"测一下"时触发。
  不自动触发，不管测试框架选择，不管 CI 配置。
metadata:
  collection: 2agathon-dotfiles
  layer: 工程执行
  invocation: user-request-only
  scope: test-quality-not-framework-ci
  governance:
    hook: constraint
    requires: code under test, project test conventions
    enforces: behavior-over-implementation testing, mock scope control, error path coverage
    produces: test summary (structured, per test group)
    task_agnostic: false
    task_scope: test writing (write, add, update tests)
---

## 触发条件

用户主动要求写测试时触发：
- "写测试"、"加测试"、"补测试"
- "测一下这个"、"这个需要测试"
- "更新测试"、"测试也改一下"

不触发：
- 用户没提测试，AI 不主动提醒
- 讨论测试策略但没要求写

---

## 三条质量约束

### 1. 测行为不测实现

测试验证的是**输入什么、输出什么**，不是内部怎么实现的。

禁止：
- 断言内部方法被调用了几次
- 断言内部状态的中间值
- 断言调用顺序（除非顺序本身就是行为契约）

判断标准：如果重构了内部实现但外部行为不变，测试应该全绿。如果会红，这个测试在测实现。

### 2. 控制 Mock 范围

只 mock 必须 mock 的东西——外部服务、数据库、网络请求、文件系统。

禁止：
- Mock 被测模块自己的内部方法
- Mock 同一个项目里可以直接用的模块
- 把所有依赖都 mock 掉导致测试里跑的代码和真实环境完全不同

每用一个 mock，AI 必须能回答：**为什么这个不能用真实的？** 答不出来就不该 mock。

### 3. 必须覆盖错误路径

每组测试必须包含：
- 正常路径（happy path）
- 至少一个边界情况（空输入、零值、极大值、null/undefined）
- 至少一个错误路径（非法输入、依赖失败、超时）

如果 AI 写了五个测试全是 happy path → 不合格，必须补错误路径再交付。

---

## 测试输出格式

AI 写完测试后，附一段极短的测试说明：

```
测了什么：{一句话描述被测行为}
正常路径：{X 个}
边界情况：{X 个，列出哪些}
错误路径：{X 个，列出哪些}
Mock 了什么：{列出} 或 无
```

不需要用户主动要求这个说明，每次写测试都附。

---

## 跟随代码库约定

测试框架、断言风格、文件命名、目录位置 → 跟随项目已有的测试约定。

项目里没有现成测试时 → 问用户用什么框架，不自己选。

---

## Failure Modes

- 测试在断言内部实现细节而不是外部行为
- Mock 了不需要 mock 的东西
- 全部测试都是 happy path，没有错误路径
- 写了测试但没有附测试说明
- 项目没有测试约定时自己选了框架没问用户
- 测试描述模糊（如 "should work correctly"），看不出在测什么行为
