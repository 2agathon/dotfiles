---
name: git-commit
description: >
  用户想提交代码、说 commit、说 git 提交、说"提一下"时触发。
  提交之前先判断"该提交了吗"——读 diff，识别逻辑单元，告诉你哪些可以提交、哪些还没完整。
  message 从 diff 推断，不问废话。发现设计分叉时提示触发 decision-record。
license: MIT
---

## Workflow

### Step 1 — 读现场

```bash
git status --porcelain
git diff --staged
git diff
```

staged 优先；什么都没 staged，读 working tree。

### Step 2 — 识别逻辑单元

按**变更意图**分组，不按文件分组。

判断标准：**这些改动如果被 revert，会同时消失还是分别消失？** 应该同时消失的是一个单元。

输出：

```
发现 N 个逻辑单元：

[✓ 可提交] <单元描述>
  文件：...

[⚠ 未完整] <单元描述> — <为什么还不完整>
  文件：...
```

超过一个可提交单元时，询问用户是否拆分提交。不替用户决定。

### Step 3 — 生成 commit message

从 diff 推断，不问用户——除非 body 明显推断不出。

#### 格式

```
<type>(<scope>): <description>

<body>

decision-record: <触发原因>  ← 仅当检测到设计分叉时追加
```

#### type

| type | 用于 |
|------|------|
| `feat` | 新能力、新行为 |
| `fix` | 修正错误行为 |
| `refactor` | 等价重写，行为不变 |
| `perf` | 性能改进 |
| `docs` | 文档 |
| `test` | 测试 |
| `build` | 构建、依赖 |
| `chore` | 维护、配置、脚手架 |
| `revert` | 撤销 |

#### scope

从文件路径推断，取业务语义最强的词；纯技术分层词不选；推断不出时省略。不读外部配置文件。

#### description

说意图，不说实现。现在时祈使句，72 字符以内。

#### body

**不可省略**——除非 description 已完整说清楚"为什么"。

body 回答：这个改动解决了什么问题，为什么是这个方案而不是别的。从 diff 推断；推断不出时向用户提问。

### Step 4 — 决策分叉检测

改动体现了一个**选择**而不是必然路径时，就是设计分叉。主动提示：

```
⚡ 检测到设计分叉：<描述>
   这个决定需要记录吗？（触发 decision-record）[y/n]
```

用户确认后，footer 追加 `decision-record: <原因>`，并提示执行 decision-record skill。

### Step 5 — 执行提交

确认 message 后执行：

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

<body>
EOF
)"
```

---

## Safety Protocol

- **不动 git config**
- **不执行破坏性命令**（`--force`, `reset --hard`）除非用户明确要求
- **不跳过 hooks**（`--no-verify`）除非用户明确要求
- **不 force push 到 main/master**
- commit hook 失败时：修复问题，新建 commit，不 amend

---

## 提问原则

推断不确定时，只问最影响方向的一个问题。不同时问多个。
