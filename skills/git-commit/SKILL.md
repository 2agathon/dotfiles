---
name: git-commit
description: >
  用户想提交代码、说 commit、说 git 提交、说"提一下"时触发。
  提交之前先判断"该提交了吗"——读 diff，识别逻辑单元，告诉你哪些可以提交、哪些还没完整。
  message 从 diff 推断，不问废话。发现设计分叉时提示触发 decision-record。
metadata:
  collection: 2agathon-dotfiles
  layer: 工程执行
  domain: vcs-commit
  invocation: user-request
---

## 核心原则

**介入深度匹配改动复杂度。** 简单的改动不该感觉到 skill 的存在；复杂的改动才展开完整判断。

---

## Workflow

### Step 1 — 读现场

```bash
git status --porcelain
git diff --staged
git diff
git branch --show-current
```

staged 优先；什么都没 staged，读 working tree。

### Step 2 — 意图识别

先判断用户想做的是什么：

**WIP（保存现场）** — 用户说"先存一下"、"切出去"、"还没做完"：
```bash
# 推荐 stash
git stash push -m "<描述>"

# 或 wip commit（用户明确要求时）
git add -A && git commit -m "wip: <描述>"
```
告知用户 wip commit 不是正式提交，后续需要 squash 或 rebase。WIP 路径到此结束，不继续走后续步骤。

**正式提交** — 继续 Step 3。

### Step 3 — 安全检查

扫描 staged 或 working tree 改动，发现以下任意一条，**停下来告知用户**，不继续提交：

- debug 代码（`console.log`、`print(`、`debugger`、`breakpoint()`、`pdb.set_trace()` 等）
- 疑似 secrets（硬编码的 key、token、password、私钥特征）
- 明显未完成标记（`TODO`、`FIXME`、`HACK` 出现在本次新增行里）

输出：
```
⚠ 发现潜在问题：
  - <问题描述>，位于 <文件:行号>
  
确认要继续提交吗？[y/n]
```

用户确认后继续；否则停止。

### Step 4 — 分支确认

显示当前分支，判断是否异常：

```
当前分支：<branch-name>
```

主干分支（`main`、`master`）上直接提交时，提示确认：
```
⚠ 当前在 <main/master>，确认在这里提交吗？[y/n]
```

其他分支直接继续，不打扰用户。

### Step 5 — 判断复杂度，选择路径

**简单改动**（同时满足）：
- 改动集中在一个意图
- diff 范围小且清晰

→ 直接推断 message，进 Step 6 快速确认。

**复杂改动**（任意一条）：
- 改动跨越多个意图
- 意图不明显
- 文件跨越多个不相关区域

→ 进逻辑单元分析。

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

超过一个可提交单元时，询问用户：拆分逐个提交，还是合并成一次。不替用户决定。

### Step 6 — 生成 commit message

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

**简单改动可省略**——description 已足够说清楚时。

**复杂改动不可省略**——body 回答：这个改动解决了什么问题，为什么是这个方案而不是别的。从 diff 推断；推断不出时向用户提问。

#### 决策分叉检测

改动体现了一个**选择**而不是必然路径时，主动提示：

```
⚡ 检测到设计分叉：<描述>
   这个决定需要记录吗？（触发 decision-record）[y/n]
```

用户确认后，footer 追加 `decision-record: <原因>`，并提示执行 decision-record skill。

### Step 7 — 执行提交

#### 单次提交

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

<body>
EOF
)"
```

#### 拆分提交（循环）

对每个逻辑单元依次执行：

```bash
git add <该单元的文件列表>
git diff --staged
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

<body>
EOF
)"
```

每个单元提交完后告知进度（第 X / N），再处理下一个。

### Step 8 — Push

提交完成后询问：

```
✓ 已提交。要 push 到远端吗？[y/n]
```

用户确认后执行：

```bash
git push
```

如果当前分支没有上游，自动补上：

```bash
git push --set-upstream origin <branch-name>
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
